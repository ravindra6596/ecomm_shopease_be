from app.repositories import chatbot_repository
from app.services.chatbot_intent_service import process_chat_message
from app.utils.chatbot_engine import process_chat_messages


def create_chat_service_old(
    db,
    token,
    message
):

    # create conversation
    conversation = (
        chatbot_repository
        .create_conversation_repo(
            db,
            token["user_id"]
        )
    )

    # save user message
    chatbot_repository.save_message_repo(
        db=db,
        conversation_id=conversation.id,
        sender="user",
        message=message
    )

    # ai response
    # bot_response = ask_chatbot(
    #     message
    # )
    bot_response = process_chat_message(
        db=db,
        token=token,
        message=message
    )
    if not bot_response:
        bot_response = (
            "Sorry, I could not find that order."
        )
    # save bot response
    chatbot_repository.save_message_repo(
        db=db,
        conversation_id=conversation.id,
        sender="bot",
        message= bot_response or "No response available"
    )

    # get all messages
    messages = (
        chatbot_repository
        .get_messages_repo(
            db,
            conversation.id
        )
    )

    return {
        "conversation_id":
            conversation.id,

        "messages":
            messages
    }

def create_chat_service(
    db,
    token,
    message
):

    # create conversation
    conversation = (
        chatbot_repository .create_conversation_repo(
            db,token["user_id"]
        )
    )

    # save user message
    chatbot_repository.save_message_repo(
        db=db,
        conversation_id=conversation.id,
        sender="user",
        message=message,
    )


    bot_response = process_chat_messages(
        db=db,
        user_id=token.get("user_id"),
        message=message,
    )
    print("BOT RESPONSE:", bot_response)
    # 4. fallback if None
    if not bot_response:
        bot_response = {"reply": "Sorry, I could not process your request."}

    # 5. extract clean text for DB (IMPORTANT FIX)
    if isinstance(bot_response, dict):
        db_message = bot_response.get("reply")

        # fallback if reply not present
        if not db_message:
            db_message = "Here are the results"
    else:
        db_message = str(bot_response)

    #  save bot message in DB (ONLY TEXT)
    chatbot_repository.save_message_repo(
        db=db,
        conversation_id=conversation.id,
        sender="bot",
        message=db_message,
        products=bot_response.get("products") if isinstance(bot_response, dict) else None
    )

    # get all messages
    messages = (
        chatbot_repository.get_messages_repo(
            db,
            conversation.id
        )
    )

    return {
        "conversation_id": conversation.id,
        "messages": messages,
        "bot_response": bot_response,
        "products": bot_response.get("products") if isinstance(bot_response, dict) else None
    }

# get conversation messages
def get_chat_messages_service(
    db,
    conversation_id
):

    return (
        chatbot_repository
        .get_messages_repo(
            db,
            conversation_id
        )
    )

def get_user_chat_messages_service(db, user_id):
    return chatbot_repository.get_messages_repo_list(db, user_id)