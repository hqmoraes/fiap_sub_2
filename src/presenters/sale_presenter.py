"""
Presenters de Vendas - Formatação de saída para o mundo externo
Converte Entities para DTOs/Responses para diferentes tipos de saída
"""
from typing import List, Dict, Any
from decimal import Decimal

from ..entities.sale import Sale


class SalePresenter:
    """
    Presenter para formatação de saída de vendas
    
    Responsabilidades:
    - Converter Entity Sale para diferentes formatos de saída
    - Formatação para API REST (JSON)
    - Formatação para webhooks
    - Mascaramento de dados sensíveis quando necessário
    """
    
    @staticmethod
    def to_dict(sale: Sale) -> Dict[str, Any]:
        """
        Converte Sale Entity para dicionário (formato API)
        """
        return {
            'id': sale.id,
            'vehicle_id': sale.vehicle_id,
            'customer_cpf': sale.customer_cpf,
            'sale_date': sale.sale_date.isoformat(),
            'amount': float(sale.amount),
            'payment_status': sale.payment_status.value,
            'created_at': sale.created_at.isoformat() if sale.created_at else None,
            'updated_at': sale.updated_at.isoformat() if sale.updated_at else None
        }
    
    @staticmethod
    def to_list(sales: List[Sale]) -> List[Dict[str, Any]]:
        """
        Converte lista de Sale Entities para lista de dicionários
        """
        return [SalePresenter.to_dict(sale) for sale in sales]
    
    @staticmethod
    def to_summary_dict(sale: Sale) -> Dict[str, Any]:
        """
        Converte Sale Entity para resumo (formato compacto)
        """
        return {
            'id': sale.id,
            'vehicle_id': sale.vehicle_id,
            'customer_cpf': SalePresenter._mask_cpf(sale.customer_cpf),
            'amount': float(sale.amount),
            'payment_status': sale.payment_status.value,
            'sale_date': sale.sale_date.isoformat()
        }
    
    @staticmethod
    def to_summary_list(sales: List[Sale]) -> List[Dict[str, Any]]:
        """
        Converte lista de Sale Entities para lista de resumos
        """
        return [SalePresenter.to_summary_dict(sale) for sale in sales]
    
    @staticmethod
    def to_public_dict(sale: Sale) -> Dict[str, Any]:
        """
        Converte Sale Entity para formato público (CPF mascarado)
        """
        return {
            'id': sale.id,
            'vehicle_id': sale.vehicle_id,
            'customer_cpf': SalePresenter._mask_cpf(sale.customer_cpf),
            'sale_date': sale.sale_date.isoformat(),
            'amount': float(sale.amount),
            'payment_status': sale.payment_status.value
        }
    
    @staticmethod
    def to_public_list(sales: List[Sale]) -> List[Dict[str, Any]]:
        """
        Converte lista de Sale Entities para formato público
        """
        return [SalePresenter.to_public_dict(sale) for sale in sales]
    
    @staticmethod
    def to_create_response(sale: Sale) -> Dict[str, Any]:
        """
        Formato de resposta para criação de venda
        """
        return {
            'message': 'Venda criada com sucesso',
            'sale': SalePresenter.to_dict(sale),
            'status': 'created'
        }
    
    @staticmethod
    def to_payment_update_response(sale: Sale) -> Dict[str, Any]:
        """
        Formato de resposta para atualização de pagamento
        """
        return {
            'message': 'Status de pagamento atualizado com sucesso',
            'sale': SalePresenter.to_dict(sale),
            'status': 'updated'
        }
    
    @staticmethod
    def to_webhook_response(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formato de resposta para webhook de pagamento
        """
        return {
            'webhook_processed': True,
            'result': result,
            'timestamp': result.get('timestamp')
        }
    
    @staticmethod
    def to_error_response(error_message: str, error_code: str = 'SALE_ERROR') -> Dict[str, Any]:
        """
        Formato de resposta para erros relacionados a vendas
        """
        return {
            'error': True,
            'error_code': error_code,
            'message': error_message,
            'status': 'error'
        }
    
    @staticmethod
    def to_not_found_response(sale_id: int) -> Dict[str, Any]:
        """
        Formato de resposta para venda não encontrada
        """
        return {
            'error': True,
            'error_code': 'SALE_NOT_FOUND',
            'message': f'Venda com ID {sale_id} não encontrada',
            'sale_id': sale_id,
            'status': 'not_found'
        }
    
    @staticmethod
    def to_payment_status_dict(sale: Sale) -> Dict[str, Any]:
        """
        Formato específico para status de pagamento
        """
        return {
            'sale_id': sale.id,
            'payment_status': sale.payment_status.value,
            'is_approved': sale.is_payment_approved(),
            'is_pending': sale.is_payment_pending(),
            'is_rejected': sale.is_payment_rejected(),
            'updated_at': sale.updated_at.isoformat()
        }
    
    @staticmethod
    def _mask_cpf(cpf: str) -> str:
        """
        Mascara o CPF para exibição pública
        Exemplo: 123.456.789-00 -> 123.***.**9-00
        """
        if not cpf or len(cpf) < 11:
            return cpf
        
        # Remove formatação
        numbers_only = ''.join(filter(str.isdigit, cpf))
        
        if len(numbers_only) != 11:
            return cpf
        
        # Aplica máscara
        masked = f"{numbers_only[:3]}.***.**{numbers_only[8]}-{numbers_only[9:]}"
        return masked
    
    @staticmethod
    def format_amount(amount: Decimal) -> str:
        """
        Formata valor da venda para exibição em formato brasileiro
        """
        return f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def to_display_string(sale: Sale) -> str:
        """
        Converte Sale Entity para string de exibição amigável
        """
        amount_formatted = SalePresenter.format_amount(sale.amount)
        cpf_masked = SalePresenter._mask_cpf(sale.customer_cpf)
        status_text = {
            'pending': 'Pendente',
            'approved': 'Aprovado',
            'rejected': 'Rejeitado'
        }.get(sale.payment_status.value, sale.payment_status.value)
        
        return f"Venda {sale.id} - Veículo {sale.vehicle_id} - {cpf_masked} - {amount_formatted} ({status_text})"
