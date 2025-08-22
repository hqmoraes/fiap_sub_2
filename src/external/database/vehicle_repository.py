"""
Implementação do Repository de Veículos - Camada externa
Implementa VehicleRepositoryInterface usando SQLAlchemy
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import asc

from ...gateways.vehicle_gateway import VehicleRepositoryInterface
from .models import VehicleModel


class SQLAlchemyVehicleRepository(VehicleRepositoryInterface):
    """
    Implementação concreta do repositório de veículos usando SQLAlchemy
    Camada externa - pode usar frameworks e bibliotecas
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, vehicle_data: dict) -> dict:
        """Salva um veículo no banco de dados"""
        try:
            # Cria modelo SQLAlchemy
            vehicle_model = VehicleModel(
                brand=vehicle_data['brand'],
                model=vehicle_data['model'],
                year=vehicle_data['year'],
                price=vehicle_data['price'],
                color=vehicle_data['color'],
                status=vehicle_data['status']
            )
            
            # Persiste no banco
            self._session.add(vehicle_model)
            self._session.commit()
            self._session.refresh(vehicle_model)
            
            # Converte de volta para dict
            return self._model_to_dict(vehicle_model)
            
        except Exception as e:
            self._session.rollback()
            raise Exception(f"Erro ao salvar veículo: {str(e)}")
    
    def find_by_id(self, vehicle_id: int) -> Optional[dict]:
        """Busca um veículo por ID"""
        try:
            vehicle_model = self._session.query(VehicleModel).filter(
                VehicleModel.id == vehicle_id
            ).first()
            
            if not vehicle_model:
                return None
            
            return self._model_to_dict(vehicle_model)
            
        except Exception as e:
            raise Exception(f"Erro ao buscar veículo: {str(e)}")
    
    def find_all(self) -> List[dict]:
        """Busca todos os veículos"""
        try:
            vehicle_models = self._session.query(VehicleModel).all()
            return [self._model_to_dict(model) for model in vehicle_models]
            
        except Exception as e:
            raise Exception(f"Erro ao listar veículos: {str(e)}")
    
    def find_available_ordered_by_price(self) -> List[dict]:
        """Busca veículos disponíveis ordenados por preço"""
        try:
            vehicle_models = self._session.query(VehicleModel).filter(
                VehicleModel.status == 'available'
            ).order_by(asc(VehicleModel.price)).all()
            
            return [self._model_to_dict(model) for model in vehicle_models]
            
        except Exception as e:
            raise Exception(f"Erro ao buscar veículos disponíveis: {str(e)}")
    
    def find_sold_ordered_by_price(self) -> List[dict]:
        """Busca veículos vendidos ordenados por preço"""
        try:
            vehicle_models = self._session.query(VehicleModel).filter(
                VehicleModel.status == 'sold'
            ).order_by(asc(VehicleModel.price)).all()
            
            return [self._model_to_dict(model) for model in vehicle_models]
            
        except Exception as e:
            raise Exception(f"Erro ao buscar veículos vendidos: {str(e)}")
    
    def update(self, vehicle_id: int, vehicle_data: dict) -> dict:
        """Atualiza um veículo"""
        try:
            vehicle_model = self._session.query(VehicleModel).filter(
                VehicleModel.id == vehicle_id
            ).first()
            
            if not vehicle_model:
                raise ValueError(f"Veículo com ID {vehicle_id} não encontrado")
            
            # Atualiza os campos
            for key, value in vehicle_data.items():
                if hasattr(vehicle_model, key) and key != 'id':
                    setattr(vehicle_model, key, value)
            
            self._session.commit()
            self._session.refresh(vehicle_model)
            
            return self._model_to_dict(vehicle_model)
            
        except Exception as e:
            self._session.rollback()
            raise Exception(f"Erro ao atualizar veículo: {str(e)}")
    
    def delete(self, vehicle_id: int) -> bool:
        """Remove um veículo"""
        try:
            vehicle_model = self._session.query(VehicleModel).filter(
                VehicleModel.id == vehicle_id
            ).first()
            
            if not vehicle_model:
                return False
            
            self._session.delete(vehicle_model)
            self._session.commit()
            
            return True
            
        except Exception as e:
            self._session.rollback()
            raise Exception(f"Erro ao excluir veículo: {str(e)}")
    
    def _model_to_dict(self, vehicle_model: VehicleModel) -> dict:
        """Converte modelo SQLAlchemy para dicionário"""
        return {
            'id': vehicle_model.id,
            'brand': vehicle_model.brand,
            'model': vehicle_model.model,
            'year': vehicle_model.year,
            'price': float(vehicle_model.price),
            'color': vehicle_model.color,
            'status': vehicle_model.status,
            'created_at': vehicle_model.created_at,
            'updated_at': vehicle_model.updated_at
        }
