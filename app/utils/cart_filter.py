from fastapi import HTTPException


def get_cart_filter(token: dict = None, guest_id: str = None):

    user_id = token.get("user_id") if token else None

    if user_id:
        return {"user_id": user_id}

    if guest_id:
        return {"guest_id": guest_id}

    raise HTTPException(
        status_code=400,
        detail="Missing user_id or guest_id"
    )