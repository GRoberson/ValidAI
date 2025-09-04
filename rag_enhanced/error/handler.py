#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ Error Handler - Sistema abrangente de tratamento de erros

Este módulo fornece tratamento inteligente de erros com classificação
automática, estratégias de recuperação e diagnósticos detalhados.
"""

import traceback
import logging
from typing import Dict, List, Optional, Any, Type, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from google.api_core import exceptions as gcp_exceptions
from google.cloud.exceptions import GoogleCloudError

from ..core.interfaces import ErrorHandlerInterface
from ..core.models import ErrorContext, DiagnosticsReport
from ..core.exceptions import (
    RAGEnhancedException, ConfigurationError, ProcessingError, 
    QueryError, AuthenticationError, NetworkError, ValidationError,
    ResourceError, ServiceUnavailableError, RateLimitError
)
from .retry import RetryManager
from .recovery import RecoveryManager
from .diagnostics import DiagnosticsRunner


class ErrorSeverity(Enum):
    """Severidade de erros"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categoria de erros"""
    CONFIGURATION = "configuration"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    PROCESSING = "processing"
    VALIDATION = "validation"
    RESOURCE = "resource"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


@dataclass
class ErrorAnalysis:
    """
    🔍 Análise detalhada de um erro
    """
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    is_recoverable: bool
    recovery_strategy: Optional[str]
    user_message: str
    technical_details: str
    suggestions: List[str]
    related_errors: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "category": self.category.value,
            "severity": self.severity.value,
            "is_recoverable": self.is_recoverable,
            "recovery_strategy": self.recovery_strategy,
            "user_message": self.user_message,
            "technical_details": self.technical_details,
            "suggestions": self.suggestions,
            "related_errors": self.related_errors,
            "timestamp": self.timestamp.isoformat()
        }


class ErrorHandler(ErrorHandlerInterface):
    """
    ⚠️ Gerenciador abrangente de erros
    
    Fornece tratamento inteligente incluindo:
    - Classificação automática de erros
    - Estratégias de recuperação personalizadas
    - Diagnósticos detalhados do sistema
    - Logging estruturado
    - Métricas de erro e tendências
    - Sugestões contextuais para resolução
    """
    
    def __init__(self, config=None):
        """
        Inicializa o gerenciador de erros
        
        Args:
            config: Configuração do sistema (opcional)
        """
        self.config = config
        
        # Componentes especializados
        self.retry_manager = RetryManager()
        self.recovery_manager = RecoveryManager()
        self.diagnostics_runner = DiagnosticsRunner()
        
        # Configurar logging
        self._setup_logging()
        
        # Mapeamento de tipos de erro para categorias
        self.error_mappings = self._build_error_mappings()
        
        # Estratégias de recuperação
        self.recovery_strategies = self._build_recovery_strategies()
        
        # Estatísticas de erro
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recovery_success_rate": 0.0,
            "most_common_errors": [],
            "error_trends": []
        }
        
        # Cache de análises
        self.analysis_cache = {}
    
    def handle_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """
        Trata um erro com base no contexto
        
        Args:
            error: Exceção ocorrida
            context: Contexto do erro
            
        Returns:
            Resultado do tratamento (recovery, retry, etc.)
        """
        try:
            # Analisar erro
            analysis = self.analyze_error(error, context)
            
            # Log estruturado
            self._log_error(error, analysis, context)
            
            # Atualizar estatísticas
            self._update_error_stats(analysis)
            
            # Determinar ação
            action_result = self._determine_action(error, analysis, context)
            
            # Executar estratégia de recuperação se aplicável
            if analysis.is_recoverable and analysis.recovery_strategy:
                recovery_result = self._execute_recovery(error, analysis, context)
                action_result.update(recovery_result)
            
            return {
                "analysis": analysis.to_dict(),
                "action": action_result,
                "handled": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as handler_error:
            # Erro no próprio handler - fallback
            self.logger.critical(f"Erro no error handler: {handler_error}")
            return {
                "analysis": {
                    "error_type": "handler_failure",
                    "severity": "critical",
                    "user_message": "Erro interno do sistema de tratamento de erros"
                },
                "action": {"type": "escalate"},
                "handled": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_error(self, error: Exception, context: ErrorContext) -> ErrorAnalysis:
        """
        Analisa um erro em detalhes
        
        Args:
            error: Exceção a ser analisada
            context: Contexto do erro
            
        Returns:
            Análise detalhada do erro
        """
        # Verificar cache primeiro
        error_key = f"{type(error).__name__}_{str(error)[:100]}"
        if error_key in self.analysis_cache:
            cached_analysis = self.analysis_cache[error_key]
            cached_analysis.timestamp = datetime.now()
            return cached_analysis
        
        # Classificar erro
        error_type = type(error).__name__
        category = self._classify_error(error)
        severity = self._assess_severity(error, context)
        
        # Determinar se é recuperável
        is_recoverable = self._is_recoverable(error, category)
        
        # Selecionar estratégia de recuperação
        recovery_strategy = self._select_recovery_strategy(error, category) if is_recoverable else None
        
        # Gerar mensagens
        user_message = self._generate_user_message(error, category, severity)
        technical_details = self._extract_technical_details(error, context)
        
        # Gerar sugestões
        suggestions = self._generate_suggestions(error, category, context)
        
        # Encontrar erros relacionados
        related_errors = self._find_related_errors(error, context)
        
        analysis = ErrorAnalysis(
            error_type=error_type,
            category=category,
            severity=severity,
            is_recoverable=is_recoverable,
            recovery_strategy=recovery_strategy,
            user_message=user_message,
            technical_details=technical_details,
            suggestions=suggestions,
            related_errors=related_errors,
            timestamp=datetime.now()
        )
        
        # Cache da análise
        self.analysis_cache[error_key] = analysis
        
        return analysis
    
    def classify_error(self, error: Exception) -> str:
        """
        Classifica um erro para determinar estratégia de tratamento
        
        Args:
            error: Exceção a ser classificada
            
        Returns:
            Classificação do erro
        """
        category = self._classify_error(error)
        return category.value
    
    def run_diagnostics(self) -> DiagnosticsReport:
        """
        Executa diagnósticos do sistema
        
        Returns:
            Relatório de diagnósticos
        """
        return self.diagnostics_runner.run_full_diagnostics()
    
    def create_recovery_strategy(self, error_type: str, context: ErrorContext) -> Dict[str, Any]:
        """
        Cria estratégia de recuperação para um tipo de erro
        
        Args:
            error_type: Tipo do erro
            context: Contexto do erro
            
        Returns:
            Estratégia de recuperação
        """
        if error_type in self.recovery_strategies:
            strategy = self.recovery_strategies[error_type].copy()
            
            # Personalizar baseado no contexto
            if context.operation == "file_upload" and error_type == "network_error":
                strategy["max_retries"] = 5
                strategy["backoff_factor"] = 2.0
            
            return strategy
        
        return {"type": "manual", "description": "Intervenção manual necessária"}
    
    def should_retry(self, error: Exception, attempt_count: int) -> bool:
        """
        Determina se deve tentar novamente após um erro
        
        Args:
            error: Exceção ocorrida
            attempt_count: Número de tentativas já realizadas
            
        Returns:
            True se deve tentar novamente
        """
        return self.retry_manager.should_retry(error, attempt_count)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de erro
        
        Returns:
            Estatísticas detalhadas
        """
        return self.error_stats.copy()
    
    def get_error_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analisa tendências de erro
        
        Args:
            hours: Período para análise
            
        Returns:
            Análise de tendências
        """
        # Implementação simplificada - em produção usaria dados históricos
        return {
            "period_hours": hours,
            "total_errors": self.error_stats["total_errors"],
            "trending_up": [],
            "trending_down": [],
            "new_error_types": [],
            "resolved_error_types": []
        }
    
    def _setup_logging(self) -> None:
        """Configura logging estruturado"""
        self.logger = logging.getLogger("rag_enhanced.error_handler")
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _build_error_mappings(self) -> Dict[Type[Exception], ErrorCategory]:
        """Constrói mapeamento de tipos de erro para categorias"""
        return {
            # Erros de configuração
            ConfigurationError: ErrorCategory.CONFIGURATION,
            ValidationError: ErrorCategory.VALIDATION,
            
            # Erros de rede
            NetworkError: ErrorCategory.NETWORK,
            gcp_exceptions.ServiceUnavailable: ErrorCategory.NETWORK,
            gcp_exceptions.DeadlineExceeded: ErrorCategory.NETWORK,
            
            # Erros de autenticação
            AuthenticationError: ErrorCategory.AUTHENTICATION,
            gcp_exceptions.Unauthenticated: ErrorCategory.AUTHENTICATION,
            gcp_exceptions.PermissionDenied: ErrorCategory.AUTHENTICATION,
            
            # Erros de processamento
            ProcessingError: ErrorCategory.PROCESSING,
            QueryError: ErrorCategory.PROCESSING,
            
            # Erros de recursos
            ResourceError: ErrorCategory.RESOURCE,
            gcp_exceptions.ResourceExhausted: ErrorCategory.RESOURCE,
            MemoryError: ErrorCategory.RESOURCE,
            
            # Erros de serviços externos
            ServiceUnavailableError: ErrorCategory.EXTERNAL_SERVICE,
            RateLimitError: ErrorCategory.EXTERNAL_SERVICE,
            gcp_exceptions.TooManyRequests: ErrorCategory.EXTERNAL_SERVICE,
        }
    
    def _build_recovery_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Constrói estratégias de recuperação"""
        return {
            "network_error": {
                "type": "retry_with_backoff",
                "max_retries": 3,
                "backoff_factor": 1.5,
                "description": "Retry com backoff exponencial"
            },
            "rate_limit_error": {
                "type": "wait_and_retry",
                "wait_time": 60,
                "max_retries": 2,
                "description": "Aguardar e tentar novamente"
            },
            "authentication_error": {
                "type": "refresh_credentials",
                "description": "Renovar credenciais de autenticação"
            },
            "configuration_error": {
                "type": "validate_and_fix",
                "description": "Validar e corrigir configuração"
            },
            "resource_exhausted": {
                "type": "cleanup_and_retry",
                "description": "Limpar recursos e tentar novamente"
            }
        }
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classifica erro em categoria"""
        error_type = type(error)
        
        # Verificar mapeamento direto
        if error_type in self.error_mappings:
            return self.error_mappings[error_type]
        
        # Verificar herança
        for mapped_type, category in self.error_mappings.items():
            if isinstance(error, mapped_type):
                return category
        
        # Classificação baseada em string (fallback)
        error_str = str(error).lower()
        
        if any(word in error_str for word in ['network', 'connection', 'timeout']):
            return ErrorCategory.NETWORK
        elif any(word in error_str for word in ['auth', 'permission', 'credential']):
            return ErrorCategory.AUTHENTICATION
        elif any(word in error_str for word in ['config', 'setting', 'parameter']):
            return ErrorCategory.CONFIGURATION
        elif any(word in error_str for word in ['memory', 'resource', 'quota']):
            return ErrorCategory.RESOURCE
        
        return ErrorCategory.UNKNOWN
    
    def _assess_severity(self, error: Exception, context: ErrorContext) -> ErrorSeverity:
        """Avalia severidade do erro"""
        # Erros críticos
        if isinstance(error, (MemoryError, SystemError)):
            return ErrorSeverity.CRITICAL
        
        # Erros de autenticação são sempre altos
        if isinstance(error, (AuthenticationError, gcp_exceptions.Unauthenticated)):
            return ErrorSeverity.HIGH
        
        # Erros de configuração crítica
        if isinstance(error, ConfigurationError) and "project_id" in str(error):
            return ErrorSeverity.CRITICAL
        
        # Erros de rede são médios por padrão
        if isinstance(error, (NetworkError, gcp_exceptions.ServiceUnavailable)):
            return ErrorSeverity.MEDIUM
        
        # Baseado no contexto
        if context.operation in ["initialization", "authentication"]:
            return ErrorSeverity.HIGH
        
        return ErrorSeverity.MEDIUM
    
    def _is_recoverable(self, error: Exception, category: ErrorCategory) -> bool:
        """Determina se erro é recuperável"""
        # Erros sempre recuperáveis
        recoverable_types = [
            NetworkError, gcp_exceptions.ServiceUnavailable,
            gcp_exceptions.DeadlineExceeded, RateLimitError
        ]
        
        if any(isinstance(error, t) for t in recoverable_types):
            return True
        
        # Erros nunca recuperáveis
        non_recoverable_types = [
            MemoryError, SystemError, KeyboardInterrupt
        ]
        
        if any(isinstance(error, t) for t in non_recoverable_types):
            return False
        
        # Baseado na categoria
        if category in [ErrorCategory.NETWORK, ErrorCategory.EXTERNAL_SERVICE]:
            return True
        
        if category == ErrorCategory.AUTHENTICATION:
            return "expired" in str(error).lower() or "refresh" in str(error).lower()
        
        return False
    
    def _select_recovery_strategy(self, error: Exception, category: ErrorCategory) -> Optional[str]:
        """Seleciona estratégia de recuperação"""
        if isinstance(error, (NetworkError, gcp_exceptions.ServiceUnavailable)):
            return "network_error"
        
        if isinstance(error, (RateLimitError, gcp_exceptions.TooManyRequests)):
            return "rate_limit_error"
        
        if isinstance(error, (AuthenticationError, gcp_exceptions.Unauthenticated)):
            return "authentication_error"
        
        if isinstance(error, ConfigurationError):
            return "configuration_error"
        
        if isinstance(error, (ResourceError, gcp_exceptions.ResourceExhausted)):
            return "resource_exhausted"
        
        return None
    
    def _generate_user_message(self, error: Exception, category: ErrorCategory, severity: ErrorSeverity) -> str:
        """Gera mensagem amigável para o usuário"""
        severity_emoji = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️", 
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }
        
        emoji = severity_emoji[severity]
        
        # Mensagens específicas por categoria
        if category == ErrorCategory.NETWORK:
            return f"{emoji} Problema de conectividade detectado. Verifique sua conexão com a internet."
        
        elif category == ErrorCategory.AUTHENTICATION:
            return f"{emoji} Erro de autenticação. Verifique suas credenciais do Google Cloud."
        
        elif category == ErrorCategory.CONFIGURATION:
            return f"{emoji} Problema na configuração. Verifique os parâmetros do sistema."
        
        elif category == ErrorCategory.PROCESSING:
            return f"{emoji} Erro durante processamento. A operação não pôde ser concluída."
        
        elif category == ErrorCategory.RESOURCE:
            return f"{emoji} Recursos insuficientes. O sistema atingiu um limite."
        
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            return f"{emoji} Serviço externo temporariamente indisponível."
        
        else:
            return f"{emoji} Erro inesperado: {str(error)[:100]}"
    
    def _extract_technical_details(self, error: Exception, context: ErrorContext) -> str:
        """Extrai detalhes técnicos do erro"""
        details = []
        
        # Tipo e mensagem do erro
        details.append(f"Tipo: {type(error).__name__}")
        details.append(f"Mensagem: {str(error)}")
        
        # Contexto da operação
        if context.operation:
            details.append(f"Operação: {context.operation}")
        
        if context.component:
            details.append(f"Componente: {context.component}")
        
        # Stack trace (resumido)
        if hasattr(error, '__traceback__') and error.__traceback__:
            tb_lines = traceback.format_tb(error.__traceback__)
            if tb_lines:
                last_frame = tb_lines[-1].strip()
                details.append(f"Local: {last_frame}")
        
        # Estado do sistema
        if context.system_state:
            relevant_state = {k: v for k, v in context.system_state.items() 
                            if k in ['memory_usage', 'disk_space', 'network_status']}
            if relevant_state:
                details.append(f"Estado: {relevant_state}")
        
        return " | ".join(details)
    
    def _generate_suggestions(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> List[str]:
        """Gera sugestões para resolução"""
        suggestions = []
        
        if category == ErrorCategory.NETWORK:
            suggestions.extend([
                "Verifique sua conexão com a internet",
                "Tente novamente em alguns minutos",
                "Verifique se não há firewall bloqueando a conexão"
            ])
        
        elif category == ErrorCategory.AUTHENTICATION:
            suggestions.extend([
                "Execute 'gcloud auth application-default login'",
                "Verifique se o projeto Google Cloud está correto",
                "Confirme se você tem as permissões necessárias"
            ])
        
        elif category == ErrorCategory.CONFIGURATION:
            suggestions.extend([
                "Execute o wizard de configuração novamente",
                "Verifique o arquivo de configuração",
                "Confirme se todos os campos obrigatórios estão preenchidos"
            ])
        
        elif category == ErrorCategory.PROCESSING:
            suggestions.extend([
                "Verifique se os arquivos de entrada são válidos",
                "Tente processar um conjunto menor de arquivos",
                "Verifique os logs para mais detalhes"
            ])
        
        elif category == ErrorCategory.RESOURCE:
            suggestions.extend([
                "Feche outras aplicações para liberar memória",
                "Verifique o espaço em disco disponível",
                "Considere processar em lotes menores"
            ])
        
        # Sugestões específicas baseadas no erro
        error_str = str(error).lower()
        
        if "bucket" in error_str:
            suggestions.append("Verifique se o bucket existe e você tem acesso")
        
        if "quota" in error_str or "limit" in error_str:
            suggestions.append("Verifique suas cotas no Google Cloud Console")
        
        if "timeout" in error_str:
            suggestions.append("Aumente o timeout nas configurações")
        
        return suggestions[:5]  # Limitar a 5 sugestões
    
    def _find_related_errors(self, error: Exception, context: ErrorContext) -> List[str]:
        """Encontra erros relacionados"""
        related = []
        
        # Baseado no tipo de erro
        error_type = type(error).__name__
        
        if "Network" in error_type:
            related.extend(["ConnectionError", "TimeoutError", "ServiceUnavailable"])
        
        elif "Authentication" in error_type:
            related.extend(["PermissionDenied", "Unauthenticated", "Forbidden"])
        
        elif "Configuration" in error_type:
            related.extend(["ValidationError", "ValueError", "KeyError"])
        
        # Baseado na operação
        if context.operation == "file_upload":
            related.extend(["FileTooLarge", "InvalidFileType", "StorageError"])
        
        elif context.operation == "query_processing":
            related.extend(["QueryTimeout", "ModelError", "ResponseError"])
        
        return related[:3]  # Limitar a 3 erros relacionados
    
    def _determine_action(self, error: Exception, analysis: ErrorAnalysis, context: ErrorContext) -> Dict[str, Any]:
        """Determina ação a ser tomada"""
        if analysis.is_recoverable:
            if analysis.recovery_strategy:
                return {
                    "type": "recover",
                    "strategy": analysis.recovery_strategy,
                    "description": f"Tentando recuperação usando estratégia: {analysis.recovery_strategy}"
                }
            else:
                return {
                    "type": "retry",
                    "description": "Tentando novamente com configurações padrão"
                }
        
        elif analysis.severity == ErrorSeverity.CRITICAL:
            return {
                "type": "escalate",
                "description": "Erro crítico - intervenção manual necessária"
            }
        
        else:
            return {
                "type": "log_and_continue",
                "description": "Erro registrado - continuando operação"
            }
    
    def _execute_recovery(self, error: Exception, analysis: ErrorAnalysis, context: ErrorContext) -> Dict[str, Any]:
        """Executa estratégia de recuperação"""
        try:
            strategy = analysis.recovery_strategy
            
            if strategy == "network_error":
                return self.retry_manager.execute_with_backoff(
                    lambda: None,  # Placeholder - seria a operação real
                    max_retries=3,
                    backoff_factor=1.5
                )
            
            elif strategy == "authentication_error":
                return self.recovery_manager.refresh_authentication()
            
            elif strategy == "configuration_error":
                return self.recovery_manager.validate_and_fix_config()
            
            else:
                return {"success": False, "message": f"Estratégia {strategy} não implementada"}
        
        except Exception as recovery_error:
            return {
                "success": False,
                "message": f"Falha na recuperação: {str(recovery_error)}"
            }
    
    def _log_error(self, error: Exception, analysis: ErrorAnalysis, context: ErrorContext) -> None:
        """Registra erro com logging estruturado"""
        log_data = {
            "error_type": analysis.error_type,
            "category": analysis.category.value,
            "severity": analysis.severity.value,
            "operation": context.operation,
            "component": context.component,
            "recoverable": analysis.is_recoverable,
            "message": str(error)
        }
        
        if analysis.severity == ErrorSeverity.CRITICAL:
            self.logger.critical("Critical error occurred", extra=log_data)
        elif analysis.severity == ErrorSeverity.HIGH:
            self.logger.error("High severity error", extra=log_data)
        elif analysis.severity == ErrorSeverity.MEDIUM:
            self.logger.warning("Medium severity error", extra=log_data)
        else:
            self.logger.info("Low severity error", extra=log_data)
    
    def _update_error_stats(self, analysis: ErrorAnalysis) -> None:
        """Atualiza estatísticas de erro"""
        self.error_stats["total_errors"] += 1
        
        # Por categoria
        category = analysis.category.value
        self.error_stats["errors_by_category"][category] = \
            self.error_stats["errors_by_category"].get(category, 0) + 1
        
        # Por severidade
        severity = analysis.severity.value
        self.error_stats["errors_by_severity"][severity] = \
            self.error_stats["errors_by_severity"].get(severity, 0) + 1
        
        # Erros mais comuns
        error_type = analysis.error_type
        common_errors = dict(self.error_stats.get("most_common_errors", []))
        common_errors[error_type] = common_errors.get(error_type, 0) + 1
        
        # Manter apenas os top 10
        sorted_errors = sorted(common_errors.items(), key=lambda x: x[1], reverse=True)
        self.error_stats["most_common_errors"] = sorted_errors[:10]