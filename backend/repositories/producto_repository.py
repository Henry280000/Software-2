"""
Repository de Producto - Maneja el acceso a datos de productos
"""

from typing import Optional, List, Dict
from models.producto import Producto
from db_mysql import MySQLConnection
from db_mongodb import MongoDBConnection


class ProductoRepository:
    """Repository para operaciones CRUD de productos (MySQL + MongoDB)"""
    
    def __init__(self):
        """Inicializa el repository con conexiones a ambas bases de datos"""
        self.mysql_db = MySQLConnection()
        self.mongo_db = MongoDBConnection()
    
    def crear(self, producto: Producto) -> Optional[int]:
        """
        Crea un nuevo producto en MySQL e inventario en MongoDB
        
        Args:
            producto: Objeto Producto a crear
            
        Returns:
            ID del producto creado o None si hay error
        """
        try:
            # Insertar en MySQL
            query = """
                INSERT INTO Productos (nombre, descripcion, precio, categoria, 
                                      equipo, liga, temporada, imagen_url, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                producto.nombre,
                producto.descripcion,
                producto.precio,
                producto.categoria,
                producto.equipo,
                producto.liga,
                producto.temporada,
                producto.imagen_url,
                producto.activo
            )
            
            connection = self.mysql_db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            
            producto_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            # Insertar inventario en MongoDB
            inventario_doc = {
                'producto_id': producto_id,
                'inventario': producto.inventario
            }
            self.mongo_db.insert_one('inventario', inventario_doc)
            
            return producto_id
            
        except Exception as e:
            print(f"Error al crear producto: {str(e)}")
            return None
    
    def obtener_por_id(self, id_producto: int) -> Optional[Producto]:
        """
        Obtiene un producto por su ID (con inventario de MongoDB)
        
        Args:
            id_producto: ID del producto
            
        Returns:
            Objeto Producto o None si no se encuentra
        """
        try:
            # Obtener de MySQL
            query = """
                SELECT id_producto, nombre, descripcion, precio, categoria,
                       equipo, liga, temporada, imagen_url, activo, fecha_creacion
                FROM Productos
                WHERE id_producto = %s
            """
            result = self.mysql_db.execute_query(query, (id_producto,))
            
            if not result:
                return None
            
            producto_data = result[0]
            
            # Obtener inventario de MongoDB
            inventario_doc = self.mongo_db.find_one(
                'inventario',
                {'producto_id': id_producto}
            )
            
            if inventario_doc and 'inventario' in inventario_doc:
                producto_data['inventario'] = inventario_doc['inventario']
            
            return Producto.from_dict(producto_data)
            
        except Exception as e:
            print(f"Error al obtener producto: {str(e)}")
            return None
    
    def obtener_todos(self, 
                      categoria: Optional[str] = None,
                      solo_activos: bool = True,
                      con_stock: bool = False) -> List[Producto]:
        """
        Obtiene todos los productos con filtros opcionales
        
        Args:
            categoria: Filtrar por categoría
            solo_activos: Solo productos activos
            con_stock: Solo productos con stock disponible
            
        Returns:
            Lista de productos
        """
        try:
            # Construir query base
            query = """
                SELECT id_producto, nombre, descripcion, precio, categoria,
                       equipo, liga, temporada, imagen_url, activo, fecha_creacion
                FROM Productos
                WHERE 1=1
            """
            params = []
            
            if solo_activos:
                query += " AND activo = TRUE"
            
            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)
            
            query += " ORDER BY fecha_creacion DESC"
            
            # Ejecutar query
            results = self.mysql_db.execute_query(query, tuple(params) if params else None)
            
            if not results:
                return []
            
            # Agregar inventario de MongoDB
            productos = []
            for row in results:
                producto_data = row
                
                inventario_doc = self.mongo_db.find_one(
                    'inventario',
                    {'producto_id': row['id_producto']}
                )
                
                if inventario_doc and 'inventario' in inventario_doc:
                    producto_data['inventario'] = inventario_doc['inventario']
                
                producto = Producto.from_dict(producto_data)
                
                # Filtrar por stock si es necesario
                if con_stock and producto.get_stock_total() == 0:
                    continue
                
                productos.append(producto)
            
            return productos
            
        except Exception as e:
            print(f"Error al obtener productos: {str(e)}")
            return []
    
    def actualizar(self, producto: Producto) -> bool:
        """
        Actualiza un producto existente
        
        Args:
            producto: Objeto Producto con los datos actualizados
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Actualizar en MySQL
            query = """
                UPDATE Productos
                SET nombre = %s, descripcion = %s, precio = %s, categoria = %s,
                    equipo = %s, liga = %s, temporada = %s, imagen_url = %s, activo = %s
                WHERE id_producto = %s
            """
            params = (
                producto.nombre,
                producto.descripcion,
                producto.precio,
                producto.categoria,
                producto.equipo,
                producto.liga,
                producto.temporada,
                producto.imagen_url,
                producto.activo,
                producto.id_producto
            )
            
            self.mysql_db.execute_query(query, params, fetch=False)
            
            # Actualizar inventario en MongoDB
            self.mongo_db.update_one(
                'inventario',
                {'producto_id': producto.id_producto},
                {'$set': {'inventario': producto.inventario}}
            )
            
            return True
            
        except Exception as e:
            print(f"Error al actualizar producto: {str(e)}")
            return False
    
    def actualizar_stock(self, id_producto: int, talla: str, cantidad: int) -> bool:
        """
        Actualiza el stock de un producto en MongoDB
        
        Args:
            id_producto: ID del producto
            talla: Talla a actualizar
            cantidad: Nueva cantidad
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            self.mongo_db.update_one(
                'inventario',
                {'producto_id': id_producto},
                {'$set': {f'inventario.{talla}': cantidad}}
            )
            return True
            
        except Exception as e:
            print(f"Error al actualizar stock: {str(e)}")
            return False
    
    def reducir_stock(self, id_producto: int, talla: str, cantidad: int) -> bool:
        """
        Reduce el stock de un producto
        
        Args:
            id_producto: ID del producto
            talla: Talla a reducir
            cantidad: Cantidad a reducir
            
        Returns:
            True si se redujo correctamente, False si no hay stock suficiente
        """
        try:
            producto = self.obtener_por_id(id_producto)
            if not producto or not producto.tiene_stock(talla, cantidad):
                return False
            
            nueva_cantidad = producto.inventario[talla] - cantidad
            return self.actualizar_stock(id_producto, talla, nueva_cantidad)
            
        except Exception as e:
            print(f"Error al reducir stock: {str(e)}")
            return False
    
    def eliminar(self, id_producto: int) -> bool:
        """
        Elimina (desactiva) un producto
        
        Args:
            id_producto: ID del producto a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            query = "UPDATE Productos SET activo = FALSE WHERE id_producto = %s"
            self.mysql_db.execute_query(query, (id_producto,), fetch=False)
            return True
            
        except Exception as e:
            print(f"Error al eliminar producto: {str(e)}")
            return False
