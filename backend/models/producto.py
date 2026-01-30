"""
Modelo Producto - Representa un producto del catálogo
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class Producto:
    """Clase que representa un producto del catálogo"""
    
    id_producto: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    precio: float = 0.0
    categoria: str = ""
    equipo: Optional[str] = None
    liga: Optional[str] = None
    temporada: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: bool = True
    fecha_creacion: Optional[datetime] = None
    
    # Inventario (desde MongoDB)
    inventario: Dict[str, int] = field(default_factory=lambda: {'S': 0, 'M': 0, 'L': 0, 'XL': 0})
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now()
    
    def tiene_stock(self, talla: str = 'M', cantidad: int = 1) -> bool:
        """
        Verifica si hay stock disponible
        
        Args:
            talla: Talla del producto
            cantidad: Cantidad solicitada
            
        Returns:
            True si hay stock suficiente, False en caso contrario
        """
        return self.inventario.get(talla, 0) >= cantidad
    
    def get_stock_total(self) -> int:
        """Obtiene el stock total de todas las tallas"""
        return sum(self.inventario.values())
    
    def reducir_stock(self, talla: str, cantidad: int) -> bool:
        """
        Reduce el stock de una talla específica
        
        Args:
            talla: Talla a reducir
            cantidad: Cantidad a reducir
            
        Returns:
            True si se pudo reducir, False si no hay stock suficiente
        """
        if self.tiene_stock(talla, cantidad):
            self.inventario[talla] -= cantidad
            return True
        return False
    
    def aumentar_stock(self, talla: str, cantidad: int) -> None:
        """
        Aumenta el stock de una talla específica
        
        Args:
            talla: Talla a aumentar
            cantidad: Cantidad a aumentar
        """
        if talla in self.inventario:
            self.inventario[talla] += cantidad
        else:
            self.inventario[talla] = cantidad
    
    def calcular_precio_con_descuento(self, descuento: float = 0.0) -> float:
        """
        Calcula el precio con descuento aplicado
        
        Args:
            descuento: Porcentaje de descuento (0-100)
            
        Returns:
            Precio con descuento
        """
        return self.precio * (1 - descuento / 100)
    
    def to_dict(self) -> dict:
        """Convierte el producto a diccionario"""
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'categoria': self.categoria,
            'equipo': self.equipo,
            'liga': self.liga,
            'temporada': self.temporada,
            'imagen_url': self.imagen_url,
            'activo': self.activo,
            'inventario': self.inventario,
            'stock_total': self.get_stock_total(),
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Producto':
        """
        Crea un producto desde un diccionario
        
        Args:
            data: Diccionario con los datos del producto
            
        Returns:
            Instancia de Producto
        """
        return cls(
            id_producto=data.get('id_producto'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            precio=float(data.get('precio', 0.0)),
            categoria=data.get('categoria', ''),
            equipo=data.get('equipo'),
            liga=data.get('liga'),
            temporada=data.get('temporada'),
            imagen_url=data.get('imagen_url'),
            activo=data.get('activo', True),
            inventario=data.get('inventario', {'S': 0, 'M': 0, 'L': 0, 'XL': 0}),
            fecha_creacion=data.get('fecha_creacion')
        )
    
    def __repr__(self) -> str:
        return f"<Producto(id={self.id_producto}, nombre={self.nombre}, precio={self.precio})>"
