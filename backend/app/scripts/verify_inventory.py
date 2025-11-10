"""
Script para verificar que el sistema de inventario esté correctamente instalado
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.app.database import SessionLocal, init_db
from sqlalchemy import text

def verify_inventory_tables():
    """Verifica que las tablas de inventario existan"""
    
    print("🔄 Inicializando base de datos...")
    init_db()
    
    db = SessionLocal()
    
    tables_to_check = [
        'vendedores',
        'productos',
        'stock_vendedores',
        'ventas_vendedor',
        'asignaciones_productos_vendedor',
        'ajustes_inventario_vendedor'
    ]
    
    print("\n🔍 Verificando tablas de inventario...")
    print("-" * 50)
    
    all_exist = True
    for table in tables_to_check:
        try:
            result = db.execute(text(f"SHOW TABLES LIKE '{table}'"))
            if result.fetchone():
                print(f"✅ Tabla '{table}' existe")
            else:
                print(f"❌ Tabla '{table}' NO existe")
                all_exist = False
        except Exception as e:
            print(f"❌ Error verificando tabla '{table}': {e}")
            all_exist = False
    
    print("-" * 50)
    
    if all_exist:
        # Verificar que podemos hacer consultas
        try:
            vendedores_count = db.execute(text("SELECT COUNT(*) FROM vendedores")).scalar()
            productos_count = db.execute(text("SELECT COUNT(*) FROM productos")).scalar()
            
            print(f"\n📊 Estadísticas:")
            print(f"   - Vendedores: {vendedores_count}")
            print(f"   - Productos: {productos_count}")
            
        except Exception as e:
            print(f"⚠️ Error consultando datos: {e}")
    else:
        print("\n⚠️ Algunas tablas no existen. Ejecuta el SQL de creación primero.")
    
    db.close()
    print("\n✅ Verificación completada")

if __name__ == "__main__":
    verify_inventory_tables()