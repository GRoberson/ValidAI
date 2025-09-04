#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Test Validators - Validadores para testes

Este módulo fornece validadores abrangentes para verificar
a integridade e correção dos dados e resultados de teste.
"""

import re
import json
import yaml
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from ..core.models import ProcessingResult, QueryResponse


@dataclass
class ValidationResult:
    """
    📊 Resultado de validação
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    
    @classmethod
    def create_empty(cls) -> 'ValidationResult':
        """Cria resultado de validação vazio"""
        return cls(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def add_error(self, message: str) -> None:
        """Adiciona erro à validação"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Adiciona warning à validação"""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details
        }


class TestValidators:
    """
    ✅ Conjunto de validadores para testes
    
    Fornece validação para:
    - Configurações
    - Dados de entrada
    - Resultados de processamento
    - Estruturas de arquivos
    - Formatos de dados
    - Performance e métricas
    """
    
    def __init__(self):
        """Inicializa validadores"""
        # Padrões de validação
        self.patterns = {
            "project_id": re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"),
            "bucket_name": re.compile(r"^[a-z0-9][a-z0-9-_.]{1,61}[a-z0-9]$"),
            "corpus_name": re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$"),
            "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            "url": re.compile(r"^https?://[^\s/$.?#].[^\s]*$"),
            "version": re.compile(r"^\d+\.\d+\.\d+$")
        }
        
        # Limites de validação
        self.limits = {
            "max_file_size_mb": 100,
            "max_batch_size": 1000,
            "max_timeout_seconds": 300,
            "min_timeout_seconds": 1,
            "max_retry_attempts": 10,
            "min_retry_attempts": 0
        }
        
        # Extensões de arquivo suportadas
        self.supported_extensions = {
            ".py", ".js", ".java", ".cpp", ".c", ".h", ".hpp",
            ".md", ".txt", ".json", ".yaml", ".yml", ".xml",
            ".html", ".css", ".sql", ".sh", ".bat", ".ps1"
        }
        
        # Localizações válidas do GCP
        self.valid_locations = {
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1"
        }
    
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Valida configuração do sistema
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={"config_keys": list(config.keys())}
        )
        
        # Validar campos obrigatórios
        required_fields = ["project_id", "location"]
        for field in required_fields:
            if field not in config:
                result.add_error(f"Campo obrigatório ausente: {field}")
            elif not config[field]:
                result.add_error(f"Campo obrigatório vazio: {field}")
        
        # Validar project_id
        if "project_id" in config and config["project_id"]:
            if not self.patterns["project_id"].match(config["project_id"]):
                result.add_error("project_id deve seguir o padrão: letras minúsculas, números e hífens, 6-30 caracteres")
        
        # Validar location
        if "location" in config and config["location"]:
            if config["location"] not in self.valid_locations:
                result.add_error(f"location inválida: {config['location']}. Deve ser uma das: {', '.join(sorted(self.valid_locations))}")
        
        # Validar bucket_name (se presente)
        if "bucket_name" in config and config["bucket_name"]:
            if not self.patterns["bucket_name"].match(config["bucket_name"]):
                result.add_error("bucket_name deve seguir as regras do GCS: letras minúsculas, números, hífens e pontos, 3-63 caracteres")
        
        # Validar corpus_name (se presente)
        if "corpus_name" in config and config["corpus_name"]:
            if not self.patterns["corpus_name"].match(config["corpus_name"]):
                result.add_error("corpus_name deve começar com letra e conter apenas letras, números, hífens e underscores, máximo 64 caracteres")
        
        # Validar configurações numéricas
        numeric_configs = {
            "max_file_size_mb": (1, self.limits["max_file_size_mb"]),
            "batch_size": (1, self.limits["max_batch_size"]),
            "timeout_seconds": (self.limits["min_timeout_seconds"], self.limits["max_timeout_seconds"]),
            "retry_attempts": (self.limits["min_retry_attempts"], self.limits["max_retry_attempts"])
        }
        
        for key, (min_val, max_val) in numeric_configs.items():
            if key in config:
                value = config[key]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    result.add_error(f"{key} deve ser um número entre {min_val} e {max_val}")
        
        # Validar extensões suportadas (se presente)
        if "supported_extensions" in config:
            extensions = config["supported_extensions"]
            if not isinstance(extensions, list):
                result.add_error("supported_extensions deve ser uma lista")
            else:
                for ext in extensions:
                    if not isinstance(ext, str) or not ext.startswith("."):
                        result.add_error(f"Extensão inválida: {ext}. Deve começar com ponto")
        
        # Warnings para configurações opcionais
        optional_configs = ["bucket_name", "corpus_name", "max_file_size_mb"]
        for key in optional_configs:
            if key not in config:
                result.add_warning(f"Configuração opcional não definida: {key}")
        
        return result
    
    def validate_file_data(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        Valida dados de arquivo
        
        Args:
            file_data: Dados do arquivo a serem validados
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={"file_info": file_data.get("name", "unknown")}
        )
        
        # Validar campos obrigatórios
        required_fields = ["name", "content", "size"]
        for field in required_fields:
            if field not in file_data:
                result.add_error(f"Campo obrigatório ausente: {field}")
        
        # Validar nome do arquivo
        if "name" in file_data:
            name = file_data["name"]
            if not isinstance(name, str) or not name.strip():
                result.add_error("Nome do arquivo deve ser uma string não vazia")
            else:
                # Verificar extensão
                path = Path(name)
                if path.suffix not in self.supported_extensions:
                    result.add_warning(f"Extensão não suportada: {path.suffix}")
                
                # Verificar caracteres especiais
                if any(char in name for char in ['<', '>', ':', '"', '|', '?', '*']):
                    result.add_error("Nome do arquivo contém caracteres inválidos")
        
        # Validar conteúdo
        if "content" in file_data:
            content = file_data["content"]
            if not isinstance(content, (str, bytes)):
                result.add_error("Conteúdo deve ser string ou bytes")
            elif isinstance(content, str) and len(content.strip()) == 0:
                result.add_warning("Arquivo parece estar vazio")
        
        # Validar tamanho
        if "size" in file_data:
            size = file_data["size"]
            if not isinstance(size, (int, float)) or size < 0:
                result.add_error("Tamanho deve ser um número não negativo")
            elif size > self.limits["max_file_size_mb"] * 1024 * 1024:
                result.add_error(f"Arquivo muito grande: {size / (1024*1024):.1f}MB (máximo: {self.limits['max_file_size_mb']}MB)")
            elif size == 0:
                result.add_warning("Arquivo tem tamanho zero")
        
        # Validar tipo MIME (se presente)
        if "mime_type" in file_data:
            mime_type = file_data["mime_type"]
            if not isinstance(mime_type, str):
                result.add_error("mime_type deve ser uma string")
            elif not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9!#$&\-\^_]*\/[a-zA-Z0-9][a-zA-Z0-9!#$&\-\^_]*$", mime_type):
                result.add_error(f"mime_type inválido: {mime_type}")
        
        return result
    
    def validate_data_structure(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Valida estrutura de dados genérica
        
        Args:
            data: Dados para validar
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult.create_empty()
        
        if not isinstance(data, dict):
            result.add_error("Dados devem ser um dicionário")
            return result
        
        # Validar estrutura básica
        if "files" in data:
            files = data["files"]
            if not isinstance(files, list):
                result.add_error("'files' deve ser uma lista")
            else:
                for i, file_data in enumerate(files):
                    if not isinstance(file_data, dict):
                        result.add_error(f"Arquivo {i} deve ser um dicionário")
                    else:
                        # Validar campos obrigatórios do arquivo
                        required_file_fields = ["name", "size", "type"]
                        for field in required_file_fields:
                            if field not in file_data:
                                result.add_error(f"Arquivo {i}: campo obrigatório '{field}' ausente")
        
        # Validar metadados
        if "metadata" in data:
            metadata = data["metadata"]
            if not isinstance(metadata, dict):
                result.add_error("'metadata' deve ser um dicionário")
            else:
                # Validar campos de metadata
                if "created_at" in metadata:
                    created_at = metadata["created_at"]
                    if not isinstance(created_at, str):
                        result.add_error("'created_at' deve ser uma string")
                    else:
                        # Tentar validar formato ISO
                        try:
                            from datetime import datetime
                            datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except ValueError:
                            result.add_error("'created_at' deve estar no formato ISO 8601")
                
                if "version" in metadata:
                    version = metadata["version"]
                    if not isinstance(version, str):
                        result.add_error("'version' deve ser uma string")
                    elif not re.match(r"^\d+\.\d+\.\d+$", version):
                        result.add_warning("'version' não segue o padrão semver (x.y.z)")
        
        return result
    
    def validate_performance_metrics(self, metrics: Dict[str, Any]) -> ValidationResult:
        """
        Valida métricas de performance
        
        Args:
            metrics: Métricas para validar
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult.create_empty()
        
        if not isinstance(metrics, dict):
            result.add_error("Métricas devem ser um dicionário")
            return result
        
        # Definir limites aceitáveis
        limits = {
            "response_time": 1000,  # ms
            "memory_usage": 512,    # MB
            "cpu_usage": 80,        # %
            "throughput": 100       # req/s mínimo
        }
        
        # Validar cada métrica
        for metric_name, limit in limits.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                
                if not isinstance(value, (int, float)):
                    result.add_error(f"'{metric_name}' deve ser um número")
                    continue
                
                if metric_name == "response_time" and value > limit:
                    result.add_warning(f"Tempo de resposta alto: {value}ms (limite: {limit}ms)")
                elif metric_name == "memory_usage" and value > limit:
                    result.add_warning(f"Uso de memória alto: {value}MB (limite: {limit}MB)")
                elif metric_name == "cpu_usage" and value > limit:
                    result.add_warning(f"Uso de CPU alto: {value}% (limite: {limit}%)")
                elif metric_name == "throughput" and value < limit:
                    result.add_warning(f"Throughput baixo: {value} req/s (mínimo: {limit} req/s)")
        
        return result
    
    def validate_processing_result(self, processing_result: Union[Dict[str, Any], ProcessingResult]) -> ValidationResult:
        """
        Valida resultado de processamento
        
        Args:
            processing_result: Resultado do processamento
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        # Converter para dict se necessário
        if hasattr(processing_result, 'to_dict'):
            data = processing_result.to_dict()
        elif isinstance(processing_result, dict):
            data = processing_result
        else:
            result.add_error("Resultado de processamento deve ser dict ou ProcessingResult")
            return result
        
        # Validar campos obrigatórios
        required_fields = ["status", "timestamp"]
        for field in required_fields:
            if field not in data:
                result.add_error(f"Campo obrigatório ausente: {field}")
        
        # Validar status
        if "status" in data:
            valid_statuses = ["success", "error", "pending", "processing"]
            if data["status"] not in valid_statuses:
                result.add_error(f"Status inválido: {data['status']}. Deve ser um de: {', '.join(valid_statuses)}")
        
        # Validar timestamp
        if "timestamp" in data:
            timestamp = data["timestamp"]
            if isinstance(timestamp, str):
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    result.add_error("Timestamp deve estar no formato ISO 8601")
            elif not isinstance(timestamp, datetime):
                result.add_error("Timestamp deve ser string ISO 8601 ou objeto datetime")
        
        # Validar dados específicos por status
        if data.get("status") == "success":
            if "data" not in data:
                result.add_warning("Resultado de sucesso sem dados")
        elif data.get("status") == "error":
            if "error_message" not in data:
                result.add_warning("Resultado de erro sem mensagem de erro")
        
        # Validar métricas (se presentes)
        if "metrics" in data:
            metrics = data["metrics"]
            if not isinstance(metrics, dict):
                result.add_error("Métricas devem ser um dicionário")
            else:
                # Validar métricas específicas
                numeric_metrics = ["processing_time", "file_count", "success_rate"]
                for metric in numeric_metrics:
                    if metric in metrics:
                        value = metrics[metric]
                        if not isinstance(value, (int, float)) or value < 0:
                            result.add_error(f"Métrica {metric} deve ser um número não negativo")
        
        return result
    
    def validate_query_result(self, query_result: Union[Dict[str, Any], QueryResponse]) -> ValidationResult:
        """
        Valida resultado de query
        
        Args:
            query_result: Resultado da query
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        # Converter para dict se necessário
        if hasattr(query_result, 'to_dict'):
            data = query_result.to_dict()
        elif isinstance(query_result, dict):
            data = query_result
        else:
            result.add_error("Resultado de query deve ser dict ou QueryResponse")
            return result
        
        # Validar campos obrigatórios
        required_fields = ["query", "response", "timestamp"]
        for field in required_fields:
            if field not in data:
                result.add_error(f"Campo obrigatório ausente: {field}")
        
        # Validar query
        if "query" in data:
            query = data["query"]
            if not isinstance(query, str) or not query.strip():
                result.add_error("Query deve ser uma string não vazia")
            elif len(query) > 1000:
                result.add_warning("Query muito longa (>1000 caracteres)")
        
        # Validar response
        if "response" in data:
            response = data["response"]
            if not isinstance(response, str):
                result.add_error("Response deve ser uma string")
            elif not response.strip():
                result.add_warning("Response está vazia")
            elif len(response) < 10:
                result.add_warning("Response muito curta (<10 caracteres)")
        
        # Validar sources (se presentes)
        if "sources" in data:
            sources = data["sources"]
            if not isinstance(sources, list):
                result.add_error("Sources devem ser uma lista")
            else:
                for i, source in enumerate(sources):
                    if not isinstance(source, dict):
                        result.add_error(f"Source {i} deve ser um dicionário")
                    elif "name" not in source:
                        result.add_error(f"Source {i} deve ter campo 'name'")
        
        # Validar confidence (se presente)
        if "confidence" in data:
            confidence = data["confidence"]
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                result.add_error("Confidence deve ser um número entre 0 e 1")
        
        # Validar processing_time (se presente)
        if "processing_time" in data:
            processing_time = data["processing_time"]
            if not isinstance(processing_time, (int, float)) or processing_time < 0:
                result.add_error("Processing_time deve ser um número não negativo")
            elif processing_time > 30:
                result.add_warning("Processing_time muito alto (>30 segundos)")
        
        return result
    
    def validate_json_structure(self, json_data: Union[str, Dict[str, Any]], 
                              expected_schema: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Valida estrutura JSON
        
        Args:
            json_data: Dados JSON (string ou dict)
            expected_schema: Schema esperado (opcional)
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        # Parse JSON se for string
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                result.add_error(f"JSON inválido: {e}")
                return result
        else:
            data = json_data
        
        # Validar se é um dicionário válido
        if not isinstance(data, dict):
            result.add_error("JSON deve ser um objeto (dicionário)")
            return result
        
        # Validar contra schema se fornecido
        if expected_schema:
            self._validate_against_schema(data, expected_schema, result)
        
        # Validações gerais
        if len(data) == 0:
            result.add_warning("JSON está vazio")
        
        # Verificar profundidade excessiva
        max_depth = self._get_json_depth(data)
        if max_depth > 10:
            result.add_warning(f"JSON muito profundo ({max_depth} níveis)")
        
        return result
    
    def validate_yaml_structure(self, yaml_data: Union[str, Dict[str, Any]]) -> ValidationResult:
        """
        Valida estrutura YAML
        
        Args:
            yaml_data: Dados YAML (string ou dict)
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        # Parse YAML se for string
        if isinstance(yaml_data, str):
            try:
                data = yaml.safe_load(yaml_data)
            except yaml.YAMLError as e:
                result.add_error(f"YAML inválido: {e}")
                return result
        else:
            data = yaml_data
        
        # Validar estrutura básica
        if data is None:
            result.add_warning("YAML está vazio")
        elif not isinstance(data, dict):
            result.add_warning("YAML não é um objeto (dicionário)")
        
        return result
    
    def validate_performance_metrics(self, metrics: Dict[str, Any]) -> ValidationResult:
        """
        Valida métricas de performance
        
        Args:
            metrics: Métricas de performance
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={"metrics_count": len(metrics)}
        )
        
        # Métricas esperadas
        expected_metrics = {
            "response_time": {"type": (int, float), "min": 0, "max": 60},
            "throughput": {"type": (int, float), "min": 0, "max": 10000},
            "error_rate": {"type": (int, float), "min": 0, "max": 1},
            "cpu_usage": {"type": (int, float), "min": 0, "max": 100},
            "memory_usage": {"type": (int, float), "min": 0, "max": 100}
        }
        
        # Validar cada métrica
        for metric_name, constraints in expected_metrics.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                
                # Validar tipo
                if not isinstance(value, constraints["type"]):
                    result.add_error(f"Métrica {metric_name} deve ser numérica")
                    continue
                
                # Validar range
                if value < constraints["min"] or value > constraints["max"]:
                    result.add_error(f"Métrica {metric_name} fora do range válido: {constraints['min']}-{constraints['max']}")
                
                # Warnings para valores suspeitos
                if metric_name == "response_time" and value > 5:
                    result.add_warning(f"Response time alto: {value}s")
                elif metric_name == "error_rate" and value > 0.1:
                    result.add_warning(f"Error rate alto: {value*100:.1f}%")
                elif metric_name in ["cpu_usage", "memory_usage"] and value > 80:
                    result.add_warning(f"{metric_name} alto: {value}%")
        
        # Verificar métricas ausentes
        missing_metrics = set(expected_metrics.keys()) - set(metrics.keys())
        for metric in missing_metrics:
            result.add_warning(f"Métrica ausente: {metric}")
        
        return result
    
    def validate_batch_results(self, batch_results: List[Dict[str, Any]]) -> ValidationResult:
        """
        Valida resultados de processamento em lote
        
        Args:
            batch_results: Lista de resultados do lote
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={"batch_size": len(batch_results)}
        )
        
        if not isinstance(batch_results, list):
            result.add_error("Batch results deve ser uma lista")
            return result
        
        if len(batch_results) == 0:
            result.add_warning("Batch está vazio")
            return result
        
        # Validar cada resultado individualmente
        success_count = 0
        error_count = 0
        
        for i, item_result in enumerate(batch_results):
            item_validation = self.validate_processing_result(item_result)
            
            if not item_validation.is_valid:
                result.add_error(f"Item {i} inválido: {', '.join(item_validation.errors)}")
            
            # Contar sucessos e erros
            if item_result.get("status") == "success":
                success_count += 1
            elif item_result.get("status") == "error":
                error_count += 1
        
        # Calcular taxa de sucesso
        total_items = len(batch_results)
        success_rate = success_count / total_items if total_items > 0 else 0
        
        result.details.update({
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_rate
        })
        
        # Warnings baseados na taxa de sucesso
        if success_rate < 0.5:
            result.add_warning(f"Taxa de sucesso baixa: {success_rate*100:.1f}%")
        elif success_rate < 0.8:
            result.add_warning(f"Taxa de sucesso moderada: {success_rate*100:.1f}%")
        
        return result
    
    def validate_system_health(self, health_data: Dict[str, Any]) -> ValidationResult:
        """
        Valida dados de saúde do sistema
        
        Args:
            health_data: Dados de saúde do sistema
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        # Campos obrigatórios
        required_fields = ["overall_healthy", "checks", "timestamp"]
        for field in required_fields:
            if field not in health_data:
                result.add_error(f"Campo obrigatório ausente: {field}")
        
        # Validar overall_healthy
        if "overall_healthy" in health_data:
            if not isinstance(health_data["overall_healthy"], bool):
                result.add_error("overall_healthy deve ser boolean")
        
        # Validar checks
        if "checks" in health_data:
            checks = health_data["checks"]
            if not isinstance(checks, dict):
                result.add_error("checks deve ser um dicionário")
            else:
                for check_name, check_result in checks.items():
                    if not isinstance(check_result, dict):
                        result.add_error(f"Check {check_name} deve ser um dicionário")
                        continue
                    
                    if "healthy" not in check_result:
                        result.add_error(f"Check {check_name} deve ter campo 'healthy'")
                    elif not isinstance(check_result["healthy"], bool):
                        result.add_error(f"Check {check_name}.healthy deve ser boolean")
                    
                    # Se não está saudável, deve ter detalhes
                    if not check_result.get("healthy", True):
                        if "error" not in check_result and "details" not in check_result:
                            result.add_warning(f"Check {check_name} não saudável sem detalhes")
        
        # Validar timestamp
        if "timestamp" in health_data:
            timestamp = health_data["timestamp"]
            if isinstance(timestamp, str):
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    result.add_error("Timestamp deve estar no formato ISO 8601")
        
        return result
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any], 
                                result: ValidationResult) -> None:
        """Valida dados contra schema"""
        # Implementação básica de validação de schema
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    result.add_error(f"Campo obrigatório ausente: {field}")
        
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    value = data[field]
                    
                    # Validar tipo
                    if "type" in field_schema:
                        expected_type = field_schema["type"]
                        if expected_type == "string" and not isinstance(value, str):
                            result.add_error(f"Campo {field} deve ser string")
                        elif expected_type == "number" and not isinstance(value, (int, float)):
                            result.add_error(f"Campo {field} deve ser número")
                        elif expected_type == "boolean" and not isinstance(value, bool):
                            result.add_error(f"Campo {field} deve ser boolean")
                        elif expected_type == "array" and not isinstance(value, list):
                            result.add_error(f"Campo {field} deve ser array")
                        elif expected_type == "object" and not isinstance(value, dict):
                            result.add_error(f"Campo {field} deve ser objeto")
    
    def _get_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calcula profundidade máxima de estrutura JSON"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_json_depth(value, current_depth + 1) for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_json_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth


class SchemaValidator:
    """
    📋 Validador de schemas
    
    Valida estruturas de dados contra schemas definidos.
    """
    
    def __init__(self):
        """Inicializa validador de schemas"""
        self.schemas = {
            "config": {
                "type": "object",
                "required": ["project_id", "location"],
                "properties": {
                    "project_id": {"type": "string"},
                    "location": {"type": "string"},
                    "bucket_name": {"type": "string"},
                    "corpus_name": {"type": "string"},
                    "max_file_size_mb": {"type": "number"},
                    "timeout_seconds": {"type": "number"}
                }
            },
            "processing_result": {
                "type": "object",
                "required": ["status", "timestamp"],
                "properties": {
                    "status": {"type": "string", "enum": ["success", "error", "pending", "processing"]},
                    "timestamp": {"type": "string"},
                    "data": {"type": "object"},
                    "error_message": {"type": "string"},
                    "metrics": {"type": "object"}
                }
            },
            "query_result": {
                "type": "object",
                "required": ["query", "response", "timestamp"],
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "sources": {"type": "array"},
                    "confidence": {"type": "number"},
                    "processing_time": {"type": "number"}
                }
            }
        }
    
    def validate(self, data: Dict[str, Any], schema_name: str) -> ValidationResult:
        """
        Valida dados contra schema específico
        
        Args:
            data: Dados a serem validados
            schema_name: Nome do schema
            
        Returns:
            Resultado da validação
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={"schema": schema_name}
        )
        
        if schema_name not in self.schemas:
            result.add_error(f"Schema desconhecido: {schema_name}")
            return result
        
        schema = self.schemas[schema_name]
        validators = TestValidators()
        validators._validate_against_schema(data, schema, result)
        
        return result
    
    def add_schema(self, name: str, schema: Dict[str, Any]) -> None:
        """Adiciona novo schema"""
        self.schemas[name] = schema
    
    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém schema por nome"""
        return self.schemas.get(name)
    
    def list_schemas(self) -> List[str]:
        """Lista schemas disponíveis"""
        return list(self.schemas.keys())


if __name__ == "__main__":
    # Exemplo de uso
    validators = TestValidators()
    
    # Testar validação de configuração
    config = {
        "project_id": "test-project-123",
        "location": "us-central1",
        "bucket_name": "test-bucket",
        "max_file_size_mb": 50
    }
    
    result = validators.validate_config(config)
    print(f"Configuração válida: {result.is_valid}")
    if result.errors:
        print(f"Erros: {result.errors}")
    if result.warnings:
        print(f"Warnings: {result.warnings}")