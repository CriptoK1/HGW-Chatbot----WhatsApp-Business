# backend/app/api/v1/inventory.py

"""
Endpoints para el sistema de inventario y ventas
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, date

from ...database import get_db
from ...models.inventory import (
    Vendedor, Producto, StockVendedor, VentaVendedor,
    AsignacionProductoVendedor, AjusteInventarioVendedor
)
from ...schemas.inventory import (
    VendedorCreate, VendedorUpdate, VendedorResponse,
    ProductoCreate, ProductoUpdate, ProductoResponse,
    StockCreate, StockUpdate, StockResponse,
    VentaCreate, VentaUpdate, VentaResponse,
    AsignacionCreate, AsignacionResponse,
    AjusteCreate, AjusteResponse,
    EstadisticasVendedor, EstadisticasProducto
)

router = APIRouter(prefix="/inventory", tags=["inventory"])

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

@router.post("/vendedores", response_model=VendedorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendedor(vendedor: VendedorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo vendedor"""
    # Verificar teléfono único
    existing = db.query(Vendedor).filter(Vendedor.telefono == vendedor.telefono).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un vendedor con ese teléfono")
    
    db_vendedor = Vendedor(**vendedor.dict())
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
    
    update_data = vendedor.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vendedor, field, value)
    
    db.commit()
    db.refresh(db_vendedor)
    return db_vendedor

@router.delete("/vendedores/{vendedor_id}", status_code=status.HTTP_200_OK)
async def delete_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    """Elimina un vendedor (soft delete)"""
    db_vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not db_vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    # Soft delete
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

@router.post("/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto"""
    # Verificar código único
    existing = db.query(Producto).filter(Producto.codigo == producto.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    
    db_producto = Producto(**producto.dict())
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
    
    update_data = producto.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_producto, field, value)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.delete("/productos/{producto_id}", status_code=status.HTTP_200_OK)
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
    
    # Soft delete
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

@router.get("/stock/vendedor/{vendedor_id}", response_model=List[StockResponse])
async def get_stock_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    """Obtiene todo el stock de un vendedor específico"""
    stock_items = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == vendedor_id
    ).all()
    return stock_items

@router.post("/stock/asignar", status_code=status.HTTP_201_CREATED)
async def asignar_stock(asignacion: StockCreate, db: Session = Depends(get_db)):
    """Asigna stock inicial a un vendedor"""
    # Verificar que existan vendedor y producto
    vendedor = db.query(Vendedor).filter(Vendedor.id == asignacion.vendedor_id).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    producto = db.query(Producto).filter(Producto.id == asignacion.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar si ya existe stock para este vendedor-producto
    stock_existente = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == asignacion.vendedor_id,
        StockVendedor.producto_id == asignacion.producto_id
    ).first()
    
    if stock_existente:
        # Actualizar el stock existente
        stock_existente.cantidad_actual += asignacion.cantidad
        stock_existente.cantidad_inicial += asignacion.cantidad
    else:
        # Crear nuevo registro de stock
        stock_existente = StockVendedor(
            vendedor_id=asignacion.vendedor_id,
            producto_id=asignacion.producto_id,
            cantidad_inicial=asignacion.cantidad,
            cantidad_actual=asignacion.cantidad
        )
        db.add(stock_existente)
    
    # Registrar la asignación
    db_asignacion = AsignacionProductoVendedor(
        vendedor_id=asignacion.vendedor_id,
        producto_id=asignacion.producto_id,
        cantidad=asignacion.cantidad,
        asignado_por=1,  # TODO: Obtener del usuario autenticado
        notas=f"Asignación inicial de {asignacion.cantidad} unidades"
    )
    db.add(db_asignacion)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Se asignaron {asignacion.cantidad} unidades correctamente",
        "stock_id": stock_existente.id
    }

@router.put("/stock/{stock_id}", response_model=StockResponse)
async def update_stock(
    stock_id: int,
    stock_update: StockUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza el stock actual de un vendedor-producto"""
    stock = db.query(StockVendedor).filter(StockVendedor.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    
    cantidad_anterior = stock.cantidad_actual
    stock.cantidad_actual = stock_update.cantidad_actual
    
    # Registrar el ajuste
    tipo_ajuste = "aumento" if stock_update.cantidad_actual > cantidad_anterior else "disminucion"
    diferencia = abs(stock_update.cantidad_actual - cantidad_anterior)
    
    ajuste = AjusteInventarioVendedor(
        vendedor_id=stock.vendedor_id,
        producto_id=stock.producto_id,
        tipo_ajuste=tipo_ajuste,
        cantidad=diferencia,
        cantidad_anterior=cantidad_anterior,
        cantidad_nueva=stock_update.cantidad_actual,
        razon="Ajuste manual de inventario",
        ajustado_por=1  # TODO: Obtener del usuario autenticado
    )
    db.add(ajuste)
    
    db.commit()
    db.refresh(stock)
    return stock

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

@router.get("/ventas/{venta_id}", response_model=VentaResponse)
async def get_venta(venta_id: int, db: Session = Depends(get_db)):
    """Obtiene una venta específica"""
    venta = db.query(VentaVendedor).filter(VentaVendedor.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@router.post("/ventas", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def create_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """Registra una nueva venta"""
    # Verificar stock disponible
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
    
    # Obtener precio del producto si no se especificó
    precio_venta = venta.precio_venta
    if not precio_venta:
        producto = db.query(Producto).filter(Producto.id == venta.producto_id).first()
        precio_venta = producto.precio_unitario
    
    # Crear la venta
    venta_data = venta.dict()
    venta_data['precio_venta'] = precio_venta
    db_venta = VentaVendedor(**venta_data)
    db.add(db_venta)
    db.flush()  # Para obtener el ID antes del commit
    
    # Actualizar stock
    stock.cantidad_actual -= venta.cantidad
    
    # Registrar ajuste de inventario
    ajuste = AjusteInventarioVendedor(
        vendedor_id=venta.vendedor_id,
        producto_id=venta.producto_id,
        tipo_ajuste="disminucion",
        cantidad=venta.cantidad,
        cantidad_anterior=stock.cantidad_actual + venta.cantidad,
        cantidad_nueva=stock.cantidad_actual,
        razon=f"Venta registrada - ID: {db_venta.id}",
        ajustado_por=venta.creado_por or 1
    )
    db.add(ajuste)
    
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
    
    # Si se actualiza la cantidad, ajustar el stock
    if venta_update.cantidad and venta_update.cantidad != venta.cantidad:
        stock = db.query(StockVendedor).filter(
            StockVendedor.vendedor_id == venta.vendedor_id,
            StockVendedor.producto_id == venta.producto_id
        ).first()
        
        diferencia = venta_update.cantidad - venta.cantidad
        
        if diferencia > 0 and stock.cantidad_actual < diferencia:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para ajustar la venta. Disponible: {stock.cantidad_actual}"
            )
        
        # Ajustar stock
        stock.cantidad_actual -= diferencia
        
        # Registrar ajuste
        tipo_ajuste = "disminucion" if diferencia > 0 else "aumento"
        ajuste = AjusteInventarioVendedor(
            vendedor_id=venta.vendedor_id,
            producto_id=venta.producto_id,
            tipo_ajuste=tipo_ajuste,
            cantidad=abs(diferencia),
            cantidad_anterior=stock.cantidad_actual + diferencia,
            cantidad_nueva=stock.cantidad_actual,
            razon=f"Ajuste por edición de venta ID: {venta_id}",
            ajustado_por=1
        )
        db.add(ajuste)
    
    # Actualizar campos
    update_data = venta_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venta, field, value)
    
    db.commit()
    db.refresh(venta)
    return venta

@router.delete("/ventas/{venta_id}", status_code=status.HTTP_200_OK)
async def delete_venta(venta_id: int, db: Session = Depends(get_db)):
    """Elimina una venta y restaura el stock"""
    venta = db.query(VentaVendedor).filter(VentaVendedor.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Restaurar stock
    stock = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == venta.vendedor_id,
        StockVendedor.producto_id == venta.producto_id
    ).first()
    
    if stock:
        cantidad_anterior = stock.cantidad_actual
        stock.cantidad_actual += venta.cantidad
        
        # Registrar ajuste
        ajuste = AjusteInventarioVendedor(
            vendedor_id=venta.vendedor_id,
            producto_id=venta.producto_id,
            tipo_ajuste="aumento",
            cantidad=venta.cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=stock.cantidad_actual,
            razon=f"Cancelación de venta ID: {venta_id}",
            ajustado_por=1
        )
        db.add(ajuste)
    
    db.delete(venta)
    db.commit()
    
    return {"success": True, "message": "Venta eliminada y stock restaurado"}

# ===============================================
# AJUSTES DE INVENTARIO ENDPOINTS
# ===============================================

@router.get("/ajustes", response_model=List[AjusteResponse])
async def get_ajustes(
    vendedor_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    tipo_ajuste: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de ajustes de inventario"""
    query = db.query(AjusteInventarioVendedor)
    
    if vendedor_id:
        query = query.filter(AjusteInventarioVendedor.vendedor_id == vendedor_id)
    
    if producto_id:
        query = query.filter(AjusteInventarioVendedor.producto_id == producto_id)
    
    if tipo_ajuste:
        query = query.filter(AjusteInventarioVendedor.tipo_ajuste == tipo_ajuste)
    
    ajustes = query.order_by(
        AjusteInventarioVendedor.fecha_ajuste.desc()
    ).offset(skip).limit(limit).all()
    return ajustes

@router.post("/ajustes", response_model=AjusteResponse, status_code=status.HTTP_201_CREATED)
async def create_ajuste(ajuste: AjusteCreate, db: Session = Depends(get_db)):
    """Registra un ajuste manual de inventario"""
    # Verificar stock existente
    stock = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == ajuste.vendedor_id,
        StockVendedor.producto_id == ajuste.producto_id
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=404, 
            detail="No existe stock para este vendedor y producto"
        )
    
    cantidad_anterior = stock.cantidad_actual
    
    # Aplicar ajuste
    if ajuste.tipo_ajuste == "aumento":
        cantidad_nueva = cantidad_anterior + ajuste.cantidad
    else:  # disminucion
        if cantidad_anterior < ajuste.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede disminuir {ajuste.cantidad} unidades. Stock actual: {cantidad_anterior}"
            )
        cantidad_nueva = cantidad_anterior - ajuste.cantidad
    
    # Actualizar stock
    stock.cantidad_actual = cantidad_nueva
    
    # Crear registro de ajuste
    db_ajuste = AjusteInventarioVendedor(
        vendedor_id=ajuste.vendedor_id,
        producto_id=ajuste.producto_id,
        tipo_ajuste=ajuste.tipo_ajuste,
        cantidad=ajuste.cantidad,
        cantidad_anterior=cantidad_anterior,
        cantidad_nueva=cantidad_nueva,
        razon=ajuste.razon or "Ajuste manual",
        ajustado_por=ajuste.ajustado_por or 1
    )
    db.add(db_ajuste)
    
    db.commit()
    db.refresh(db_ajuste)
    return db_ajuste

# ===============================================
# ASIGNACIONES ENDPOINTS
# ===============================================

@router.get("/asignaciones", response_model=List[AsignacionResponse])
async def get_asignaciones(
    vendedor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de asignaciones de productos"""
    query = db.query(AsignacionProductoVendedor)
    
    if vendedor_id:
        query = query.filter(AsignacionProductoVendedor.vendedor_id == vendedor_id)
    
    asignaciones = query.order_by(
        AsignacionProductoVendedor.fecha_asignacion.desc()
    ).offset(skip).limit(limit).all()
    return asignaciones

# ===============================================
# ESTADISTICAS ENDPOINTS
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

@router.get("/estadisticas/vendedor/{vendedor_id}")
async def get_estadisticas_vendedor(vendedor_id: int, db: Session = Depends(get_db)):
    """Obtiene estadísticas de un vendedor específico"""
    vendedor = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    # Productos asignados
    productos_asignados = db.query(StockVendedor).filter(
        StockVendedor.vendedor_id == vendedor_id,
        StockVendedor.cantidad_actual > 0
    ).count()
    
    # Stock total
    stock_total = db.query(func.sum(StockVendedor.cantidad_actual)).filter(
        StockVendedor.vendedor_id == vendedor_id
    ).scalar() or 0
    
    # Valor del inventario
    valor_inventario = db.query(
        func.sum(StockVendedor.cantidad_actual * Producto.precio_unitario)
    ).join(Producto).filter(
        StockVendedor.vendedor_id == vendedor_id
    ).scalar() or 0
    
    # Total de ventas
    total_ventas = db.query(VentaVendedor).filter(
        VentaVendedor.vendedor_id == vendedor_id
    ).count()
    
    # Valor total vendido
    valor_vendido = db.query(
        func.sum(VentaVendedor.cantidad * VentaVendedor.precio_venta)
    ).filter(
        VentaVendedor.vendedor_id == vendedor_id
    ).scalar() or 0
    
    return {
        "vendedor_id": vendedor.id,
        "vendedor_nombre": vendedor.nombre,
        "productos_asignados": productos_asignados,
        "stock_total": int(stock_total),
        "valor_inventario": float(valor_inventario),
        "total_ventas": total_ventas,
        "valor_vendido": float(valor_vendido)
    }

@router.get("/estadisticas/producto/{producto_id}")
async def get_estadisticas_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtiene estadísticas de un producto específico"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Stock total del producto
    stock_total = db.query(func.sum(StockVendedor.cantidad_actual)).filter(
        StockVendedor.producto_id == producto_id
    ).scalar() or 0
    
    # Vendedores que tienen este producto
    vendedores_con_producto = db.query(StockVendedor).filter(
        StockVendedor.producto_id == producto_id,
        StockVendedor.cantidad_actual > 0
    ).count()
    
    # Total vendido
    total_vendido = db.query(func.sum(VentaVendedor.cantidad)).filter(
        VentaVendedor.producto_id == producto_id
    ).scalar() or 0
    
    # Valor total vendido
    valor_vendido = db.query(
        func.sum(VentaVendedor.cantidad * VentaVendedor.precio_venta)
    ).filter(
        VentaVendedor.producto_id == producto_id
    ).scalar() or 0
    
    return {
        "producto_id": producto.id,
        "producto_nombre": producto.nombre,
        "producto_codigo": producto.codigo,
        "precio_unitario": float(producto.precio_unitario),
        "stock_total": int(stock_total),
        "vendedores_asignados": vendedores_con_producto,
        "total_vendido": int(total_vendido),
        "valor_vendido": float(valor_vendido),
        "valor_en_stock": float(stock_total * producto.precio_unitario)
    }