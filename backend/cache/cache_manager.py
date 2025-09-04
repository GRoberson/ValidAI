#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗄️ Cache Manager - Gerenciador de cache com TTL e limpeza automática

Este módulo fornece um sistema de cache thread-safe com:
- TTL (Time To Live) configurável
- Limpeza automática de entradas expiradas
- Limites de tamanho para prevenir vazamentos de memória
- Métricas de performance
"""

import time
import threading
import weakref
from typing import Any, Optional, Dict, Callable, Tuple
from dataclasses import dataclass
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """
    📝 Entrada do cache com metadados
    """
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self) -> None:
        """Atualiza timestamp de último acesso"""
        self.last_accessed = time.time()
        self.access_count += 1


class SmartCache:
    """
    🧠 Cache inteligente com TTL e gerenciamento automático de memória
    
    Features:
    - TTL configurável por entrada
    - Limite de tamanho com LRU eviction
    - Limpeza automática de entradas expiradas
    - Thread-safe
    - Métricas de performance
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: Optional[float] = 3600,  # 1 hora
        cleanup_interval: float = 300,  # 5 minutos
        enable_stats: bool = True
    ):
        """
        Inicializa o cache
        
        Args:
            max_size: Número máximo de entradas
            default_ttl: TTL padrão em segundos (None = sem expiração)
            cleanup_interval: Intervalo de limpeza automática em segundos
            enable_stats: Habilitar coleta de estatísticas
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.enable_stats = enable_stats
        
        # Cache storage usando OrderedDict para LRU
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Estatísticas
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_cleanups': 0,
            'total_accesses': 0
        }
        
        # Thread de limpeza automática
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self) -> None:
        """Inicia thread de limpeza automática"""
        if self.cleanup_interval > 0:
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                daemon=True,
                name="CacheCleanup"
            )
            self._cleanup_thread.start()
            logger.debug("Thread de limpeza de cache iniciada")
    
    def _cleanup_worker(self) -> None:
        """Worker thread para limpeza automática"""
        while not self._stop_cleanup.wait(self.cleanup_interval):
            try:
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Erro na limpeza automática do cache: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado
            
        Returns:
            Valor armazenado ou default
        """
        with self._lock:
            self._update_stats('total_accesses')
            
            if key not in self._cache:
                self._update_stats('misses')
                return default
            
            entry = self._cache[key]
            
            # Verificar se expirou
            if entry.is_expired():
                del self._cache[key]
                self._update_stats('misses')
                self._update_stats('expired_cleanups')
                return default
            
            # Atualizar acesso e mover para o final (LRU)
            entry.touch()
            self._cache.move_to_end(key)
            self._update_stats('hits')
            
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None
    ) -> None:
        """
        Define valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: TTL específico (None usa default)
        """
        with self._lock:
            current_time = time.time()
            ttl = ttl if ttl is not None else self.default_ttl
            
            # Criar nova entrada
            entry = CacheEntry(
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=0,
                ttl=ttl
            )
            
            # Se a chave já existe, apenas atualizar
            if key in self._cache:
                self._cache[key] = entry
                self._cache.move_to_end(key)
                return
            
            # Verificar limite de tamanho
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            # Adicionar nova entrada
            self._cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """
        Remove entrada do cache
        
        Args:
            key: Chave a remover
            
        Returns:
            True se removeu, False se não existia
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def _evict_oldest(self) -> None:
        """Remove a entrada menos recentemente usada"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._update_stats('evictions')
            logger.debug(f"Cache eviction: removido {oldest_key}")
    
    def cleanup_expired(self) -> int:
        """
        Remove entradas expiradas
        
        Returns:
            Número de entradas removidas
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._update_stats('expired_cleanups')
            
            if expired_keys:
                logger.debug(f"Cache cleanup: removidas {len(expired_keys)} entradas expiradas")
            
            return len(expired_keys)
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache limpo completamente")
    
    def _update_stats(self, metric: str) -> None:
        """Atualiza estatísticas se habilitado"""
        if self.enable_stats:
            self._stats[metric] = self._stats.get(metric, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'expired_cleanups': self._stats['expired_cleanups'],
                'total_accesses': self._stats['total_accesses'],
                'utilization': len(self._cache) / self.max_size
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre entradas do cache
        
        Returns:
            Informações sobre as entradas
        """
        with self._lock:
            current_time = time.time()
            entries_info = []
            
            for key, entry in self._cache.items():
                age = current_time - entry.created_at
                last_access_ago = current_time - entry.last_accessed
                
                entries_info.append({
                    'key': key,
                    'age_seconds': age,
                    'last_access_seconds_ago': last_access_ago,
                    'access_count': entry.access_count,
                    'ttl': entry.ttl,
                    'expires_in': (entry.ttl - age) if entry.ttl else None,
                    'is_expired': entry.is_expired()
                })
            
            return {
                'total_entries': len(entries_info),
                'entries': entries_info
            }
    
    def shutdown(self) -> None:
        """Para o cache e limpa recursos"""
        self._stop_cleanup.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        self.clear()
        logger.debug("Cache shutdown completo")
    
    def __del__(self) -> None:
        """Cleanup automático na destruição"""
        try:
            self.shutdown()
        except:
            pass  # Evitar exceções durante garbage collection


class CacheManager:
    """
    🗄️ Gerenciador global de caches
    
    Permite gerenciar múltiplos caches nomeados com configurações diferentes.
    """
    
    def __init__(self):
        self._caches: Dict[str, SmartCache] = {}
        self._lock = threading.Lock()
    
    def get_cache(
        self,
        name: str,
        max_size: int = 1000,
        default_ttl: Optional[float] = 3600,
        cleanup_interval: float = 300
    ) -> SmartCache:
        """
        Obtém ou cria um cache nomeado
        
        Args:
            name: Nome do cache
            max_size: Tamanho máximo
            default_ttl: TTL padrão
            cleanup_interval: Intervalo de limpeza
            
        Returns:
            Instância do cache
        """
        with self._lock:
            if name not in self._caches:
                self._caches[name] = SmartCache(
                    max_size=max_size,
                    default_ttl=default_ttl,
                    cleanup_interval=cleanup_interval
                )
                logger.info(f"Cache '{name}' criado com max_size={max_size}, ttl={default_ttl}")
            
            return self._caches[name]
    
    def clear_all(self) -> None:
        """Limpa todos os caches"""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
            logger.info("Todos os caches foram limpos")
    
    def shutdown_all(self) -> None:
        """Para todos os caches"""
        with self._lock:
            for cache in self._caches.values():
                cache.shutdown()
            self._caches.clear()
            logger.info("Todos os caches foram finalizados")
    
    def get_global_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém estatísticas de todos os caches
        
        Returns:
            Estatísticas globais por cache
        """
        with self._lock:
            return {
                name: cache.get_stats()
                for name, cache in self._caches.items()
            }


# Instância global do gerenciador
_cache_manager = CacheManager()

def get_cache(name: str = "default", **kwargs) -> SmartCache:
    """
    Função utilitária para obter cache
    
    Args:
        name: Nome do cache
        **kwargs: Argumentos para criação do cache
        
    Returns:
        Instância do cache
    """
    return _cache_manager.get_cache(name, **kwargs)

def clear_all_caches() -> None:
    """Limpa todos os caches globais"""
    _cache_manager.clear_all()

def shutdown_cache_system() -> None:
    """Para todo o sistema de cache"""
    _cache_manager.shutdown_all()