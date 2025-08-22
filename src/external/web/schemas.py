"""
Schemas Pydantic para validação de dados da API
Camada externa - validação de entrada e saída HTTP
"""
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime


class VehicleCreate(BaseModel):
    """Schema para criação de veículo"""
    brand: str = Field(..., min_length=2, max_length=50, description="Marca do veículo")
    model: str = Field(..., min_length=1, max_length=100, description="Modelo do veículo")
    year: int = Field(..., ge=1900, le=2030, description="Ano do veículo")
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Preço do veículo")
    color: str = Field(..., min_length=3, max_length=30, description="Cor do veículo")
    
    @validator('brand', 'color')
    def validate_text_fields(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('Deve conter apenas letras e espaços')
        return v.title()
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError(f'Ano não pode ser maior que {current_year + 1}')
        return v


class VehicleUpdate(BaseModel):
    """Schema para atualização de veículo"""
    brand: Optional[str] = Field(None, min_length=2, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    color: Optional[str] = Field(None, min_length=3, max_length=30)
    
    @validator('brand', 'color')
    def validate_text_fields(cls, v):
        if v and not v.replace(' ', '').isalpha():
            raise ValueError('Deve conter apenas letras e espaços')
        return v.title() if v else v
    
    @validator('year')
    def validate_year(cls, v):
        if v:
            current_year = datetime.now().year
            if v > current_year + 1:
                raise ValueError(f'Ano não pode ser maior que {current_year + 1}')
        return v


class VehicleResponse(BaseModel):
    """Schema de resposta para veículo"""
    id: int
    brand: str
    model: str
    year: int
    price: Decimal
    color: str
    status: str
    created_at: datetime
    updated_at: datetime


class SaleCreate(BaseModel):
    """Schema para criação de venda"""
    vehicle_id: int = Field(..., gt=0, description="ID do veículo")
    customer_cpf: str = Field(..., min_length=11, max_length=14, description="CPF do cliente")
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Valor da venda")
    
    @validator('customer_cpf')
    def validate_cpf_format(cls, v):
        # Remove caracteres não numéricos
        numbers_only = ''.join(filter(str.isdigit, v))
        if len(numbers_only) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v


class SaleResponse(BaseModel):
    """Schema de resposta para venda"""
    id: int
    vehicle_id: int
    customer_cpf: str
    sale_date: datetime
    amount: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime


class PaymentWebhook(BaseModel):
    """Schema para webhook de pagamento"""
    sale_id: int = Field(..., gt=0, description="ID da venda")
    status: str = Field(..., description="Status do pagamento")
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['approved', 'rejected']
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Status deve ser um de: {allowed_statuses}')
        return v.lower()


class PaymentStatusUpdate(BaseModel):
    """Schema para atualização de status de pagamento"""
    payment_status: str = Field(..., description="Novo status do pagamento")
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        allowed_statuses = ['approved', 'rejected']
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Status deve ser um de: {allowed_statuses}')
        return v.lower()
