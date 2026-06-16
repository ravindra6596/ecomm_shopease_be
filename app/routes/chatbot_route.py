import re

from fastapi import APIRouter, Depends
from openai import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.chatbot_schema import (
    ChatRequest,
    ChatMessageResponse
)
from app.schemas.response_schema import CustomResponse
from app.services import chatbot_service
from app.utils.auth_dependency import verify_token
from app.utils.strings import ConstStrings

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


@router.post(ConstStrings.GET_POST_ROUTE)
def create_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):

    result = (
        chatbot_service
        .create_chat_service(
            db,
            token,
            request.message
        )
    )

    return (
        CustomResponse.success_response(
            statusCode=200,
            message="Chat created successfully",
            data={
                "conversation_id":
                    result[ "conversation_id"],

                "messages": [
                    ChatMessageResponse.model_validate(message)
                    for message in result["messages"]
                ],
                "bot_response": result.get("bot_response"),
                # "products": result.get("products")if isinstance('bot_response', dict) else None
            }
        )
    )


# get chat messages
@router.get(ConstStrings.ID_ROUTE)
def get_chat_messages(
    id: int,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):

    result = (
        chatbot_service
        .get_chat_messages_service(
            db,
            id
        )
    )

    return (
        CustomResponse
        .success_response(
            statusCode=200,
            message="Chat messages fetched successfully",
            data=[
                ChatMessageResponse.model_validate(message)
                for message in result
            ]
        )
    )

@router.get(ConstStrings.GET_POST_ROUTE)
def get_user_chats(
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    user_id = token.get(ConstStrings.USER_ID_FIELD)

    result = chatbot_service.get_user_chat_messages_service(db, user_id)
    return CustomResponse.success_response(
        statusCode=200,
        message="Chats fetched successfully",
        data=result
    )

# CUSTOM CHAT BOAT



# detect intent
def detect_intent(message):
    msg = message.lower()

    if any(x in msg for x in ["where is my order", "track order"]):
        return "order_status"

    if any(x in msg for x in ["latest order", "last order"]):
        return "latest_order"

    if any(x in msg for x in ["delivery date", "arrive", "delivery"]):
        return "delivery_date"

    if "cart" in msg:
        return "cart_items"

    if any(x in msg for x in ["recommend", "suggest"]):
        return "product_recommendation"

    if any(x in msg for x in ["show", "search", "find"]):
        return "product_search"

    if any(x in msg for x in ["price", "cost", "how much"]):
        return "product_price"

    return "unknown"


def extract_product(message: str):
    stop_words = ["price", "cost", "how much is", "rate of"]
    for word in stop_words:
        message = message.lower().replace(word, "")
    return message.strip()


@router.post("/chat-api")
async def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    intent = detect_intent(req.message)

    handler = INTENTS.get(intent)

    if not handler:
        return {"reply": "Sorry, I didn't understand that."}

    return handler(
        req.message,
        token.get(ConstStrings.USER_ID_FIELD),
        db
    )


class ChatRequest(BaseModel):
    message: str
    user_id: int


def get_order_status(user_id: int,db  ):
    # Example: fetch latest order
    order = db.execute(
        text("""
            SELECT id, status
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"user_id": user_id}
    ).fetchone()

    if not order:
        return {"reply": "No orders found."}

    return {
         "reply": f"Your order #{order[0]} is {order[1]}"
    }

def get_product_price(message: str,db):
    product_name = extract_product(message)
    message = message.lower()
    for word in ["how much", "price", "for"]:
        message = message.replace(word, "")
    product = db.execute(
        text("""
            SELECT name, price
            FROM products
            WHERE LOWER(name) LIKE :name
            LIMIT 1
        """),
        {"name": f"%{message.strip()}%"}
    ).fetchone()

    if not product:
        return {"reply": f"{product_name.lower()} - Product not found."}

    return {
        "reply": f"{product.name} costs ₹{product.price}"
    }

def get_latest_order(message, user_id, db):
    order = db.execute(
        text("""
            SELECT id,status,total_amount
            FROM orders
            WHERE user_id=:user_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"user_id": user_id}
    ).mappings().fetchone()

    if not order:
        return {"reply": "No orders found."}

    return {
        "reply": f"Order #{order['id']} is {order['status']} and amount is ₹{order['total_amount']}"
    }

def get_delivery_date(message, user_id, db):
    order = db.execute(
        text("""
            SELECT id,estimated_delivery_date
            FROM orders
            WHERE user_id=:user_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"user_id": user_id}
    ).mappings().fetchone()

    if not order:
        return {"reply": "No active order found."}

    return {
        "reply": f"Order #{order['id']} will arrive on {order['estimated_delivery_date']}"
    }

def get_cart_items(message, user_id, db):
    rows = db.execute(
        text("""
            SELECT p.name,c.quantity
            FROM cart_items c
            JOIN products p ON p.id = c.product_id
            WHERE c.user_id = :user_id
        """),
        {"user_id": user_id}
    ).mappings().fetchall()

    if not rows:
        return {"reply": "Your cart is empty."}

    items = [
        f"{r['name']} (Qty: {r['quantity']})"
        for r in rows
    ]

    return {
        "reply": "Cart Items:\n" + "\n".join(items)
    }

def search_products(message, user_id, db):

    msg = message.lower()

    match = re.search(r'under\s+(\d+)', msg)

    if match:
        max_price = int(match.group(1))

        products = db.execute(
            text("""
                SELECT name, price
                FROM products
                WHERE price <= :max_price
                LIMIT 10
            """),
            {"max_price": max_price}
        ).mappings().fetchall()

        if not products:
            return {"reply": f"No products found under ₹{max_price}"}

        return {
            "products": [
                {
                    "name": p["name"],
                    "price": p["price"]
                }
                for p in products
            ]
        }

    return {"reply": "Please specify a price range."}

def recommend_products(message, user_id, db):

    products = db.execute(
        text("""
            SELECT name,price
            FROM products
            WHERE category='Laptop'
            ORDER BY rating DESC
            LIMIT 5
        """)
    ).mappings().fetchall()

    if not products:
        return {"reply": "No recommendations available."}

    return {
        "recommended": [
            {
                "name": p["name"],
                "price": p["price"]
            }
            for p in products
        ]
    }

INTENTS = {
    "order_status": get_order_status,
    "product_price": get_product_price,
    "latest_order": get_latest_order,
    "delivery_date": get_delivery_date,
    "cart_items": get_cart_items,
    "product_search": search_products,
    "product_recommendation": recommend_products,
}
