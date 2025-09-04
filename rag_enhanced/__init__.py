#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 RAG Enhanced - Sistema RAG Aprimorado para Análise de Código

Este módulo fornece um sistema RAG (Retrieval-Augmented Generation) aprimorado
para análise de código local com recursos avançados de configuração, processamento
de arquivos, tratamento de erros e análise inteligente.

Principais componentes:
- Configuration: Sistema de configuração flexível com perfis
- Processing: Pipeline robusto de processamento de arquivos
- Query: Motor de consultas avançado com análise de padrões
- Error: Sistema abrangente de tratamento de erros
- Testing: Framework completo de testes
"""

from .core.interfaces import (
    ConfigurationManagerInterface,
    FileProcessorInterface,
    QueryEngineInterface,
    ErrorHandlerInterface,
    ProgressTrackerInterface,
    TestFrameworkInterface
)
from .core.models import (
    RAGConfig,
    ProcessingResult,
    QueryResponse,
    ValidationResult,
    ProcessingCheckpoint,
    ErrorContext,
    DiagnosticsReport
)
from .core.exceptions import (
    RAGEnhancedException,
    ConfigurationError,
    ProcessingError,
    QueryError
)

__version__ = "2.0.0"
__author__ = "ValidAI Enhanced Team"
__description__ = "Sistema RAG aprimorado para análise de código local"

# Exportar classes principais
__all__ = [
    # Core interfaces
    'ConfigurationManagerInterface',
    'FileProcessorInterface', 
    'QueryEngineInterface',
    'ErrorHandlerInterface',
    'ProgressTrackerInterface',
    'TestFrameworkInterface',
    
    # Data models
    'RAGConfig',
    'ProcessingResult',
    'QueryResponse',
    'ValidationResult',
    'ProcessingCheckpoint',
    'ErrorContext',
    'DiagnosticsReport',
    
    # Exceptions
    'RAGEnhancedException',
    'ConfigurationError',
    'ProcessingError',
    'QueryError',
]