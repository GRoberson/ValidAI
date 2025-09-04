#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Configuration Manager - Gerenciador principal de configurações

Este módulo fornece o gerenciador central de configurações com suporte
a perfis, validação automática e integração com wizard de configuração.
"""

import os
import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..core.interfaces import ConfigurationManagerInterface
from ..core.models import RAGConfig, ValidationResult
from ..core.exceptions import ConfigurationError
from .validator import ConfigValidator
from .profiles import ProfileManager

# Importar sistema de cache
try:
    from backend.cache import get_cache
except ImportError:
    # Fallback se o módulo de cache não estiver disponível
    get_cache = None


class EnhancedConfigurationManager(ConfigurationManagerInterface):
    """
    🔧 Gerenciador aprimorado de configurações
    
    Fornece gerenciamento completo de configurações com suporte a:
    - Múltiplos perfis de configuração
    - Validação automática e robusta
    - Carregamento de variáveis de ambiente
    - Wizard interativo de configuração
    """
    
    def __init__(self, config_dir: str = ".rag_config"):
        """
        Inicializa o gerenciador de configurações
        
        Args:
            config_dir: Diretório para armazenar configurações
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        self.validator = ConfigValidator()
        self.profiles = ProfileManager(self.config_dir)
        
        # Cache de configurações com sistema inteligente
        if get_cache:
            self._config_cache = get_cache(
                name="config_cache",
                max_size=50,  # Limite menor para configs
                default_ttl=1800,  # 30 minutos
                cleanup_interval=600  # 10 minutos
            )
            self._use_smart_cache = True
        else:
            # Fallback para cache simples
            self._config_cache = {}
            self._use_smart_cache = False
            self._cache_max_size = 50
        
        self._current_profile = None
        self._lock = threading.RLock()  # Usar RLock para permitir reentrada
    
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
        with self._lock:
            # Verificar cache primeiro
            if self._use_smart_cache:
                cached_config = self._config_cache.get(profile_name)
                if cached_config is not None:
                    return cached_config
            else:
                if profile_name in self._config_cache:
                    return self._config_cache[profile_name]
                
                # Gerenciar tamanho do cache para fallback
                if len(self._config_cache) >= self._cache_max_size:
                    oldest_key = next(iter(self._config_cache))
                    del self._config_cache[oldest_key]
        
        try:
            # Tentar carregar perfil existente
            if self.profiles.profile_exists(profile_name):
                config = self.profiles.load_profile(profile_name)
            else:
                # Se perfil não existe, criar configuração padrão
                if profile_name == "default":
                    config = self._create_default_config()
                    # Salvar como perfil padrão
                    self.profiles.create_profile(
                        "default", 
                        config, 
                        "Configuração padrão criada automaticamente"
                    )
                else:
                    raise ConfigurationError(
                        field="profile_name",
                        message=f"Perfil '{profile_name}' não encontrado",
                        suggestion=f"Perfis disponíveis: {', '.join(self.list_profiles())}"
                    )
            
            # Aplicar overrides de variáveis de ambiente
            config = self._apply_env_overrides(config)
            
            # Validar configuração
            validation = self.validator.validate_config(config, check_connectivity=False)
            if not validation.is_valid:
                raise ConfigurationError(
                    field="configuration",
                    message=f"Configuração do perfil '{profile_name}' é inválida",
                    suggestion="Execute o wizard de configuração para corrigir os problemas"
                )
            
            # Armazenar no cache
            if self._use_smart_cache:
                self._config_cache.set(profile_name, config)
            else:
                self._config_cache[profile_name] = config
            
            self._current_profile = profile_name
            
            return config
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                field="config_loading",
                message=f"Erro ao carregar configuração: {str(e)}",
                suggestion="Verifique se o perfil existe e tem formato válido"
            )
    
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
        try:
            # Validar configuração antes de salvar
            validation = self.validate_config(config)
            if not validation.is_valid:
                raise ConfigurationError(
                    field="configuration",
                    message="Não é possível salvar configuração inválida",
                    suggestion="Corrija os problemas de validação primeiro"
                )
            
            # Salvar ou atualizar perfil
            if self.profiles.profile_exists(profile_name):
                success = self.profiles.update_profile(profile_name, config)
            else:
                success = self.profiles.create_profile(
                    profile_name, 
                    config, 
                    f"Perfil criado em {config.location}"
                )
            
            if success:
                # Limpar cache para forçar reload (thread-safe)
                with self._lock:
                    if self._use_smart_cache:
                        self._config_cache.delete(profile_name)
                    else:
                        if profile_name in self._config_cache:
                            del self._config_cache[profile_name]
            
            return success
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                field="config_saving",
                message=f"Erro ao salvar configuração: {str(e)}",
                suggestion="Verifique permissões de escrita"
            )
    
    def validate_config(self, config: RAGConfig) -> ValidationResult:
        """
        Valida uma configuração
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            Resultado da validação com detalhes
        """
        return self.validator.validate_config(config, check_connectivity=True)
    
    def create_config_wizard(self) -> RAGConfig:
        """
        Executa wizard interativo de configuração
        
        Returns:
            Configuração criada pelo wizard
        """
        from .wizard import SetupWizard
        
        wizard = SetupWizard(self)
        return wizard.run_wizard()
    
    def list_profiles(self) -> List[str]:
        """
        Lista perfis de configuração disponíveis
        
        Returns:
            Lista de nomes de perfis
        """
        return self.profiles.list_profiles()
    
    def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um perfil
        
        Args:
            profile_name: Nome do perfil
            
        Returns:
            Dicionário com informações do perfil
        """
        return self.profiles.get_profile_info(profile_name)
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        Remove um perfil de configuração
        
        Args:
            profile_name: Nome do perfil a remover
            
        Returns:
            True se removeu com sucesso
        """
        success = self.profiles.delete_profile(profile_name)
        
        if success and profile_name in self._config_cache:
            del self._config_cache[profile_name]
        
        return success
    
    def export_profile(self, profile_name: str, export_path: Path) -> bool:
        """
        Exporta um perfil para arquivo
        
        Args:
            profile_name: Nome do perfil
            export_path: Caminho para exportar
            
        Returns:
            True se exportou com sucesso
        """
        return self.profiles.export_profile(profile_name, export_path)
    
    def import_profile(self, import_path: Path, new_name: Optional[str] = None) -> str:
        """
        Importa um perfil de arquivo
        
        Args:
            import_path: Caminho do arquivo a importar
            new_name: Novo nome para o perfil (opcional)
            
        Returns:
            Nome do perfil importado
        """
        return self.profiles.import_profile(import_path, new_name)
    
    def get_current_profile(self) -> Optional[str]:
        """
        Obtém o nome do perfil atualmente carregado
        
        Returns:
            Nome do perfil atual ou None
        """
        return self._current_profile
    
    def switch_profile(self, profile_name: str) -> RAGConfig:
        """
        Troca para outro perfil
        
        Args:
            profile_name: Nome do perfil para trocar
            
        Returns:
            Configuração do novo perfil
        """
        return self.get_config(profile_name)
    
    def get_profiles_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo de todos os perfis
        
        Returns:
            Resumo com informações de todos os perfis
        """
        return self.profiles.get_profiles_summary()
    
    def quick_setup(self, project_id: str, bucket_name: str, codebase_path: str) -> RAGConfig:
        """
        Configuração rápida com parâmetros mínimos
        
        Args:
            project_id: ID do projeto Google Cloud
            bucket_name: Nome do bucket
            codebase_path: Caminho da base de código
            
        Returns:
            Configuração criada
        """
        config = RAGConfig(
            project_id=project_id,
            bucket_name=bucket_name,
            codebase_path=Path(codebase_path)
        )
        
        # Validar configuração básica
        validation = self.validate_config(config)
        if not validation.is_valid:
            critical_issues = [
                issue for issue in validation.issues 
                if issue.severity.value == "critical"
            ]
            if critical_issues:
                raise ConfigurationError(
                    field="quick_setup",
                    message="Configuração rápida tem problemas críticos",
                    suggestion=validation.get_error_summary()
                )
        
        # Salvar como perfil padrão
        self.save_config(config, "default")
        
        return config
    
    def auto_detect_config(self) -> Optional[RAGConfig]:
        """
        Tenta detectar configuração automaticamente
        
        Returns:
            Configuração detectada ou None se não conseguir
        """
        try:
            # Tentar detectar projeto do gcloud
            project_id = self._detect_gcloud_project()
            
            # Procurar diretório de código comum
            codebase_path = self._detect_codebase_path()
            
            if project_id and codebase_path:
                # Gerar nome de bucket baseado no projeto
                bucket_name = f"{project_id}-rag-codebase"
                
                return RAGConfig(
                    project_id=project_id,
                    bucket_name=bucket_name,
                    codebase_path=codebase_path
                )
        
        except Exception:
            pass
        
        return None
    
    def _create_default_config(self) -> RAGConfig:
        """Cria configuração padrão"""
        # Tentar auto-detecção primeiro
        auto_config = self.auto_detect_config()
        if auto_config:
            return auto_config
        
        # Configuração padrão básica
        return RAGConfig(
            project_id="seu-projeto-aqui",
            bucket_name="seu-bucket-aqui",
            codebase_path=Path(".")
        )
    
    def _apply_env_overrides(self, config: RAGConfig) -> RAGConfig:
        """Aplica overrides de variáveis de ambiente"""
        env_mappings = {
            "RAG_PROJECT_ID": "project_id",
            "RAG_BUCKET_NAME": "bucket_name", 
            "RAG_LOCATION": "location",
            "RAG_CODEBASE_PATH": "codebase_path",
            "RAG_MAX_FILE_SIZE_MB": "max_file_size_mb",
            "RAG_TEMPERATURE": "temperature",
            "RAG_MAX_OUTPUT_TOKENS": "max_output_tokens",
            "RAG_EMBEDDING_MODEL": "embedding_model",
            "RAG_GENERATION_MODEL": "generation_model"
        }
        
        # Criar dicionário da configuração atual
        config_dict = {
            "project_id": config.project_id,
            "bucket_name": config.bucket_name,
            "location": config.location,
            "codebase_path": config.codebase_path,
            "max_file_size_mb": config.max_file_size_mb,
            "chunk_size": config.chunk_size,
            "chunk_overlap": config.chunk_overlap,
            "parallel_uploads": config.parallel_uploads,
            "embedding_model": config.embedding_model,
            "generation_model": config.generation_model,
            "retry_attempts": config.retry_attempts,
            "timeout_seconds": config.timeout_seconds,
            "enable_caching": config.enable_caching,
            "enable_compression": config.enable_compression,
            "gcs_folder": config.gcs_folder,
            "supported_extensions": config.supported_extensions,
            "temperature": config.temperature,
            "max_output_tokens": config.max_output_tokens
        }
        
        # Aplicar overrides
        for env_var, config_field in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                try:
                    # Converter tipos apropriados
                    if config_field in ["max_file_size_mb", "max_output_tokens", "chunk_size", "chunk_overlap", "parallel_uploads", "retry_attempts", "timeout_seconds"]:
                        config_dict[config_field] = int(env_value)
                    elif config_field == "temperature":
                        config_dict[config_field] = float(env_value)
                    elif config_field == "codebase_path":
                        config_dict[config_field] = Path(env_value)
                    else:
                        config_dict[config_field] = env_value
                except (ValueError, TypeError):
                    pass  # Ignorar valores inválidos
        
        return RAGConfig(**config_dict)
    
    def _detect_gcloud_project(self) -> Optional[str]:
        """Tenta detectar projeto do gcloud"""
        try:
            import subprocess
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                project_id = result.stdout.strip()
                if project_id and project_id != "(unset)":
                    return project_id
        except Exception:
            pass
        
        return None
    
    def _detect_codebase_path(self) -> Optional[Path]:
        """Tenta detectar caminho da base de código"""
        # Procurar por diretórios comuns de código
        common_dirs = ["src", "lib", "app", "code", "."]
        
        for dir_name in common_dirs:
            path = Path(dir_name)
            if path.exists() and path.is_dir():
                # Verificar se tem arquivos de código
                code_files = list(path.glob("**/*.py"))[:5]  # Limitar busca
                if code_files:
                    return path
        
        return Path(".")  # Fallback para diretório atual