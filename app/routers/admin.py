from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database import get_db
from app.dependencies import require_admin
from app.models import Offer, Product, ProductAttribute, Seller
from app.placeholder import make_thumbnail
from app.s3 import get_public_url, upload_file
from app.schemas import (
    AttributeOut,
    ImageUploadResponse,
    OfferCreate,
    OfferOut,
    OfferUpdate,
    ProductAdminItem,
    ProductAdminListResponse,
    ProductCreate,
    ProductDetail,
    ProductUpdate,
    SellerCreate,
    SellerOut,
    SellerShort,
)

router = APIRouter(dependencies=[Depends(require_admin)])


# ── Helpers ────────────────────────────────────────────────────────────────────

def _product_to_admin_item(p: Product) -> ProductAdminItem:
    return ProductAdminItem(
        id=p.id,
        name=p.name,
        description=p.description,
        price_amount=p.price_amount,
        price_currency=p.price_currency,
        stock=p.stock,
        image_url=get_public_url(p.image_object_key) if p.image_object_key else None,
        thumbnail_url=get_public_url(p.thumbnail_object_key) if p.thumbnail_object_key else None,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


async def _get_product_or_404(db: AsyncSession, product_id: int) -> Product:
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def _get_offer_or_404(db: AsyncSession, offer_id: int) -> Offer:
    offer = await db.get(Offer, offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


# ── Products ───────────────────────────────────────────────────────────────────

@router.get("/products", response_model=ProductAdminListResponse)
async def list_products(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    rows = (await db.execute(select(Product).offset(offset).limit(limit + 1))).scalars().all()
    has_more = len(rows) > limit
    return ProductAdminListResponse(
        items=[_product_to_admin_item(p) for p in rows[:limit]],
        has_more=has_more,
    )


@router.post("/products", response_model=ProductAdminItem, status_code=201)
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude={"attributes"})
    product = Product(**data)
    db.add(product)
    await db.flush()
    for attr in body.attributes:
        db.add(ProductAttribute(product_id=product.id, name=attr.name, value=attr.value))
    await db.commit()
    await db.refresh(product)
    return _product_to_admin_item(product)


@router.get("/products/{product_id}", response_model=ProductDetail)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
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

    return ProductDetail(
        id=product.id,
        name=product.name,
        description=product.description,
        price_amount=product.price_amount,
        price_currency=product.price_currency,
        stock=product.stock,
        image_url=get_public_url(product.image_object_key) if product.image_object_key else None,
        thumbnail_url=get_public_url(product.thumbnail_object_key) if product.thumbnail_object_key else None,
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
            for o in sorted(product.offers, key=lambda o: o.price_amount)
        ],
    )


@router.put("/products/{product_id}", response_model=ProductAdminItem)
async def update_product(
    product_id: int,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    product = await _get_product_or_404(db, product_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return _product_to_admin_item(product)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await _get_product_or_404(db, product_id)
    await db.delete(product)
    await db.commit()


@router.post("/products/{product_id}/image", response_model=ImageUploadResponse)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    product = await _get_product_or_404(db, product_id)

    data = await file.read()
    ext = "jpg" if "jpeg" in (file.content_type or "") else "png"
    img_key = f"img_{product_id}.{ext}"
    thumb_key = f"thumb_{product_id}.png"

    thumbnail_data = make_thumbnail(data)

    await upload_file(img_key, data, file.content_type or "image/png")
    await upload_file(thumb_key, thumbnail_data, "image/png")

    product.image_object_key = img_key
    product.thumbnail_object_key = thumb_key
    await db.commit()

    return ImageUploadResponse(
        image_url=get_public_url(img_key),
        thumbnail_url=get_public_url(thumb_key),
    )


# ── Sellers ────────────────────────────────────────────────────────────────────

@router.get("/sellers", response_model=list[SellerOut])
async def list_sellers(db: AsyncSession = Depends(get_db)):
    sellers = (await db.execute(select(Seller).order_by(Seller.id))).scalars().all()
    return [SellerOut.model_validate(s) for s in sellers]


@router.post("/sellers", response_model=SellerOut, status_code=201)
async def create_seller(body: SellerCreate, db: AsyncSession = Depends(get_db)):
    seller = Seller(**body.model_dump())
    db.add(seller)
    await db.commit()
    await db.refresh(seller)
    return SellerOut.model_validate(seller)


# ── Offers ─────────────────────────────────────────────────────────────────────

@router.get("/products/{product_id}/offers", response_model=list[OfferOut])
async def list_offers(product_id: int, db: AsyncSession = Depends(get_db)):
    await _get_product_or_404(db, product_id)
    stmt = (
        select(Offer)
        .where(Offer.product_id == product_id)
        .options(joinedload(Offer.seller))
        .order_by(Offer.price_amount)
    )
    offers = (await db.execute(stmt)).scalars().all()
    return [
        OfferOut(
            id=o.id,
            price_amount=o.price_amount,
            price_currency=o.price_currency,
            delivery_date=o.delivery_date,
            seller=SellerShort.model_validate(o.seller),
        )
        for o in offers
    ]


@router.post("/products/{product_id}/offers", response_model=OfferOut, status_code=201)
async def create_offer(
    product_id: int,
    body: OfferCreate,
    db: AsyncSession = Depends(get_db),
):
    await _get_product_or_404(db, product_id)
    seller = await db.get(Seller, body.seller_id)
    if seller is None:
        raise HTTPException(status_code=404, detail="Seller not found")

    offer = Offer(product_id=product_id, **body.model_dump())
    db.add(offer)
    await db.commit()
    await db.refresh(offer)

    return OfferOut(
        id=offer.id,
        price_amount=offer.price_amount,
        price_currency=offer.price_currency,
        delivery_date=offer.delivery_date,
        seller=SellerShort.model_validate(seller),
    )


@router.put("/offers/{offer_id}", response_model=OfferOut)
async def update_offer(
    offer_id: int,
    body: OfferUpdate,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Offer).where(Offer.id == offer_id).options(joinedload(Offer.seller))
    offer = (await db.execute(stmt)).scalar_one_or_none()
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(offer, field, value)
    await db.commit()
    await db.refresh(offer)

    return OfferOut(
        id=offer.id,
        price_amount=offer.price_amount,
        price_currency=offer.price_currency,
        delivery_date=offer.delivery_date,
        seller=SellerShort.model_validate(offer.seller),
    )


@router.delete("/offers/{offer_id}", status_code=204)
async def delete_offer(offer_id: int, db: AsyncSession = Depends(get_db)):
    offer = await _get_offer_or_404(db, offer_id)
    await db.delete(offer)
    await db.commit()
