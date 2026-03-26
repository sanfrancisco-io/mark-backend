from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date, ForeignKey, Integer, Numeric, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Seller(Base):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[Decimal] = mapped_column(Numeric(2, 1), nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    offers: Mapped[list["Offer"]] = relationship(back_populates="seller")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(Text, nullable=False, default="RUB")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image_object_key: Mapped[str | None] = mapped_column(Text)
    thumbnail_object_key: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    attributes: Mapped[list["ProductAttribute"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    offers: Mapped[list["Offer"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="attributes")


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"), nullable=False)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(Text, nullable=False, default="RUB")
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="offers")
    seller: Mapped["Seller"] = relationship(back_populates="offers")
