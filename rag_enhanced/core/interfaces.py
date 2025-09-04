#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔌 Interfaces - Definições de interfaces base para o RAG Enhanced

Este módulo define as interfaces abstratas que todos os componentes principais
devem implementar, garantindo consistência e permitindo fácil extensibilidade.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from .models import (
    RAGConfig, ValidationResult, ProcessingResult, QueryResponse,
    ProcessingCheckpoint, ErrorContext, DiagnosticsReport
)


class ConfigurationManagerInterface(ABC):
    """
    🔧 Interface para gerenciamento de configurações
    
    Define os métodos que qualquer gerenciador de configuração deve implementar
    para fornecer funcionalidades de carregamento, validação e persistência.
    """
    
    @abstractmethod
    def get_config(self, profile_name: str = "default") -> RAGConfig:
        """
        Carrega configuração para o perfil especificado
        
        Args:
            profile_name: Nome do perfil de configuração
            
        Returns:
            Configuração carregada e validada
            
        Raises:
            ConfigurationError: Se o perfil não existir ou configuração for inválida
        """
        pass
    
    @abstractmethod
    def save_config(self, config: RAGConfig, profile_name: str = "default") -> bool:
        """
        Salva configuração no perfil especificado
        
        Args:
            config: Configuração a ser salva
            profile_name: Nome do perfil
            
        Returns:
            True se salvou com sucesso
            
        Raises:
            ConfigurationError: Se não conseguir salvar
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: RAGConfig) -> ValidationResult:
        """
        Valida uma configuração
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            Resultado da validação com detalhes
        """
        pass
    
    @abstractmethod
    def create_config_wizard(self) -> RAGConfig:
        """
        Executa wizard interativo de configuração
        
        Returns:
            Configuração criada pelo wizard
        """
        pass
    
    @abstractmethod
    def list_profiles(self) -> List[str]:
        """
        Lista perfis de configuração disponíveis
        
        Returns:
            Lista de nomes de perfis
        """
        pass


class FileProcessorInterface(ABC):
    """
    📁 Interface para processamento de arquivos
    
    Define os métodos para análise, upload e processamento de arquivos
    com suporte a progresso, retry e recuperação.
    """
    
    @abstractmethod
    def process_codebase(self, path: Path, progress_callback: Optional[Callable] = None) -> ProcessingResult:
        """
        Processa uma base de código completa
        
        Args:
            path: Caminho para a base de código
            progress_callback: Callback para atualizações de progresso
            
        Returns:
            Resultado do processamento
        """
        pass
    
    @abstractmethod
    def analyze_files(self, files: List[Path]) -> Dict[str, Any]:
        """
        Analisa arquivos para determinar requisitos de processamento
        
        Args:
            files: Lista de arquivos para analisar
            
        Returns:
            Análise dos arquivos (tipos, tamanhos, etc.)
        """
        pass
    
    @abstractmethod
    def upload_with_retry(self, files: List[Path]) -> ProcessingResult:
        """
        Faz upload de arquivos com retry automático
        
        Args:
            files: Lista de arquivos para upload
            
        Returns:
            Resultado do upload
        """
        pass
    
    @abstractmethod
    def resume_processing(self, checkpoint: ProcessingCheckpoint) -> ProcessingResult:
        """
        Resume processamento a partir de um checkpoint
        
        Args:
            checkpoint: Checkpoint de onde resumir
            
        Returns:
            Resultado do processamento resumido
        """
        pass
    
    @abstractmethod
    def create_checkpoint(self) -> ProcessingCheckpoint:
        """
        Cria checkpoint do estado atual
        
        Returns:
            Checkpoint criado
        """
        pass


class QueryEngineInterface(ABC):
    """
    🔍 Interface para motor de consultas
    
    Define os métodos para processamento de consultas, análise avançada
    e geração de documentação.
    """
    
    @abstractmethod
    def process_query(self, query: str, context: Optional[Dict] = None) -> QueryResponse:
        """
        Processa uma consulta com contexto opcional
        
        Args:
            query: Consulta a ser processada
            context: Contexto adicional para a consulta
            
        Returns:
            Resposta estruturada da consulta
        """
        pass
    
    @abstractmethod
    def analyze_code_patterns(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analisa padrões de código na base
        
        Args:
            focus_areas: Áreas específicas para focar a análise
            
        Returns:
            Análise de padrões encontrados
        """
        pass
    
    @abstractmethod
    def generate_documentation(self, doc_type: str, options: Optional[Dict] = None) -> str:
        """
        Gera documentação baseada no código
        
        Args:
            doc_type: Tipo de documentação (api, architecture, etc.)
            options: Opções específicas para o tipo de documentação
            
        Returns:
            Documentação gerada
        """
        pass
    
    @abstractmethod
    def assess_code_quality(self) -> Dict[str, Any]:
        """
        Avalia qualidade do código
        
        Returns:
            Avaliação de qualidade com métricas e recomendações
        """
        pass
    
    @abstractmethod
    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analisa dependências da base de código
        
        Returns:
            Análise de dependências e estrutura
        """
        pass


class ErrorHandlerInterface(ABC):
    """
    ⚠️ Interface para tratamento de erros
    
    Define os métodos para classificação, tratamento e recuperação de erros
    com estratégias inteligentes de retry e diagnóstico.
    """
    
    @abstractmethod
    def handle_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """
        Trata um erro com base no contexto
        
        Args:
            error: Exceção ocorrida
            context: Contexto do erro
            
        Returns:
            Resultado do tratamento (recovery, retry, etc.)
        """
        pass
    
    @abstractmethod
    def classify_error(self, error: Exception) -> str:
        """
        Classifica um erro para determinar estratégia de tratamento
        
        Args:
            error: Exceção a ser classificada
            
        Returns:
            Classificação do erro
        """
        pass
    
    @abstractmethod
    def run_diagnostics(self) -> DiagnosticsReport:
        """
        Executa diagnósticos do sistema
        
        Returns:
            Relatório de diagnósticos
        """
        pass
    
    @abstractmethod
    def create_recovery_strategy(self, error_type: str, context: ErrorContext) -> Dict[str, Any]:
        """
        Cria estratégia de recuperação para um tipo de erro
        
        Args:
            error_type: Tipo do erro
            context: Contexto do erro
            
        Returns:
            Estratégia de recuperação
        """
        pass
    
    @abstractmethod
    def should_retry(self, error: Exception, attempt_count: int) -> bool:
        """
        Determina se deve tentar novamente após um erro
        
        Args:
            error: Exceção ocorrida
            attempt_count: Número de tentativas já realizadas
            
        Returns:
            True se deve tentar novamente
        """
        pass


class ProgressTrackerInterface(ABC):
    """
    📊 Interface para rastreamento de progresso
    
    Define métodos para rastrear e reportar progresso de operações longas.
    """
    
    @abstractmethod
    def start_operation(self, operation_name: str, total_items: int) -> None:
        """
        Inicia rastreamento de uma operação
        
        Args:
            operation_name: Nome da operação
            total_items: Total de itens a processar
        """
        pass
    
    @abstractmethod
    def update_progress(self, completed_items: int, message: Optional[str] = None) -> None:
        """
        Atualiza progresso da operação
        
        Args:
            completed_items: Itens completados
            message: Mensagem opcional de status
        """
        pass
    
    @abstractmethod
    def finish_operation(self, success: bool = True, message: Optional[str] = None) -> None:
        """
        Finaliza rastreamento da operação
        
        Args:
            success: Se a operação foi bem-sucedida
            message: Mensagem final opcional
        """
        pass
    
    @abstractmethod
    def get_eta(self) -> Optional[float]:
        """
        Calcula tempo estimado para conclusão
        
        Returns:
            ETA em segundos ou None se não disponível
        """
        pass


class TestFrameworkInterface(ABC):
    """
    🧪 Interface para framework de testes
    
    Define métodos para execução de testes unitários, integração e performance.
    """
    
    @abstractmethod
    def run_unit_tests(self) -> Dict[str, Any]:
        """
        Executa testes unitários
        
        Returns:
            Resultados dos testes unitários
        """
        pass
    
    @abstractmethod
    def run_integration_tests(self) -> Dict[str, Any]:
        """
        Executa testes de integração
        
        Returns:
            Resultados dos testes de integração
        """
        pass
    
    @abstractmethod
    def run_performance_tests(self) -> Dict[str, Any]:
        """
        Executa testes de performance
        
        Returns:
            Resultados dos testes de performance
        """
        pass
    
    @abstractmethod
    def generate_test_report(self) -> str:
        """
        Gera relatório completo de testes
        
        Returns:
            Relatório formatado dos testes
        """
        pass