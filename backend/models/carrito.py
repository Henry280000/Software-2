"""
Modelo Carrito - Representa el carrito de compras
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .producto import Producto


@dataclass
class CarritoItem:
    """Representa un item en el carrito"""
    
    producto: Producto
    talla: str = 'M'
    cantidad: int = 1
    
    def get_subtotal(self) -> float:
        """Calcula el subtotal del item"""
        return self.producto.precio * self.cantidad
    
    def to_dict(self) -> dict:
        """Convierte el item a diccionario"""
        return {
            'producto': self.producto.to_dict(),
            'talla': self.talla,
            'cantidad': self.cantidad,
            'subtotal': self.get_subtotal()
        }
    
    def __repr__(self) -> str:
        return f"<CarritoItem(producto={self.producto.nombre}, talla={self.talla}, cantidad={self.cantidad})>"


@dataclass
class Carrito:
    """Clase que representa un carrito de compras"""
    
    id_usuario: Optional[int] = None
    items: List[CarritoItem] = field(default_factory=list)
    
    def agregar_producto(self, producto: Producto, talla: str = 'M', cantidad: int = 1) -> bool:
        """
        Agrega un producto al carrito
        
        Args:
            producto: Producto a agregar
            talla: Talla del producto
            cantidad: Cantidad a agregar
            
        Returns:
            True si se agregó correctamente, False si no hay stock
        """
        # Verificar stock
        if not producto.tiene_stock(talla, cantidad):
            return False
        
        # Buscar si ya existe el producto con esa talla
        for item in self.items:
            if item.producto.id_producto == producto.id_producto and item.talla == talla:
                item.cantidad += cantidad
                return True
        
        # Si no existe, crear nuevo item
        nuevo_item = CarritoItem(producto=producto, talla=talla, cantidad=cantidad)
        self.items.append(nuevo_item)
        return True
    
    def eliminar_producto(self, id_producto: int, talla: str) -> bool:
        """
        Elimina un producto del carrito
        
        Args:
            id_producto: ID del producto
            talla: Talla del producto
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        for i, item in enumerate(self.items):
            if item.producto.id_producto == id_producto and item.talla == talla:
                self.items.pop(i)
                return True
        return False
    
    def actualizar_cantidad(self, id_producto: int, talla: str, nueva_cantidad: int) -> bool:
        """
        Actualiza la cantidad de un producto en el carrito
        
        Args:
            id_producto: ID del producto
            talla: Talla del producto
            nueva_cantidad: Nueva cantidad
            
        Returns:
            True si se actualizó, False si no se encontró o no hay stock
        """
        for item in self.items:
            if item.producto.id_producto == id_producto and item.talla == talla:
                if item.producto.tiene_stock(talla, nueva_cantidad):
                    item.cantidad = nueva_cantidad
                    return True
                return False
        return False
    
    def vaciar(self) -> None:
        """Vacía el carrito"""
        self.items.clear()
    
    def get_total_items(self) -> int:
        """Obtiene el número total de items en el carrito"""
        return sum(item.cantidad for item in self.items)
    
    def get_total(self) -> float:
        """Calcula el total del carrito"""
        return sum(item.get_subtotal() for item in self.items)
    
    def esta_vacio(self) -> bool:
        """Verifica si el carrito está vacío"""
        return len(self.items) == 0
    
    def validar_stock(self) -> Dict[str, bool]:
        """
        Valida que todos los productos tengan stock disponible
        
        Returns:
            Diccionario con el resultado de validación por producto
        """
        resultados = {}
        for item in self.items:
            key = f"{item.producto.id_producto}_{item.talla}"
            resultados[key] = item.producto.tiene_stock(item.talla, item.cantidad)
        return resultados
    
    def to_dict(self) -> dict:
        """Convierte el carrito a diccionario"""
        return {
            'id_usuario': self.id_usuario,
            'items': [item.to_dict() for item in self.items],
            'total_items': self.get_total_items(),
            'total': self.get_total(),
            'vacio': self.esta_vacio()
        }
    
    def __repr__(self) -> str:
        return f"<Carrito(usuario={self.id_usuario}, items={len(self.items)}, total={self.get_total()})>"
