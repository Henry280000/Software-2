#!/usr/bin/env python3
"""
Script POO para sincronizar inventario de MongoDB a MySQL
Implementa clase InventorySynchronizer para gestión de sincronización
"""

import sys
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass

sys.path.append('/app')

from db_mysql import MySQLConnection
from db_mongodb import MongoDBConnection


@dataclass
class InventoryItem:
    """Representa un item de inventario"""
    sku: str
    producto_id: str
    nombre_producto: str
    talla: str
    stock: int
    precio: float


class InventorySynchronizer:
    """
    Clase que gestiona la sincronización de inventario entre MongoDB y MySQL
    Implementa validaciones y manejo de errores robusto
    """
    
    def __init__(self):
        """Inicializa las conexiones a bases de datos (Singleton)"""
        self.mysql = MySQLConnection()
        self.mongo = MongoDBConnection()
        self.items_procesados = 0
        self.items_actualizados = 0
        self.items_agregados = 0
        self.errores = []
    
    def _get_inventory_mapping(self) -> Dict[str, List[Tuple[str, str, int]]]:
        """
        Retorna el mapeo de productos a items de inventario
        
        Returns:
            Diccionario con producto_id como key y lista de (sku, talla, stock)
        """
        return {
            'jersey_rm_home_2024': [
                ('RM-HOME-2024-S', 'S', 50),
                ('RM-HOME-2024-M', 'M', 75),
                ('RM-HOME-2024-L', 'L', 100),
                ('RM-HOME-2024-XL', 'XL', 60)
            ],
            'jersey_bar_home_2024': [
                ('BAR-HOME-2024-S', 'S', 45),
                ('BAR-HOME-2024-M', 'M', 80),
                ('BAR-HOME-2024-L', 'L', 90),
                ('BAR-HOME-2024-XL', 'XL', 55)
            ],
            'jersey_man_home_2024': [
                ('MU-HOME-2024-S', 'S', 40),
                ('MU-HOME-2024-M', 'M', 70),
                ('MU-HOME-2024-L', 'L', 85),
                ('MU-HOME-2024-XL', 'XL', 50)
            ],
            'jersey_liv_home_2024': [
                ('LIV-HOME-2024-S', 'S', 55),
                ('LIV-HOME-2024-M', 'M', 85),
                ('LIV-HOME-2024-L', 'L', 95),
                ('LIV-HOME-2024-XL', 'XL', 65)
            ],
            'jersey_psg_home_2024': [
                ('PSG-HOME-2024-S', 'S', 35),
                ('PSG-HOME-2024-M', 'M', 60),
                ('PSG-HOME-2024-L', 'L', 75),
                ('PSG-HOME-2024-XL', 'XL', 45)
            ],
            'jersey_bay_home_2024': [
                ('BAY-HOME-2024-S', 'S', 42),
                ('BAY-HOME-2024-M', 'M', 68),
                ('BAY-HOME-2024-L', 'L', 82),
                ('BAY-HOME-2024-XL', 'XL', 52)
            ]
        }
    
    def _limpiar_inventario_existente(self, cursor):
        """Limpia el inventario existente antes de sincronizar"""
        print("\nLimpiando inventario existente...")
        cursor.execute("DELETE FROM Inventario WHERE id_inventario > 10")
    
    def _crear_inventory_item(self, jersey: dict, sku: str, talla: str, stock: int) -> InventoryItem:
        """Crea un objeto InventoryItem desde datos de jersey"""
        return InventoryItem(
            sku=sku,
            producto_id=jersey['_id'],
            nombre_producto=jersey['nombre'],
            talla=talla,
            stock=stock,
            precio=float(jersey['precio_base'])
        )
    
    def _item_existe(self, cursor, sku: str) -> bool:
        """Verifica si un item ya existe en la base de datos"""
        cursor.execute("SELECT id_inventario FROM Inventario WHERE sku = %s", (sku,))
        return cursor.fetchone() is not None
    
    def _actualizar_item(self, cursor, item: InventoryItem) -> bool:
        """Actualiza un item existente en el inventario"""
        try:
            cursor.execute("""
                UPDATE Inventario 
                SET cantidad_disponible = %s, precio_unitario = %s
                WHERE sku = %s
            """, (item.stock, item.precio, item.sku))
            print(f"  Actualizado: {item.sku} ({item.talla}) - Stock: {item.stock}")
            self.items_actualizados += 1
            return True
        except Exception as e:
            self.errores.append(f"Error actualizando {item.sku}: {e}")
            return False
    
    def _insertar_item(self, cursor, item: InventoryItem) -> bool:
        """Inserta un nuevo item en el inventario"""
        try:
            cursor.execute("""
                INSERT INTO Inventario 
                (sku, producto_id, nombre_producto, talla, cantidad_disponible, precio_unitario)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item.sku, item.producto_id, item.nombre_producto, 
                  item.talla, item.stock, item.precio))
            print(f"  Agregado: {item.sku} ({item.talla}) - Stock: {item.stock}")
            self.items_agregados += 1
            return True
        except Exception as e:
            self.errores.append(f"Error insertando {item.sku}: {e}")
            return False
    
    def sincronizar(self) -> bool:
        """
        Ejecuta la sincronización completa del inventario
        
        Returns:
            True si la sincronización fue exitosa, False en caso contrario
        """
        print("=" * 60)
        print("SINCRONIZACIÓN DE INVENTARIO: MongoDB -> MySQL")
        print("=" * 60)
        
        try:
            jerseys = list(self.mongo.db.jerseys.find())
            print(f"\nEncontrados {len(jerseys)} productos en MongoDB")
            
            inventory_mapping = self._get_inventory_mapping()
            
            connection = self.mysql.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            self._limpiar_inventario_existente(cursor)
            connection.commit()
            
            for jersey in jerseys:
                product_id = jersey['_id']
                product_name = jersey['nombre']
                
                if product_id in inventory_mapping:
                    print(f"\nProcesando: {product_name}")
                    
                    for sku, talla, stock in inventory_mapping[product_id]:
                        item = self._crear_inventory_item(jersey, sku, talla, stock)
                        
                        if self._item_existe(cursor, sku):
                            self._actualizar_item(cursor, item)
                        else:
                            self._insertar_item(cursor, item)
                        
                        self.items_procesados += 1
                    
                    connection.commit()
            
            cursor.execute("SELECT COUNT(*) as total FROM Inventario")
            total = cursor.fetchone()['total']
            
            self._imprimir_resumen(total)
            
            cursor.close()
            connection.close()
            
            return len(self.errores) == 0
            
        except Exception as e:
            print(f"\nError en sincronización: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _imprimir_resumen(self, total_inventario: int):
        """Imprime el resumen de la sincronización"""
        print("\n" + "=" * 60)
        print("SINCRONIZACIÓN COMPLETADA")
        print(f"  Items procesados: {self.items_procesados}")
        print(f"  Items agregados: {self.items_agregados}")
        print(f"  Items actualizados: {self.items_actualizados}")
        print(f"  Total en inventario: {total_inventario}")
        
        if self.errores:
            print(f"  Errores encontrados: {len(self.errores)}")
            for error in self.errores:
                print(f"    - {error}")
        
        print("=" * 60)


if __name__ == "__main__":
    synchronizer = InventorySynchronizer()
    success = synchronizer.sincronizar()
    sys.exit(0 if success else 1)
