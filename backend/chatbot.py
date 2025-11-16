import httpx
import os
from openai import OpenAI
from sqlalchemy.orm import Session
from datetime import datetime
from models import Conversation, Message, Lead
import re

class ChatbotService:
    def __init__(self):
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN")
        self.phone_id = os.getenv("WHATSAPP_PHONE_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = os.getenv("USE_OPENAI", "false").lower() == "true"
        
        if self.openai_api_key and self.use_openai:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
        
        self.processed_messages = set()
        self.business_prompt = """
        Eres un asistente experto de HGW (Health Green World) con Richard Córdoba.
        Tu objetivo es ayudar a las personas a entender claramente el negocio y motivarlas a empezar.
        Enfócate en las 5 preguntas clave: Qué es HGW, Qué hacer, Inversión, Recuperación, Ganancias.
        Sé claro, específico, usa números reales y ejemplos concretos.
        Respuestas completas pero fáciles de entender.
        Siempre invita a contactar a Richard al +57 305 2490438 para más detalles.
        """

    async def process_message(self, webhook_data: dict, db: Session):
        """Procesa mensaje entrante de WhatsApp"""
        message_info = self._parse_webhook(webhook_data)
        if not message_info:
            return None
        
        phone = message_info["from"]
        text = message_info["text"]
        msg_id = message_info["id"]
        
        if msg_id in self.processed_messages:
            return None
        self.processed_messages.add(msg_id)
        
        conversation = self._get_or_create_conversation(db, phone)
        
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=text
        )
        db.add(user_message)
        
        if not conversation.user_name:
            name = self._extract_name(text)
            if name:
                conversation.user_name = name
        
        conversation.profile_type = self._detect_profile(text)
        self._update_lead(db, phone, conversation.user_name, text)
        
        response = await self._generate_response(text, conversation, db)
        
        bot_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response
        )
        db.add(bot_message)
        
        conversation.last_interaction = datetime.utcnow()
        db.commit()
        
        await self._send_whatsapp_message(phone, response)
        return response

    def _parse_webhook(self, data: dict):
        """Parsea el webhook de WhatsApp"""
        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return None
            
            message = messages[0]
            return {
                "id": message.get("id"),
                "from": message.get("from"),
                "text": message.get("text", {}).get("body", ""),
                "timestamp": message.get("timestamp")
            }
        except:
            return None

    def _get_or_create_conversation(self, db: Session, phone: str):
        """Obtiene o crea una conversación"""
        conversation = db.query(Conversation).filter(
            Conversation.phone_number == phone
        ).first()
        
        if not conversation:
            conversation = Conversation(
                phone_number=phone,
                status="nuevo",
                profile_type="otro"
            )
            db.add(conversation)
            db.flush()
        
        return conversation

    def _extract_name(self, text: str):
        """Extrae el nombre del texto"""
        patterns = [
            r"(?:soy|me llamo|mi nombre es)\s+([A-Za-zÁÉÍÓÚÑáéíóúñ]+)",
            r"^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,})$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                if len(name) >= 3:
                    return name
        return None

    def _detect_profile(self, text: str):
        """Detecta el perfil del usuario"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["tiempo", "ocupado", "trabajo", "empleado"]):
            return "sin_tiempo"
        elif any(w in text_lower for w in ["dinero", "joven", "estudiante", "poco presupuesto"]):
            return "joven_economico"
        elif any(w in text_lower for w in ["salud", "bienestar", "natural", "enfermedad"]):
            return "bienestar"
        elif any(w in text_lower for w in ["negocio", "emprender", "ganar", "ingresos", "libertad financiera"]):
            return "emprendedor"
        
        return "otro"

    def _update_lead(self, db: Session, phone: str, name: str, text: str):
        """Actualiza o crea un lead"""
        lead = db.query(Lead).filter(Lead.phone_number == phone).first()
        interest = self._detect_interest(text)
        
        if not lead:
            lead = Lead(
                phone_number=phone,
                user_name=name,
                profile_type=self._detect_profile(text),
                interest_level=interest,
                status="nuevo"
            )
            db.add(lead)
        else:
            lead.interest_level = max(lead.interest_level, interest)
            lead.updated_at = datetime.utcnow()
            if name and not lead.user_name:
                lead.user_name = name

    def _detect_interest(self, text: str):
        """Detecta nivel de interés (0-10)"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["quiero empezar", "inscribirme", "registrarme", "cuánto cuesta"]):
            return 9
        elif any(w in text_lower for w in ["me interesa", "cuéntame más", "información"]):
            return 7
        elif any(w in text_lower for w in ["quizás", "tal vez", "no sé"]):
            return 4
        elif any(w in text_lower for w in ["no gracias", "no interesa"]):
            return 1
        
        return 5

    async def _generate_response(self, text: str, conversation, db: Session):
        """Genera respuesta del chatbot"""
        auto_response = self._get_auto_response(text, conversation.user_name)
        if auto_response:
            return auto_response
        
        if self.openai_client and self.use_openai:
            return await self._get_ai_response(text, conversation, db)
        
        return self._get_default_response(conversation.user_name)

    def _get_auto_response(self, text: str, user_name: str = None):
        """Respuestas automáticas mejoradas - LAS 5 PREGUNTAS CLAVE SON PRIORIDAD"""
        t = text.lower().strip()
        greeting = f"¡Hola {user_name}! 👋" if user_name else "¡Hola! 👋"

        if t in ["1", "1️⃣"]:
            t = "qué es hgw"
        elif t in ["2", "2️⃣"]:
            t = "qué tengo que hacer"
        elif t in ["3", "3️⃣"]:
            t = "inversión"
        elif t in ["4", "4️⃣"]:
            t = "recuperar inversión"
        elif t in ["5", "5️⃣"]:
            t = "cuándo gano"
        elif t in ["6", "6️⃣"]:
            t = "productos"
        elif t in ["7", "7️⃣"]:
            t = "richard"
        
        # ============ SALUDO INICIAL MEJORADO ============
        if any(w in t for w in ["hola", "buenas", "buenos días", "buenas tardes", "hi", "hello"]) and len(t) < 25:
            return f"""{greeting}

           ¡Bienvenido a *HGW - Empoderando Líderes* con Richard Córdoba! 🌿

Antes de empezar, déjame contarte lo MÁS IMPORTANTE en *5 puntos clave*:

*1️⃣ ¿QUÉ ES HGW?*
Una empresa internacional de productos naturales con 30+ años de experiencia. Sistema de venta directa LEGAL que te permite ganar dinero desde casa.

*2️⃣ ¿QUÉ HACES EXACTAMENTE?*
Dos cosas: Vendes productos naturales (margen 30%-52%) + Construyes un equipo (ganas comisiones de sus ventas).

*3️⃣ ¿CUÁNTO NECESITO INVERTIR?*
Desde $360.000 hasta $4.320.000 COP. Tú eliges según tu presupuesto. El plan más popular es $2.160.000 (Senior).

*4️⃣ ¿CUÁNDO RECUPERO MI INVERSIÓN?*
Entre 1 y 6 meses, dependiendo del plan y qué tan rápido vendas los productos de tu kit inicial.

*5️⃣ ¿CUÁNDO EMPIEZO A GANAR?*
Desde tu PRIMERA VENTA ya estás ganando dinero. No tienes que esperar meses para ver resultados.

*¿Qué quieres saber en detalle?*
Escribe el número o palabra:

1️⃣ *Qué es HGW* (explicación completa)
2️⃣ *Qué tengo que hacer* (actividades diarias)
3️⃣ *Inversión* (todos los planes)
4️⃣ *Recuperar inversión* (con ejemplos)
5️⃣ *Cuándo gano dinero* (cronograma real)
6️⃣ *Ver productos*
7️⃣ *Hablar con Richard*

O dime tu nombre para personalizar tu experiencia 😊"""
        


        # ============ 1. ¿QUÉ ES HGW? - RESPUESTA COMPLETA Y DETALLADA ============
        if any(w in t for w in ["qué es hgw", "que es hgw", "qué es", "que es", "empresa", "compañía", "explicame hgw", "sobre hgw", "cuéntame de hgw"]):
            return """🌿 *PREGUNTA 1: ¿QUÉ ES HGW (HEALTH GREEN WORLD)?*

Te lo explico de forma clara y completa:

*LA EMPRESA:*
HGW es una empresa INTERNACIONAL de *venta directa multinivel* con:
• ✅ Más de 30 años en el mercado (fundada en 1993)
• ✅ Presencia en más de 30 países del mundo
• ✅ Miles de distribuidores activos
• ✅ Productos certificados internacionalmente
• ✅ Sistema 100% LEGAL y regulado

*¿QUÉ VENDEMOS?*
Productos de salud, bienestar y cuidado personal 100% NATURALES:
🥗 Suplementos alimenticios (Omega, Espirulina, Arándanos)
☕ Bebidas funcionales (Café con hongos medicinales)
🧼 Productos de higiene personal (Pasta dental, Jabones, Shampoo)
🌸 Productos para el cuidado femenino (Toallas sanitarias con tecnología)
💎 Accesorios de bienestar (Termos, Collares de turmalina)

*¿CÓMO FUNCIONA EL MODELO DE NEGOCIO?*

1. *VENTA DIRECTA:*
• Compras productos con descuento (como distribuidor)
• Los vendes a precio normal
• Te quedas con la ganancia (30% al 52% de margen)

2. *MULTINIVEL (MLM):*
• Invitas a otras personas a ser distribuidores
• Ellos también compran y venden productos
• TÚ ganas comisiones de las ventas de tu equipo
• Hasta 10 niveles de profundidad (Plan de Ganancia Mutua)

*¿ES LEGAL Y SEGURO?*
✅ SÍ. HGW es venta directa LEGAL (no es pirámide)
✅ Hay productos REALES que se venden a clientes reales
✅ No solo ganas por reclutar, sino por ventas de productos
✅ Sistema regulado y transparente

*¿QUÉ LO HACE DIFERENTE?*
• NO necesitas local ni oficina
• NO necesitas experiencia previa
• Trabajas desde tu casa con tu celular 📱
• Horarios 100% flexibles
• Capacitación gratuita incluida
• Mentor personal que te guía (Richard)

*¿PARA QUIÉN ES HGW?*
✅ Personas que buscan ingresos extra sin dejar su trabajo
✅ Emprendedores que quieren su propio negocio
✅ Personas que buscan productos naturales de calidad
✅ Quien quiera libertad de tiempo y dinero

*¿QUÉ RECIBES AL UNIRTE?*
📦 Kit de productos para empezar a vender
📱 Acceso a plataforma digital (backoffice)
📚 Capacitación completa y gratuita
👥 Apoyo de tu mentor personal (Richard)
🎓 Material de ventas (catálogos, videos, imágenes)

*EN RESUMEN:*
HGW te da la oportunidad de ganar dinero vendiendo productos naturales de calidad, mientras construyes un equipo que genera ingresos pasivos para ti.

¿Quieres saber QUÉ TIENES QUE HACER exactamente en el día a día? Escribe "2" o "qué tengo que hacer"

O habla directo con Richard para más detalles:
📞 +57 305 2490438"""

        # ============ 2. ¿QUÉ TENGO QUE HACER? - ULTRA DETALLADO ============
        if any(w in t for w in ["qué tengo que hacer", "que tengo que hacer", "qué hago", "que hago", "actividades", "tareas", "trabajo diario", "responsabilidades"]):
            return """💼 *PREGUNTA 2: ¿QUÉ TENGO QUE HACER EXACTAMENTE EN HGW?*

Te voy a explicar PASO A PASO tus actividades diarias y cómo funciona todo:

*═══════════════════════════════*
*LAS 2 FORMAS DE GANAR DINERO:*
*═══════════════════════════════*

*💰 FORMA 1: VENDER PRODUCTOS (Ganancia Inmediata)*

*¿Cómo funciona?*
1. Compras productos con descuento de distribuidor
2. Los vendes a precio normal (público)
3. Te quedas con la diferencia = TU GANANCIA

*Ejemplo Real:*
• Compras Blueberry Candy en: $20.000 (precio distribuidor)
• Lo vendes en: $28.000 (precio público)
• *Tu ganancia: $8.000 por producto* ✅

Dependiendo de tu nivel:
• Junior/Pre-Junior: Ganas 30% de margen
• Senior: Ganas 30% + bonos adicionales
• Master: Ganas 52% de margen (¡SÚPER RENTABLE!)

*¿A quién le vendes?*
• Familiares y amigos
• Compañeros de trabajo
• Vecinos
• Personas en redes sociales (Facebook, Instagram, WhatsApp)
• Clientes recurrentes (que repiten compra cada mes)

*💰 FORMA 2: CONSTRUIR EQUIPO (Ingresos Residuales)*

*¿Cómo funciona?*
1. Invitas personas a ser distribuidores (con tu enlace de referido)
2. Ellos se registran y compran su membresía
3. Empiezan a vender productos
4. TÚ ganas comisiones de TODAS sus ventas (sin hacer nada)

*Ejemplo Real:*
• Invitas a tu primo Carlos
• Carlos compra plan Senior ($2.160.000)
• *Tú ganas bono de inicio: $216.000* ✅
• Carlos vende $1.000.000 al mes
• *Tú ganas comisión mensual: $100.000* (sin trabajar)

Y así con cada persona que invites. Imagina tener 10, 20 o 50 personas vendiendo para ti 📈

*═══════════════════════════════*
*TU DÍA A DÍA (ACTIVIDADES):*
*═══════════════════════════════*

*🌅 MAÑANA (30-45 minutos):*
• Revisar mensajes de clientes en WhatsApp
• Publicar 2-3 productos en tus estados de WhatsApp
• Publicar 1 post en Facebook/Instagram sobre productos
• Revisar tu backoffice (ver si hay pedidos nuevos)

*🌞 TARDE (30-45 minutos):*
• Hacer seguimiento a clientes interesados
• Procesar pedidos (si tienes ventas)
• Contactar 3-5 personas nuevas para ofrecer productos
• Responder preguntas sobre el negocio

*🌙 NOCHE (30-45 minutos):*
• Hacer llamadas o videollamadas a prospectos
• Capacitar a tu equipo (si ya tienes distribuidores)
• Planificar las publicaciones del día siguiente
• Cerrar ventas pendientes

*TOTAL: 1.5 a 2 horas al día* ⏰

*═══════════════════════════════*
*ACTIVIDADES SEMANALES:*
*═══════════════════════════════*

📅 *LUNES:* Planificación semanal (qué productos promocionar)
📅 *MARTES:* Hacer pedidos de productos (si necesitas restock)
📅 *MIÉRCOLES:* Reunión virtual con tu equipo (capacitación)
📅 *JUEVES:* Contactar nuevos prospectos para tu red
📅 *VIERNES:* Cerrar ventas de la semana
📅 *SÁBADO:* Entregas de productos a clientes locales
📅 *DOMINGO:* Descanso o planificación próxima semana

*═══════════════════════════════*
*¿QUÉ NECESITAS?*
*═══════════════════════════════*

✅ Un celular con WhatsApp
✅ Internet
✅ 1-2 horas al día
✅ Actitud positiva y constancia

*NO necesitas:*
❌ Oficina o local físico
❌ Empleados
❌ Experiencia en ventas
❌ Horario fijo
❌ Invertir en publicidad (opcional)

*═══════════════════════════════*
*HERRAMIENTAS QUE USARÁS:*
*═══════════════════════════════*

📱 *WhatsApp Business:* Para contactar clientes
📱 *App HGW:* Para hacer pedidos y ver tu red
💻 *Backoffice web:* Para gestionar tu negocio
📸 *Redes sociales:* Para promocionar productos
📦 *Material de apoyo:* Catálogos, videos, imágenes (todo gratis)

*═══════════════════════════════*
*EJEMPLO DE RUTINA EXITOSA:*
*═══════════════════════════════*

María (Distribuidora Senior) nos cuenta su rutina:

*Lunes a Viernes:*
• 7:00 AM - Publicar productos en estados de WhatsApp
• 12:00 PM - Responder mensajes (en mi hora de almuerzo)
• 7:00 PM - Hacer 2-3 llamadas a prospectos
• 9:00 PM - Cerrar ventas del día

*Resultado: $1.500.000 al mes* 💰

*═══════════════════════════════*
*LO MÁS IMPORTANTE:*
*═══════════════════════════════*

🔑 *CONSTANCIA:* Trabajar todos los días (aunque sea 1 hora)
🔑 *SEGUIMIENTO:* No dejar clientes sin responder
🔑 *APRENDER:* Ver tutoriales y capacitaciones
🔑 *DUPLICAR:* Enseñar a tu equipo lo que tú haces
🔑 *ACTIVACIÓN:* Mantener compra mensual mínima (10 BV)

*¿Listo para empezar?*
Richard te explica todo en detalle y te acompaña paso a paso:
📞 +57 305 2490438

¿Quieres saber cuánto necesitas INVERTIR? Escribe "3" o "inversión" 💰"""

        # ============ 3. INVERSIÓN INICIAL - SÚPER DETALLADO ============
        if any(w in t for w in ["inversión", "inversion", "cuánto cuesta", "cuanto cuesta", "precio", "cuanto necesito", "cuánto necesito", "planes", "membresia", "membresía", "paquetes"]):
            return """💰 *PREGUNTA 3: ¿CUÁNTO ES LA INVERSIÓN INICIAL?*

Te voy a explicar TODOS los planes disponibles con TODOS los detalles:

*═══════════════════════════════*
*🎯 PLAN 1: PRE-JUNIOR*
*═══════════════════════════════*

💵 *Inversión: $360.000 COP*
📊 Puntos de Volumen: 50 BV
📦 Kit de productos valorado en: $468.000 (precio venta)

*¿Qué recibes?*
• Productos para empezar a vender
• Acceso al backoffice
• Capacitación básica
• Tu enlace de referido

*Ganancias:*
• 30% de margen en ventas directas
• Comisiones limitadas de red

*¿Para quién es?*
✅ Personas con presupuesto MUY limitado
✅ Quienes quieren "probar" el negocio
✅ Estudiantes o jóvenes

*Tiempo de recuperación: 3-4 semanas*
(Si vendes todos los productos del kit)

*═══════════════════════════════*
*🎯 PLAN 2: JUNIOR* 
*═══════════════════════════════*

💵 *Inversión: $720.000 COP*
📊 Puntos de Volumen: 100 BV
📦 Kit de productos valorado en: $936.000 (precio venta)

*¿Qué recibes?*
• Más productos que en Pre-Junior
• Acceso completo al backoffice
• Capacitación completa
• Material de apoyo
• Tu enlace de referido

*Ganancias:*
• 30% de margen en ventas directas
• Comisiones básicas de red (3 niveles)
• Bono de inicio rápido

*¿Para quién es?*
✅ Personas que quieren empezar con inversión moderada
✅ Quienes buscan ingresos extra sin mucho riesgo

*Tiempo de recuperación: 1-2 meses*

*Ejemplo real:*
Vendes todo el kit en 1 mes:
• Inversión: $720.000
• Venta total: $936.000
• *Ganancia: $216.000*
• *Recuperas: $720.000* ✅

*═══════════════════════════════*
*🎯 PLAN 3: SENIOR* ⭐ (MÁS POPULAR)
*═══════════════════════════════*

💵 *Inversión: $2.160.000 COP*
📊 Puntos de Volumen: 300 BV
📦 Kit de productos valorado en: $2.808.000 (precio venta)

*¿Qué recibes?*
• Kit COMPLETO de productos variados
• Acceso premium al backoffice
• Capacitación avanzada
• Todo el material de apoyo
• Soporte prioritario

*Ganancias:*
• 30% de margen en ventas directas
• TODAS las comisiones de red (10 niveles)
• Bono de inicio rápido
• Bono de liderazgo
• Bono de equipo

*¿Para quién es?*
✅ Personas que quieren tomarlo EN SERIO
✅ Quienes buscan reemplazar su ingreso actual
✅ Emprendedores comprometidos

*Tiempo de recuperación: 2-3 meses*

*Ejemplo real:*
Carlos invirtió $2.160.000 en Senior:

*Mes 1:* Vendió $1.200.000 en productos
Ganancia: $360.000

*Mes 2:* Vendió $1.000.000 + Invitó 3 personas
Ganancia: $300.000 (ventas) + $150.000 (bonos) = $450.000

*Mes 3:* Vendió $608.000 + Su equipo vendió $2.000.000
Ganancia: $182.400 (ventas) + $400.000 (comisiones) = $582.400

*Total 3 meses: $1.392.400*
*RECUPERÓ: $2.160.000 al mes 3.5* ✅

*═══════════════════════════════*
*🎯 PLAN 4: MASTER* 🏆
*═══════════════════════════════*

💵 *Inversión: $4.320.000 COP*
📊 Puntos de Volumen: 600 BV
📦 Kit de productos valorado en: $6.566.400 (precio venta)

*¿Qué recibes?*
• Kit PREMIUM con TODOS los productos
• Acceso VIP al backoffice
• Capacitación personalizada 1 a 1
• Mentor exclusivo
• Soporte prioritario 24/7

*Ganancias:*
• *52% de margen en ventas directas* (¡EL MÁS ALTO!)
• TODAS las comisiones de red (10 niveles)
• Todos los bonos disponibles
• Calificación rápida a rangos superiores

*¿Para quién es?*
✅ Personas con capital disponible
✅ Quienes quieren MÁXIMA ganancia desde el inicio
✅ Líderes que quieren construir rápido

*Tiempo de recuperación: 4-6 meses*

*Ejemplo real:*
Ana invirtió $4.320.000 en Master:

*Mes 1-2:* Vendió $3.000.000 en productos
Ganancia: $1.560.000 (52%)

*Mes 3-4:* Construyó equipo de 10 personas
Comisiones: $1.200.000

*Mes 5-6:* Su equipo creció a 25 personas
Comisiones: $2.500.000

*Total 6 meses: $5.260.000*
*RECUPERÓ inversión + Ganó $940.000 extra* 🎉

*═══════════════════════════════*
*📊 COMPARACIÓN RÁPIDA:*
*═══════════════════════════════*

| Plan | Inversión | Margen | Recuperación |
|------|-----------|--------|--------------|
| Pre-Junior | $360K | 30% | 3-4 semanas |
| Junior | $720K | 30% | 1-2 meses |
| Senior ⭐ | $2.16M | 30%+ | 2-3 meses |
| Master 🏆 | $4.32M | 52% | 4-6 meses |

*═══════════════════════════════*
*¿CUÁL PLAN ELEGIR?*
*═══════════════════════════════*

💡 *Si tienes poco presupuesto:* Pre-Junior o Junior
💡 *Si quieres mejores resultados:* Senior (el más popular)
💡 *Si tienes capital y quieres lo mejor:* Master

*Recomendación de Richard:*
El 70% de distribuidores exitosos empezaron con *SENIOR* porque es el mejor balance entre inversión y ganancias.

*═══════════════════════════════*
*FORMAS DE PAGO:*
*═══════════════════════════════*

💳 Nequi
💳 Botón Bancolombia
💳 Efecty (efectivo)
💳 Tarjeta de crédito

*También puedes:*
• Pagar en cuotas (con tarjeta)
• Hacer "vaca" con un socio
• Pedir prestado y recuperar rápido

*═══════════════════════════════*

*IMPORTANTE:*
No es "gastar" dinero, es *INVERTIR* en inventario. Los productos están ahí, solo tienes que venderlos y recuperas TODO + ganancias.

¿Quieres saber CUÁNDO RECUPERAS tu inversión exactamente? Escribe "4" o "recuperar inversión"

O habla con Richard para elegir el mejor plan para ti:
📞 +57 305 2490438"""

        # ============ 4. RECUPERACIÓN DE INVERSIÓN - MATEMÁTICAS DETALLADAS ============
        if any(w in t for w in ["recuperar", "recupero", "cuándo recupero", "cuando recupero", "devolver", "regresa", "tiempo de recuperación"]):
            return """⏰ *PREGUNTA 4: ¿CUÁNDO RECUPERO MI INVERSIÓN?*

Te voy a explicar EXACTAMENTE cómo y cuándo recuperas cada peso invertido:

*═══════════════════════════════*
*💡 CONCEPTO CLAVE:*
*═══════════════════════════════*

Tu inversión NO se "pierde". Se convierte en PRODUCTOS que vendes con GANANCIA.

Es como si compraras $2.160.000 en mercancía y la vendieras en $2.808.000. ¿Perdiste dinero? NO. Ganaste $648.000 + Recuperaste los $2.160.000.

*═══════════════════════════════*
*📊 PLAN PRE-JUNIOR ($360.000)*
*═══════════════════════════════*

*Inviertes: $360.000*
*Recibes productos valorados en: $468.000*

*¿Cómo recuperar?*

*OPCIÓN 1: Vender todo el kit*
• Vendes productos por $468.000
• Ganancia: $108.000 (30%)
• Recuperas: $360.000 ✅
• *Tiempo: 3-4 semanas*

*OPCIÓN 2: Vender + Invitar*
• Vendes $300.000 en productos
• Invitas 1 persona (bono $36.000)
• Ganancia: $90.000 + $36.000 = $126.000
• Recuperas: $360.000 al mes 2 ✅

*═══════════════════════════════*
*📊 PLAN JUNIOR ($720.000)*
*═══════════════════════════════*

*Inviertes: $720.000*
*Recibes productos valorados en: $936.000*

*Estrategia de recuperación MÁS RÁPIDA:*

*SEMANA 1-2:*
• Vendes a familiares/amigos: $400.000
• Ganancia: $120.000

*SEMANA 3-4:*
• Vendes en redes sociales: $300.000
• Ganancia: $90.000

*SEMANA 5-6:*
• Vendes el resto: $236.000
• Ganancia: $70.800

*TOTAL: $280.800 de ganancia*
*RECUPERASTE: $720.000 en 1.5 meses* ✅

*Caso real - Laura (Junior):*
"Empecé en Junior con $720.000. En 3 semanas vendí todo a mis compañeros de trabajo y vecinos. Gané $216.000 y recuperé mi inversión. Ahora estoy en mi segundo kit y ya tengo 5 clientes fijos." - Laura, Cali

*═══════════════════════════════*
*📊 PLAN SENIOR ($2.160.000)* ⭐
*═══════════════════════════════*

*Inviertes: $2.160.000*
*Recibes productos valorados en: $2.808.000*

*ESTRATEGIA INTELIGENTE (2-3 meses):*

*MES 1:*
📍 Vendes 40% del kit: $1.123.200
💰 Ganancia: $336.960
📍 Invitas 2 personas (bonos): $216.000
*Total mes 1: $552.960*

*MES 2:*
📍 Vendes otro 40%: $1.123.200
💰 Ganancia: $336.960
📍 Tu equipo vende (comisiones): $200.000
*Total mes 2: $536.960*

*MES 3:*
📍 Vendes el resto: $561.600
💰 Ganancia: $168.480
📍 Comisiones de red: $300.000
*Total mes 3: $468.480*

*SUMA TOTAL: $1.558.400*
*Aún faltan $601.600 para recuperar*

📍 *Mes 4:* Con ventas nuevas y comisiones
*RECUPERAS COMPLETO: $2.160.000* ✅

*Caso real - Carlos (Senior):*
"Invertí $2.160.000 en Senior. Los primeros 2 meses vendí casi todo el kit. Al mes 3 ya tenía un equipo de 8 personas. Recuperé mi inversión completa al mes 3.5 y desde el mes 4 TODO es ganancia pura." - Carlos, Bogotá

*═══════════════════════════════*
*📊 PLAN MASTER ($4.320.000)* 🏆
*═══════════════════════════════*

*Inviertes: $4.320.000*
*Recibes productos valorados en: $6.566.400*
*GANANCIA POTENCIAL: $2.246.400 (52%)*

*ESTRATEGIA PROFESIONAL (4-6 meses):*

*MES 1-2:*
📍 Vendes 35% del kit: $2.298.240
💰 Ganancia (52%): $1.195.085
📍 Invitas 5 personas: $1.080.000 (bonos)
*Total 2 meses: $2.275.085*

¡Ya recuperaste más de la mitad!

*MES 3-4:*
📍 Vendes otro 35%: $2.298.240
💰 Ganancia: $1.195.085
📍 Comisiones de equipo: $800.000
*Total meses 3-4: $1.995.085*

*SUMA: $4.270.170*
*RECUPERASTE: $4.320.000 al mes 4* ✅

*MES 5-6:*
📍 Vendes el resto + nuevos pedidos
📍 Comisiones de red creciente
*TODO ES GANANCIA PURA: $1.500.000 - $3.000.000/mes* 🎉

*Caso real - Ana (Master):*
"Hice la inversión más grande de mi vida: $4.320.000 en Master. Los primeros meses vendí como loca y construí mi equipo rápido. Al mes 5 ya había recuperado TODO. Hoy, 8 meses después, gano entre $2.5M y $4M al mes. Fue la mejor decisión." - Ana, Medellín

*═══════════════════════════════*
*⚡ FACTORES QUE ACELERAN LA RECUPERACIÓN:*
*═══════════════════════════════*

✅ *Dedicar 2-3 horas diarias*
Más tiempo = Más ventas = Recuperación rápida

✅ *Construir equipo desde el MES 1*
Bonos de inicio te ayudan a recuperar MÁS RÁPIDO

✅ *Vender productos de alto margen primero*
Enfócate en productos con mejor ganancia

✅ *Mantener activación mensual (10 BV)*
Habilita TODAS tus comisiones

✅ *Aplicar estrategias de venta*
Publicar en redes, hacer seguimiento, cerrar ventas

*═══════════════════════════════*
*📈 TABLA RESUMEN DE RECUPERACIÓN:*
*═══════════════════════════════*

| Plan | Inversión | Tiempo Promedio |
|------|-----------|-----------------|
| Pre-Junior | $360K | 3-4 semanas |
| Junior | $720K | 1-2 meses |
| Senior | $2.16M | 2-3 meses |
| Master | $4.32M | 4-6 meses |

*═══════════════════════════════*
*💡 LO MÁS IMPORTANTE:*
*═══════════════════════════════*

🔑 Recuperar inversión NO significa "dejar de ganar"
🔑 Después de recuperar, TODO lo que vendas es GANANCIA PURA
🔑 Las comisiones de red son INGRESOS ADICIONALES (no cuentan los productos)
🔑 Entre más rápido vendas, más rápido recuperas

*¿Quieres saber CUÁNDO EMPIEZAS A GANAR dinero?*
Escribe "5" o "cuándo gano"

O habla con Richard para ver tu plan personalizado:
📞 +57 305 2490438"""

        # ============ 5. CUÁNDO EMPIEZO A GANAR - CRONOGRAMA COMPLETO ============
        if any(w in t for w in ["cuándo gano", "cuando gano", "cuándo empiezo a ganar", "cuando empiezo a ganar", "ganancias", "ganar dinero", "utilidad", "cuanto gano", "cuánto gano", "ingresos"]):
            return """💵 *PREGUNTA 5: ¿CUÁNDO EMPIEZO A GANAR DINERO?*

La respuesta es simple: *DESDE TU PRIMERA VENTA* 🎯

Pero déjame explicarte TODO el sistema de ganancias:

*═══════════════════════════════*
*💰 LAS 5 FORMAS DE GANAR EN HGW:*
*═══════════════════════════════*

*1. GANANCIA POR VENTA DIRECTA* (Inmediata)
*2. BONO DE INICIO RÁPIDO* (Semana 1-4)
*3. COMISIONES DE RED* (Mes 2 en adelante)
*4. BONOS DE LIDERAZGO* (Mes 3 en adelante)
*5. INGRESOS RESIDUALES* (Mes 6 en adelante)

*═══════════════════════════════*
*💰 FORMA 1: GANANCIA POR VENTA DIRECTA*
*═══════════════════════════════*

*¿Cuándo empiezas a ganar?*
*DESDE TU PRIMERA VENTA* (puede ser el mismo día que te registras)

*Ejemplo Día 1:*
• Te registras en la mañana
• Recibes tu kit en 5-7 días
• Mientras esperas, ya puedes vender (desde el backoffice)
• Vendes Blueberry Candy a tu vecina
• Precio distribuidor: $20.000
• Precio venta: $28.000
• *TU GANANCIA: $8.000* ✅

*Ejemplo Semana 1:*
• Lunes: Vendes $150.000 → Ganas $45.000
• Miércoles: Vendes $200.000 → Ganas $60.000
• Viernes: Vendes $180.000 → Ganas $54.000
• *TOTAL SEMANA: $159.000* 🎉

*Ganancias según tu nivel:*
• Junior/Pre-Junior: 30% de margen
• Senior: 30% + bonos adicionales
• Master: 52% de margen (¡DOBLE!)

*═══════════════════════════════*
*💰 FORMA 2: BONO DE INICIO RÁPIDO*
*═══════════════════════════════*

*¿Cuándo lo recibes?*
Cuando invitas a alguien y se registra (puede ser semana 1)

*¿Cuánto ganas?*
10% al 20% de la inversión de la persona que invitaste

*Ejemplos:*
• Invitas a tu primo, compra Junior ($720.000)
• *Tú ganas: $72.000 - $144.000* ✅

• Invitas a tu amiga, compra Senior ($2.160.000)
• *Tú ganas: $216.000 - $432.000* 💰

*Caso real - Semana 2:*
Pedro invitó a 3 amigos en su segunda semana:
• Amigo 1: Junior → Bono $72.000
• Amigo 2: Junior → Bono $72.000
• Amigo 3: Senior → Bono $216.000
*TOTAL: $360.000 en bonos* 🎉

*═══════════════════════════════*
*💰 FORMA 3: COMISIONES DE RED*
*═══════════════════════════════*

*¿Cuándo empiezas a ganar?*
Cuando tu equipo empieza a vender (generalmente mes 2-3)

*¿Cómo funciona?*
Ganas un % de TODAS las ventas de tu red (hasta 10 niveles de profundidad)

*Ejemplo Mes 2:*
Tienes 5 personas en tu equipo:
• Cada uno vende $500.000 al mes
• Total ventas de red: $2.500.000
• *Tú ganas comisión: $250.000 - $375.000* (10%-15%)

*Ejemplo Mes 6:*
Tu equipo creció a 20 personas:
• Ventas totales: $10.000.000
• *Tú ganas: $1.000.000 - $1.500.000* 💰

¡Y tú NO vendiste nada ese mes! Son INGRESOS PASIVOS.

*═══════════════════════════════*
*💰 FORMA 4: BONOS DE LIDERAZGO*
*═══════════════════════════════*

*¿Cuándo los recibes?*
Cuando alcanzas ciertos rangos (generalmente mes 3-6)

*Tipos de bonos:*
• Bono de Equipo (cuando tu equipo es activo)
• Bono de Generación (por niveles profundos)
• Bono de Crecimiento (por expansión rápida)
• Bonos especiales (autos, viajes, premios)

*Ejemplo:*
Al alcanzar rango "Silver":
• Bono mensual adicional: $300.000 - $500.000

*═══════════════════════════════*
*💰 FORMA 5: INGRESOS RESIDUALES*
*═══════════════════════════════*

*¿Qué son?*
Dinero que ganas SIN trabajar (tu equipo trabaja por ti)

*¿Cuándo empiezas?*
Cuando tu red es sólida (mes 6 en adelante)

*Ejemplo real - Mes 12:*
María tiene 50 personas activas en su red:
• Ella ya NO vende productos (solo lidera)
• Su equipo genera $15.000.000 al mes
• *María gana: $2.000.000 - $3.000.000/mes* 💰
• *Sin vender un solo producto*

*═══════════════════════════════*
*📊 CRONOGRAMA REAL DE GANANCIAS:*
*═══════════════════════════════*

*SEMANA 1:*
• Ventas directas: $100.000 - $300.000
• *GANANCIA: $30.000 - $90.000*

*SEMANA 2-4:*
• Ventas directas: $400.000 - $800.000
• Bonos de inicio: $72.000 - $216.000
• *GANANCIA: $192.000 - $456.000*

*MES 2:*
• Ventas directas: $600.000
• Comisiones iniciales: $150.000
• *GANANCIA: $330.000*

*MES 3:*
• Ventas directas: $800.000
• Comisiones de red: $300.000
• Bonos: $100.000
• *GANANCIA: $540.000*

*MES 4-6:*
• Ventas directas: $1.000.000
• Comisiones de red: $500.000 - $800.000
• Bonos de liderazgo: $200.000
• *GANANCIA: $1.200.000 - $1.800.000*

*MES 7-12:*
• Ventas directas: $800.000 (menos porque delegas)
• Comisiones de red: $1.500.000 - $3.000.000
• Bonos de liderazgo: $500.000
• *GANANCIA: $2.300.000 - $4.000.000*

*AÑO 2:*
• Ingresos pasivos principalmente
• *GANANCIA PROMEDIO: $3.000.000 - $6.000.000/mes*

*═══════════════════════════════*
*💡 CASOS REALES DE DISTRIBUIDORES:*
*═══════════════════════════════*

*📍 Laura - Junior ($720.000):*
• Mes 1: Ganó $216.000 (ventas)
• Mes 2: Ganó $350.000 (ventas + 2 bonos)
• Mes 3: Ganó $480.000 (ventas + comisiones)
• *Hoy (mes 8): Gana $1.200.000/mes*

*📍 Carlos - Senior ($2.160.000):*
• Mes 1-2: Ganó $700.000
• Mes 3: Ganó $850.000
• Mes 4-6: Ganó $1.500.000/mes promedio
• *Hoy (mes 14): Gana $3.500.000/mes*

*📍 Ana - Master ($4.320.000):*
• Mes 1-2: Ganó $2.000.000 (52% margen)
• Mes 3-4: Ganó $2.500.000/mes
• Mes 5-6: Ganó $3.200.000/mes
• *Hoy (año 2): Gana $5.000.000 - $7.000.000/mes*

*═══════════════════════════════*
*⚡ FACTORES QUE AUMENTAN GANANCIAS:*
*═══════════════════════════════*

✅ *Dedicación diaria (2-3 horas)*
Más tiempo = Más ventas = Más dinero

✅ *Construir equipo rápido*
Más personas = Más comisiones

✅ *Mantener activación mensual*
Habilita TODAS las comisiones

✅ *Alcanzar rangos superiores*
Más bonos y porcentajes más altos

✅ *Duplicar el sistema*
Enseñar a tu equipo a hacer lo mismo

✅ *Vender productos de alta rotación*
Clientes recurrentes = Ingresos constantes

*═══════════════════════════════*
*🎯 RESPUESTA DIRECTA:*
*═══════════════════════════════*

*¿CUÁNDO EMPIEZAS A GANAR?*
👉 *HOY MISMO* si vendes algo hoy
👉 *ESTA SEMANA* con tus primeras ventas
👉 *ESTE MES* con ventas + bonos
👉 *PRÓXIMOS MESES* con tu red trabajando para ti

*NO tienes que esperar 6 meses o 1 año.*
Desde tu PRIMERA VENTA ya estás ganando dinero.

*Lo mejor:*
• Mes 1-3: Recuperas inversión
• Mes 4+: TODO es ganancia pura
• Mes 6+: Ingresos pasivos comienzan
• Año 2: Libertad financiera posible

*═══════════════════════════════*

*¿LISTO PARA EMPEZAR A GANAR HOY?*

Richard te muestra el camino exacto para tu situación:
📞 WhatsApp: +57 305 2490438

Dile: "Hola Richard, quiero empezar en HGW y ganar dinero"

¿Tienes más dudas? Escribe:
• "resumen" (ver las 5 preguntas juntas)
• "productos" (ver catálogo)
• "inscribir" (cómo registrarse)
• "richard" (contactar mentor)

¡Tu futuro financiero comienza AHORA! 🚀"""

        # ============ RESUMEN DE LAS 5 PREGUNTAS ============
        if any(w in t for w in ["resumen", "todo", "5 puntos", "5 preguntas", "explicame todo", "todo junto"]):
            return """📊 *RESUMEN COMPLETO - LAS 5 PREGUNTAS CLAVE DE HGW*

*═══════════════════════════════*
*1️⃣ ¿QUÉ ES HGW?*
*═══════════════════════════════*

Empresa internacional de venta directa multinivel con:
• 30+ años de experiencia (desde 1993)
• Presente en 30+ países
• Productos naturales 100% certificados
• Sistema legal y transparente

*Lo que haces:*
Vendes productos naturales + Construyes equipo = Ganas dinero

*═══════════════════════════════*
*2️⃣ ¿QUÉ TENGO QUE HACER?*
*═══════════════════════════════*

*Dos actividades principales:*

*A) VENDER PRODUCTOS:*
• Compras con descuento (30%-52%)
• Vendes a precio normal
• Te quedas con la ganancia
• 1-2 horas al día desde tu celular

*B) CONSTRUIR EQUIPO:*
• Invitas personas a ser distribuidores
• Ellos compran y venden
• Tú ganas comisiones (hasta 10 niveles)
• Ingresos pasivos/residuales

*Herramientas:*
WhatsApp, App HGW, Redes sociales, Backoffice web

*═══════════════════════════════*
*3️⃣ ¿CUÁNTO ES LA INVERSIÓN?*
*═══════════════════════════════*

*4 planes disponibles:*

📦 *Pre-Junior:* $360.000 (50 BV)
📦 *Junior:* $720.000 (100 BV)
📦 *Senior:* $2.160.000 (300 BV) ⭐ MÁS POPULAR
📦 *Master:* $4.320.000 (600 BV) 🏆 MÁXIMA GANANCIA

*¿Qué incluye?*
• Kit de productos para vender
• Acceso al backoffice
• Capacitación completa
• Mentor personal (Richard)

*Formas de pago:*
Nequi, Bancolombia, Efecty, Tarjeta

*═══════════════════════════════*
*4️⃣ ¿CUÁNDO RECUPERO INVERSIÓN?*
*═══════════════════════════════*

*Tiempos promedio:*

• Pre-Junior ($360K): 3-4 semanas
• Junior ($720K): 1-2 meses
• Senior ($2.16M): 2-3 meses
• Master ($4.32M): 4-6 meses

*¿Cómo?*
Vendiendo los productos de tu kit + Invitando personas (bonos)

*Importante:*
No "pierdes" dinero. Se convierte en productos que vendes con GANANCIA.

*═══════════════════════════════*
*5️⃣ ¿CUÁNDO EMPIEZO A GANAR?*
*═══════════════════════════════*

*DESDE TU PRIMERA VENTA* (puede ser día 1)

*Cronograma real:*

*Semana 1:* $30.000 - $90.000 (ventas directas)
*Mes 1:* $200.000 - $600.000 (ventas + bonos)
*Mes 2-3:* $500.000 - $1.000.000 (ventas + comisiones)
*Mes 4-6:* $1.000.000 - $2.000.000 (red creciente)
*Mes 7+:* $2.000.000 - $5.000.000+ (ingresos pasivos)

*5 formas de ganar:*
1. Venta directa (inmediata)
2. Bonos de inicio (semana 1-4)
3. Comisiones de red (mes 2+)
4. Bonos de liderazgo (mes 3+)
5. Ingresos residuales (mes 6+)

*═══════════════════════════════*
*🎯 EN RESUMEN:*
*═══════════════════════════════*

HGW es una oportunidad REAL de:
✅ Generar ingresos desde casa
✅ Trabajar con horarios flexibles
✅ Construir un negocio propio
✅ Crear ingresos residuales
✅ Alcanzar libertad financiera

*NO necesitas:*
❌ Experiencia previa
❌ Local u oficina
❌ Horario fijo
❌ Empleados

*SÍ necesitas:*
✅ Celular con internet
✅ 1-2 horas al día
✅ Constancia y compromiso
✅ Ganas de aprender

*═══════════════════════════════*
*🚀 SIGUIENTE PASO:*
*═══════════════════════════════*

Habla con Richard Córdoba para:
✅ Resolver todas tus dudas
✅ Ver el plan ideal para ti
✅ Conocer casos de éxito reales
✅ Empezar HOY mismo

📞 *WhatsApp: +57 305 2490438*

Mensaje sugerido:
"Hola Richard, vi el resumen de HGW y quiero más información para empezar"

*¿Qué más necesitas saber?*
Escribe: "productos", "inscribir", "tutoriales" o tu pregunta específica.

¡El momento es AHORA! 🌟"""

        # Unirse / Inscribirse con nombre
        if any(w in t for w in ["unirme", "unir", "inscribirme", "registrarme", "ser parte", "entrar", "quiero empezar", "empezar"]):
            nombre = f"{user_name}" if user_name else "amigo/a"
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

        # Productos - Catálogo general
        if any(w in t for w in ["producto", "qué venden", "qué tienen", "catalogo", "catálogo"]) and not any(x in t for x in ["blueberry", "cafe", "omega", "espirulina", "pasta", "jabon", "shampoo", "toalla", "collar", "termo"]):
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

        # Productos específicos - Alimentos
        if any(w in t for w in ["blueberry", "arandano", "arándano"]) and not any(x in t for x in ["fresh", "regaliz"]):
            return """🍬 *Productos de Arándano HGW*

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

¿Quieres ordenar? Habla con Richard:
📞 +57 305 2490438"""

        if any(w in t for w in ["fresh candy", "regaliz", "caramelo regaliz"]):
            return """🍬 *Fresh Candy sabor Regaliz HGW*

*Caramelos con extracto de regaliz*
🌿 Dulce natural con propiedades medicinales

✅ Alivia irritaciones de garganta
✅ Mejora la digestión
✅ Reduce el mal aliento
✅ Propiedades antiinflamatorias
✅ Sabor natural agradable

Ideal para llevar en tu bolso y cuidar tu salud en cualquier momento.

Pedidos con Richard:
📞 +57 305 2490438"""

        if any(w in t for w in ["cafe", "café", "ganoderma", "cordyceps", "coffee"]):
            return """☕ *Cafés Funcionales HGW*

*Café con Ganoderma (Ganoderma Soluble Coffee)*
🍄 Café enriquecido con hongo medicinal
✅ Refuerza el sistema inmunológico
✅ Mejora la energía natural
✅ Reduce el estrés
✅ Protege el hígado

*Cordyceps Coffee*
⚡ Café con hongo Cordyceps
✅ Aumenta vitalidad y resistencia
✅ Mejora resistencia física y respiratoria
✅ Ideal para deportistas
✅ Combate la fatiga crónica

Precio y pedidos con Richard:
📞 +57 305 2490438"""

        if any(w in t for w in ["omega", "espirulina", "suplemento"]):
            return """💊 *Suplementos HGW*

*Omega 3-6-9*
🐟 Ácidos grasos esenciales
✅ Salud cardiovascular
✅ Mejora cerebral y memoria
✅ Salud articular
✅ Regula colesterol
✅ Mejora estado de ánimo

*Espirulina*
🌿 Superalimento completo
✅ Alto en proteínas, hierro y clorofila
✅ Fortalece sistema inmune
✅ Combate la anemia
✅ Control de peso saludable
✅ Desintoxica el organismo

¿Cuál necesitas? Habla con Richard:
📞 +57 305 2490438"""

        # Productos de higiene
        if any(w in t for w in ["pasta dental", "dientes", "toothpaste"]):
            return """🦷 *Pasta Dental Herbal HGW*

*Herb Toothpaste*
🌿 100% herbal con menta, clavo y extractos naturales

✅ Elimina bacterias bucales
✅ Blanquea los dientes naturalmente
✅ Previene encías sangrantes
✅ Elimina mal aliento
✅ Protección anticaries

Sin químicos agresivos, toda la familia puede usarla.

¿Quieres probarla? Contacta a Richard:
📞 +57 305 2490438"""

        if any(w in t for w in ["jabon", "jabón", "turmalina", "oliva"]):
            return """🧼 *Jabones Naturales HGW*

*Jabón de Turmalina*
💎 Con piedra turmalina natural
✅ Libera iones negativos
✅ Mejora la circulación
✅ Elimina toxinas de la piel
✅ Ideal para piel grasa o acné

*Jabón de Oliva*
🫒 Con aceite de oliva puro
✅ Hidratante natural
✅ Limpia suavemente
✅ Nutre piel seca o sensible
✅ Uso diario para toda la familia

Pedidos con Richard:
📞 +57 305 2490438"""

        if any(w in t for w in ["shampoo", "champú", "keratina", "cabello"]):
            return """💇 *Shampoo Keratina HGW*

*Smilife Keratin Shampoo*
✨ Regenerador con queratina natural

✅ Restaura cabello dañado
✅ Da brillo intenso
✅ Fortalece el cuero cabelludo
✅ Repara puntas abiertas
✅ Suave y natural

Ideal para cabello maltratado, teñido o con tratamientos químicos.

¿Quieres revitalizar tu cabello? Habla con Richard:
📞 +57 305 2490438"""

        # Productos femeninos
        if any(w in t for w in ["toalla sanitaria", "toallas", "femenino", "menstruacion", "menstruación"]):
            return """🌸 *Toallas Sanitarias Smilife HGW*

*Toallas día y noche*
💎 Con turmalina y aniones

✅ Previenen infecciones
✅ Neutralizan olores
✅ Alivian cólicos menstruales
✅ Mejoran la circulación
✅ Mantienen pH balanceado
✅ Ultra absorbentes

Tecnología que cuida tu salud íntima naturalmente.

Pedidos con Richard:
📞 +57 305 2490438"""

        # Productos de bienestar
        if any(w in t for w in ["termo", "collar", "pulsera", "turmalina", "accesorio"]):
            return """💎 *Accesorios de Bienestar HGW*

*Termo con Turmalina Waterson*
🌊 Estructura el agua con iones negativos
✅ Mejora la hidratación
✅ Elimina toxinas
✅ Equilibra energía corporal

*Collar y Pulsera de Turmalinas*
💍 Emiten iones negativos y radiación infrarroja
✅ Favorecen la circulación
✅ Alivian el estrés
✅ Equilibran la energía del cuerpo
✅ Uso diario para bienestar

¿Quieres probarlos? Habla con Richard:
📞 +57 305 2490438"""

        # Sin tiempo
        if any(w in t for w in ["tiempo", "ocupado", "no tengo tiempo", "trabajo mucho"]):
            return """¡Te entiendo perfectamente! ⏰

La buena noticia: solo necesitas 1-2 horas al día para empezar.

Trabajas desde tu celular en tus ratos libres. Muchos de nuestros distribuidores exitosos empezaron igual de ocupados.

Lo mejor: cuando construyes tu equipo, ellos generan ingresos para ti aunque no estés trabajando. Eso es libertad de tiempo.

¿Te gustaría ver cómo encaja con tu rutina?
📞 Habla con Richard: +57 305 2490438"""

        # Bienestar/Salud
        if any(w in t for w in ["salud", "bienestar", "energía", "cansado", "energia", "vitaminas", "natural"]):
            return """¡Excelente! 🌿

Nuestros productos naturales te van a sorprender:

• Más energía durante el día ⚡
• Mejor descanso 😴
• Sistema inmune más fuerte 🛡️
• Peso saludable ⚖️

Todo 100% natural, certificado internacionalmente.

Y si te gustan los resultados, puedes volverte distribuidor y ganar dinero compartiendo lo que funciona.

¿Quieres saber cuál es el mejor para ti?
📞 Richard te asesora: +57 305 2490438"""

        # Contacto con Richard
        if any(w in t for w in ["richard", "llamar", "contacto", "hablar", "agendar", "numero", "número", "telefono", "teléfono"]):
            return """¡Perfecto! 📞

Richard es el líder de *Empoderando Líderes* y mentor personal de distribuidores HGW.

Él puede:
✅ Resolver todas tus dudas
✅ Mostrarte cómo iniciar
✅ Ofrecerte planes según tu presupuesto
✅ Darte capacitación gratis

*Escríbele por WhatsApp:*
📱 +57 305 2490438

Puedes decirle: "Hola Richard, vengo del bot y me interesa conocer más sobre [lo que te interese]"

¡Él está esperando tu mensaje! 😊"""

        # Testimonios
        if any(w in t for w in ["testimonio", "experiencia", "funciona", "resultados", "casos de exito"]):
            return """¡Claro! ⭐

Miles de personas han cambiado su vida con HGW:

"Empecé hace 2 años trabajando 2 horas al día. Hoy gano más que en mi trabajo de oficina" - María, Bogotá 💰

"Los productos me devolvieron la energía. Me siento 10 años más joven" - Carlos, Medellín 🌿

"Comencé sin saber nada. Hoy lidero un equipo de 50 personas" - Ana, Cali 📈

¿Quieres crear tu propia historia de éxito?

Richard puede conectarte con más distribuidores:
📞 +57 305 2490438"""

        # Dudas / No sé
        if any(w in t for w in ["no sé", "no se", "duda", "pregunta", "no entiendo"]):
            return """¡Tranquilo! 🤔

Es normal tener dudas al principio.

*Preguntas comunes:*

¿Es pirámide? → No, es mercadeo en red LEGAL con productos reales.
¿Necesito experiencia? → No, te capacitan desde cero.
¿Cuánto puedo ganar? → Depende de tu esfuerzo. Desde $500 mil hasta $5 millones+ al mes.

La mejor forma de resolver TODAS tus dudas es hablar con Richard. Sin compromiso, solo info clara.

📞 WhatsApp: +57 305 2490438"""

        # Cómo inscribirse - PASO A PASO DETALLADO
        if any(w in t for w in ["inscribir", "registrar", "como me inscribo", "cómo me registro", "como inicio"]):
            return """🚀 *PASO A PASO: Cómo Inscribirse en HGW*

*PASO 1: VER EL TUTORIAL* 📹
Primero mira este video que te explica TODO el proceso:
👉 https://youtu.be/HCyEHyREYfg

*PASO 2: ENTRAR AL SITIO WEB*
1️⃣ Solicita el enlace de referido a Richard (+57 305 2490438)
2️⃣ Haz click en el enlace
3️⃣ Te llevará a la página de registro

*PASO 3: LLENAR EL FORMULARIO*
📝 Completa tus datos:
- Nombre completo
- Documento de identidad
- Correo electrónico
- Teléfono
- Dirección

*PASO 4: ELEGIR TU PLAN*
💰 Selecciona el plan que más te convenga
(Richard te habrá explicado las opciones antes)

*PASO 5: REALIZAR EL PAGO*
💳 Puedes pagar con:
- Nequi
- Botón Bancolombia
- Efecty
- Tarjeta de crédito

*PASO 6: CONFIRMAR TU REGISTRO*
✅ Recibirás un correo de confirmación
✅ Podrás ingresar al backoffice

*¿NECESITAS AYUDA EN EL PROCESO?*
Si tienes alguna dificultad, escribe "no puedo" y te ayudo con lo que necesites.

O contacta directamente a Richard:
📞 +57 305 2490438"""

        # Cuando dice "no puedo" o tiene dificultades
        if any(w in t for w in ["no puedo", "no se como", "no sé cómo", "ayuda", "dificultad", "problema", "error"]):
            return """🆘 *¡Estoy Aquí Para Ayudarte!*

Entiendo que el proceso puede tener dudas. Cuéntame específicamente:

*¿Qué necesitas?*

📹 *TUTORIALES DISPONIBLES:*
1️⃣ Cómo inscribirse
2️⃣ Cómo ingresar al backoffice
3️⃣ Cómo comprar la membresía
4️⃣ Cómo hacer un pedido
5️⃣ Cómo cobrar comisiones
6️⃣ Cómo hacer retiros
7️⃣ Ver todos los tutoriales

Escribe el número de lo que necesitas o describe tu dificultad.

*¿PREFIERES AYUDA PERSONAL?*
Richard puede ayudarte en videollamada:
📞 +57 305 2490438

¡No te quedes con dudas! 😊"""

        # Tutorial: Descargar aplicación HGW
        if any(w in t for w in ["aplicacion", "aplicación", "app", "descargar app", "instalar app", "descargar aplicacion", "movil", "móvil", "celular"]):
            return """📱 *Cómo Descargar la Aplicación HGW*

La app oficial de HGW te permite gestionar tu negocio desde tu celular.

*TUTORIAL EN VIDEO:*
👉 https://youtube.com/shorts/K7vBQXzoeng

*LINK DE DESCARGA:*
👉 https://file.healthgreenworld.com/app-download/index.html

*PASOS PARA INSTALAR:*

1️⃣ Entra al link de descarga desde tu celular
2️⃣ Descarga el archivo APK (Android) o sigue instrucciones para iOS
3️⃣ Permite instalación de fuentes desconocidas (Android)
4️⃣ Instala la aplicación
5️⃣ Abre la app e inicia sesión con tus credenciales

*FUNCIONES DE LA APP:*
✅ Ver tu backoffice desde el celular
✅ Hacer pedidos rápido
✅ Consultar comisiones
✅ Ver tu red de distribuidores
✅ Compartir productos fácilmente
✅ Recibir notificaciones

*¿PROBLEMAS AL INSTALAR?*
Escribe "ayuda app" o contacta a Richard:
📞 +57 305 2490438

¡Gestiona tu negocio desde cualquier lugar! 📲"""

        # Ayuda con problemas de la app
        if any(w in t for w in ["ayuda app", "problema app", "no instala", "no funciona app", "error app"]):
            return """🔧 *Solución de Problemas - App HGW*

*Problemas comunes y soluciones:*

❌ *"No puedo instalar (Android)"*
→ Ve a Configuración > Seguridad
→ Activa "Orígenes desconocidos" o "Instalar apps desconocidas"
→ Intenta instalar nuevamente

❌ *"La app no abre"*
→ Desinstala la app
→ Descarga nuevamente desde el link oficial
→ Instala y prueba

❌ *"No puedo iniciar sesión"*
→ Verifica que uses tu correo y contraseña del backoffice
→ Si olvidaste tu contraseña, recupérala primero

❌ *"No funciona en iPhone"*
→ Sigue las instrucciones específicas para iOS en el link de descarga

*LINKS IMPORTANTES:*
📱 Descarga: https://file.healthgreenworld.com/app-download/index.html
📹 Tutorial: https://youtube.com/shorts/K7vBQXzoeng

*¿Sigue sin funcionar?*
Richard puede ayudarte en videollamada:
📞 +57 305 2490438"""

        # Tutorial: Cómo ingresar al backoffice
        if any(w in t for w in ["backoffice", "back office", "ingresar", "login", "iniciar sesion", "iniciar sesión"]):
            return """🔐 *Cómo Ingresar al Backoffice HGW*

El backoffice es tu panel de control donde gestionas todo tu negocio.

*TUTORIAL EN VIDEO:*
👉 https://youtu.be/RA3LS-xB3Yw

*PASO A PASO:*
1️⃣ Ve a: www.healthgreenworld.com
2️⃣ Click en "Iniciar Sesión" o "Login"
3️⃣ Ingresa tu usuario (correo o ID)
4️⃣ Ingresa tu contraseña
5️⃣ Click en "Entrar"

*¿OLVIDASTE TU CONTRASEÑA?*
Tutorial para recuperarla:
👉 https://youtu.be/qe9J6D2WHlM

*¿QUIERES CAMBIAR TU CONTRASEÑA?*
Tutorial para cambiarla:
👉 https://youtu.be/JjkH2BDJJ-g

¿Necesitas más ayuda?"""

        # Tutorial: Cómo comprar membresía
        if any(w in t for w in ["membresia", "membresía", "comprar membresia", "adquirir membresia", "activar"]):
            return """💎 *Cómo Comprar Tu Membresía HGW*

La membresía te da acceso a TODOS los beneficios de distribuidor.

*TUTORIAL EN VIDEO:*
👉 https://youtu.be/4D4hEGGJ4Hs

*PASOS:*
1️⃣ Ingresa al backoffice
2️⃣ Ve a "Comprar Membresía"
3️⃣ Selecciona el plan
4️⃣ Elige método de pago
5️⃣ Confirma la compra
6️⃣ ¡Listo! Ya eres distribuidor activo

*MÉTODOS DE PAGO:*
- Nequi 👉 https://youtu.be/MPnSXWut-dk
- Botón Bancolombia 👉 https://youtu.be/BB4CzZYEre4
- Efecty 👉 https://youtu.be/vslriStB4J0

¿Alguna duda con el proceso?"""

        # Tutorial: Cómo hacer pedidos
        if any(w in t for w in ["pedido", "comprar productos", "hacer pedido", "ordenar", "comprar"]):
            return """📦 *Cómo Hacer un Pedido de Productos*

Puedes hacer pedidos para ti o para tus clientes.

*TUTORIALES EN VIDEO:*

📹 Cómo hacer un pedido:
👉 https://youtu.be/D0OeKFFwo6s

📹 Cómo hacer una compra:
👉 https://youtu.be/hTkwRgvRtdQ

*PASOS BÁSICOS:*
1️⃣ Ingresa al backoffice
2️⃣ Ve a "Hacer Pedido" o "Tienda"
3️⃣ Selecciona los productos
4️⃣ Agrega al carrito
5️⃣ Confirma la dirección de envío
6️⃣ Elige método de pago
7️⃣ Finaliza la compra

*OPCIONES DE PAGO:*
💳 Nequi
💳 Botón Bancolombia
💳 Efecty
💳 Tarjeta de crédito

¿Necesitas ver los precios?
Tutorial: https://youtu.be/yBf8VAmaVs4"""

        # Tutorial: Cómo cobrar comisiones
        if any(w in t for w in ["comision", "comisión", "cobrar", "ganancias", "retiro", "retirar", "dinero", "pagar"]):
            return """💰 *Cómo Cobrar Tus Comisiones*

¡Es hora de recibir tus ganancias! Aquí te explico cómo.

*TUTORIAL SUBIR DOCUMENTOS:*
👉 https://youtu.be/AiQ7A01BgY4

*TUTORIAL HACER RETIROS:*
👉 https://youtu.be/axJ8gte1xes

*PROCESO COMPLETO:*

*PASO 1: SUBIR DOCUMENTOS* 📄
(Solo la primera vez)
- Cédula
- RUT (si aplica)
- Certificación bancaria

*PASO 2: VER TUS GANANCIAS* 💵
Tutorial: https://youtu.be/NLCVYvfwtng
- Ingresa al backoffice
- Ve a "Mi Billetera" o "Finanzas"
- Ahí verás tu saldo disponible

*PASO 3: SOLICITAR RETIRO* 🏦
- Click en "Solicitar Retiro"
- Ingresa el monto
- Confirma tu cuenta bancaria
- Listo! El dinero llega en 2-5 días hábiles

¿Problemas con el proceso?"""

        # Tutorial: Enlace de referido
        if any(w in t for w in ["referido", "enlace", "link", "invitar", "compartir", "reclutar"]):
            return """🔗 *Tu Enlace de Referido*

Con este enlace invitas a otras personas y ganas comisiones.

*TUTORIAL EN VIDEO:*
👉 https://youtu.be/r9VrzBnuLoA

*CÓMO ENCONTRARLO:*
1️⃣ Ingresa al backoffice
2️⃣ Ve a "Mi Enlace" o "Referidos"
3️⃣ Copia tu enlace único
4️⃣ Compártelo por WhatsApp, redes sociales, etc.

*CÓMO USARLO:*
📱 Envíaselo a personas interesadas
✅ Cuando se registren con tu enlace, automáticamente quedan en tu red
💰 Ganas comisiones por sus compras

*TIP:*
Usa tu enlace en:
- Estados de WhatsApp
- Facebook
- Instagram
- TikTok
- Email

¿Necesitas estrategias para invitar personas?"""

        # Tutorial: Ver red de socios
        if any(w in t for w in ["red", "equipo", "socios", "downline", "genealogia", "genealogía"]):
            return """👥 *Ver Tu Red de Socios*

Aquí puedes ver toda tu organización y cómo crece.

*TUTORIAL EN VIDEO:*
👉 https://youtu.be/mJNawbqn4Is

*QUÉ PUEDES VER:*
📊 Estructura de tu red
👤 Personas directas que invitaste
👥 Personas que ellos invitaron
📈 Niveles de cada persona
💰 Comisiones generadas

*CÓMO ACCEDER:*
1️⃣ Ingresa al backoffice
2️⃣ Ve a "Mi Red" o "Genealogía"
3️⃣ Explora tu organización

Esto te ayuda a:
✅ Saber quién necesita apoyo
✅ Identificar líderes potenciales
✅ Entender de dónde vienen tus comisiones

¿Quieres tips para hacer crecer tu red?"""

        # Tutorial: Material de apoyo
        if any(w in t for w in ["material", "catalogo", "catálogo", "folleto", "informacion productos", "información productos"]):
            return """📚 *Material de Apoyo HGW*

Tenemos todo el material que necesitas para vender.

*TUTORIAL EN VIDEO:*
👉 https://youtu.be/afeW_mSB3bI

*INFORMACIÓN DE PRODUCTOS:*
👉 https://youtu.be/sIFdPLW3Nrc

*QUÉ ENCUENTRAS:*
📋 Catálogos digitales
📄 Fichas técnicas de productos
🖼️ Imágenes para redes sociales
📹 Videos de productos
📊 Presentaciones
✍️ Testimonios

*DÓNDE ESTÁN:*
1️⃣ Ingresa al backoffice
2️⃣ Ve a "Material de Apoyo" o "Recursos"
3️⃣ Descarga lo que necesites

*USA EL MATERIAL PARA:*
📱 Publicar en redes sociales
💬 Enviar a clientes por WhatsApp
🖨️ Imprimir catálogos físicos
📧 Campañas de email

¡Todo el material es GRATIS!"""

        # Tutorial: Cambiar datos personales
        if any(w in t for w in ["cambiar datos", "actualizar datos", "modificar datos", "direccion", "dirección", "telefono", "teléfono"]):
            return """✏️ *Actualizar Tus Datos*

Es importante mantener tu información actualizada.

*CAMBIAR DATOS PERSONALES:*
👉 https://youtu.be/IDZkjVRKi9I

*CAMBIAR DIRECCIÓN DE ENVÍO:*
👉 https://youtu.be/2O9rox5UiSc

*CAMBIAR CONTRASEÑA DE ACCESO:*
👉 https://youtu.be/JjkH2BDJJ-g

*CAMBIAR CONTRASEÑA DE FINANZAS:*
👉 https://youtu.be/2rmwnPG6org

*¿QUÉ PUEDES ACTUALIZAR?*
✅ Teléfono
✅ Correo electrónico
✅ Dirección de envío
✅ Dirección de facturación
✅ Información bancaria
✅ Contraseñas

*PROCESO:*
1️⃣ Ingresa al backoffice
2️⃣ Ve a "Mi Perfil" o "Configuración"
3️⃣ Edita lo que necesites
4️⃣ Guarda los cambios

¿Necesitas ayuda con algún cambio específico?"""

        # Todos los tutoriales
        if any(w in t for w in ["tutoriales", "videos", "todos los tutoriales", "lista de tutoriales"]):
            return """📲 *TODOS LOS TUTORIALES HGW*

Aquí está la lista completa para que aprendas a usar todo:

*REGISTRO E INICIO:*
1. Cómo inscribirse: https://youtu.be/HCyEHyREYfg
2. Cómo ingresar al backoffice: https://youtu.be/RA3LS-xB3Yw
3. Cómo comprar la membresía: https://youtu.be/4D4hEGGJ4Hs
4. Descargar aplicación móvil: https://youtube.com/shorts/K7vBQXzoeng

*VENTAS Y PEDIDOS:*
5. Enlace de referido: https://youtu.be/r9VrzBnuLoA
6. Hacer un pedido: https://youtu.be/D0OeKFFwo6s
7. Hacer una compra: https://youtu.be/hTkwRgvRtdQ
8. Precios de venta: https://youtu.be/yBf8VAmaVs4

*PAGOS:*
9. Pagar con Nequi: https://youtu.be/MPnSXWut-dk
10. Pagar con Bancolombia: https://youtu.be/BB4CzZYEre4
11. Pagar por Efecty: https://youtu.be/vslriStB4J0

*COMISIONES Y RETIROS:*
12. Subir documentos: https://youtu.be/AiQ7A01BgY4
13. Hacer retiros: https://youtu.be/axJ8gte1xes
14. Ver ganancias: https://youtu.be/NLCVYvfwtng

*GESTIÓN:*
15. Cambiar contraseña acceso: https://youtu.be/JjkH2BDJJ-g
16. Cambiar contraseña finanzas: https://youtu.be/2rmwnPG6org
17. Recuperar contraseña: https://youtu.be/qe9J6D2WHlM
18. Cambiar datos personales: https://youtu.be/IDZkjVRKi9I
19. Cambiar dirección: https://youtu.be/2O9rox5UiSc

*INFORMACIÓN:*
20. Info de productos: https://youtu.be/sIFdPLW3Nrc
21. Material de apoyo: https://youtu.be/afeW_mSB3bI
22. Ver tu red: https://youtu.be/mJNawbqn4Is

*LINK DE DESCARGA APP:*
📱 https://file.healthgreenworld.com/app-download/index.html

*COMPARTE ESTOS TUTORIALES CON TU EQUIPO* 📤

¿Necesitas ayuda con alguno específico?"""

        # Respuesta por defecto - no hay coincidencia
        return None

    async def _get_ai_response(self, text: str, conversation, db: Session):
        """Genera respuesta usando OpenAI"""
        try:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.timestamp).limit(10).all()
            
            chat_history = [{"role": "system", "content": self.business_prompt}]
            for msg in messages:
                chat_history.append({"role": msg.role, "content": msg.content})
            chat_history.append({"role": "user", "content": text})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error en OpenAI: {e}")
            return self._get_default_response(conversation.user_name)

    def _get_default_response(self, user_name: str = None):
        """Respuesta por defecto mejorada"""
        name = user_name if user_name else "amigo/a"
        return f"""Hola {name}, gracias por escribir 😊

Para ayudarte mejor, dime:

*¿Qué te interesa saber?*
1️⃣ Qué es HGW
2️⃣ Qué tengo que hacer
3️⃣ Cuánto cuesta
4️⃣ Cuándo recupero inversión
5️⃣ Cuándo gano dinero
6️⃣ Ver productos
7️⃣ Hablar con Richard

Escribe el número o tu pregunta.

O contacta directo a Richard:
📞 +57 305 2490438"""

    async def _send_whatsapp_message(self, to: str, message: str):
        """Envía mensaje por WhatsApp"""
        if not self.whatsapp_token or not self.phone_id:
            print("WhatsApp no configurado")
            return False
        
        url = f"https://graph.facebook.com/v18.0/{self.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
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
                response = await client.post(url, json=data, headers=headers)
                return response.status_code == 200
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False