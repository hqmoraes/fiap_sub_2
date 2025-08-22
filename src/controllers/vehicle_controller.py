"""
Vehicle Controller - Orquestração da Clean Architecture
Responsável por instanciar e coordenar Gateway, UseCase e Presenter
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal

from ..gateways.vehicle_gateway import VehicleGateway, VehicleRepositoryInterface
from ..use_cases.vehicle_use_cases import (
    CreateVehicleUseCase,
    FindVehicleByIdUseCase,
    ListAllVehiclesUseCase,
    ListAvailableVehiclesUseCase,
    ListSoldVehiclesUseCase,
    UpdateVehicleUseCase,
    DeleteVehicleUseCase,
    MarkVehicleAsSoldUseCase
)
from ..presenters.vehicle_presenter import VehiclePresenter


class VehicleController:
    """
    Controller de Veículos - Clean Architecture
    
    Responsabilidades:
    - Receber repositório externo da Controller Web
    - Instanciar Gateway com repositório injetado
    - Instanciar Use Cases com Gateway injetado
    - Orquestrar fluxo: UseCase -> Presenter
    - Retornar dados formatados para Controller Web
    """
    
    def __init__(self, repository: VehicleRepositoryInterface):
        # Injeta repositório no Gateway (Inversão de Dependência - SOLID)
        self._gateway = VehicleGateway(repository)
        
        # Injeta Gateway nos Use Cases
        self._create_use_case = CreateVehicleUseCase(self._gateway)
        self._find_by_id_use_case = FindVehicleByIdUseCase(self._gateway)
        self._list_all_use_case = ListAllVehiclesUseCase(self._gateway)
        self._list_available_use_case = ListAvailableVehiclesUseCase(self._gateway)
        self._list_sold_use_case = ListSoldVehiclesUseCase(self._gateway)
        self._update_use_case = UpdateVehicleUseCase(self._gateway)
        self._delete_use_case = DeleteVehicleUseCase(self._gateway)
        self._mark_sold_use_case = MarkVehicleAsSoldUseCase(self._gateway)
    
    def create_vehicle(self, brand: str, model: str, year: int, 
                      price: Decimal, color: str) -> Dict[str, Any]:
        """
        Orquestra criação de veículo: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicle = self._create_use_case.execute(
                brand=brand,
                model=model,
                year=year,
                price=price,
                color=color
            )
            
            # Formata resposta via Presenter
            return VehiclePresenter.to_create_response(vehicle)
            
        except ValueError as e:
            return VehiclePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def find_vehicle_by_id(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Orquestra busca por ID: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicle = self._find_by_id_use_case.execute(vehicle_id)
            
            if not vehicle:
                return VehiclePresenter.to_not_found_response(vehicle_id)
            
            # Formata resposta via Presenter
            return {
                'vehicle': VehiclePresenter.to_dict(vehicle),
                'status': 'found'
            }
            
        except ValueError as e:
            return VehiclePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def list_all_vehicles(self) -> Dict[str, Any]:
        """
        Orquestra listagem de todos os veículos: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicles = self._list_all_use_case.execute()
            
            # Formata resposta via Presenter
            return {
                'vehicles': VehiclePresenter.to_list(vehicles),
                'total': len(vehicles),
                'status': 'success'
            }
            
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def list_available_vehicles(self) -> Dict[str, Any]:
        """
        Orquestra listagem de veículos disponíveis: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicles = self._list_available_use_case.execute()
            
            # Formata resposta via Presenter
            return {
                'vehicles': VehiclePresenter.to_public_list(vehicles),
                'total': len(vehicles),
                'status': 'success',
                'filter': 'available_only'
            }
            
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def list_sold_vehicles(self) -> Dict[str, Any]:
        """
        Orquestra listagem de veículos vendidos: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicles = self._list_sold_use_case.execute()
            
            # Formata resposta via Presenter
            return {
                'vehicles': VehiclePresenter.to_public_list(vehicles),
                'total': len(vehicles),
                'status': 'success',
                'filter': 'sold_only'
            }
            
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def update_vehicle(self, vehicle_id: int, brand: str = None, model: str = None,
                      year: int = None, price: Decimal = None, color: str = None) -> Dict[str, Any]:
        """
        Orquestra atualização de veículo: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicle = self._update_use_case.execute(
                vehicle_id=vehicle_id,
                brand=brand,
                model=model,
                year=year,
                price=price,
                color=color
            )
            
            # Formata resposta via Presenter
            return VehiclePresenter.to_update_response(vehicle)
            
        except ValueError as e:
            return VehiclePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def delete_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Orquestra exclusão de veículo: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            success = self._delete_use_case.execute(vehicle_id)
            
            if success:
                # Formata resposta via Presenter
                return VehiclePresenter.to_delete_response(vehicle_id)
            else:
                return VehiclePresenter.to_error_response(
                    "Falha ao excluir veículo", 'DELETE_ERROR'
                )
            
        except ValueError as e:
            return VehiclePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def mark_vehicle_as_sold(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Orquestra marcação como vendido: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            vehicle = self._mark_sold_use_case.execute(vehicle_id)
            
            # Formata resposta via Presenter
            return {
                'message': 'Veículo marcado como vendido',
                'vehicle': VehiclePresenter.to_dict(vehicle),
                'status': 'sold'
            }
            
        except ValueError as e:
            return VehiclePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return VehiclePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
