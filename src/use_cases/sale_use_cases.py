"""
Use Cases de Vendas - Camada de interação com regras de negócio
Orquestra as operações entre Entities, Gateways e validações de negócio
"""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from ..entities.sale import Sale, PaymentStatus
from ..entities.vehicle import Vehicle
from ..gateways.sale_gateway import SaleGateway
from ..gateways.vehicle_gateway import VehicleGateway


class CreateSaleUseCase:
    """Use Case para criar uma nova venda"""
    
    def __init__(self, sale_gateway: SaleGateway, vehicle_gateway: VehicleGateway):
        self._sale_gateway = sale_gateway
        self._vehicle_gateway = vehicle_gateway
    
    def execute(self, vehicle_id: int, customer_cpf: str, amount: Decimal) -> Sale:
        """
        Executa a criação de uma nova venda
        
        Regras de negócio:
        - Veículo deve existir e estar disponível
        - CPF deve ser válido (validado pela Entity)
        - Valor deve ser positivo
        - Veículo é marcado como vendido
        - Venda criada com status PENDING
        """
        # Verifica se veículo existe e está disponível
        vehicle = self._vehicle_gateway.find_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Veículo com ID {vehicle_id} não encontrado")
        
        if not vehicle.is_available():
            raise ValueError("Veículo não está disponível para venda")
        
        # Verifica se já existe venda para o veículo
        existing_sale = self._sale_gateway.find_sale_by_vehicle_id(vehicle_id)
        if existing_sale:
            raise ValueError("Veículo já possui uma venda registrada")
        
        # Cria a Entity Sale (validações automáticas)
        sale = Sale(
            vehicle_id=vehicle_id,
            customer_cpf=customer_cpf,
            sale_date=datetime.now(),
            amount=amount,
            payment_status=PaymentStatus.PENDING
        )
        
        # Salva a venda
        saved_sale = self._sale_gateway.save_sale(sale)
        
        # Marca o veículo como vendido
        vehicle.mark_as_sold()
        self._vehicle_gateway.update_vehicle(vehicle)
        
        return saved_sale


class FindSaleByIdUseCase:
    """Use Case para buscar uma venda por ID"""
    
    def __init__(self, sale_gateway: SaleGateway):
        self._sale_gateway = sale_gateway
    
    def execute(self, sale_id: int) -> Optional[Sale]:
        """
        Executa a busca de uma venda por ID
        
        Regras de negócio:
        - ID deve ser válido (número positivo)
        - Retorna None se não encontrado
        """
        if not isinstance(sale_id, int) or sale_id <= 0:
            raise ValueError("ID da venda deve ser um número positivo")
        
        return self._sale_gateway.find_sale_by_id(sale_id)


class FindSaleByVehicleIdUseCase:
    """Use Case para buscar uma venda por ID do veículo"""
    
    def __init__(self, sale_gateway: SaleGateway):
        self._sale_gateway = sale_gateway
    
    def execute(self, vehicle_id: int) -> Optional[Sale]:
        """
        Executa a busca de uma venda por ID do veículo
        
        Regras de negócio:
        - ID do veículo deve ser válido
        - Retorna None se não encontrado
        """
        if not isinstance(vehicle_id, int) or vehicle_id <= 0:
            raise ValueError("ID do veículo deve ser um número positivo")
        
        return self._sale_gateway.find_sale_by_vehicle_id(vehicle_id)


class ListAllSalesUseCase:
    """Use Case para listar todas as vendas"""
    
    def __init__(self, sale_gateway: SaleGateway):
        self._sale_gateway = sale_gateway
    
    def execute(self) -> List[Sale]:
        """
        Executa a listagem de todas as vendas
        
        Regras de negócio:
        - Retorna lista vazia se não houver vendas
        """
        return self._sale_gateway.find_all_sales()


class UpdatePaymentStatusUseCase:
    """Use Case para atualizar status de pagamento (webhook)"""
    
    def __init__(self, sale_gateway: SaleGateway):
        self._sale_gateway = sale_gateway
    
    def execute(self, sale_id: int, payment_status: str) -> Sale:
        """
        Executa a atualização do status de pagamento
        
        Regras de negócio:
        - Venda deve existir
        - Status deve ser válido (approved/rejected)
        - Operação deve ser idempotente
        - Transições de status devem ser respeitadas
        """
        # Busca a venda
        sale = self._sale_gateway.find_sale_by_id(sale_id)
        if not sale:
            raise ValueError(f"Venda com ID {sale_id} não encontrada")
        
        # Valida e normaliza o status
        payment_status = payment_status.lower().strip()
        if payment_status not in ['approved', 'rejected']:
            raise ValueError("Status de pagamento deve ser 'approved' ou 'rejected'")
        
        # Aplica a mudança de status (com validações da Entity)
        if payment_status == 'approved':
            sale.approve_payment()
        else:
            sale.reject_payment()
        
        # Persiste a alteração
        return self._sale_gateway.update_sale(sale)


class ProcessPaymentWebhookUseCase:
    """Use Case para processar webhook de pagamento (idempotente)"""
    
    def __init__(self, sale_gateway: SaleGateway):
        self._sale_gateway = sale_gateway
    
    def execute(self, payment_data: dict) -> dict:
        """
        Executa o processamento de webhook de pagamento
        
        Regras de negócio:
        - Deve ser idempotente
        - Valida estrutura dos dados
        - Atualiza status conforme necessário
        - Retorna resultado da operação
        """
        # Valida dados obrigatórios
        required_fields = ['sale_id', 'status']
        for field in required_fields:
            if field not in payment_data:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        sale_id = payment_data['sale_id']
        status = payment_data['status']
        
        # Valida tipos
        if not isinstance(sale_id, int):
            raise ValueError("sale_id deve ser um número inteiro")
        
        # Processa a atualização
        try:
            updated_sale = UpdatePaymentStatusUseCase(self._sale_gateway).execute(
                sale_id=sale_id,
                payment_status=status
            )
            
            return {
                'success': True,
                'sale_id': updated_sale.id,
                'previous_status': payment_data.get('previous_status', 'unknown'),
                'current_status': updated_sale.payment_status.value,
                'message': 'Status de pagamento atualizado com sucesso',
                'timestamp': datetime.now().isoformat()
            }
            
        except ValueError as e:
            # Retorna erro mas mantém idempotência
            return {
                'success': False,
                'sale_id': sale_id,
                'error': str(e),
                'message': 'Erro ao processar webhook de pagamento',
                'timestamp': datetime.now().isoformat()
            }
