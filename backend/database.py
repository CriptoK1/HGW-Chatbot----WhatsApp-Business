from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Configuración local MySQL
    DB_USER = os.getenv("DB_USER", "hgw_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "HGW2025_Seguro")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "hgw_chatbot")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Crear engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    # Importar TODOS los modelos para que SQLAlchemy los conozca
    from .models.conversation import Conversation, Message
    from .models.lead import Lead
    from .models.distributor import Distributor
    from .models.admin import AdminUser
    
    # Importar los nuevos modelos de inventario
    from .models.inventory import (
        Vendedor, 
        Producto, 
        StockVendedor, 
        VentaVendedor,
        AsignacionProductoVendedor, 
        AjusteInventarioVendedor
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente (incluyendo inventario)")
    
    return True
