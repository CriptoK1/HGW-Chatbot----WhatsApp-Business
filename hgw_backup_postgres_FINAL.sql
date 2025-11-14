
BEGIN;
DROP TABLE IF EXISTS admin_users CASCADE;

CREATE TABLE admin_users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  nombre_completo VARCHAR(200) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT NULL,
  CONSTRAINT unique_username UNIQUE (username)
);

-- CORREGIDO: Eliminada la inserción duplicada
INSERT INTO admin_users (id, username, password, nombre_completo, created_at)
VALUES
  (1,'admin','$2b$12$1QXUUYrSY/TRikC5xkl5Du6auYHcTHkWubl.Q/Ws26vxZV1j5VhIm','Administrador Principal','2025-10-13 03:12:55');

-- =========================================
-- vendedores
-- =========================================
DROP TABLE IF EXISTS vendedores CASCADE;

CREATE TABLE vendedores (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  email VARCHAR(255) DEFAULT NULL,
  direccion TEXT,
  ciudad VARCHAR(100) DEFAULT NULL,
  estado VARCHAR(50) DEFAULT 'activo',
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS productos CASCADE;

CREATE TABLE productos (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  codigo VARCHAR(50) DEFAULT NULL,
  precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario >= 0),
  categoria VARCHAR(100) DEFAULT NULL,
  estado VARCHAR(50) DEFAULT 'activo',
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT unique_codigo UNIQUE (codigo)
);

INSERT INTO productos (id, nombre, descripcion, codigo, precio_unitario, categoria, estado, fecha_creacion, fecha_actualizacion)
VALUES
 (9,'Crema Dental HGW','Crema dental con propiedades de limpieza y protección dental','HGW-CD-001',30000.00,'Higiene Personal','activo','2025-11-13 01:53:46','2025-11-13 02:02:18'),
 (10,'Jabón de Turmalina HGW','Jabón enriquecido con turmalina para cuidado de la piel','HGW-JT-001',18000.00,'Higiene Personal','activo','2025-11-13 01:53:46','2025-11-13 02:02:18'),
 (11,'Jabón de Oliva HGW','Jabón suave de oliva, ideal para piel sensible','HGW-JO-001',18000.00,'Higiene Personal','activo','2025-11-13 01:53:46','2025-11-13 02:02:18'),
 (12,'Toalla Higiénica Día HGW','Toalla higiénica de día, máxima absorción','HGW-THD-001',21000.00,'Femenino','activo','2025-11-13 01:53:46','2025-11-13 02:02:18'),
 (13,'Toalla Higiénica Noche HGW','Toalla higiénica de noche, protección extra','HGW-THN-001',19200.00,'Femenino','activo','2025-11-13 01:53:46','2025-11-13 02:02:18'),
 (14,'Protector Diario HGW','Protector diario suave, ideal para uso diario','HGW-PD-001',21000.00,'Femenino','activo','2025-11-13 01:53:46','2025-11-13 02:02:18');

DROP TABLE IF EXISTS ajustes_inventario_vendedor CASCADE;

CREATE TABLE ajustes_inventario_vendedor (
  id SERIAL PRIMARY KEY,
  vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
  producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  tipo_ajuste VARCHAR(50) NOT NULL,
  cantidad INT NOT NULL,
  cantidad_anterior INT NOT NULL,
  cantidad_nueva INT NOT NULL,
  razon TEXT,
  ajustado_por INT DEFAULT NULL,
  fecha_ajuste TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS asignaciones_productos_vendedor CASCADE;

CREATE TABLE asignaciones_productos_vendedor (
  id SERIAL PRIMARY KEY,
  vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
  producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  cantidad INT NOT NULL,
  fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  asignado_por INT DEFAULT NULL,
  notas TEXT
);


DROP TABLE IF EXISTS asignaciones_vendedor CASCADE;

CREATE TABLE asignaciones_vendedor (
  id SERIAL PRIMARY KEY,
  vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
  producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  cantidad INT NOT NULL,
  fecha_asignacion TIMESTAMP DEFAULT NULL,
  notas TEXT
);

DROP TABLE IF EXISTS conversations CASCADE;

CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR(20) NOT NULL,
  user_name VARCHAR(100) DEFAULT NULL,
  status VARCHAR(50) DEFAULT NULL,
  profile_type VARCHAR(50) DEFAULT NULL,
  last_interaction TIMESTAMP DEFAULT NULL,
  created_at TIMESTAMP DEFAULT NULL,
  CONSTRAINT unique_phone_number_conversations UNIQUE (phone_number)
);

INSERT INTO conversations VALUES
  (1,'573053677841','Nicol','nuevo','otro','2025-11-04 03:37:49','2025-10-12 03:23:07'),
  (2,'573052490438','Richard','nuevo','otro','2025-10-13 00:44:49','2025-10-12 23:38:23');


DROP TABLE IF EXISTS distributors CASCADE;

CREATE TABLE distributors (
  id SERIAL PRIMARY KEY,
  nombres VARCHAR(100) NOT NULL,
  apellidos VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  email VARCHAR(100) DEFAULT NULL,
  fecha_ingreso DATE NOT NULL,
  fecha_cumpleanos DATE DEFAULT NULL,
  usuario VARCHAR(100) NOT NULL,
  contrasena VARCHAR(255) NOT NULL,
  contrasena_doble_factor VARCHAR(255) DEFAULT NULL,
  contrasena_texto VARCHAR(255) DEFAULT NULL,
  contrasena_2fa_texto VARCHAR(255) DEFAULT NULL,
  nivel VARCHAR(50) DEFAULT NULL,
  estado VARCHAR(50) DEFAULT NULL,
  lead_phone VARCHAR(20) DEFAULT NULL,
  notas TEXT,
  created_at TIMESTAMP DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT NULL,
  CONSTRAINT unique_telefono_distributors UNIQUE (telefono),
  CONSTRAINT unique_usuario_distributors UNIQUE (usuario),
  CONSTRAINT unique_email_distributors UNIQUE (email)
);

INSERT INTO distributors VALUES
(1,'Nicol','Cordoba','3053677841','nicolcordobam@gmail.com','2025-10-19','2006-10-24','Criptodata',
 '$2b$12$7Nsjn0iQs6W8qQm4g7fNWOi2gg87yME.AprK5jCRmOB7sRtGM/BO.',
 '$2b$12$0/fFL8fxQmp1UaGy4KzH1ehvRc82svwd8nW.weghUHEALa3yRRdvC',
 'RChef123.','11111111','Master','activo',NULL,'sapa','2025-10-24 05:58:46','2025-11-13 02:03:16'),
(2,'richard','cordoba','3052490438','richychef2016@gmail.com','2023-10-23','1967-03-01','RCHGW',
 '$2b$12$6/OoffvsdvmRZq70809LW.xH7D99sc7QmWV6ReHe6MtzxLw/1/BAq',
 '$2b$12$AbNtpqZhFLQDd4Ly73c77ODT.h8LklwcSC040OR46AT6FJDk9vln2',
 '2023Richy','11111111','Oro','activo',NULL,'lider','2025-10-26 01:35:55','2025-11-13 02:09:06'),
(8,'Olga','exito','20390394',NULL,'2025-11-02',NULL,'OlgaHGW',
 '$2b$12$yX7a46TTeLqpGk8Y5y.GjO5vaUCu1nEpppNTUyIJN.QLBsaKikkXC',
 '$2b$12$750soXbINdJYCCvVuA4UouJZEse602HWV/d47F2AyO.gctEnjjsnS',
 'HGWolguita','11111111','Plata','activo',NULL,'es  se volvio plata en 2 semanas','2025-11-04 03:08:02','2025-11-13 02:09:30'),
(9,'floralba','brava','422343425',NULL,'2025-10-31',NULL,'floralbaHGW',
 '$2b$12$6FfdQRUiONk3eNGFf5KEzO7R2NWJP2BjQVuQ/SgRzZpjCrIEcZ0j2',
 '$2b$12$rXt1JlHtc6x3LsM3I6EOnOol9u8P3gxqc3oH9rmRD/PrSsbGNztmS',
 '238992834','11111111','Master','activo',NULL,'NO LA AYUDARON EN HGW jajajajaj','2025-11-04 03:24:43','2025-11-13 02:09:20');

DROP TABLE IF EXISTS leads CASCADE;

CREATE TABLE leads (
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR(20) NOT NULL,
  user_name VARCHAR(100) DEFAULT NULL,
  email VARCHAR(100) DEFAULT NULL,
  profile_type VARCHAR(50) DEFAULT NULL,
  interest_level INT DEFAULT NULL,
  status VARCHAR(50) DEFAULT NULL,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT NULL,
  CONSTRAINT unique_phone_number_leads UNIQUE (phone_number)
);

INSERT INTO leads VALUES
(1,'573053677841','Nicol',NULL,'otro',9,'nuevo',NULL,'2025-10-12 03:23:07','2025-11-04 03:37:49'),
(2,'573052490438','Richard',NULL,'otro',8,'nuevo',NULL,'2025-10-13 00:29:37','2025-10-13 00:29:37');


DROP TABLE IF EXISTS stock_vendedor CASCADE;

CREATE TABLE stock_vendedor (
  id SERIAL PRIMARY KEY,
  vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
  producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  cantidad_inicial INT DEFAULT NULL,
  cantidad_actual INT DEFAULT NULL,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
DROP TABLE IF EXISTS messages CASCADE;

CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT NULL
);

INSERT INTO "messages" VALUES (1,1,'system','\nEres un asistente virtual de HGW (Health Green World) para la organización Empoderando Líderes, trabajando junto a Richard Córdoba.\n\n🎯 Tu misión es:\n1. Dar la bienvenida de forma cercana, alegre y profesional.\n2. Preguntar el nombre de la persona para crear confianza.\n3. Mostrar empatía según el perfil del cliente:\n   - Si menciona que no tiene tiempo: destaca que en HGW se puede generar ingresos dedicando pocas horas al día.\n   - Si es joven o dice que el dinero no alcanza: resalta que puede empezar con poco y generar ingresos adicionales.\n   - Si busca bienestar: habla de los productos naturales y sus beneficios para salud y energía.\n4. Explicar los beneficios de HGW: Ingresos semanales, sistema de puntos, oportunidad global.\n5. Ser persuasivo de forma natural.\n6. Siempre invitar a agendar una llamada con Richard Córdoba 📞 al +57 305 2490438.\n7. Termina con tono positivo y motivador.\n\nRespuestas cortas: máximo 3-4 párrafos.\n','2025-10-12 03:23:07'),(59,2,'system','\nEres un asistente virtual de HGW (Health Green World) para la organización Empoderando Líderes, trabajando junto a Richard Córdoba.\n\n🎯 Tu misión es:\n1. Dar la bienvenida de forma cercana, alegre y profesional.\n2. Preguntar el nombre de la persona para crear confianza.\n3. Mostrar empatía según el perfil del cliente:\n   - Si menciona que no tiene tiempo: destaca que en HGW se puede generar ingresos dedicando pocas horas al día.\n   - Si es joven o dice que el dinero no alcanza: resalta que puede empezar con poco y generar ingresos adicionales.\n   - Si busca bienestar: habla de los productos naturales y sus beneficios para salud y energía.\n4. Explicar los beneficios de HGW: Ingresos semanales, sistema de puntos, oportunidad global.\n5. Ser persuasivo de forma natural y casual.\n6. Siempre invitar a agendar una llamada con Richard Córdoba 📞 al +57 305 2490438.\n7. Termina con tono positivo y motivador.\n\nRespuestas cortas y conversacionales: máximo 2-3 párrafos cortos.\nHabla como un amigo que quiere ayudar, no como un vendedor.\n','2025-10-12 23:38:23'),(74,1,'user','Hola','2025-10-13 00:24:34'),(76,1,'user','Que es hgw','2025-10-13 00:24:51'),(77,1,'assistant','🌿 *¿Qué es HGW (Health Green World)?*\n\nHGW es una empresa transnacional de venta directa con más de 30 años de trayectoria, presente en más de 30 países.\n\n*Ofrecemos:*\n✅ Productos naturales de salud y bienestar\n✅ Sistema de compensación \"Plan de Ganancia Mutua\"\n✅ Oportunidad de negocio flexible\n✅ Capacitación completa y apoyo\n\n*Nuestro modelo:*\n• Vendes productos con margen de 30% a 52%\n• Construyes tu red de distribuidores\n• Ganas comisiones hasta 10 generaciones\n• Sin límite de ingresos\n\n¿Quieres saber más? Habla con Richard:\n📞 +57 305 2490438','2025-10-13 00:24:51'),(78,1,'user','Que productos ofreces','2025-10-13 00:25:15'),(79,1,'assistant','🛒 *Catálogo HGW Colombia*\n\nTenemos productos 100% naturales certificados:\n\n*🥗 Alimentos y Bebidas:*\n• Blueberry Candy, Fresh Candy\n• Concentrado de Arándanos\n• Té de Arándanos\n• Café con Ganoderma / Cordyceps\n• Omega 3-6-9, Espirulina\n\n*🧼 Higiene Personal:*\n• Pasta dental herbal\n• Jabones (turmalina, oliva)\n• Shampoo Keratina\n• Gel de ducha\n\n*🌸 Productos Femeninos:*\n• Toallas sanitarias Smilife\n• Protectores diarios\n\n*💎 Bienestar Físico:*\n• Termos con turmalina\n• Collares y pulseras\n\nEscribe el nombre del producto que te interesa para más detalles 😊\n\nO habla con Richard: +57 305 2490438','2025-10-13 00:25:15'),(80,1,'user','Hablame de las toallas higiénicas','2025-10-13 00:25:34'),(81,1,'assistant','🌸 *Toallas Sanitarias Smilife HGW*\n\n*Toallas día y noche*\n💎 Con turmalina y aniones\n\n✅ Previenen infecciones\n✅ Neutralizan olores\n✅ Alivian cólicos menstruales\n✅ Mejoran la circulación\n✅ Mantienen pH balanceado\n✅ Ultra absorbentes\n\nTecnología que cuida tu salud íntima naturalmente.\n\nPedidos con Richard:\n📞 +57 305 2490438','2025-10-13 00:25:34'),(82,1,'user','Que tengo que hacer para ganar dinero','2025-10-13 00:25:55'),(83,1,'assistant','💼 *Oportunidad de Negocio HGW*\n\n*¿Qué tienes que hacer?*\n\n1️⃣ *Registrarte como distribuidor*\nElige tu membresía de inicio (Pre-Junior, Junior, Senior, Master)\n\n2️⃣ *Activación mensual*\nMantén compra mínima mensual (10 BV) para habilitar comisiones\n\n3️⃣ *Vender productos*\nGana del 30% al 52% de margen en ventas directas\n\n4️⃣ *Construir tu red*\nRecluta distribuidores y gana comisiones de su actividad\n\n5️⃣ *Alcanzar rangos*\nMás rango = más bonos y comisiones (hasta 10 generaciones)\n\n*Ganancias:*\n✅ Margen de venta directa (30% - 52%)\n✅ Bono de Inicio Rápido\n✅ Bono de Equipo\n✅ Comisiones de red (10 generaciones)\n✅ Bonos por rango\n✅ Sin límite de ingresos\n\nRichard te explica todo paso a paso:\n📞 +57 305 2490438','2025-10-13 00:25:55'),(84,1,'user','Cómo me registro','2025-10-13 00:26:06'),(85,1,'assistant','🚀 *PASO A PASO: Cómo Inscribirse en HGW*\n\n*PASO 1: VER EL TUTORIAL* 📹\nPrimero mira este video que te explica TODO el proceso:\n👉 https://youtu.be/HCyEHyREYfg\n\n*PASO 2: ENTRAR AL SITIO WEB*\n1️⃣ Solicita el enlace de referido a Richard (+57 305 2490438)\n2️⃣ Haz click en el enlace\n3️⃣ Te llevará a la página de registro\n\n*PASO 3: LLENAR EL FORMULARIO*\n📝 Completa tus datos:\n- Nombre completo\n- Documento de identidad\n- Correo electrónico\n- Teléfono\n- Dirección\n\n*PASO 4: ELEGIR TU PLAN*\n💰 Selecciona el plan que más te convenga\n(Richard te habrá explicado las opciones antes)\n\n*PASO 5: REALIZAR EL PAGO*\n💳 Puedes pagar con:\n- Nequi\n- Botón Bancolombia\n- Efecty\n- Tarjeta de crédito\n\n*PASO 6: CONFIRMAR TU REGISTRO*\n✅ Recibirás un correo de confirmación\n✅ Podrás ingresar al backoffice\n\n*¿NECESITAS AYUDA EN EL PROCESO?*\nSi tienes alguna dificultad, escribe \"no puedo\" y te ayudo con lo que necesites.\n\nO contacta directamente a Richard:\n📞 +57 305 2490438','2025-10-13 00:26:06'),(92,2,'user','Cómo me puedo inscribir?','2025-10-13 00:31:45'),(93,2,'assistant','🚀 *PASO A PASO: Cómo Inscribirse en HGW*\n\n*PASO 1: VER EL TUTORIAL* 📹\nPrimero mira este video que te explica TODO el proceso:\n👉 https://youtu.be/HCyEHyREYfg\n\n*PASO 2: ENTRAR AL SITIO WEB*\n1️⃣ Solicita el enlace de referido a Richard (+57 305 2490438)\n2️⃣ Haz click en el enlace\n3️⃣ Te llevará a la página de registro\n\n*PASO 3: LLENAR EL FORMULARIO*\n📝 Completa tus datos:\n- Nombre completo\n- Documento de identidad\n- Correo electrónico\n- Teléfono\n- Dirección\n\n*PASO 4: ELEGIR TU PLAN*\n💰 Selecciona el plan que más te convenga\n(Richard te habrá explicado las opciones antes)\n\n*PASO 5: REALIZAR EL PAGO*\n💳 Puedes pagar con:\n- Nequi\n- Botón Bancolombia\n- Efecty\n- Tarjeta de crédito\n\n*PASO 6: CONFIRMAR TU REGISTRO*\n✅ Recibirás un correo de confirmación\n✅ Podrás ingresar al backoffice\n\n*¿NECESITAS AYUDA EN EL PROCESO?*\nSi tienes alguna dificultad, escribe \"no puedo\" y te ayudo con lo que necesites.\n\nO contacta directamente a Richard:\n📞 +57 305 2490438','2025-10-13 00:31:45'),(94,2,'user','Cómo descargo la aplicación de HGW?','2025-10-13 00:33:44'),(95,2,'assistant','¡Hola Richard! 👋\n\nEntiendo tu pregunta. Te comparto info clave:\n\n*HGW ofrece:*\n🛒 Productos naturales certificados (alimentos, higiene, suplementos)\n💰 Ganancias del 30% al 52% en ventas\n📈 Comisiones de red hasta 10 generaciones\n📊 Recuperas inversión desde el primer mes\n🎓 Capacitación completa gratis\n\n*Pregúntame sobre:*\n• Productos específicos (café, omega, jabones, etc.)\n• Precios y membresías\n• Cuánto puedo ganar\n• Cómo empezar\n\nO contacta directo a Richard para info personalizada:\n📞 +57 305 2490438\n\n¿Qué más quieres saber? 😊','2025-10-13 00:33:44'),(96,2,'user','Quiero saber sobre los productos','2025-10-13 00:37:08'),(97,2,'assistant','🛒 *Catálogo HGW Colombia*\n\nTenemos productos 100% naturales certificados:\n\n*🥗 Alimentos y Bebidas:*\n• Blueberry Candy, Fresh Candy\n• Concentrado de Arándanos\n• Té de Arándanos\n• Café con Ganoderma / Cordyceps\n• Omega 3-6-9, Espirulina\n\n*🧼 Higiene Personal:*\n• Pasta dental herbal\n• Jabones (turmalina, oliva)\n• Shampoo Keratina\n• Gel de ducha\n\n*🌸 Productos Femeninos:*\n• Toallas sanitarias Smilife\n• Protectores diarios\n\n*💎 Bienestar Físico:*\n• Termos con turmalina\n• Collares y pulseras\n\nEscribe el nombre del producto que te interesa para más detalles 😊\n\nO habla con Richard: +57 305 2490438','2025-10-13 00:37:08'),(98,2,'user','Quiero saber sobre el gano derma','2025-10-13 00:38:10'),(99,2,'assistant','¡Hola Richard! 👋\n\nEntiendo tu pregunta. Te comparto info clave:\n\n*HGW ofrece:*\n🛒 Productos naturales certificados (alimentos, higiene, suplementos)\n💰 Ganancias del 30% al 52% en ventas\n📈 Comisiones de red hasta 10 generaciones\n📊 Recuperas inversión desde el primer mes\n🎓 Capacitación completa gratis\n\n*Pregúntame sobre:*\n• Productos específicos (café, omega, jabones, etc.)\n• Precios y membresías\n• Cuánto puedo ganar\n• Cómo empezar\n\nO contacta directo a Richard para info personalizada:\n📞 +57 305 2490438\n\n¿Qué más quieres saber? 😊','2025-10-13 00:38:10'),(100,2,'user','Quiero saber sobre el café','2025-10-13 00:39:18'),(101,2,'assistant','☕ *Cafés Funcionales HGW*\n\n*Café con Ganoderma (Ganoderma Soluble Coffee)*\n🍄 Café enriquecido con hongo medicinal\n✅ Refuerza el sistema inmunológico\n✅ Mejora la energía natural\n✅ Reduce el estrés\n✅ Protege el hígado\n\n*Cordyceps Coffee*\n⚡ Café con hongo Cordyceps\n✅ Aumenta vitalidad y resistencia\n✅ Mejora resistencia física y respiratoria\n✅ Ideal para deportistas\n✅ Combate la fatiga crónica\n\nPrecio y pedidos con Richard:\n📞 +57 305 2490438','2025-10-13 00:39:18'),(102,2,'user','Ganoderma','2025-10-13 00:40:36'),(103,2,'assistant','☕ *Cafés Funcionales HGW*\n\n*Café con Ganoderma (Ganoderma Soluble Coffee)*\n🍄 Café enriquecido con hongo medicinal\n✅ Refuerza el sistema inmunológico\n✅ Mejora la energía natural\n✅ Reduce el estrés\n✅ Protege el hígado\n\n*Cordyceps Coffee*\n⚡ Café con hongo Cordyceps\n✅ Aumenta vitalidad y resistencia\n✅ Mejora resistencia física y respiratoria\n✅ Ideal para deportistas\n✅ Combate la fatiga crónica\n\nPrecio y pedidos con Richard:\n📞 +57 305 2490438','2025-10-13 00:40:36'),(104,2,'user','Cómo puedo ganar dinero','2025-10-13 00:41:32'),(105,2,'assistant','💼 *Oportunidad de Negocio HGW*\n\n*¿Qué tienes que hacer?*\n\n1️⃣ *Registrarte como distribuidor*\nElige tu membresía de inicio (Pre-Junior, Junior, Senior, Master)\n\n2️⃣ *Activación mensual*\nMantén compra mínima mensual (10 BV) para habilitar comisiones\n\n3️⃣ *Vender productos*\nGana del 30% al 52% de margen en ventas directas\n\n4️⃣ *Construir tu red*\nRecluta distribuidores y gana comisiones de su actividad\n\n5️⃣ *Alcanzar rangos*\nMás rango = más bonos y comisiones (hasta 10 generaciones)\n\n*Ganancias:*\n✅ Margen de venta directa (30% - 52%)\n✅ Bono de Inicio Rápido\n✅ Bono de Equipo\n✅ Comisiones de red (10 generaciones)\n✅ Bonos por rango\n✅ Sin límite de ingresos\n\nRichard te explica todo paso a paso:\n📞 +57 305 2490438','2025-10-13 00:41:32'),(106,2,'user','Me explicas sobre los bonos','2025-10-13 00:42:32'),(107,2,'assistant','¡Hola Richard! 👋\n\nEntiendo tu pregunta. Te comparto info clave:\n\n*HGW ofrece:*\n🛒 Productos naturales certificados (alimentos, higiene, suplementos)\n💰 Ganancias del 30% al 52% en ventas\n📈 Comisiones de red hasta 10 generaciones\n📊 Recuperas inversión desde el primer mes\n🎓 Capacitación completa gratis\n\n*Pregúntame sobre:*\n• Productos específicos (café, omega, jabones, etc.)\n• Precios y membresías\n• Cuánto puedo ganar\n• Cómo empezar\n\nO contacta directo a Richard para info personalizada:\n📞 +57 305 2490438\n\n¿Qué más quieres saber? 😊','2025-10-13 00:42:32'),(108,2,'user','Que es  esactamente lo que tengo que hacer en hgw','2025-10-13 00:43:56'),(109,2,'assistant','📋 *¿Qué Necesitas para Empezar?*\n\n*Pasos Simples:*\n\n1️⃣ *Hablar con Richard*\nTe explica todo el sistema y resuelve dudas\n\n2️⃣ *Elegir membresía*\nSegún tu presupuesto e interés\n\n3️⃣ *Registrarte*\nCompletar formulario de inscripción\n\n4️⃣ *Pagar membresía*\nCon Nequi, Bancolombia, Efecty o tarjeta\n\n5️⃣ *Recibir productos*\nTu kit de inicio llega en 5-7 días\n\n6️⃣ *Capacitación gratis*\nAprende a vender y construir red\n\n7️⃣ *Activación mensual*\nMantén compra de 10 BV mensual\n\n*No necesitas:*\n❌ Experiencia previa\n❌ Local físico\n❌ Inventario grande\n❌ Horario fijo\n\nTrabaja desde casa con tu celular 📱\n\nComienza hoy con Richard:\n📞 +57 305 2490438','2025-10-13 00:43:56'),(110,2,'user','4','2025-10-13 00:44:49'),(111,2,'assistant','¡Hola Richard! 👋\n\nEntiendo tu pregunta. Te comparto info clave:\n\n*HGW ofrece:*\n🛒 Productos naturales certificados (alimentos, higiene, suplementos)\n💰 Ganancias del 30% al 52% en ventas\n📈 Comisiones de red hasta 10 generaciones\n📊 Recuperas inversión desde el primer mes\n🎓 Capacitación completa gratis\n\n*Pregúntame sobre:*\n• Productos específicos (café, omega, jabones, etc.)\n• Precios y membresías\n• Cuánto puedo ganar\n• Cómo empezar\n\nO contacta directo a Richard para info personalizada:\n📞 +57 305 2490438\n\n¿Qué más quieres saber? 😊','2025-10-13 00:44:49'),(112,1,'user','Quiero descargar la app','2025-10-13 01:20:11'),(113,1,'user','Quiero descargar la app','2025-10-13 01:21:28'),(114,1,'assistant','📱 *Cómo Descargar la Aplicación HGW*\n\nLa app oficial de HGW te permite gestionar tu negocio desde tu celular.\n\n*TUTORIAL EN VIDEO:*\n👉 https://youtube.com/shorts/K7vBQXzoeng\n\n*LINK DE DESCARGA:*\n👉 https://file.healthgreenworld.com/app-download/index.html\n\n*PASOS PARA INSTALAR:*\n\n1️⃣ Entra al link de descarga desde tu celular\n2️⃣ Descarga el archivo APK (Android) o sigue instrucciones para iOS\n3️⃣ Permite instalación de fuentes desconocidas (Android)\n4️⃣ Instala la aplicación\n5️⃣ Abre la app e inicia sesión con tus credenciales\n\n*FUNCIONES DE LA APP:*\n✅ Ver tu backoffice desde el celular\n✅ Hacer pedidos rápido\n✅ Consultar comisiones\n✅ Ver tu red de distribuidores\n✅ Compartir productos fácilmente\n✅ Recibir notificaciones\n\n*¿PROBLEMAS AL INSTALAR?*\nEscribe \"ayuda app\" o contacta a Richard:\n📞 +57 305 2490438\n\n¡Gestiona tu negocio desde cualquier lugar! 📲','2025-10-13 01:21:28'),(115,1,'user','Hola','2025-10-13 03:23:34'),(116,1,'assistant','¡Hola Nicol! 👋 Bienvenido a *HGW (Health Green World)*\n🌿 *Empoderando Líderes con Richard Córdoba*\n\nSomos una empresa transnacional con +30 años de experiencia en productos naturales para salud y bienestar, presente en más de 30 países.\n\n*¿Qué te interesa conocer?*\n\n🛒 Ver catálogo de productos\n💰 Oportunidad de negocio\n📊 Cuánto puedo ganar\n🚀 Cómo empezar\n❓ Qué es HGW\n\nEscribe lo que te interese o dime tu nombre para personalizar tu experiencia 😊','2025-10-13 03:23:34'),(117,1,'user','Hola','2025-10-13 04:38:45'),(118,1,'assistant','¡Hola Nicol! 👋 Bienvenido a *HGW (Health Green World)*\n🌿 *Empoderando Líderes con Richard Córdoba*\n\nSomos una empresa transnacional con +30 años de experiencia en productos naturales para salud y bienestar, presente en más de 30 países.\n\n*¿Qué te interesa conocer?*\n\n🛒 Ver catálogo de productos\n💰 Oportunidad de negocio\n📊 Cuánto puedo ganar\n🚀 Cómo empezar\n❓ Qué es HGW\n\nEscribe lo que te interese o dime tu nombre para personalizar tu experiencia 😊','2025-10-13 04:38:46'),(119,1,'user','hola','2025-10-22 05:46:57'),(120,1,'assistant','¡Hola Nicol! 👋 Bienvenido a *HGW (Health Green World)*\n🌿 *Empoderando Líderes con Richard Córdoba*\n\nSomos una empresa transnacional con +30 años de experiencia en productos naturales para salud y bienestar, presente en más de 30 países.\n\n*¿Qué te interesa conocer?*\n\n🛒 Ver catálogo de productos\n💰 Oportunidad de negocio\n📊 Cuánto puedo ganar\n🚀 Cómo empezar\n❓ Qué es HGW\n\nEscribe lo que te interese o dime tu nombre para personalizar tu experiencia 😊','2025-10-22 05:46:57'),(121,1,'user','Hola','2025-10-29 05:15:45'),(122,1,'assistant','¡Hola Nicol! 👋 Bienvenido a HGW (Health Green World)\n🌿 Empoderando Líderes con Richard Córdoba\n\nSomos una empresa con +30 años en productos naturales y bienestar.\n\n¿Qué te interesa?\n🛒 Ver productos\n💰 Oportunidad de negocio\n📊 Cuánto puedo ganar\n\nEscribe lo que te interese o tu nombre para personalizar tu experiencia 😊','2025-10-29 05:15:45'),(123,1,'user','Quiero saber sobre los productos','2025-10-29 05:16:08'),(124,1,'assistant','🛒 Catálogo HGW Colombia\n\n✅ Alimentos: Arándanos, Café Ganoderma, Omega 3-6-9\n✅ Higiene: Pasta dental, Jabones, Shampoo\n✅ Bienestar: Termos con turmalina\n✅ Femeninos: Toallas sanitarias Smilife\n\nEscribe el producto que te interesa para más detalles.\nContacta a Richard para precios: +57 305 2490438','2025-10-29 05:16:08'),(125,1,'user','Quiero saber sobre los tutoriales','2025-10-29 05:17:57'),(126,1,'assistant','Hola Nicol, gracias por tu mensaje.\n\nTe invito a conocer más sobre HGW y nuestra oportunidad de negocio.\nContacta directamente a Richard Córdoba:\n\n📱 WhatsApp: +57 305 2490438\n\n¡Te esperamos en el equipo HGW! 🌿','2025-10-29 05:17:57'),(127,1,'user','Hola quiero ver los tutoriales','2025-10-29 06:25:03'),(128,1,'assistant','📲 *TODOS LOS TUTORIALES HGW*\n\nAquí está la lista completa para que aprendas a usar todo:\n\n*REGISTRO E INICIO:*\n1. Cómo inscribirse: https://youtu.be/HCyEHyREYfg\n2. Cómo ingresar al backoffice: https://youtu.be/RA3LS-xB3Yw\n3. Cómo comprar la membresía: https://youtu.be/4D4hEGGJ4Hs\n4. Descargar aplicación móvil: https://youtube.com/shorts/K7vBQXzoeng\n\n*VENTAS Y PEDIDOS:*\n5. Enlace de referido: https://youtu.be/r9VrzBnuLoA\n6. Hacer un pedido: https://youtu.be/D0OeKFFwo6s\n7. Hacer una compra: https://youtu.be/hTkwRgvRtdQ\n8. Precios de venta: https://youtu.be/yBf8VAmaVs4\n\n*PAGOS:*\n9. Pagar con Nequi: https://youtu.be/MPnSXWut-dk\n10. Pagar con Bancolombia: https://youtu.be/BB4CzZYEre4\n11. Pagar por Efecty: https://youtu.be/vslriStB4J0\n\n*COMISIONES Y RETIROS:*\n12. Subir documentos: https://youtu.be/AiQ7A01BgY4\n13. Hacer retiros: https://youtu.be/axJ8gte1xes\n14. Ver ganancias: https://youtu.be/NLCVYvfwtng\n\n*GESTIÓN:*\n15. Cambiar contraseña acceso: https://youtu.be/JjkH2BDJJ-g\n16. Cambiar contraseña finanzas: https://youtu.be/2rmwnPG6org\n17. Recuperar contraseña: https://youtu.be/qe9J6D2WHlM\n18. Cambiar datos personales: https://youtu.be/IDZkjVRKi9I\n19. Cambiar dirección: https://youtu.be/2O9rox5UiSc\n\n*INFORMACIÓN:*\n20. Info de productos: https://youtu.be/sIFdPLW3Nrc\n21. Material de apoyo: https://youtu.be/afeW_mSB3bI\n22. Ver tu red: https://youtu.be/mJNawbqn4Is\n\n*LINK DE DESCARGA APP:*\n📱 https://file.healthgreenworld.com/app-download/index.html\n\n*COMPARTE ESTOS TUTORIALES CON TU EQUIPO* 📤\n\n¿Necesitas ayuda con alguno específico?','2025-10-29 06:25:03'),(129,1,'user','Solo dame el de como puedo a era retiros','2025-10-29 06:25:37'),(130,1,'assistant','💰 *Cómo Cobrar Tus Comisiones*\n\n¡Es hora de recibir tus ganancias! Aquí te explico cómo.\n\n*TUTORIAL SUBIR DOCUMENTOS:*\n👉 https://youtu.be/AiQ7A01BgY4\n\n*TUTORIAL HACER RETIROS:*\n👉 https://youtu.be/axJ8gte1xes\n\n*PROCESO COMPLETO:*\n\n*PASO 1: SUBIR DOCUMENTOS* 📄\n(Solo la primera vez)\n- Cédula\n- RUT (si aplica)\n- Certificación bancaria\n\n*PASO 2: VER TUS GANANCIAS* 💵\nTutorial: https://youtu.be/NLCVYvfwtng\n- Ingresa al backoffice\n- Ve a \"Mi Billetera\" o \"Finanzas\"\n- Ahí verás tu saldo disponible\n\n*PASO 3: SOLICITAR RETIRO* 🏦\n- Click en \"Solicitar Retiro\"\n- Ingresa el monto\n- Confirma tu cuenta bancaria\n- Listo! El dinero llega en 2-5 días hábiles\n\n¿Problemas con el proceso?','2025-10-29 06:25:37'),(131,1,'user','Hola quiero ver los tutoriales','2025-10-29 06:40:09'),(132,1,'assistant','📲 *TODOS LOS TUTORIALES HGW*\n\nAquí está la lista completa para que aprendas a usar todo:\n\n*REGISTRO E INICIO:*\n1. Cómo inscribirse: https://youtu.be/HCyEHyREYfg\n2. Cómo ingresar al backoffice: https://youtu.be/RA3LS-xB3Yw\n3. Cómo comprar la membresía: https://youtu.be/4D4hEGGJ4Hs\n4. Descargar aplicación móvil: https://youtube.com/shorts/K7vBQXzoeng\n\n*VENTAS Y PEDIDOS:*\n5. Enlace de referido: https://youtu.be/r9VrzBnuLoA\n6. Hacer un pedido: https://youtu.be/D0OeKFFwo6s\n7. Hacer una compra: https://youtu.be/hTkwRgvRtdQ\n8. Precios de venta: https://youtu.be/yBf8VAmaVs4\n\n*PAGOS:*\n9. Pagar con Nequi: https://youtu.be/MPnSXWut-dk\n10. Pagar con Bancolombia: https://youtu.be/BB4CzZYEre4\n11. Pagar por Efecty: https://youtu.be/vslriStB4J0\n\n*COMISIONES Y RETIROS:*\n12. Subir documentos: https://youtu.be/AiQ7A01BgY4\n13. Hacer retiros: https://youtu.be/axJ8gte1xes\n14. Ver ganancias: https://youtu.be/NLCVYvfwtng\n\n*GESTIÓN:*\n15. Cambiar contraseña acceso: https://youtu.be/JjkH2BDJJ-g\n16. Cambiar contraseña finanzas: https://youtu.be/2rmwnPG6org\n17. Recuperar contraseña: https://youtu.be/qe9J6D2WHlM\n18. Cambiar datos personales: https://youtu.be/IDZkjVRKi9I\n19. Cambiar dirección: https://youtu.be/2O9rox5UiSc\n\n*INFORMACIÓN:*\n20. Info de productos: https://youtu.be/sIFdPLW3Nrc\n21. Material de apoyo: https://youtu.be/afeW_mSB3bI\n22. Ver tu red: https://youtu.be/mJNawbqn4Is\n\n*LINK DE DESCARGA APP:*\n📱 https://file.healthgreenworld.com/app-download/index.html\n\n*COMPARTE ESTOS TUTORIALES CON TU EQUIPO* 📤\n\n¿Necesitas ayuda con alguno específico?','2025-10-29 06:40:09'),(133,1,'user','Hola','2025-11-04 03:37:49'),(134,1,'assistant','¡Hola Nicol! 👋 Bienvenido a *HGW (Health Green World)*\n🌿 *Empoderando Líderes con Richard Córdoba*\n\nSomos una empresa transnacional con +30 años de experiencia en productos naturales para salud y bienestar, presente en más de 30 países.\n\n*¿Qué te interesa conocer?*\n\n🛒 Ver catálogo de productos\n💰 Oportunidad de negocio\n📊 Cuánto puedo ganar\n🚀 Cómo empezar\n❓ Qué es HGW\n\nEscribe lo que te interese o dime tu nombre para personalizar tu experiencia 😊','2025-11-04 03:37:49');

DROP TABLE IF EXISTS stock_vendedores CASCADE;

CREATE TABLE stock_vendedores (
  id SERIAL PRIMARY KEY,
  vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
  producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  cantidad_inicial INT NOT NULL DEFAULT 0,
  cantidad_actual INT NOT NULL DEFAULT 0,
  ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT unique_stock_vendedor_producto UNIQUE (vendedor_id, producto_id)
);


DROP TABLE IF EXISTS ventas_vendedor CASCADE;

CREATE TABLE ventas_vendedor (
  id SERIAL PRIMARY KEY,
  vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE CASCADE,
  producto_id INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
  cantidad INT NOT NULL,
  precio_venta NUMERIC(10,2) DEFAULT NULL,
  fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  notas TEXT,
  creado_por INT DEFAULT NULL
);


COMMIT;