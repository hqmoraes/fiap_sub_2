"""
Configuração do banco de dados - Camada externa
SQLAlchemy models e configuração de conexão
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class VehicleModel(Base):
    """Modelo SQLAlchemy para Veículo"""
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    color = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default='available')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamento com vendas
    sale = relationship("SaleModel", back_populates="vehicle", uselist=False)


class SaleModel(Base):
    """Modelo SQLAlchemy para Venda"""
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False, unique=True)
    customer_cpf = Column(String(14), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(String(20), nullable=False, default='pending')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamento com veículo
    vehicle = relationship("VehicleModel", back_populates="sale")


class DatabaseConfig:
    """Configuração do banco de dados"""
    
    @staticmethod
    def get_database_url() -> str:
        """Constrói URL do banco a partir de variáveis de ambiente"""
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'fiap_vehicles')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', 'password')
        
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @staticmethod
    def create_engine():
        """Cria engine do SQLAlchemy"""
        database_url = DatabaseConfig.get_database_url()
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
    
    @staticmethod
    def create_tables(engine):
        """Cria todas as tabelas"""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def get_session_factory(engine):
        """Retorna factory de sessões"""
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
