"""
Implementação do Repository de Vendas - Camada externa
Implementa SaleRepositoryInterface usando SQLAlchemy
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ...gateways.sale_gateway import SaleRepositoryInterface
from .models import SaleModel


class SQLAlchemySaleRepository(SaleRepositoryInterface):
    """
    Implementação concreta do repositório de vendas usando SQLAlchemy
    Camada externa - pode usar frameworks e bibliotecas
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, sale_data: dict) -> dict:
        """Salva uma venda no banco de dados"""
        try:
            # Cria modelo SQLAlchemy
            sale_model = SaleModel(
                vehicle_id=sale_data['vehicle_id'],
                customer_cpf=sale_data['customer_cpf'],
                sale_date=sale_data['sale_date'],
                amount=sale_data['amount'],
                payment_status=sale_data['payment_status']
            )
            
            # Persiste no banco
            self._session.add(sale_model)
            self._session.commit()
            self._session.refresh(sale_model)
            
            # Converte de volta para dict
            return self._model_to_dict(sale_model)
            
        except Exception as e:
            self._session.rollback()
            raise Exception(f"Erro ao salvar venda: {str(e)}")
    
    def find_by_id(self, sale_id: int) -> Optional[dict]:
        """Busca uma venda por ID"""
        try:
            sale_model = self._session.query(SaleModel).filter(
                SaleModel.id == sale_id
            ).first()
            
            if not sale_model:
                return None
            
            return self._model_to_dict(sale_model)
            
        except Exception as e:
            raise Exception(f"Erro ao buscar venda: {str(e)}")
    
    def find_by_vehicle_id(self, vehicle_id: int) -> Optional[dict]:
        """Busca uma venda por ID do veículo"""
        try:
            sale_model = self._session.query(SaleModel).filter(
                SaleModel.vehicle_id == vehicle_id
            ).first()
            
            if not sale_model:
                return None
            
            return self._model_to_dict(sale_model)
            
        except Exception as e:
            raise Exception(f"Erro ao buscar venda por veículo: {str(e)}")
    
    def find_all(self) -> List[dict]:
        """Busca todas as vendas"""
        try:
            sale_models = self._session.query(SaleModel).all()
            return [self._model_to_dict(model) for model in sale_models]
            
        except Exception as e:
            raise Exception(f"Erro ao listar vendas: {str(e)}")
    
    def update(self, sale_id: int, sale_data: dict) -> dict:
        """Atualiza uma venda"""
        try:
            sale_model = self._session.query(SaleModel).filter(
                SaleModel.id == sale_id
            ).first()
            
            if not sale_model:
                raise ValueError(f"Venda com ID {sale_id} não encontrada")
            
            # Atualiza os campos
            for key, value in sale_data.items():
                if hasattr(sale_model, key) and key != 'id':
                    setattr(sale_model, key, value)
            
            self._session.commit()
            self._session.refresh(sale_model)
            
            return self._model_to_dict(sale_model)
            
        except Exception as e:
            self._session.rollback()
            raise Exception(f"Erro ao atualizar venda: {str(e)}")
    
    def _model_to_dict(self, sale_model: SaleModel) -> dict:
        """Converte modelo SQLAlchemy para dicionário"""
        return {
            'id': sale_model.id,
            'vehicle_id': sale_model.vehicle_id,
            'customer_cpf': sale_model.customer_cpf,
            'sale_date': sale_model.sale_date,
            'amount': float(sale_model.amount),
            'payment_status': sale_model.payment_status,
            'created_at': sale_model.created_at,
            'updated_at': sale_model.updated_at
        }
