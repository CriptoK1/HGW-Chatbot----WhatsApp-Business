# backend/distributor_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, date
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from database import get_db
from models import Distributor
from auth import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== SCHEMAS ====================

class DistributorCreate(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    telefono: str = Field(..., min_length=7)
    email: Optional[EmailStr] = None
    fecha_ingreso: date
    fecha_cumpleanos: Optional[date] = None
    usuario: str = Field(..., min_length=3)
    contrasena: str = Field(..., min_length=6)
    contrasena_doble_factor: Optional[str] = None
    nivel: str = "Pre-Junior"
    estado: str = "activo"
    notas: Optional[str] = None


class DistributorUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_ingreso: Optional[date] = None
    fecha_cumpleanos: Optional[date] = None
    usuario: Optional[str] = None
    contrasena: Optional[str] = None
    contrasena_doble_factor: Optional[str] = None
    nivel: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None


# ==================== ENDPOINTS ====================

@router.get("/")
async def get_distributors(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    estado: Optional[str] = None,
    nivel: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene todos los distribuidores con filtros"""
    query = db.query(Distributor)
    
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
    
    distributors = query.offset(skip).limit(limit).all()
    
    return [{
        "id": d.id,
        "nombres": d.nombres,
        "apellidos": d.apellidos,
        "nombre_completo": f"{d.nombres} {d.apellidos}",
        "telefono": d.telefono,
        "email": d.email,
        "usuario": d.usuario,
        "nivel": d.nivel,
        "estado": d.estado,
        "fecha_ingreso": d.fecha_ingreso,
        "fecha_cumpleanos": d.fecha_cumpleanos,
        "notas": d.notas,
        # ✅ columnas nuevas visibles
        "contrasena_texto": d.contrasena_texto,
        "contrasena_2fa_texto": d.contrasena_2fa_texto,
        "created_at": d.created_at
    } for d in distributors]


@router.get("/{distributor_id}")
async def get_distributor(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene un distribuidor por ID"""
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    return {
        "id": distributor.id,
        "nombres": distributor.nombres,
        "apellidos": distributor.apellidos,
        "telefono": distributor.telefono,
        "email": distributor.email,
        "usuario": distributor.usuario,
        "nivel": distributor.nivel,
        "estado": distributor.estado,
        "fecha_ingreso": distributor.fecha_ingreso,
        "fecha_cumpleanos": distributor.fecha_cumpleanos,
        "notas": distributor.notas,
        # ✅ visibles
        "contrasena_texto": distributor.contrasena_texto,
        "contrasena_2fa_texto": distributor.contrasena_2fa_texto,
        "created_at": distributor.created_at,
        "updated_at": distributor.updated_at
    }


@router.post("/")
async def create_distributor(
    distributor: DistributorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Crea un nuevo distribuidor"""
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

    db_distributor = Distributor(
        nombres=distributor.nombres,
        apellidos=distributor.apellidos,
        telefono=distributor.telefono,
        email=distributor.email,
        fecha_ingreso=distributor.fecha_ingreso,
        fecha_cumpleanos=distributor.fecha_cumpleanos,
        usuario=distributor.usuario,
        contrasena=pwd_context.hash(distributor.contrasena),
        contrasena_texto=distributor.contrasena,  # ✅ texto visible
        nivel=distributor.nivel or "Pre-Junior",
        estado=distributor.estado or "activo",
        notas=distributor.notas
    )

    if distributor.contrasena_doble_factor:
        db_distributor.contrasena_doble_factor = pwd_context.hash(distributor.contrasena_doble_factor)
        db_distributor.contrasena_2fa_texto = distributor.contrasena_doble_factor  # ✅ texto visible
    
    db.add(db_distributor)
    db.commit()
    db.refresh(db_distributor)
    
    return {
        "success": True,
        "id": db_distributor.id,
        "message": "Distribuidor creado exitosamente"
    }


@router.put("/{distributor_id}")
async def update_distributor(
    distributor_id: int,
    distributor_data: DistributorUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza un distribuidor"""
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    update_data = distributor_data.dict(exclude_unset=True)

    if "contrasena" in update_data and update_data["contrasena"]:
        plain_password = update_data["contrasena"]
        update_data["contrasena"] = pwd_context.hash(plain_password)
        update_data["contrasena_texto"] = plain_password

    if "contrasena_doble_factor" in update_data and update_data["contrasena_doble_factor"]:
        plain_2fa = update_data["contrasena_doble_factor"]
        update_data["contrasena_doble_factor"] = pwd_context.hash(plain_2fa)
        update_data["contrasena_2fa_texto"] = plain_2fa

    for field, value in update_data.items():
        setattr(distributor, field, value)
    
    distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Distribuidor actualizado"}


@router.delete("/{distributor_id}")
async def delete_distributor(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Elimina un distribuidor (soft delete)"""
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    distributor.estado = "eliminado"
    distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Distribuidor eliminado"}


@router.post("/{distributor_id}/activate")
async def activate_distributor(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    distributor.estado = "activo"
    distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Distribuidor activado"}


@router.post("/{distributor_id}/suspend")
async def suspend_distributor(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    distributor = db.query(Distributor).filter(Distributor.id == distributor_id).first()
    
    if not distributor:
        raise HTTPException(status_code=404, detail="Distribuidor no encontrado")
    
    distributor.estado = "suspendido"
    distributor.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Distribuidor suspendido"}