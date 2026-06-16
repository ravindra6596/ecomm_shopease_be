from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.address_model import Address
from app.schemas.address_schema import AddressCreate
from app.utils.strings import ConstStrings


# create address
def create_address_repo(db: Session, address: AddressCreate, token):
    user_id = token.get(ConstStrings.USER_ID_FIELD)
    # check existing default address
    existing_default = db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True,
        Address.is_deleted == False
    ).first()

    # if no default exists -> make this default
    is_default = address.is_default

    if not existing_default:
        is_default = True

    # if current new address set as default
    if address.is_default:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_deleted == False
        ).update(
            {"is_default": False}
        )
    address_data = Address(
        user_id=user_id,
        full_name=address.full_name,
        phone=address.phone,
        address_line=address.address_line,
        city=address.city,
        state=address.state,
        country=address.country,
        pincode=address.pincode,
        is_default=is_default,
        address_type=address.address_type,
        latitude=address.latitude,
        longitude=address.longitude,
        is_deleted=False
    )

    db.add(address_data)
    db.commit()
    db.refresh(address_data)

    return address_data

def get_addresses_repo(db: Session, token: dict):

    user_id = token.get(ConstStrings.USER_ID_FIELD)
    role = token.get("role")

    # admin -> all addresses
    if role == "admin":
        addresses = db.query(Address).filter(Address.deleted_at.is_(None)).all()

    # user -> own addresses only
    else:
        addresses = (
            db.query(Address)
            .filter(
                Address.user_id == user_id,
                Address.is_deleted == False
            )
            .order_by(Address.is_default.desc(), Address.id.desc())
            .all()
        )

    return addresses
# address by id
def get_address_by_id_repo(db: Session, address_id: int):

    return db.query(Address).filter(
        Address.id == address_id,

    ).first()

# update address
def update_address_repo(db, address_id: int, address_data):

    address = db.query(Address).filter(
        Address.id == address_id,
        # Address.deleted_at.is_(None)
    ).first()

    if not address:
        return None

    update_data = address_data.model_dump(exclude_unset=True)

    # if setting current address as default
    if update_data.get("is_default") is True:
        # remove previous defaults
        db.query(Address).filter(
            Address.user_id == address.user_id,
            Address.id != address.id
        ).update(
            {"is_default": False}
        )

    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return address

# delete address
def delete_address_repo(db: Session, address: Address):

    user_id = address.user_id
    was_default = address.is_default

    # Soft delete the address
    address.is_deleted = True
    address.deleted_at = func.now()
    address.is_default = False
    db.commit()

    # if deleted address was default
    if was_default:
        next_address = db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_deleted == False
        ).first()

        if next_address:
            next_address.is_default = True
            db.commit()

    return True