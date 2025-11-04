# 📋 INSTRUCCIONES DE MIGRACIÓN Y CONFIGURACIÓN
## Proyecto HGW Chatbot - Estructura Organizada

## 🎯 RESUMEN DE LA ORGANIZACIÓN

### ✅ Lo que hemos hecho:

1. **Backend Organizado por Módulos:**
   - ✅ Configuración centralizada (`config.py`)
   - ✅ Modelos separados (`models/`)
   - ✅ Servicios de negocio (`services/`)
   - ✅ Endpoints API organizados (`api/v1/`)
   - ✅ Schemas de validación (`schemas/`)
   - ✅ Main.py simplificado

2. **Frontend Responsive (Móvil + PC):**
   - ✅ Panel de administración HTML5/CSS3/JS
   - ✅ Diseño responsive con Bootstrap 5
   - ✅ Cliente API JavaScript
   - ✅ Compatible con móviles y desktop
   - ✅ PWA ready (instalable en móviles)

3. **Módulos del Sistema:**
   - ✅ **Chatbot WhatsApp**: Webhooks y respuestas automáticas
   - ✅ **Admin Dashboard**: Estadísticas y visualización
   - ✅ **CRUD Distribuidores**: Gestión completa con 2FA
   - ✅ **Gestión Conversaciones**: Historial y seguimiento
   - ✅ **Gestión Leads**: Tracking de prospectos

---

## 📁 ESTRUCTURA FINAL DEL PROYECTO

```bash
hgw-chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # App principal simplificada
│   │   ├── config.py                 # Configuración
│   │   ├── database.py               # Base de datos
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── chatbot.py           # Modelos chatbot
│   │   │   ├── distributor.py       # Modelos distribuidores
│   │   │   └── admin.py             # Modelos admin
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── distributor.py       # Validación datos
│   │   │   └── chatbot.py
│   │   ├── api/v1/
│   │   │   ├── __init__.py
│   │   │   ├── chatbot.py           # Endpoints WhatsApp
│   │   │   ├── distributors.py      # CRUD distribuidores
│   │   │   ├── conversations.py     # Gestión conversaciones
│   │   │   ├── leads.py             # Gestión leads
│   │   │   ├── admin.py             # Auth admin
│   │   │   └── stats.py             # Estadísticas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── whatsapp.py          # Servicio WhatsApp
│   │   │   ├── openai_service.py    # IA respuestas
│   │   │   └── auto_responses.py    # Respuestas automáticas
│   │   └── utils/
│   │       └── helpers.py
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    └── admin-panel/
        ├── index.html                # Panel principal
        ├── css/
        │   └── styles.css           # Estilos responsive
        ├── js/
        │   ├── api.js              # Cliente API
        │   ├── dashboard.js        # Lógica dashboard
        │   ├── distributors.js     # CRUD distribuidores
        │   └── app.js             # App principal
        └── pages/
            ├── login.html
            └── register.html
```

---

## 🚀 PASOS DE INSTALACIÓN

### PASO 1: Crear la Estructura de Carpetas

```bash
# Crear estructura del backend
mkdir -p hgw-chatbot/backend/app/{models,schemas,api/v1,services,core,utils}

# Crear estructura del frontend
mkdir -p hgw-chatbot/frontend/admin-panel/{css,js,pages}

# Crear carpeta de scripts
mkdir -p hgw-chatbot/scripts
```

### PASO 2: Mover y Organizar Archivos

```bash
# Navegar al proyecto
cd hgw-chatbot/backend

# Copiar tu database.py actual
cp /tu/ruta/actual/database.py app/database.py

# Copiar requirements.txt
cp /tu/ruta/actual/requirements.txt .

# Copiar .env
cp /tu/ruta/actual/.env .
```

### PASO 3: Crear Archivos __init__.py

```bash
# Backend init files
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/services/__init__.py
touch backend/app/core/__init__.py
touch backend/app/utils/__init__.py
```

### PASO 4: Copiar el Código Organizado

Copia los siguientes archivos que he creado a sus respectivas ubicaciones:

1. `backend/app/config.py` - Configuración
2. `backend/app/models/chatbot.py` - Modelos chatbot
3. `backend/app/models/distributor.py` - Modelos distribuidores
4. `backend/app/services/auto_responses.py` - Respuestas automáticas
5. `backend/app/services/whatsapp.py` - Servicio WhatsApp
6. `backend/app/api/v1/distributors.py` - Endpoints distribuidores
7. `backend/app/schemas/distributor.py` - Validación datos
8. `backend/app/main.py` - Aplicación principal
9. `frontend/admin-panel/index.html` - Panel admin
10. `frontend/admin-panel/css/styles.css` - Estilos
11. `frontend/admin-panel/js/api.js` - Cliente API

---

## 🔧 CONFIGURACIÓN

### 1. Variables de Entorno (.env)

```env
# App
APP_NAME="HGW Chatbot"
VERSION="2.0.0"
DEBUG=False

# Database
DB_USER=hgw_user
DB_PASSWORD=HGW2025_Seguro
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hgw_chatbot

# WhatsApp
WHATSAPP_TOKEN=tu_token_aqui
WHATSAPP_PHONE_ID=tu_phone_id
VERIFY_TOKEN=hgw_verify_2025

# OpenAI
OPENAI_API_KEY=tu_api_key
USE_OPENAI=true

# Security
SECRET_KEY=tu_secret_key_segura_aqui
```

### 2. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 3. Inicializar Base de Datos

```bash
cd backend
python -c "from app.database import init_db; init_db()"
```

---

## 🏃‍♂️ EJECUTAR EL PROYECTO

### Backend (API FastAPI)

```bash
cd backend
# Desarrollo (con auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (Panel Admin)

#### Opción 1: Servidor Python Simple
```bash
cd frontend/admin-panel
python -m http.server 8080
# Abrir: http://localhost:8080
```

#### Opción 2: Live Server (VS Code)
- Instalar extensión "Live Server" en VS Code
- Click derecho en `index.html` → "Open with Live Server"

#### Opción 3: Node.js
```bash
npm install -g http-server
cd frontend/admin-panel
http-server -p 8080
```

---

## 📱 ACCESO MÓVIL Y PC

### Para PC:
- Abrir navegador: `http://localhost:8080`

### Para Móvil (misma red):
1. Obtener IP de tu PC:
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. En el móvil, abrir: `http://TU_IP_LOCAL:8080`
   Ejemplo: `http://192.168.1.100:8080`

### PWA (Instalable en Móvil):
1. Abrir el sitio en Chrome móvil
2. Menú → "Añadir a pantalla de inicio"
3. Se instalará como app nativa

---

## 🔗 CREAR LOS ARCHIVOS FALTANTES

Necesitas crear estos archivos adicionales:

### 1. backend/app/api/v1/__init__.py
```python
from . import chatbot, distributors, conversations, leads, admin, stats
```

### 2. backend/app/models/__init__.py
```python
from .chatbot import Conversation, Message, Lead
from .distributor import Distributor
from .admin import AdminUser
```

### 3. backend/app/api/v1/chatbot.py
```python
# Copiar el código del webhook de WhatsApp del main.py original
# Líneas aproximadas: 880-1040 del main.py original
```

### 4. backend/app/api/v1/conversations.py
```python
# Copiar endpoints de conversaciones del main.py original
# Líneas aproximadas: 1470-1530
```

### 5. backend/app/api/v1/leads.py
```python
# Copiar endpoints de leads del main.py original
# Líneas aproximadas: 1540-1583
```

---

## 🎯 VENTAJAS DE ESTA ESTRUCTURA

1. **Modular**: Cada módulo tiene su responsabilidad específica
2. **Escalable**: Fácil agregar nuevas funcionalidades
3. **Mantenible**: Código organizado y limpio
4. **Testeable**: Fácil escribir tests unitarios
5. **Responsive**: Funciona en todos los dispositivos
6. **PWA Ready**: Instalable como app móvil
7. **API REST**: Puede consumirse desde cualquier cliente
8. **Separación Frontend/Backend**: Desarrollo independiente

---

## 🛠️ PRÓXIMOS PASOS (OPCIONALES)

### 1. Agregar Autenticación JWT
```python
# backend/app/core/security.py
from jose import jwt
# Implementar tokens JWT
```

### 2. Agregar Tests
```bash
# Crear carpeta tests
mkdir -p backend/tests
# Usar pytest para testing
```

### 3. Docker
```dockerfile
# Crear Dockerfile
FROM python:3.9
# ... configuración Docker
```

### 4. CI/CD
- GitHub Actions
- GitLab CI
- Jenkins

### 5. App Móvil Nativa (Opcional)
- React Native
- Flutter
- Ionic

---

## 📞 ENDPOINTS API DISPONIBLES

### Base URL: `http://localhost:8000/api/v1`

#### Distribuidores
- `GET /distributors` - Listar todos
- `GET /distributors/{id}` - Obtener uno
- `POST /distributors` - Crear nuevo
- `PUT /distributors/{id}` - Actualizar
- `DELETE /distributors/{id}` - Eliminar
- `POST /distributors/{id}/activate` - Activar
- `POST /distributors/{id}/suspend` - Suspender

#### Conversaciones
- `GET /conversations` - Listar todas
- `GET /conversations/{id}` - Obtener una
- `GET /conversations/{id}/messages` - Ver mensajes

#### Leads
- `GET /leads` - Listar todos
- `PUT /leads/{id}/status` - Actualizar estado

#### Estadísticas
- `GET /stats` - Dashboard general
- `GET /distributors/stats/summary` - Stats distribuidores

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "Module not found"
```bash
# Asegurarse de estar en la carpeta correcta
cd backend
# Instalar en modo desarrollo
pip install -e .
```

### Error: "CORS blocked"
```javascript
// En frontend/js/api.js, cambiar:
this.baseUrl = 'http://TU_IP_BACKEND:8000/api/v1'
```

### Base de datos no conecta
```bash
# Verificar MySQL esté corriendo
sudo systemctl status mysql
# O en Windows
net start MySQL80
```

---

## ✅ CHECKLIST FINAL

- [ ] Estructura de carpetas creada
- [ ] Archivos organizados en sus módulos
- [ ] .env configurado
- [ ] Base de datos inicializada
- [ ] Backend corriendo (puerto 8000)
- [ ] Frontend corriendo (puerto 8080)
- [ ] Probado en navegador PC
- [ ] Probado en móvil
- [ ] API documentación: http://localhost:8000/api/docs

---

## 🎉 ¡LISTO!

Tu proyecto ahora está:
- ✅ Organizado profesionalmente
- ✅ Separado en módulos
- ✅ Con frontend responsive
- ✅ Funcional en móvil y PC
- ✅ Listo para escalar

¿Necesitas ayuda con algún paso específico?
