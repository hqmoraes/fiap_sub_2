"""
Aplicação principal - Clean Architecture implementada
Ponto de entrada que conecta todas as camadas
"""
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

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
    
        # Configuração de lifespan para substituir on_event deprecated
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Gerencia o ciclo de vida da aplicação"""
        # Startup
        try:
            engine = DatabaseConfig.create_engine()
            DatabaseConfig.create_tables(engine)
            print("✅ Banco de dados inicializado com sucesso")
            print("🏗️  Clean Architecture implementada")
            print("📋 Camadas: Entity -> UseCase -> Controller -> Gateway -> Repository")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
        
        yield
        
        # Shutdown
        print("🔻 Aplicação finalizada")
    
    # Criar aplicação com lifespan
    app = FastAPI(
        title="FIAP Vehicles API - Clean Architecture",
        description="""
        API RESTful para gerenciamento de veículos implementada com Clean Architecture.
        
        ### Arquitetura
        - **Clean Architecture** com separação rigorosa de camadas
        - **SOLID Principles** aplicados em todas as camadas
        - **Dependency Injection** para inversão de controle
        
        ### Camadas
        - **Entities**: Regras de negócio puras
        - **Use Cases**: Casos de uso da aplicação  
        - **Controllers**: Orquestração (Clean Controllers)
        - **Gateways**: Tradutores Entity ↔ Repository
        - **Presenters**: Formatação de saídas
        - **External**: Frameworks (FastAPI, SQLAlchemy)
        """,
        version="2.0.0",
        lifespan=lifespan
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
    
    # Endpoint de teste para debug
    @app.get("/debug/database")
    async def test_database():
        """Endpoint para testar conexão com banco"""
        try:
            engine = DatabaseConfig.create_engine()
            SessionLocal = DatabaseConfig.get_session_factory(engine)
            session = SessionLocal()
            
            # Teste simples de query
            from src.external.database.vehicle_repository import SQLAlchemyVehicleRepository
            repo = SQLAlchemyVehicleRepository(session)
            vehicles = repo.find_all()
            
            session.close()
            
            return {
                "status": "success",
                "message": "Conexão com banco funcionando",
                "total_vehicles": len(vehicles),
                "vehicles": vehicles
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao conectar com banco: {str(e)}",
                "error_type": str(type(e))
            }
    
    # Endpoint para recriar tabelas
    @app.post("/debug/recreate-tables")
    async def recreate_tables():
        """Endpoint para recriar tabelas do banco"""
        try:
            engine = DatabaseConfig.create_engine()
            from src.external.database.models import Base
            
            # Drop e recria todas as tabelas
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            
            return {
                "status": "success",
                "message": "Tabelas recriadas com sucesso"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao recriar tabelas: {str(e)}",
                "error_type": str(type(e))
            }
    
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
