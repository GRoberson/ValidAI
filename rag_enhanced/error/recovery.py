#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Recovery Manager - Gerenciador de recuperação de falhas

Este módulo fornece estratégias avançadas de recuperação incluindo
restauração de estado, limpeza de recursos e auto-correção.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from ..core.models import ProcessingCheckpoint
from ..core.exceptions import ProcessingError, ConfigurationError


@dataclass
class RecoveryAction:
    """
    🔧 Ação de recuperação
    """
    name: str
    description: str
    action_type: str  # cleanup, restore, validate, refresh
    priority: int  # 1 = alta, 5 = baixa
    auto_execute: bool = True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a ação de recuperação"""
        raise NotImplementedError


class RecoveryManager:
    """
    🔧 Gerenciador de recuperação de falhas
    
    Fornece estratégias de recuperação incluindo:
    - Restauração de checkpoints
    - Limpeza de recursos
    - Validação e correção de configurações
    - Refresh de credenciais
    - Auto-correção de problemas comuns
    """
    
    def __init__(self):
        """Inicializa o gerenciador de recuperação"""
        self.recovery_actions = self._build_recovery_actions()
        self.recovery_history = []
    
    def refresh_authentication(self) -> Dict[str, Any]:
        """
        Tenta renovar credenciais de autenticação
        
        Returns:
            Resultado da operação de refresh
        """
        try:
            # Verificar variáveis de ambiente
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                return {
                    "success": True,
                    "message": "Credenciais encontradas via variável de ambiente",
                    "action": "environment_credentials"
                }
            
            # Tentar gcloud auth
            import subprocess
            result = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Credenciais renovadas via gcloud",
                    "action": "gcloud_refresh"
                }
            else:
                return {
                    "success": False,
                    "message": "Falha ao renovar credenciais",
                    "suggestion": "Execute: gcloud auth application-default login"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao renovar credenciais: {str(e)}",
                "suggestion": "Verifique se gcloud está instalado e configurado"
            }
    
    def validate_and_fix_config(self) -> Dict[str, Any]:
        """
        Valida e tenta corrigir configuração
        
        Returns:
            Resultado da validação e correção
        """
        try:
            fixes_applied = []
            
            # Verificar diretórios necessários
            required_dirs = [".rag_config", ".rag_checkpoints", ".rag_history"]
            
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    fixes_applied.append(f"Criado diretório: {dir_name}")
            
            # Verificar arquivo de configuração
            config_file = Path(".rag_config/default.json")
            if not config_file.exists():
                # Criar configuração básica
                default_config = {
                    "project_id": "seu-projeto-aqui",
                    "bucket_name": "seu-bucket-aqui",
                    "location": "us-central1",
                    "created_at": datetime.now().isoformat()
                }
                
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                fixes_applied.append("Criado arquivo de configuração padrão")
            
            return {
                "success": True,
                "fixes_applied": fixes_applied,
                "message": f"Aplicadas {len(fixes_applied)} correções"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na validação: {str(e)}"
            }
    
    def cleanup_resources(self) -> Dict[str, Any]:
        """
        Limpa recursos temporários e arquivos órfãos
        
        Returns:
            Resultado da limpeza
        """
        try:
            cleaned_items = []
            
            # Limpar arquivos temporários
            temp_patterns = ["*.tmp", "*.temp", ".rag_temp_*"]
            
            for pattern in temp_patterns:
                for file_path in Path(".").glob(pattern):
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                            cleaned_items.append(f"Arquivo: {file_path}")
                        elif file_path.is_dir():
                            shutil.rmtree(file_path)
                            cleaned_items.append(f"Diretório: {file_path}")
                    except Exception:
                        continue
            
            # Limpar checkpoints antigos (> 7 dias)
            checkpoint_dir = Path(".rag_checkpoints")
            if checkpoint_dir.exists():
                cutoff_time = datetime.now().timestamp() - (7 * 24 * 3600)
                
                for checkpoint_file in checkpoint_dir.glob("*.json"):
                    try:
                        if checkpoint_file.stat().st_mtime < cutoff_time:
                            checkpoint_file.unlink()
                            cleaned_items.append(f"Checkpoint antigo: {checkpoint_file.name}")
                    except Exception:
                        continue
            
            return {
                "success": True,
                "cleaned_items": cleaned_items,
                "message": f"Limpeza concluída: {len(cleaned_items)} itens removidos"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na limpeza: {str(e)}"
            }
    
    def restore_from_checkpoint(self, checkpoint_path: Path) -> Dict[str, Any]:
        """
        Restaura estado a partir de checkpoint
        
        Args:
            checkpoint_path: Caminho do checkpoint
            
        Returns:
            Resultado da restauração
        """
        try:
            if not checkpoint_path.exists():
                return {
                    "success": False,
                    "message": f"Checkpoint não encontrado: {checkpoint_path}"
                }
            
            # Carregar checkpoint
            checkpoint = ProcessingCheckpoint.load_from_file(checkpoint_path)
            
            # Validar checkpoint
            if not checkpoint.files_remaining:
                return {
                    "success": True,
                    "message": "Checkpoint indica processamento completo",
                    "files_remaining": 0
                }
            
            return {
                "success": True,
                "message": f"Checkpoint carregado: {len(checkpoint.files_remaining)} arquivos restantes",
                "checkpoint": checkpoint,
                "files_remaining": len(checkpoint.files_remaining)
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao restaurar checkpoint: {str(e)}"
            }
    
    def _build_recovery_actions(self) -> Dict[str, RecoveryAction]:
        """Constrói ações de recuperação disponíveis"""
        return {
            "refresh_auth": RecoveryAction(
                name="Renovar Autenticação",
                description="Tenta renovar credenciais do Google Cloud",
                action_type="refresh",
                priority=1,
                auto_execute=True
            ),
            
            "validate_config": RecoveryAction(
                name="Validar Configuração",
                description="Valida e corrige configurações do sistema",
                action_type="validate",
                priority=2,
                auto_execute=True
            ),
            
            "cleanup_temp": RecoveryAction(
                name="Limpeza Temporária",
                description="Remove arquivos temporários e recursos órfãos",
                action_type="cleanup",
                priority=3,
                auto_execute=True
            ),
            
            "restore_checkpoint": RecoveryAction(
                name="Restaurar Checkpoint",
                description="Restaura estado a partir do último checkpoint",
                action_type="restore",
                priority=2,
                auto_execute=False
            )
        }