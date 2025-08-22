"""
Sale Controller - Orquestração da Clean Architecture
Responsável por instanciar e coordenar Gateways, UseCases e Presenters
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal

from ..gateways.sale_gateway import SaleGateway, SaleRepositoryInterface
from ..gateways.vehicle_gateway import VehicleGateway, VehicleRepositoryInterface
from ..use_cases.sale_use_cases import (
    CreateSaleUseCase,
    FindSaleByIdUseCase,
    FindSaleByVehicleIdUseCase,
    ListAllSalesUseCase,
    UpdatePaymentStatusUseCase,
    ProcessPaymentWebhookUseCase
)
from ..presenters.sale_presenter import SalePresenter


class SaleController:
    """
    Controller de Vendas - Clean Architecture
    
    Responsabilidades:
    - Receber repositórios externos da Controller Web
    - Instanciar Gateways com repositórios injetados
    - Instanciar Use Cases com Gateways injetados
    - Orquestrar fluxo: UseCase -> Presenter
    - Retornar dados formatados para Controller Web
    """
    
    def __init__(self, sale_repository: SaleRepositoryInterface, 
                 vehicle_repository: VehicleRepositoryInterface):
        # Injeta repositórios nos Gateways (Inversão de Dependência - SOLID)
        self._sale_gateway = SaleGateway(sale_repository)
        self._vehicle_gateway = VehicleGateway(vehicle_repository)
        
        # Injeta Gateways nos Use Cases
        self._create_use_case = CreateSaleUseCase(self._sale_gateway, self._vehicle_gateway)
        self._find_by_id_use_case = FindSaleByIdUseCase(self._sale_gateway)
        self._find_by_vehicle_use_case = FindSaleByVehicleIdUseCase(self._sale_gateway)
        self._list_all_use_case = ListAllSalesUseCase(self._sale_gateway)
        self._update_payment_use_case = UpdatePaymentStatusUseCase(self._sale_gateway)
        self._webhook_use_case = ProcessPaymentWebhookUseCase(self._sale_gateway)
    
    def create_sale(self, vehicle_id: int, customer_cpf: str, amount: Decimal) -> Dict[str, Any]:
        """
        Orquestra criação de venda: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            sale = self._create_use_case.execute(
                vehicle_id=vehicle_id,
                customer_cpf=customer_cpf,
                amount=amount
            )
            
            # Formata resposta via Presenter
            return SalePresenter.to_create_response(sale)
            
        except ValueError as e:
            return SalePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def find_sale_by_id(self, sale_id: int) -> Dict[str, Any]:
        """
        Orquestra busca por ID: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            sale = self._find_by_id_use_case.execute(sale_id)
            
            if not sale:
                return SalePresenter.to_not_found_response(sale_id)
            
            # Formata resposta via Presenter
            return {
                'sale': SalePresenter.to_dict(sale),
                'status': 'found'
            }
            
        except ValueError as e:
            return SalePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def find_sale_by_vehicle_id(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Orquestra busca por ID do veículo: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            sale = self._find_by_vehicle_use_case.execute(vehicle_id)
            
            if not sale:
                return {
                    'error': True,
                    'error_code': 'SALE_NOT_FOUND',
                    'message': f'Venda para veículo {vehicle_id} não encontrada',
                    'vehicle_id': vehicle_id,
                    'status': 'not_found'
                }
            
            # Formata resposta via Presenter
            return {
                'sale': SalePresenter.to_dict(sale),
                'status': 'found'
            }
            
        except ValueError as e:
            return SalePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def list_all_sales(self) -> Dict[str, Any]:
        """
        Orquestra listagem de todas as vendas: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            sales = self._list_all_use_case.execute()
            
            # Formata resposta via Presenter
            return {
                'sales': SalePresenter.to_public_list(sales),  # CPF mascarado
                'total': len(sales),
                'status': 'success'
            }
            
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def update_payment_status(self, sale_id: int, payment_status: str) -> Dict[str, Any]:
        """
        Orquestra atualização de status de pagamento: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            sale = self._update_payment_use_case.execute(
                sale_id=sale_id,
                payment_status=payment_status
            )
            
            # Formata resposta via Presenter
            return SalePresenter.to_payment_update_response(sale)
            
        except ValueError as e:
            return SalePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
    
    def process_payment_webhook(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquestra processamento de webhook: UseCase -> Presenter
        """
        try:
            # Executa Use Case (idempotente)
            result = self._webhook_use_case.execute(payment_data)
            
            # Formata resposta via Presenter
            return SalePresenter.to_webhook_response(result)
            
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'WEBHOOK_ERROR')
    
    def get_payment_status(self, sale_id: int) -> Dict[str, Any]:
        """
        Orquestra consulta de status de pagamento: UseCase -> Presenter
        """
        try:
            # Executa Use Case
            sale = self._find_by_id_use_case.execute(sale_id)
            
            if not sale:
                return SalePresenter.to_not_found_response(sale_id)
            
            # Formata resposta via Presenter
            return {
                'payment_status': SalePresenter.to_payment_status_dict(sale),
                'status': 'success'
            }
            
        except ValueError as e:
            return SalePresenter.to_error_response(str(e), 'VALIDATION_ERROR')
        except Exception as e:
            return SalePresenter.to_error_response(str(e), 'INTERNAL_ERROR')
