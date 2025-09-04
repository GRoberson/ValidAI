#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗄️ Cache Module - Sistema de cache inteligente

Este módulo fornece gerenciamento avançado de cache com TTL,
limpeza automática e prevenção de vazamentos de memória.
"""

from .cache_manager import (
    SmartCache,
    CacheManager, 
    CacheEntry,
    get_cache,
    clear_all_caches,
    shutdown_cache_system
)

__all__ = [
    'SmartCache',
    'CacheManager',
    'CacheEntry', 
    'get_cache',
    'clear_all_caches',
    'shutdown_cache_system'
]