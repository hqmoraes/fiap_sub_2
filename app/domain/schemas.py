from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"

class VehicleCreate(BaseModel):
    brand: str
    model: str
    year: int = Field(ge=1900, le=datetime.now().year + 1)
    color: str
    price: float = Field(gt=0)

class VehicleUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = Field(default=None, ge=1900, le=datetime.now().year + 1)
    color: str | None = None
    price: float | None = Field(default=None, gt=0)

class VehicleOut(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    color: str
    price: float
    status: VehicleStatus
    createdAt: datetime
    updatedAt: datetime

class SellRequest(BaseModel):
    buyerCpf: str
    saleDate: datetime
    salePrice: float = Field(gt=0)
    paymentCode: str | None = None

    @field_validator("buyerCpf")
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        digits = [c for c in v if c.isdigit()]
        if len(digits) != 11:
            raise ValueError("CPF inválido")
        return v

class PaymentWebhook(BaseModel):
    paymentCode: str
    status: str
