# backend/admin_routes.py - VERSIÓN CORREGIDA
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, text
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models import Conversation, Message, Lead
from auth import get_current_user

router = APIRouter()

# ==================== CONVERSACIONES ====================

@router.get("/conversations")
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene todas las conversaciones"""
    query = db.query(Conversation)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Conversation.phone_number.like(search_filter)) |
            (Conversation.user_name.ilike(search_filter))
        )
    
    if status:
        query = query.filter(Conversation.status == status)
    
    conversations = query.order_by(
        Conversation.last_interaction.desc()
    ).offset(skip).limit(limit).all()
    
    return [{
        "id": c.id,
        "phone_number": c.phone_number,
        "user_name": c.user_name,
        "status": c.status,
        "profile_type": c.profile_type,
        "last_interaction": c.last_interaction,
        "created_at": c.created_at,
        "messages_count": len(c.messages)
    } for c in conversations]

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene una conversación específica con sus mensajes"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()
    
    return {
        "conversation": {
            "id": conversation.id,
            "phone_number": conversation.phone_number,
            "user_name": conversation.user_name,
            "status": conversation.status,
            "profile_type": conversation.profile_type,
            "last_interaction": conversation.last_interaction,
            "created_at": conversation.created_at
        },
        "messages": [{
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp
        } for m in messages]
    }

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene los mensajes de una conversación"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()
    
    return [{
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "timestamp": m.timestamp
    } for m in messages]

@router.put("/conversations/{conversation_id}/status")
async def update_conversation_status(
    conversation_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza el estado de una conversación"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    conversation.status = status
    conversation.last_interaction = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Estado actualizado"}

# ==================== LEADS ====================

@router.get("/leads")
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    min_interest: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene todos los leads"""
    query = db.query(Lead)
    
    if min_interest:
        query = query.filter(Lead.interest_level >= min_interest)
    
    if status:
        query = query.filter(Lead.status == status)
    
    leads = query.order_by(
        Lead.interest_level.desc(),
        Lead.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [{
        "id": l.id,
        "phone_number": l.phone_number,
        "user_name": l.user_name,
        "email": l.email,
        "profile_type": l.profile_type,
        "interest_level": l.interest_level,
        "status": l.status,
        "notes": l.notes,
        "created_at": l.created_at,
        "updated_at": l.updated_at
    } for l in leads]

@router.get("/leads/{lead_id}")
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene un lead específico"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    # Buscar conversación relacionada
    conversation = db.query(Conversation).filter(
        Conversation.phone_number == lead.phone_number
    ).first()
    
    return {
        "lead": {
            "id": lead.id,
            "phone_number": lead.phone_number,
            "user_name": lead.user_name,
            "email": lead.email,
            "profile_type": lead.profile_type,
            "interest_level": lead.interest_level,
            "status": lead.status,
            "notes": lead.notes,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at
        },
        "conversation_id": conversation.id if conversation else None
    }

@router.put("/leads/{lead_id}")
async def update_lead(
    lead_id: int,
    status: Optional[str] = None,
    interest_level: Optional[int] = None,
    notes: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza un lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    if status:
        lead.status = status
    if interest_level is not None:
        lead.interest_level = interest_level
    if notes is not None:
        lead.notes = notes
    if email:
        lead.email = email
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Lead actualizado"}

@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_distributor(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Convierte un lead en distribuidor"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    # Marcar lead como convertido
    lead.status = "convertido"
    lead.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Lead marcado como convertido",
        "lead_phone": lead.phone_number
    }

# ==================== ESTADÍSTICAS ====================

@router.get("/stats/detailed")
async def get_detailed_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene estadísticas detalladas"""
    # Estadísticas generales
    total_conversations = db.query(Conversation).count()
    total_leads = db.query(Lead).count()
    high_interest = db.query(Lead).filter(Lead.interest_level >= 7).count()
    
    # Conversaciones últimos 7 días
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_conversations = db.query(Conversation).filter(
        Conversation.created_at >= week_ago
    ).count()
    
    # Leads por estado
    leads_by_status = db.query(
        Lead.status,
        func.count(Lead.id)
    ).group_by(Lead.status).all()
    
    # Perfiles más comunes
    profiles = db.query(
        Conversation.profile_type,
        func.count(Conversation.id)
    ).group_by(Conversation.profile_type).all()
    
    return {
        "general": {
            "total_conversations": total_conversations,
            "total_leads": total_leads,
            "high_interest_leads": high_interest,
            "recent_conversations": recent_conversations
        },
        "leads_by_status": {status: count for status, count in leads_by_status},
        "profiles": {profile: count for profile, count in profiles}
    }

@router.get("/stats/activity-flow")
async def get_activity_flow(
    months: int = Query(6, ge=1, le=12, description="Número de meses a obtener"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene el flujo de actividad (conversaciones por mes)"""
    try:
        # Nombres de meses en español
        month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                       'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Generar últimos N meses
        result = []
        current_date = datetime.utcnow()
        
        # Obtener datos de conversaciones
        start_date = current_date - timedelta(days=months * 30)
        conversations = db.query(Conversation).filter(
            Conversation.created_at >= start_date
        ).all()
        
        # Agrupar por mes manualmente
        month_counts = {}
        for conv in conversations:
            year_month = (conv.created_at.year, conv.created_at.month)
            month_counts[year_month] = month_counts.get(year_month, 0) + 1
        
        # Generar resultado para los últimos N meses
        for i in range(months - 1, -1, -1):
            target_date = current_date - timedelta(days=i * 30)
            year = target_date.year
            month = target_date.month
            month_idx = month - 1
            
            count = month_counts.get((year, month), 0)
            
            result.append({
                "month": month_names[month_idx],
                "value": count,
                "year": year,
                "month_number": month
            })
        
        return result
        
    except Exception as e:
        # Si hay error, devolver array vacío
        print(f"Error en activity-flow: {str(e)}")
        return []