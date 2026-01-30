"""
Módulo de conexión a MySQL con patrón Singleton
"""

import mysql.connector
from mysql.connector import pooling
import os
from threading import Lock


class MySQLConnection:
    """
    Clase Singleton para manejar conexiones a MySQL
    Garantiza una única instancia de conexión en toda la aplicación
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Implementación del patrón Singleton con thread-safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MySQLConnection, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializar pool de conexiones a MySQL (solo una vez)"""
        if self._initialized:
            return
        
        self.pool = None
        self.connect()
        self._initialized = True
    
    def connect(self):
        """Crear pool de conexiones"""
        try:
            config = {
                'host': os.getenv('MYSQL_HOST', 'mysql_db'),
                'port': int(os.getenv('MYSQL_PORT', 3306)),
                'database': os.getenv('MYSQL_DATABASE', 'ecommerce_db'),
                'user': os.getenv('MYSQL_USER', 'ecommerce_user'),
                'password': os.getenv('MYSQL_PASSWORD', 'ecommerce_pass'),
                'pool_name': 'ecommerce_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                'autocommit': False
            }
            
            self.pool = pooling.MySQLConnectionPool(**config)
            print("✓ Conexión a MySQL establecida correctamente")
            
        except Exception as e:
            print(f"✗ Error al conectar con MySQL: {str(e)}")
            raise
    
    def get_connection(self):
        """Obtener conexión del pool"""
        try:
            return self.pool.get_connection()
        except Exception as e:
            print(f"Error al obtener conexión: {str(e)}")
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Ejecutar una query SQL
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros para la query (tupla)
            fetch: Si True, retorna resultados; si False, solo ejecuta
            
        Returns:
            Lista de diccionarios con los resultados (si fetch=True)
            None (si fetch=False)
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Si es una query de lectura
            if fetch and query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return results
            
            # Si es una query de escritura o stored procedure
            connection.commit()
            
            # Para stored procedures, intentar obtener resultados
            if 'CALL' in query.upper():
                try:
                    # Puede haber múltiples result sets
                    results = []
                    for result in cursor.stored_results():
                        results.extend(result.fetchall())
                    return results if results else None
                except:
                    return None
            
            return None
            
        except mysql.connector.Error as e:
            if connection:
                connection.rollback()
            print(f"Error en MySQL query: {str(e)}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_transaction(self, queries_with_params):
        """
        Ejecutar múltiples queries en una transacción
        
        Args:
            queries_with_params: Lista de tuplas (query, params)
            
        Returns:
            True si la transacción fue exitosa
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Deshabilitar autocommit
            connection.start_transaction()
            
            for query, params in queries_with_params:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            
            connection.commit()
            return True
            
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Error en transacción: {str(e)}")
            raise
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def close(self):
        """Cerrar todas las conexiones del pool"""
        if self.pool:
            # No hay método directo para cerrar el pool en mysql-connector-python
            # Las conexiones se cierran automáticamente cuando se destruye el objeto
            print("Pool de conexiones MySQL cerrado")
