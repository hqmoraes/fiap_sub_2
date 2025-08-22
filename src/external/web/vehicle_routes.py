"""
Web Controller de Veículos - Camada externa da API
Controller HTTP que usa frameworks (FastAPI) e injeta repositórios na Clean Architecture
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from ...controllers.vehicle_controller import VehicleController
from ..database.models import DatabaseConfig
from ..database.vehicle_repository import SQLAlchemyVehicleRepository
from .schemas import VehicleCreate, VehicleUpdate, VehicleResponse


# Router do FastAPI (camada externa)
router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def get_db_session():
    """Dependency para obter sessão do banco"""
    engine = DatabaseConfig.create_engine()
    SessionLocal = DatabaseConfig.get_session_factory(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_vehicle_controller(session: Session = Depends(get_db_session)) -> VehicleController:
    """
    Dependency para obter VehicleController com repositório injetado
    Aqui é onde a magia da Clean Architecture acontece:
    - Instancia repositório concreto (SQLAlchemy)
    - Injeta no Controller da Clean Architecture
    - Controller instancia Gateway, UseCase e Presenter internamente
    """
    repository = SQLAlchemyVehicleRepository(session)
    return VehicleController(repository)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """
    Endpoint para criar um novo veículo
    
    Fluxo:
    1. FastAPI recebe e valida dados (Pydantic)
    2. Injeta repositório no Controller da Clean Architecture
    3. Controller orquestra: Gateway -> UseCase -> Presenter
    4. Retorna resposta formatada
    """
    try:
        result = controller.create_vehicle(
            brand=vehicle_data.brand,
            model=vehicle_data.model,
            year=vehicle_data.year,
            price=vehicle_data.price,
            color=vehicle_data.color
        )
        
        if result.get('error'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor"}
        )


@router.get("/{vehicle_id}", response_model=dict)
async def get_vehicle(
    vehicle_id: int,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Endpoint para buscar um veículo por ID"""
    try:
        result = controller.find_vehicle_by_id(vehicle_id)
        
        if result.get('error'):
            if result.get('error_code') == 'VEHICLE_NOT_FOUND':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result
                )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor"}
        )


@router.get("/", response_model=dict)
async def list_vehicles(
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Endpoint para listar todos os veículos"""
    try:
        result = controller.list_all_vehicles()
        
        if result.get('error'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        return result
        
    except Exception as e:
        print(f"Erro na listagem de veículos: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Erro interno: {str(e)}"}
        )


@router.get("/status/available", response_model=dict)
async def list_available_vehicles(
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Endpoint para listar veículos disponíveis ordenados por preço"""
    try:
        result = controller.list_available_vehicles()
        
        if result.get('error'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor"}
        )


@router.get("/status/sold", response_model=dict)
async def list_sold_vehicles(
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Endpoint para listar veículos vendidos ordenados por preço"""
    try:
        result = controller.list_sold_vehicles()
        
        if result.get('error'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor"}
        )


@router.put("/{vehicle_id}", response_model=dict)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Endpoint para atualizar um veículo"""
    try:
        # Converte apenas campos que foram fornecidos
        update_data = {}
        if vehicle_data.brand is not None:
            update_data['brand'] = vehicle_data.brand
        if vehicle_data.model is not None:
            update_data['model'] = vehicle_data.model
        if vehicle_data.year is not None:
            update_data['year'] = vehicle_data.year
        if vehicle_data.price is not None:
            update_data['price'] = vehicle_data.price
        if vehicle_data.color is not None:
            update_data['color'] = vehicle_data.color
        
        result = controller.update_vehicle(vehicle_id, **update_data)
        
        if result.get('error'):
            if result.get('error_code') == 'VALIDATION_ERROR':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result
                )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor"}
        )


@router.delete("/{vehicle_id}", response_model=dict)
async def delete_vehicle(
    vehicle_id: int,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Endpoint para excluir um veículo"""
    try:
        result = controller.delete_vehicle(vehicle_id)
        
        if result.get('error'):
            if result.get('error_code') == 'VALIDATION_ERROR':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result
                )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor"}
        )
