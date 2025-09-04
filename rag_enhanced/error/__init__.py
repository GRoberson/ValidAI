#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ Error - Sistema abrangente de tratamento de erros

Este módulo fornece tratamento inteligente de erros com
classificação automática, estratégias de recuperação e diagnósticos.
"""

from .handler import ErrorHandler
from .retry import RetryManager
from .recovery import RecoveryManager
from .diagnostics import DiagnosticsRunner

__all__ = [
    'ErrorHandler',
    'RetryManager',
    'RecoveryManager',
    'DiagnosticsRunner'
]