"""
Repository de Usuario - Maneja el acceso a datos de usuarios
"""

from typing import Optional, List
from models.usuario import Usuario
from db_mysql import MySQLConnection


class UsuarioRepository:
    """Repository para operaciones CRUD de usuarios"""
    
    def __init__(self):
        """Inicializa el repository con la conexión a MySQL"""
        self.db = MySQLConnection()
    
    def crear(self, usuario: Usuario) -> Optional[int]:
        """
        Crea un nuevo usuario en la base de datos
        
        Args:
            usuario: Objeto Usuario a crear
            
        Returns:
            ID del usuario creado o None si hay error
        """
        try:
            query = """
                INSERT INTO Usuarios (nombre, email, password_hash, telefono, direccion, rol, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                usuario.nombre,
                usuario.email,
                usuario.password_hash,
                usuario.telefono,
                usuario.direccion,
                usuario.rol,
                usuario.activo
            )
            
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            
            user_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            return user_id
            
        except Exception as e:
            print(f"Error al crear usuario: {str(e)}")
            return None
    
    def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Objeto Usuario o None si no se encuentra
        """
        try:
            query = """
                SELECT id_usuario, nombre, email, password_hash, telefono, 
                       direccion, rol, activo, fecha_registro
                FROM Usuarios
                WHERE id_usuario = %s
            """
            result = self.db.execute_query(query, (id_usuario,))
            
            if result:
                return Usuario.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error al obtener usuario: {str(e)}")
            return None
    
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por su email
        
        Args:
            email: Email del usuario
            
        Returns:
            Objeto Usuario o None si no se encuentra
        """
        try:
            query = """
                SELECT id_usuario, nombre, email, password_hash, telefono, 
                       direccion, rol, activo, fecha_registro
                FROM Usuarios
                WHERE email = %s
            """
            result = self.db.execute_query(query, (email,))
            
            if result:
                return Usuario.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error al obtener usuario por email: {str(e)}")
            return None
    
    def obtener_todos(self, solo_activos: bool = True) -> List[Usuario]:
        """
        Obtiene todos los usuarios
        
        Args:
            solo_activos: Si True, solo retorna usuarios activos
            
        Returns:
            Lista de usuarios
        """
        try:
            if solo_activos:
                query = """
                    SELECT id_usuario, nombre, email, password_hash, telefono, 
                           direccion, rol, activo, fecha_registro
                    FROM Usuarios
                    WHERE activo = TRUE
                    ORDER BY fecha_registro DESC
                """
            else:
                query = """
                    SELECT id_usuario, nombre, email, password_hash, telefono, 
                           direccion, rol, activo, fecha_registro
                    FROM Usuarios
                    ORDER BY fecha_registro DESC
                """
            
            results = self.db.execute_query(query)
            return [Usuario.from_dict(row) for row in results] if results else []
            
        except Exception as e:
            print(f"Error al obtener usuarios: {str(e)}")
            return []
    
    def actualizar(self, usuario: Usuario) -> bool:
        """
        Actualiza un usuario existente
        
        Args:
            usuario: Objeto Usuario con los datos actualizados
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            query = """
                UPDATE Usuarios
                SET nombre = %s, email = %s, telefono = %s, 
                    direccion = %s, rol = %s, activo = %s
                WHERE id_usuario = %s
            """
            params = (
                usuario.nombre,
                usuario.email,
                usuario.telefono,
                usuario.direccion,
                usuario.rol,
                usuario.activo,
                usuario.id_usuario
            )
            
            self.db.execute_query(query, params, fetch=False)
            return True
            
        except Exception as e:
            print(f"Error al actualizar usuario: {str(e)}")
            return False
    
    def eliminar(self, id_usuario: int) -> bool:
        """
        Elimina (desactiva) un usuario
        
        Args:
            id_usuario: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            query = "UPDATE Usuarios SET activo = FALSE WHERE id_usuario = %s"
            self.db.execute_query(query, (id_usuario,), fetch=False)
            return True
            
        except Exception as e:
            print(f"Error al eliminar usuario: {str(e)}")
            return False
    
    def email_existe(self, email: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si un email ya existe en la base de datos
        
        Args:
            email: Email a verificar
            excluir_id: ID de usuario a excluir de la búsqueda (útil para actualizaciones)
            
        Returns:
            True si el email existe, False en caso contrario
        """
        try:
            if excluir_id:
                query = "SELECT COUNT(*) as count FROM Usuarios WHERE email = %s AND id_usuario != %s"
                result = self.db.execute_query(query, (email, excluir_id))
            else:
                query = "SELECT COUNT(*) as count FROM Usuarios WHERE email = %s"
                result = self.db.execute_query(query, (email,))
            
            return result[0]['count'] > 0 if result else False
            
        except Exception as e:
            print(f"Error al verificar email: {str(e)}")
            return False
