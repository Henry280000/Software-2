"""
Servicio de Pedidos - Lógica de negocio para pedidos
Integra Repository, Factory y Observer
"""

from typing import Optional, List
from models.pedido import Pedido, EstadoPedido
from models.carrito import Carrito
from models.usuario import Usuario
from repositories.pedido_repository import PedidoRepository
from repositories.producto_repository import ProductoRepository
from services.pedido_factory import PedidoFactory
from services.notification_service import NotificationService, TipoEvento


class PedidoService:
    """
    Servicio que gestiona la lógica de negocio de pedidos
    Coordina Repository, Factory y notificaciones
    """
    
    def __init__(self):
        """Inicializa el servicio con sus dependencias"""
        self.pedido_repo = PedidoRepository()
        self.producto_repo = ProductoRepository()
        self.notification_service = NotificationService()
    
    def crear_pedido_desde_carrito(self, carrito: Carrito, usuario: Usuario,
                                   direccion_envio: str = None,
                                   telefono_contacto: str = None,
                                   notas: str = None) -> Optional[int]:
        """
        Crea un pedido desde un carrito de compras
        
        Args:
            carrito: Carrito con productos
            usuario: Usuario que realiza el pedido
            direccion_envio: Dirección de envío (opcional)
            telefono_contacto: Teléfono de contacto (opcional)
            notas: Notas adicionales
            
        Returns:
            ID del pedido creado o None si hay error
        """
        try:
            # Validar stock antes de crear el pedido
            validacion = carrito.validar_stock()
            if not all(validacion.values()):
                print("Error: No hay suficiente stock para algunos productos")
                return None
            
            # Usar Factory para crear el pedido
            pedido = PedidoFactory.crear_desde_carrito(
                carrito=carrito,
                usuario=usuario,
                direccion_envio=direccion_envio,
                telefono_contacto=telefono_contacto,
                notas=notas
            )
            
            # Guardar en la base de datos
            pedido_id = self.pedido_repo.crear(pedido)
            
            if pedido_id:
                # Reducir stock de los productos
                for item in carrito.items:
                    self.producto_repo.reducir_stock(
                        id_producto=item.producto.id_producto,
                        talla=item.talla,
                        cantidad=item.cantidad
                    )
                
                # Notificar evento (Patrón Observer)
                self.notification_service.notify(
                    TipoEvento.PEDIDO_CREADO,
                    {
                        'id_pedido': pedido_id,
                        'id_usuario': usuario.id_usuario,
                        'email': usuario.email,
                        'total': pedido.total,
                        'cantidad_productos': pedido.get_cantidad_productos(),
                        'mensaje': f'Nuevo pedido #{pedido_id} creado para {usuario.nombre}'
                    }
                )
                
                return pedido_id
            
            return None
            
        except Exception as e:
            print(f"Error al crear pedido: {str(e)}")
            return None
    
    def obtener_pedido(self, id_pedido: int) -> Optional[Pedido]:
        """
        Obtiene un pedido por su ID
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            Objeto Pedido o None
        """
        return self.pedido_repo.obtener_por_id(id_pedido)
    
    def obtener_pedidos_usuario(self, id_usuario: int) -> List[Pedido]:
        """
        Obtiene todos los pedidos de un usuario
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Lista de pedidos
        """
        return self.pedido_repo.obtener_por_usuario(id_usuario)
    
    def obtener_todos_pedidos(self, estado: Optional[EstadoPedido] = None) -> List[Pedido]:
        """
        Obtiene todos los pedidos, opcionalmente filtrados por estado
        
        Args:
            estado: Estado del pedido para filtrar
            
        Returns:
            Lista de pedidos
        """
        return self.pedido_repo.obtener_todos(estado)
    
    def actualizar_estado_pedido(self, id_pedido: int, 
                                 nuevo_estado: EstadoPedido,
                                 notificar_usuario: bool = True) -> bool:
        """
        Actualiza el estado de un pedido y notifica el cambio
        
        Args:
            id_pedido: ID del pedido
            nuevo_estado: Nuevo estado del pedido
            notificar_usuario: Si se debe notificar al usuario
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Obtener pedido actual
            pedido = self.pedido_repo.obtener_por_id(id_pedido)
            if not pedido:
                print("Pedido no encontrado")
                return False
            
            # Validar transición de estado
            if not pedido.cambiar_estado(nuevo_estado):
                print(f"Transición de estado inválida: {pedido.estado.value} -> {nuevo_estado.value}")
                return False
            
            # Actualizar en base de datos
            if self.pedido_repo.actualizar_estado(id_pedido, nuevo_estado):
                # Notificar evento
                self.notification_service.notify(
                    TipoEvento.PEDIDO_ACTUALIZADO,
                    {
                        'id_pedido': id_pedido,
                        'estado_anterior': pedido.estado.value,
                        'estado_nuevo': nuevo_estado.value,
                        'id_usuario': pedido.id_usuario,
                        'mensaje': f'Pedido #{id_pedido} actualizado a {nuevo_estado.value}'
                    }
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error al actualizar estado del pedido: {str(e)}")
            return False
    
    def cancelar_pedido(self, id_pedido: int) -> bool:
        """
        Cancela un pedido y restaura el stock
        
        Args:
            id_pedido: ID del pedido a cancelar
            
        Returns:
            True si se canceló correctamente
        """
        try:
            # Obtener pedido
            pedido = self.pedido_repo.obtener_por_id(id_pedido)
            if not pedido:
                return False
            
            # Verificar si puede cancelarse
            if not pedido.puede_cancelarse():
                print(f"El pedido no puede cancelarse en estado: {pedido.estado.value}")
                return False
            
            # Restaurar stock
            for detalle in pedido.detalles:
                producto = self.producto_repo.obtener_por_id(detalle.id_producto)
                if producto:
                    producto.aumentar_stock(detalle.talla, detalle.cantidad)
                    self.producto_repo.actualizar(producto)
            
            # Actualizar estado a cancelado
            if self.pedido_repo.actualizar_estado(id_pedido, EstadoPedido.CANCELADO):
                # Notificar evento
                self.notification_service.notify(
                    TipoEvento.PEDIDO_CANCELADO,
                    {
                        'id_pedido': id_pedido,
                        'id_usuario': pedido.id_usuario,
                        'total_reembolso': pedido.total,
                        'mensaje': f'Pedido #{id_pedido} cancelado. Stock restaurado.'
                    }
                )
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error al cancelar pedido: {str(e)}")
            return False
    
    def verificar_stock_productos(self, pedido: Pedido) -> bool:
        """
        Verifica que haya stock suficiente para todos los productos del pedido
        
        Args:
            pedido: Pedido a verificar
            
        Returns:
            True si hay stock suficiente para todos los productos
        """
        for detalle in pedido.detalles:
            producto = self.producto_repo.obtener_por_id(detalle.id_producto)
            if not producto or not producto.tiene_stock(detalle.talla, detalle.cantidad):
                return False
        return True
