"""
Script para insertar datos de prueba en el sistema de inventario
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.app.database import SessionLocal
from backend.app.models.inventory import Vendedor, Producto
from datetime import datetime

def seed_data():
    db = SessionLocal()
    
    try:
        # Verificar si ya existen datos
        vendedor_count = db.query(Vendedor).count()
        producto_count = db.query(Producto).count()
        
        if vendedor_count > 0 or producto_count > 0:
            print(f"ℹ️ Ya existen {vendedor_count} vendedores y {producto_count} productos en la base de datos")
            response = input("¿Deseas agregar más datos de prueba? (s/n): ")
            if response.lower() != 's':
                return
        
        print("🌱 Insertando datos de prueba...")
        
        # Insertar vendedores de prueba
        nuevos_vendedores = [
            Vendedor(
                nombre="Ana Martínez",
                telefono="3112223333",
                email="ana@example.com",
                ciudad="Barranquilla",
                direccion="Calle 45 #12-34",
                estado="activo"
            ),
            Vendedor(
                nombre="Pedro Rodríguez",
                telefono="3154445555",
                email="pedro@example.com",
                ciudad="Cartagena",
                direccion="Carrera 23 #56-78",
                estado="activo"
            ),
            Vendedor(
                nombre="Laura Gómez",
                telefono="3186667777",
                email="laura@example.com",
                ciudad="Bucaramanga",
                direccion="Avenida 9 #34-56",
                estado="activo"
            )
        ]
        
        for vendedor in nuevos_vendedores:
            # Verificar que no exista el teléfono
            existe = db.query(Vendedor).filter(Vendedor.telefono == vendedor.telefono).first()
            if not existe:
                db.add(vendedor)
                print(f"  ✅ Vendedor '{vendedor.nombre}' agregado")
            else:
                print(f"  ⚠️ Vendedor con teléfono {vendedor.telefono} ya existe")
        
        # Insertar productos de prueba
        nuevos_productos = [
            Producto(
                nombre="Producto F",
                codigo="PROD-006",
                descripcion="Descripción del producto F",
                precio_unitario=35000.00,
                categoria="Categoría 3",
                estado="activo"
            ),
            Producto(
                nombre="Producto G",
                codigo="PROD-007",
                descripcion="Descripción del producto G",
                precio_unitario=40000.00,
                categoria="Categoría 4",
                estado="activo"
            ),
            Producto(
                nombre="Producto H",
                codigo="PROD-008",
                descripcion="Descripción del producto H",
                precio_unitario=45000.00,
                categoria="Categoría 4",
                estado="activo"
            )
        ]
        
        for producto in nuevos_productos:
            # Verificar que no exista el código
            existe = db.query(Producto).filter(Producto.codigo == producto.codigo).first()
            if not existe:
                db.add(producto)
                print(f"  ✅ Producto '{producto.nombre}' agregado")
            else:
                print(f"  ⚠️ Producto con código {producto.codigo} ya existe")
        
        db.commit()
        print("\n✅ Datos de prueba insertados correctamente")
        
        # Mostrar resumen
        total_vendedores = db.query(Vendedor).count()
        total_productos = db.query(Producto).count()
        print(f"\n📊 Resumen:")
        print(f"   - Total vendedores: {total_vendedores}")
        print(f"   - Total productos: {total_productos}")
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()