"""
Patrón Factory - Crea objetos Pedido de diferentes tipos
"""

from typing import Dict, List
from models.pedido import Pedido, DetallePedido, EstadoPedido
from models.carrito import Carrito
from models.usuario import Usuario


class PedidoFactory:
    """
    Factory para crear diferentes tipos de pedidos
    Implementa el patrón Factory Method
    """
    
    @staticmethod
    def crear_desde_carrito(carrito: Carrito, usuario: Usuario, 
                           direccion_envio: str = None,
                           telefono_contacto: str = None,
                           notas: str = None) -> Pedido:
        """
        Crea un pedido desde un carrito de compras
        
        Args:
            carrito: Carrito con los productos
            usuario: Usuario que realiza el pedido
            direccion_envio: Dirección de envío (opcional, usa la del usuario por defecto)
            telefono_contacto: Teléfono de contacto (opcional, usa el del usuario por defecto)
            notas: Notas adicionales
            
        Returns:
            Objeto Pedido creado
        """
        # Crear detalles desde el carrito
        detalles = []
        for item in carrito.items:
            detalle = DetallePedido(
                id_producto=item.producto.id_producto,
                nombre_producto=item.producto.nombre,
                talla=item.talla,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            detalles.append(detalle)
        
        # Crear pedido
        pedido = Pedido(
            id_usuario=usuario.id_usuario,
            estado=EstadoPedido.PENDIENTE,
            total=carrito.get_total(),
            direccion_envio=direccion_envio or usuario.direccion,
            telefono_contacto=telefono_contacto or usuario.telefono,
            notas=notas,
            detalles=detalles
        )
        
        return pedido
    
    @staticmethod
    def crear_pedido_express(id_usuario: int, id_producto: int, 
                            nombre_producto: str, talla: str, 
                            cantidad: int, precio_unitario: float,
                            direccion_envio: str, telefono_contacto: str) -> Pedido:
        """
        Crea un pedido express (compra directa de un producto)
        
        Args:
            id_usuario: ID del usuario
            id_producto: ID del producto
            nombre_producto: Nombre del producto
            talla: Talla seleccionada
            cantidad: Cantidad
            precio_unitario: Precio unitario
            direccion_envio: Dirección de envío
            telefono_contacto: Teléfono de contacto
            
        Returns:
            Objeto Pedido creado
        """
        detalle = DetallePedido(
            id_producto=id_producto,
            nombre_producto=nombre_producto,
            talla=talla,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        
        total = precio_unitario * cantidad
        
        pedido = Pedido(
            id_usuario=id_usuario,
            estado=EstadoPedido.PENDIENTE,
            total=total,
            direccion_envio=direccion_envio,
            telefono_contacto=telefono_contacto,
            detalles=[detalle]
        )
        
        return pedido
    
    @staticmethod
    def crear_pedido_personalizado(id_usuario: int, 
                                   items: List[Dict],
                                   direccion_envio: str,
                                   telefono_contacto: str,
                                   notas: str = None) -> Pedido:
        """
        Crea un pedido personalizado desde una lista de items
        
        Args:
            id_usuario: ID del usuario
            items: Lista de diccionarios con datos de productos
            direccion_envio: Dirección de envío
            telefono_contacto: Teléfono de contacto
            notas: Notas adicionales
            
        Returns:
            Objeto Pedido creado
        """
        detalles = []
        total = 0.0
        
        for item in items:
            detalle = DetallePedido(
                id_producto=item['id_producto'],
                nombre_producto=item['nombre_producto'],
                talla=item.get('talla', 'M'),
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario']
            )
            detalles.append(detalle)
            total += detalle.get_subtotal()
        
        pedido = Pedido(
            id_usuario=id_usuario,
            estado=EstadoPedido.PENDIENTE,
            total=total,
            direccion_envio=direccion_envio,
            telefono_contacto=telefono_contacto,
            notas=notas,
            detalles=detalles
        )
        
        return pedido
