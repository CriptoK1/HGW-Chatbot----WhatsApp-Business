# Estructura del Proyecto HGW Chatbot

## 📁 Estructura de Carpetas

```
hgw-chatbot/
│
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app principal (simplificado)
│   │   ├── config.py                  # Configuración y variables de entorno
│   │   ├── database.py                # Configuración de base de datos
│   │   │
│   │   ├── 📁 models/
│   │   │   ├── __init__.py
│   │   │   ├── chatbot.py            # Modelos del chatbot
│   │   │   ├── distributor.py        # Modelo de distribuidores
│   │   │   └── admin.py              # Modelo de admin
│   │   │
│   │   ├── 📁 schemas/
│   │   │   ├── __init__.py
│   │   │   ├── chatbot.py            # Esquemas Pydantic para chatbot
│   │   │   ├── distributor.py        # Esquemas para distribuidores
│   │   │   └── admin.py              # Esquemas para admin
│   │   │
│   │   ├── 📁 api/
│   │   │   ├── __init__.py
│   │   │   ├── 📁 v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chatbot.py        # Endpoints del chatbot WhatsApp
│   │   │   │   ├── admin.py          # Endpoints del panel admin
│   │   │   │   ├── distributors.py   # CRUD de distribuidores
│   │   │   │   ├── conversations.py  # Endpoints de conversaciones
│   │   │   │   ├── leads.py          # Endpoints de leads
│   │   │   │   └── stats.py          # Estadísticas
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── __init__.py
│   │   │   ├── whatsapp.py           # Lógica de WhatsApp
│   │   │   ├── openai_service.py     # Integración con OpenAI
│   │   │   ├── auto_responses.py     # Respuestas automáticas
│   │   │   └── profile_detector.py   # Detección de perfiles
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # Autenticación y seguridad
│   │   │   └── dependencies.py       # Dependencias comunes
│   │   │
│   │   └── 📁 utils/
│   │       ├── __init__.py
│   │       └── helpers.py            # Funciones auxiliares
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── 📁 frontend/
│   ├── 📁 admin-panel/              # Panel de administración responsive
│   │   ├── index.html
│   │   ├── 📁 css/
│   │   │   ├── styles.css
│   │   │   └── responsive.css
│   │   ├── 📁 js/
│   │   │   ├── api.js              # Cliente API
│   │   │   ├── dashboard.js        # Dashboard principal
│   │   │   ├── conversations.js    # Gestión de conversaciones
│   │   │   ├── distributors.js     # CRUD distribuidores
│   │   │   └── auth.js            # Autenticación
│   │   └── 📁 pages/
│   │       ├── dashboard.html
│   │       ├── conversations.html
│   │       ├── distributors.html
│   │       ├── leads.html
│   │       └── login.html
│   │
│   └── 📁 mobile-app/              # PWA para móviles (opcional)
│       ├── manifest.json
│       ├── service-worker.js
│       └── index.html
│
├── 📁 scripts/
│   ├── init_db.py                  # Script para inicializar DB
│   └── migrate.py                   # Script de migración
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🔧 Pasos de Migración

### Paso 1: Crear la estructura de carpetas
```bash
mkdir -p hgw-chatbot/{backend,frontend,scripts}
mkdir -p hgw-chatbot/backend/app/{models,schemas,api/v1,services,core,utils}
mkdir -p hgw-chatbot/frontend/admin-panel/{css,js,pages}
mkdir -p hgw-chatbot/frontend/mobile-app
```

### Paso 2: Separar el código actual en módulos

#### 2.1 Archivos de configuración base
- `backend/app/config.py` - Variables de entorno
- `backend/app/database.py` - Tu archivo actual de database.py

#### 2.2 Separar modelos
- `backend/app/models/chatbot.py` - Conversation, Message, Lead
- `backend/app/models/distributor.py` - Distributor
- `backend/app/models/admin.py` - AdminUser

#### 2.3 Crear servicios
- `backend/app/services/whatsapp.py` - Lógica de WhatsApp
- `backend/app/services/openai_service.py` - Integración OpenAI
- `backend/app/services/auto_responses.py` - Respuestas automáticas

#### 2.4 Separar endpoints por módulos
- `backend/app/api/v1/chatbot.py` - Webhooks de WhatsApp
- `backend/app/api/v1/distributors.py` - CRUD distribuidores
- `backend/app/api/v1/conversations.py` - Gestión conversaciones
- `backend/app/api/v1/admin.py` - Login y administración

### Paso 3: Frontend Responsive

Para que funcione en móviles y PC, usaremos:
- **HTML5 + CSS3 + JavaScript Vanilla** (opción simple)
- **Framework CSS**: Bootstrap o Tailwind para diseño responsive
- **API REST**: Consumir los endpoints de FastAPI
- **PWA**: Para instalación en móviles

### Paso 4: Herramientas recomendadas

Para móvil y PC:
1. **Frontend Web Responsive**: HTML/CSS/JS con Bootstrap
2. **PWA (Progressive Web App)**: Para instalar en móviles
3. **API REST**: Tu backend FastAPI actual
4. **Opcional**: React Native o Flutter para app nativa

## 📱 Solución Móvil + PC

### Opción 1: PWA (Recomendada) ✅
- Una sola aplicación web que funciona en todos los dispositivos
- Se puede instalar como app en móviles
- Usa el mismo código para móvil y PC
- Notificaciones push disponibles

### Opción 2: Aplicación Híbrida
- React Native / Flutter
- Ionic + Capacitor
- Requiere más desarrollo

### Opción 3: Web Responsive Simple
- HTML + CSS + JavaScript
- Bootstrap o Tailwind CSS
- Funciona en navegadores móviles y PC

## 🚀 Ventajas de esta estructura

1. **Modular**: Cada componente tiene su responsabilidad
2. **Escalable**: Fácil agregar nuevas funcionalidades
3. **Mantenible**: Código organizado y limpio
4. **Testeable**: Fácil escribir pruebas unitarias
5. **Reutilizable**: Servicios compartidos entre endpoints
6. **Responsive**: Funciona en todos los dispositivos
