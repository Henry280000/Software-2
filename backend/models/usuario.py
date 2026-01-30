"""
Modelo Usuario - Representa un usuario del sistema
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


@dataclass
class Usuario:
    """Clase que representa un usuario del sistema"""
    
    id_usuario: Optional[int] = None
    nombre: str = ""
    email: str = ""
    password_hash: str = ""
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    rol: str = "CLIENTE"
    activo: bool = True
    fecha_registro: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_registro is None:
            self.fecha_registro = datetime.now()
    
    def set_password(self, password: str) -> None:
        """
        Establece la contraseña del usuario (hasheada)
        
        Args:
            password: Contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Verifica si la contraseña es correcta
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            True si la contraseña es correcta, False en caso contrario
        """
        return check_password_hash(self.password_hash, password)
    
    def es_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == "ADMIN"
    
    def esta_activo(self) -> bool:
        """Verifica si el usuario está activo"""
        return self.activo
    
    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario"""
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """
        Crea un usuario desde un diccionario
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            Instancia de Usuario
        """
        return cls(
            id_usuario=data.get('id_usuario'),
            nombre=data.get('nombre', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            rol=data.get('rol', 'CLIENTE'),
            activo=data.get('activo', True),
            fecha_registro=data.get('fecha_registro')
        )
    
    def __repr__(self) -> str:
        return f"<Usuario(id={self.id_usuario}, email={self.email}, rol={self.rol})>"
