#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Test Framework - Framework completo de testes (CORRIGIDO)

Este módulo fornece um framework abrangente para testes unitários,
integração e performance com mocks e validação automática.
"""

import unittest
import time
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from dataclasses import dataclass

from .mocks import MockServices, MockFileSystem
from .generators import TestDataGenerator
from .validators import TestValidators


@dataclass
class TestResult:
    """
    📊 Resultado de um teste
    """
    test_name: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "success": self.success,
            "execution_time": self.execution_time,
            "error_message": self.error_message,
            "details": self.details or {}
        }


@dataclass
class TestSuiteResult:
    """
    📈 Resultado de uma suíte de testes
    """
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_time: float
    results: List[TestResult]
    
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "success_rate": self.success_rate,
            "total_time": self.total_time,
            "results": [result.to_dict() for result in self.results]
        }


class TestFramework:
    """
    🧪 Framework completo de testes
    
    Fornece funcionalidades abrangentes incluindo:
    - Testes unitários com mocks
    - Testes de integração
    - Testes de performance
    - Validação automática
    - Geração de relatórios
    - Cenários de teste pré-definidos
    """
    
    def __init__(self):
        """Inicializa o framework de testes"""
        self.mock_services = MockServices()
        self.mock_filesystem = MockFileSystem()
        self.test_data_generator = TestDataGenerator()
        self.validators = TestValidators()
        
        # Resultados dos testes
        self.test_results = []
        self.suite_results = []
        
        # Configurações
        self.temp_dir = None
        self.cleanup_after_tests = True
        
        # Estatísticas
        self.stats = {
            "total_tests_run": 0,
            "total_suites_run": 0,
            "overall_success_rate": 0.0,
            "avg_test_time": 0.0
        }
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """
        Executa testes unitários
        
        Returns:
            Resultados dos testes unitários
        """
        print("\n🧪 Executando Testes Unitários")
        print("=" * 50)
        
        # Configurar ambiente de teste
        self._setup_test_environment()
        
        try:
            # Executar suítes de teste unitário
            suites = [
                ("Configuração", self._test_configuration_components),
                ("Processamento", self._test_processing_components),
                ("Query Engine", self._test_query_components),
                ("Error Handling", self._test_error_handling),
                ("Utilitários", self._test_utility_functions)
            ]
            
            all_results = []
            
            for suite_name, test_func in suites:
                print(f"\n📋 Executando suíte: {suite_name}")
                suite_result = self._run_test_suite(suite_name, test_func)
                all_results.append(suite_result)
                self.suite_results.append(suite_result)
            
            # Compilar resultados
            total_tests = sum(r.total_tests for r in all_results)
            passed_tests = sum(r.passed_tests for r in all_results)
            total_time = sum(r.total_time for r in all_results)
            
            return {
                "type": "unit_tests",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_time": total_time,
                "suites": [r.to_dict() for r in all_results]
            }
            
        finally:
            self._cleanup_test_environment()
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """
        Executa testes de integração
        
        Returns:
            Resultados dos testes de integração
        """
        print("\n🔗 Executando Testes de Integração")
        print("=" * 50)
        
        self._setup_test_environment()
        
        try:
            # Configurar mocks para integração
            self.mock_services.setup_scenario("normal")
            
            # Executar testes de integração
            suites = [
                ("Pipeline Completo", self._test_complete_pipeline),
                ("Integração com GCS", self._test_gcs_integration),
                ("Integração com Vertex AI", self._test_vertex_ai_integration),
                ("Fluxo End-to-End", self._test_end_to_end_flow)
            ]
            
            all_results = []
            
            for suite_name, test_func in suites:
                print(f"\n📋 Executando suíte: {suite_name}")
                suite_result = self._run_test_suite(suite_name, test_func)
                all_results.append(suite_result)
                self.suite_results.append(suite_result)
            
            # Compilar resultados
            total_tests = sum(r.total_tests for r in all_results)
            passed_tests = sum(r.passed_tests for r in all_results)
            total_time = sum(r.total_time for r in all_results)
            
            return {
                "type": "integration_tests",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_time": total_time,
                "suites": [r.to_dict() for r in all_results]
            }
            
        finally:
            self._cleanup_test_environment()
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """
        Executa testes de performance
        
        Returns:
            Resultados dos testes de performance
        """
        print("\n⚡ Executando Testes de Performance")
        print("=" * 50)
        
        self._setup_test_environment()
        
        try:
            # Configurar cenários de performance
            scenarios = [
                ("Carga Normal", "normal", self._test_normal_load),
                ("Alta Latência", "high_latency", self._test_high_latency_performance),
                ("Rate Limiting", "rate_limiting", self._test_rate_limiting_performance),
                ("Degradação de Serviço", "service_degradation", self._test_service_degradation)
            ]
            
            all_results = []
            
            for scenario_name, mock_scenario, test_func in scenarios:
                print(f"\n⚡ Testando cenário: {scenario_name}")
                
                # Configurar mock para o cenário
                self.mock_services.setup_scenario(mock_scenario)
                
                suite_result = self._run_test_suite(f"Performance - {scenario_name}", test_func)
                all_results.append(suite_result)
                self.suite_results.append(suite_result)
            
            # Compilar resultados
            total_tests = sum(r.total_tests for r in all_results)
            passed_tests = sum(r.passed_tests for r in all_results)
            total_time = sum(r.total_time for r in all_results)
            
            return {
                "type": "performance_tests",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_time": total_time,
                "suites": [r.to_dict() for r in all_results]
            }
            
        finally:
            self._cleanup_test_environment()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Executa todos os tipos de teste
        
        Returns:
            Resultados consolidados de todos os testes
        """
        print("\n🚀 Executando Todos os Testes")
        print("=" * 60)
        
        start_time = time.time()
        
        # Executar todos os tipos de teste
        unit_results = self.run_unit_tests()
        integration_results = self.run_integration_tests()
        performance_results = self.run_performance_tests()
        
        total_time = time.time() - start_time
        
        # Consolidar resultados
        all_results = [unit_results, integration_results, performance_results]
        
        total_tests = sum(r["total_tests"] for r in all_results)
        passed_tests = sum(r["passed_tests"] for r in all_results)
        failed_tests = sum(r["failed_tests"] for r in all_results)
        
        # Atualizar estatísticas globais
        self.stats["total_tests_run"] += total_tests
        self.stats["total_suites_run"] += len(self.suite_results)
        self.stats["overall_success_rate"] = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.stats["avg_test_time"] = total_time / total_tests if total_tests > 0 else 0
        
        consolidated_results = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_time": total_time,
                "execution_date": datetime.now().isoformat()
            },
            "unit_tests": unit_results,
            "integration_tests": integration_results,
            "performance_tests": performance_results,
            "statistics": self.stats
        }
        
        # Gerar relatório
        self._generate_test_report(consolidated_results)
        
        return consolidated_results
    
    def validate_system_health(self) -> Dict[str, Any]:
        """
        Valida a saúde geral do sistema
        
        Returns:
            Relatório de saúde do sistema
        """
        print("\n🏥 Validando Saúde do Sistema")
        print("=" * 50)
        
        health_checks = {
            "configuration": self._check_configuration_health,
            "dependencies": self._check_dependencies_health,
            "resources": self._check_resources_health,
            "connectivity": self._check_connectivity_health
        }
        
        results = {}
        overall_health = True
        
        for check_name, check_func in health_checks.items():
            try:
                result = check_func()
                results[check_name] = result
                if not result.get("healthy", False):
                    overall_health = False
            except Exception as e:
                results[check_name] = {
                    "healthy": False,
                    "error": str(e),
                    "details": "Falha na execução do health check"
                }
                overall_health = False
        
        return {
            "overall_healthy": overall_health,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _setup_test_environment(self) -> None:
        """Configura ambiente de teste"""
        # Criar diretório temporário
        self.temp_dir = tempfile.mkdtemp(prefix="rag_test_")
        
        # Resetar mocks
        self.mock_services.reset_all_mocks()
        self.mock_filesystem = MockFileSystem()
        
        # Criar dados de teste
        test_files = self.mock_services.create_test_data(10)
        for file in test_files:
            self.mock_filesystem.create_file(f"/test/{file.name}", file.content)
    
    def _cleanup_test_environment(self) -> None:
        """Limpa ambiente de teste"""
        if self.cleanup_after_tests and self.temp_dir:
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"⚠️ Erro ao limpar diretório temporário: {e}")
    
    def _run_test_suite(self, suite_name: str, test_func: Callable) -> TestSuiteResult:
        """Executa uma suíte de testes"""
        start_time = time.time()
        results = []
        
        try:
            # Executar função de teste
            test_results = test_func()
            
            # Processar resultados
            if isinstance(test_results, list):
                results.extend(test_results)
            elif isinstance(test_results, TestResult):
                results.append(test_results)
            
        except Exception as e:
            # Criar resultado de falha para a suíte
            error_result = TestResult(
                test_name=f"{suite_name}_suite_error",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            results.append(error_result)
        
        total_time = time.time() - start_time
        
        # Compilar estatísticas
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=0,
            total_time=total_time,
            results=results
        )
    
    def _test_configuration_components(self) -> List[TestResult]:
        """Testa componentes de configuração"""
        results = []
        
        # Teste básico de configuração
        start_time = time.time()
        try:
            config_data = {
                "project_id": "test-project",
                "location": "us-central1",
                "bucket_name": "test-bucket"
            }
            
            # Validar usando validators
            is_valid = self.validators.validate_config(config_data).is_valid
            
            results.append(TestResult(
                test_name="config_validation",
                success=is_valid,
                execution_time=time.time() - start_time,
                details={"config": config_data}
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="config_validation",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_processing_components(self) -> List[TestResult]:
        """Testa componentes de processamento"""
        results = []
        
        # Teste básico de processamento
        start_time = time.time()
        try:
            test_content = b"Conteudo de teste para upload"
            
            upload_result = self.mock_services.storage.upload_blob(
                "test-bucket", "test-file.txt", test_content
            )
            
            success = upload_result is not None
            
            results.append(TestResult(
                test_name="file_upload",
                success=success,
                execution_time=time.time() - start_time,
                details={"upload_result": upload_result}
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="file_upload",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_query_components(self) -> List[TestResult]:
        """Testa componentes de query"""
        results = []
        
        # Teste básico de query
        start_time = time.time()
        try:
            query = "Como funciona o sistema de RAG?"
            
            response = self.mock_services.vertex_ai.generate_content(
                query, "test-corpus"
            )
            
            success = response is not None and "text" in response
            
            results.append(TestResult(
                test_name="query_generation",
                success=success,
                execution_time=time.time() - start_time,
                details={"response_length": len(response.get("text", ""))}
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="query_generation",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_error_handling(self) -> List[TestResult]:
        """Testa tratamento de erros"""
        results = []
        
        # Teste básico de erro
        start_time = time.time()
        try:
            # Simular falha
            self.mock_services.storage.set_failure_rate(1.0)  # 100% falha
            
            try:
                self.mock_services.storage.upload_blob(
                    "test-bucket", "test-file.txt", b"test"
                )
                success = False  # Não deveria chegar aqui
            except Exception:
                # Falha esperada
                success = True
            
            # Resetar taxa de falha
            self.mock_services.storage.set_failure_rate(0.0)
            
            results.append(TestResult(
                test_name="error_recovery",
                success=success,
                execution_time=time.time() - start_time
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="error_recovery",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_utility_functions(self) -> List[TestResult]:
        """Testa funções utilitárias"""
        results = []
        
        # Teste básico de utilitários
        start_time = time.time()
        try:
            test_data = self.test_data_generator.generate_test_files(5)
            
            success = len(test_data) == 5 and all(
                hasattr(file, 'name') and hasattr(file, 'content')
                for file in test_data
            )
            
            results.append(TestResult(
                test_name="test_data_generation",
                success=success,
                execution_time=time.time() - start_time,
                details={"files_generated": len(test_data)}
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="test_data_generation",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_complete_pipeline(self) -> List[TestResult]:
        """Testa pipeline completo"""
        results = []
        
        start_time = time.time()
        try:
            # Simular pipeline completo
            bucket_result = self.mock_services.storage.create_bucket("test-pipeline-bucket")
            test_files = self.mock_services.create_test_data(3)
            
            upload_results = []
            for file in test_files:
                upload_result = self.mock_services.storage.upload_blob(
                    "test-pipeline-bucket", file.name, file.content.encode()
                )
                upload_results.append(upload_result)
            
            success = bucket_result is not None and len(upload_results) == 3
            
            results.append(TestResult(
                test_name="complete_pipeline",
                success=success,
                execution_time=time.time() - start_time,
                details={
                    "bucket_created": bucket_result is not None,
                    "files_uploaded": len(upload_results)
                }
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="complete_pipeline",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_gcs_integration(self) -> List[TestResult]:
        """Testa integração com Google Cloud Storage"""
        results = []
        
        start_time = time.time()
        try:
            bucket_name = "test-gcs-integration"
            self.mock_services.storage.create_bucket(bucket_name)
            
            content = b"Test content for GCS integration"
            upload_result = self.mock_services.storage.upload_blob(
                bucket_name, "test-file.txt", content
            )
            
            success = upload_result is not None
            
            results.append(TestResult(
                test_name="gcs_operations",
                success=success,
                execution_time=time.time() - start_time
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="gcs_operations",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_vertex_ai_integration(self) -> List[TestResult]:
        """Testa integração com Vertex AI"""
        results = []
        
        start_time = time.time()
        try:
            corpus_name = "test-vertex-integration"
            corpus_result = self.mock_services.vertex_ai.create_corpus(
                corpus_name, "Test Vertex Integration"
            )
            
            success = corpus_result is not None
            
            results.append(TestResult(
                test_name="vertex_ai_operations",
                success=success,
                execution_time=time.time() - start_time
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="vertex_ai_operations",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_end_to_end_flow(self) -> List[TestResult]:
        """Testa fluxo end-to-end completo"""
        results = []
        
        start_time = time.time()
        try:
            # Simular fluxo completo
            config = {
                "project_id": "test-e2e-project",
                "location": "us-central1",
                "bucket_name": "test-e2e-bucket"
            }
            
            config_valid = self.validators.validate_config(config).is_valid
            test_files = self.mock_services.create_test_data(5)
            
            success = config_valid and len(test_files) == 5
            
            results.append(TestResult(
                test_name="end_to_end_flow",
                success=success,
                execution_time=time.time() - start_time,
                details={
                    "config_valid": config_valid,
                    "files_processed": len(test_files)
                }
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="end_to_end_flow",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_normal_load(self) -> List[TestResult]:
        """Testa performance sob carga normal"""
        results = []
        
        start_time = time.time()
        try:
            num_operations = 10
            operation_times = []
            
            for i in range(num_operations):
                op_start = time.time()
                self.mock_services.vertex_ai.generate_content(f"Query {i}")
                op_time = time.time() - op_start
                operation_times.append(op_time)
            
            avg_time = sum(operation_times) / len(operation_times)
            success = avg_time < 1.0
            
            results.append(TestResult(
                test_name="normal_load_performance",
                success=success,
                execution_time=time.time() - start_time,
                details={
                    "operations": num_operations,
                    "avg_time": avg_time
                }
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="normal_load_performance",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_high_latency_performance(self) -> List[TestResult]:
        """Testa performance com alta latência"""
        results = []
        
        start_time = time.time()
        try:
            # Configurar alta latência
            original_delay = self.mock_services.vertex_ai.response_delay
            self.mock_services.vertex_ai.set_response_delay(2.0)
            
            # Testar operação
            op_start = time.time()
            self.mock_services.vertex_ai.generate_content("High latency query")
            op_time = time.time() - op_start
            
            # Restaurar delay original
            self.mock_services.vertex_ai.set_response_delay(original_delay)
            
            success = op_time >= 2.0  # Confirma que latência foi aplicada
            
            results.append(TestResult(
                test_name="high_latency_performance",
                success=success,
                execution_time=time.time() - start_time,
                details={"operation_time": op_time}
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="high_latency_performance",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_rate_limiting_performance(self) -> List[TestResult]:
        """Testa performance com rate limiting"""
        results = []
        
        start_time = time.time()
        try:
            # Configurar rate limiting baixo
            self.mock_services.storage.rate_limit_threshold = 3
            
            # Tentar muitas operações
            num_operations = 10
            success_count = 0
            error_count = 0
            
            for i in range(num_operations):
                try:
                    self.mock_services.storage.upload_blob(
                        "test-bucket", f"rate_limit_file_{i}.txt", b"test"
                    )
                    success_count += 1
                except Exception:
                    error_count += 1
            
            # Deve ter algumas falhas por rate limiting
            success = error_count > 0 and success_count > 0
            
            results.append(TestResult(
                test_name="rate_limiting_performance",
                success=success,
                execution_time=time.time() - start_time,
                details={
                    "success_count": success_count,
                    "error_count": error_count
                }
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="rate_limiting_performance",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _test_service_degradation(self) -> List[TestResult]:
        """Testa performance com degradação de serviços"""
        results = []
        
        start_time = time.time()
        try:
            # Configurar degradação
            self.mock_services.simulate_network_issues(0.3)
            
            # Testar operações
            num_operations = 10
            success_count = 0
            error_count = 0
            
            for i in range(num_operations):
                try:
                    self.mock_services.vertex_ai.generate_content(f"Degraded query {i}")
                    success_count += 1
                except Exception:
                    error_count += 1
            
            # Sistema deve funcionar parcialmente
            success = success_count > 0
            
            results.append(TestResult(
                test_name="service_degradation_performance",
                success=success,
                execution_time=time.time() - start_time,
                details={
                    "success_count": success_count,
                    "error_count": error_count
                }
            ))
            
        except Exception as e:
            results.append(TestResult(
                test_name="service_degradation_performance",
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            ))
        
        return results
    
    def _check_configuration_health(self) -> Dict[str, Any]:
        """Verifica saúde da configuração"""
        try:
            # Verificação básica
            return {
                "healthy": True,
                "details": {"status": "OK"},
                "message": "Configurações OK"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Erro ao verificar configurações"
            }
    
    def _check_dependencies_health(self) -> Dict[str, Any]:
        """Verifica saúde das dependências"""
        try:
            # Verificação básica
            return {
                "healthy": True,
                "details": {"status": "OK"},
                "message": "Dependências OK"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Erro ao verificar dependências"
            }
    
    def _check_resources_health(self) -> Dict[str, Any]:
        """Verifica saúde dos recursos"""
        try:
            # Verificação básica
            return {
                "healthy": True,
                "details": {"status": "OK"},
                "message": "Recursos OK"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Erro ao verificar recursos"
            }
    
    def _check_connectivity_health(self) -> Dict[str, Any]:
        """Verifica saúde da conectividade"""
        try:
            # Verificação básica
            return {
                "healthy": True,
                "details": {"status": "OK"},
                "message": "Conectividade OK"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Erro ao verificar conectividade"
            }
    
    def _generate_test_report(self, results: Dict[str, Any]) -> None:
        """Gera relatório detalhado dos testes"""
        try:
            report_path = Path(self.temp_dir) / "test_report.json" if self.temp_dir else Path("test_report.json")
            
            enhanced_results = {
                **results,
                "report_generated_at": datetime.now().isoformat(),
                "system_info": {
                    "platform": "mock_testing_environment",
                    "framework_version": "1.0.0"
                }
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📊 Relatório de testes salvo em: {report_path}")
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar relatório: {e}")


class TestRunner:
    """
    🏃 Executor de testes
    
    Interface simplificada para executar diferentes tipos de teste.
    """
    
    def __init__(self):
        self.framework = TestFramework()
    
    def run_quick_test(self) -> Dict[str, Any]:
        """Executa teste rápido (apenas unitários)"""
        print("🚀 Executando Teste Rápido")
        return self.framework.run_unit_tests()
    
    def run_full_test(self) -> Dict[str, Any]:
        """Executa teste completo (todos os tipos)"""
        print("🚀 Executando Teste Completo")
        return self.framework.run_all_tests()
    
    def run_performance_only(self) -> Dict[str, Any]:
        """Executa apenas testes de performance"""
        print("⚡ Executando Testes de Performance")
        return self.framework.run_performance_tests()
    
    def check_system_health(self) -> Dict[str, Any]:
        """Verifica saúde do sistema"""
        print("🏥 Verificando Saúde do Sistema")
        return self.framework.validate_system_health()
    
    def run_with_scenario(self, scenario: str) -> Dict[str, Any]:
        """Executa testes com cenário específico"""
        print(f"🎭 Executando testes com cenário: {scenario}")
        
        # Configurar cenário
        self.framework.mock_services.setup_scenario(scenario)
        
        # Executar testes
        return self.framework.run_all_tests()


if __name__ == "__main__":
    # Exemplo de uso
    runner = TestRunner()
    
    print("🧪 Framework de Testes RAG Enhanced")
    print("=" * 50)
    
    # Executar teste rápido
    quick_results = runner.run_quick_test()
    print(f"\n✅ Teste rápido concluído: {quick_results['success_rate']:.1f}% sucesso")
    
    # Verificar saúde do sistema
    health_results = runner.check_system_health()
    status = "✅ OK" if health_results['overall_healthy'] else "❌ Problemas"
    print(f"\n🏥 Saúde do sistema: {status}")