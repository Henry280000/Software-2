"""
Patrón Observer - Sistema de notificaciones en tiempo real
Permite notificar eventos a múltiples observadores
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


class TipoEvento(Enum):
    """Tipos de eventos del sistema"""
    PEDIDO_CREADO = "PEDIDO_CREADO"
    PEDIDO_ACTUALIZADO = "PEDIDO_ACTUALIZADO"
    PEDIDO_CANCELADO = "PEDIDO_CANCELADO"
    STOCK_BAJO = "STOCK_BAJO"
    PRODUCTO_AGOTADO = "PRODUCTO_AGOTADO"
    USUARIO_REGISTRADO = "USUARIO_REGISTRADO"
    PAGO_PROCESADO = "PAGO_PROCESADO"


class EventObserver(ABC):
    """
    Interfaz base para observadores (Patrón Observer)
    Todos los observadores deben implementar el método update
    """
    
    @abstractmethod
    def update(self, tipo_evento: TipoEvento, datos: Dict[str, Any]) -> None:
        """
        Método llamado cuando ocurre un evento
        
        Args:
            tipo_evento: Tipo del evento
            datos: Datos asociados al evento
        """
        pass


class NotificationService:
    """
    Servicio de notificaciones en tiempo real (Patrón Observer)
    Gestiona observadores y notifica eventos
    """
    
    _instance = None
    
    def __new__(cls):
        """Implementación Singleton"""
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el servicio de notificaciones"""
        if self._initialized:
            return
        
        self._observers: Dict[TipoEvento, List[EventObserver]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._initialized = True
    
    def attach(self, tipo_evento: TipoEvento, observer: EventObserver) -> None:
        """
        Agrega un observador para un tipo de evento específico
        
        Args:
            tipo_evento: Tipo de evento a observar
            observer: Observador a agregar
        """
        if tipo_evento not in self._observers:
            self._observers[tipo_evento] = []
        
        if observer not in self._observers[tipo_evento]:
            self._observers[tipo_evento].append(observer)
            print(f"Observador agregado para evento: {tipo_evento.value}")
    
    def detach(self, tipo_evento: TipoEvento, observer: EventObserver) -> None:
        """
        Elimina un observador de un tipo de evento
        
        Args:
            tipo_evento: Tipo de evento
            observer: Observador a eliminar
        """
        if tipo_evento in self._observers and observer in self._observers[tipo_evento]:
            self._observers[tipo_evento].remove(observer)
            print(f"Observador eliminado para evento: {tipo_evento.value}")
    
    def notify(self, tipo_evento: TipoEvento, datos: Dict[str, Any]) -> None:
        """
        Notifica a todos los observadores de un evento
        
        Args:
            tipo_evento: Tipo del evento
            datos: Datos del evento
        """
        # Registrar evento en historial
        evento = {
            'tipo': tipo_evento.value,
            'datos': datos,
            'timestamp': datetime.now()
        }
        self._event_history.append(evento)
        
        # Notificar a observadores
        if tipo_evento in self._observers:
            for observer in self._observers[tipo_evento]:
                try:
                    observer.update(tipo_evento, datos)
                except Exception as e:
                    print(f"Error al notificar observador: {str(e)}")
    
    def get_event_history(self, tipo_evento: TipoEvento = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de eventos
        
        Args:
            tipo_evento: Filtrar por tipo de evento (opcional)
            limit: Límite de eventos a retornar
            
        Returns:
            Lista de eventos
        """
        if tipo_evento:
            eventos = [e for e in self._event_history if e['tipo'] == tipo_evento.value]
        else:
            eventos = self._event_history
        
        return eventos[-limit:]
    
    def clear_history(self) -> None:
        """Limpia el historial de eventos"""
        self._event_history.clear()


# Implementaciones concretas de observadores

class EmailNotificationObserver(EventObserver):
    """Observador que envía notificaciones por email"""
    
    def update(self, tipo_evento: TipoEvento, datos: Dict[str, Any]) -> None:
        """Envía un email cuando ocurre un evento"""
        print(f"[EMAIL] Evento: {tipo_evento.value}")
        print(f"[EMAIL] Destinatario: {datos.get('email', 'No especificado')}")
        print(f"[EMAIL] Mensaje: {datos.get('mensaje', 'Sin mensaje')}")
        # Aquí iría la lógica real de envío de email


class WebSocketNotificationObserver(EventObserver):
    """Observador que envía notificaciones por WebSocket para tiempo real"""
    
    def update(self, tipo_evento: TipoEvento, datos: Dict[str, Any]) -> None:
        """Envía una notificación por WebSocket"""
        print(f"[WEBSOCKET] Evento en tiempo real: {tipo_evento.value}")
        print(f"[WEBSOCKET] Datos: {datos}")
        # Aquí iría la lógica de emisión por WebSocket


class LogNotificationObserver(EventObserver):
    """Observador que registra eventos en logs"""
    
    def __init__(self, log_file: str = "events.log"):
        self.log_file = log_file
    
    def update(self, tipo_evento: TipoEvento, datos: Dict[str, Any]) -> None:
        """Registra el evento en un archivo de log"""
        timestamp = datetime.now().isoformat()
        log_message = f"[{timestamp}] {tipo_evento.value}: {datos}\n"
        print(f"[LOG] {log_message.strip()}")
        # Aquí iría la lógica de escritura en archivo


class InventoryAlertObserver(EventObserver):
    """Observador que maneja alertas de inventario bajo"""
    
    def __init__(self, umbral_minimo: int = 5):
        self.umbral_minimo = umbral_minimo
    
    def update(self, tipo_evento: TipoEvento, datos: Dict[str, Any]) -> None:
        """Procesa alertas de inventario"""
        if tipo_evento == TipoEvento.STOCK_BAJO:
            producto_id = datos.get('producto_id')
            stock_actual = datos.get('stock_actual', 0)
            
            print(f"[ALERTA INVENTARIO] Producto {producto_id} tiene stock bajo: {stock_actual} unidades")
            
            if stock_actual == 0:
                print(f"[ALERTA CRÍTICA] Producto {producto_id} AGOTADO!")
