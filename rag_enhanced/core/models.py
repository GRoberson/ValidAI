#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Models - Modelos de dados para o RAG Enhanced

Este módulo define todas as classes de dados (dataclasses) utilizadas
pelo sistema, incluindo configurações, resultados e contextos.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from enum import Enum


class ValidationStatus(Enum):
    """Status de validação"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"


class ProcessingStatus(Enum):
    """Status de processamento"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ErrorSeverity(Enum):
    """Severidade de erro"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RAGConfig:
    """
    🔧 Configuração principal do sistema RAG Enhanced
    
    Contém todas as configurações necessárias para o funcionamento
    do sistema, incluindo credenciais, parâmetros de processamento
    e configurações avançadas.
    """
    
    # Configurações obrigatórias do Google Cloud
    project_id: str
    bucket_name: str
    location: str = "us-central1"
    
    # Caminho da base de código
    codebase_path: Path = field(default_factory=lambda: Path("."))
    
    # Configurações de processamento
    max_file_size_mb: int = 10
    chunk_size: int = 1024
    chunk_overlap: int = 256
    parallel_uploads: int = 5
    
    # Modelos de IA
    embedding_model: str = "publishers/google/models/text-embedding-005"
    generation_model: str = "gemini-2.5-flash"
    
    # Configurações avançadas
    retry_attempts: int = 3
    timeout_seconds: int = 300
    enable_caching: bool = True
    enable_compression: bool = True
    
    # Configurações de pasta no GCS
    gcs_folder: str = "rag-codebase"
    
    # Tipos de arquivo suportados
    supported_extensions: List[str] = field(default_factory=lambda: [
        ".py", ".java", ".js", ".ts", ".go", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".rs", ".dart",
        ".md", ".txt", ".rst", ".html", ".css", ".scss", ".json", ".yaml", ".yml"
    ])
    
    # Configurações de temperatura e tokens
    temperature: float = 0.2
    max_output_tokens: int = 8000
    
    def __post_init__(self):
        """Validação e normalização após inicialização"""
        if isinstance(self.codebase_path, str):
            self.codebase_path = Path(self.codebase_path)
        
        # Normalizar extensões
        self.supported_extensions = [
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in self.supported_extensions
        ]
    
    def validate(self) -> 'ValidationResult':
        """
        Valida a configuração
        
        Returns:
            Resultado da validação com detalhes
        """
        issues = []
        
        # Validar campos obrigatórios
        if not self.project_id or self.project_id == "seu-projeto-aqui":
            issues.append(ValidationIssue(
                field="project_id",
                severity=ErrorSeverity.CRITICAL,
                message="Project ID é obrigatório e deve ser um ID válido do Google Cloud",
                suggestion="Configure o ID do seu projeto Google Cloud"
            ))
        
        if not self.bucket_name or self.bucket_name == "seu-bucket-aqui":
            issues.append(ValidationIssue(
                field="bucket_name", 
                severity=ErrorSeverity.CRITICAL,
                message="Nome do bucket é obrigatório",
                suggestion="Configure o nome do seu bucket no Google Cloud Storage"
            ))
        
        # Validar caminho da base de código
        if not self.codebase_path.exists():
            issues.append(ValidationIssue(
                field="codebase_path",
                severity=ErrorSeverity.HIGH,
                message=f"Caminho da base de código não existe: {self.codebase_path}",
                suggestion="Verifique se o caminho está correto"
            ))
        
        # Validar parâmetros numéricos
        if self.temperature < 0 or self.temperature > 2:
            issues.append(ValidationIssue(
                field="temperature",
                severity=ErrorSeverity.MEDIUM,
                message="Temperatura deve estar entre 0 e 2",
                suggestion="Use valores entre 0.1 (mais determinístico) e 1.0 (mais criativo)"
            ))
        
        if self.max_output_tokens <= 0:
            issues.append(ValidationIssue(
                field="max_output_tokens",
                severity=ErrorSeverity.MEDIUM,
                message="Max output tokens deve ser maior que 0",
                suggestion="Use valores entre 1000 e 8000"
            ))
        
        # Determinar status geral
        if any(issue.severity == ErrorSeverity.CRITICAL for issue in issues):
            status = ValidationStatus.ERROR
        elif any(issue.severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM] for issue in issues):
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID
        
        return ValidationResult(
            status=status,
            issues=issues,
            is_valid=status != ValidationStatus.ERROR
        )


@dataclass
class ValidationIssue:
    """
    ⚠️ Problema encontrado durante validação
    """
    field: str
    severity: ErrorSeverity
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """
    ✅ Resultado de uma validação
    """
    status: ValidationStatus
    issues: List[ValidationIssue]
    is_valid: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_error_summary(self) -> str:
        """
        Gera resumo dos erros encontrados
        
        Returns:
            Resumo formatado dos erros
        """
        if not self.issues:
            return "✅ Configuração válida"
        
        summary = []
        for issue in self.issues:
            emoji = {
                ErrorSeverity.CRITICAL: "🚨",
                ErrorSeverity.HIGH: "❌", 
                ErrorSeverity.MEDIUM: "⚠️",
                ErrorSeverity.LOW: "ℹ️"
            }[issue.severity]
            
            summary.append(f"{emoji} {issue.field}: {issue.message}")
            if issue.suggestion:
                summary.append(f"   💡 {issue.suggestion}")
        
        return "\n".join(summary)


@dataclass
class ProcessingCheckpoint:
    """
    📍 Checkpoint para resumir processamento
    """
    operation_id: str
    timestamp: datetime
    files_processed: List[str]
    files_remaining: List[str]
    current_state: Dict[str, Any]
    error_count: int = 0
    
    def save_to_file(self, path: Path) -> None:
        """Salva checkpoint em arquivo"""
        import json
        
        data = {
            'operation_id': self.operation_id,
            'timestamp': self.timestamp.isoformat(),
            'files_processed': self.files_processed,
            'files_remaining': self.files_remaining,
            'current_state': self.current_state,
            'error_count': self.error_count
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'ProcessingCheckpoint':
        """Carrega checkpoint de arquivo"""
        import json
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls(
            operation_id=data['operation_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            files_processed=data['files_processed'],
            files_remaining=data['files_remaining'],
            current_state=data['current_state'],
            error_count=data.get('error_count', 0)
        )


@dataclass
class ProcessingResult:
    """
    📊 Resultado de processamento de arquivos
    """
    files_processed: int
    files_skipped: int
    files_failed: int
    total_size_mb: float
    processing_time: float
    status: ProcessingStatus
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checkpoint: Optional[ProcessingCheckpoint] = None
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso do processamento"""
        total = self.files_processed + self.files_skipped + self.files_failed
        return (self.files_processed / total * 100) if total > 0 else 0
    
    def get_summary(self) -> str:
        """
        Gera resumo do processamento
        
        Returns:
            Resumo formatado
        """
        return f"""
📊 Resumo do Processamento:
   ✅ Processados: {self.files_processed}
   ⏭️ Pulados: {self.files_skipped}
   ❌ Falharam: {self.files_failed}
   📏 Tamanho total: {self.total_size_mb:.1f} MB
   ⏱️ Tempo: {self.processing_time:.1f}s
   📈 Taxa de sucesso: {self.success_rate:.1f}%
        """.strip()


@dataclass
class QueryResponse:
    """
    💬 Resposta de uma consulta
    """
    query: str
    answer: str
    confidence_score: float
    processing_time: float
    sources: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def format_response(self) -> str:
        """
        Formata resposta para exibição
        
        Returns:
            Resposta formatada
        """
        formatted = f"🤖 **Resposta:** {self.answer}\n"
        
        if self.confidence_score > 0:
            confidence_emoji = "🎯" if self.confidence_score > 0.8 else "🤔" if self.confidence_score > 0.5 else "❓"
            formatted += f"{confidence_emoji} **Confiança:** {self.confidence_score:.1%}\n"
        
        if self.sources:
            formatted += f"\n📚 **Fontes:**\n"
            for source in self.sources[:3]:  # Limitar a 3 fontes
                formatted += f"   • {source}\n"
        
        if self.suggestions:
            formatted += f"\n💡 **Sugestões:**\n"
            for suggestion in self.suggestions[:2]:  # Limitar a 2 sugestões
                formatted += f"   • {suggestion}\n"
        
        return formatted


@dataclass
class ErrorContext:
    """
    🔍 Contexto de um erro
    """
    operation: str
    component: str
    timestamp: datetime
    user_action: Optional[str] = None
    system_state: Dict[str, Any] = field(default_factory=dict)
    previous_errors: List[str] = field(default_factory=list)
    
    def add_context(self, key: str, value: Any) -> None:
        """Adiciona informação ao contexto"""
        self.system_state[key] = value


@dataclass
class DiagnosticsReport:
    """
    🔍 Relatório de diagnósticos do sistema
    """
    timestamp: datetime
    overall_status: str
    component_status: Dict[str, str]
    issues_found: List[str]
    recommendations: List[str]
    system_info: Dict[str, Any]
    
    def format_report(self) -> str:
        """
        Formata relatório para exibição
        
        Returns:
            Relatório formatado
        """
        status_emoji = "✅" if self.overall_status == "healthy" else "⚠️" if self.overall_status == "warning" else "❌"
        
        report = f"{status_emoji} **Status Geral:** {self.overall_status}\n\n"
        
        report += "🔧 **Componentes:**\n"
        for component, status in self.component_status.items():
            comp_emoji = "✅" if status == "ok" else "⚠️" if status == "warning" else "❌"
            report += f"   {comp_emoji} {component}: {status}\n"
        
        if self.issues_found:
            report += "\n⚠️ **Problemas Encontrados:**\n"
            for issue in self.issues_found:
                report += f"   • {issue}\n"
        
        if self.recommendations:
            report += "\n💡 **Recomendações:**\n"
            for rec in self.recommendations:
                report += f"   • {rec}\n"
        
        return report


@dataclass
class FileAnalysis:
    """
    📄 Análise de um arquivo
    """
    path: Path
    size_bytes: int
    file_type: str
    language: Optional[str] = None
    encoding: str = "utf-8"
    line_count: Optional[int] = None
    is_supported: bool = True
    skip_reason: Optional[str] = None
    
    @property
    def size_mb(self) -> float:
        """Tamanho em MB"""
        return self.size_bytes / (1024 * 1024)
    
    def __str__(self) -> str:
        status = "✅" if self.is_supported else "⏭️"
        return f"{status} {self.path.name} ({self.size_mb:.1f}MB, {self.language or self.file_type})"


@dataclass
class CodebaseAnalysis:
    """
    📊 Análise completa de uma base de código
    """
    total_files: int
    supported_files: int
    total_size_mb: float
    language_distribution: Dict[str, int]
    file_type_distribution: Dict[str, int]
    largest_files: List[FileAnalysis]
    analysis_time: float
    
    def get_summary(self) -> str:
        """
        Gera resumo da análise
        
        Returns:
            Resumo formatado
        """
        return f"""
📊 Análise da Base de Código:
   📁 Total de arquivos: {self.total_files}
   ✅ Arquivos suportados: {self.supported_files}
   📏 Tamanho total: {self.total_size_mb:.1f} MB
   🔤 Linguagens principais: {', '.join(list(self.language_distribution.keys())[:3])}
   ⏱️ Tempo de análise: {self.analysis_time:.1f}s
        """.strip()