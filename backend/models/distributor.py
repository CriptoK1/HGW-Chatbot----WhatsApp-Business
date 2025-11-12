# backend/models.py (o donde esté tu modelo)
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from datetime import datetime
from database import Base

class Distributor(Base):
    """Modelo para los distribuidores de la red"""
    __tablename__ = "distributors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información personal
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    
    # Fechas importantes
    fecha_ingreso = Column(Date, nullable=False)
    fecha_cumpleanos = Column(Date, nullable=True)
    
    # Credenciales de acceso
    usuario = Column(String(100), unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)  # Hasheada con bcrypt
    contrasena_doble_factor = Column(String(255), nullable=True)  # Para finanzas, hasheada
    
    # ✅ AGREGAR ESTAS DOS LÍNEAS:
    contrasena_texto = Column(String(255), nullable=True)  # Contraseña en texto plano
    contrasena_2fa_texto = Column(String(255), nullable=True)  # 2FA en texto plano
    
    # Información del negocio
    nivel = Column(String(50), default="Pre-Junior")
    estado = Column(String(50), default="activo")
    lead_phone = Column(String(20), nullable=True)
    
    # Notas administrativas
    notas = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_sensitive=False):
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
        
        if include_sensitive:
            data["has_2fa"] = bool(self.contrasena_doble_factor)
            data["contrasena_texto"] = self.contrasena_texto
            data["contrasena_2fa_texto"] = self.contrasena_2fa_texto
        
        return data
    
    def __repr__(self):
        return f"<Distributor {self.usuario} - {self.nombres} {self.apellidos}>"