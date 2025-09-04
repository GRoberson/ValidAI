#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👤 Profile Manager - Gerenciamento de perfis de configuração

Este módulo permite criar, salvar e gerenciar múltiplos perfis de configuração,
facilitando o uso do sistema em diferentes ambientes e projetos.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.models import RAGConfig
from ..core.exceptions import ConfigurationError


class ProfileManager:
    """
    👤 Gerenciador de perfis de configuração
    
    Permite criar e gerenciar múltiplos perfis de configuração,
    cada um otimizado para diferentes projetos ou ambientes.
    """
    
    def __init__(self, config_dir: Path):
        """
        Inicializa o gerenciador de perfis
        
        Args:
            config_dir: Diretório onde os perfis serão armazenados
        """
        self.config_dir = Path(config_dir)
        self.profiles_dir = self.config_dir / "profiles"
        self.metadata_file = self.config_dir / "profiles_metadata.json"
        
        # Criar diretórios se não existirem
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar ou criar metadata
        self.metadata = self._load_metadata()
    
    def create_profile(self, name: str, config: RAGConfig, description: str = "") -> bool:
        """
        Cria um novo perfil de configuração
        
        Args:
            name: Nome do perfil
            config: Configuração a ser salva
            description: Descrição opcional do perfil
            
        Returns:
            True se criou com sucesso
            
        Raises:
            ConfigurationError: Se o perfil já existir ou houver erro ao salvar
        """
        if self.profile_exists(name):
            raise ConfigurationError(
                field="profile_name",
                message=f"Perfil '{name}' já existe",
                suggestion="Use um nome diferente ou atualize o perfil existente"
            )
        
        try:
            # Salvar configuração
            profile_file = self.profiles_dir / f"{name}.json"
            config_dict = self._config_to_dict(config)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            # Atualizar metadata
            self.metadata[name] = {
                "description": description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "file_path": str(profile_file),
                "version": "2.0.0"
            }
            
            self._save_metadata()
            
            return True
            
        except Exception as e:
            raise ConfigurationError(
                field="profile_creation",
                message=f"Erro ao criar perfil '{name}': {str(e)}",
                suggestion="Verifique permissões de escrita no diretório de configuração"
            )
    
    def load_profile(self, name: str) -> RAGConfig:
        """
        Carrega um perfil de configuração
        
        Args:
            name: Nome do perfil a carregar
            
        Returns:
            Configuração carregada
            
        Raises:
            ConfigurationError: Se o perfil não existir ou houver erro ao carregar
        """
        if not self.profile_exists(name):
            raise ConfigurationError(
                field="profile_name",
                message=f"Perfil '{name}' não encontrado",
                suggestion=f"Perfis disponíveis: {', '.join(self.list_profiles())}"
            )
        
        try:
            profile_file = self.profiles_dir / f"{name}.json"
            
            with open(profile_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Atualizar último acesso
            if name in self.metadata:
                self.metadata[name]["last_accessed"] = datetime.now().isoformat()
                self._save_metadata()
            
            return self._dict_to_config(config_dict)
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                field="profile_format",
                message=f"Perfil '{name}' tem formato JSON inválido: {str(e)}",
                suggestion="Verifique o arquivo de configuração ou recrie o perfil"
            )
        except Exception as e:
            raise ConfigurationError(
                field="profile_loading",
                message=f"Erro ao carregar perfil '{name}': {str(e)}",
                suggestion="Verifique se o arquivo existe e tem permissões de leitura"
            )
    
    def update_profile(self, name: str, config: RAGConfig, description: Optional[str] = None) -> bool:
        """
        Atualiza um perfil existente
        
        Args:
            name: Nome do perfil
            config: Nova configuração
            description: Nova descrição (opcional)
            
        Returns:
            True se atualizou com sucesso
            
        Raises:
            ConfigurationError: Se o perfil não existir ou houver erro ao salvar
        """
        if not self.profile_exists(name):
            raise ConfigurationError(
                field="profile_name",
                message=f"Perfil '{name}' não encontrado para atualização",
                suggestion="Crie o perfil primeiro ou verifique o nome"
            )
        
        try:
            # Salvar configuração atualizada
            profile_file = self.profiles_dir / f"{name}.json"
            config_dict = self._config_to_dict(config)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            # Atualizar metadata
            if name in self.metadata:
                self.metadata[name]["updated_at"] = datetime.now().isoformat()
                if description is not None:
                    self.metadata[name]["description"] = description
            
            self._save_metadata()
            
            return True
            
        except Exception as e:
            raise ConfigurationError(
                field="profile_update",
                message=f"Erro ao atualizar perfil '{name}': {str(e)}",
                suggestion="Verifique permissões de escrita"
            )
    
    def delete_profile(self, name: str) -> bool:
        """
        Remove um perfil
        
        Args:
            name: Nome do perfil a remover
            
        Returns:
            True se removeu com sucesso
            
        Raises:
            ConfigurationError: Se o perfil não existir ou for o perfil padrão
        """
        if name == "default":
            raise ConfigurationError(
                field="profile_name",
                message="Não é possível remover o perfil padrão",
                suggestion="Crie outro perfil e defina como padrão antes de remover"
            )
        
        if not self.profile_exists(name):
            raise ConfigurationError(
                field="profile_name",
                message=f"Perfil '{name}' não encontrado",
                suggestion="Verifique o nome do perfil"
            )
        
        try:
            # Remover arquivo
            profile_file = self.profiles_dir / f"{name}.json"
            profile_file.unlink()
            
            # Remover metadata
            if name in self.metadata:
                del self.metadata[name]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            raise ConfigurationError(
                field="profile_deletion",
                message=f"Erro ao remover perfil '{name}': {str(e)}",
                suggestion="Verifique permissões de escrita"
            )
    
    def list_profiles(self) -> List[str]:
        """
        Lista todos os perfis disponíveis
        
        Returns:
            Lista de nomes de perfis
        """
        profiles = []
        
        # Buscar arquivos .json no diretório de perfis
        if self.profiles_dir.exists():
            for file_path in self.profiles_dir.glob("*.json"):
                profile_name = file_path.stem
                profiles.append(profile_name)
        
        return sorted(profiles)
    
    def get_profile_info(self, name: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um perfil
        
        Args:
            name: Nome do perfil
            
        Returns:
            Dicionário com informações do perfil
            
        Raises:
            ConfigurationError: Se o perfil não existir
        """
        if not self.profile_exists(name):
            raise ConfigurationError(
                field="profile_name",
                message=f"Perfil '{name}' não encontrado",
                suggestion="Verifique o nome do perfil"
            )
        
        info = {
            "name": name,
            "exists": True,
            "file_path": str(self.profiles_dir / f"{name}.json")
        }
        
        # Adicionar metadata se disponível
        if name in self.metadata:
            info.update(self.metadata[name])
        
        # Adicionar informações do arquivo
        profile_file = Path(info["file_path"])
        if profile_file.exists():
            stat = profile_file.stat()
            info["file_size"] = stat.st_size
            info["file_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return info
    
    def profile_exists(self, name: str) -> bool:
        """
        Verifica se um perfil existe
        
        Args:
            name: Nome do perfil
            
        Returns:
            True se o perfil existe
        """
        profile_file = self.profiles_dir / f"{name}.json"
        return profile_file.exists()
    
    def get_profiles_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo de todos os perfis
        
        Returns:
            Dicionário com resumo dos perfis
        """
        profiles = self.list_profiles()
        
        summary = {
            "total_profiles": len(profiles),
            "profiles": {},
            "config_dir": str(self.config_dir),
            "profiles_dir": str(self.profiles_dir)
        }
        
        for profile_name in profiles:
            try:
                info = self.get_profile_info(profile_name)
                summary["profiles"][profile_name] = {
                    "description": info.get("description", ""),
                    "created_at": info.get("created_at", ""),
                    "updated_at": info.get("updated_at", ""),
                    "last_accessed": info.get("last_accessed", "")
                }
            except Exception:
                summary["profiles"][profile_name] = {"error": "Não foi possível carregar informações"}
        
        return summary
    
    def export_profile(self, name: str, export_path: Path) -> bool:
        """
        Exporta um perfil para um arquivo
        
        Args:
            name: Nome do perfil
            export_path: Caminho para exportar
            
        Returns:
            True se exportou com sucesso
        """
        if not self.profile_exists(name):
            raise ConfigurationError(
                field="profile_name",
                message=f"Perfil '{name}' não encontrado",
                suggestion="Verifique o nome do perfil"
            )
        
        try:
            config = self.load_profile(name)
            info = self.get_profile_info(name)
            
            export_data = {
                "profile_name": name,
                "exported_at": datetime.now().isoformat(),
                "metadata": info,
                "configuration": self._config_to_dict(config)
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            raise ConfigurationError(
                field="profile_export",
                message=f"Erro ao exportar perfil '{name}': {str(e)}",
                suggestion="Verifique permissões de escrita no destino"
            )
    
    def import_profile(self, import_path: Path, new_name: Optional[str] = None) -> str:
        """
        Importa um perfil de um arquivo
        
        Args:
            import_path: Caminho do arquivo a importar
            new_name: Novo nome para o perfil (opcional)
            
        Returns:
            Nome do perfil importado
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Determinar nome do perfil
            profile_name = new_name or import_data.get("profile_name", "imported")
            
            # Verificar se já existe
            if self.profile_exists(profile_name):
                counter = 1
                while self.profile_exists(f"{profile_name}_{counter}"):
                    counter += 1
                profile_name = f"{profile_name}_{counter}"
            
            # Criar configuração
            config_dict = import_data.get("configuration", {})
            config = self._dict_to_config(config_dict)
            
            # Criar perfil
            description = f"Importado de {import_path.name}"
            if "metadata" in import_data and "description" in import_data["metadata"]:
                description = import_data["metadata"]["description"]
            
            self.create_profile(profile_name, config, description)
            
            return profile_name
            
        except Exception as e:
            raise ConfigurationError(
                field="profile_import",
                message=f"Erro ao importar perfil: {str(e)}",
                suggestion="Verifique se o arquivo tem formato válido"
            )
    
    def _config_to_dict(self, config: RAGConfig) -> Dict[str, Any]:
        """Converte RAGConfig para dicionário"""
        return {
            "project_id": config.project_id,
            "bucket_name": config.bucket_name,
            "location": config.location,
            "codebase_path": str(config.codebase_path),
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
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> RAGConfig:
        """Converte dicionário para RAGConfig"""
        # Converter codebase_path para Path
        if "codebase_path" in config_dict:
            config_dict["codebase_path"] = Path(config_dict["codebase_path"])
        
        return RAGConfig(**config_dict)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Carrega metadata dos perfis"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {}
    
    def _save_metadata(self) -> None:
        """Salva metadata dos perfis"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Falha silenciosa para não quebrar operações principais