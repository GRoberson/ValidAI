#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Retry Manager - Gerenciador inteligente de retry

Este módulo fornece estratégias avançadas de retry com backoff
exponencial, jitter e classificação inteligente de erros.
"""

import time
import random
import math
from typing import Callable, Any, Optional, Dict, List, Type
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from google.api_core import exceptions as gcp_exceptions

from ..core.exceptions import (
    NetworkError, AuthenticationError, RateLimitError,
    ServiceUnavailableError, ResourceError
)


class RetryStrategy(Enum):
    """Estratégias de retry disponíveis"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    ADAPTIVE = "adaptive"


@dataclass
class RetryConfig:
    """
    ⚙️ Configuração de retry
    """
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    
    def __post_init__(self):
        if self.max_retries < 0:
            self.max_retries = 0
        if self.base_delay < 0:
            self.base_delay = 0.1
        if self.backoff_factor < 1:
            self.backoff_factor = 1.0


@dataclass
class RetryAttempt:
    """
    📊 Informações sobre uma tentativa de retry
    """
    attempt_number: int
    delay_used: float
    error: Optional[Exception]
    timestamp: datetime
    success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "attempt_number": self.attempt_number,
            "delay_used": self.delay_used,
            "error": str(self.error) if self.error else None,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success
        }


@dataclass
class RetryResult:
    """
    📈 Resultado de uma operação com retry
    """
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    attempts: List[RetryAttempt] = None
    total_time: float = 0.0
    
    def __post_init__(self):
        if self.attempts is None:
            self.attempts = []
    
    @property
    def attempt_count(self) -> int:
        return len(self.attempts)
    
    @property
    def final_delay(self) -> float:
        return self.attempts[-1].delay_used if self.attempts else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error": str(self.error) if self.error else None,
            "attempt_count": self.attempt_count,
            "total_time": self.total_time,
            "attempts": [attempt.to_dict() for attempt in self.attempts]
        }


class RetryManager:
    """
    🔄 Gerenciador inteligente de retry
    
    Fornece estratégias avançadas de retry incluindo:
    - Backoff exponencial com jitter
    - Classificação inteligente de erros
    - Estratégias adaptativas
    - Métricas detalhadas de retry
    - Configuração por tipo de operação
    """
    
    def __init__(self):
        """Inicializa o gerenciador de retry"""
        
        # Configurações por tipo de erro
        self.error_configs = self._build_error_configs()
        
        # Configurações por operação
        self.operation_configs = self._build_operation_configs()
        
        # Tipos de erro que nunca devem ser retried
        self.non_retryable_errors = {
            KeyboardInterrupt,
            SystemExit,
            MemoryError,
            AuthenticationError,  # Geralmente requer intervenção manual
        }
        
        # Tipos de erro que são sempre retryable
        self.always_retryable_errors = {
            NetworkError,
            gcp_exceptions.ServiceUnavailable,
            gcp_exceptions.DeadlineExceeded,
            gcp_exceptions.InternalServerError,
            ConnectionError,
            TimeoutError,
        }
        
        # Estatísticas
        self.retry_stats = {
            "total_operations": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "avg_attempts": 0.0,
            "avg_total_time": 0.0,
            "success_rate_by_error_type": {},
            "most_retried_errors": {}
        }
    
    def execute_with_retry(self, 
                          operation: Callable,
                          config: Optional[RetryConfig] = None,
                          operation_type: Optional[str] = None,
                          error_context: Optional[Dict] = None) -> RetryResult:
        """
        Executa operação com retry inteligente
        
        Args:
            operation: Função a ser executada
            config: Configuração de retry (opcional)
            operation_type: Tipo da operação para configuração específica
            error_context: Contexto adicional para decisões de retry
            
        Returns:
            Resultado da operação com detalhes de retry
        """
        start_time = time.time()
        
        # Determinar configuração
        if config is None:
            config = self._get_config_for_operation(operation_type)
        
        result = RetryResult()
        last_error = None
        
        for attempt in range(config.max_retries + 1):  # +1 para tentativa inicial
            try:
                # Executar operação
                operation_result = operation()
                
                # Sucesso!
                result.success = True
                result.result = operation_result
                
                # Registrar tentativa bem-sucedida
                attempt_info = RetryAttempt(
                    attempt_number=attempt + 1,
                    delay_used=0.0,
                    error=None,
                    timestamp=datetime.now(),
                    success=True
                )
                result.attempts.append(attempt_info)
                
                break
                
            except Exception as error:
                last_error = error
                
                # Verificar se deve tentar novamente
                if not self.should_retry(error, attempt, config, error_context):
                    result.success = False
                    result.error = error
                    break
                
                # Calcular delay
                delay = self._calculate_delay(attempt, config, error)
                
                # Registrar tentativa
                attempt_info = RetryAttempt(
                    attempt_number=attempt + 1,
                    delay_used=delay,
                    error=error,
                    timestamp=datetime.now(),
                    success=False
                )
                result.attempts.append(attempt_info)
                
                # Aguardar antes da próxima tentativa (exceto na última)
                if attempt < config.max_retries:
                    time.sleep(delay)
        
        # Se chegou aqui sem sucesso, falhou
        if not result.success:
            result.error = last_error
        
        result.total_time = time.time() - start_time
        
        # Atualizar estatísticas
        self._update_stats(result, last_error)
        
        return result
    
    def execute_with_backoff(self, 
                           operation: Callable,
                           max_retries: int = 3,
                           backoff_factor: float = 2.0,
                           base_delay: float = 1.0) -> Dict[str, Any]:
        """
        Executa operação com backoff exponencial simples
        
        Args:
            operation: Função a ser executada
            max_retries: Número máximo de tentativas
            backoff_factor: Fator de multiplicação do delay
            base_delay: Delay base em segundos
            
        Returns:
            Resultado da operação
        """
        config = RetryConfig(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            base_delay=base_delay,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        result = self.execute_with_retry(operation, config)
        
        return {
            "success": result.success,
            "result": result.result,
            "error": str(result.error) if result.error else None,
            "attempts": result.attempt_count,
            "total_time": result.total_time
        }
    
    def should_retry(self, 
                    error: Exception, 
                    attempt_count: int,
                    config: Optional[RetryConfig] = None,
                    context: Optional[Dict] = None) -> bool:
        """
        Determina se deve tentar novamente após um erro
        
        Args:
            error: Exceção ocorrida
            attempt_count: Número de tentativas já realizadas
            config: Configuração de retry
            context: Contexto adicional
            
        Returns:
            True se deve tentar novamente
        """
        # Verificar limite de tentativas
        if config and attempt_count >= config.max_retries:
            return False
        
        # Erros que nunca devem ser retried
        if any(isinstance(error, err_type) for err_type in self.non_retryable_errors):
            return False
        
        # Erros que sempre devem ser retried
        if any(isinstance(error, err_type) for err_type in self.always_retryable_errors):
            return True
        
        # Rate limiting - sempre retry com delay maior
        if isinstance(error, (RateLimitError, gcp_exceptions.TooManyRequests)):
            return True
        
        # Erros de recurso - retry com cuidado
        if isinstance(error, (ResourceError, gcp_exceptions.ResourceExhausted)):
            return attempt_count < 2  # Máximo 2 tentativas
        
        # Análise baseada na mensagem do erro
        error_str = str(error).lower()
        
        # Erros temporários
        temporary_indicators = [
            'timeout', 'temporary', 'unavailable', 'busy',
            'overloaded', 'throttled', 'rate limit'
        ]
        
        if any(indicator in error_str for indicator in temporary_indicators):
            return True
        
        # Erros permanentes
        permanent_indicators = [
            'not found', 'invalid', 'forbidden', 'unauthorized',
            'bad request', 'malformed', 'syntax error'
        ]
        
        if any(indicator in error_str for indicator in permanent_indicators):
            return False
        
        # Contexto específico
        if context:
            operation = context.get('operation', '')
            
            # Para uploads, ser mais agressivo com retry
            if 'upload' in operation:
                return attempt_count < 5
            
            # Para queries, menos agressivo
            if 'query' in operation:
                return attempt_count < 2
        
        # Padrão: retry para erros desconhecidos (conservador)
        return attempt_count < 1
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de retry
        
        Returns:
            Estatísticas detalhadas
        """
        return self.retry_stats.copy()
    
    def reset_stats(self) -> None:
        """Reseta estatísticas de retry"""
        self.retry_stats = {
            "total_operations": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "avg_attempts": 0.0,
            "avg_total_time": 0.0,
            "success_rate_by_error_type": {},
            "most_retried_errors": {}
        }
    
    def _calculate_delay(self, attempt: int, config: RetryConfig, error: Exception) -> float:
        """Calcula delay para próxima tentativa"""
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_factor ** attempt)
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        
        elif config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = config.base_delay * self._fibonacci(attempt + 1)
        
        elif config.strategy == RetryStrategy.ADAPTIVE:
            delay = self._adaptive_delay(attempt, config, error)
        
        else:
            delay = config.base_delay * (config.backoff_factor ** attempt)
        
        # Aplicar limite máximo
        delay = min(delay, config.max_delay)
        
        # Aplicar jitter se habilitado
        if config.jitter:
            jitter_amount = delay * config.jitter_factor
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0.1, delay + jitter)
        
        return delay
    
    def _adaptive_delay(self, attempt: int, config: RetryConfig, error: Exception) -> float:
        """Calcula delay adaptativo baseado no tipo de erro"""
        base_delay = config.base_delay
        
        # Rate limiting - delay maior
        if isinstance(error, (RateLimitError, gcp_exceptions.TooManyRequests)):
            return base_delay * (5 ** attempt)  # Crescimento mais agressivo
        
        # Erros de rede - delay moderado
        if isinstance(error, (NetworkError, gcp_exceptions.ServiceUnavailable)):
            return base_delay * (2 ** attempt)
        
        # Erros de recurso - delay linear
        if isinstance(error, (ResourceError, gcp_exceptions.ResourceExhausted)):
            return base_delay * (attempt + 1) * 2
        
        # Padrão
        return base_delay * (config.backoff_factor ** attempt)
    
    def _fibonacci(self, n: int) -> int:
        """Calcula número de Fibonacci"""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        
        return b
    
    def _get_config_for_operation(self, operation_type: Optional[str]) -> RetryConfig:
        """Obtém configuração específica para tipo de operação"""
        if operation_type and operation_type in self.operation_configs:
            return self.operation_configs[operation_type]
        
        return RetryConfig()  # Configuração padrão
    
    def _build_error_configs(self) -> Dict[Type[Exception], RetryConfig]:
        """Constrói configurações específicas por tipo de erro"""
        return {
            NetworkError: RetryConfig(
                max_retries=5,
                base_delay=1.0,
                backoff_factor=2.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            
            RateLimitError: RetryConfig(
                max_retries=3,
                base_delay=5.0,
                backoff_factor=3.0,
                strategy=RetryStrategy.ADAPTIVE
            ),
            
            gcp_exceptions.ServiceUnavailable: RetryConfig(
                max_retries=4,
                base_delay=2.0,
                backoff_factor=2.5,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            
            gcp_exceptions.DeadlineExceeded: RetryConfig(
                max_retries=3,
                base_delay=1.5,
                backoff_factor=2.0,
                strategy=RetryStrategy.LINEAR_BACKOFF
            ),
            
            ResourceError: RetryConfig(
                max_retries=2,
                base_delay=3.0,
                backoff_factor=1.5,
                strategy=RetryStrategy.LINEAR_BACKOFF
            )
        }
    
    def _build_operation_configs(self) -> Dict[str, RetryConfig]:
        """Constrói configurações específicas por tipo de operação"""
        return {
            "file_upload": RetryConfig(
                max_retries=5,
                base_delay=2.0,
                backoff_factor=2.0,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            
            "query_processing": RetryConfig(
                max_retries=3,
                base_delay=1.0,
                backoff_factor=1.5,
                max_delay=15.0,
                strategy=RetryStrategy.ADAPTIVE
            ),
            
            "authentication": RetryConfig(
                max_retries=2,
                base_delay=1.0,
                backoff_factor=2.0,
                max_delay=10.0,
                strategy=RetryStrategy.FIXED_DELAY
            ),
            
            "corpus_creation": RetryConfig(
                max_retries=3,
                base_delay=5.0,
                backoff_factor=2.0,
                max_delay=60.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            ),
            
            "file_analysis": RetryConfig(
                max_retries=2,
                base_delay=0.5,
                backoff_factor=1.5,
                max_delay=5.0,
                strategy=RetryStrategy.LINEAR_BACKOFF
            )
        }
    
    def _update_stats(self, result: RetryResult, error: Optional[Exception]) -> None:
        """Atualiza estatísticas de retry"""
        self.retry_stats["total_operations"] += 1
        
        if result.success:
            if result.attempt_count > 1:
                self.retry_stats["successful_retries"] += 1
        else:
            self.retry_stats["failed_retries"] += 1
        
        # Atualizar médias
        total_ops = self.retry_stats["total_operations"]
        
        # Média de tentativas
        current_avg_attempts = self.retry_stats["avg_attempts"]
        new_avg_attempts = ((current_avg_attempts * (total_ops - 1)) + result.attempt_count) / total_ops
        self.retry_stats["avg_attempts"] = new_avg_attempts
        
        # Média de tempo total
        current_avg_time = self.retry_stats["avg_total_time"]
        new_avg_time = ((current_avg_time * (total_ops - 1)) + result.total_time) / total_ops
        self.retry_stats["avg_total_time"] = new_avg_time
        
        # Estatísticas por tipo de erro
        if error:
            error_type = type(error).__name__
            
            if error_type not in self.retry_stats["success_rate_by_error_type"]:
                self.retry_stats["success_rate_by_error_type"][error_type] = {
                    "total": 0, "successful": 0, "rate": 0.0
                }
            
            error_stats = self.retry_stats["success_rate_by_error_type"][error_type]
            error_stats["total"] += 1
            
            if result.success:
                error_stats["successful"] += 1
            
            error_stats["rate"] = error_stats["successful"] / error_stats["total"]
            
            # Erros mais retried
            if error_type not in self.retry_stats["most_retried_errors"]:
                self.retry_stats["most_retried_errors"][error_type] = 0
            
            self.retry_stats["most_retried_errors"][error_type] += result.attempt_count