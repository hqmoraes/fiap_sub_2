"""
Gateway de Veículos - Interface entre o mundo interno (Entity) e externo (Repository)
Responsável por traduzir dados do repositório para Entity e vice-versa
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal

from ..entities.vehicle import Vehicle, VehicleStatus


class VehicleRepositoryInterface(ABC):
    """Interface abstrata para o repositório de veículos (mundo externo)"""
    
    @abstractmethod
    def save(self, vehicle_data: dict) -> dict:
        """Salva um veículo no repositório externo"""
        pass
    
    @abstractmethod
    def find_by_id(self, vehicle_id: int) -> Optional[dict]:
        """Busca um veículo por ID no repositório externo"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[dict]:
        """Busca todos os veículos no repositório externo"""
        pass
    
    @abstractmethod
    def find_available_ordered_by_price(self) -> List[dict]:
        """Busca veículos disponíveis ordenados por preço"""
        pass
    
    @abstractmethod
    def find_sold_ordered_by_price(self) -> List[dict]:
        """Busca veículos vendidos ordenados por preço"""
        pass
    
    @abstractmethod
    def update(self, vehicle_id: int, vehicle_data: dict) -> dict:
        """Atualiza um veículo no repositório externo"""
        pass
    
    @abstractmethod
    def delete(self, vehicle_id: int) -> bool:
        """Remove um veículo do repositório externo"""
        pass


class VehicleGateway:
    """
    Gateway de Veículos - Tradutor entre Entity e Repository
    
    Responsabilidades:
    - Converter Entity para DTO/DAO para o repositório
    - Converter dados do repositório para Entity
    - Abstrair o repositório para o mundo interno
    """
    
    def __init__(self, repository: VehicleRepositoryInterface):
        self._repository = repository
    
    def save_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Salva um veículo convertendo Entity -> DTO -> Repository -> Entity
        """
        # Converte Entity para DTO (mundo externo)
        vehicle_data = self._entity_to_dict(vehicle)
        
        # Salva no repositório externo
        saved_data = self._repository.save(vehicle_data)
        
        # Converte dados salvos de volta para Entity
        return self._dict_to_entity(saved_data)
    
    def find_vehicle_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        """
        Busca um veículo por ID convertendo Repository -> Entity
        """
        # Busca no repositório externo
        vehicle_data = self._repository.find_by_id(vehicle_id)
        
        if not vehicle_data:
            return None
        
        # Converte dados do repositório para Entity
        return self._dict_to_entity(vehicle_data)
    
    def find_all_vehicles(self) -> List[Vehicle]:
        """
        Busca todos os veículos convertendo Repository -> List[Entity]
        """
        # Busca no repositório externo
        vehicles_data = self._repository.find_all()
        
        # Converte lista de dados para lista de Entities
        return [self._dict_to_entity(data) for data in vehicles_data]
    
    def find_available_vehicles_ordered_by_price(self) -> List[Vehicle]:
        """
        Busca veículos disponíveis ordenados por preço
        """
        vehicles_data = self._repository.find_available_ordered_by_price()
        return [self._dict_to_entity(data) for data in vehicles_data]
    
    def find_sold_vehicles_ordered_by_price(self) -> List[Vehicle]:
        """
        Busca veículos vendidos ordenados por preço
        """
        vehicles_data = self._repository.find_sold_ordered_by_price()
        return [self._dict_to_entity(data) for data in vehicles_data]
    
    def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Atualiza um veículo convertendo Entity -> DTO -> Repository -> Entity
        """
        if not vehicle.id:
            raise ValueError("Veículo deve ter ID para ser atualizado")
        
        # Converte Entity para DTO
        vehicle_data = self._entity_to_dict(vehicle)
        
        # Atualiza no repositório externo
        updated_data = self._repository.update(vehicle.id, vehicle_data)
        
        # Converte dados atualizados de volta para Entity
        return self._dict_to_entity(updated_data)
    
    def delete_vehicle(self, vehicle_id: int) -> bool:
        """
        Remove um veículo do repositório
        """
        return self._repository.delete(vehicle_id)
    
    def _entity_to_dict(self, vehicle: Vehicle) -> dict:
        """
        Converte Entity Vehicle para dicionário (DTO para mundo externo)
        """
        return {
            'id': vehicle.id,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'year': vehicle.year,
            'price': float(vehicle.price),  # Decimal -> float para persistência
            'color': vehicle.color,
            'status': vehicle.status.value,  # Enum -> string
            'created_at': vehicle.created_at,
            'updated_at': vehicle.updated_at
        }
    
    def _dict_to_entity(self, data: dict) -> Vehicle:
        """
        Converte dicionário (dados do repositório) para Entity Vehicle
        """
        return Vehicle(
            vehicle_id=data.get('id'),
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            price=Decimal(str(data['price'])),  # float -> Decimal
            color=data['color'],
            status=VehicleStatus(data['status'].lower()),  # string -> Enum (lowercase)
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
