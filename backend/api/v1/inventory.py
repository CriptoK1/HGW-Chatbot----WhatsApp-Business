# backend/app/api/v1/inventory.py
"""
Endpoints para el sistema de inventario y ventas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime, date
import sys
import os

# Agregar el backend al path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Importar desde backend directamente (no desde app)
from database import get_db

# Importar modelos y schemas desde la estructura app/
from inventory.models.inventory import (
    Vendedor, Producto, StockVendedor, VentaVendedor,
    AsignacionProductoVendedor
)
from inventory.schemas.inventory import (
    VendedorCreate, VendedorUpdate, VendedorResponse,
    ProductoCreate, ProductoUpdate, ProductoResponse,
    StockCreate, StockUpdate, StockResponse,
    VentaCreate, VentaUpdate, VentaResponse,
    AsignacionCreate, AsignacionResponse,
    AjusteCreate, AjusteResponse
)

router = APIRouter(prefix="/inventory", tags=["inventory"])

# ===============================================
# ESTADÍSTICAS GENERALES
# ===============================================

@router.get("/estadisticas/general")
async def get_estadisticas_general(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales del inventario"""
    total_vendedores = db.query(Vendedor).filter(Vendedor.estado == "activo").count()
    total_productos = db.query(Producto).filter(Producto.estado == "activo").count()
    
    # Stock total
    stock_total = db.query(func.sum(StockVendedor.cantidad_actual)).scalar() or 0
    
    # Valor total del inventario
    valor_inventario = db.query(
        func.sum(StockVendedor.cantidad_actual * Producto.precio_unitario)
    ).join(Producto).scalar() or 0
    
    # Ventas del mes
    inicio_mes = datetime.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    
    ventas_mes = db.query(VentaVendedor).filter(
        VentaVendedor.fecha_venta >= inicio_mes
    ).count()
    
    valor_ventas_mes = db.query(
        func.sum(VentaVendedor.cantidad * VentaVendedor.precio_venta)
    ).filter(
        VentaVendedor.fecha_venta >= inicio_mes
    ).scalar() or 0
    
    return {
        "total_vendedores": total_vendedores,
        "total_productos": total_productos,
        "stock_total": int(stock_total),
        "valor_inventario": float(valor_inventario),
        "ventas_mes": ventas_mes,
        "valor_ventas_mes": float(valor_ventas_mes)
    }

# ===============================================
# VENDEDORES ENDPOINTS
# ===============================================

@router.get("/vendedores", response_model=List[VendedorResponse])
async def get_vendedores(
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    search: Optional[str] = None,
    ciudad: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtiene todos los vendedores con filtros opcionales"""
    query = db.query(Vendedor)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Vendedor.nombre.ilike(search_filter),
                Vendedor.telefono.like(search_filter),
                Vendedor.email.ilike(search_filter)
            )
        )
    
    if ciudad:
        query = query.filter(Vendedor.ciudad == ciudad)
    
    if estado:
        query = query.filter(Vendedor.estado == estado)
    
    vendedores = query.order_by(Vendedor.id.desc()).offset(skip).limit(limit).all()
    return vendedores

@router.get("/vendedores/{vendedor_id}", response_model=VendedorResponse)
async def get_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    """Obtiene un vendedor específico"""
    vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    return vendedor

@router.post("/vendedores", response_model=VendedorResponse)
async def create_vendedor(vendedor: VendedorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo vendedor"""
    # Verificar teléfono único
    existing = db.query(Vendedor).filter(Vendedor.telefono == vendedor.telefono).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un vendedor con ese teléfono")
    
    db_vendedor = Vendedor(**vendedor.model_dump())
    db.add(db_vendedor)
    db.commit()
    db.refresh(db_vendedor)
    return db_vendedor

@router.put("/vendedores/{vendedor_id}", response_model=VendedorResponse)
async def update_vendedor(
    vendedor_id: int,
    vendedor: VendedorUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un vendedor existente"""
    db_vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not db_vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    # Verificar teléfono único si se está actualizando
    if vendedor.telefono and vendedor.telefono != db_vendedor.telefono:
        existing = db.query(Vendedor).filter(Vendedor.telefono == vendedor.telefono).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un vendedor con ese teléfono")
    
    update_data = vendedor.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vendedor, field, value)
    
    db.commit()
    db.refresh(db_vendedor)
    return db_vendedor

@router.delete("/vendedores/{vendedor_id}")
async def delete_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    """Elimina un vendedor (soft delete)"""
    db_vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not db_vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    db_vendedor.estado = "inactivo"
    db.commit()
    
    return {"success": True, "message": "Vendedor desactivado correctamente"}

# ===============================================
# PRODUCTOS ENDPOINTS
# ===============================================

@router.get("/productos", response_model=List[ProductoResponse])
async def get_productos(
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    search: Optional[str] = None,
    categoria: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obtiene todos los productos con filtros opcionales"""
    query = db.query(Producto)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Producto.nombre.ilike(search_filter),
                Producto.codigo.like(search_filter),
                Producto.descripcion.ilike(search_filter)
            )
        )
    
    if categoria:
        query = query.filter(Producto.categoria == categoria)
    
    if estado:
        query = query.filter(Producto.estado == estado)
    
    productos = query.order_by(Producto.id.desc()).offset(skip).limit(limit).all()
    return productos

@router.get("/productos/{producto_id}", response_model=ProductoResponse)
async def get_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto específico"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/productos", response_model=ProductoResponse)
async def create_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto"""
    # Verificar código único
    existing = db.query(Producto).filter(Producto.codigo == producto.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    
    db_producto = Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.put("/productos/{producto_id}", response_model=ProductoResponse)
async def update_producto(
    producto_id: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un producto existente"""
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar código único si se está actualizando
    if producto.codigo and producto.codigo != db_producto.codigo:
        existing = db.query(Producto).filter(Producto.codigo == producto.codigo).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    
    update_data = producto.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_producto, field, value)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.delete("/productos/{producto_id}")
async def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    """Elimina un producto (soft delete)"""
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar si tiene stock asignado
    stock_count = db.query(StockVendedor).filter(
        StockVendedor.producto_id == producto_id,
        StockVendedor.cantidad_actual > 0
    ).count()
    
    if stock_count > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el producto porque tiene stock asignado a vendedores"
        )
    
    db_producto.estado = "inactivo"
    db.commit()
    
    return {"success": True, "message": "Producto desactivado correctamente"}

# ===============================================
# STOCK ENDPOINTS
# ===============================================

@router.get("/stock", response_model=List[StockResponse])
async def get_stock(
    vendedor_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Obtiene el stock de vendedores"""
    query = db.query(StockVendedor)
    
    if vendedor_id:
        query = query.filter(StockVendedor.vendedor_id == vendedor_id)
    
    if producto_id:
        query = query.filter(StockVendedor.producto_id == producto_id)
    
    stock_items = query.offset(skip).limit(limit).all()
    return stock_items

@router.post("/stock/asignar")
async def asignar_stock(asignacion: StockCreate, db: Session = Depends(get_db)):
    """Asigna stock inicial a un vendedor"""
    vendedor = db.query(Vendedor).filter(Vendedor.id == asignacion.vendedor_id).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    producto = db.query(Producto).filter(Producto.id == asignacion.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    stock_existente = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == asignacion.vendedor_id,
        StockVendedor.producto_id == asignacion.producto_id
    ).first()
    
    if stock_existente:
        stock_existente.cantidad_actual += asignacion.cantidad
        stock_existente.cantidad_inicial += asignacion.cantidad
    else:
        stock_existente = StockVendedor(
            vendedor_id=asignacion.vendedor_id,
            producto_id=asignacion.producto_id,
            cantidad_inicial=asignacion.cantidad,
            cantidad_actual=asignacion.cantidad
        )
        db.add(stock_existente)
    
    db_asignacion = AsignacionProductoVendedor(
        vendedor_id=asignacion.vendedor_id,
        producto_id=asignacion.producto_id,
        cantidad=asignacion.cantidad,
        asignado_por=1,
        notas=f"Asignación de {asignacion.cantidad} unidades"
    )
    db.add(db_asignacion)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Se asignaron {asignacion.cantidad} unidades correctamente",
        "stock_id": stock_existente.id
    }

# ===============================================
# VENTAS ENDPOINTS
# ===============================================

@router.get("/ventas", response_model=List[VentaResponse])
async def get_ventas(
    vendedor_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Obtiene las ventas con filtros opcionales"""
    query = db.query(VentaVendedor)
    
    if vendedor_id:
        query = query.filter(VentaVendedor.vendedor_id == vendedor_id)
    
    if producto_id:
        query = query.filter(VentaVendedor.producto_id == producto_id)
    
    if fecha_desde:
        query = query.filter(VentaVendedor.fecha_venta >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(VentaVendedor.fecha_venta <= fecha_hasta)
    
    ventas = query.order_by(VentaVendedor.fecha_venta.desc()).offset(skip).limit(limit).all()
    return ventas

@router.post("/ventas", response_model=VentaResponse)
async def create_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """Registra una nueva venta"""
    stock = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == venta.vendedor_id,
        StockVendedor.producto_id == venta.producto_id
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=404, 
            detail="No hay stock asignado para este producto y vendedor"
        )
    
    if stock.cantidad_actual < venta.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {stock.cantidad_actual}, Solicitado: {venta.cantidad}"
        )
    
    precio_venta = venta.precio_venta
    if not precio_venta:
        producto = db.query(Producto).filter(Producto.id == venta.producto_id).first()
        precio_venta = producto.precio_unitario
    
    venta_data = venta.model_dump()
    venta_data['precio_venta'] = precio_venta
    db_venta = VentaVendedor(**venta_data)
    db.add(db_venta)
    db.flush()
    
    stock.cantidad_actual -= venta.cantidad
    
    db.commit()
    db.refresh(db_venta)
    return db_venta

@router.put("/ventas/{venta_id}", response_model=VentaResponse)
async def update_venta(
    venta_id: int,
    venta_update: VentaUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una venta existente"""
    venta = db.query(VentaVendedor).filter(VentaVendedor.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    update_data = venta_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venta, field, value)
    
    db.commit()
    db.refresh(venta)
    return venta

@router.delete("/ventas/{venta_id}")
async def delete_venta(venta_id: int, db: Session = Depends(get_db)):
    """Elimina una venta y restaura el stock"""
    venta = db.query(VentaVendedor).filter(VentaVendedor.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    stock = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == venta.vendedor_id,
        StockVendedor.producto_id == venta.producto_id
    ).first()
    
    if stock:
        stock.cantidad_actual += venta.cantidad
    
    db.delete(venta)
    db.commit()
    
    return {"success": True, "message": "Venta eliminada y stock restaurado"}