from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database import get_db
from app.models import Offer, Product, ProductAttribute, Seller
from app.s3 import get_public_url
from app.schemas import (
    AttributeOut,
    OfferOut,
    ProductDetail,
    ProductListItem,
    ProductListResponse,
    SellerShort,
)

router = APIRouter()


def _thumbnail_url(key: str | None) -> str | None:
    return get_public_url(key) if key else None


def _image_url(key: str | None) -> str | None:
    return get_public_url(key) if key else None


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    nearest_delivery_sq = (
        select(func.min(Offer.delivery_date))
        .where(Offer.product_id == Product.id)
        .correlate(Product)
        .scalar_subquery()
    )

    stmt = (
        select(Product, nearest_delivery_sq.label("nearest_delivery_date"))
        .offset(offset)
        .limit(limit + 1)
    )
    rows = (await db.execute(stmt)).all()

    has_more = len(rows) > limit
    rows = rows[:limit]

    items = [
        ProductListItem(
            id=product.id,
            name=product.name,
            price_amount=product.price_amount,
            price_currency=product.price_currency,
            stock=product.stock,
            thumbnail_url=_thumbnail_url(product.thumbnail_object_key),
            nearest_delivery_date=nearest_delivery_date,
        )
        for product, nearest_delivery_date in rows
    ]

    return ProductListResponse(items=items, has_more=has_more)


@router.get("/products/{product_id}", response_model=ProductDetail)
async def get_product(
    product_id: int,
    offers_sort: Literal["price", "delivery_date"] = Query("price"),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.attributes),
            selectinload(Product.offers).joinedload(Offer.seller),
        )
    )
    product = (await db.execute(stmt)).scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    sorted_offers = sorted(
        product.offers,
        key=lambda o: o.price_amount if offers_sort == "price" else o.delivery_date,
    )

    return ProductDetail(
        id=product.id,
        name=product.name,
        description=product.description,
        price_amount=product.price_amount,
        price_currency=product.price_currency,
        stock=product.stock,
        image_url=_image_url(product.image_object_key),
        thumbnail_url=_thumbnail_url(product.thumbnail_object_key),
        created_at=product.created_at,
        updated_at=product.updated_at,
        attributes=[AttributeOut.model_validate(a) for a in product.attributes],
        offers=[
            OfferOut(
                id=o.id,
                price_amount=o.price_amount,
                price_currency=o.price_currency,
                delivery_date=o.delivery_date,
                seller=SellerShort.model_validate(o.seller),
            )
            for o in sorted_offers
        ],
    )
