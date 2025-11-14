from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render usa postgres://, cambiar a postgresql+psycopg://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    print("✅ URL configurada para psycopg3")
else:
    # Fallback para desarrollo
    print("⚠️ DATABASE_URL no encontrada, usando configuración local")
    DATABASE_URL = "postgresql+psycopg://hgw_user:4RKbLFTurg3DtkVIArb5DrrXpqEaovE0@dpg-d4ala6muk2gs739hq0fg-a.oregon-postgres.render.com/hgw_chatbot"

print(f"🔗 Conectando a base de datos...")

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