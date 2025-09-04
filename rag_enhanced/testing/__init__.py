#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 RAG Enhanced Testing Module

Este módulo fornece um framework completo de testes para o sistema RAG Enhanced,
incluindo mocks, geradores de dados, validadores e framework de execução.

Componentes principais:
- TestFramework: Framework principal de execução de testes
- TestRunner: Interface simplificada para execução
- MockServices: Serviços simulados para testes offline
- TestDataGenerator: Gerador de dados de teste realistas
- TestValidators: Validadores abrangentes
- SchemaValidator: Validação contra schemas

Exemplo de uso:
    from rag_enhanced.testing import TestRunner
    
    runner = TestRunner()
    results = runner.run_full_test()
    print(f"Sucesso: {results['summary']['success_rate']:.1f}%")
"""

from .framework import TestFramework, TestRunner, TestResult, TestSuiteResult
from .mocks import (
    MockServices, 
    MockCloudStorage, 
    MockVertexAI, 
    MockGenAI,
    MockFileSystem,
    MockFile
)
from .generators import TestDataGenerator, TestFile
from .validators import TestValidators, SchemaValidator, ValidationResult

# Versão do módulo de testes
__version__ = "1.0.0"

# Exports principais
__all__ = [
    # Framework principal
    "TestFramework",
    "TestRunner",
    "TestResult", 
    "TestSuiteResult",
    
    # Mocks
    "MockServices",
    "MockCloudStorage",
    "MockVertexAI", 
    "MockGenAI",
    "MockFileSystem",
    "MockFile",
    
    # Geradores
    "TestDataGenerator",
    "TestFile",
    
    # Validadores
    "TestValidators",
    "SchemaValidator", 
    "ValidationResult",
    
    # Utilitários
    "create_test_suite",
    "run_quick_test",
    "run_full_test",
    "validate_system"
]


def create_test_suite(name: str = "default") -> TestFramework:
    """
    Cria uma nova suíte de testes
    
    Args:
        name: Nome da suíte de testes
        
    Returns:
        Instância do TestFramework configurada
    """
    framework = TestFramework()
    framework.suite_name = name
    return framework


def run_quick_test() -> dict:
    """
    Executa teste rápido (apenas unitários)
    
    Returns:
        Resultados do teste rápido
    """
    runner = TestRunner()
    return runner.run_quick_test()


def run_full_test() -> dict:
    """
    Executa teste completo (todos os tipos)
    
    Returns:
        Resultados do teste completo
    """
    runner = TestRunner()
    return runner.run_full_test()


def validate_system() -> dict:
    """
    Valida saúde do sistema
    
    Returns:
        Relatório de saúde do sistema
    """
    runner = TestRunner()
    return runner.check_system_health()


# Configurações padrão para testes
DEFAULT_TEST_CONFIG = {
    "mock_scenarios": {
        "normal": {
            "failure_rate": 0.0,
            "latency_multiplier": 1.0,
            "rate_limit_threshold": 100
        },
        "high_latency": {
            "failure_rate": 0.0,
            "latency_multiplier": 3.0,
            "rate_limit_threshold": 100
        },
        "network_issues": {
            "failure_rate": 0.2,
            "latency_multiplier": 1.0,
            "rate_limit_threshold": 100
        },
        "rate_limiting": {
            "failure_rate": 0.0,
            "latency_multiplier": 1.0,
            "rate_limit_threshold": 10
        },
        "service_degradation": {
            "failure_rate": 0.1,
            "latency_multiplier": 2.0,
            "rate_limit_threshold": 50
        }
    },
    "test_data": {
        "default_file_count": 10,
        "default_query_count": 20,
        "supported_languages": ["python", "javascript", "java", "markdown", "json"],
        "complexity_levels": ["low", "medium", "high"]
    },
    "validation": {
        "max_file_size_mb": 100,
        "max_batch_size": 1000,
        "max_timeout_seconds": 300,
        "supported_extensions": [
            ".py", ".js", ".java", ".cpp", ".c", ".h", ".hpp",
            ".md", ".txt", ".json", ".yaml", ".yml", ".xml",
            ".html", ".css", ".sql", ".sh", ".bat", ".ps1"
        ]
    },
    "performance": {
        "max_response_time": 30.0,
        "min_success_rate": 0.8,
        "max_error_rate": 0.2,
        "max_cpu_usage": 80.0,
        "max_memory_usage": 80.0
    }
}


class TestingError(Exception):
    """Exceção base para erros de teste"""
    pass


class MockError(TestingError):
    """Exceção para erros de mock"""
    pass


class ValidationError(TestingError):
    """Exceção para erros de validação"""
    pass


class TestExecutionError(TestingError):
    """Exceção para erros de execução de teste"""
    pass


# Utilitários de conveniência
def setup_test_environment():
    """
    Configura ambiente de teste padrão
    
    Returns:
        Tupla com (framework, mock_services, generators, validators)
    """
    framework = TestFramework()
    mock_services = MockServices()
    generators = TestDataGenerator()
    validators = TestValidators()
    
    return framework, mock_services, generators, validators


def cleanup_test_environment(framework: TestFramework):
    """
    Limpa ambiente de teste
    
    Args:
        framework: Framework de teste a ser limpo
    """
    if hasattr(framework, '_cleanup_test_environment'):
        framework._cleanup_test_environment()


# Decoradores para testes
def mock_scenario(scenario_name: str):
    """
    Decorator para configurar cenário de mock
    
    Args:
        scenario_name: Nome do cenário a ser configurado
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Configurar cenário antes da execução
            if hasattr(args[0], 'mock_services'):
                args[0].mock_services.setup_scenario(scenario_name)
            
            try:
                return func(*args, **kwargs)
            finally:
                # Resetar após execução
                if hasattr(args[0], 'mock_services'):
                    args[0].mock_services.reset_all_mocks()
        
        return wrapper
    return decorator


def test_timeout(seconds: int):
    """
    Decorator para definir timeout de teste
    
    Args:
        seconds: Timeout em segundos
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Teste excedeu timeout de {seconds} segundos")
            
            # Configurar timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Cancelar timeout
        
        return wrapper
    return decorator


# Informações do módulo
def get_module_info():
    """
    Obtém informações sobre o módulo de testes
    
    Returns:
        Dicionário com informações do módulo
    """
    return {
        "name": "RAG Enhanced Testing Module",
        "version": __version__,
        "description": __doc__.strip(),
        "components": {
            "framework": "Framework principal de execução de testes",
            "mocks": "Serviços simulados para testes offline", 
            "generators": "Geradores de dados de teste realistas",
            "validators": "Validadores abrangentes de dados e resultados"
        },
        "features": [
            "Testes unitários automatizados",
            "Testes de integração com mocks",
            "Testes de performance e carga",
            "Validação automática de resultados",
            "Geração de dados de teste realistas",
            "Cenários de erro simulados",
            "Relatórios detalhados",
            "Health checks do sistema"
        ],
        "supported_scenarios": list(DEFAULT_TEST_CONFIG["mock_scenarios"].keys()),
        "supported_languages": DEFAULT_TEST_CONFIG["test_data"]["supported_languages"]
    }


if __name__ == "__main__":
    # Exemplo de uso quando executado diretamente
    print("🧪 RAG Enhanced Testing Module")
    print("=" * 50)
    
    info = get_module_info()
    print(f"Versão: {info['version']}")
    print(f"Componentes: {len(info['components'])}")
    print(f"Funcionalidades: {len(info['features'])}")
    
    print("\n🚀 Executando teste rápido...")
    results = run_quick_test()
    print(f"✅ Teste concluído: {results['success_rate']:.1f}% sucesso")
    
    print("\n🏥 Verificando saúde do sistema...")
    health = validate_system()
    status = "✅ Saudável" if health['overall_healthy'] else "❌ Problemas detectados"
    print(f"Status: {status}")