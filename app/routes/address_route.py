from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.core.event_logger import log_event
from app.core.log_events import AddressEvent
from app.database.connection import get_db
from app.models.address_model import Address
from app.schemas.address_schema import AddressCreate, AddressResponse, AddressUpdate
from app.schemas.response_schema import CustomResponse
from app.services import address_service
from app.utils.auth_dependency import verify_token
from app.utils.strings import ConstStrings

router = APIRouter(prefix=ConstStrings.ADDRESS_PREFIX, tags=[ConstStrings.ADDRESS_TAG])


# create address
@router.post(ConstStrings.GET_POST_ROUTE)
def create_address_route(
        address: AddressCreate,
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    try:
        created_address = address_service.create_address_service(
            db,
            address,
            token_data
        )

        user_id = token_data.get(ConstStrings.USER_ID_FIELD)

        log_event(
            AddressEvent.CREATED.value,
            {
                "user_id": user_id,
                "address": address,
            }
        )

        return CustomResponse.success_response(
            statusCode=201,
            message=ConstStrings.ADDRESS_CREATED,
            data={},
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=CustomResponse.error_response(
                statusCode=e.status_code,
                message=e.detail,
                error=e.detail,
                data={}
            )
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=CustomResponse.error_response(
                statusCode=500,
                message=ConstStrings.INTERNAL_SERVER_ERROR,
                error=str(e),
                data={}
            )
        )


# get address route
@router.get(ConstStrings.GET_POST_ROUTE)
def get_addresses_route(
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    addresses = address_service.get_addresses_service(
        db=db,
        token=token_data
    )

    response = [
        AddressResponse(
            id=item.id,
            user_id=item.user_id,
            full_name=item.full_name,
            phone=item.phone,
            address_line=item.address_line,
            city=item.city,
            state=item.state,
            country=item.country,
            pincode=item.pincode,
            is_default=item.is_default,
            address_type=item.address_type,
            latitude=item.latitude,
            longitude=item.longitude
        )
        for item in addresses
    ]

    log_event(
        AddressEvent.LISTED.value,
        {
            "count": len(response),
            "result": response
        }
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.ADDRESS_FETCHED,
        data=response
    )


# Update address
@router.patch(ConstStrings.ID_ROUTE)
def update_address_route(
        id: int,
        payload: AddressUpdate,
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    #   AUTH CHECK (same as user module)
    user_id = token_data.get(ConstStrings.USER_ID_FIELD)
    role = token_data.get("role")

    # fetch for ownership check
    address = db.query(Address).filter(
        Address.id == id,
        # Address.deleted_at.is_(None)
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    # ✔ only owner OR admin
    if role != "admin" and address.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail=ConstStrings.OWN_ADDRESS
        )

    updated_address = address_service.update_address_service(
        db,
        id,
        payload,
        token_data
    )
    log_event(
        AddressEvent.UPDATED.value,
        {
            "user_id":user_id,
            "result": payload,
            "updated_address":updated_address
        }
    )
    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.ADDRESS_UPDATED,
        data={}
    )


# get address by id
@router.get(ConstStrings.ID_ROUTE)
def get_address_by_id(
        id: int,
        db: Session = Depends(get_db),
        token_data: dict = Depends(verify_token)
):
    address = address_service.get_address_service(db, id)

    if not address:
        raise HTTPException(status_code=404, detail=ConstStrings.ADDRESS_NOT_FOUND)

    user_id = token_data.get(ConstStrings.USER_ID_FIELD)
    role = token_data.get("role")

    # RBAC
    if role != "admin" and address.user_id != user_id:
        raise HTTPException(status_code=403, detail=ConstStrings.NOT_ALLOWED)

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.ADDRESS_FETCHED,
        data=AddressResponse.model_validate(address)
    )

# delete add route
@router.delete(ConstStrings.ID_ROUTE)
def delete_address(
    id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):

    # fetch address
    address = db.query(Address).filter(
        Address.id == id
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail=ConstStrings.ADDRESS_NOT_FOUND
        )

    user_id = token_data.get(ConstStrings.USER_ID_FIELD)
    role = token_data.get("role")

    # RBAC
    if role != "admin" and address.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail=ConstStrings.NOT_ALLOWED
        )

    # store before delete (important for logs)
    deleted_address_id = address.id

    # hard delete
    address_service.delete_address_service(db, address)

    log_event(
        AddressEvent.DELETED.value,
        {
            "user_id": user_id,
            "address_id": deleted_address_id,
            "deleted_by": role
        }
    )

    return CustomResponse.success_response(
        statusCode=200,
        message=ConstStrings.ADDRESS_DELETED,
        data={}
    )