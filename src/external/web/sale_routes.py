"""
Web Controller de Vendas - Camada externa da API
Controller HTTP que usa frameworks (FastAPI) e injeta repositórios na Clean Architecture
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from decimal import Decimal

from ...controllers.sale_controller import SaleController
from ..database.models import DatabaseConfig
from ..database.sale_repository import SQLAlchemySaleRepository
from ..database.vehicle_repository import SQLAlchemyVehicleRepository
from .schemas import SaleCreate, SaleResponse, PaymentWebhook, PaymentStatusUpdate


# Router do FastAPI (camada externa)
router = APIRouter(prefix="/sales", tags=["sales"])


def get_db_session():
    """Dependency para obter sessão do banco"""
    engine = DatabaseConfig.create_engine()
    SessionLocal = DatabaseConfig.get_session_factory(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_sale_controller(session: Session = Depends(get_db_session)) -> SaleController:
    """
    Dependency para obter SaleController com repositórios injetados
    Aqui é onde a magia da Clean Architecture acontece:
    - Instancia repositórios concretos (SQLAlchemy)
    - Injeta no Controller da Clean Architecture
    - Controller instancia Gateways, UseCases e Presenters internamente
    """
    sale_repository = SQLAlchemySaleRepository(session)
    vehicle_repository = SQLAlchemyVehicleRepository(session)
    return SaleController(sale_repository, vehicle_repository)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    controller: SaleController = Depends(get_sale_controller)
):
    """
    Endpoint para criar uma nova venda
    
    Fluxo:
    1. FastAPI recebe e valida dados (Pydantic)
    2. Injeta repositórios no Controller da Clean Architecture
    3. Controller orquestra: Gateways -> UseCases -> Presenter
    4. Retorna resposta formatada
    """
    try:
        result = controller.create_sale(
            vehicle_id=sale_data.vehicle_id,
            customer_cpf=sale_data.customer_cpf,
            amount=sale_data.amount
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


@router.get("/{sale_id}", response_model=dict)
async def get_sale(
    sale_id: int,
    controller: SaleController = Depends(get_sale_controller)
):
    """Endpoint para buscar uma venda por ID"""
    try:
        result = controller.find_sale_by_id(sale_id)
        
        if result.get('error'):
            if result.get('error_code') == 'SALE_NOT_FOUND':
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


@router.get("/vehicle/{vehicle_id}", response_model=dict)
async def get_sale_by_vehicle(
    vehicle_id: int,
    controller: SaleController = Depends(get_sale_controller)
):
    """Endpoint para buscar uma venda por ID do veículo"""
    try:
        result = controller.find_sale_by_vehicle_id(vehicle_id)
        
        if result.get('error'):
            if result.get('error_code') == 'SALE_NOT_FOUND':
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
async def list_sales(
    controller: SaleController = Depends(get_sale_controller)
):
    """Endpoint para listar todas as vendas"""
    try:
        result = controller.list_all_sales()
        
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


@router.put("/{sale_id}/payment-status", response_model=dict)
async def update_payment_status(
    sale_id: int,
    payment_data: PaymentStatusUpdate,
    controller: SaleController = Depends(get_sale_controller)
):
    """Endpoint para atualizar status de pagamento"""
    try:
        result = controller.update_payment_status(
            sale_id=sale_id,
            payment_status=payment_data.payment_status
        )
        
        if result.get('error'):
            if result.get('error_code') == 'VALIDATION_ERROR':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result
                )
            elif result.get('error_code') == 'SALE_NOT_FOUND':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
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


@router.post("/payment-webhook", response_model=dict)
async def payment_webhook(
    webhook_data: PaymentWebhook,
    controller: SaleController = Depends(get_sale_controller)
):
    """
    Endpoint para webhook de pagamento (idempotente)
    
    Este endpoint deve ser idempotente para garantir que múltiplas
    chamadas com os mesmos dados não causem problemas
    """
    try:
        result = controller.process_payment_webhook({
            'sale_id': webhook_data.sale_id,
            'status': webhook_data.status
        })
        
        # Webhook sempre retorna 200, mesmo com erros de negócio
        # para indicar que foi processado com sucesso
        return result
        
    except Exception as e:
        # Log do erro, mas não expõe detalhes internos
        return {
            'webhook_processed': True,
            'result': {
                'success': False,
                'error': 'Erro interno do webhook',
                'sale_id': webhook_data.sale_id
            }
        }


@router.get("/{sale_id}/payment-status", response_model=dict)
async def get_payment_status(
    sale_id: int,
    controller: SaleController = Depends(get_sale_controller)
):
    """Endpoint para consultar status de pagamento"""
    try:
        result = controller.get_payment_status(sale_id)
        
        if result.get('error'):
            if result.get('error_code') == 'SALE_NOT_FOUND':
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
