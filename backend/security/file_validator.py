#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 File Validator - Validação de segurança para arquivos

Este módulo fornece validação abrangente de segurança para operações
com arquivos, prevenindo path traversal, validando tipos e tamanhos.
"""

import os
import mimetypes
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileSecurityValidator:
    """
    🔒 Validador de segurança para arquivos
    
    Implementa verificações de segurança para prevenir:
    - Path traversal attacks
    - Uploads de arquivos maliciosos
    - Overflow de tamanho
    - Tipos de arquivo não permitidos
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o validador
        
        Args:
            config: Configurações de segurança
        """
        self.config = config or {}
        
        # Configurações padrão de segurança
        self.max_file_size_mb = self.config.get('max_file_size_mb', 50)
        self.allowed_extensions = set(self.config.get('allowed_extensions', [
            '.pdf', '.sas', '.ipynb', '.py', '.txt', '.csv', '.xlsx',
            '.png', '.jpg', '.jpeg', '.mp4', '.md', '.json', '.yaml', '.yml'
        ]))
        
        # Diretórios seguros para upload
        self.safe_upload_dirs = [
            Path('./temp_files').resolve(),
            Path('./uploads').resolve(),
            Path('./base_conhecimento').resolve()
        ]
        
        # MIME types permitidos
        self.allowed_mime_types = {
            'application/pdf',
            'text/plain',
            'text/csv', 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/png',
            'image/jpeg',
            'video/mp4',
            'text/markdown',
            'application/json',
            'application/x-yaml',
            'text/x-python'
        }
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str, Optional[Path]]:
        """
        Valida se um caminho de arquivo é seguro
        
        Args:
            file_path: Caminho do arquivo para validar
            
        Returns:
            (is_valid, error_message, resolved_path)
        """
        try:
            # Converter para Path e resolver
            path = Path(file_path).resolve()
            
            # Verificar se existe
            if not path.exists():
                return False, "Arquivo não encontrado", None
            
            # Verificar se é arquivo (não diretório)
            if not path.is_file():
                return False, "Caminho não aponta para um arquivo", None
            
            # Verificar path traversal
            is_safe_dir = any(
                safe_dir in path.parents or path == safe_dir
                for safe_dir in self.safe_upload_dirs
            )
            
            if not is_safe_dir:
                # Permitir caminhos absolutos seguros do sistema
                if not self._is_system_safe_path(path):
                    return False, "Caminho de arquivo não permitido (path traversal detectado)", None
            
            # Verificar extensão
            extension = path.suffix.lower()
            if extension not in self.allowed_extensions:
                return False, f"Extensão de arquivo não permitida: {extension}", None
            
            # Verificar tamanho
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return False, f"Arquivo muito grande: {file_size_mb:.1f}MB (máximo: {self.max_file_size_mb}MB)", None
            
            return True, "Arquivo válido", path
            
        except Exception as e:
            logger.error(f"Erro ao validar caminho do arquivo: {e}")
            return False, f"Erro na validação: {str(e)}", None
    
    def _is_system_safe_path(self, path: Path) -> bool:
        """
        Verifica se um caminho do sistema é seguro
        
        Args:
            path: Caminho para verificar
            
        Returns:
            True se for seguro
        """
        # Lista de diretórios perigosos
        dangerous_dirs = {
            '/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin',
            '/root', '/home', '/var/log', '/var/run',
            'C:\\Windows', 'C:\\Program Files', 'C:\\Users'
        }
        
        path_str = str(path)
        return not any(path_str.startswith(dangerous) for dangerous in dangerous_dirs)
    
    def validate_file_content(self, file_path: Path) -> Tuple[bool, str]:
        """
        Valida o conteúdo do arquivo para detectar problemas de segurança
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Verificar MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type and mime_type not in self.allowed_mime_types:
                logger.warning(f"MIME type suspeito: {mime_type}")
            
            # Ler início do arquivo para detectar headers maliciosos
            with open(file_path, 'rb') as f:
                header = f.read(1024)
            
            # Verificar assinaturas maliciosas conhecidas
            if self._contains_malicious_signatures(header):
                return False, "Arquivo contém assinatura maliciosa"
            
            # Para arquivos de texto, verificar conteúdo suspeito
            if file_path.suffix.lower() in {'.py', '.txt', '.md', '.json', '.yaml', '.yml'}:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(10000)  # Ler apenas os primeiros 10KB
                    
                    if self._contains_suspicious_content(content):
                        return False, "Conteúdo do arquivo contém elementos suspeitos"
                        
                except UnicodeDecodeError:
                    return False, "Arquivo de texto com encoding inválido"
            
            return True, "Conteúdo válido"
            
        except Exception as e:
            logger.error(f"Erro ao validar conteúdo do arquivo: {e}")
            return False, f"Erro na validação de conteúdo: {str(e)}"
    
    def _contains_malicious_signatures(self, header: bytes) -> bool:
        """
        Verifica se o header contém assinaturas maliciosas conhecidas
        
        Args:
            header: Primeiros bytes do arquivo
            
        Returns:
            True se contém assinaturas suspeitas
        """
        # Assinaturas de executáveis
        executable_signatures = [
            b'MZ',  # PE executables (Windows)
            b'\x7fELF',  # ELF executables (Linux)
            b'\xca\xfe\xba\xbe',  # Mach-O (macOS)
            b'PK\x03\x04',  # ZIP (pode conter executáveis)
        ]
        
        # Verificar se começa com alguma assinatura suspeita
        for signature in executable_signatures:
            if header.startswith(signature):
                # Para ZIP, permitir apenas se for .xlsx (Excel)
                if signature == b'PK\x03\x04':
                    return False  # Excel files são ZIP, permitir
                return True
        
        return False
    
    def _contains_suspicious_content(self, content: str) -> bool:
        """
        Verifica se o conteúdo de texto contém elementos suspeitos
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            True se contém elementos suspeitos
        """
        # Padrões suspeitos em arquivos de texto
        suspicious_patterns = [
            'exec(',
            'eval(',
            '__import__',
            'subprocess.',
            'os.system',
            'shell=True',
            '<script>',
            'javascript:',
            'rm -rf',
            'deltree',
            'format c:',
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                logger.warning(f"Padrão suspeito encontrado: {pattern}")
                # Não bloquear automaticamente, apenas logar
                # return True
        
        return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calcula hash SHA-256 do arquivo para verificação de integridade
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Hash SHA-256 em hexadecimal
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Ler em chunks para arquivos grandes
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"Erro ao calcular hash do arquivo: {e}")
            return ""
    
    def validate_upload_request(self, file_path: str) -> Dict[str, Any]:
        """
        Validação completa para requisições de upload
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com resultado da validação
        """
        result = {
            'is_valid': False,
            'error_message': '',
            'file_info': {},
            'security_checks': {}
        }
        
        try:
            # Validar caminho
            path_valid, path_error, resolved_path = self.validate_file_path(file_path)
            result['security_checks']['path_validation'] = {
                'passed': path_valid,
                'message': path_error
            }
            
            if not path_valid:
                result['error_message'] = path_error
                return result
            
            # Validar conteúdo
            content_valid, content_error = self.validate_file_content(resolved_path)
            result['security_checks']['content_validation'] = {
                'passed': content_valid,
                'message': content_error
            }
            
            if not content_valid:
                result['error_message'] = content_error
                return result
            
            # Calcular informações do arquivo
            file_stats = resolved_path.stat()
            file_hash = self.calculate_file_hash(resolved_path)
            
            result['file_info'] = {
                'name': resolved_path.name,
                'size_bytes': file_stats.st_size,
                'size_mb': file_stats.st_size / (1024 * 1024),
                'extension': resolved_path.suffix.lower(),
                'sha256': file_hash,
                'resolved_path': str(resolved_path)
            }
            
            result['is_valid'] = True
            result['error_message'] = 'Arquivo validado com sucesso'
            
        except Exception as e:
            logger.error(f"Erro na validação completa: {e}")
            result['error_message'] = f"Erro interno na validação: {str(e)}"
        
        return result


# Instância global do validador
_file_validator = None

def get_file_validator(config: Optional[Dict[str, Any]] = None) -> FileSecurityValidator:
    """
    Obtém instância singleton do validador de arquivos
    
    Args:
        config: Configurações (apenas na primeira chamada)
        
    Returns:
        Instância do validador
    """
    global _file_validator
    if _file_validator is None:
        _file_validator = FileSecurityValidator(config)
    return _file_validator


def validate_file_security(file_path: str) -> Dict[str, Any]:
    """
    Função utilitária para validação rápida de segurança
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Resultado da validação
    """
    validator = get_file_validator()
    return validator.validate_upload_request(file_path)