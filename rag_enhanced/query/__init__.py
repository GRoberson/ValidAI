#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Query - Motor de consultas avançado

Este módulo fornece processamento inteligente de consultas com
análise de padrões, geração de documentação e avaliação de qualidade.
"""

from .engine import AdvancedQueryEngine
from .analyzer import AnalysisEngine
from .formatter import ResponseFormatter
from .history import QueryHistory

__all__ = [
    'AdvancedQueryEngine',
    'AnalysisEngine',
    'ResponseFormatter',
    'QueryHistory'
]