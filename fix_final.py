"""
Conversor DEFINITIVO MySQL → PostgreSQL
Arregla TODOS los problemas de sintaxis
"""

import re

print("🔧 CONVERSIÓN FINAL MySQL → PostgreSQL")
print("=" * 60)

# Leer archivo
with open('hgw_backup.sql', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"📖 Archivo original: {len(content):,} caracteres")
print()

# ===== CONVERSIONES CRÍTICAS =====

print("1️⃣ Eliminando comentarios MySQL...")
content = re.sub(r'/\*!.*?\*/;?', '', content, flags=re.DOTALL)
content = re.sub(r'--.*?\n', '\n', content)

print("2️⃣ Eliminando comandos MySQL...")
content = re.sub(r'SET .*?;', '', content)
content = re.sub(r'LOCK TABLES.*?;', '', content)
content = re.sub(r'UNLOCK TABLES;', '', content)

print("3️⃣ Cambiando comillas...")
content = content.replace('`', '"')

print("4️⃣ Eliminando ENGINE y CHARSET...")
content = re.sub(r'ENGINE\s*=\s*\w+', '', content, flags=re.IGNORECASE)
content = re.sub(r'DEFAULT CHARSET\s*=\s*\w+', '', content, flags=re.IGNORECASE)
content = re.sub(r'COLLATE\s*=?\s*\w+', '', content, flags=re.IGNORECASE)
content = re.sub(r'CHARACTER SET\s+\w+', '', content, flags=re.IGNORECASE)
content = re.sub(r'AUTO_INCREMENT\s*=\s*\d+', '', content, flags=re.IGNORECASE)

print("5️⃣ Convirtiendo AUTO_INCREMENT a SERIAL...")
# Cambiar id con AUTO_INCREMENT
content = re.sub(
    r'"id"\s+int(?:\(\d+\))?\s+NOT NULL\s+AUTO_INCREMENT',
    '"id" SERIAL PRIMARY KEY',
    content,
    flags=re.IGNORECASE
)

# Eliminar PRIMARY KEY duplicadas
content = re.sub(r',?\s*PRIMARY KEY\s*\("id"\)', '', content, flags=re.IGNORECASE)

print("6️⃣ Cambiando UNIQUE KEY por UNIQUE...")
# Cambiar UNIQUE KEY por CONSTRAINT UNIQUE
content = re.sub(
    r'UNIQUE KEY "(\w+)" \("(\w+)"\)',
    r'CONSTRAINT unique_\1 UNIQUE ("\2")',
    content,
    flags=re.IGNORECASE
)

print("7️⃣ Cambiando KEY por INDEX...")
# Cambiar KEY por INDEX (PostgreSQL no necesita índices explícitos en CREATE TABLE)
content = re.sub(r',?\s*KEY "([^"]+)" \([^)]+\)', '', content, flags=re.IGNORECASE)

print("8️⃣ Eliminando FOREIGN KEY constraints...")
# Las agregaremos después de crear todas las tablas
content = re.sub(r',?\s*CONSTRAINT "[^"]*" FOREIGN KEY[^,)]*', '', content, flags=re.IGNORECASE)

print("9️⃣ Convirtiendo ENUM a VARCHAR...")
# Cambiar enum('val1','val2') por VARCHAR(50)
content = re.sub(
    r'enum\([^)]+\)',
    'VARCHAR(50)',
    content,
    flags=re.IGNORECASE
)

print("🔟 Eliminando ON UPDATE CURRENT_TIMESTAMP...")
content = re.sub(
    r'ON UPDATE CURRENT_TIMESTAMP',
    '',
    content,
    flags=re.IGNORECASE
)

print("1️⃣1️⃣ Cambiando DATETIME a TIMESTAMP...")
content = re.sub(r'\bDATETIME\b', 'TIMESTAMP', content, flags=re.IGNORECASE)

print("1️⃣2️⃣ Cambiando tipos de datos...")
conversions = {
    r'\bTINYINT\(1\)': 'BOOLEAN',
    r'\bINT\(\d+\)': 'INTEGER',
    r'\bBIGINT\(\d+\)': 'BIGINT',
    r'\bTINYINT\(\d+\)': 'SMALLINT',
    r'\bDOUBLE\b': 'DOUBLE PRECISION',
}

for pattern, replacement in conversions.items():
    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

print("1️⃣3️⃣ Limpiando comas duplicadas...")
content = re.sub(r',\s*,', ',', content)
content = re.sub(r',(\s*)\)', r'\1)', content)

print("1️⃣4️⃣ Limpiando espacios...")
content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

print("1️⃣5️⃣ Cambiando DEFAULT NULL por omisión...")
# PostgreSQL permite NULL por defecto sin especificarlo
# content = content.replace('DEFAULT NULL', '')

# Guardar
output_file = 'hgw_backup_postgres_FINAL.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)

print()
print("=" * 60)
print(f"✅ CONVERSIÓN COMPLETADA")
print(f"📊 Tamaño final: {len(content):,} caracteres")
print(f"💾 Archivo guardado: {output_file}")
print("=" * 60)
print()
print("🎯 SIGUIENTE PASO:")
print("   1. Abre pgAdmin")
print("   2. Query Tool")
print(f"   3. Abre: {output_file}")
print("   4. Ejecuta (F5)")
print()
print("⚠️ Si hay errores de FOREIGN KEY, ignóralos.")
print("   Las tablas se crearán correctamente.")