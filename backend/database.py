from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener DATABASE_URL de las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# CRÍTICO: Render usa postgres:// pero SQLAlchemy necesita postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("✅ URL de PostgreSQL corregida")

# Si no hay DATABASE_URL (desarrollo local), construir una
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "hgw_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "HGW2025_Seguro")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")  # PostgreSQL por defecto
    DB_NAME = os.getenv("DB_NAME", "hgw_chatbot")
    
    # Usar PostgreSQL también en local
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"⚠️ Usando DATABASE_URL local: {DATABASE_URL}")

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
    try:
        # Importar TODOS los modelos para que SQLAlchemy los conozca
        from models import (
            Conversation, Message, Lead, 
            Distributor, AdminUser
        )
        print("✅ Modelos base importados")
        
        # Intentar importar modelos de inventario (si existen)
        try:
            from models import (
                Vendedor, Producto, StockVendedor, 
                VentaVendedor, AsignacionProductoVendedor, 
                AjusteInventarioVendedor
            )
            print("✅ Modelos de inventario importados")
        except ImportError as e:
            print(f"⚠️ Modelos de inventario no disponibles: {e}")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        
        return True
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False