#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Progress Tracker - Sistema de rastreamento de progresso

Este módulo fornece rastreamento detalhado de progresso para operações longas
com ETA, visualização em tempo real e callbacks personalizáveis.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

from ..core.interfaces import ProgressTrackerInterface
from ..core.exceptions import ProcessingError


class OperationStatus(Enum):
    """Status de uma operação"""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressSnapshot:
    """
    📸 Snapshot do progresso em um momento específico
    """
    timestamp: datetime
    completed_items: int
    total_items: int
    current_item: Optional[str] = None
    message: Optional[str] = None
    bytes_processed: int = 0
    total_bytes: int = 0
    
    @property
    def completion_percentage(self) -> float:
        """Percentual de conclusão"""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def bytes_percentage(self) -> float:
        """Percentual de bytes processados"""
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_processed / self.total_bytes) * 100


@dataclass
class OperationMetrics:
    """
    📈 Métricas de uma operação
    """
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    total_bytes: int = 0
    processed_bytes: int = 0
    status: OperationStatus = OperationStatus.NOT_STARTED
    error_messages: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Duração da operação"""
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def items_per_second(self) -> float:
        """Taxa de processamento (itens por segundo)"""
        duration = self.duration
        if not duration or duration.total_seconds() == 0:
            return 0.0
        return self.completed_items / duration.total_seconds()
    
    @property
    def bytes_per_second(self) -> float:
        """Taxa de processamento (bytes por segundo)"""
        duration = self.duration
        if not duration or duration.total_seconds() == 0:
            return 0.0
        return self.processed_bytes / duration.total_seconds()


class ProgressTracker(ProgressTrackerInterface):
    """
    📊 Rastreador de progresso avançado
    
    Fornece rastreamento detalhado com:
    - Cálculo de ETA baseado em histórico
    - Visualização em tempo real
    - Callbacks personalizáveis
    - Métricas de performance
    - Suporte a operações aninhadas
    """
    
    def __init__(self, update_interval: float = 1.0):
        """
        Inicializa o rastreador
        
        Args:
            update_interval: Intervalo entre atualizações (segundos)
        """
        self.update_interval = update_interval
        
        # Estado atual
        self.current_operation: Optional[OperationMetrics] = None
        self.progress_history: List[ProgressSnapshot] = []
        self.callbacks: List[Callable] = []
        
        # Controle de thread
        self._update_thread: Optional[threading.Thread] = None
        self._stop_updates = threading.Event()
        self._lock = threading.Lock()
        
        # Operações aninhadas
        self.operation_stack: List[OperationMetrics] = []
        
        # Cache de cálculos
        self._eta_cache: Optional[float] = None
        self._eta_cache_time: Optional[datetime] = None
    
    def start_operation(self, operation_name: str, total_items: int, total_bytes: int = 0) -> None:
        """
        Inicia rastreamento de uma operação
        
        Args:
            operation_name: Nome da operação
            total_items: Total de itens a processar
            total_bytes: Total de bytes a processar (opcional)
        """
        with self._lock:
            # Se há operação em andamento, empilhar
            if self.current_operation and self.current_operation.status == OperationStatus.RUNNING:
                self.operation_stack.append(self.current_operation)
            
            # Criar nova operação
            self.current_operation = OperationMetrics(
                operation_name=operation_name,
                start_time=datetime.now(),
                total_items=total_items,
                total_bytes=total_bytes,
                status=OperationStatus.RUNNING
            )
            
            # Limpar histórico e cache
            self.progress_history.clear()
            self._eta_cache = None
            self._eta_cache_time = None
            
            # Iniciar thread de atualização
            self._start_update_thread()
            
            # Notificar callbacks
            self._notify_callbacks("operation_started")
    
    def update_progress(self, 
                       completed_items: int = None, 
                       message: Optional[str] = None,
                       current_item: Optional[str] = None,
                       bytes_processed: int = None) -> None:
        """
        Atualiza progresso da operação
        
        Args:
            completed_items: Itens completados (incrementa se None)
            message: Mensagem opcional de status
            current_item: Item atual sendo processado
            bytes_processed: Bytes processados (incrementa se None)
        """
        if not self.current_operation:
            return
        
        with self._lock:
            # Atualizar contadores
            if completed_items is not None:
                self.current_operation.completed_items = completed_items
            else:
                self.current_operation.completed_items += 1
            
            if bytes_processed is not None:
                self.current_operation.processed_bytes = bytes_processed
            
            # Criar snapshot
            snapshot = ProgressSnapshot(
                timestamp=datetime.now(),
                completed_items=self.current_operation.completed_items,
                total_items=self.current_operation.total_items,
                current_item=current_item,
                message=message,
                bytes_processed=self.current_operation.processed_bytes,
                total_bytes=self.current_operation.total_bytes
            )
            
            # Adicionar ao histórico (manter apenas os últimos 100)
            self.progress_history.append(snapshot)
            if len(self.progress_history) > 100:
                self.progress_history.pop(0)
            
            # Invalidar cache de ETA
            self._eta_cache = None
            self._eta_cache_time = None
            
            # Notificar callbacks
            self._notify_callbacks("progress_updated", snapshot)
    
    def add_failed_item(self, error_message: str = "") -> None:
        """
        Registra um item que falhou
        
        Args:
            error_message: Mensagem de erro opcional
        """
        if not self.current_operation:
            return
        
        with self._lock:
            self.current_operation.failed_items += 1
            if error_message:
                self.current_operation.error_messages.append(error_message)
    
    def add_skipped_item(self, reason: str = "") -> None:
        """
        Registra um item que foi pulado
        
        Args:
            reason: Razão para pular o item
        """
        if not self.current_operation:
            return
        
        with self._lock:
            self.current_operation.skipped_items += 1
    
    def pause_operation(self) -> None:
        """Pausa a operação atual"""
        if not self.current_operation:
            return
        
        with self._lock:
            self.current_operation.status = OperationStatus.PAUSED
            self._stop_update_thread()
            self._notify_callbacks("operation_paused")
    
    def resume_operation(self) -> None:
        """Resume a operação pausada"""
        if not self.current_operation or self.current_operation.status != OperationStatus.PAUSED:
            return
        
        with self._lock:
            self.current_operation.status = OperationStatus.RUNNING
            self._start_update_thread()
            self._notify_callbacks("operation_resumed")
    
    def finish_operation(self, success: bool = True, message: Optional[str] = None) -> OperationMetrics:
        """
        Finaliza rastreamento da operação
        
        Args:
            success: Se a operação foi bem-sucedida
            message: Mensagem final opcional
            
        Returns:
            Métricas finais da operação
        """
        if not self.current_operation:
            raise ProcessingError(
                operation="progress_tracking",
                message="Nenhuma operação em andamento para finalizar"
            )
        
        with self._lock:
            # Finalizar operação atual
            self.current_operation.end_time = datetime.now()
            self.current_operation.status = OperationStatus.COMPLETED if success else OperationStatus.FAILED
            
            # Parar thread de atualização
            self._stop_update_thread()
            
            # Criar snapshot final
            final_snapshot = ProgressSnapshot(
                timestamp=datetime.now(),
                completed_items=self.current_operation.completed_items,
                total_items=self.current_operation.total_items,
                message=message or ("Operação concluída" if success else "Operação falhou"),
                bytes_processed=self.current_operation.processed_bytes,
                total_bytes=self.current_operation.total_bytes
            )
            
            self.progress_history.append(final_snapshot)
            
            # Notificar callbacks
            self._notify_callbacks("operation_finished", final_snapshot)
            
            # Salvar métricas
            finished_operation = self.current_operation
            
            # Restaurar operação anterior se houver
            if self.operation_stack:
                self.current_operation = self.operation_stack.pop()
                self._start_update_thread()
            else:
                self.current_operation = None
            
            return finished_operation
    
    def cancel_operation(self, message: str = "Operação cancelada") -> None:
        """
        Cancela a operação atual
        
        Args:
            message: Mensagem de cancelamento
        """
        if not self.current_operation:
            return
        
        with self._lock:
            self.current_operation.status = OperationStatus.CANCELLED
            self.current_operation.end_time = datetime.now()
            
            self._stop_update_thread()
            self._notify_callbacks("operation_cancelled")
    
    def get_eta(self) -> Optional[float]:
        """
        Calcula tempo estimado para conclusão
        
        Returns:
            ETA em segundos ou None se não disponível
        """
        if not self.current_operation or len(self.progress_history) < 2:
            return None
        
        # Usar cache se recente (< 5 segundos)
        now = datetime.now()
        if (self._eta_cache is not None and 
            self._eta_cache_time and 
            (now - self._eta_cache_time).total_seconds() < 5):
            return self._eta_cache
        
        with self._lock:
            # Calcular baseado nos últimos snapshots
            recent_snapshots = self.progress_history[-10:]  # Últimos 10 snapshots
            
            if len(recent_snapshots) < 2:
                return None
            
            # Calcular taxa média
            first_snapshot = recent_snapshots[0]
            last_snapshot = recent_snapshots[-1]
            
            time_diff = (last_snapshot.timestamp - first_snapshot.timestamp).total_seconds()
            items_diff = last_snapshot.completed_items - first_snapshot.completed_items
            
            if time_diff <= 0 or items_diff <= 0:
                return None
            
            items_per_second = items_diff / time_diff
            remaining_items = self.current_operation.total_items - last_snapshot.completed_items
            
            eta = remaining_items / items_per_second
            
            # Cache do resultado
            self._eta_cache = eta
            self._eta_cache_time = now
            
            return eta
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Obtém status atual detalhado
        
        Returns:
            Dicionário com status completo
        """
        if not self.current_operation:
            return {"status": "no_operation"}
        
        latest_snapshot = self.progress_history[-1] if self.progress_history else None
        eta = self.get_eta()
        
        return {
            "operation_name": self.current_operation.operation_name,
            "status": self.current_operation.status.value,
            "completed_items": self.current_operation.completed_items,
            "total_items": self.current_operation.total_items,
            "failed_items": self.current_operation.failed_items,
            "skipped_items": self.current_operation.skipped_items,
            "completion_percentage": latest_snapshot.completion_percentage if latest_snapshot else 0,
            "eta_seconds": eta,
            "eta_formatted": self._format_duration(eta) if eta else None,
            "duration": self.current_operation.duration.total_seconds() if self.current_operation.duration else 0,
            "items_per_second": self.current_operation.items_per_second,
            "bytes_processed": self.current_operation.processed_bytes,
            "total_bytes": self.current_operation.total_bytes,
            "bytes_per_second": self.current_operation.bytes_per_second,
            "current_message": latest_snapshot.message if latest_snapshot else None,
            "current_item": latest_snapshot.current_item if latest_snapshot else None
        }
    
    def add_callback(self, callback: Callable) -> None:
        """
        Adiciona callback para eventos de progresso
        
        Args:
            callback: Função a ser chamada nos eventos
        """
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable) -> None:
        """
        Remove callback
        
        Args:
            callback: Função a ser removida
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_progress_history(self) -> List[ProgressSnapshot]:
        """
        Obtém histórico de progresso
        
        Returns:
            Lista de snapshots de progresso
        """
        return self.progress_history.copy()
    
    def format_progress_bar(self, width: int = 50) -> str:
        """
        Formata barra de progresso textual
        
        Args:
            width: Largura da barra em caracteres
            
        Returns:
            String com barra de progresso formatada
        """
        if not self.current_operation or not self.progress_history:
            return "No operation in progress"
        
        latest = self.progress_history[-1]
        percentage = latest.completion_percentage
        
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        eta = self.get_eta()
        eta_str = f" ETA: {self._format_duration(eta)}" if eta else ""
        
        return f"[{bar}] {percentage:.1f}% ({latest.completed_items}/{latest.total_items}){eta_str}"
    
    def _start_update_thread(self) -> None:
        """Inicia thread de atualização automática"""
        if self._update_thread and self._update_thread.is_alive():
            return
        
        self._stop_updates.clear()
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def _stop_update_thread(self) -> None:
        """Para thread de atualização"""
        self._stop_updates.set()
        if self._update_thread:
            self._update_thread.join(timeout=1.0)
    
    def _update_loop(self) -> None:
        """Loop principal de atualização"""
        while not self._stop_updates.wait(self.update_interval):
            if self.current_operation and self.current_operation.status == OperationStatus.RUNNING:
                self._notify_callbacks("periodic_update")
    
    def _notify_callbacks(self, event_type: str, data: Any = None) -> None:
        """Notifica todos os callbacks"""
        for callback in self.callbacks:
            try:
                callback(event_type, data, self.get_current_status())
            except Exception:
                pass  # Ignorar erros em callbacks
    
    def _format_duration(self, seconds: Optional[float]) -> str:
        """Formata duração em formato legível"""
        if seconds is None:
            return "N/A"
        
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class ConsoleProgressDisplay:
    """
    🖥️ Display de progresso para console
    
    Exibe progresso em tempo real no terminal com
    barra de progresso, estatísticas e ETA.
    """
    
    def __init__(self, tracker: ProgressTracker, show_details: bool = True):
        """
        Inicializa display
        
        Args:
            tracker: Rastreador de progresso
            show_details: Se deve mostrar detalhes adicionais
        """
        self.tracker = tracker
        self.show_details = show_details
        self.last_line_length = 0
        
        # Registrar callback
        tracker.add_callback(self._on_progress_event)
    
    def _on_progress_event(self, event_type: str, data: Any, status: Dict[str, Any]) -> None:
        """Callback para eventos de progresso"""
        if event_type in ["progress_updated", "periodic_update"]:
            self._update_display(status)
        elif event_type == "operation_started":
            print(f"\n🚀 Iniciando: {status['operation_name']}")
        elif event_type == "operation_finished":
            self._show_final_summary(status)
        elif event_type == "operation_paused":
            print(f"\n⏸️ Operação pausada")
        elif event_type == "operation_resumed":
            print(f"\n▶️ Operação resumida")
        elif event_type == "operation_cancelled":
            print(f"\n❌ Operação cancelada")
    
    def _update_display(self, status: Dict[str, Any]) -> None:
        """Atualiza display no console"""
        # Limpar linha anterior
        if self.last_line_length > 0:
            print("\r" + " " * self.last_line_length, end="\r")
        
        # Criar linha de progresso
        progress_bar = self.tracker.format_progress_bar(40)
        
        line = f"\r📊 {progress_bar}"
        
        if self.show_details:
            # Adicionar detalhes
            if status.get("items_per_second", 0) > 0:
                line += f" | {status['items_per_second']:.1f} items/s"
            
            if status.get("current_item"):
                item_name = status["current_item"]
                if len(item_name) > 30:
                    item_name = item_name[:27] + "..."
                line += f" | {item_name}"
        
        print(line, end="", flush=True)
        self.last_line_length = len(line)
    
    def _show_final_summary(self, status: Dict[str, Any]) -> None:
        """Mostra resumo final"""
        print()  # Nova linha
        
        duration = status.get("duration", 0)
        completed = status.get("completed_items", 0)
        failed = status.get("failed_items", 0)
        skipped = status.get("skipped_items", 0)
        
        print(f"✅ {status['operation_name']} concluída!")
        print(f"   📊 Processados: {completed} | ❌ Falharam: {failed} | ⏭️ Pulados: {skipped}")
        print(f"   ⏱️ Tempo total: {self.tracker._format_duration(duration)}")
        
        if status.get("items_per_second", 0) > 0:
            print(f"   🚀 Taxa média: {status['items_per_second']:.1f} items/s")
        
        print()