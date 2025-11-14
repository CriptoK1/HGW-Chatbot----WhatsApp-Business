# backend/app.py
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
import sys
import importlib.util
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from passlib.context import CryptContext

# Importar módulos locales
from database import engine, Base, get_db
from models import *
from auth import create_access_token
from admin_routes import router as admin_router
from distributor_routes import router as distributor_router
from chatbot import ChatbotService

# 🆕 Importar rutas de inventario
try:
    # Cargar el módulo desde backend/api/v1/inventory.py
    inventory_path = Path(__file__).parent / "api" / "v1" / "inventory.py"
    
    if not inventory_path.exists():
        raise FileNotFoundError(f"No se encontró: {inventory_path}")
    
    spec = importlib.util.spec_from_file_location("inventory_module", str(inventory_path))
    inventory_module = importlib.util.module_from_spec(spec)
    sys.modules["inventory_module"] = inventory_module
    spec.loader.exec_module(inventory_module)
    
    inventory_router = inventory_module.router
    INVENTORY_ENABLED = True
    print("✅ Módulo de inventario cargado correctamente")
    print(f"   📂 Desde: api/v1/inventory.py")
    
except Exception as e:
    INVENTORY_ENABLED = False
    inventory_router = None
    print(f"⚠️ Módulo de inventario no disponible")
    print(f"   ❌ Error: {e}")

# ==================== NGROK (solo desarrollo) ====================
try:
    from pyngrok import ngrok
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False
    ngrok = None

load_dotenv()

app = FastAPI(
    title="HGW Chatbot API",
    version="2.0",
    docs_url="/api/docs"
)

# CORS - 🆕 Agregado más orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear base de datos
Base.metadata.create_all(bind=engine)

# Seguridad
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Variable global del chatbot
chatbot_service = None

# ==================== EVENTOS ====================
@app.on_event("startup")
async def startup_event():
    global chatbot_service
    try:
        chatbot_service = ChatbotService()
        print("✅ ChatbotService inicializado correctamente")
    except Exception as e:
        chatbot_service = None
        print(f"⚠️ Error inicializando ChatbotService: {e}")
    
    if NGROK_AVAILABLE and os.getenv("USE_NGROK", "false").lower() == "true":
        try:
            ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
            if ngrok_auth_token:
                ngrok.set_auth_token(ngrok_auth_token)
                
            port = int(os.getenv("PORT", 8000))
            public_url = ngrok.connect(port)
            
            print("\n" + "="*60)
            print("🌐 NGROK TÚNEL ACTIVO")
            print("="*60)
            print(f"📍 URL pública: {public_url}")
            print(f"📍 URL webhook: {public_url}/webhook")
            print(f"📍 URL docs: {public_url}/api/docs")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"⚠️ Error iniciando ngrok: {e}")
            print("💡 Asegúrate de tener tu NGROK_AUTH_TOKEN configurado")

@app.on_event("shutdown")
async def shutdown_event():
    """Cerrar túnel ngrok al apagar el servidor"""
    if NGROK_AVAILABLE:
        try:
            ngrok.kill()
            print("🔴 Túnel ngrok cerrado")
        except:
            pass
# ==================== RUTAS ====================

@app.get("/")
async def root():
    return {
        "name": "HGW Chatbot API",
        "version": "2.0",
        "status": "active",
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# ==================== WEBHOOK PARA WHATSAPP (SIN /api) ====================

@app.get("/webhook")
async def verify_webhook_direct(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verificación de webhook de WhatsApp (ruta directa para Meta)"""
    print(f"📥 Verificación webhook - mode: {hub_mode}, token: {hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == os.getenv("VERIFY_TOKEN"):
        print(f"✅ Webhook verificado correctamente. Challenge: {hub_challenge}")
        return int(hub_challenge)
    
    print(f"❌ Token inválido. Esperado: {os.getenv('VERIFY_TOKEN')}, Recibido: {hub_verify_token}")
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post("/webhook")
async def handle_webhook_direct(request: Request, db=Depends(get_db)):
    """Manejo de mensajes de WhatsApp (ruta directa para Meta)"""
    if not chatbot_service:
        raise HTTPException(status_code=503, detail="Chatbot no disponible")

    try:
        data = await request.json()
        print(f"📨 Mensaje recibido: {data}")
        
        response = await chatbot_service.process_message(data, db)
        print(f"✅ Mensaje procesado correctamente")
        
        return {"status": "ok", "response": response}
    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        return {"status": "error", "detail": str(e)}

# ==================== RUTAS CON /api (para compatibilidad) ====================

@app.get("/api/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if token == os.getenv("VERIFY_TOKEN"):
        return int(challenge)
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/api/webhook")
async def handle_webhook(request: Request, db=Depends(get_db)):
    if not chatbot_service:
        raise HTTPException(status_code=503, detail="Chatbot no disponible")

    data = await request.json()

    try:
        response = await chatbot_service.process_message(data, db)
        return {"status": "ok", "response": response}
    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        return {"status": "error", "detail": str(e)}

@app.post("/api/auth/login")
async def login(username: str, password: str):
    if username == "admin" and password == "admin123":
        token = create_access_token({"sub": username, "role": "admin"})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": username,
                "role": "admin"
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ==================== MIGRACIÓN DE COLUMNAS ====================
@app.post("/api/admin/migrate-password-columns")
async def migrate_password_columns(db=Depends(get_db)):
    """Agrega columnas de contraseñas en texto plano si no existen"""
    from sqlalchemy import text
    
    try:
        # Intentar agregar las columnas
        db.execute(text("ALTER TABLE distributors ADD COLUMN contrasena_texto VARCHAR(255)"))
        db.commit()
        print("✅ Columna contrasena_texto agregada")
    except Exception as e:
        print(f"Columna contrasena_texto ya existe o error: {e}")
        db.rollback()
    
    try:
        db.execute(text("ALTER TABLE distributors ADD COLUMN contrasena_2fa_texto VARCHAR(255)"))
        db.commit()
        print("✅ Columna contrasena_2fa_texto agregada")
    except Exception as e:
        print(f"Columna contrasena_2fa_texto ya existe o error: {e}")
        db.rollback()
    
    return {
        "success": True,
        "message": "Migración de columnas completada (si ya existían, se ignoraron)"
    }

# ==================== ENDPOINTS MODIFICADOS DE DISTRIBUIDORES ====================

@app.get("/api/distributors/{distributor_id}")
async def get_distributor_with_passwords(distributor_id: int, db=Depends(get_db)):
    """Obtiene un distribuidor con contraseñas en texto plano"""
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    data = distributor.to_dict()
    # Agregar contraseñas en texto plano
    data["contrasena_texto"] = distributor.contrasena_texto if hasattr(distributor, 'contrasena_texto') else None
    data["contrasena_2fa_texto"] = distributor.contrasena_2fa_texto if hasattr(distributor, 'contrasena_2fa_texto') else None
    
    return data

# ==================== ROUTERS ====================

# 🆕 Incluir router de inventario si está disponible
if INVENTORY_ENABLED and inventory_router:
    app.include_router(inventory_router, prefix="/api/v1")
    print("✅ Rutas de inventario registradas en /api/v1/inventory")

# Otros routers (el orden importa - endpoints específicos antes del router)
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(distributor_router, prefix="/api/distributors", tags=["Distributors"])

@app.get("/api/stats")
async def get_stats(db=Depends(get_db)):
    """Obtiene estadísticas generales - VERSIÓN CORREGIDA"""
    from sqlalchemy import func, text
    
    try:
        # Usar query específico que solo cuenta IDs en lugar de seleccionar todas las columnas
        total_distributors = db.execute(text("SELECT COUNT(id) FROM distributors")).scalar()
    except Exception as e:
        print(f"⚠️ Error contando distribuidores: {e}")
        total_distributors = 0

    return {
        "total_conversations": db.query(Conversation).count(),
        "total_distributors": total_distributors,
        "total_leads": db.query(Lead).count(),
        "active_distributors": db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'activo'")).scalar() or 0,
        "high_interest_leads": db.query(Lead).filter(Lead.interest_level >= 7).count()
    }

# backend/app.py - SOLO LA PARTE A REEMPLAZAR

@app.get("/api/distributors/stats/summary")
async def get_distributors_stats(db=Depends(get_db)):
    """Obtiene estadísticas de los distribuidores - VERSIÓN CORREGIDA CON TODOS LOS NIVELES"""
    from sqlalchemy import text
    
    try:
        total = db.execute(text("SELECT COUNT(id) FROM distributors")).scalar() or 0
        activos = db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'activo'")).scalar() or 0
        inactivos = db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'inactivo'")).scalar() or 0
        suspendidos = db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'suspendido'")).scalar() or 0
        
        # ⭐ TODOS LOS NIVELES - SINCRONIZADO CON FRONTEND
        niveles_lista = [
            "Pre-Junior", 
            "Junior", 
            "Senior", 
            "Master", 
            "Plata", 
            "Oro", 
            "Platino", 
            "Diamante"
        ]
        
        # Contar por nivel (todos los estados, no solo activos)
        niveles = {}
        for nivel in niveles_lista:
            count = db.execute(
                text("SELECT COUNT(id) FROM distributors WHERE nivel = :nivel"),
                {"nivel": nivel}
            ).scalar() or 0
            
            # Solo agregar al resultado si hay distribuidores de ese nivel
            if count > 0:
                niveles[nivel] = count
        
        print(f"📊 Estadísticas por nivel: {niveles}")  # Para debug
        
        return {
            "total": total,
            "por_estado": {
                "activos": activos,
                "inactivos": inactivos,
                "suspendidos": suspendidos
            },
            "por_nivel": niveles
        }
    except Exception as e:
        print(f"⚠️ Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# ==================== EJECUCIÓN ====================
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Detectar entorno
    is_dev = os.getenv("DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 8000))
    
    if is_dev:
        # Desarrollo: con reload
        print("🔧 Modo DESARROLLO")
        uvicorn.run(
            "app:app", 
            host="127.0.0.1",  # Solo localhost en desarrollo
            port=port, 
            reload=True  # Auto-reload cuando cambies código
        )
    else:
        # Producción: sin reload
        print("🚀 Modo PRODUCCIÓN")
        uvicorn.run(
            "app:app", 
            host="0.0.0.0",  # Todas las interfaces en producción
            port=port, 
            reload=False  # Sin reload para mejor rendimiento
        )