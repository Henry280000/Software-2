"""
Modelo Pedido - Representa un pedido del sistema
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class EstadoPedido(Enum):
    """Estados posibles de un pedido"""
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    EN_PROCESO = "EN_PROCESO"
    ENVIADO = "ENVIADO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


@dataclass
class DetallePedido:
    """Representa el detalle de un producto en un pedido"""
    
    id_detalle: Optional[int] = None
    id_pedido: Optional[int] = None
    id_producto: int = 0
    nombre_producto: str = ""
    talla: str = 'M'
    cantidad: int = 1
    precio_unitario: float = 0.0
    
    def get_subtotal(self) -> float:
        """Calcula el subtotal del detalle"""
        return self.precio_unitario * self.cantidad
    
    def to_dict(self) -> dict:
        """Convierte el detalle a diccionario"""
        return {
            'id_detalle': self.id_detalle,
            'id_pedido': self.id_pedido,
            'id_producto': self.id_producto,
            'nombre_producto': self.nombre_producto,
            'talla': self.talla,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.get_subtotal()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DetallePedido':
        """Crea un detalle desde un diccionario"""
        return cls(
            id_detalle=data.get('id_detalle'),
            id_pedido=data.get('id_pedido'),
            id_producto=data.get('id_producto', 0),
            nombre_producto=data.get('nombre_producto', ''),
            talla=data.get('talla', 'M'),
            cantidad=data.get('cantidad', 1),
            precio_unitario=float(data.get('precio_unitario', 0.0))
        )


@dataclass
class Pedido:
    """Clase que representa un pedido"""
    
    id_pedido: Optional[int] = None
    id_usuario: int = 0
    fecha_pedido: Optional[datetime] = None
    estado: EstadoPedido = EstadoPedido.PENDIENTE
    total: float = 0.0
    direccion_envio: Optional[str] = None
    telefono_contacto: Optional[str] = None
    notas: Optional[str] = None
    detalles: List[DetallePedido] = field(default_factory=list)
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_pedido is None:
            self.fecha_pedido = datetime.now()
    
    def agregar_detalle(self, detalle: DetallePedido) -> None:
        """Agrega un detalle al pedido"""
        self.detalles.append(detalle)
        self.recalcular_total()
    
    def recalcular_total(self) -> None:
        """Recalcula el total del pedido"""
        self.total = sum(detalle.get_subtotal() for detalle in self.detalles)
    
    def cambiar_estado(self, nuevo_estado: EstadoPedido) -> bool:
        """
        Cambia el estado del pedido
        
        Args:
            nuevo_estado: Nuevo estado del pedido
            
        Returns:
            True si el cambio es válido, False en caso contrario
        """
        # Validar transiciones de estado
        transiciones_validas = {
            EstadoPedido.PENDIENTE: [EstadoPedido.CONFIRMADO, EstadoPedido.CANCELADO],
            EstadoPedido.CONFIRMADO: [EstadoPedido.EN_PROCESO, EstadoPedido.CANCELADO],
            EstadoPedido.EN_PROCESO: [EstadoPedido.ENVIADO, EstadoPedido.CANCELADO],
            EstadoPedido.ENVIADO: [EstadoPedido.ENTREGADO],
            EstadoPedido.ENTREGADO: [],
            EstadoPedido.CANCELADO: []
        }
        
        if nuevo_estado in transiciones_validas.get(self.estado, []):
            self.estado = nuevo_estado
            return True
        return False
    
    def puede_cancelarse(self) -> bool:
        """Verifica si el pedido puede cancelarse"""
        return self.estado in [EstadoPedido.PENDIENTE, EstadoPedido.CONFIRMADO, EstadoPedido.EN_PROCESO]
    
    def esta_completado(self) -> bool:
        """Verifica si el pedido está completado"""
        return self.estado in [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]
    
    def get_cantidad_productos(self) -> int:
        """Obtiene la cantidad total de productos"""
        return sum(detalle.cantidad for detalle in self.detalles)
    
    def to_dict(self) -> dict:
        """Convierte el pedido a diccionario"""
        return {
            'id_pedido': self.id_pedido,
            'id_usuario': self.id_usuario,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'estado': self.estado.value if isinstance(self.estado, EstadoPedido) else self.estado,
            'total': self.total,
            'direccion_envio': self.direccion_envio,
            'telefono_contacto': self.telefono_contacto,
            'notas': self.notas,
            'detalles': [detalle.to_dict() for detalle in self.detalles],
            'cantidad_productos': self.get_cantidad_productos()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Pedido':
        """Crea un pedido desde un diccionario"""
        estado = data.get('estado', 'PENDIENTE')
        if isinstance(estado, str):
            estado = EstadoPedido[estado]
        
        detalles = []
        if 'detalles' in data:
            detalles = [DetallePedido.from_dict(d) for d in data['detalles']]
        
        return cls(
            id_pedido=data.get('id_pedido'),
            id_usuario=data.get('id_usuario', 0),
            fecha_pedido=data.get('fecha_pedido'),
            estado=estado,
            total=float(data.get('total', 0.0)),
            direccion_envio=data.get('direccion_envio'),
            telefono_contacto=data.get('telefono_contacto'),
            notas=data.get('notas'),
            detalles=detalles
        )
    
    def __repr__(self) -> str:
        return f"<Pedido(id={self.id_pedido}, usuario={self.id_usuario}, estado={self.estado.value}, total={self.total})>"
