#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ Config Validator - Validação robusta de configurações

Este módulo fornece validação abrangente de configurações com
verificações específicas para cada campo e sugestões úteis.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from google.cloud import storage
import vertexai

from ..core.models import RAGConfig, ValidationResult, ValidationIssue, ErrorSeverity
from ..core.exceptions import ValidationError


class ConfigValidator:
    """
    ✅ Validador de configurações com verificações abrangentes
    
    Realiza validação detalhada de todos os aspectos da configuração,
    incluindo conectividade com Google Cloud e validação de recursos.
    """
    
    def __init__(self):
        self.validation_cache = {}
    
    def validate_config(self, config: RAGConfig, check_connectivity: bool = True) -> ValidationResult:
        """
        Valida configuração completa
        
        Args:
            config: Configuração a ser validada
            check_connectivity: Se deve verificar conectividade com Google Cloud
            
        Returns:
            Resultado detalhado da validação
        """
        issues = []
        
        # Validações básicas (sempre executadas)
        issues.extend(self._validate_required_fields(config))
        issues.extend(self._validate_paths(config))
        issues.extend(self._validate_numeric_ranges(config))
        issues.extend(self._validate_model_names(config))
        issues.extend(self._validate_file_extensions(config))
        
        # Validações de conectividade (opcionais)
        if check_connectivity:
            issues.extend(self._validate_google_cloud_connectivity(config))
        
        # Determinar status geral
        status = self._determine_validation_status(issues)
        
        return ValidationResult(
            status=status,
            issues=issues,
            is_valid=status.value != "error"
        )
    
    def _validate_required_fields(self, config: RAGConfig) -> List[ValidationIssue]:
        """Valida campos obrigatórios"""
        issues = []
        
        # Project ID
        if not config.project_id or config.project_id.strip() == "":
            issues.append(ValidationIssue(
                field="project_id",
                severity=ErrorSeverity.CRITICAL,
                message="Project ID é obrigatório",
                suggestion="Configure o ID do seu projeto Google Cloud (ex: 'meu-projeto-123')"
            ))
        elif config.project_id in ["seu-projeto-aqui", "your-project-here", "project-id"]:
            issues.append(ValidationIssue(
                field="project_id",
                severity=ErrorSeverity.CRITICAL,
                message="Project ID ainda está com valor padrão",
                suggestion="Substitua pelo ID real do seu projeto Google Cloud"
            ))
        elif not self._is_valid_project_id(config.project_id):
            issues.append(ValidationIssue(
                field="project_id",
                severity=ErrorSeverity.HIGH,
                message="Project ID tem formato inválido",
                suggestion="Use apenas letras minúsculas, números e hífens (6-30 caracteres)"
            ))
        
        # Bucket name
        if not config.bucket_name or config.bucket_name.strip() == "":
            issues.append(ValidationIssue(
                field="bucket_name",
                severity=ErrorSeverity.CRITICAL,
                message="Nome do bucket é obrigatório",
                suggestion="Configure o nome do seu bucket no Google Cloud Storage"
            ))
        elif config.bucket_name in ["seu-bucket-aqui", "your-bucket-here", "bucket-name"]:
            issues.append(ValidationIssue(
                field="bucket_name",
                severity=ErrorSeverity.CRITICAL,
                message="Nome do bucket ainda está com valor padrão",
                suggestion="Substitua pelo nome real do seu bucket"
            ))
        elif not self._is_valid_bucket_name(config.bucket_name):
            issues.append(ValidationIssue(
                field="bucket_name",
                severity=ErrorSeverity.HIGH,
                message="Nome do bucket tem formato inválido",
                suggestion="Use apenas letras minúsculas, números, hífens e underscores (3-63 caracteres)"
            ))
        
        # Location
        if not config.location:
            issues.append(ValidationIssue(
                field="location",
                severity=ErrorSeverity.MEDIUM,
                message="Location não especificada",
                suggestion="Use 'us-central1' ou outra região próxima"
            ))
        elif config.location not in self._get_valid_locations():
            issues.append(ValidationIssue(
                field="location",
                severity=ErrorSeverity.MEDIUM,
                message=f"Location '{config.location}' pode não ser válida",
                suggestion="Verifique se a região suporta Vertex AI"
            ))
        
        return issues
    
    def _validate_paths(self, config: RAGConfig) -> List[ValidationIssue]:
        """Valida caminhos de arquivos e diretórios"""
        issues = []
        
        # Codebase path
        if not config.codebase_path:
            issues.append(ValidationIssue(
                field="codebase_path",
                severity=ErrorSeverity.HIGH,
                message="Caminho da base de código não especificado",
                suggestion="Configure o caminho para o diretório do seu código"
            ))
        elif not config.codebase_path.exists():
            issues.append(ValidationIssue(
                field="codebase_path",
                severity=ErrorSeverity.HIGH,
                message=f"Caminho não existe: {config.codebase_path}",
                suggestion="Verifique se o caminho está correto e o diretório existe"
            ))
        elif not config.codebase_path.is_dir():
            issues.append(ValidationIssue(
                field="codebase_path",
                severity=ErrorSeverity.HIGH,
                message=f"Caminho não é um diretório: {config.codebase_path}",
                suggestion="O caminho deve apontar para um diretório, não um arquivo"
            ))
        else:
            # Verificar se há arquivos suportados
            supported_files = self._count_supported_files(config.codebase_path, config.supported_extensions)
            if supported_files == 0:
                issues.append(ValidationIssue(
                    field="codebase_path",
                    severity=ErrorSeverity.MEDIUM,
                    message="Nenhum arquivo suportado encontrado no diretório",
                    suggestion="Verifique se o diretório contém arquivos de código ou ajuste as extensões suportadas"
                ))
            elif supported_files > 10000:
                issues.append(ValidationIssue(
                    field="codebase_path",
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Muitos arquivos encontrados ({supported_files})",
                    suggestion="Considere filtrar o diretório ou aumentar os limites de processamento"
                ))
        
        return issues
    
    def _validate_numeric_ranges(self, config: RAGConfig) -> List[ValidationIssue]:
        """Valida ranges de valores numéricos"""
        issues = []
        
        # Temperature
        if config.temperature < 0 or config.temperature > 2:
            issues.append(ValidationIssue(
                field="temperature",
                severity=ErrorSeverity.MEDIUM,
                message=f"Temperatura {config.temperature} fora do range válido (0-2)",
                suggestion="Use 0.1-0.3 para respostas mais determinísticas, 0.7-1.0 para mais criatividade"
            ))
        elif config.temperature > 1.5:
            issues.append(ValidationIssue(
                field="temperature",
                severity=ErrorSeverity.LOW,
                message=f"Temperatura {config.temperature} muito alta",
                suggestion="Valores altos podem gerar respostas inconsistentes"
            ))
        
        # Max output tokens
        if config.max_output_tokens <= 0:
            issues.append(ValidationIssue(
                field="max_output_tokens",
                severity=ErrorSeverity.HIGH,
                message="Max output tokens deve ser maior que 0",
                suggestion="Use valores entre 1000-8000 dependendo da complexidade das respostas"
            ))
        elif config.max_output_tokens > 32000:
            issues.append(ValidationIssue(
                field="max_output_tokens",
                severity=ErrorSeverity.MEDIUM,
                message=f"Max output tokens muito alto ({config.max_output_tokens})",
                suggestion="Valores muito altos podem aumentar custos e latência"
            ))
        
        # File size limits
        if config.max_file_size_mb <= 0:
            issues.append(ValidationIssue(
                field="max_file_size_mb",
                severity=ErrorSeverity.MEDIUM,
                message="Limite de tamanho de arquivo deve ser maior que 0",
                suggestion="Use valores entre 5-50 MB dependendo dos seus arquivos"
            ))
        elif config.max_file_size_mb > 100:
            issues.append(ValidationIssue(
                field="max_file_size_mb",
                severity=ErrorSeverity.LOW,
                message=f"Limite de arquivo muito alto ({config.max_file_size_mb} MB)",
                suggestion="Arquivos muito grandes podem causar problemas de processamento"
            ))
        
        # Chunk settings
        if config.chunk_size <= 0:
            issues.append(ValidationIssue(
                field="chunk_size",
                severity=ErrorSeverity.MEDIUM,
                message="Tamanho do chunk deve ser maior que 0",
                suggestion="Use valores entre 512-2048 caracteres"
            ))
        elif config.chunk_overlap >= config.chunk_size:
            issues.append(ValidationIssue(
                field="chunk_overlap",
                severity=ErrorSeverity.MEDIUM,
                message="Overlap não pode ser maior ou igual ao tamanho do chunk",
                suggestion="Use overlap de 10-25% do tamanho do chunk"
            ))
        
        # Parallel uploads
        if config.parallel_uploads <= 0:
            issues.append(ValidationIssue(
                field="parallel_uploads",
                severity=ErrorSeverity.MEDIUM,
                message="Número de uploads paralelos deve ser maior que 0",
                suggestion="Use valores entre 3-10 dependendo da sua conexão"
            ))
        elif config.parallel_uploads > 20:
            issues.append(ValidationIssue(
                field="parallel_uploads",
                severity=ErrorSeverity.LOW,
                message=f"Muitos uploads paralelos ({config.parallel_uploads})",
                suggestion="Valores muito altos podem sobrecarregar a rede"
            ))
        
        return issues
    
    def _validate_model_names(self, config: RAGConfig) -> List[ValidationIssue]:
        """Valida nomes dos modelos de IA"""
        issues = []
        
        # Embedding model
        if not config.embedding_model:
            issues.append(ValidationIssue(
                field="embedding_model",
                severity=ErrorSeverity.HIGH,
                message="Modelo de embedding não especificado",
                suggestion="Use 'publishers/google/models/text-embedding-005'"
            ))
        elif not self._is_valid_embedding_model(config.embedding_model):
            issues.append(ValidationIssue(
                field="embedding_model",
                severity=ErrorSeverity.MEDIUM,
                message=f"Modelo de embedding pode não ser válido: {config.embedding_model}",
                suggestion="Verifique se o modelo existe e está disponível na sua região"
            ))
        
        # Generation model
        if not config.generation_model:
            issues.append(ValidationIssue(
                field="generation_model",
                severity=ErrorSeverity.HIGH,
                message="Modelo de geração não especificado",
                suggestion="Use 'gemini-2.5-flash' ou 'gemini-1.5-pro-002'"
            ))
        elif not self._is_valid_generation_model(config.generation_model):
            issues.append(ValidationIssue(
                field="generation_model",
                severity=ErrorSeverity.MEDIUM,
                message=f"Modelo de geração pode não ser válido: {config.generation_model}",
                suggestion="Verifique se o modelo existe e está disponível"
            ))
        
        return issues
    
    def _validate_file_extensions(self, config: RAGConfig) -> List[ValidationIssue]:
        """Valida extensões de arquivo suportadas"""
        issues = []
        
        if not config.supported_extensions:
            issues.append(ValidationIssue(
                field="supported_extensions",
                severity=ErrorSeverity.HIGH,
                message="Nenhuma extensão de arquivo especificada",
                suggestion="Configure pelo menos algumas extensões como ['.py', '.js', '.md']"
            ))
        else:
            # Verificar formato das extensões
            invalid_extensions = []
            for ext in config.supported_extensions:
                if not isinstance(ext, str) or not ext.startswith('.'):
                    invalid_extensions.append(ext)
            
            if invalid_extensions:
                issues.append(ValidationIssue(
                    field="supported_extensions",
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Extensões inválidas: {invalid_extensions}",
                    suggestion="Extensões devem começar com ponto (ex: '.py', '.js')"
                ))
        
        return issues
    
    def _validate_google_cloud_connectivity(self, config: RAGConfig) -> List[ValidationIssue]:
        """Valida conectividade com Google Cloud"""
        issues = []
        
        try:
            # Verificar credenciais
            if not self._check_credentials():
                issues.append(ValidationIssue(
                    field="credentials",
                    severity=ErrorSeverity.CRITICAL,
                    message="Credenciais do Google Cloud não encontradas",
                    suggestion="Configure GOOGLE_APPLICATION_CREDENTIALS ou faça login com 'gcloud auth application-default login'"
                ))
                return issues  # Não continuar se não há credenciais
            
            # Verificar acesso ao projeto
            if not self._check_project_access(config.project_id):
                issues.append(ValidationIssue(
                    field="project_id",
                    severity=ErrorSeverity.HIGH,
                    message=f"Não foi possível acessar o projeto {config.project_id}",
                    suggestion="Verifique se o projeto existe e você tem permissões"
                ))
            
            # Verificar acesso ao bucket
            if not self._check_bucket_access(config.project_id, config.bucket_name):
                issues.append(ValidationIssue(
                    field="bucket_name",
                    severity=ErrorSeverity.HIGH,
                    message=f"Não foi possível acessar o bucket {config.bucket_name}",
                    suggestion="Verifique se o bucket existe e você tem permissões de escrita"
                ))
            
            # Verificar Vertex AI
            if not self._check_vertex_ai_access(config.project_id, config.location):
                issues.append(ValidationIssue(
                    field="location",
                    severity=ErrorSeverity.HIGH,
                    message=f"Não foi possível acessar Vertex AI em {config.location}",
                    suggestion="Verifique se a API está habilitada e a região é válida"
                ))
        
        except Exception as e:
            issues.append(ValidationIssue(
                field="connectivity",
                severity=ErrorSeverity.MEDIUM,
                message=f"Erro ao verificar conectividade: {str(e)}",
                suggestion="Verifique sua conexão com a internet e configurações"
            ))
        
        return issues
    
    def _is_valid_project_id(self, project_id: str) -> bool:
        """Verifica se o project ID tem formato válido"""
        # Project IDs devem ter 6-30 caracteres, começar com letra, apenas letras minúsculas, números e hífens
        pattern = r'^[a-z][a-z0-9-]{5,29}$'
        return bool(re.match(pattern, project_id))
    
    def _is_valid_bucket_name(self, bucket_name: str) -> bool:
        """Verifica se o nome do bucket tem formato válido"""
        # Bucket names devem ter 3-63 caracteres, apenas letras minúsculas, números, hífens e underscores
        pattern = r'^[a-z0-9][a-z0-9_-]{2,62}$'
        return bool(re.match(pattern, bucket_name))
    
    def _get_valid_locations(self) -> List[str]:
        """Retorna lista de locations válidas para Vertex AI"""
        return [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west4",
            "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6",
            "asia-east1", "asia-northeast1", "asia-southeast1", "australia-southeast1"
        ]
    
    def _is_valid_embedding_model(self, model: str) -> bool:
        """Verifica se o modelo de embedding é válido"""
        valid_models = [
            "publishers/google/models/text-embedding-005",
            "publishers/google/models/text-embedding-004",
            "publishers/google/models/textembedding-gecko"
        ]
        return model in valid_models
    
    def _is_valid_generation_model(self, model: str) -> bool:
        """Verifica se o modelo de geração é válido"""
        valid_models = [
            "gemini-2.5-flash", "gemini-1.5-pro-002", "gemini-1.5-flash-002",
            "gemini-1.0-pro", "gemini-pro", "gemini-pro-vision"
        ]
        return model in valid_models
    
    def _count_supported_files(self, path: Path, extensions: List[str]) -> int:
        """Conta arquivos suportados no diretório"""
        count = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    count += 1
                    if count > 10000:  # Parar contagem em números muito altos
                        break
        except (PermissionError, OSError):
            pass
        return count
    
    def _check_credentials(self) -> bool:
        """Verifica se há credenciais válidas"""
        try:
            # Verificar variável de ambiente
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                return True
            
            # Tentar criar cliente para testar credenciais padrão
            storage.Client()
            return True
        except Exception:
            return False
    
    def _check_project_access(self, project_id: str) -> bool:
        """Verifica acesso ao projeto"""
        try:
            client = storage.Client(project=project_id)
            # Tentar listar buckets para verificar acesso
            list(client.list_buckets(max_results=1))
            return True
        except Exception:
            return False
    
    def _check_bucket_access(self, project_id: str, bucket_name: str) -> bool:
        """Verifica acesso ao bucket"""
        try:
            client = storage.Client(project=project_id)
            bucket = client.bucket(bucket_name)
            # Tentar verificar se o bucket existe
            bucket.reload()
            return True
        except Exception:
            return False
    
    def _check_vertex_ai_access(self, project_id: str, location: str) -> bool:
        """Verifica acesso ao Vertex AI"""
        try:
            vertexai.init(project=project_id, location=location)
            return True
        except Exception:
            return False
    
    def _determine_validation_status(self, issues: List[ValidationIssue]) -> 'ValidationStatus':
        """Determina status geral baseado nos problemas encontrados"""
        from ..core.models import ValidationStatus
        
        if any(issue.severity == ErrorSeverity.CRITICAL for issue in issues):
            return ValidationStatus.ERROR
        elif any(issue.severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM] for issue in issues):
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.VALID