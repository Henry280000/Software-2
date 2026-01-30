"""
Script de Python para automatizar respaldos con POO
Implementa clase BackupManager para gestión de respaldos
"""

import os
import subprocess
import logging
from datetime import datetime
from typing import Optional
import schedule
import time


class BackupManager:
    """
    Clase que gestiona los respaldos automatizados del sistema
    Implementa el patrón Singleton para garantizar una única instancia
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.backup_script_path = '/app/scripts/backup_complete.sh'
        self.backup_dir = '/app/scripts/backups'
        self.log_file = os.path.join(self.backup_dir, 'backup.log')
        
        self._setup_logging()
        self._create_directories()
        self._initialized = True
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_directories(self):
        """Crea directorios necesarios para respaldos"""
        os.makedirs(os.path.join(self.backup_dir, 'mysql'), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, 'mongodb'), exist_ok=True)

    
    def ejecutar_backup(self) -> bool:
        """
        Ejecuta el script de backup completo
        
        Returns:
            True si el backup fue exitoso, False en caso contrario
        """
        self.logger.info("=" * 50)
        self.logger.info("Iniciando respaldo automático del sistema")
        self.logger.info("=" * 50)
        
        try:
            result = subprocess.run(
                ['bash', self.backup_script_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info("STDOUT:")
            self.logger.info(result.stdout)
            
            if result.stderr:
                self.logger.warning("STDERR:")
                self.logger.warning(result.stderr)
            
            self.logger.info("Respaldo completado exitosamente")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al ejecutar el backup: {e}")
            self.logger.error(f"STDOUT: {e.stdout}")
            self.logger.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return False
    
    def ejecutar_manual(self):
        """Ejecuta un backup manual"""
        self.logger.info("Ejecutando backup manual...")
        return self.ejecutar_backup()
    
    def programar_backup(self, hora: str = "02:00"):
        """
        Programa backups automáticos
        
        Args:
            hora: Hora del día para ejecutar backup (formato HH:MM)
        """
        schedule.every().day.at(hora).do(self.ejecutar_backup)
        
        self.logger.info("Servicio de backup automático iniciado")
        self.logger.info(f"Próximo backup programado: Todos los días a las {hora}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    import sys
    
    backup_manager = BackupManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'manual':
        backup_manager.ejecutar_manual()
    else:
        backup_manager.programar_backup()
