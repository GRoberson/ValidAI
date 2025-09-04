#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 Security Module - Módulo de segurança do backend

Este módulo fornece funcionalidades de segurança centralizadas
para o sistema ValidAI.
"""

from .file_validator import FileSecurityValidator, get_file_validator, validate_file_security

__all__ = [
    'FileSecurityValidator',
    'get_file_validator', 
    'validate_file_security'
]