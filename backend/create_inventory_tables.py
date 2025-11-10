import pymysql
import sys

# Configuración de la base de datos
config = {
    "host": "localhost",
    "user": "hgw_user",
    "password": "HGW2025_Seguro",
    "database": "hgw_chatbot"
}

# SQL para crear las tablas
sql_commands = [
    """
    CREATE TABLE IF NOT EXISTS vendedores (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nombre VARCHAR(255) NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        email VARCHAR(255),
        direccion TEXT,
        ciudad VARCHAR(100),
        estado ENUM('activo', 'inactivo') DEFAULT 'activo',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_vendedor_estado (estado),
        INDEX idx_vendedor_telefono (telefono)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS productos (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nombre VARCHAR(255) NOT NULL,
        descripcion TEXT,
        codigo VARCHAR(50) UNIQUE,
        precio_unitario DECIMAL(10, 2) NOT NULL,
        categoria VARCHAR(100),
        estado ENUM('activo', 'inactivo') DEFAULT 'activo',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_producto_codigo (codigo),
        INDEX idx_producto_estado (estado)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS stock_vendedores (
        id INT PRIMARY KEY AUTO_INCREMENT,
        vendedor_id INT NOT NULL,
        producto_id INT NOT NULL,
        cantidad_inicial INT NOT NULL DEFAULT 0,
        cantidad_actual INT NOT NULL DEFAULT 0,
        ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (vendedor_id) REFERENCES vendedores(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
        UNIQUE KEY unico_vendedor_producto (vendedor_id, producto_id),
        INDEX idx_stock_vendedor (vendedor_id),
        INDEX idx_stock_producto (producto_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ventas_vendedor (
        id INT PRIMARY KEY AUTO_INCREMENT,
        vendedor_id INT NOT NULL,
        producto_id INT NOT NULL,
        cantidad INT NOT NULL,
        precio_venta DECIMAL(10, 2),
        fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notas TEXT,
        creado_por INT,
        FOREIGN KEY (vendedor_id) REFERENCES vendedores(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
        INDEX idx_ventas_vendedor (vendedor_id),
        INDEX idx_ventas_fecha (fecha_venta)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS asignaciones_productos_vendedor (
        id INT PRIMARY KEY AUTO_INCREMENT,
        vendedor_id INT NOT NULL,
        producto_id INT NOT NULL,
        cantidad INT NOT NULL,
        fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        asignado_por INT,
        notas TEXT,
        FOREIGN KEY (vendedor_id) REFERENCES vendedores(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
        INDEX idx_asignaciones_vendedor (vendedor_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ajustes_inventario_vendedor (
        id INT PRIMARY KEY AUTO_INCREMENT,
        vendedor_id INT NOT NULL,
        producto_id INT NOT NULL,
        tipo_ajuste ENUM('aumento', 'disminucion') NOT NULL,
        cantidad INT NOT NULL,
        cantidad_anterior INT NOT NULL,
        cantidad_nueva INT NOT NULL,
        razon TEXT,
        ajustado_por INT,
        fecha_ajuste TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vendedor_id) REFERENCES vendedores(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
        INDEX idx_ajustes_vendedor (vendedor_id)
    )
    """,
    """
    INSERT INTO vendedores (nombre, telefono, ciudad) VALUES 
    ('Juan Pérez', '3001234567', 'Bogotá'),
    ('María López', '3107654321', 'Medellín'),
    ('Carlos García', '3209876543', 'Cali')
    """,
    """
    INSERT INTO productos (nombre, codigo, precio_unitario, categoria) VALUES
    ('Producto A', 'PROD-001', 10000.00, 'Categoría 1'),
    ('Producto B', 'PROD-002', 15000.00, 'Categoría 1'),
    ('Producto C', 'PROD-003', 20000.00, 'Categoría 2'),
    ('Producto D', 'PROD-004', 25000.00, 'Categoría 2'),
    ('Producto E', 'PROD-005', 30000.00, 'Categoría 3')
    """
]

try:
    # Conectar a la base de datos
    print("🔄 Conectando a la base de datos...")
    connection = pymysql.connect(**config)
    cursor = connection.cursor()
    
    # Ejecutar cada comando SQL
    for i, sql in enumerate(sql_commands, 1):
        try:
            cursor.execute(sql)
            if "CREATE TABLE" in sql:
                print(f"✅ Tabla creada correctamente")
            elif "INSERT INTO" in sql:
                print(f"✅ Datos insertados correctamente")
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"⚠️ Algunos datos ya existen, continuando...")
            else:
                print(f"❌ Error: {e}")
    
    # Confirmar los cambios
    connection.commit()
    
    # Verificar las tablas creadas
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("\n📋 Tablas en la base de datos:")
    for table in tables:
        print(f"   - {table[0]}")
    
    print("\n✅ ¡Tablas de inventario creadas exitosamente!")
    
except Exception as e:
    print(f"❌ Error conectando a la base de datos: {e}")
    sys.exit(1)
finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()