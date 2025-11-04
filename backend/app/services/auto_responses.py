# backend/app/services/auto_responses.py
"""Servicio de respuestas automáticas del chatbot"""

import re
from typing import Optional, Dict, Tuple

# Catálogo de productos con sus descripciones
PRODUCT_CATALOG = {
    "blueberry": {
        "name": "Productos de Arándano",
        "response": """🍬 *Productos de Arándano HGW*

*Blueberry Candy (Caramelo de arándano)*
💰 Caramelos naturales con extracto de arándano
✅ Aportan antioxidantes
✅ Ayudan a la salud ocular
✅ Refuerzan el sistema inmunológico
✅ Combaten radicales libres

*Blueberry Concentrate (Concentrado)*
💧 Potente antioxidante líquido
✅ Protege las células
✅ Mejora la circulación
✅ Fortalece la vista
✅ Ideal para gastritis y estrés oxidativo

*Blueberry Fruit Tea (Té)*
☕ Infusión antioxidante natural
✅ Favorece la digestión
✅ Protege la vista
✅ Equilibrio hormonal
✅ Combate el cansancio

Habla con Richard para precios especiales:
📞 +57 305 2490438"""
    },
    "cafe": {
        "name": "Café con Ganoderma",
        "response": """☕ *Café con Ganoderma HGW*

Café premium mezclado con el hongo Ganoderma Lucidum (Rey de las Hierbas)

*Beneficios:*
✅ Energía sin nerviosismo
✅ Fortalece sistema inmune
✅ Mejora concentración
✅ Antioxidante potente
✅ Regula presión arterial
✅ Protege el hígado

*Presentaciones:*
• Café 3 en 1 (con crema y azúcar)
• Café negro puro
• Café con Cordyceps (extra energía)

Sin acidez ni efectos secundarios del café tradicional.

Pide el tuyo con Richard:
📞 +57 305 2490438"""
    },
    "omega": {
        "name": "Omega 3-6-9",
        "response": """💊 *Omega 3-6-9 HGW*

Ácidos grasos esenciales de origen vegetal

*Beneficios principales:*
✅ Salud cardiovascular
✅ Reduce colesterol malo
✅ Mejora memoria y concentración
✅ Antiinflamatorio natural
✅ Piel y cabello saludables
✅ Regula hormonas

*Ideal para:*
• Personas con colesterol alto
• Estudiantes y profesionales
• Deportistas
• Adultos mayores
• Cuidado preventivo

100% natural, sin mercurio ni contaminantes.

Consulta precio con Richard:
📞 +57 305 2490438"""
    }
}

class AutoResponseService:
    """Servicio para generar respuestas automáticas del chatbot"""
    
    def __init__(self):
        self.business_prompt = """
Eres un asistente virtual de HGW (Health Green World) para la organización Empoderando Líderes, trabajando junto a Richard Córdoba.

🎯 Tu misión es:
1. Dar la bienvenida de forma cercana, alegre y profesional.
2. Preguntar el nombre de la persona para crear confianza.
3. Mostrar empatía según el perfil del cliente.
4. Explicar los beneficios de HGW: Ingresos semanales, sistema de puntos, oportunidad global.
5. Ser persuasivo de forma natural y casual.
6. Siempre invitar a agendar una llamada con Richard Córdoba 📞 al +57 305 2490438.
7. Termina con tono positivo y motivador.

Respuestas cortas y conversacionales: máximo 2-3 párrafos cortos.
Habla como un amigo que quiere ayudar, no como un vendedor.
"""
    
    def detect_profile(self, message: str) -> str:
        """Detecta el perfil del usuario según su mensaje"""
        msg_lower = message.lower()
        
        if any(word in msg_lower for word in ["tiempo", "ocupado", "ocupada", "trabajo mucho"]):
            return "sin_tiempo"
        elif any(word in msg_lower for word in ["dinero", "joven", "estudiante", "poco", "alcanza"]):
            return "joven_economico"
        elif any(word in msg_lower for word in ["salud", "bienestar", "natural", "sano", "enfermo"]):
            return "bienestar"
        elif any(word in msg_lower for word in ["negocio", "emprender", "ganar", "ingresos"]):
            return "emprendedor"
        
        return "otro"
    
    def detect_interest_level(self, message: str) -> int:
        """Detecta el nivel de interés del usuario (0-10)"""
        msg_lower = message.lower()
        
        # Alto interés (8-10)
        if any(word in msg_lower for word in ["precio", "costo", "empezar", "quiero", "inscribir", "unirme"]):
            return 9
        elif any(word in msg_lower for word in ["cuanto", "como empiezo", "registrar"]):
            return 8
        
        # Interés medio (5-7)
        elif any(word in msg_lower for word in ["información", "info", "cuéntame", "saber más"]):
            return 6
        elif any(word in msg_lower for word in ["interesante", "me llama", "curioso"]):
            return 7
        
        # Bajo interés (1-4)
        elif any(word in msg_lower for word in ["no gracias", "no interesa", "paso"]):
            return 2
        elif any(word in msg_lower for word in ["tal vez", "quizás", "luego", "después"]):
            return 4
        
        return 5
    
    def extract_name(self, message: str) -> Optional[str]:
        """Extrae el nombre del usuario del mensaje"""
        msg = message.strip()
        
        # Lista de palabras que NO son nombres
        palabras_excluidas = [
            "hola", "buenas", "buenos", "dias", "tardes", "noches",
            "hello", "hi", "hey", "que", "como", "gracias", "bien",
            "mal", "si", "no", "ok", "vale", "claro", "perfecto",
            "ola", "bueno", "tarde", "dia", "noche", "saludos"
        ]
        
        # Patrones comunes: "soy X", "me llamo X", "mi nombre es X"
        patterns = [
            r"(?:soy|me llamo|mi nombre es)\s+([a-záéíóúñA-ZÁÉÍÓÚÑ][a-záéíóúñ]+)",
            r"^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,})$",  # Solo un nombre con mayúscula inicial
        ]
        
        for pattern in patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                name = match.group(1).strip().capitalize()
                if name.lower() not in palabras_excluidas and len(name) >= 3:
                    return name
        
        return None
    
    def get_greeting_response(self, user_name: Optional[str] = None) -> str:
        """Genera respuesta de saludo"""
        greeting = f"¡Hola {user_name}! 👋" if user_name else "¡Hola! 👋"
        
        return f"""{greeting} Bienvenido a *HGW (Health Green World)*
🌿 *Empoderando Líderes con Richard Córdoba*

Somos una empresa transnacional con +30 años de experiencia en productos naturales para salud y bienestar, presente en más de 30 países.

*¿Qué te interesa conocer?*

🛒 Ver catálogo de productos
💰 Oportunidad de negocio
📊 Cuánto puedo ganar
🚀 Cómo empezar
❓ Qué es HGW

Escribe lo que te interese o dime tu nombre para personalizar tu experiencia 😊"""
    
    def get_join_response(self, user_name: Optional[str] = None) -> str:
        """Genera respuesta para unirse al negocio"""
        nombre = user_name if user_name else "amigo/a"
        
        return f"""¡Excelente decisión, {nombre}! 🎉

Para unirte a HGW es muy sencillo:

*PASO 1:* Habla con Richard Córdoba 📞
Él te explicará los planes disponibles y te guiará en todo el proceso.

*PASO 2:* Elige tu plan 💰
Hay opciones para todos los presupuestos. Desde inversión pequeña hasta planes más grandes.

*PASO 3:* Registro rápido 📝
Richard te enviará tu enlace personalizado y completarás tu registro.

*PASO 4:* ¡Listo! 🚀
Recibes tu kit, capacitación y empiezas a ganar.

*Contacta a Richard ahora:*
📱 WhatsApp: +57 305 2490438

Dile: "Hola Richard, {user_name if user_name else 'me interesa'} quiero unirme a HGW"

¿Tienes alguna pregunta antes de contactarlo? 😊"""
    
    def get_product_response(self, product_key: str) -> Optional[str]:
        """Obtiene la respuesta para un producto específico"""
        return PRODUCT_CATALOG.get(product_key, {}).get("response")
    
    def get_catalog_response(self) -> str:
        """Genera respuesta con el catálogo general"""
        return """🛒 *Catálogo HGW Colombia*

Tenemos productos 100% naturales certificados:

*🥗 Alimentos y Bebidas:*
• Blueberry Candy, Fresh Candy
• Concentrado de Arándanos
• Té de Arándanos
• Café con Ganoderma / Cordyceps
• Omega 3-6-9, Espirulina

*🧼 Higiene Personal:*
• Pasta dental herbal
• Jabones (turmalina, oliva)
• Shampoo Keratina
• Gel de ducha

*🌸 Productos Femeninos:*
• Toallas sanitarias Smilife
• Protectores diarios

*💎 Bienestar Físico:*
• Termos con turmalina
• Collares y pulseras

Escribe el nombre del producto que te interesa para más detalles 😊

O habla con Richard: +57 305 2490438"""
    
    def get_automatic_response(self, message: str, user_name: Optional[str] = None) -> Tuple[Optional[str], Dict]:
        """
        Genera una respuesta automática basada en palabras clave
        
        Returns:
            Tuple[Optional[str], Dict]: (respuesta, metadata)
        """
        msg_lower = message.lower()
        metadata = {
            "profile": self.detect_profile(message),
            "interest_level": self.detect_interest_level(message),
            "detected_name": self.extract_name(message)
        }
        
        # Actualizar nombre si se detectó
        if metadata["detected_name"]:
            user_name = metadata["detected_name"]
        
        # Saludos
        if any(w in msg_lower for w in ["hola", "buenas", "buenos días", "buenas tardes", "hi", "hello"]) and len(msg_lower) < 30:
            return self.get_greeting_response(user_name), metadata
        
        # Unirse al negocio
        if any(w in msg_lower for w in ["unirme", "unir", "inscribirme", "registrarme", "ser parte", "entrar", "empezar"]):
            return self.get_join_response(user_name), metadata
        
        # Productos específicos
        for product_key, product_info in PRODUCT_CATALOG.items():
            if product_key in msg_lower:
                response = self.get_product_response(product_key)
                if response:
                    return response, metadata
        
        # Catálogo general
        if any(w in msg_lower for w in ["producto", "catalogo", "catálogo", "qué venden", "que tienen"]):
            return self.get_catalog_response(), metadata
        
        # Precios
        if any(w in msg_lower for w in ["precio", "costo", "cuanto", "valor"]):
            return self._get_price_response(user_name), metadata
        
        # Ganancias
        if any(w in msg_lower for w in ["ganar", "ganancia", "ingreso", "dinero", "comision"]):
            return self._get_earnings_response(), metadata
        
        # Sobre HGW
        if any(w in msg_lower for w in ["qué es hgw", "que es hgw", "empresa", "compañía"]):
            return self._get_about_hgw_response(), metadata
        
        return None, metadata
    
    def _get_price_response(self, user_name: Optional[str] = None) -> str:
        """Respuesta sobre precios"""
        nombre = user_name if user_name else "amigo/a"
        return f"""💰 *Información de Precios*

{nombre}, tenemos diferentes opciones de inversión para empezar:

*Planes de Inicio:*
• Plan Básico: Desde inversión mínima
• Plan Profesional: Mayor inventario
• Plan Empresarial: Máximo beneficio

Los precios varían según el plan y productos que elijas.

Para darte los precios exactos y promociones actuales, habla directamente con Richard:

📱 WhatsApp: +57 305 2490438

Él te dará toda la información de precios y te ayudará a elegir el mejor plan para ti. ¿Te interesa algún plan en particular?"""
    
    def _get_earnings_response(self) -> str:
        """Respuesta sobre ganancias"""
        return """💰 *¿Cuánto puedo ganar en HGW?*

Tu ingreso depende de tu dedicación:

*Ganancias Directas:*
• 30% a 52% por venta de productos
• Comisiones semanales
• Bonos por volumen

*Ganancias por Red:*
• Comisiones hasta 10 generaciones
• Bonos de liderazgo
• Viajes y premios

*Ejemplos reales:*
✅ Tiempo parcial: $500-$2000 USD/mes
✅ Tiempo completo: $2000-$10,000 USD/mes
✅ Líderes top: $10,000+ USD/mes

Sin límite de ingresos. Tu éxito depende de ti.

Habla con Richard para plan personalizado:
📞 +57 305 2490438"""
    
    def _get_about_hgw_response(self) -> str:
        """Respuesta sobre qué es HGW"""
        return """🌿 *¿Qué es HGW (Health Green World)?*

HGW es una empresa transnacional de venta directa con más de 30 años de trayectoria, presente en más de 30 países.

*Ofrecemos:*
✅ Productos naturales de salud y bienestar
✅ Sistema de compensación "Plan de Ganancia Mutua"
✅ Oportunidad de negocio flexible
✅ Capacitación completa y apoyo

*Nuestro modelo:*
• Vendes productos con margen de 30% a 52%
• Construyes tu red de distribuidores
• Ganas comisiones hasta 10 generaciones
• Sin límite de ingresos

¿Quieres saber más? Habla con Richard:
📞 +57 305 2490438"""
