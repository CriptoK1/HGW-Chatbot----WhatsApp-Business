# backend/app/services/whatsapp.py
"""Servicio para interactuar con la API de WhatsApp Business"""

import httpx
import logging
from typing import Optional, Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Servicio para manejar la comunicación con WhatsApp Business API"""
    
    def __init__(self):
        self.token = settings.WHATSAPP_TOKEN
        self.phone_id = settings.WHATSAPP_PHONE_ID
        self.api_url = f"{settings.WHATSAPP_API_URL}/{self.phone_id}/messages"
        self.processed_messages = set()  # Para evitar duplicados
        
    async def send_message(self, to: str, message: str) -> bool:
        """
        Envía un mensaje de WhatsApp
        
        Args:
            to: Número de teléfono del destinatario
            message: Texto del mensaje
            
        Returns:
            bool: True si se envió correctamente, False si hubo error
        """
        if not self.token or not self.phone_id:
            logger.error("WhatsApp credentials not configured")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Message sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Error sending message: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Exception sending message: {str(e)}")
            return False
    
    def send_message_sync(self, to: str, message: str) -> bool:
        """
        Versión síncrona para enviar mensaje (para compatibilidad)
        """
        if not self.token or not self.phone_id:
            logger.error("WhatsApp credentials not configured")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = httpx.post(
                self.api_url,
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {to}")
                return True
            else:
                logger.error(f"Error sending message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Exception sending message: {str(e)}")
            return False
    
    def parse_webhook(self, data: Dict[Any, Any]) -> Optional[Dict[str, Any]]:
        """
        Parsea el webhook de WhatsApp y extrae la información del mensaje
        
        Args:
            data: Datos del webhook
            
        Returns:
            Dict con la información del mensaje o None si no es válido
        """
        try:
            # Verificar estructura del webhook
            if "entry" not in data or not data["entry"]:
                return None
                
            entry = data["entry"][0]
            if "changes" not in entry or not entry["changes"]:
                return None
                
            change = entry["changes"][0]
            if "value" not in change:
                return None
                
            value = change["value"]
            if "messages" not in value or not value["messages"]:
                return None
                
            message = value["messages"][0]
            message_id = message.get("id")
            
            # Verificar si ya procesamos este mensaje
            if message_id in self.processed_messages:
                logger.info(f"Message {message_id} already processed, skipping")
                return None
                
            # Marcar como procesado
            self.processed_messages.add(message_id)
            
            # Limpiar mensajes antiguos del set (mantener solo últimos 1000)
            if len(self.processed_messages) > 1000:
                self.processed_messages.clear()
            
            # Extraer información del mensaje
            return {
                "id": message_id,
                "from": message.get("from"),
                "text": message.get("text", {}).get("body", ""),
                "timestamp": message.get("timestamp"),
                "type": message.get("type", "text")
            }
            
        except Exception as e:
            logger.error(f"Error parsing webhook: {str(e)}")
            return None
    
    def verify_webhook(self, token: str, challenge: str) -> Optional[str]:
        """
        Verifica el webhook de WhatsApp
        
        Args:
            token: Token de verificación recibido
            challenge: Challenge recibido
            
        Returns:
            Challenge si la verificación es correcta, None si no
        """
        if token == settings.VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return challenge
        else:
            logger.warning(f"Invalid verification token: {token}")
            return None
    
    def format_phone_number(self, phone: str) -> str:
        """
        Formatea el número de teléfono para WhatsApp
        
        Args:
            phone: Número de teléfono
            
        Returns:
            Número formateado
        """
        # Remover caracteres no numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Si no tiene código de país, agregar el de Colombia
        if not phone.startswith('57') and len(phone) == 10:
            phone = '57' + phone
            
        return phone
    
    async def send_template_message(self, to: str, template_name: str, parameters: list = None) -> bool:
        """
        Envía un mensaje usando una plantilla de WhatsApp
        
        Args:
            to: Número de destino
            template_name: Nombre de la plantilla
            parameters: Parámetros de la plantilla
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.token or not self.phone_id:
            logger.error("WhatsApp credentials not configured")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "es"}
            }
        }
        
        # Agregar parámetros si existen
        if parameters:
            data["template"]["components"] = [{
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in parameters]
            }]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Template message sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Error sending template message: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Exception sending template message: {str(e)}")
            return False
    
    def is_message_duplicate(self, message_id: str) -> bool:
        """
        Verifica si un mensaje es duplicado
        
        Args:
            message_id: ID del mensaje
            
        Returns:
            bool: True si es duplicado, False si no
        """
        return message_id in self.processed_messages
