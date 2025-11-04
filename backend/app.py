# backend/app.py
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
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

# ==================== NGROK ====================
from pyngrok import ngrok

load_dotenv()

app = FastAPI(
    title="HGW Chatbot API",
    version="2.0",
    docs_url="/api/docs"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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
    
    # Iniciar ngrok si está habilitado
    if os.getenv("USE_NGROK", "false").lower() == "true":
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

# Routers (el orden importa - endpoints específicos antes del router)
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

@app.get("/api/distributors/stats/summary")
async def get_distributors_stats(db=Depends(get_db)):
    """Obtiene estadísticas de los distribuidores - VERSIÓN CORREGIDA"""
    from sqlalchemy import text
    
    try:
        total = db.execute(text("SELECT COUNT(id) FROM distributors")).scalar() or 0
        activos = db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'activo'")).scalar() or 0
        inactivos = db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'inactivo'")).scalar() or 0
        suspendidos = db.execute(text("SELECT COUNT(id) FROM distributors WHERE estado = 'suspendido'")).scalar() or 0
        
        # Contar por nivel
        niveles = {}
        for nivel in ["Pre-Junior", "Junior", "Senior", "Master"]:
            count = db.execute(
                text("SELECT COUNT(id) FROM distributors WHERE nivel = :nivel AND estado = 'activo'"),
                {"nivel": nivel}
            ).scalar() or 0
            niveles[nivel] = count
        
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)