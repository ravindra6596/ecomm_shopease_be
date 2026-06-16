# chatbot_intent_service.py
from app.services.chatbot_order_service import get_user_orders, get_cancel_order_help
from app.utils.openai_helper import ask_chatbot


def get_latest_order_status(db, token):
    pass


def process_chat_message(
    db,
    token,
    message: str
):
    text = message.lower()
    print("USER MESSAGE =", text)
    if "order status" in text:
        print("MATCHED ORDER STATUS")
        return get_latest_order_status(db, token)

    if "where is my order" in text:
        print("MATCHED WHERE IS MY ORDER")
        return get_latest_order_status(db, token)

    if "track order" in text:
        print("MATCHED TRACK ORDER")
        return get_latest_order_status(db, token)

    if "my orders" in text:
        return get_user_orders(db, token)

    if "cancel order" in text:
        return get_cancel_order_help(db, token)

    return ask_chatbot(message)