from app.models.chatbot_model import ChatMessage, ChatConversation


# create conversation
def create_conversation_repo(
    db,
    user_id
):

    conversation = ChatConversation(
        user_id=user_id
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


# save message
def save_message_repo(
    db,
    conversation_id,
    sender,
    message,products=None
):

    chat_message = ChatMessage(
        conversation_id=conversation_id,
        sender=sender,
        message=message,
        products=products
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message


# get messages
def get_messages_repo(
    db,
    conversation_id
):

    return db.query(ChatMessage).filter(
        ChatMessage.conversation_id  == conversation_id
    ).order_by(
        ChatMessage.id.asc()
    ).all()

def get_messages_repo_list(db, user_id):
    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.id.desc())
        .all()
    )

    result = []

    for conv in conversations:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conv.id)
            .order_by(ChatMessage.id.asc())
            .all()
        )

        result.append({
            "conversation_id": conv.id,
            "messages": [
                {
                    "id": m.id,
                    "conversation_id": m.conversation_id,
                    "sender": m.sender,
                    "message": m.message,
                    "products": m.products,
                    "created_at": m.created_at
                }
                for m in messages
            ]
        })

    return result