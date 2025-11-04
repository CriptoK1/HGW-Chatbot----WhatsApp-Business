# backend/app/api/v1/distributors.py
"""Endpoints para el CRUD de distribuidores"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, date
from passlib.context import CryptContext

from ...database import get_db
from ...models.distributor import Distributor
from ...schemas.distributor import (
    DistributorCreate, 
    DistributorUpdate, 
    DistributorResponse,
    DistributorListResponse
)

router = APIRouter(prefix="/distributors", tags=["distributors"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/stats/summary", response_model=dict)
async def get_distributors_stats(db: Session = Depends(get_db)):
    """Obtiene estadísticas de los distribuidores"""
    total = db.query(Distributor).count()
    activos = db.query(Distributor).filter(Distributor.estado == "activo").count()
    inactivos = db.query(Distributor).filter(Distributor.estado == "inactivo").count()
    suspendidos = db.query(Distributor).filter(Distributor.estado == "suspendido").count()
    
    # Contar por nivel
    niveles = {}
    for nivel in ["Pre-Junior", "Junior", "Senior", "Master"]:
        count = db.query(Distributor).filter(
            Distributor.nivel == nivel,
            Distributor.estado == "activo"
        ).count()
        niveles[nivel] = count
    
    return {
        "total": total,
        "por_estado": {
            "activos": activos,
            "inactivos": inactivos,
            "suspendidos": suspendidos
        },
        "por_nivel": niveles
    }

@router.get("/", response_model=List[DistributorListResponse])
async def get_all_distributors(
    skip: int = 0,
    limit: int = Query(default=100, le=1000),
    search: Optional[str] = None,
    estado: Optional[str] = None,
    nivel: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los distribuidores con filtros opcionales
    
    - **search**: Busca en nombres, apellidos, teléfono, email y usuario
    - **estado**: Filtra por estado (activo, inactivo, suspendido)
    - **nivel**: Filtra por nivel (Pre-Junior, Junior, Senior, Master)
    """
    query = db.query(Distributor)
    
    # Aplicar filtros
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Distributor.nombres.ilike(search_filter),
                Distributor.apellidos.ilike(search_filter),
                Distributor.telefono.like(search_filter),
                Distributor.email.ilike(search_filter),
                Distributor.usuario.ilike(search_filter)
            )
        )
    
    if estado:
        query = query.filter(Distributor.estado == estado)
    
    if nivel:
        query = query.filter(Distributor.nivel == nivel)
    
    # Ordenar y paginar
    distributors = query.order_by(Distributor.created_at.desc()).offset(skip).limit(limit).all()
    
    return [d.to_dict() for d in distributors]

@router.get("/{distributor_id}", response_model=DistributorResponse)
async def get_distributor(distributor_id: int, db: Session = Depends(get_db)):
    """Obtiene un distribuidor específico por ID"""
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    return distributor.to_dict(include_sensitive=True)

@router.post("/", response_model=dict)
async def create_distributor(distributor: DistributorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo distribuidor"""
    
    # Verificar que no exista el teléfono, email o usuario
    existing = db.query(Distributor).filter(
        or_(
            Distributor.telefono == distributor.telefono,
            Distributor.usuario == distributor.usuario,
            Distributor.email == distributor.email if distributor.email else False
        )
    ).first()
    
    if existing:
        if existing.telefono == distributor.telefono:
            raise HTTPException(status_code=400, detail="Ya existe un distribuidor con ese teléfono")
        elif existing.usuario == distributor.usuario:
            raise HTTPException(status_code=400, detail="Ya existe un distribuidor con ese usuario")
        elif existing.email == distributor.email:
            raise HTTPException(status_code=400, detail="Ya existe un distribuidor con ese email")
    
    # Crear el nuevo distribuidor
    db_distributor = Distributor(
        nombres=distributor.nombres,
        apellidos=distributor.apellidos,
        telefono=distributor.telefono,
        email=distributor.email,
        fecha_ingreso=distributor.fecha_ingreso,
        fecha_cumpleanos=distributor.fecha_cumpleanos,
        usuario=distributor.usuario,
        contrasena=pwd_context.hash(distributor.contrasena),
        contrasena_doble_factor=pwd_context.hash(distributor.contrasena_doble_factor) if distributor.contrasena_doble_factor else None,
        nivel=distributor.nivel or "Pre-Junior",
        estado=distributor.estado or "activo",
        lead_phone=distributor.lead_phone,
        notas=distributor.notas
    )
    
    db.add(db_distributor)
    db.commit()
    db.refresh(db_distributor)
    
    return {
        "success": True,
        "id": db_distributor.id,
        "message": "Distribuidor creado exitosamente"
    }

@router.put("/{distributor_id}", response_model=dict)
async def update_distributor(
    distributor_id: int, 
    distributor: DistributorUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza un distribuidor existente"""
    db_distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not db_distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    # Verificar unicidad si se está actualizando teléfono, email o usuario
    if distributor.telefono and distributor.telefono != db_distributor.telefono:
        existing = db.query(Distributor).filter(Distributor.telefono == distributor.telefono).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un distribuidor con ese teléfono")
    
    if distributor.email and distributor.email != db_distributor.email:
        existing = db.query(Distributor).filter(Distributor.email == distributor.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un distribuidor con ese email")
    
    if distributor.usuario and distributor.usuario != db_distributor.usuario:
        existing = db.query(Distributor).filter(Distributor.usuario == distributor.usuario).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un distribuidor con ese usuario")
    
    # Actualizar solo los campos que se enviaron
    update_data = distributor.dict(exclude_unset=True)
    
    # Hashear contraseñas si se están actualizando
    if "contrasena" in update_data and update_data["contrasena"]:
        update_data["contrasena"] = pwd_context.hash(update_data["contrasena"])
    
    if "contrasena_doble_factor" in update_data and update_data["contrasena_doble_factor"]:
        update_data["contrasena_doble_factor"] = pwd_context.hash(update_data["contrasena_doble_factor"])
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(db_distributor, field, value)
    
    db_distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Distribuidor actualizado correctamente"
    }

@router.delete("/{distributor_id}", response_model=dict)
async def delete_distributor(distributor_id: int, db: Session = Depends(get_db)):
    """Elimina un distribuidor (soft delete cambiando estado)"""
    db_distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not db_distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    # Opción 1: Soft delete (cambiar estado)
    db_distributor.estado = "eliminado"
    db_distributor.updated_at = datetime.utcnow()
    
    # Opción 2: Hard delete (eliminar de la BD)
    # db.delete(db_distributor)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Distribuidor eliminado correctamente"
    }

@router.post("/{distributor_id}/activate", response_model=dict)
async def activate_distributor(distributor_id: int, db: Session = Depends(get_db)):
    """Activa un distribuidor"""
    db_distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not db_distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    db_distributor.estado = "activo"
    db_distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Distribuidor activado correctamente"
    }

@router.post("/{distributor_id}/suspend", response_model=dict)
async def suspend_distributor(distributor_id: int, db: Session = Depends(get_db)):
    """Suspende un distribuidor"""
    db_distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not db_distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    db_distributor.estado = "suspendido"
    db_distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Distribuidor suspendido"
    }