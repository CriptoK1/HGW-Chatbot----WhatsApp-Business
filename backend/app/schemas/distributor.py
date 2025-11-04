# backend/app/schemas/distributor.py
"""Schemas de Pydantic para validación de distribuidores"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime

class DistributorBase(BaseModel):
    """Schema base para distribuidores"""
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    fecha_ingreso: date
    fecha_cumpleanos: Optional[date] = None
    usuario: str = Field(..., min_length=3, max_length=100)
    nivel: Optional[str] = Field(default="Pre-Junior", pattern="^(Pre-Junior|Junior|Senior|Master)$")
    estado: Optional[str] = Field(default="activo", pattern="^(activo|inactivo|suspendido|eliminado)$")
    lead_phone: Optional[str] = Field(None, max_length=20)
    notas: Optional[str] = None
    
    @validator('telefono')
    def validate_phone(cls, v):
        """Valida que el teléfono solo contenga números y símbolos permitidos"""
        import re
        if not re.match(r'^[\d\+\-\(\)\s]+$', v):
            raise ValueError('El teléfono solo puede contener números y los símbolos + - ( ) y espacios')
        return v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    @validator('fecha_cumpleanos')
    def validate_birthday(cls, v, values):
        """Valida que la fecha de cumpleaños sea válida"""
        if v and 'fecha_ingreso' in values:
            if v > date.today():
                raise ValueError('La fecha de cumpleaños no puede ser futura')
        return v

class DistributorCreate(DistributorBase):
    """Schema para crear un distribuidor"""
    contrasena: str = Field(..., min_length=6)
    contrasena_doble_factor: Optional[str] = Field(None, min_length=6)
    
    @validator('contrasena')
    def validate_password(cls, v):
        """Valida que la contraseña sea segura"""
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class DistributorUpdate(BaseModel):
    """Schema para actualizar un distribuidor"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    fecha_ingreso: Optional[date] = None
    fecha_cumpleanos: Optional[date] = None
    usuario: Optional[str] = Field(None, min_length=3, max_length=100)
    contrasena: Optional[str] = Field(None, min_length=6)
    contrasena_doble_factor: Optional[str] = Field(None, min_length=6)
    nivel: Optional[str] = Field(None, pattern="^(Pre-Junior|Junior|Senior|Master)$")
    estado: Optional[str] = Field(None, pattern="^(activo|inactivo|suspendido|eliminado)$")
    lead_phone: Optional[str] = Field(None, max_length=20)
    notas: Optional[str] = None
    
    class Config:
        orm_mode = True

class DistributorResponse(DistributorBase):
    """Schema para respuesta de distribuidor"""
    id: int
    nombre_completo: str
    has_2fa: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class DistributorListResponse(BaseModel):
    """Schema para listado de distribuidores"""
    id: int
    nombres: str
    apellidos: str
    nombre_completo: str
    telefono: str
    email: Optional[str]
    usuario: str
    nivel: str
    estado: str
    fecha_ingreso: date
    created_at: datetime
    
    class Config:
        orm_mode = True

class DistributorLogin(BaseModel):
    """Schema para login de distribuidor"""
    usuario: str
    contrasena: str
    
class DistributorLoginResponse(BaseModel):
    """Respuesta al login de distribuidor"""
    success: bool
    token: Optional[str] = None
    distributor: Optional[DistributorResponse] = None
    message: str
    requires_2fa: bool = False
