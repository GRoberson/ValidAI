#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 File Processing Pipeline - Pipeline integrado de processamento

Este módulo orquestra todo o fluxo de processamento de arquivos,
desde análise até upload, com recuperação de falhas e checkpoints.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import time

from ..core.interfaces import FileProcessorInterface
from ..core.models import RAGConfig, ProcessingResult, ProcessingCheckpoint, CodebaseAnalysis
from ..core.exceptions import ProcessingError, ConfigurationError
from .analyzer import FileAnalyzer
from .uploader import CloudUploader
from .progress import ProgressTracker, ConsoleProgressDisplay


class EnhancedFileProcessor(FileProcessorInterface):
    """
    🔄 Processador de arquivos aprimorado
    
    Orquestra o pipeline completo de processamento:
    1. Análise da base de código
    2. Filtros e validações
    3. Upload resiliente para GCS
    4. Processamento no Vertex AI
    5. Recuperação de falhas
    """
    
    def __init__(self, config: RAGConfig):
        """
        Inicializa o processador
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        
        # Componentes do pipeline
        self.analyzer = FileAnalyzer(config)
        self.uploader = CloudUploader(config)
        self.progress_tracker = ProgressTracker()
        
        # Display de progresso no console
        self.console_display = ConsoleProgressDisplay(self.progress_tracker)
        
        # Estado do processamento
        self.current_checkpoint: Optional[ProcessingCheckpoint] = None
        self.processing_stats = {
            "start_time": None,
            "end_time": None,
            "total_files_found": 0,
            "files_analyzed": 0,
            "files_uploaded": 0,
            "files_failed": 0,
            "total_size_mb": 0.0
        }
        
        # Callbacks personalizados
        self.callbacks: List[Callable] = []
    
    def process_codebase(self, 
                        path: Path, 
                        progress_callback: Optional[Callable] = None,
                        filters: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Processa uma base de código completa
        
        Args:
            path: Caminho para a base de código
            progress_callback: Callback para atualizações de progresso
            filters: Filtros opcionais para arquivos
            
        Returns:
            Resultado do processamento
        """
        try:
            # Registrar callback se fornecido
            if progress_callback:
                self.progress_tracker.add_callback(progress_callback)
            
            # Inicializar estatísticas
            self.processing_stats["start_time"] = datetime.now()
            
            print(f"\n🚀 Iniciando processamento da base de código: {path}")
            
            # Fase 1: Análise da base de código
            print("\n📊 Fase 1: Analisando base de código...")
            codebase_analysis = self._analyze_codebase_phase(path)
            
            # Fase 2: Preparação dos arquivos
            print(f"\n📁 Fase 2: Preparando {codebase_analysis.supported_files} arquivos...")
            files_to_process = self._prepare_files_phase(path, filters)
            
            # Fase 3: Upload dos arquivos
            print(f"\n☁️ Fase 3: Enviando {len(files_to_process)} arquivos para Google Cloud...")
            upload_result = self._upload_files_phase(files_to_process)
            
            # Fase 4: Processamento no Vertex AI (placeholder)
            print(f"\n🧠 Fase 4: Processando arquivos no Vertex AI...")
            processing_result = self._vertex_ai_processing_phase(upload_result)
            
            # Finalizar
            self.processing_stats["end_time"] = datetime.now()
            
            final_result = self._create_final_result(codebase_analysis, upload_result, processing_result)
            
            print(f"\n✅ Processamento concluído!")
            self._print_final_summary(final_result)
            
            return final_result
            
        except Exception as e:
            self.processing_stats["end_time"] = datetime.now()
            
            if isinstance(e, (ProcessingError, ConfigurationError)):
                raise
            
            raise ProcessingError(
                operation="codebase_processing",
                message=f"Erro durante processamento: {str(e)}",
                suggestion="Verifique os logs para mais detalhes"
            )
        
        finally:
            # Limpar callbacks
            if progress_callback and progress_callback in self.progress_tracker.callbacks:
                self.progress_tracker.remove_callback(progress_callback)
    
    def analyze_files(self, files: List[Path]) -> Dict[str, Any]:
        """
        Analisa arquivos para determinar requisitos de processamento
        
        Args:
            files: Lista de arquivos para analisar
            
        Returns:
            Análise dos arquivos (tipos, tamanhos, etc.)
        """
        print(f"\n🔍 Analisando {len(files)} arquivos...")
        
        analysis_results = {
            "total_files": len(files),
            "supported_files": 0,
            "total_size_mb": 0.0,
            "file_analyses": [],
            "language_distribution": {},
            "size_distribution": {"small": 0, "medium": 0, "large": 0},
            "recommendations": []
        }
        
        self.progress_tracker.start_operation("Análise de arquivos", len(files))
        
        try:
            for i, file_path in enumerate(files):
                try:
                    file_analysis = self.analyzer.analyze_file(file_path)
                    analysis_results["file_analyses"].append(file_analysis)
                    
                    if file_analysis.is_supported:
                        analysis_results["supported_files"] += 1
                        analysis_results["total_size_mb"] += file_analysis.size_mb
                        
                        # Distribuição por linguagem
                        if file_analysis.language:
                            lang = file_analysis.language
                            analysis_results["language_distribution"][lang] = \
                                analysis_results["language_distribution"].get(lang, 0) + 1
                        
                        # Distribuição por tamanho
                        if file_analysis.size_mb < 0.1:
                            analysis_results["size_distribution"]["small"] += 1
                        elif file_analysis.size_mb < 1.0:
                            analysis_results["size_distribution"]["medium"] += 1
                        else:
                            analysis_results["size_distribution"]["large"] += 1
                    
                    self.progress_tracker.update_progress(
                        completed_items=i + 1,
                        current_item=file_path.name
                    )
                    
                except Exception as e:
                    print(f"⚠️ Erro ao analisar {file_path}: {e}")
                    continue
            
            # Gerar recomendações
            analysis_results["recommendations"] = self._generate_analysis_recommendations(analysis_results)
            
            self.progress_tracker.finish_operation(success=True)
            
            return analysis_results
            
        except Exception as e:
            self.progress_tracker.finish_operation(success=False, message=str(e))
            raise
    
    def upload_with_retry(self, files: List[Path]) -> ProcessingResult:
        """
        Faz upload de arquivos com retry automático
        
        Args:
            files: Lista de arquivos para upload
            
        Returns:
            Resultado do upload
        """
        return self.uploader.upload_files(files, self.config.gcs_folder)
    
    def resume_processing(self, checkpoint: ProcessingCheckpoint) -> ProcessingResult:
        """
        Resume processamento a partir de um checkpoint
        
        Args:
            checkpoint: Checkpoint de onde resumir
            
        Returns:
            Resultado do processamento resumido
        """
        print(f"\n🔄 Resumindo processamento do checkpoint: {checkpoint.operation_id}")
        
        try:
            # Restaurar estado
            self.current_checkpoint = checkpoint
            
            # Determinar arquivos restantes
            remaining_files = [Path(f) for f in checkpoint.files_remaining]
            
            if not remaining_files:
                print("✅ Todos os arquivos já foram processados!")
                return ProcessingResult(
                    files_processed=len(checkpoint.files_processed),
                    files_skipped=0,
                    files_failed=0,
                    total_size_mb=0,
                    processing_time=0,
                    status="completed"
                )
            
            print(f"📁 Processando {len(remaining_files)} arquivos restantes...")
            
            # Continuar processamento
            return self.upload_with_retry(remaining_files)
            
        except Exception as e:
            raise ProcessingError(
                operation="resume_processing",
                message=f"Erro ao resumir processamento: {str(e)}",
                suggestion="Verifique se o checkpoint é válido"
            )
    
    def create_checkpoint(self) -> ProcessingCheckpoint:
        """
        Cria checkpoint do estado atual
        
        Returns:
            Checkpoint criado
        """
        if not self.current_checkpoint:
            # Criar novo checkpoint
            checkpoint = ProcessingCheckpoint(
                operation_id=f"processing_{int(time.time())}",
                timestamp=datetime.now(),
                files_processed=[],
                files_remaining=[],
                current_state=self.processing_stats.copy()
            )
        else:
            # Atualizar checkpoint existente
            checkpoint = self.current_checkpoint
            checkpoint.timestamp = datetime.now()
            checkpoint.current_state.update(self.processing_stats)
        
        return checkpoint
    
    def save_checkpoint(self, checkpoint: ProcessingCheckpoint, path: Optional[Path] = None) -> Path:
        """
        Salva checkpoint em arquivo
        
        Args:
            checkpoint: Checkpoint a salvar
            path: Caminho do arquivo (opcional)
            
        Returns:
            Caminho onde foi salvo
        """
        if not path:
            checkpoint_dir = Path(".rag_checkpoints")
            checkpoint_dir.mkdir(exist_ok=True)
            path = checkpoint_dir / f"{checkpoint.operation_id}.json"
        
        try:
            checkpoint.save_to_file(path)
            print(f"💾 Checkpoint salvo: {path}")
            return path
            
        except Exception as e:
            raise ProcessingError(
                operation="save_checkpoint",
                message=f"Erro ao salvar checkpoint: {str(e)}",
                suggestion="Verifique permissões de escrita"
            )
    
    def load_checkpoint(self, path: Path) -> ProcessingCheckpoint:
        """
        Carrega checkpoint de arquivo
        
        Args:
            path: Caminho do arquivo
            
        Returns:
            Checkpoint carregado
        """
        try:
            return ProcessingCheckpoint.load_from_file(path)
            
        except Exception as e:
            raise ProcessingError(
                operation="load_checkpoint",
                message=f"Erro ao carregar checkpoint: {str(e)}",
                suggestion="Verifique se o arquivo existe e tem formato válido"
            )
    
    def add_callback(self, callback: Callable) -> None:
        """Adiciona callback personalizado"""
        self.callbacks.append(callback)
        self.progress_tracker.add_callback(callback)
    
    def remove_callback(self, callback: Callable) -> None:
        """Remove callback personalizado"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
        self.progress_tracker.remove_callback(callback)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de processamento
        
        Returns:
            Dicionário com estatísticas
        """
        stats = self.processing_stats.copy()
        
        # Adicionar estatísticas de upload
        upload_stats = self.uploader.get_upload_stats()
        stats.update(upload_stats)
        
        # Adicionar estatísticas de progresso
        progress_stats = self.progress_tracker.get_current_status()
        stats.update(progress_stats)
        
        return stats
    
    def _analyze_codebase_phase(self, path: Path) -> CodebaseAnalysis:
        """Fase 1: Análise da base de código"""
        analysis = self.analyzer.analyze_codebase(path)
        
        self.processing_stats.update({
            "total_files_found": analysis.total_files,
            "files_analyzed": analysis.supported_files,
            "total_size_mb": analysis.total_size_mb
        })
        
        print(f"📊 Análise concluída:")
        print(f"   📁 Total de arquivos: {analysis.total_files}")
        print(f"   ✅ Arquivos suportados: {analysis.supported_files}")
        print(f"   📏 Tamanho total: {analysis.total_size_mb:.1f} MB")
        
        if analysis.language_distribution:
            top_languages = list(analysis.language_distribution.items())[:3]
            languages_str = ", ".join([f"{lang} ({count})" for lang, count in top_languages])
            print(f"   🔤 Principais linguagens: {languages_str}")
        
        return analysis
    
    def _prepare_files_phase(self, path: Path, filters: Optional[Dict[str, Any]]) -> List[Path]:
        """Fase 2: Preparação dos arquivos"""
        # Coletar todos os arquivos
        all_files = []
        for file_path in path.rglob('*'):
            if file_path.is_file():
                all_files.append(file_path)
        
        # Aplicar filtros se fornecidos
        if filters:
            filtered_files = self.analyzer.filter_files_by_criteria(all_files, filters)
        else:
            # Filtrar apenas por suporte básico
            filtered_files = []
            for file_path in all_files:
                try:
                    analysis = self.analyzer.analyze_file(file_path)
                    if analysis.is_supported:
                        filtered_files.append(file_path)
                except Exception:
                    continue
        
        print(f"📁 Arquivos preparados: {len(filtered_files)}")
        return filtered_files
    
    def _upload_files_phase(self, files: List[Path]) -> ProcessingResult:
        """Fase 3: Upload dos arquivos"""
        if not files:
            return ProcessingResult(
                files_processed=0,
                files_skipped=0,
                files_failed=0,
                total_size_mb=0,
                processing_time=0,
                status="completed"
            )
        
        # Configurar uploader com progress tracker
        self.uploader.progress_tracker = self.progress_tracker
        
        # Executar upload
        result = self.uploader.upload_files(files, self.config.gcs_folder)
        
        self.processing_stats.update({
            "files_uploaded": result.files_processed,
            "files_failed": result.files_failed
        })
        
        return result
    
    def _vertex_ai_processing_phase(self, upload_result: ProcessingResult) -> Dict[str, Any]:
        """Fase 4: Processamento no Vertex AI (placeholder)"""
        # Esta fase seria implementada com a integração real do Vertex AI
        # Por enquanto, retorna resultado simulado
        
        if upload_result.files_processed == 0:
            return {"status": "skipped", "reason": "no_files_uploaded"}
        
        print(f"🧠 Processando {upload_result.files_processed} arquivos no Vertex AI...")
        
        # Simular processamento
        time.sleep(1)
        
        return {
            "status": "completed",
            "files_processed": upload_result.files_processed,
            "corpus_created": True,
            "embeddings_generated": True
        }
    
    def _create_final_result(self, 
                           codebase_analysis: CodebaseAnalysis,
                           upload_result: ProcessingResult,
                           vertex_result: Dict[str, Any]) -> ProcessingResult:
        """Cria resultado final consolidado"""
        
        total_time = 0
        if self.processing_stats["start_time"] and self.processing_stats["end_time"]:
            total_time = (self.processing_stats["end_time"] - self.processing_stats["start_time"]).total_seconds()
        
        return ProcessingResult(
            files_processed=upload_result.files_processed,
            files_skipped=upload_result.files_skipped,
            files_failed=upload_result.files_failed,
            total_size_mb=codebase_analysis.total_size_mb,
            processing_time=total_time,
            status="completed" if upload_result.files_failed == 0 else "partial_failure",
            errors=upload_result.errors,
            warnings=[]
        )
    
    def _generate_analysis_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações baseadas no número de arquivos
        if analysis["supported_files"] == 0:
            recommendations.append("Nenhum arquivo suportado encontrado. Verifique o diretório e as extensões configuradas.")
        elif analysis["supported_files"] > 1000:
            recommendations.append("Muitos arquivos detectados. Considere filtrar apenas os diretórios mais importantes.")
        
        # Recomendações baseadas no tamanho
        if analysis["total_size_mb"] > 100:
            recommendations.append("Base de código grande detectada. O processamento pode demorar mais tempo.")
        
        # Recomendações baseadas nas linguagens
        languages = analysis.get("language_distribution", {})
        if len(languages) > 5:
            recommendations.append("Múltiplas linguagens detectadas. Considere processar cada linguagem separadamente.")
        
        return recommendations
    
    def _print_final_summary(self, result: ProcessingResult) -> None:
        """Imprime resumo final"""
        print(f"\n📊 Resumo Final:")
        print(f"   ✅ Arquivos processados: {result.files_processed}")
        print(f"   ⏭️ Arquivos pulados: {result.files_skipped}")
        print(f"   ❌ Arquivos com falha: {result.files_failed}")
        print(f"   📏 Tamanho total: {result.total_size_mb:.1f} MB")
        print(f"   ⏱️ Tempo total: {result.processing_time:.1f}s")
        
        if result.errors:
            print(f"\n⚠️ Erros encontrados:")
            for error in result.errors[:5]:  # Mostrar apenas os primeiros 5
                print(f"   • {error}")
            
            if len(result.errors) > 5:
                print(f"   ... e mais {len(result.errors) - 5} erros")
        
        # Status final
        if result.status == "completed":
            print(f"\n🎉 Processamento concluído com sucesso!")
        else:
            print(f"\n⚠️ Processamento concluído com algumas falhas")
            print(f"💡 Verifique os erros acima e tente novamente se necessário")