#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ Exceptions - Exceções customizadas para o RAG Enhanced

Este módulo define todas as exceções específicas do sistema,
permitindo tratamento de erros mais granular e informativo.
"""

from typing import Optional, Dict, Any


class RAGEnhancedException(Exception):
    """
    🚨 Exceção base para o sistema RAG Enhanced
    
    Todas as exceções específicas do sistema herdam desta classe,
    permitindo captura genérica quando necessário.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, suggestion: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
    
    def __str__(self) -> str:
        result = f"❌ {self.message}"
        if self.suggestion:
            result += f"\n💡 Sugestão: {self.suggestion}"
        return result
    
    def get_formatted_error(self) -> str:
        """
        Retorna erro formatado para exibição ao usuário
        
        Returns:
            Mensagem de erro formatada com emoji e sugestão
        """
        return str(self)


class ConfigurationError(RAGEnhancedException):
    """
    🔧 Erro de configuração
    
    Lançado quando há problemas com configurações do sistema,
    como valores inválidos ou campos obrigatórios faltando.
    """
    
    def __init__(self, field: str, message: str, current_value: Any = None, suggestion: Optional[str] = None):
        self.field = field
        self.current_value = current_value
        
        details = {"field": field}
        if current_value is not None:
            details["current_value"] = current_value
        
        super().__init__(
            message=f"Erro na configuração '{field}': {message}",
            details=details,
            suggestion=suggestion
        )


class ProcessingError(RAGEnhancedException):
    """
    📁 Erro de processamento de arquivos
    
    Lançado durante operações de processamento, upload ou análise de arquivos.
    """
    
    def __init__(self, operation: str, message: str, file_path: Optional[str] = None, suggestion: Optional[str] = None):
        self.operation = operation
        self.file_path = file_path
        
        details = {"operation": operation}
        if file_path:
            details["file_path"] = file_path
        
        full_message = f"Erro durante {operation}"
        if file_path:
            full_message += f" do arquivo '{file_path}'"
        full_message += f": {message}"
        
        super().__init__(
            message=full_message,
            details=details,
            suggestion=suggestion
        )


class QueryError(RAGEnhancedException):
    """
    🔍 Erro de consulta
    
    Lançado quando há problemas no processamento de consultas ou
    na comunicação com os serviços de IA.
    """
    
    def __init__(self, query: str, message: str, error_type: Optional[str] = None, suggestion: Optional[str] = None):
        self.query = query
        self.error_type = error_type
        
        details = {"query": query}
        if error_type:
            details["error_type"] = error_type
        
        super().__init__(
            message=f"Erro ao processar consulta '{query[:50]}...': {message}",
            details=details,
            suggestion=suggestion
        )


class AuthenticationError(RAGEnhancedException):
    """
    🔐 Erro de autenticação
    
    Lançado quando há problemas de autenticação com Google Cloud
    ou outros serviços externos.
    """
    
    def __init__(self, service: str, message: str, suggestion: Optional[str] = None):
        self.service = service
        
        super().__init__(
            message=f"Erro de autenticação com {service}: {message}",
            details={"service": service},
            suggestion=suggestion or "Verifique suas credenciais e permissões"
        )


class NetworkError(RAGEnhancedException):
    """
    🌐 Erro de rede
    
    Lançado quando há problemas de conectividade ou timeout
    em operações de rede.
    """
    
    def __init__(self, operation: str, message: str, retry_count: int = 0, suggestion: Optional[str] = None):
        self.operation = operation
        self.retry_count = retry_count
        
        super().__init__(
            message=f"Erro de rede durante {operation}: {message}",
            details={"operation": operation, "retry_count": retry_count},
            suggestion=suggestion or "Verifique sua conexão com a internet"
        )


class ValidationError(RAGEnhancedException):
    """
    ✅ Erro de validação
    
    Lançado quando dados não passam na validação,
    seja de configuração, entrada do usuário ou estado do sistema.
    """
    
    def __init__(self, field: str, value: Any, message: str, suggestion: Optional[str] = None):
        self.field = field
        self.value = value
        
        super().__init__(
            message=f"Validação falhou para '{field}' com valor '{value}': {message}",
            details={"field": field, "value": value},
            suggestion=suggestion
        )


class ResourceError(RAGEnhancedException):
    """
    💾 Erro de recursos
    
    Lançado quando há problemas relacionados a recursos do sistema,
    como memória, espaço em disco ou limites de API.
    """
    
    def __init__(self, resource: str, message: str, current_usage: Optional[str] = None, suggestion: Optional[str] = None):
        self.resource = resource
        self.current_usage = current_usage
        
        details = {"resource": resource}
        if current_usage:
            details["current_usage"] = current_usage
        
        super().__init__(
            message=f"Problema com recurso '{resource}': {message}",
            details=details,
            suggestion=suggestion
        )


class ServiceUnavailableError(RAGEnhancedException):
    """
    🚫 Erro de serviço indisponível
    
    Lançado quando serviços externos (Google Cloud, APIs) estão
    temporariamente indisponíveis.
    """
    
    def __init__(self, service: str, message: str, retry_after: Optional[int] = None, suggestion: Optional[str] = None):
        self.service = service
        self.retry_after = retry_after
        
        details = {"service": service}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=f"Serviço '{service}' temporariamente indisponível: {message}",
            details=details,
            suggestion=suggestion or "Tente novamente em alguns minutos"
        )


class RateLimitError(RAGEnhancedException):
    """
    🚦 Erro de limite de taxa
    
    Lançado quando limites de API são atingidos.
    """
    
    def __init__(self, service: str, limit_type: str, reset_time: Optional[int] = None, suggestion: Optional[str] = None):
        self.service = service
        self.limit_type = limit_type
        self.reset_time = reset_time
        
        details = {"service": service, "limit_type": limit_type}
        if reset_time:
            details["reset_time"] = reset_time
        
        super().__init__(
            message=f"Limite de {limit_type} atingido para {service}",
            details=details,
            suggestion=suggestion or "Aguarde antes de tentar novamente"
        )


class CorruptedDataError(RAGEnhancedException):
    """
    🗂️ Erro de dados corrompidos
    
    Lançado quando dados estão corrompidos ou em formato inválido.
    """
    
    def __init__(self, data_type: str, location: str, message: str, suggestion: Optional[str] = None):
        self.data_type = data_type
        self.location = location
        
        super().__init__(
            message=f"Dados corrompidos ({data_type}) em {location}: {message}",
            details={"data_type": data_type, "location": location},
            suggestion=suggestion or "Verifique a integridade dos dados"
        )


# Mapeamento de exceções para códigos de erro
ERROR_CODES = {
    ConfigurationError: "CONFIG_ERROR",
    ProcessingError: "PROCESSING_ERROR", 
    QueryError: "QUERY_ERROR",
    AuthenticationError: "AUTH_ERROR",
    NetworkError: "NETWORK_ERROR",
    ValidationError: "VALIDATION_ERROR",
    ResourceError: "RESOURCE_ERROR",
    ServiceUnavailableError: "SERVICE_UNAVAILABLE",
    RateLimitError: "RATE_LIMIT",
    CorruptedDataError: "DATA_CORRUPTED"
}


def get_error_code(exception: Exception) -> str:
    """
    Obtém código de erro para uma exceção
    
    Args:
        exception: Exceção para obter código
        
    Returns:
        Código de erro ou "UNKNOWN_ERROR"
    """
    return ERROR_CODES.get(type(exception), "UNKNOWN_ERROR")


def create_user_friendly_error(exception: Exception) -> str:
    """
    Cria mensagem de erro amigável para o usuário
    
    Args:
        exception: Exceção para formatar
        
    Returns:
        Mensagem formatada para o usuário
    """
    if isinstance(exception, RAGEnhancedException):
        return exception.get_formatted_error()
    
    # Para exceções não customizadas, criar mensagem genérica
    error_type = type(exception).__name__
    return f"❌ Erro inesperado ({error_type}): {str(exception)}\n💡 Sugestão: Tente novamente ou contate o suporte"