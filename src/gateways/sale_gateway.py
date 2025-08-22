"""
Gateway de Vendas - Interface entre o mundo interno (Entity) e externo (Repository)
Responsável por traduzir dados do repositório para Entity e vice-versa
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal

from ..entities.sale import Sale, PaymentStatus


class SaleRepositoryInterface(ABC):
    """Interface abstrata para o repositório de vendas (mundo externo)"""
    
    @abstractmethod
    def save(self, sale_data: dict) -> dict:
        """Salva uma venda no repositório externo"""
        pass
    
    @abstractmethod
    def find_by_id(self, sale_id: int) -> Optional[dict]:
        """Busca uma venda por ID no repositório externo"""
        pass
    
    @abstractmethod
    def find_by_vehicle_id(self, vehicle_id: int) -> Optional[dict]:
        """Busca uma venda por ID do veículo"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[dict]:
        """Busca todas as vendas no repositório externo"""
        pass
    
    @abstractmethod
    def update(self, sale_id: int, sale_data: dict) -> dict:
        """Atualiza uma venda no repositório externo"""
        pass


class SaleGateway:
    """
    Gateway de Vendas - Tradutor entre Entity e Repository
    
    Responsabilidades:
    - Converter Entity para DTO/DAO para o repositório
    - Converter dados do repositório para Entity
    - Abstrair o repositório para o mundo interno
    """
    
    def __init__(self, repository: SaleRepositoryInterface):
        self._repository = repository
    
    def save_sale(self, sale: Sale) -> Sale:
        """
        Salva uma venda convertendo Entity -> DTO -> Repository -> Entity
        """
        # Converte Entity para DTO (mundo externo)
        sale_data = self._entity_to_dict(sale)
        
        # Salva no repositório externo
        saved_data = self._repository.save(sale_data)
        
        # Converte dados salvos de volta para Entity
        return self._dict_to_entity(saved_data)
    
    def find_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """
        Busca uma venda por ID convertendo Repository -> Entity
        """
        # Busca no repositório externo
        sale_data = self._repository.find_by_id(sale_id)
        
        if not sale_data:
            return None
        
        # Converte dados do repositório para Entity
        return self._dict_to_entity(sale_data)
    
    def find_sale_by_vehicle_id(self, vehicle_id: int) -> Optional[Sale]:
        """
        Busca uma venda por ID do veículo
        """
        sale_data = self._repository.find_by_vehicle_id(vehicle_id)
        
        if not sale_data:
            return None
        
        return self._dict_to_entity(sale_data)
    
    def find_all_sales(self) -> List[Sale]:
        """
        Busca todas as vendas convertendo Repository -> List[Entity]
        """
        # Busca no repositório externo
        sales_data = self._repository.find_all()
        
        # Converte lista de dados para lista de Entities
        return [self._dict_to_entity(data) for data in sales_data]
    
    def update_sale(self, sale: Sale) -> Sale:
        """
        Atualiza uma venda convertendo Entity -> DTO -> Repository -> Entity
        """
        if not sale.id:
            raise ValueError("Venda deve ter ID para ser atualizada")
        
        # Converte Entity para DTO
        sale_data = self._entity_to_dict(sale)
        
        # Atualiza no repositório externo
        updated_data = self._repository.update(sale.id, sale_data)
        
        # Converte dados atualizados de volta para Entity
        return self._dict_to_entity(updated_data)
    
    def _entity_to_dict(self, sale: Sale) -> dict:
        """
        Converte Entity Sale para dicionário (DTO para mundo externo)
        """
        return {
            'id': sale.id,
            'vehicle_id': sale.vehicle_id,
            'customer_cpf': sale.customer_cpf,
            'sale_date': sale.sale_date,
            'amount': float(sale.amount),  # Decimal -> float para persistência
            'payment_status': sale.payment_status.value,  # Enum -> string
            'created_at': sale.created_at,
            'updated_at': sale.updated_at
        }
    
    def _dict_to_entity(self, data: dict) -> Sale:
        """
        Converte dicionário (dados do repositório) para Entity Sale
        """
        return Sale(
            sale_id=data.get('id'),
            vehicle_id=data['vehicle_id'],
            customer_cpf=data['customer_cpf'],
            sale_date=data['sale_date'],
            amount=Decimal(str(data['amount'])),  # float -> Decimal
            payment_status=PaymentStatus(data['payment_status']),  # string -> Enum
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
