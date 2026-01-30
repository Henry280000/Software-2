"""
Repository de Pedido - Maneja el acceso a datos de pedidos
"""

from typing import Optional, List
from models.pedido import Pedido, DetallePedido, EstadoPedido
from db_mysql import MySQLConnection


class PedidoRepository:
    """Repository para operaciones CRUD de pedidos"""
    
    def __init__(self):
        """Inicializa el repository con la conexión a MySQL"""
        self.db = MySQLConnection()
    
    def crear(self, pedido: Pedido) -> Optional[int]:
        """
        Crea un nuevo pedido con sus detalles (transacción)
        
        Args:
            pedido: Objeto Pedido a crear
            
        Returns:
            ID del pedido creado o None si hay error
        """
        try:
            # Insertar pedido
            query_pedido = """
                INSERT INTO Pedidos (id_usuario, total, direccion_envio, telefono_contacto, notas, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params_pedido = (
                pedido.id_usuario,
                pedido.total,
                pedido.direccion_envio,
                pedido.telefono_contacto,
                pedido.notas,
                pedido.estado.value if isinstance(pedido.estado, EstadoPedido) else pedido.estado
            )
            
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query_pedido, params_pedido)
            
            pedido_id = cursor.lastrowid
            
            # Insertar detalles
            query_detalle = """
                INSERT INTO Detalles_Pedido (id_pedido, id_producto, talla, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for detalle in pedido.detalles:
                params_detalle = (
                    pedido_id,
                    detalle.id_producto,
                    detalle.talla,
                    detalle.cantidad,
                    detalle.precio_unitario
                )
                cursor.execute(query_detalle, params_detalle)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return pedido_id
            
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error al crear pedido: {str(e)}")
            return None
    
    def obtener_por_id(self, id_pedido: int) -> Optional[Pedido]:
        """
        Obtiene un pedido completo con sus detalles
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            Objeto Pedido o None si no se encuentra
        """
        try:
            # Obtener pedido
            query_pedido = """
                SELECT id_pedido, id_usuario, fecha_pedido, estado, total,
                       direccion_envio, telefono_contacto, notas
                FROM Pedidos
                WHERE id_pedido = %s
            """
            result = self.db.execute_query(query_pedido, (id_pedido,))
            
            if not result:
                return None
            
            pedido_data = result[0]
            
            # Obtener detalles
            query_detalles = """
                SELECT d.id_detalle, d.id_pedido, d.id_producto, d.talla, 
                       d.cantidad, d.precio_unitario, p.nombre as nombre_producto
                FROM Detalles_Pedido d
                JOIN Productos p ON d.id_producto = p.id_producto
                WHERE d.id_pedido = %s
            """
            detalles_result = self.db.execute_query(query_detalles, (id_pedido,))
            
            detalles = []
            if detalles_result:
                detalles = [DetallePedido.from_dict(row) for row in detalles_result]
            
            pedido_data['detalles'] = detalles
            return Pedido.from_dict(pedido_data)
            
        except Exception as e:
            print(f"Error al obtener pedido: {str(e)}")
            return None
    
    def obtener_por_usuario(self, id_usuario: int) -> List[Pedido]:
        """
        Obtiene todos los pedidos de un usuario
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Lista de pedidos
        """
        try:
            query = """
                SELECT id_pedido, id_usuario, fecha_pedido, estado, total,
                       direccion_envio, telefono_contacto, notas
                FROM Pedidos
                WHERE id_usuario = %s
                ORDER BY fecha_pedido DESC
            """
            results = self.db.execute_query(query, (id_usuario,))
            
            if not results:
                return []
            
            pedidos = []
            for row in results:
                # Obtener detalles de cada pedido
                query_detalles = """
                    SELECT d.id_detalle, d.id_pedido, d.id_producto, d.talla, 
                           d.cantidad, d.precio_unitario, p.nombre as nombre_producto
                    FROM Detalles_Pedido d
                    JOIN Productos p ON d.id_producto = p.id_producto
                    WHERE d.id_pedido = %s
                """
                detalles_result = self.db.execute_query(query_detalles, (row['id_pedido'],))
                
                detalles = []
                if detalles_result:
                    detalles = [DetallePedido.from_dict(d) for d in detalles_result]
                
                row['detalles'] = detalles
                pedidos.append(Pedido.from_dict(row))
            
            return pedidos
            
        except Exception as e:
            print(f"Error al obtener pedidos del usuario: {str(e)}")
            return []
    
    def obtener_todos(self, estado: Optional[EstadoPedido] = None) -> List[Pedido]:
        """
        Obtiene todos los pedidos, opcionalmente filtrados por estado
        
        Args:
            estado: Estado del pedido para filtrar
            
        Returns:
            Lista de pedidos
        """
        try:
            query = """
                SELECT id_pedido, id_usuario, fecha_pedido, estado, total,
                       direccion_envio, telefono_contacto, notas
                FROM Pedidos
            """
            params = None
            
            if estado:
                query += " WHERE estado = %s"
                params = (estado.value if isinstance(estado, EstadoPedido) else estado,)
            
            query += " ORDER BY fecha_pedido DESC"
            
            results = self.db.execute_query(query, params)
            
            if not results:
                return []
            
            pedidos = []
            for row in results:
                # Obtener detalles de cada pedido
                query_detalles = """
                    SELECT d.id_detalle, d.id_pedido, d.id_producto, d.talla, 
                           d.cantidad, d.precio_unitario, p.nombre as nombre_producto
                    FROM Detalles_Pedido d
                    JOIN Productos p ON d.id_producto = p.id_producto
                    WHERE d.id_pedido = %s
                """
                detalles_result = self.db.execute_query(query_detalles, (row['id_pedido'],))
                
                detalles = []
                if detalles_result:
                    detalles = [DetallePedido.from_dict(d) for d in detalles_result]
                
                row['detalles'] = detalles
                pedidos.append(Pedido.from_dict(row))
            
            return pedidos
            
        except Exception as e:
            print(f"Error al obtener pedidos: {str(e)}")
            return []
    
    def actualizar_estado(self, id_pedido: int, nuevo_estado: EstadoPedido) -> bool:
        """
        Actualiza el estado de un pedido
        
        Args:
            id_pedido: ID del pedido
            nuevo_estado: Nuevo estado del pedido
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            query = "UPDATE Pedidos SET estado = %s WHERE id_pedido = %s"
            estado_value = nuevo_estado.value if isinstance(nuevo_estado, EstadoPedido) else nuevo_estado
            self.db.execute_query(query, (estado_value, id_pedido), fetch=False)
            return True
            
        except Exception as e:
            print(f"Error al actualizar estado del pedido: {str(e)}")
            return False
