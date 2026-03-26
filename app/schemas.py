from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class SellerShort(BaseModel):
    id: int
    name: str
    rating: Decimal

    model_config = {"from_attributes": True}


class OfferOut(BaseModel):
    id: int
    price_amount: Decimal
    price_currency: str
    delivery_date: date
    seller: SellerShort

    model_config = {"from_attributes": True}


class AttributeOut(BaseModel):
    name: str
    value: str

    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    id: int
    name: str
    price_amount: Decimal
    price_currency: str
    stock: int
    thumbnail_url: str | None
    nearest_delivery_date: date | None


class ProductListResponse(BaseModel):
    items: list[ProductListItem]
    has_more: bool


class ProductDetail(BaseModel):
    id: int
    name: str
    description: str | None
    price_amount: Decimal
    price_currency: str
    stock: int
    image_url: str | None
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime
    attributes: list[AttributeOut]
    offers: list[OfferOut]
