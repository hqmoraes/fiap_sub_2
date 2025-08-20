from sqlalchemy import String, Integer, DateTime, Float, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum

class Base(DeclarativeBase):
    pass

class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(SAEnum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sale: Mapped["Sale"] = relationship("Sale", back_populates="vehicle", uselist=False)

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELED = "CANCELED"

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False, unique=True)
    buyer_cpf: Mapped[str] = mapped_column(String(14), nullable=False)
    sale_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)
    payment_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    vehicle: Mapped[Vehicle] = relationship("Vehicle", back_populates="sale")
