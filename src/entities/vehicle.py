"""
Entidade Vehicle - Camada mais pura da Clean Architecture
Contém apenas regras de negócio sem dependências externas
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
import re


class VehicleStatus(Enum):
    """Status disponíveis para um veículo"""
    AVAILABLE = "available"
    SOLD = "sold"


class Vehicle:
    """
    Entidade Vehicle - Representa um veículo no domínio
    
    Contém:
    - Atributos essenciais do veículo
    - Regras de negócio puras (validações)
    - Lógica de domínio sem dependências externas
    """
    
    def __init__(
        self,
        brand: str,
        model: str,
        year: int,
        price: Decimal,
        color: str,
        vehicle_id: Optional[int] = None,
        status: VehicleStatus = VehicleStatus.AVAILABLE,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = vehicle_id
        self._brand = self._validate_brand(brand)
        self._model = self._validate_model(model)
        self._year = self._validate_year(year)
        self._price = self._validate_price(price)
        self._color = self._validate_color(color)
        self._status = status
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()
    
    # Getters (properties)
    @property
    def id(self) -> Optional[int]:
        return self._id
    
    @property
    def brand(self) -> str:
        return self._brand
    
    @property
    def model(self) -> str:
        return self._model
    
    @property
    def year(self) -> int:
        return self._year
    
    @property
    def price(self) -> Decimal:
        return self._price
    
    @property
    def color(self) -> str:
        return self._color
    
    @property
    def status(self) -> VehicleStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Métodos de negócio
    def is_available(self) -> bool:
        """Verifica se o veículo está disponível para venda"""
        return self._status == VehicleStatus.AVAILABLE
    
    def mark_as_sold(self) -> None:
        """Marca o veículo como vendido"""
        if not self.is_available():
            raise ValueError("Veículo já foi vendido")
        self._status = VehicleStatus.SOLD
        self._updated_at = datetime.now()
    
    def update_price(self, new_price: Decimal) -> None:
        """Atualiza o preço do veículo"""
        if not self.is_available():
            raise ValueError("Não é possível alterar preço de veículo vendido")
        self._price = self._validate_price(new_price)
        self._updated_at = datetime.now()
    
    def update_details(self, brand: str = None, model: str = None, 
                      year: int = None, color: str = None) -> None:
        """Atualiza detalhes do veículo"""
        if not self.is_available():
            raise ValueError("Não é possível alterar veículo vendido")
        
        if brand:
            self._brand = self._validate_brand(brand)
        if model:
            self._model = self._validate_model(model)
        if year:
            self._year = self._validate_year(year)
        if color:
            self._color = self._validate_color(color)
        
        self._updated_at = datetime.now()
    
    # Validações de negócio (regras puras)
    def _validate_brand(self, brand: str) -> str:
        """Valida a marca do veículo"""
        if not brand or not isinstance(brand, str):
            raise ValueError("Marca é obrigatória e deve ser uma string")
        
        brand = brand.strip()
        if len(brand) < 2:
            raise ValueError("Marca deve ter pelo menos 2 caracteres")
        if len(brand) > 50:
            raise ValueError("Marca deve ter no máximo 50 caracteres")
        
        # Apenas letras, números e espaços
        if not re.match(r'^[a-zA-Z0-9\s]+$', brand):
            raise ValueError("Marca deve conter apenas letras, números e espaços")
        
        return brand.title()  # Primeira letra maiúscula
    
    def _validate_model(self, model: str) -> str:
        """Valida o modelo do veículo"""
        if not model or not isinstance(model, str):
            raise ValueError("Modelo é obrigatório e deve ser uma string")
        
        model = model.strip()
        if len(model) < 1:
            raise ValueError("Modelo deve ter pelo menos 1 caractere")
        if len(model) > 100:
            raise ValueError("Modelo deve ter no máximo 100 caracteres")
        
        return model.title()
    
    def _validate_year(self, year: int) -> int:
        """Valida o ano do veículo"""
        if not isinstance(year, int):
            raise ValueError("Ano deve ser um número inteiro")
        
        current_year = datetime.now().year
        if year < 1900:
            raise ValueError("Ano deve ser maior que 1900")
        if year > current_year + 1:
            raise ValueError(f"Ano não pode ser maior que {current_year + 1}")
        
        return year
    
    def _validate_price(self, price: Decimal) -> Decimal:
        """Valida o preço do veículo"""
        if not isinstance(price, (Decimal, int, float)):
            raise ValueError("Preço deve ser um número")
        
        price = Decimal(str(price))
        
        if price <= 0:
            raise ValueError("Preço deve ser maior que zero")
        if price > Decimal('9999999.99'):
            raise ValueError("Preço deve ser menor que R$ 9.999.999,99")
        
        return price.quantize(Decimal('0.01'))  # 2 casas decimais
    
    def _validate_color(self, color: str) -> str:
        """Valida a cor do veículo"""
        if not color or not isinstance(color, str):
            raise ValueError("Cor é obrigatória e deve ser uma string")
        
        color = color.strip()
        if len(color) < 3:
            raise ValueError("Cor deve ter pelo menos 3 caracteres")
        if len(color) > 30:
            raise ValueError("Cor deve ter no máximo 30 caracteres")
        
        # Apenas letras e espaços
        if not re.match(r'^[a-zA-Z\s]+$', color):
            raise ValueError("Cor deve conter apenas letras e espaços")
        
        return color.title()
    
    def __str__(self) -> str:
        return f"{self._brand} {self._model} {self._year} - {self._color} - R$ {self._price}"
    
    def __repr__(self) -> str:
        return (f"Vehicle(id={self._id}, brand='{self._brand}', model='{self._model}', "
                f"year={self._year}, price={self._price}, color='{self._color}', "
                f"status={self._status.value})")
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vehicle):
            return False
        return (self._brand == other._brand and 
                self._model == other._model and
                self._year == other._year and
                self._color == other._color)
