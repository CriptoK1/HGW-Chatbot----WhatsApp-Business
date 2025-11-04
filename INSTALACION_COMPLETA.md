# 🚀 INSTRUCCIONES COMPLETAS - HGW CHATBOT v2.0

## 📋 RESUMEN DEL PROYECTO

### ✅ Lo que tienes ahora:

1. **Backend Simplificado (FastAPI)**
   - Chatbot WhatsApp funcional
   - CRUD completo de distribuidores
   - Gestión de conversaciones y leads
   - Autenticación JWT
   - API REST documentada

2. **Frontend Moderno (React PWA)**
   - Panel de administración responsive
   - Funciona en móviles y PC
   - Instalable como app (PWA)
   - Material-UI para diseño profesional
   - Dashboard con estadísticas

---

## 📦 INSTALACIÓN PASO A PASO

### 1️⃣ REQUISITOS PREVIOS

```bash
# Instalar Python 3.9+
python --version

# Instalar Node.js 16+
node --version

# Instalar MySQL
mysql --version
```

### 2️⃣ CLONAR/CREAR ESTRUCTURA

```bash
# Crear carpeta principal
mkdir hgw-chatbot
cd hgw-chatbot

# Crear carpetas
mkdir backend
mkdir frontend-react
```

### 3️⃣ CONFIGURAR BACKEND

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv/Scripts/activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install fastapi uvicorn sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] python-multipart httpx openai python-dotenv

# Crear archivo .env
```

**Crear archivo `backend/.env`:**
```env
# App
APP_NAME="HGW Chatbot"
VERSION="2.0"
SECRET_KEY="tu-clave-super-secreta-cambiar-en-produccion-abc123xyz789"

# Database
DB_USER=hgw_user
DB_PASSWORD=HGW2025_Seguro
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hgw_chatbot

# WhatsApp
WHATSAPP_TOKEN=tu_token_de_whatsapp
WHATSAPP_PHONE_ID=tu_phone_id
VERIFY_TOKEN=hgw_verify_2025

# OpenAI (opcional)
OPENAI_API_KEY=tu_api_key_opcional
USE_OPENAI=false
```

**Copiar archivos del backend:**
1. Copia todos los archivos que creé:
   - `app.py`
   - `database.py` (tu archivo original)
   - `models.py` (tu archivo original)
   - `chatbot.py`
   - `admin_routes.py`
   - `distributor_routes.py`
   - `auth.py`

### 4️⃣ INICIALIZAR BASE DE DATOS

```bash
# En la carpeta backend con el entorno virtual activado
python

>>> from database import engine, Base
>>> from models import *
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

### 5️⃣ CONFIGURAR FRONTEND REACT

```bash
cd frontend-react

# Instalar dependencias
npm install

# O con yarn
yarn install
```

**Copiar archivos del frontend:**
1. Copia la estructura de archivos que creé:
   - `src/App.js`
   - `src/components/Layout.js`
   - `src/components/Dashboard.js`
   - `src/components/Distributors.js`
   - `src/api/apiClient.js`

2. Crear componentes faltantes simples:

**`src/components/Login.js`:**
```javascript
import React, { useState } from 'react';
import { Box, Card, TextField, Button, Typography, Alert } from '@mui/material';
import api from '../api/apiClient';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.login(username, password);
      onLogin(response.user, response.access_token);
    } catch (err) {
      setError('Credenciales inválidas');
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="background.default">
      <Card sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" align="center" gutterBottom>HGW Admin</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
          />
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 2 }}>
            Iniciar Sesión
          </Button>
        </form>
        <Typography variant="caption" display="block" align="center" sx={{ mt: 2 }}>
          Usuario: admin | Contraseña: admin123
        </Typography>
      </Card>
    </Box>
  );
}

export default Login;
```

**`src/components/Conversations.js`:**
```javascript
import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CircularProgress } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import api from '../api/apiClient';
import { format } from 'date-fns';

function Conversations() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await api.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'phone_number', headerName: 'Teléfono', width: 150 },
    { field: 'user_name', headerName: 'Nombre', width: 150 },
    { field: 'profile_type', headerName: 'Perfil', width: 120 },
    { field: 'status', headerName: 'Estado', width: 120 },
    { field: 'messages_count', headerName: 'Mensajes', width: 100 },
    {
      field: 'last_interaction',
      headerName: 'Última Interacción',
      width: 180,
      renderCell: (params) => params.value ? format(new Date(params.value), 'dd/MM/yyyy HH:mm') : '-'
    },
  ];

  if (loading) return <Box display="flex" justifyContent="center"><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Conversaciones</Typography>
      <Card>
        <DataGrid
          rows={conversations}
          columns={columns}
          pageSize={10}
          autoHeight
          disableSelectionOnClick
        />
      </Card>
    </Box>
  );
}

export default Conversations;
```

**`src/components/Leads.js`:**
```javascript
import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CircularProgress, Chip } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import api from '../api/apiClient';

function Leads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      setLoading(true);
      const data = await api.getLeads();
      setLeads(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'phone_number', headerName: 'Teléfono', width: 150 },
    { field: 'user_name', headerName: 'Nombre', width: 150 },
    { field: 'email', headerName: 'Email', width: 200 },
    { field: 'profile_type', headerName: 'Perfil', width: 120 },
    {
      field: 'interest_level',
      headerName: 'Interés',
      width: 100,
      renderCell: (params) => (
        <Chip label={params.value} color={params.value >= 7 ? 'success' : 'default'} size="small" />
      )
    },
    { field: 'status', headerName: 'Estado', width: 120 },
  ];

  if (loading) return <Box display="flex" justifyContent="center"><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Leads</Typography>
      <Card>
        <DataGrid
          rows={leads}
          columns={columns}
          pageSize={10}
          autoHeight
          disableSelectionOnClick
        />
      </Card>
    </Box>
  );
}

export default Leads;
```

**`src/index.js`:**
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### 6️⃣ ARCHIVOS PWA

**`public/manifest.json`:**
```json
{
  "short_name": "HGW Admin",
  "name": "HGW Chatbot Admin Panel",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#28a745",
  "background_color": "#ffffff"
}
```

**`public/index.html`:**
```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#28a745" />
    <meta name="description" content="HGW Chatbot Admin Panel" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>HGW Admin Panel</title>
  </head>
  <body>
    <noscript>Necesitas habilitar JavaScript para usar esta aplicación.</noscript>
    <div id="root"></div>
  </body>
</html>
```

---

## 🏃‍♂️ EJECUTAR EL PROYECTO

### Terminal 1 - Backend:
```bash
cd backend
# Activar entorno virtual
source venv/bin/activate  # Mac/Linux
# o
venv\Scripts\activate  # Windows

# Ejecutar servidor
python app.py
# o
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```bash
cd frontend-react
npm start
# La app se abrirá en http://localhost:3000
```

---

## 📱 ACCESO Y USO

### Para PC:
1. Abrir navegador
2. Ir a: `http://localhost:3000`
3. Login: **usuario:** admin **contraseña:** admin123

### Para Móvil (misma red WiFi):
1. Obtener IP de tu PC:
   ```bash
   # Windows
   ipconfig
   # Mac/Linux
   ifconfig
   ```
2. En el móvil: `http://TU_IP:3000`
   Ejemplo: `http://192.168.1.100:3000`

### Instalar como App (PWA):
1. Abrir en Chrome móvil
2. Menú (3 puntos) → "Añadir a pantalla de inicio"
3. Se instalará como app nativa

---

## 🔗 ENDPOINTS PRINCIPALES

### API Backend:
- Documentación: http://localhost:8000/api/docs
- Webhook WhatsApp: http://localhost:8000/api/webhook
- Admin API: http://localhost:8000/api/admin/*
- Distributors: http://localhost:8000/api/distributors/*

### Frontend Routes:
- Login: http://localhost:3000/login
- Dashboard: http://localhost:3000/dashboard
- Distribuidores: http://localhost:3000/distributors
- Conversaciones: http://localhost:3000/conversations
- Leads: http://localhost:3000/leads

---

## 🛠️ CONFIGURACIÓN WHATSAPP

1. Ir a [Facebook Developers](https://developers.facebook.com)
2. Crear app de WhatsApp Business
3. Obtener token y phone_id
4. Configurar webhook:
   - URL: `https://tu-dominio.com/api/webhook`
   - Token: `hgw_verify_2025`
5. Usar ngrok para pruebas locales:
   ```bash
   ngrok http 8000
   ```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error CORS:
```javascript
// En frontend-react/src/api/apiClient.js
const API_BASE_URL = 'http://localhost:8000/api';  // Cambiar si es necesario
```

### MySQL no conecta:
```bash
# Verificar MySQL está corriendo
sudo systemctl status mysql

# Crear usuario y base de datos
mysql -u root -p
CREATE DATABASE hgw_chatbot;
CREATE USER 'hgw_user'@'localhost' IDENTIFIED BY 'HGW2025_Seguro';
GRANT ALL ON hgw_chatbot.* TO 'hgw_user'@'localhost';
```

### Error de módulos:
```bash
pip install -r requirements.txt
# o instalar uno por uno
pip install fastapi uvicorn sqlalchemy pymysql
```

---

## ✅ CHECKLIST FINAL

- [ ] Python 3.9+ instalado
- [ ] Node.js 16+ instalado
- [ ] MySQL configurado y corriendo
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 3000
- [ ] Login funciona (admin/admin123)
- [ ] Dashboard muestra estadísticas
- [ ] CRUD de distribuidores funciona
- [ ] App se ve bien en móvil

---

## 🎉 ¡LISTO!

Tu proyecto ahora tiene:
- ✅ Backend API organizado y funcional
- ✅ Frontend React moderno y responsive
- ✅ PWA instalable en móviles
- ✅ Panel admin completo
- ✅ Chatbot WhatsApp integrado

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

¿Necesitas ayuda? El backend está documentado en: http://localhost:8000/api/docs
