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
        Eres un asistente de HGW (Health Green World) con Richard Córdoba.
        Sé amigable, profesional y persuasivo de forma natural.
        Invita siempre a contactar a Richard al +57 305 2490438.
        Respuestas cortas, máximo 2-3 párrafos.
        """

    async def process_message(self, webhook_data: dict, db: Session):
        """Procesa mensaje entrante de WhatsApp"""
        # Extraer información del webhook
        message_info = self._parse_webhook(webhook_data)
        if not message_info:
            return None
        
        phone = message_info["from"]
        text = message_info["text"]
        msg_id = message_info["id"]
        
        # Verificar duplicados
        if msg_id in self.processed_messages:
            return None
        self.processed_messages.add(msg_id)
        
        # Obtener o crear conversación
        conversation = self._get_or_create_conversation(db, phone)
        
        # Guardar mensaje del usuario
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=text
        )
        db.add(user_message)
        
        # Detectar nombre si es necesario
        if not conversation.user_name:
            name = self._extract_name(text)
            if name:
                conversation.user_name = name
        
        # Detectar perfil e interés
        conversation.profile_type = self._detect_profile(text)
        
        # Actualizar o crear lead
        self._update_lead(db, phone, conversation.user_name, text)
        
        # Generar respuesta
        response = await self._generate_response(text, conversation, db)
        
        # Guardar respuesta del bot
        bot_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response
        )
        db.add(bot_message)
        
        # Actualizar última interacción
        conversation.last_interaction = datetime.utcnow()
        
        db.commit()
        
        # Enviar respuesta por WhatsApp
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
        
        if any(w in text_lower for w in ["tiempo", "ocupado"]):
            return "sin_tiempo"
        elif any(w in text_lower for w in ["dinero", "joven", "estudiante"]):
            return "joven_economico"
        elif any(w in text_lower for w in ["salud", "bienestar", "natural"]):
            return "bienestar"
        elif any(w in text_lower for w in ["negocio", "emprender", "ganar"]):
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
        
        if any(w in text_lower for w in ["precio", "empezar", "quiero", "inscribir"]):
            return 9
        elif any(w in text_lower for w in ["información", "cuéntame"]):
            return 6
        elif any(w in text_lower for w in ["no gracias", "no interesa"]):
            return 2
        
        return 5

    async def _generate_response(self, text: str, conversation, db: Session):
        """Genera respuesta del chatbot"""
        # Primero intentar respuestas automáticas
        auto_response = self._get_auto_response(text, conversation.user_name)
        if auto_response:
            return auto_response
        
        # Si OpenAI está habilitado, usar IA
        if self.openai_client and self.use_openai:
            return await self._get_ai_response(text, conversation, db)
        
        # Respuesta por defecto
        return self._get_default_response(conversation.user_name)

    def _get_auto_response(self, text: str, user_name: str = None):
        """Respuestas automáticas basadas en palabras clave - VERSIÓN MEJORADA"""
        t = text.lower()
        
        # Saludos - SOLO AQUÍ usamos el nombre personalizado
        if any(w in t for w in ["hola", "buenas", "buenos días", "buenas tardes", "hi", "hello"]) and len(t) < 20:
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
        
        # Unirse / Inscribirse con nombre
        if any(w in t for w in ["unirme", "unir", "inscribirme", "registrarme", "ser parte", "entrar"]):
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
        
        # Sobre HGW / Empresa
        if any(w in t for w in ["qué es hgw", "que es hgw", "empresa", "compañía", "sobre hgw"]):
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
        
        # Precios e inversión
        if any(w in t for w in ["precio", "costo", "cuánto", "vale", "cuanto cuesta", "inversión"]):
            return """💰 *Inversión y Precios HGW*

*Membresías de Inicio:*

📦 *Pre-Junior / Junior*
• Desde $360.000 - $720.000 COP
• Ganancia: 30% en ventas
• Recuperas inversión en 1 mes vendiendo todo

📦 *Senior (300 puntos)*
• $2.160.000 COP
• Ganancia: 30% + bonos de red
• Tiempo: 3 meses aprox.

📦 *Master (600 puntos)*
• $4.320.000 COP
• Ganancia: 52% + todos los bonos
• Tiempo: 6 meses aprox.

*¿Cómo recupero mi inversión?*
Si vendes todos los productos, recuperas tu inversión desde el primer mes + ganas el 30%.

Richard puede explicarte en detalle:
📞 +57 305 2490438"""
        
        # Oportunidad de negocio / Cómo funciona
        if any(w in t for w in ["negocio", "ganar", "ingresos", "trabajo", "dinero", "oportunidad", "emprender", "funciona"]):
            return """💼 *Oportunidad de Negocio HGW*

*¿Qué tienes que hacer?*

1️⃣ *Registrarte como distribuidor*
Elige tu membresía de inicio (Pre-Junior, Junior, Senior, Master)

2️⃣ *Activación mensual*
Mantén compra mínima mensual (10 BV) para habilitar comisiones

3️⃣ *Vender productos*
Gana del 30% al 52% de margen en ventas directas

4️⃣ *Construir tu red*
Recluta distribuidores y gana comisiones de su actividad

5️⃣ *Alcanzar rangos*
Más rango = más bonos y comisiones (hasta 10 generaciones)

*Ganancias:*
✅ Margen de venta directa (30% - 52%)
✅ Bono de Inicio Rápido
✅ Bono de Equipo
✅ Comisiones de red (10 generaciones)
✅ Bonos por rango
✅ Sin límite de ingresos

Richard te explica todo paso a paso:
📞 +57 305 2490438"""
        
        # Cuándo empiezo a ganar
        if any(w in t for w in ["cuando gano", "cuándo gano", "cuando empiezo", "ganancia", "utilidad", "cuanto gano", "cuánto gano"]):
            return """📊 *¿Cuándo Empiezas a Ganar?*

*Recuperación de Inversión:*
✅ *Mes 1:* Si vendes todo, recuperas inversión + ganas 30%

Ejemplo con 100 puntos:
• Inversión: $720.000
• Venta (30% más): $936.000
• Ganancia: $216.000

*Ganancias por Nivel:*

📈 *Pre-Junior / Junior (30%)*
Desde mes 1 → Ganancia por ventas directas

📈 *Senior - 300 pts (30% + bonos)*
Aprox. mes 3 → Bonos de red iniciales

📈 *Master - 600 pts (52% + todos los bonos)*
Aprox. mes 6 → Mayor margen + ingresos residuales

*Plan de Ganancia Mutua:*
• Cobras el mismo cheque que tus directos
• Comisiones hasta 10 generaciones
• Bonos por activación mensual de tu red

¿Quieres tu plan personalizado? Habla con Richard:
📞 +57 305 2490438"""
        
        # Qué tengo que hacer / Requisitos
        if any(w in t for w in ["qué tengo que hacer", "que tengo que hacer", "requisitos", "necesito", "paso a paso"]):
            return """📋 *¿Qué Necesitas para Empezar?*

*Pasos Simples:*

1️⃣ *Hablar con Richard*
Te explica todo el sistema y resuelve dudas

2️⃣ *Elegir membresía*
Según tu presupuesto e interés

3️⃣ *Registrarte*
Completar formulario de inscripción

4️⃣ *Pagar membresía*
Con Nequi, Bancolombia, Efecty o tarjeta

5️⃣ *Recibir productos*
Tu kit de inicio llega en 5-7 días

6️⃣ *Capacitación gratis*
Aprende a vender y construir red

7️⃣ *Activación mensual*
Mantén compra de 10 BV mensual

*No necesitas:*
❌ Experiencia previa
❌ Local físico
❌ Inventario grande
❌ Horario fijo

Trabaja desde casa con tu celular 📱

Comienza hoy con Richard:
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
        
        # Cómo empezar
        if any(w in t for w in ["empezar", "comenzar", "inicio", "como empiezo"]):
            return """¡Excelente decisión! 🚀

Es súper fácil:

1️⃣ Hablas con Richard → te explica los planes
2️⃣ Te registras → recibes tu kit de inicio
3️⃣ Capacitación gratis → aprendes todo

En menos de 1 semana estás listo para empezar a ganar.

Recibes: kit de productos, acceso a la app, capacitación completa y mentor personal.

*Siguiente paso:*
📞 WhatsApp: +57 305 2490438

¿Listo para comenzar? 🌟"""
        
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
            # Obtener historial
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.timestamp).limit(10).all()
            
            # Construir contexto
            chat_history = [{"role": "system", "content": self.business_prompt}]
            for msg in messages:
                chat_history.append({"role": msg.role, "content": msg.content})
            chat_history.append({"role": "user", "content": text})
            
            # Llamar a OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except:
            return self._get_default_response(conversation.user_name)

    def _get_default_response(self, user_name: str = None):
        """Respuesta por defecto"""
        name = user_name if user_name else "amigo/a"
        return f"""Hola {name}, gracias por tu mensaje.

Te invito a conocer más sobre HGW y nuestra oportunidad de negocio.
Contacta directamente a Richard Córdoba:

📱 WhatsApp: +57 305 2490438

¡Te esperamos en el equipo HGW! 🌿"""

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