#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Diagnostics Runner - Sistema de diagnósticos do sistema

Este módulo fornece diagnósticos abrangentes incluindo verificação
de conectividade, recursos, configurações e saúde geral do sistema.
"""

import os
import sys
import psutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from google.cloud import storage
from google.api_core import exceptions as gcp_exceptions
import vertexai

from ..core.models import DiagnosticsReport
from ..core.exceptions import ProcessingError


class DiagnosticsRunner:
    """
    🔍 Executor de diagnósticos do sistema
    
    Fornece verificações abrangentes incluindo:
    - Conectividade com Google Cloud
    - Recursos do sistema (CPU, memória, disco)
    - Configurações e dependências
    - Saúde dos componentes
    - Testes de funcionalidade básica
    """
    
    def __init__(self):
        """Inicializa o executor de diagnósticos"""
        self.test_results = {}
        self.system_info = {}
    
    def run_full_diagnostics(self) -> DiagnosticsReport:
        """
        Executa diagnósticos completos do sistema
        
        Returns:
            Relatório completo de diagnósticos
        """
        print("🔍 Executando diagnósticos completos do sistema...")
        
        # Coletar informações do sistema
        self.system_info = self._collect_system_info()
        
        # Executar testes
        tests = [
            ("Recursos do Sistema", self._test_system_resources),
            ("Dependências Python", self._test_python_dependencies),
            ("Configurações", self._test_configurations),
            ("Conectividade Google Cloud", self._test_gcp_connectivity),
            ("Vertex AI", self._test_vertex_ai),
            ("Cloud Storage", self._test_cloud_storage),
            ("Estrutura de Arquivos", self._test_file_structure),
            ("Permissões", self._test_permissions)
        ]
        
        component_status = {}
        issues_found = []
        recommendations = []
        
        for test_name, test_func in tests:
            try:
                print(f"  🔍 Testando: {test_name}")
                result = test_func()
                
                component_status[test_name] = result["status"]
                
                if result["status"] != "ok":
                    issues_found.extend(result.get("issues", []))
                
                recommendations.extend(result.get("recommendations", []))
                
                self.test_results[test_name] = result
                
            except Exception as e:
                component_status[test_name] = "error"
                issues_found.append(f"Erro no teste {test_name}: {str(e)}")
                self.test_results[test_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Determinar status geral
        overall_status = self._determine_overall_status(component_status)
        
        return DiagnosticsReport(
            timestamp=datetime.now(),
            overall_status=overall_status,
            component_status=component_status,
            issues_found=issues_found,
            recommendations=recommendations,
            system_info=self.system_info
        )
    
    def test_connectivity(self) -> Dict[str, Any]:
        """
        Testa conectividade básica
        
        Returns:
            Resultado do teste de conectividade
        """
        return self._test_gcp_connectivity()
    
    def test_system_health(self) -> Dict[str, Any]:
        """
        Testa saúde geral do sistema
        
        Returns:
            Resultado do teste de saúde
        """
        return self._test_system_resources()
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Coleta informações básicas do sistema"""
        try:
            return {
                "platform": platform.platform(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_free_gb": round(psutil.disk_usage('.').free / (1024**3), 2),
                "current_directory": str(Path.cwd()),
                "environment_variables": {
                    "GOOGLE_APPLICATION_CREDENTIALS": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
                    "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
                    "PATH_exists": bool(os.getenv("PATH"))
                }
            }
        except Exception as e:
            return {"error": f"Erro ao coletar informações: {str(e)}"}
    
    def _test_system_resources(self) -> Dict[str, Any]:
        """Testa recursos do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disco
            disk = psutil.disk_usage('.')
            disk_free_gb = disk.free / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            
            issues = []
            recommendations = []
            
            # Verificar limites
            if cpu_percent > 90:
                issues.append(f"CPU usage muito alto: {cpu_percent}%")
                recommendations.append("Feche outras aplicações para liberar CPU")
            
            if memory_percent > 85:
                issues.append(f"Uso de memória alto: {memory_percent}%")
                recommendations.append("Feche outras aplicações para liberar memória")
            
            if memory_available_gb < 1:
                issues.append(f"Pouca memória disponível: {memory_available_gb:.1f}GB")
                recommendations.append("Considere aumentar a memória do sistema")
            
            if disk_free_gb < 5:
                issues.append(f"Pouco espaço em disco: {disk_free_gb:.1f}GB")
                recommendations.append("Libere espaço em disco antes de continuar")
            
            status = "warning" if issues else "ok"
            
            return {
                "status": status,
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_available_gb": round(memory_available_gb, 2),
                    "disk_free_gb": round(disk_free_gb, 2),
                    "disk_percent": round(disk_percent, 2)
                },
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "recommendations": ["Verifique se psutil está instalado corretamente"]
            }
    
    def _test_python_dependencies(self) -> Dict[str, Any]:
        """Testa dependências Python"""
        required_packages = [
            "google-cloud-storage",
            "google-genai", 
            "vertexai",
            "psutil",
            "chardet"
        ]
        
        missing_packages = []
        installed_packages = {}
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                
                # Tentar obter versão
                try:
                    import pkg_resources
                    version = pkg_resources.get_distribution(package).version
                    installed_packages[package] = version
                except:
                    installed_packages[package] = "unknown"
                    
            except ImportError:
                missing_packages.append(package)
        
        issues = []
        recommendations = []
        
        if missing_packages:
            issues.append(f"Pacotes faltando: {', '.join(missing_packages)}")
            recommendations.append(f"Instale: pip install {' '.join(missing_packages)}")
        
        status = "error" if missing_packages else "ok"
        
        return {
            "status": status,
            "details": {
                "installed_packages": installed_packages,
                "missing_packages": missing_packages
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _test_configurations(self) -> Dict[str, Any]:
        """Testa configurações do sistema"""
        issues = []
        recommendations = []
        
        # Verificar diretórios de configuração
        config_dirs = [".rag_config", ".rag_checkpoints", ".rag_history"]
        missing_dirs = []
        
        for dir_name in config_dirs:
            if not Path(dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            issues.append(f"Diretórios de configuração faltando: {', '.join(missing_dirs)}")
            recommendations.append("Execute o wizard de configuração para criar estrutura")
        
        # Verificar arquivo de configuração
        config_file = Path(".rag_config/default.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if config.get("project_id") == "seu-projeto-aqui":
                    issues.append("Configuração ainda tem valores padrão")
                    recommendations.append("Configure project_id e bucket_name reais")
                    
            except json.JSONDecodeError:
                issues.append("Arquivo de configuração tem formato inválido")
                recommendations.append("Recrie o arquivo de configuração")
        
        status = "warning" if issues else "ok"
        
        return {
            "status": status,
            "details": {
                "config_dirs_exist": len(missing_dirs) == 0,
                "config_file_exists": config_file.exists()
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _test_gcp_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade com Google Cloud"""
        issues = []
        recommendations = []
        
        # Verificar credenciais
        credentials_ok = False
        
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            credentials_ok = True
        else:
            # Tentar gcloud
            try:
                result = subprocess.run(
                    ["gcloud", "auth", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    auth_accounts = json.loads(result.stdout)
                    if auth_accounts:
                        credentials_ok = True
                        
            except Exception:
                pass
        
        if not credentials_ok:
            issues.append("Credenciais do Google Cloud não encontradas")
            recommendations.append("Execute: gcloud auth application-default login")
        
        # Testar conectividade básica
        connectivity_ok = False
        
        if credentials_ok:
            try:
                # Tentar criar cliente básico
                client = storage.Client()
                connectivity_ok = True
                
            except Exception as e:
                issues.append(f"Erro de conectividade: {str(e)}")
                recommendations.append("Verifique conexão com internet e credenciais")
        
        status = "error" if not credentials_ok else "warning" if issues else "ok"
        
        return {
            "status": status,
            "details": {
                "credentials_found": credentials_ok,
                "connectivity_ok": connectivity_ok
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _test_vertex_ai(self) -> Dict[str, Any]:
        """Testa acesso ao Vertex AI"""
        issues = []
        recommendations = []
        
        try:
            # Tentar inicializar Vertex AI
            vertexai.init(project="test-project", location="us-central1")
            
            vertex_ok = True
            
        except Exception as e:
            vertex_ok = False
            issues.append(f"Erro no Vertex AI: {str(e)}")
            recommendations.append("Verifique se a API do Vertex AI está habilitada")
        
        status = "warning" if issues else "ok"
        
        return {
            "status": status,
            "details": {
                "vertex_ai_accessible": vertex_ok
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _test_cloud_storage(self) -> Dict[str, Any]:
        """Testa acesso ao Cloud Storage"""
        issues = []
        recommendations = []
        
        try:
            # Tentar criar cliente
            client = storage.Client()
            
            # Tentar listar buckets (apenas para testar acesso)
            try:
                buckets = list(client.list_buckets(max_results=1))
                storage_ok = True
            except gcp_exceptions.Forbidden:
                storage_ok = False
                issues.append("Sem permissão para listar buckets")
                recommendations.append("Verifique permissões de Storage no Google Cloud")
            except Exception as e:
                storage_ok = False
                issues.append(f"Erro no Cloud Storage: {str(e)}")
        
        except Exception as e:
            storage_ok = False
            issues.append(f"Erro ao conectar Cloud Storage: {str(e)}")
            recommendations.append("Verifique credenciais e conectividade")
        
        status = "warning" if issues else "ok"
        
        return {
            "status": status,
            "details": {
                "cloud_storage_accessible": storage_ok
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _test_file_structure(self) -> Dict[str, Any]:
        """Testa estrutura de arquivos necessária"""
        issues = []
        recommendations = []
        
        # Verificar se estamos em um diretório com código
        code_files = list(Path(".").glob("*.py"))
        
        if not code_files:
            issues.append("Nenhum arquivo Python encontrado no diretório atual")
            recommendations.append("Navegue para um diretório com código Python")
        
        # Verificar permissões de escrita
        try:
            test_file = Path(".rag_test_write")
            test_file.write_text("test")
            test_file.unlink()
            write_ok = True
        except Exception:
            write_ok = False
            issues.append("Sem permissão de escrita no diretório atual")
            recommendations.append("Verifique permissões do diretório")
        
        status = "warning" if issues else "ok"
        
        return {
            "status": status,
            "details": {
                "code_files_found": len(code_files),
                "write_permission": write_ok
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _test_permissions(self) -> Dict[str, Any]:
        """Testa permissões necessárias"""
        issues = []
        recommendations = []
        
        # Testar criação de diretórios
        try:
            test_dir = Path(".rag_test_dir")
            test_dir.mkdir(exist_ok=True)
            test_dir.rmdir()
            dir_ok = True
        except Exception:
            dir_ok = False
            issues.append("Sem permissão para criar diretórios")
        
        # Testar escrita de arquivos
        try:
            test_file = Path(".rag_test_file")
            test_file.write_text("test")
            test_file.unlink()
            file_ok = True
        except Exception:
            file_ok = False
            issues.append("Sem permissão para criar arquivos")
        
        if not dir_ok or not file_ok:
            recommendations.append("Execute com permissões adequadas ou mude para diretório com acesso")
        
        status = "error" if issues else "ok"
        
        return {
            "status": status,
            "details": {
                "directory_creation": dir_ok,
                "file_creation": file_ok
            },
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _determine_overall_status(self, component_status: Dict[str, str]) -> str:
        """Determina status geral baseado nos componentes"""
        if any(status == "error" for status in component_status.values()):
            return "error"
        elif any(status == "warning" for status in component_status.values()):
            return "warning"
        else:
            return "healthy"