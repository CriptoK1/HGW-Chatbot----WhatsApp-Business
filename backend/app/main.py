"""
Aplicación principal de HGW Chatbot
FastAPI con estructura modular y organizada
"""

from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

# Importar configuración
from .config import settings
from .database import init_db

# Importar routers existentes
from .api.v1 import (
    chatbot,
    distributors,
    conversations,
    leads,
    admin,
    stats,
    inventory  # NUEVO: Importar el router de inventario
)

# ==================== NGROK ====================
from pyngrok import ngrok

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API de HGW Chatbot con panel de administración y sistema de inventario",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # En producción, quitar ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================================
# Event Handlers
# ===============================================

@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar la aplicación"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    
    # Inicializar base de datos
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    
    # Verificar configuración de WhatsApp
    if not settings.WHATSAPP_TOKEN:
        logger.warning("WhatsApp token not configured")
    
    # Verificar configuración de OpenAI
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured - using auto responses only")
    
    # ==================== INICIAR NGROK ====================
    if os.getenv("USE_NGROK", "false").lower() == "true":
        try:
            ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
            if ngrok_auth_token:
                ngrok.set_auth_token(ngrok_auth_token)
                
            port = int(os.getenv("PORT", 8000))
            public_url = ngrok.connect(port)
            
            logger.info("\n" + "="*60)
            logger.info("🌐 NGROK TÚNEL ACTIVO")
            logger.info("="*60)
            logger.info(f"📍 URL pública: {public_url}")
            logger.info(f"📍 URL webhook: {public_url}/webhook")
            logger.info(f"📍 URL docs: {public_url}/api/docs")
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"⚠️ Error iniciando ngrok: {e}")
            logger.error("💡 Asegúrate de tener tu NGROK_AUTH_TOKEN configurado")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación"""
    logger.info("Shutting down application")
    
    # Cerrar túnel ngrok
    if os.getenv("USE_NGROK", "false").lower() == "true":
        try:
            ngrok.kill()
            logger.info("🔴 Túnel ngrok cerrado")
        except:
            pass

# ===============================================
# WEBHOOK ROUTES (sin prefijo /api/v1 para WhatsApp)
# ===============================================

from .services.whatsapp import WhatsAppService
from .database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

whatsapp_service = WhatsAppService()

@app.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verificación de webhook de WhatsApp (ruta directa)"""
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        logger.info("✅ Webhook verificado correctamente")
        return int(hub_challenge)
    
    logger.warning(f"❌ Token inválido. Recibido: {hub_verify_token}")
    return JSONResponse(
        status_code=403,
        content={"error": "Invalid verification token"}
    )

@app.post("/webhook")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    """Manejo de mensajes de WhatsApp (ruta directa)"""
    try:
        data = await request.json()
        logger.info(f"📨 Webhook recibido: {data}")
        
        # Parsear el mensaje
        message_data = whatsapp_service.parse_webhook(data)
        
        if message_data:
            logger.info(f"✅ Mensaje parseado: {message_data}")
            # Aquí puedes llamar a tu servicio de chatbot
            # await chatbot_service.process_message(message_data, db)
            
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Error procesando webhook: {e}")
        return {"status": "error", "detail": str(e)}

# ===============================================
# Incluir Routers
# ===============================================

# Chatbot endpoints (con prefijo /api/v1)
app.include_router(
    chatbot.router,
    prefix="/api/v1",
    tags=["chatbot"]
)

# Distribuidores CRUD
app.include_router(
    distributors.router,
    prefix="/api/v1",
    tags=["distribuidores"]
)

# Conversaciones
app.include_router(
    conversations.router,
    prefix="/api/v1",
    tags=["conversaciones"]
)

# Leads
app.include_router(
    leads.router,
    prefix="/api/v1",
    tags=["leads"]
)

# Admin
app.include_router(
    admin.router,
    prefix="/api/v1",
    tags=["admin"]
)

# Estadísticas
app.include_router(
    stats.router,
    prefix="/api/v1",
    tags=["estadísticas"]
)

# NUEVO: Sistema de Inventario
app.include_router(
    inventory.router,
    prefix="/api/v1",
    tags=["inventario"]
)

# ===============================================
# Endpoints Base
# ===============================================

@app.get("/")
async def root():
    """Endpoint raíz - información de la API"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "active",
        "documentation": "/api/docs",
        "endpoints": {
            "webhook": "/webhook",  # Ruta directa para WhatsApp
            "chatbot": "/api/v1/webhook",  # Ruta con prefijo
            "admin": "/api/v1/admin",
            "distributors": "/api/v1/distributors",
            "conversations": "/api/v1/conversations",
            "leads": "/api/v1/leads",
            "stats": "/api/v1/stats",
            # NUEVO: Endpoints de inventario
            "inventory": {
                "vendedores": "/api/v1/inventory/vendedores",
                "productos": "/api/v1/inventory/productos",
                "stock": "/api/v1/inventory/stock",
                "ventas": "/api/v1/inventory/ventas",
                "ajustes": "/api/v1/inventory/ajustes",
                "asignaciones": "/api/v1/inventory/asignaciones",
                "estadisticas": "/api/v1/inventory/estadisticas"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Verificar conexión a la base de datos
    try:
        db = next(get_db())
        # Hacer una consulta simple para verificar la conexión
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    finally:
        try:
            db.close()
        except:
            pass
    
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "whatsapp_configured": bool(settings.WHATSAPP_TOKEN),
        "openai_configured": bool(settings.OPENAI_API_KEY)
    }

# ===============================================
# Error Handlers
# ===============================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Manejador para rutas no encontradas"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The path {request.url.path} was not found",
            "documentation": "/api/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Manejador para errores internos"""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal error occurred. Please try again later."
        }
    )

# ===============================================
# Función principal para desarrollo
# ===============================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuración para desarrollo
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",  # Cambiar para que apunte correctamente al módulo
        host="0.0.0.0",
        port=port,
        reload=True,  # Recarga automática en desarrollo
        log_level="info"
    )