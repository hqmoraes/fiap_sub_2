"""
Use Cases de Veículos - Camada de interação com regras de negócio
Orquestra as operações entre Entities e Gateways
"""
from typing import List, Optional
from decimal import Decimal

from ..entities.vehicle import Vehicle, VehicleStatus
from ..gateways.vehicle_gateway import VehicleGateway


class CreateVehicleUseCase:
    """Use Case para criar um novo veículo"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self, brand: str, model: str, year: int, price: Decimal, color: str) -> Vehicle:
        """
        Executa a criação de um novo veículo
        
        Regras de negócio:
        - Todos os dados devem ser válidos (validado pela Entity)
        - Veículo criado sempre com status AVAILABLE
        """
        # Cria a Entity (validações automáticas)
        vehicle = Vehicle(
            brand=brand,
            model=model,
            year=year,
            price=price,
            color=color,
            status=VehicleStatus.AVAILABLE
        )
        
        # Persiste através do Gateway
        return self._vehicle_gateway.save_vehicle(vehicle)


class FindVehicleByIdUseCase:
    """Use Case para buscar um veículo por ID"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self, vehicle_id: int) -> Optional[Vehicle]:
        """
        Executa a busca de um veículo por ID
        
        Regras de negócio:
        - ID deve ser válido (número positivo)
        - Retorna None se não encontrado
        """
        if not isinstance(vehicle_id, int) or vehicle_id <= 0:
            raise ValueError("ID do veículo deve ser um número positivo")
        
        return self._vehicle_gateway.find_vehicle_by_id(vehicle_id)


class ListAllVehiclesUseCase:
    """Use Case para listar todos os veículos"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self) -> List[Vehicle]:
        """
        Executa a listagem de todos os veículos
        
        Regras de negócio:
        - Retorna lista vazia se não houver veículos
        """
        return self._vehicle_gateway.find_all_vehicles()


class ListAvailableVehiclesUseCase:
    """Use Case para listar veículos disponíveis ordenados por preço"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self) -> List[Vehicle]:
        """
        Executa a listagem de veículos disponíveis ordenados por preço
        
        Regras de negócio:
        - Apenas veículos com status AVAILABLE
        - Ordenados por preço crescente
        """
        return self._vehicle_gateway.find_available_vehicles_ordered_by_price()


class ListSoldVehiclesUseCase:
    """Use Case para listar veículos vendidos ordenados por preço"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self) -> List[Vehicle]:
        """
        Executa a listagem de veículos vendidos ordenados por preço
        
        Regras de negócio:
        - Apenas veículos com status SOLD
        - Ordenados por preço crescente
        """
        return self._vehicle_gateway.find_sold_vehicles_ordered_by_price()


class UpdateVehicleUseCase:
    """Use Case para atualizar um veículo"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self, vehicle_id: int, brand: str = None, model: str = None, 
                year: int = None, price: Decimal = None, color: str = None) -> Vehicle:
        """
        Executa a atualização de um veículo
        
        Regras de negócio:
        - Veículo deve existir
        - Apenas veículos disponíveis podem ser alterados
        - Validações feitas pela Entity
        """
        # Busca o veículo atual
        vehicle = self._vehicle_gateway.find_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Veículo com ID {vehicle_id} não encontrado")
        
        # Atualiza os dados (com validações da Entity)
        if brand or model or year or color:
            vehicle.update_details(brand=brand, model=model, year=year, color=color)
        
        if price is not None:
            vehicle.update_price(price)
        
        # Persiste as alterações
        return self._vehicle_gateway.update_vehicle(vehicle)


class DeleteVehicleUseCase:
    """Use Case para deletar um veículo"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self, vehicle_id: int) -> bool:
        """
        Executa a exclusão de um veículo
        
        Regras de negócio:
        - Veículo deve existir
        - Apenas veículos disponíveis podem ser deletados
        """
        # Busca o veículo
        vehicle = self._vehicle_gateway.find_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Veículo com ID {vehicle_id} não encontrado")
        
        # Verifica se pode ser deletado
        if not vehicle.is_available():
            raise ValueError("Não é possível deletar veículo vendido")
        
        # Deleta através do Gateway
        return self._vehicle_gateway.delete_vehicle(vehicle_id)


class MarkVehicleAsSoldUseCase:
    """Use Case para marcar um veículo como vendido"""
    
    def __init__(self, vehicle_gateway: VehicleGateway):
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self, vehicle_id: int) -> Vehicle:
        """
        Executa a marcação de um veículo como vendido
        
        Regras de negócio:
        - Veículo deve existir
        - Veículo deve estar disponível
        """
        # Busca o veículo
        vehicle = self._vehicle_gateway.find_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Veículo com ID {vehicle_id} não encontrado")
        
        # Marca como vendido (validação na Entity)
        vehicle.mark_as_sold()
        
        # Persiste a alteração
        return self._vehicle_gateway.update_vehicle(vehicle)
