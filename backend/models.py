from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# =================== MODELOS DEL CHATBOT ===================

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    user_name = Column(String(100))
    status = Column(String(50), default="nuevo")
    profile_type = Column(String(50), default="otro")
    last_interaction = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    user_name = Column(String(100))
    email = Column(String(100))
    profile_type = Column(String(50))
    interest_level = Column(Integer, default=5)
    status = Column(String(50), default="nuevo")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# =================== MODELOS DEL ADMIN (NUEVOS) ===================

class Distributor(Base):
    __tablename__ = "distributors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información personal
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    
    # Fechas importantes
    fecha_ingreso = Column(Date, nullable=False)
    fecha_cumpleanos = Column(Date, nullable=True)
    
    # Credenciales de acceso
    usuario = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)  # Hasheada con bcrypt
    contrasena_doble_factor = Column(String(255), nullable=True)  # Para finanzas, hasheada
    
    # ✅ CONTRASEÑAS EN TEXTO PLANO (para que el admin las vea)
    contrasena_texto = Column(String(255), nullable=True)
    contrasena_2fa_texto = Column(String(255), nullable=True)
    
    # Información del negocio
    nivel = Column(String(50), default="Pre-Junior")  # Pre-Junior, Junior, Senior, Master
    estado = Column(String(50), default="activo")  # activo, inactivo, suspendido
    
    # Relación con leads del chatbot (opcional)
    lead_phone = Column(String(20), nullable=True)  # Para vincular con un lead
    
    # Notas administrativas
    notas = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_sensitive=False):
        """Convierte el modelo a diccionario"""
        data = {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "nombre_completo": f"{self.nombres} {self.apellidos}",
            "telefono": self.telefono,
            "email": self.email,
            "fecha_ingreso": self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            "fecha_cumpleanos": self.fecha_cumpleanos.isoformat() if self.fecha_cumpleanos else None,
            "usuario": self.usuario,
            "nivel": self.nivel,
            "estado": self.estado,
            "lead_phone": self.lead_phone,
            "notas": self.notas,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Incluir contraseñas en texto plano solo si se solicita (para admin)
        if include_sensitive:
            data["has_2fa"] = bool(self.contrasena_doble_factor)
            data["contrasena_texto"] = self.contrasena_texto
            data["contrasena_2fa_texto"] = self.contrasena_2fa_texto
        
        return data
    
    def __repr__(self):
        return f"<Distributor {self.usuario} - {self.nombres} {self.apellidos}>"


class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hasheada con bcrypt
    nombre_completo = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)