"""
Repositorios - Patrón Repository para acceso a datos
Separa la lógica de acceso a datos de la lógica de negocio
"""

from .usuario_repository import UsuarioRepository
from .producto_repository import ProductoRepository
from .pedido_repository import PedidoRepository

__all__ = [
    'UsuarioRepository',
    'ProductoRepository',
    'PedidoRepository'
]
