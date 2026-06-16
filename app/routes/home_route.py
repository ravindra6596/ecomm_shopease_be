# Add To Cart
from typing import Optional

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.response_schema import CustomResponse
from app.services import home_service
from app.utils.auth_dependency import optional_verify_token, get_optional_user
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.HOME_PREFIX, tags=[ConstStrings.HOME_TAG])
@router.get(ConstStrings.GET_POST_ROUTE)
def get_home_data(
    db: Session = Depends(get_db),
    category_id: Optional[int] = None,
    token_data: dict = Depends(get_optional_user)
):

    result = (home_service.get_home_service(db,category_id=category_id,token=token_data))

    return (
        CustomResponse.success_response(
            statusCode=200,
            message= "Home data fetched successfully",
            data=result
        )
    )