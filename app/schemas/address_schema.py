import re

from pydantic import BaseModel, field_validator, Field
from typing import Optional


# CREATE
class AddressCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    address_line: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    country: str = Field(..., min_length=2, max_length=50)
    pincode: str = Field(..., min_length=4, max_length=10)
    is_default: Optional[bool] = False
    address_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # phone validation
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.fullmatch(r"^[0-9]{10,15}$", v):
            raise ValueError("Phone must contain only digits (10-15 length)")
        return v

    # pincode validation (India + generic)
    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v):
        if not re.fullmatch(r"^[0-9]{4,10}$", v):
            raise ValueError("Invalid pincode format")
        return v

    # optional cleanup
    @field_validator("full_name", "city", "state", "country")
    @classmethod
    def strip_fields(cls, v):
        return v.strip()


# UPDATE
class AddressUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    address_line: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=50)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    country: Optional[str] = Field(None, min_length=2, max_length=50)
    pincode: Optional[str] = Field(None, min_length=4, max_length=10)
    address_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = None
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.fullmatch(r"^[0-9]{10,15}$", v):
            raise ValueError("Invalid phone number")
        return v

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v):
        if v and not re.fullmatch(r"^[0-9]{4,10}$", v):
            raise ValueError("Invalid pincode")
        return v


# RESPONSE
class AddressResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    full_name: str
    phone: str
    address_line: str
    city: str
    state: str
    country: str
    pincode: str
    is_default: bool
    address_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True