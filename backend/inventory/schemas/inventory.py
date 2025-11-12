# backend/app/schemas/inventory.py
"""
Schemas para el sistema de inventario - Compatible con Pydantic v2
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# ================ VENDEDORES ================

class VendedorBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    telefono: str = Field(..., min_length=6, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field('activo', pattern='^(activo|inactivo)$')

class VendedorCreate(VendedorBase):
    pass

class VendedorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    telefono: Optional[str] = Field(None, min_length=6, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, pattern='^(activo|inactivo)$')

class VendedorResponse(VendedorBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================ PRODUCTOS ================

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    codigo: str = Field(..., min_length=1, max_length=50)
    precio_unitario: Decimal = Field(..., gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field('activo', pattern='^(activo|inactivo)$')

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    precio_unitario: Optional[Decimal] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, pattern='^(activo|inactivo)$')

class ProductoResponse(ProductoBase):
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ================ STOCK ================

class StockBase(BaseModel):
    vendedor_id: int
    producto_id: int
    cantidad_inicial: int = Field(0, ge=0)
    cantidad_actual: int = Field(0, ge=0)

class StockCreate(BaseModel):
    vendedor_id: int
    producto_id: int
    cantidad: int = Field(..., ge=0, description="Cantidad a asignar")

class StockUpdate(BaseModel):
    cantidad_actual: int = Field(..., ge=0)

class StockResponse(StockBase):
    id: int
    ultima_actualizacion: datetime
    vendedor: Optional[VendedorResponse] = None
    producto: Optional[ProductoResponse] = None
    
    class Config:
        from_attributes = True

# ================ VENTAS ================

class VentaBase(BaseModel):
    vendedor_id: int
    producto_id: int
    cantidad: int = Field(..., gt=0)
    precio_venta: Optional[Decimal] = None
    notas: Optional[str] = None

class VentaCreate(VentaBase):
    creado_por: Optional[int] = None

class VentaUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, gt=0)
    precio_venta: Optional[Decimal] = None
    notas: Optional[str] = None

class VentaResponse(VentaBase):
    id: int
    fecha_venta: datetime
    creado_por: Optional[int] = None
    vendedor: Optional[VendedorResponse] = None
    producto: Optional[ProductoResponse] = None
    
    class Config:
        from_attributes = True

# ================ ASIGNACIONES ================

class AsignacionBase(BaseModel):
    vendedor_id: int
    producto_id: int
    cantidad: int = Field(..., gt=0)
    notas: Optional[str] = None

class AsignacionCreate(AsignacionBase):
    asignado_por: Optional[int] = None

class AsignacionResponse(AsignacionBase):
    id: int
    fecha_asignacion: datetime
    asignado_por: Optional[int] = None
    vendedor: Optional[VendedorResponse] = None
    producto: Optional[ProductoResponse] = None
    
    class Config:
        from_attributes = True

# ================ AJUSTES ================

class AjusteBase(BaseModel):
    vendedor_id: int
    producto_id: int
    tipo_ajuste: str = Field(..., pattern='^(aumento|disminucion)$')
    cantidad: int = Field(..., gt=0)
    razon: Optional[str] = None

class AjusteCreate(AjusteBase):
    ajustado_por: Optional[int] = None

class AjusteResponse(AjusteBase):
    id: int
    cantidad_anterior: int
    cantidad_nueva: int
    fecha_ajuste: datetime
    ajustado_por: Optional[int] = None
    vendedor: Optional[VendedorResponse] = None
    producto: Optional[ProductoResponse] = None
    
    class Config:
        from_attributes = True