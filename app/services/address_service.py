from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.address_model import Address
from app.repositories import address_repository
from app.schemas.address_schema import AddressCreate, AddressUpdate
from app.utils.strings import ConstStrings


# create add service
def create_address_service(db: Session, address: AddressCreate, token: dict, ):
    return address_repository.create_address_repo(db, address, token)

# Get address service
def get_addresses_service(db: Session, token: dict):

    return address_repository.get_addresses_repo(db, token)

# update address service
def update_address_service(db, address_id: int, payload, token: dict):

    return address_repository.update_address_repo(
        db,
        address_id,
        payload
    )
# get add by id
def get_address_service(db: Session, address_id: int):
    return address_repository.get_address_by_id_repo(db, address_id)
# delete add
def delete_address_service(db: Session, address: Address):
    return address_repository.delete_address_repo(db, address)