#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Config Loader - Carregador de configurações unificado

Este módulo fornece carregamento centralizado e seguro de configurações
com validação, fallbacks e cache.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    ⚙️ Carregador de configurações inteligente
    
    Fornece:
    - Carregamento de múltiplos formatos (JSON, ENV)
    - Validação de configurações
    - Valores padrão seguros
    - Cache de configurações
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa o carregador
        
        Args:
            config_file: Caminho para arquivo de configuração
        """
        self.config_file = config_file or "config/validai_config.json"
        self.config_cache: Dict[str, Any] = {}
        self._loaded = False
        
        # Configurações padrão seguras
        self.default_config = {
            # Core settings
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
            "location": "us-central1",
            "modelo_versao": "gemini-1.5-pro-002",
            "nome_exibicao": "ValidAI Enhanced",
            
            # LLM Parameters
            "temperatura": 0.2,
            "top_p": 0.8,
            "max_output_tokens": 8000,
            
            # Performance
            "time_sleep": 0.006,
            "time_sleep_compare": 0.006,
            "max_arquivos_processo": 10,
            
            # Storage
            "temp_dir": "./temp_files",
            "historico_dir": "./historico_conversas", 
            "base_conhecimento_dir": "./base_conhecimento",
            
            # File limits
            "tamanho_max_arquivo_mb": 50,
            "extensoes_permitidas": [
                ".pdf", ".sas", ".ipynb", ".py", ".txt", ".csv", ".xlsx",
                ".png", ".jpg", ".jpeg", ".mp4", ".md", ".json", ".yaml", ".yml"
            ],
            
            # Cache settings
            "cache_ttl_segundos": 1800,
            "cache_max_size": 1000,
            "cache_cleanup_interval": 600,
            
            # Security
            "enable_file_validation": True,
            "max_upload_size_mb": 100,
            "allowed_upload_dirs": ["./temp_files", "./uploads"],
            
            # Logging
            "log_level": "INFO",
            "enable_debug": False,
            
            # RAG settings
            "rag_bucket_name": os.getenv("RAG_BUCKET_NAME", ""),
            "embedding_model": "text-embedding-005",
            "chunk_size": 1024,
            "chunk_overlap": 256,
            
            # Rate limiting
            "max_requests_per_minute": 60,
            "enable_rate_limiting": True
        }
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Carrega configurações de arquivo e variáveis de ambiente
        
        Args:
            force_reload: Forçar recarregamento do cache
            
        Returns:
            Dicionário com configurações completas
        """
        if self._loaded and not force_reload:
            return self.config_cache
        
        # Começar com valores padrão
        config = self.default_config.copy()
        
        # Carregar arquivo de configuração se existir
        file_config = self._load_from_file()
        if file_config:
            config.update(file_config)
            logger.info(f"Configurações carregadas de: {self.config_file}")
        
        # Sobrescrever com variáveis de ambiente
        env_config = self._load_from_env()
        config.update(env_config)
        
        # Validar configurações
        config = self._validate_and_normalize(config)
        
        # Cache e marcar como carregado
        self.config_cache = config
        self._loaded = True
        
        logger.info("Configurações carregadas e validadas com sucesso")
        return config
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Carrega configurações de arquivo JSON"""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON do arquivo de configuração: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo de configuração: {e}")
            return {}
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Carrega configurações de variáveis de ambiente"""
        env_config = {}
        
        # Mapeamento de variáveis de ambiente
        env_mapping = {
            "GOOGLE_CLOUD_PROJECT": "project_id",
            "GOOGLE_CLOUD_LOCATION": "location", 
            "VALIDAI_MODEL_VERSION": "modelo_versao",
            "VALIDAI_TEMPERATURE": ("temperatura", float),
            "VALIDAI_MAX_TOKENS": ("max_output_tokens", int),
            "VALIDAI_MAX_FILE_SIZE": ("tamanho_max_arquivo_mb", int),
            "VALIDAI_MAX_FILES": ("max_arquivos_processo", int),
            "VALIDAI_CACHE_TTL": ("cache_ttl_segundos", int),
            "VALIDAI_CACHE_SIZE": ("cache_max_size", int),
            "VALIDAI_LOG_LEVEL": "log_level",
            "VALIDAI_DEBUG": ("enable_debug", bool),
            "RAG_BUCKET_NAME": "rag_bucket_name"
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Se config_key é tupla, segundo elemento é o tipo
                if isinstance(config_key, tuple):
                    key, value_type = config_key
                    try:
                        if value_type == bool:
                            value = value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            value = value_type(value)
                        env_config[key] = value
                    except ValueError as e:
                        logger.warning(f"Erro ao converter {env_var}={value} para {value_type}: {e}")
                else:
                    env_config[config_key] = value
        
        if env_config:
            logger.info(f"Configurações carregadas de variáveis de ambiente: {list(env_config.keys())}")
        
        return env_config
    
    def _validate_and_normalize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e normaliza configurações"""
        validated_config = config.copy()
        
        # Validar campos obrigatórios
        required_fields = ["project_id"]
        for field in required_fields:
            if not config.get(field):
                logger.warning(f"Campo obrigatório não configurado: {field}")
        
        # Normalizar caminhos
        path_fields = ["temp_dir", "historico_dir", "base_conhecimento_dir"]
        for field in path_fields:
            if field in validated_config:
                path = Path(validated_config[field])
                path.mkdir(parents=True, exist_ok=True)
                validated_config[field] = str(path.resolve())
        
        # Validar limites numéricos
        numeric_limits = {
            "temperatura": (0.0, 2.0),
            "top_p": (0.0, 1.0),
            "max_output_tokens": (1, 32000),
            "tamanho_max_arquivo_mb": (1, 1000),
            "max_arquivos_processo": (1, 100),
            "cache_ttl_segundos": (60, 86400),  # 1min a 24h
            "cache_max_size": (10, 10000)
        }
        
        for field, (min_val, max_val) in numeric_limits.items():
            if field in validated_config:
                value = validated_config[field]
                if not min_val <= value <= max_val:
                    logger.warning(f"{field}={value} fora do limite [{min_val}, {max_val}], usando padrão")
                    validated_config[field] = self.default_config[field]
        
        # Validar extensões de arquivo
        if "extensoes_permitidas" in validated_config:
            extensions = validated_config["extensoes_permitidas"]
            if not isinstance(extensions, list):
                logger.warning("extensoes_permitidas deve ser uma lista, usando padrão")
                validated_config["extensoes_permitidas"] = self.default_config["extensoes_permitidas"]
        
        return validated_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        if not self._loaded:
            self.load_config()
        
        return self.config_cache.get(key, default)
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Atualiza configurações em memória
        
        Args:
            updates: Dicionário com atualizações
        """
        if not self._loaded:
            self.load_config()
        
        self.config_cache.update(updates)
        logger.info(f"Configurações atualizadas: {list(updates.keys())}")
    
    def save_config_to_file(self, file_path: Optional[str] = None) -> bool:
        """
        Salva configurações atuais em arquivo
        
        Args:
            file_path: Caminho do arquivo (opcional)
            
        Returns:
            True se salvou com sucesso
        """
        try:
            output_path = file_path or self.config_file
            
            # Criar diretório se não existir
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Filtrar apenas configurações não-padrão para salvar
            config_to_save = {}
            for key, value in self.config_cache.items():
                if key not in self.default_config or self.default_config[key] != value:
                    config_to_save[key] = value
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configurações salvas em: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo das configurações para debug
        
        Returns:
            Resumo das configurações (sem dados sensíveis)
        """
        if not self._loaded:
            self.load_config()
        
        summary = self.config_cache.copy()
        
        # Mascarar dados sensíveis
        sensitive_keys = ["project_id", "rag_bucket_name"]
        for key in sensitive_keys:
            if key in summary and summary[key]:
                summary[key] = "*" * len(summary[key])
        
        return summary


# Instância global do carregador
_config_loader = None

def get_config_loader(config_file: Optional[str] = None) -> ConfigLoader:
    """
    Obtém instância singleton do carregador de configurações
    
    Args:
        config_file: Arquivo de configuração (apenas na primeira chamada)
        
    Returns:
        Instância do carregador
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_file)
    return _config_loader

def load_config(config_file: Optional[str] = None, force_reload: bool = False) -> Dict[str, Any]:
    """
    Função utilitária para carregar configurações
    
    Args:
        config_file: Arquivo de configuração
        force_reload: Forçar recarregamento
        
    Returns:
        Dicionário com configurações
    """
    loader = get_config_loader(config_file)
    return loader.load_config(force_reload)

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Função utilitária para obter valor de configuração
    
    Args:
        key: Chave da configuração
        default: Valor padrão
        
    Returns:
        Valor da configuração
    """
    loader = get_config_loader()
    return loader.get(key, default)