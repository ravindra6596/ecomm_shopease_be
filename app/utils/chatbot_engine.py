import re
from sqlalchemy import text
from typing import Dict, Any

from app.models.cart_item_model import CartItem
from app.models.cart_model import Cart
from app.models.products_model import Product
from app.models.wishlist_model import Wishlist
from app.models.order_items_model import OrderItem
from app.models.order_model import Order


def process_chat_messages(db, user_id: int, message: str) -> Dict[str, Any]:

    intent = detect_intent(message)

    handler = INTENTS.get(intent)

    if handler:
        return handler(message, user_id, db)

    return {"reply": "Sorry, I didn’t understand that."}

def detect_intent(message: str):
    msg = message.lower()

    if any(x in msg for x in ["where is my order", "track order"]):
        return "order_status"

    if any(x in msg for x in ["latest order", "last order"]):
        return "latest_order"

    if any(x in msg for x in ["delivery date", "arrive", "delivery"]):
        return "delivery_date"

    if any(x in msg for x in ["cart", "carts", "shopping cart",'basket']):
        return "cart_items"
    if any(x in msg for x in [
        "wishlist", "wish list",
        "favorite","favorites","favourite","favourites","saved items","saved products"]):
        return "wishlist_items"
    if any(x in msg for x in [
        "order", "orders", "purchases",
        "my purchase", "purchase history", "buy history",
        'order history'
    ]):
        return "order_items"

    if any(x in msg for x in ["recommend", "suggest"]):
        return "product_recommendation"

    if any(x in msg for x in ["show", "search", "find", "under", "below"]):
        return "product_search"

    if any(x in msg for x in ["price", "cost", "how much"]):
        return "product_price"

    return "unknown"

def extract_product(message: str):
    msg = message.lower()

    for word in ["how much", "price", "cost", "for", "of", "is"]:
        msg = msg.replace(word, "")

    return msg.strip()


def get_order_status(message, user_id, db):

    order = db.execute(
        text("""
            SELECT id, status
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"user_id": user_id}
    ).mappings().fetchone()

    if not order:
        return {"reply": "No orders found."}

    return {
        "reply": f"Your order #{order['id']} is {order['status']}"
    }

def get_latest_order(message, user_id, db):

    order = db.execute(
        text("""
            SELECT id, status, total_amount
            FROM orders
            WHERE user_id = :user_id
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
            SELECT id, estimated_delivery_date
            FROM orders
            WHERE user_id = :user_id
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

    cart_items = (
        db.query(CartItem)
        .join(Cart)
        .join(Product)
        .filter(Cart.user_id == user_id)
        .all()
    )

    if not cart_items:
        return {
            "reply": "Your cart is empty.",
            "products": []
        }

    products = []
    text_items = []

    for item in cart_items:
        product = item.product

        products.append({
            "name": product.name,
            "price": product.price,
            "quantity": item.quantity
        })

        text_items.append(
            f"{product.name} (Qty: {item.quantity})"
        )

    return {
        "products": products
    }

def get_wishlist_items(message, user_id, db):

    wishlist_items = (
        db.query(Wishlist)
        .filter(Wishlist.user_id == user_id)
        .all()
    )

    if not wishlist_items:
        return {
            "reply": "Your wishlist is empty.",
            "products": []
        }

    products = []
    text_items = []

    for item in wishlist_items:
        product = item.product

        products.append({
            "name": product.name,
            "price": product.price
        })

        text_items.append(product.name)

    return {
        "products": products
    }

def get_order_items(message, user_id, db):

    order_items = (
        db.query(OrderItem)
        .join(Order)
        .join(Product)
        .filter(Order.user_id == user_id)
        .all()
    )

    if not order_items:
        return {
            "reply": "You have no orders yet.",
            "products": []
        }

    products = []
    text_items = []

    for item in order_items:
        product = item.product

        products.append({
            "name": product.name,
            "price": item.price,   # important: order price snapshot
            "quantity": item.quantity,
            "order_id": item.order_id
        })

        text_items.append(
            f"{product.name} (Qty: {item.quantity}) - ₹{item.price}"
        )

    return {
        "products": products
    }


def get_product_price(message, user_id, db):

    product_name = extract_product(message)

    product = db.execute(
        text("""
            SELECT name, price
            FROM products
            WHERE LOWER(name) LIKE :name
            LIMIT 1
        """),
        {"name": f"%{product_name}%"}
    ).mappings().fetchone()

    if not product:
        return {"reply": f"Sorry, I couldn't find {product_name}"}

    return {
        "reply": f"{product['name']} costs ₹{product['price']}"
    }


# -----------------------------
# MAIN SEARCH FUNCTION
# -----------------------------
def search_products(message, user_id, db):

    msg = message.lower().strip()

    # -------------------------
    # 1. PRICE FILTER
    # -------------------------
    price_match = re.search(r'(under|below|less than)\s+(\d+)', msg)

    if price_match:
        max_price = int(price_match.group(2))

        products = db.execute(
            text("""
                SELECT name, price
                FROM products
                WHERE price <= :max_price
                AND is_deleted = false
                ORDER BY price ASC
            """),
            {"max_price": max_price}
        ).mappings().fetchall()

        return {
            "reply": f"Here are products under ₹{max_price}",
            "products": [
                {"name": p["name"], "price": p["price"]}
                for p in products
            ]
        }

    # -------------------------
    # 2. CATEGORY SEARCH
    # -------------------------
    category = extract_category(msg,db)
    if category:
        products = (
            db.query(Product)
            .filter(Product.category_id == category["id"])
            .all()
        )

        return {
            "reply": f"Here are {category['name']} products",
            "products": [
                {"name": p.name, "price": p.price}
                for p in products
            ]
        }

    # -------------------------
    # 3. NORMAL SEARCH (CLEANED)
    # -------------------------
    query = clean_query(msg)

    products = db.execute(
        text("""
            SELECT name, price
            FROM products
            WHERE LOWER(name) LIKE :q
               OR LOWER(description) LIKE :q
            LIMIT 10
        """),
        {"q": f"%{query}%"}
    ).mappings().fetchall()

    if products:
        return {
            "reply": f"Here are results for '{message}'",
            "products": [
                {"name": p["name"], "price": p["price"]}
                for p in products
            ]
        }

    # -------------------------
    # 4. NO RESULT
    # -------------------------
    return {
        "reply": f"No products found for '{message}'",
        "products": []
    }

def recommend_products(message, user_id, db):

    products = db.execute(
        text("""
            SELECT name, price
            FROM products
            WHERE category = 'Laptop'
            ORDER BY rating DESC
        """)
    ).mappings().fetchall()

    if not products:
        return {"reply": "No recommendations available."}

    return {
        "recommended": [
            {"name": p["name"], "price": p["price"]}
            for p in products
        ]
    }

INTENTS = {
    "order_status": get_order_status,
    "latest_order": get_latest_order,
    "delivery_date": get_delivery_date,
    "cart_items": get_cart_items,
    "wishlist_items": get_wishlist_items,
    "order_items": get_order_items,
    "product_price": get_product_price,
    "product_search": search_products,
    "product_recommendation": recommend_products,
}

# -----------------------------
# EXTRACT CATEGORY
# -----------------------------
def extract_category(message: str, db):

    msg = message.lower().strip()

    category = db.execute(
        text("""
            SELECT id, name
            FROM categories
            WHERE LOWER(:msg) LIKE '%' || LOWER(name) || '%'
            LIMIT 1
        """),
        {"msg": msg}
    ).mappings().fetchone()

    return category


# -----------------------------
# EXTRACT SEARCH QUERY CLEANING
# -----------------------------
def clean_query(message: str):
    msg = message.lower()

    remove_words = [
        "show", "search", "find", "get", "please", "me", "i want"
    ]

    for w in remove_words:
        msg = msg.replace(w, "")

    return msg.strip()

