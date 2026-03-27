from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# ── Shared output ──────────────────────────────────────────────────────────────

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


class AttributeCreate(BaseModel):
    name: str
    value: str


# ── Public API ─────────────────────────────────────────────────────────────────

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


# ── Admin: auth ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Admin: products ────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price_amount: Decimal
    price_currency: str = "RUB"
    stock: int = 0
    attributes: list[AttributeCreate] = []


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price_amount: Decimal | None = None
    price_currency: str | None = None
    stock: int | None = None


class ProductAdminItem(BaseModel):
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


class ProductAdminListResponse(BaseModel):
    items: list[ProductAdminItem]
    has_more: bool


class ImageUploadResponse(BaseModel):
    image_url: str
    thumbnail_url: str


# ── Admin: sellers ─────────────────────────────────────────────────────────────

class SellerCreate(BaseModel):
    name: str
    rating: Decimal = Decimal("0.0")


class SellerOut(BaseModel):
    id: int
    name: str
    rating: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Admin: offers ──────────────────────────────────────────────────────────────

class OfferCreate(BaseModel):
    seller_id: int
    price_amount: Decimal
    price_currency: str = "RUB"
    delivery_date: date


class OfferUpdate(BaseModel):
    price_amount: Decimal | None = None
    price_currency: str | None = None
    delivery_date: date | None = None
