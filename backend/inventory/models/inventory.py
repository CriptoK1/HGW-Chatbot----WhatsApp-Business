# backend/app/models/inventory.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
import os

# Agregar el path para importar database
import sys
import os
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_path)
from database import Base

class Vendedor(Base):
    __tablename__ = "vendedores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=False, index=True)
    email = Column(String(255))
    direccion = Column(Text)
    ciudad = Column(String(100))
    estado = Column(String(50), default='activo')
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    stock_items = relationship("StockVendedor", back_populates="vendedor", cascade="all, delete-orphan")
    ventas = relationship("VentaVendedor", back_populates="vendedor", cascade="all, delete-orphan")
    asignaciones = relationship("AsignacionProductoVendedor", back_populates="vendedor", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    codigo = Column(String(50), unique=True, index=True)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    categoria = Column(String(100))
    estado = Column(String(50), default='activo')
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    stock_items = relationship("StockVendedor", back_populates="producto", cascade="all, delete-orphan")
    ventas = relationship("VentaVendedor", back_populates="producto", cascade="all, delete-orphan")
    asignaciones = relationship("AsignacionProductoVendedor", back_populates="producto", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "codigo": self.codigo,
            "precio_unitario": float(self.precio_unitario),
            "categoria": self.categoria,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class StockVendedor(Base):
    __tablename__ = "stock_vendedores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False, index=True)
    cantidad_inicial = Column(Integer, nullable=False, default=0)
    cantidad_actual = Column(Integer, nullable=False, default=0)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    vendedor = relationship("Vendedor", back_populates="stock_items")
    producto = relationship("Producto", back_populates="stock_items")
    
    # Índice único compuesto
    __table_args__ = (
        Index('unico_vendedor_producto', 'vendedor_id', 'producto_id', unique=True),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "vendedor_id": self.vendedor_id,
            "producto_id": self.producto_id,
            "vendedor": self.vendedor.to_dict() if self.vendedor else None,
            "producto": self.producto.to_dict() if self.producto else None,
            "cantidad_inicial": self.cantidad_inicial,
            "cantidad_actual": self.cantidad_actual,
            "ultima_actualizacion": self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None
        }


class VentaVendedor(Base):
    __tablename__ = "ventas_vendedor"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_venta = Column(DECIMAL(10, 2))
    fecha_venta = Column(DateTime, default=datetime.utcnow, index=True)
    notas = Column(Text)
    creado_por = Column(Integer)
    
    # Relaciones
    vendedor = relationship("Vendedor", back_populates="ventas")
    producto = relationship("Producto", back_populates="ventas")
    
    def to_dict(self):
        return {
            "id": self.id,
            "vendedor_id": self.vendedor_id,
            "producto_id": self.producto_id,
            "vendedor": self.vendedor.to_dict() if self.vendedor else None,
            "producto": self.producto.to_dict() if self.producto else None,
            "cantidad": self.cantidad,
            "precio_venta": float(self.precio_venta) if self.precio_venta else None,
            "fecha_venta": self.fecha_venta.isoformat() if self.fecha_venta else None,
            "notas": self.notas,
            "creado_por": self.creado_por
        }


class AsignacionProductoVendedor(Base):
    __tablename__ = "asignaciones_productos_vendedor"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendedor_id = Column(Integer, ForeignKey("vendedores.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_asignacion = Column(DateTime, default=datetime.utcnow)
    asignado_por = Column(Integer)
    notas = Column(Text)
    
    # Relaciones
    vendedor = relationship("Vendedor", back_populates="asignaciones")
    producto = relationship("Producto", back_populates="asignaciones")
    
    def to_dict(self):
        return {
            "id": self.id,
            "vendedor_id": self.vendedor_id,
            "producto_id": self.producto_id,
            "vendedor": self.vendedor.to_dict() if self.vendedor else None,
            "producto": self.producto.to_dict() if self.producto else None,
            "cantidad": self.cantidad,
            "fecha_asignacion": self.fecha_asignacion.isoformat() if self.fecha_asignacion else None,
            "asignado_por": self.asignado_por,
            "notas": self.notas
        }