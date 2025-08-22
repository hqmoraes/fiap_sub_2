"""
Presenters de Veículos - Formatação de saída para o mundo externo
Converte Entities para DTOs/Responses para diferentes tipos de saída
"""
from typing import List, Dict, Any
from decimal import Decimal

from ..entities.vehicle import Vehicle


class VehiclePresenter:
    """
    Presenter para formatação de saída de veículos
    
    Responsabilidades:
    - Converter Entity Vehicle para diferentes formatos de saída
    - Formatação para API REST (JSON)
    - Formatação para relatórios
    - Mascaramento de dados sensíveis quando necessário
    """
    
    @staticmethod
    def to_dict(vehicle: Vehicle) -> Dict[str, Any]:
        """
        Converte Vehicle Entity para dicionário (formato API)
        """
        return {
            'id': vehicle.id,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'year': vehicle.year,
            'price': float(vehicle.price),
            'color': vehicle.color,
            'status': vehicle.status.value,
            'created_at': vehicle.created_at.isoformat() if vehicle.created_at else None,
            'updated_at': vehicle.updated_at.isoformat() if vehicle.updated_at else None
        }
    
    @staticmethod
    def to_list(vehicles: List[Vehicle]) -> List[Dict[str, Any]]:
        """
        Converte lista de Vehicle Entities para lista de dicionários
        """
        return [VehiclePresenter.to_dict(vehicle) for vehicle in vehicles]
    
    @staticmethod
    def to_summary_dict(vehicle: Vehicle) -> Dict[str, Any]:
        """
        Converte Vehicle Entity para resumo (formato compacto)
        """
        return {
            'id': vehicle.id,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'year': vehicle.year,
            'price': float(vehicle.price),
            'status': vehicle.status.value
        }
    
    @staticmethod
    def to_summary_list(vehicles: List[Vehicle]) -> List[Dict[str, Any]]:
        """
        Converte lista de Vehicle Entities para lista de resumos
        """
        return [VehiclePresenter.to_summary_dict(vehicle) for vehicle in vehicles]
    
    @staticmethod
    def to_public_dict(vehicle: Vehicle) -> Dict[str, Any]:
        """
        Converte Vehicle Entity para formato público (sem dados internos)
        """
        return {
            'id': vehicle.id,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'year': vehicle.year,
            'price': float(vehicle.price),
            'color': vehicle.color,
            'status': vehicle.status.value
        }
    
    @staticmethod
    def to_public_list(vehicles: List[Vehicle]) -> List[Dict[str, Any]]:
        """
        Converte lista de Vehicle Entities para formato público
        """
        return [VehiclePresenter.to_public_dict(vehicle) for vehicle in vehicles]
    
    @staticmethod
    def to_create_response(vehicle: Vehicle) -> Dict[str, Any]:
        """
        Formato de resposta para criação de veículo
        """
        return {
            'message': 'Veículo criado com sucesso',
            'vehicle': VehiclePresenter.to_dict(vehicle),
            'status': 'created'
        }
    
    @staticmethod
    def to_update_response(vehicle: Vehicle) -> Dict[str, Any]:
        """
        Formato de resposta para atualização de veículo
        """
        return {
            'message': 'Veículo atualizado com sucesso',
            'vehicle': VehiclePresenter.to_dict(vehicle),
            'status': 'updated'
        }
    
    @staticmethod
    def to_delete_response(vehicle_id: int) -> Dict[str, Any]:
        """
        Formato de resposta para exclusão de veículo
        """
        return {
            'message': 'Veículo excluído com sucesso',
            'vehicle_id': vehicle_id,
            'status': 'deleted'
        }
    
    @staticmethod
    def to_error_response(error_message: str, error_code: str = 'VEHICLE_ERROR') -> Dict[str, Any]:
        """
        Formato de resposta para erros relacionados a veículos
        """
        return {
            'error': True,
            'error_code': error_code,
            'message': error_message,
            'status': 'error'
        }
    
    @staticmethod
    def to_not_found_response(vehicle_id: int) -> Dict[str, Any]:
        """
        Formato de resposta para veículo não encontrado
        """
        return {
            'error': True,
            'error_code': 'VEHICLE_NOT_FOUND',
            'message': f'Veículo com ID {vehicle_id} não encontrado',
            'vehicle_id': vehicle_id,
            'status': 'not_found'
        }
    
    @staticmethod
    def format_price(price: Decimal) -> str:
        """
        Formata preço para exibição em formato brasileiro
        """
        return f"R$ {price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def to_display_string(vehicle: Vehicle) -> str:
        """
        Converte Vehicle Entity para string de exibição amigável
        """
        price_formatted = VehiclePresenter.format_price(vehicle.price)
        status_text = "Disponível" if vehicle.is_available() else "Vendido"
        return f"{vehicle.brand} {vehicle.model} {vehicle.year} - {vehicle.color} - {price_formatted} ({status_text})"
