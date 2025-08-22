"""
Aplicação principal - Clean Architecture implementada
Ponto de entrada que conecta todas as camadas
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.external.database.models import DatabaseConfig
from src.external.web.vehicle_routes import router as vehicle_router
from src.external.web.sale_routes import router as sale_router


def create_app() -> FastAPI:
    """
    Factory da aplicação FastAPI
    
    Responsabilidades da camada externa:
    - Configurar FastAPI (framework)
    - Registrar routers
    - Configurar middlewares
    - Inicializar banco de dados
    """
    
    # Cria aplicação FastAPI
    app = FastAPI(
        title="FIAP Vehicles API - Clean Architecture",
        description="Sistema de Revenda de Veículos implementado com Clean Architecture",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Registrar routers (camada externa)
    app.include_router(vehicle_router)
    app.include_router(sale_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Endpoint de saúde da aplicação"""
        return {
            "status": "healthy",
            "message": "FIAP Vehicles API - Clean Architecture",
            "version": "2.0.0",
            "architecture": "Clean Architecture with SOLID principles"
        }
    
    # Evento de inicialização
    @app.on_event("startup")
    async def startup_event():
        """Inicializa o banco de dados"""
        try:
            engine = DatabaseConfig.create_engine()
            DatabaseConfig.create_tables(engine)
            print("✅ Banco de dados inicializado com sucesso")
            print("🏗️  Clean Architecture implementada")
            print("📋 Camadas: Entity -> UseCase -> Controller -> Gateway -> Repository")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
    
    return app


# Cria a aplicação
app = create_app()


if __name__ == "__main__":
    # Configurações do servidor
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    print("🚀 Iniciando FIAP Vehicles API - Clean Architecture")
    print(f"📡 Servidor rodando em: http://{host}:{port}")
    print(f"📖 Documentação: http://{host}:{port}/docs")
    print("🏗️  Arquitetura: Clean Architecture + SOLID")
    
    # Executa o servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
