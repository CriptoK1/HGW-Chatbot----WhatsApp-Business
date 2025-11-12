# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación"""
    
    # App
    APP_NAME: str = "HGW Chatbot"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DB_USER: str = os.getenv("DB_USER", "hgw_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "HGW2025_Seguro")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "hgw_chatbot")
    
    # WhatsApp
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "")
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "hgw_verify_2025")
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    USE_OPENAI: bool = os.getenv("USE_OPENAI", "true").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Ngrok
    USE_NGROK: bool = os.getenv("USE_NGROK", "false").lower() == "true"
    NGROK_AUTH_TOKEN: Optional[str] = os.getenv("NGROK_AUTH_TOKEN")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    @property
    def get_database_url(self) -> str:
        """Construye la URL de la base de datos"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()