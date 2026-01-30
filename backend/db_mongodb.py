"""
Módulo de conexión a MongoDB con patrón Singleton
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from threading import Lock


class MongoDBConnection:
    """
    Clase Singleton para manejar conexiones a MongoDB
    Garantiza una única instancia de conexión en toda la aplicación
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Implementación del patrón Singleton con thread-safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MongoDBConnection, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializar conexión a MongoDB (solo una vez)"""
        if self._initialized:
            return
        
        self.client = None
        self.db = None
        self.connect()
        self._initialized = True
    
    def connect(self):
        """Establecer conexión con MongoDB"""
        try:
            # Configuración de conexión
            host = os.getenv('MONGODB_HOST', 'mongodb_db')
            port = int(os.getenv('MONGODB_PORT', 27017))
            database = os.getenv('MONGODB_DATABASE', 'ecommerce_catalog')
            username = os.getenv('MONGODB_USER', 'admin')
            password = os.getenv('MONGODB_PASSWORD', 'adminpassword')
            
            # Construir URI de conexión
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/?authSource=admin"
            else:
                connection_string = f"mongodb://{host}:{port}/"
            
            # Crear cliente
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            # Seleccionar base de datos
            self.db = self.client[database]
            
            print("✓ Conexión a MongoDB establecida correctamente")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"✗ Error al conectar con MongoDB: {str(e)}")
            raise
        except Exception as e:
            print(f"✗ Error inesperado en MongoDB: {str(e)}")
            raise
    
    def get_collection(self, collection_name):
        """
        Obtener una colección de MongoDB
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Objeto Collection de pymongo
        """
        if not self.db:
            raise Exception("No hay conexión activa a MongoDB")
        
        return self.db[collection_name]
    
    def insert_one(self, collection_name, document):
        """
        Insertar un documento en una colección
        
        Args:
            collection_name: Nombre de la colección
            document: Documento a insertar (dict)
            
        Returns:
            ID del documento insertado
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            print(f"Error al insertar documento: {str(e)}")
            raise
    
    def insert_many(self, collection_name, documents):
        """
        Insertar múltiples documentos en una colección
        
        Args:
            collection_name: Nombre de la colección
            documents: Lista de documentos a insertar
            
        Returns:
            Lista de IDs de los documentos insertados
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents)
            return result.inserted_ids
        except Exception as e:
            print(f"Error al insertar documentos: {str(e)}")
            raise
    
    def find_one(self, collection_name, query, projection=None):
        """
        Buscar un documento en una colección
        
        Args:
            collection_name: Nombre de la colección
            query: Filtro de búsqueda (dict)
            projection: Campos a retornar (dict)
            
        Returns:
            Documento encontrado o None
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query, projection)
        except Exception as e:
            print(f"Error al buscar documento: {str(e)}")
            raise
    
    def find(self, collection_name, query, projection=None, sort=None, limit=0):
        """
        Buscar múltiples documentos en una colección
        
        Args:
            collection_name: Nombre de la colección
            query: Filtro de búsqueda (dict)
            projection: Campos a retornar (dict)
            sort: Ordenamiento (lista de tuplas)
            limit: Límite de documentos a retornar
            
        Returns:
            Cursor con los documentos encontrados
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            
            if limit > 0:
                cursor = cursor.limit(limit)
            
            return cursor
        except Exception as e:
            print(f"Error al buscar documentos: {str(e)}")
            raise
    
    def update_one(self, collection_name, query, update):
        """
        Actualizar un documento en una colección
        
        Args:
            collection_name: Nombre de la colección
            query: Filtro para encontrar el documento
            update: Operaciones de actualización
            
        Returns:
            Número de documentos modificados
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, update)
            return result.modified_count
        except Exception as e:
            print(f"Error al actualizar documento: {str(e)}")
            raise
    
    def update_many(self, collection_name, query, update):
        """
        Actualizar múltiples documentos en una colección
        
        Args:
            collection_name: Nombre de la colección
            query: Filtro para encontrar los documentos
            update: Operaciones de actualización
            
        Returns:
            Número de documentos modificados
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(query, update)
            return result.modified_count
        except Exception as e:
            print(f"Error al actualizar documentos: {str(e)}")
            raise
    
    def delete_one(self, collection_name, query):
        """
        Eliminar un documento de una colección
        
        Args:
            collection_name: Nombre de la colección
            query: Filtro para encontrar el documento
            
        Returns:
            Número de documentos eliminados
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count
        except Exception as e:
            print(f"Error al eliminar documento: {str(e)}")
            raise
    
    def aggregate(self, collection_name, pipeline):
        """
        Ejecutar una agregación en una colección
        
        Args:
            collection_name: Nombre de la colección
            pipeline: Pipeline de agregación
            
        Returns:
            Cursor con los resultados de la agregación
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.aggregate(pipeline)
        except Exception as e:
            print(f"Error en agregación: {str(e)}")
            raise
    
    def close(self):
        """Cerrar la conexión a MongoDB"""
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada")
