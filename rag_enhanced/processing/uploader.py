#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
☁️ Cloud Uploader - Upload resiliente para Google Cloud Storage

Este módulo fornece upload robusto com retry automático, paralelização
inteligente, compressão e recuperação de falhas.
"""

import os
import gzip
import hashlib
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import time

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from google.api_core import retry, exceptions

from ..core.models import RAGConfig, ProcessingResult, ProcessingCheckpoint
from ..core.exceptions import ProcessingError, NetworkError, AuthenticationError
from .progress import ProgressTracker


@dataclass
class UploadTask:
    """
    📤 Tarefa de upload individual
    """
    local_path: Path
    gcs_path: str
    size_bytes: int
    checksum: Optional[str] = None
    compressed: bool = False
    attempts: int = 0
    max_attempts: int = 3
    
    @property
    def size_mb(self) -> float:
        """Tamanho em MB"""
        return self.size_bytes / (1024 * 1024)


@dataclass
class UploadResult:
    """
    📊 Resultado de upload
    """
    task: UploadTask
    success: bool
    upload_time: float
    error_message: Optional[str] = None
    bytes_uploaded: int = 0
    
    @property
    def upload_speed_mbps(self) -> float:
        """Velocidade de upload em MB/s"""
        if self.upload_time <= 0:
            return 0.0
        return (self.bytes_uploaded / (1024 * 1024)) / self.upload_time


class CloudUploader:
    """
    ☁️ Uploader resiliente para Google Cloud Storage
    
    Fornece upload robusto com:
    - Retry automático com backoff exponencial
    - Upload paralelo com controle de concorrência
    - Compressão automática para arquivos de texto
    - Verificação de integridade com checksums
    - Recuperação de uploads parciais
    - Monitoramento de progresso em tempo real
    """
    
    def __init__(self, config: RAGConfig, progress_tracker: Optional[ProgressTracker] = None):
        """
        Inicializa o uploader
        
        Args:
            config: Configuração do sistema
            progress_tracker: Rastreador de progresso opcional
        """
        self.config = config
        self.progress_tracker = progress_tracker
        
        # Cliente Google Cloud Storage
        self.storage_client = None
        self.bucket = None
        
        # Configurações de upload
        self.max_workers = min(config.parallel_uploads, 20)
        self.chunk_size = 8 * 1024 * 1024  # 8MB chunks
        self.compression_threshold = 1024   # Comprimir arquivos > 1KB
        
        # Controle de rate limiting
        self.rate_limiter = threading.Semaphore(self.max_workers)
        self.upload_stats = {
            "total_bytes": 0,
            "uploaded_bytes": 0,
            "files_uploaded": 0,
            "files_failed": 0,
            "start_time": None
        }
        
        # Lock para thread safety
        self._lock = threading.Lock()
    
    def initialize_client(self) -> None:
        """
        Inicializa cliente Google Cloud Storage
        
        Raises:
            AuthenticationError: Se não conseguir autenticar
            ProcessingError: Se não conseguir acessar o bucket
        """
        try:
            # Criar cliente
            self.storage_client = storage.Client(project=self.config.project_id)
            
            # Verificar acesso ao bucket
            self.bucket = self.storage_client.bucket(self.config.bucket_name)
            
            # Testar acesso
            try:
                self.bucket.reload()
            except exceptions.NotFound:
                # Tentar criar bucket se não existir
                self._create_bucket_if_needed()
            
        except exceptions.Forbidden as e:
            raise AuthenticationError(
                service="Google Cloud Storage",
                message="Acesso negado ao bucket",
                suggestion="Verifique se você tem permissões de Storage Admin"
            )
        except Exception as e:
            raise ProcessingError(
                operation="storage_initialization",
                message=f"Erro ao inicializar cliente: {str(e)}",
                suggestion="Verifique suas credenciais e configurações"
            )
    
    def upload_files(self, files: List[Path], gcs_folder: Optional[str] = None) -> ProcessingResult:
        """
        Faz upload de múltiplos arquivos
        
        Args:
            files: Lista de arquivos para upload
            gcs_folder: Pasta no GCS (opcional)
            
        Returns:
            Resultado do processamento
        """
        if not self.storage_client:
            self.initialize_client()
        
        start_time = time.time()
        
        # Preparar tarefas de upload
        upload_tasks = self._prepare_upload_tasks(files, gcs_folder)
        
        if not upload_tasks:
            return ProcessingResult(
                files_processed=0,
                files_skipped=len(files),
                files_failed=0,
                total_size_mb=0,
                processing_time=0,
                status="completed"
            )
        
        # Inicializar estatísticas
        total_size = sum(task.size_bytes for task in upload_tasks)
        self.upload_stats.update({
            "total_bytes": total_size,
            "uploaded_bytes": 0,
            "files_uploaded": 0,
            "files_failed": 0,
            "start_time": datetime.now()
        })
        
        # Iniciar rastreamento de progresso
        if self.progress_tracker:
            self.progress_tracker.start_operation(
                "Upload de arquivos",
                len(upload_tasks),
                total_size
            )
        
        # Executar uploads em paralelo
        results = self._execute_parallel_uploads(upload_tasks)
        
        # Processar resultados
        successful_uploads = [r for r in results if r.success]
        failed_uploads = [r for r in results if not r.success]
        
        processing_time = time.time() - start_time
        
        # Finalizar progresso
        if self.progress_tracker:
            self.progress_tracker.finish_operation(
                success=len(failed_uploads) == 0,
                message=f"Upload concluído: {len(successful_uploads)} sucessos, {len(failed_uploads)} falhas"
            )
        
        return ProcessingResult(
            files_processed=len(successful_uploads),
            files_skipped=0,
            files_failed=len(failed_uploads),
            total_size_mb=total_size / (1024 * 1024),
            processing_time=processing_time,
            status="completed" if len(failed_uploads) == 0 else "partial_failure",
            errors=[r.error_message for r in failed_uploads if r.error_message]
        )
    
    def upload_single_file(self, 
                          local_path: Path, 
                          gcs_path: str, 
                          compress: bool = None) -> UploadResult:
        """
        Faz upload de um arquivo individual
        
        Args:
            local_path: Caminho local do arquivo
            gcs_path: Caminho no GCS
            compress: Se deve comprimir (auto-detecta se None)
            
        Returns:
            Resultado do upload
        """
        if not self.storage_client:
            self.initialize_client()
        
        # Preparar tarefa
        task = UploadTask(
            local_path=local_path,
            gcs_path=gcs_path,
            size_bytes=local_path.stat().st_size,
            max_attempts=self.config.retry_attempts
        )
        
        # Determinar se deve comprimir
        if compress is None:
            compress = self._should_compress_file(local_path)
        
        task.compressed = compress
        
        return self._upload_file_with_retry(task)
    
    def verify_upload(self, local_path: Path, gcs_path: str) -> bool:
        """
        Verifica se um arquivo foi enviado corretamente
        
        Args:
            local_path: Caminho local do arquivo
            gcs_path: Caminho no GCS
            
        Returns:
            True se o arquivo existe e tem o mesmo tamanho
        """
        try:
            blob = self.bucket.blob(gcs_path)
            
            # Verificar se existe
            if not blob.exists():
                return False
            
            # Verificar tamanho
            blob.reload()
            local_size = local_path.stat().st_size
            
            # Se foi comprimido, não podemos comparar tamanhos diretamente
            if gcs_path.endswith('.gz'):
                return True  # Assumir que está correto se existe
            
            return blob.size == local_size
            
        except Exception:
            return False
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de upload
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            stats = self.upload_stats.copy()
            
            if stats["start_time"]:
                elapsed = (datetime.now() - stats["start_time"]).total_seconds()
                stats["elapsed_seconds"] = elapsed
                
                if elapsed > 0:
                    stats["upload_speed_mbps"] = (stats["uploaded_bytes"] / (1024 * 1024)) / elapsed
                else:
                    stats["upload_speed_mbps"] = 0
            
            return stats
    
    def create_checkpoint(self, completed_files: List[str]) -> ProcessingCheckpoint:
        """
        Cria checkpoint do progresso de upload
        
        Args:
            completed_files: Lista de arquivos já enviados
            
        Returns:
            Checkpoint criado
        """
        return ProcessingCheckpoint(
            operation_id=f"upload_{int(time.time())}",
            timestamp=datetime.now(),
            files_processed=completed_files,
            files_remaining=[],  # Será preenchido pelo caller
            current_state={
                "bucket_name": self.config.bucket_name,
                "gcs_folder": self.config.gcs_folder,
                "upload_stats": self.get_upload_stats()
            }
        )
    
    def _prepare_upload_tasks(self, files: List[Path], gcs_folder: Optional[str]) -> List[UploadTask]:
        """Prepara tarefas de upload"""
        tasks = []
        base_folder = gcs_folder or self.config.gcs_folder
        
        for file_path in files:
            if not file_path.exists() or not file_path.is_file():
                continue
            
            # Calcular caminho no GCS
            relative_path = file_path.name  # Simplificado - pode ser melhorado
            if base_folder:
                gcs_path = f"{base_folder.strip('/')}/{relative_path}"
            else:
                gcs_path = relative_path
            
            # Criar tarefa
            task = UploadTask(
                local_path=file_path,
                gcs_path=gcs_path,
                size_bytes=file_path.stat().st_size,
                max_attempts=self.config.retry_attempts
            )
            
            # Determinar se deve comprimir
            task.compressed = self._should_compress_file(file_path)
            if task.compressed:
                task.gcs_path += '.gz'
            
            tasks.append(task)
        
        return tasks
    
    def _execute_parallel_uploads(self, tasks: List[UploadTask]) -> List[UploadResult]:
        """Executa uploads em paralelo"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter todas as tarefas
            future_to_task = {
                executor.submit(self._upload_file_with_retry, task): task
                for task in tasks
            }
            
            # Processar resultados conforme completam
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Atualizar estatísticas
                    with self._lock:
                        if result.success:
                            self.upload_stats["files_uploaded"] += 1
                            self.upload_stats["uploaded_bytes"] += result.bytes_uploaded
                        else:
                            self.upload_stats["files_failed"] += 1
                    
                    # Atualizar progresso
                    if self.progress_tracker:
                        self.progress_tracker.update_progress(
                            current_item=task.local_path.name,
                            bytes_processed=self.upload_stats["uploaded_bytes"]
                        )
                
                except Exception as e:
                    # Criar resultado de erro
                    error_result = UploadResult(
                        task=task,
                        success=False,
                        upload_time=0,
                        error_message=str(e)
                    )
                    results.append(error_result)
                    
                    with self._lock:
                        self.upload_stats["files_failed"] += 1
        
        return results
    
    def _upload_file_with_retry(self, task: UploadTask) -> UploadResult:
        """Upload com retry automático"""
        last_error = None
        
        for attempt in range(task.max_attempts):
            try:
                task.attempts = attempt + 1
                
                # Rate limiting
                with self.rate_limiter:
                    return self._upload_file_once(task)
            
            except Exception as e:
                last_error = e
                
                # Determinar se deve tentar novamente
                if not self._should_retry_error(e) or attempt == task.max_attempts - 1:
                    break
                
                # Backoff exponencial
                wait_time = min(2 ** attempt, 60)  # Máximo 60 segundos
                time.sleep(wait_time)
        
        # Falha após todas as tentativas
        return UploadResult(
            task=task,
            success=False,
            upload_time=0,
            error_message=f"Falha após {task.attempts} tentativas: {str(last_error)}"
        )
    
    def _upload_file_once(self, task: UploadTask) -> UploadResult:
        """Executa upload uma vez"""
        start_time = time.time()
        
        try:
            blob = self.bucket.blob(task.gcs_path)
            
            # Preparar dados para upload
            if task.compressed:
                data, size = self._compress_file(task.local_path)
            else:
                with open(task.local_path, 'rb') as f:
                    data = f.read()
                size = len(data)
            
            # Configurar metadata
            metadata = {
                'original_name': task.local_path.name,
                'upload_time': datetime.now().isoformat(),
                'compressed': str(task.compressed)
            }
            
            if task.compressed:
                blob.content_encoding = 'gzip'
            
            blob.metadata = metadata
            
            # Upload com timeout
            blob.upload_from_string(
                data,
                timeout=self.config.timeout_seconds,
                checksum="md5"  # Verificação de integridade
            )
            
            upload_time = time.time() - start_time
            
            return UploadResult(
                task=task,
                success=True,
                upload_time=upload_time,
                bytes_uploaded=size
            )
            
        except Exception as e:
            upload_time = time.time() - start_time
            
            # Classificar erro
            if isinstance(e, (exceptions.TooManyRequests, exceptions.ServiceUnavailable)):
                raise NetworkError(
                    operation="file_upload",
                    message="Limite de taxa atingido ou serviço indisponível",
                    retry_count=task.attempts
                )
            elif isinstance(e, exceptions.Forbidden):
                raise AuthenticationError(
                    service="Google Cloud Storage",
                    message="Permissão negada para upload"
                )
            else:
                raise ProcessingError(
                    operation="file_upload",
                    message=str(e),
                    file_path=str(task.local_path)
                )
    
    def _should_compress_file(self, file_path: Path) -> bool:
        """Determina se deve comprimir o arquivo"""
        if not self.config.enable_compression:
            return False
        
        # Não comprimir arquivos já comprimidos
        compressed_extensions = {'.gz', '.zip', '.bz2', '.xz', '.7z', '.rar'}
        if file_path.suffix.lower() in compressed_extensions:
            return False
        
        # Não comprimir arquivos binários
        binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp4', '.mp3'}
        if file_path.suffix.lower() in binary_extensions:
            return False
        
        # Comprimir apenas arquivos de texto acima do threshold
        if file_path.stat().st_size < self.compression_threshold:
            return False
        
        # Verificar se é arquivo de texto
        text_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
                          '.cs', '.rb', '.php', '.go', '.rs', '.scala', '.kt',
                          '.html', '.css', '.scss', '.xml', '.json', '.yaml', '.yml',
                          '.md', '.txt', '.rst', '.sql', '.sh', '.bat'}
        
        return file_path.suffix.lower() in text_extensions
    
    def _compress_file(self, file_path: Path) -> Tuple[bytes, int]:
        """Comprime arquivo e retorna dados comprimidos"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        compressed_data = gzip.compress(data)
        return compressed_data, len(compressed_data)
    
    def _should_retry_error(self, error: Exception) -> bool:
        """Determina se deve tentar novamente após erro"""
        # Retry para erros de rede temporários
        if isinstance(error, (NetworkError, exceptions.TooManyRequests, 
                            exceptions.ServiceUnavailable, exceptions.InternalServerError)):
            return True
        
        # Não retry para erros de autenticação ou permissão
        if isinstance(error, (AuthenticationError, exceptions.Forbidden)):
            return False
        
        # Retry para timeouts
        if "timeout" in str(error).lower():
            return True
        
        return False
    
    def _create_bucket_if_needed(self) -> None:
        """Cria bucket se não existir"""
        try:
            bucket = self.storage_client.create_bucket(
                self.config.bucket_name,
                location=self.config.location
            )
            self.bucket = bucket
            
        except exceptions.Conflict:
            # Bucket já existe, mas não temos acesso
            raise AuthenticationError(
                service="Google Cloud Storage",
                message=f"Bucket '{self.config.bucket_name}' existe mas não temos acesso",
                suggestion="Verifique permissões ou use outro nome de bucket"
            )
        except Exception as e:
            raise ProcessingError(
                operation="bucket_creation",
                message=f"Erro ao criar bucket: {str(e)}",
                suggestion="Verifique se o nome do bucket é único globalmente"
            )