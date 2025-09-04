#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 Mock Services - Serviços mock para testes

Este módulo fornece mocks completos dos serviços Google Cloud
permitindo testes offline sem dependências externas.
"""

import json
import time
import random
from typing import Dict, List, Optional, Any, Union
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ..core.exceptions import NetworkError, AuthenticationError, RateLimitError


@dataclass
class MockFile:
    """
    📄 Arquivo simulado para testes
    """
    name: str
    content: str
    size: int
    mime_type: str = "text/plain"
    
    @property
    def size_mb(self) -> float:
        return self.size / (1024 * 1024)


@dataclass
class MockBlob:
    """
    📄 Mock de um blob do Google Cloud Storage
    """
    name: str
    bucket_name: str
    size: int = 0
    content_type: str = "application/octet-stream"
    metadata: Dict[str, str] = field(default_factory=dict)
    content: bytes = b""
    
    def upload_from_string(self, data: Union[str, bytes], **kwargs):
        """Mock do upload de string"""
        if isinstance(data, str):
            self.content = data.encode('utf-8')
        else:
            self.content = data
        self.size = len(self.content)
    
    def upload_from_filename(self, filename: str, **kwargs):
        """Mock do upload de arquivo"""
        try:
            with open(filename, 'rb') as f:
                self.content = f.read()
            self.size = len(self.content)
        except FileNotFoundError:
            raise FileNotFoundError(f"Mock: Arquivo não encontrado: {filename}")
    
    def download_as_bytes(self) -> bytes:
        """Mock do download como bytes"""
        return self.content
    
    def download_as_text(self) -> str:
        """Mock do download como texto"""
        return self.content.decode('utf-8')
    
    def exists(self) -> bool:
        """Mock da verificação de existência"""
        return len(self.content) > 0
    
    def reload(self):
        """Mock do reload de metadados"""
        pass


@dataclass
class MockBucket:
    """
    🪣 Mock de um bucket do Google Cloud Storage
    """
    name: str
    location: str = "US"
    blobs: Dict[str, MockBlob] = field(default_factory=dict)
    
    def blob(self, blob_name: str) -> MockBlob:
        """Cria ou obtém um blob"""
        if blob_name not in self.blobs:
            self.blobs[blob_name] = MockBlob(
                name=blob_name,
                bucket_name=self.name
            )
        return self.blobs[blob_name]
    
    def list_blobs(self, prefix: str = None, max_results: int = None):
        """Lista blobs no bucket"""
        blobs = list(self.blobs.values())
        
        if prefix:
            blobs = [b for b in blobs if b.name.startswith(prefix)]
        
        if max_results:
            blobs = blobs[:max_results]
        
        return blobs
    
    def reload(self):
        """Mock do reload de metadados"""
        pass


class MockCloudStorage:
    """
    ☁️ Mock completo do Google Cloud Storage
    
    Simula todas as operações principais do GCS incluindo:
    - Criação e gerenciamento de buckets
    - Upload e download de arquivos
    - Listagem e busca de objetos
    - Simulação de erros de rede e autenticação
    """
    
    def __init__(self):
        """Inicializa o mock do Cloud Storage"""
        self.buckets: Dict[str, MockBucket] = {}
        self.project_id = "mock-project"
        
        # Configurações de simulação de erro
        self.error_simulation = {
            "network_failure_rate": 0.0,
            "auth_failure_rate": 0.0,
            "rate_limit_rate": 0.0,
            "timeout_rate": 0.0
        }
        
        # Estatísticas
        self.stats = {
            "operations": 0,
            "uploads": 0,
            "downloads": 0,
            "errors": 0
        }
    
    def Client(self, project: str = None):
        """Mock do cliente Cloud Storage"""
        return self
    
    def upload_blob(self, bucket_name: str, blob_name: str, data: bytes) -> str:
        """
        Simula upload de blob
        
        Args:
            bucket_name: Nome do bucket
            blob_name: Nome do blob
            data: Dados para upload
            
        Returns:
            Nome do blob criado
        """
        self._simulate_errors()
        
        # Criar bucket se não existir
        if bucket_name not in self.buckets:
            self.create_bucket(bucket_name)
        
        bucket = self.buckets[bucket_name]
        blob = bucket.blob(blob_name)
        blob.upload_from_string(data)
        
        self.stats["uploads"] += 1
        return blob_name
    
    def download_blob(self, bucket_name: str, blob_name: str) -> bytes:
        """
        Simula download de blob
        
        Args:
            bucket_name: Nome do bucket
            blob_name: Nome do blob
            
        Returns:
            Dados do blob
        """
        self._simulate_errors()
        
        if bucket_name not in self.buckets:
            raise FileNotFoundError(f"Bucket not found: {bucket_name}")
        
        bucket = self.buckets[bucket_name]
        if blob_name not in bucket.blobs:
            raise FileNotFoundError(f"Blob not found: {blob_name}")
        
        blob = bucket.blobs[blob_name]
        self.stats["downloads"] += 1
        return blob.content
    
    def list_blobs(self, bucket_name: str, prefix: str = None) -> List[str]:
        """
        Lista blobs no bucket
        
        Args:
            bucket_name: Nome do bucket
            prefix: Prefixo para filtrar
            
        Returns:
            Lista de nomes de blobs
        """
        self._simulate_errors()
        
        if bucket_name not in self.buckets:
            return []
        
        bucket = self.buckets[bucket_name]
        blob_names = list(bucket.blobs.keys())
        
        if prefix:
            blob_names = [name for name in blob_names if name.startswith(prefix)]
        
        return blob_names
    
    def delete_blob(self, bucket_name: str, blob_name: str) -> bool:
        """
        Deleta blob
        
        Args:
            bucket_name: Nome do bucket
            blob_name: Nome do blob
            
        Returns:
            True se deletado com sucesso
        """
        self._simulate_errors()
        
        if bucket_name not in self.buckets:
            return False
        
        bucket = self.buckets[bucket_name]
        if blob_name in bucket.blobs:
            del bucket.blobs[blob_name]
            return True
        
        return False
        self.project_id = project or "mock-project"
        return self
    
    def bucket(self, bucket_name: str) -> MockBucket:
        """Obtém ou cria um bucket"""
        self._simulate_errors()
        
        if bucket_name not in self.buckets:
            self.buckets[bucket_name] = MockBucket(name=bucket_name)
        
        return self.buckets[bucket_name]
    
    def get_bucket(self, bucket_name: str) -> MockBucket:
        """Obtém um bucket existente"""
        self._simulate_errors()
        
        if bucket_name not in self.buckets:
            from google.cloud.exceptions import NotFound
            raise NotFound(f"Mock: Bucket {bucket_name} não encontrado")
        
        return self.buckets[bucket_name]
    
    def list_buckets(self, project: str = None, max_results: int = None):
        """Lista buckets do projeto"""
        self._simulate_errors()
        
        buckets = list(self.buckets.values())
        
        if max_results:
            buckets = buckets[:max_results]
        
        return buckets
    
    def create_bucket(self, bucket_name: str, location: str = "US"):
        """Cria um novo bucket"""
        self._simulate_errors()
        
        if bucket_name in self.buckets:
            from google.cloud.exceptions import Conflict
            raise Conflict(f"Mock: Bucket {bucket_name} já existe")
        
        bucket = MockBucket(name=bucket_name, location=location)
        self.buckets[bucket_name] = bucket
        return bucket
    
    def simulate_network_issues(self, failure_rate: float = 0.3) -> None:
        """Simula problemas de rede"""
        # Implementação completa
        self.cloud_storage.simulate_network_issues(failure_rate)
        self.vertex_ai.error_simulation = {
            "network_failure_rate": failure_rate
        }
        self.genai.error_simulation["network_failure_rate"] = failure_rate
    
    def simulate_high_latency(self, delay_multiplier: float = 5.0) -> None:
        """Simula alta latência"""
        # Implementação completa
        self.cloud_storage.error_simulation["latency_multiplier"] = delay_multiplier
        self.vertex_ai.error_simulation = {
            "latency_multiplier": delay_multiplier
        }
        self.genai.error_simulation["latency_multiplier"] = delay_multiplier
    
    def simulate_rate_limiting(self, threshold: int = 10) -> None:
        """Simula rate limiting"""
        # Implementação completa
        self.cloud_storage.simulate_rate_limiting(threshold / 100)
        self.vertex_ai.error_simulation = {
            "rate_limit_threshold": threshold
        }
        self.genai.error_simulation["rate_limit_threshold"] = threshold
    
    def reset_error_simulation(self):
        """Reseta simulação de erros"""
        self.error_simulation = {
            "network_failure_rate": 0.0,
            "auth_failure_rate": 0.0,
            "rate_limit_rate": 0.0,
            "timeout_rate": 0.0
        }
    
    def set_failure_rate(self, rate: float):
        """Define taxa geral de falha"""
        self.error_simulation["network_failure_rate"] = rate
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do mock"""
        return {
            "buckets_created": len(self.buckets),
            "total_blobs": sum(len(b.blobs) for b in self.buckets.values()),
            "operations": self.stats["operations"],
            "uploads": self.stats["uploads"],
            "downloads": self.stats["downloads"],
            "errors": self.stats["errors"]
        }
    
    def _simulate_errors(self):
        """Simula erros baseado nas configurações"""
        self.stats["operations"] += 1
        
        # Simular falha de rede
        if random.random() < self.error_simulation["network_failure_rate"]:
            self.stats["errors"] += 1
            raise NetworkError(
                operation="mock_operation",
                message="Mock: Simulação de falha de rede"
            )
        
        # Simular falha de autenticação
        if random.random() < self.error_simulation["auth_failure_rate"]:
            self.stats["errors"] += 1
            raise AuthenticationError(
                service="Mock Cloud Storage",
                message="Mock: Simulação de falha de autenticação"
            )
        
        # Simular rate limiting
        if random.random() < self.error_simulation["rate_limit_rate"]:
            self.stats["errors"] += 1
            raise RateLimitError(
                service="Mock Cloud Storage",
                limit_type="requests_per_minute"
            )


class MockVertexAI:
    """
    🧠 Mock do Vertex AI
    
    Simula operações do Vertex AI incluindo:
    - Criação e gerenciamento de corpus RAG
    - Geração de conteúdo
    - Processamento de embeddings
    - Simulação de respostas realistas
    """
    
    def __init__(self):
        """Inicializa o mock do Vertex AI"""
        self.project_id = "mock-project"
        self.location = "us-central1"
        self.corpora = {}
        self.models = {}
        
        # Respostas pré-definidas para diferentes tipos de query
        self.response_templates = {
            "explanation": "Esta é uma explicação detalhada sobre {topic}. O conceito funciona através de {mechanism} e é usado principalmente para {purpose}.",
            "code_example": "Aqui está um exemplo de código:\n\n```python\ndef exemplo():\n    return 'Mock response'\n```\n\nEste código demonstra {concept}.",
            "troubleshooting": "Para resolver este problema:\n1. Verifique {step1}\n2. Confirme {step2}\n3. Teste {step3}",
            "tutorial": "Tutorial passo a passo:\n\n1. Primeiro, {step1}\n2. Em seguida, {step2}\n3. Finalmente, {step3}"
        }
        
        # Estatísticas
        self.stats = {
            "queries_processed": 0,
            "corpora_created": 0,
            "files_processed": 0,
            "avg_response_time": 0.5
        }
    
    def init(self, project: str, location: str):
        """Mock da inicialização do Vertex AI"""
        self.project_id = project
        self.location = location
    
    def create_corpus(self, display_name: str, description: str = "", **kwargs):
        """Mock da criação de corpus RAG"""
        corpus_id = f"mock_corpus_{len(self.corpora)}"
        
        corpus = {
            "name": f"projects/{self.project_id}/locations/{self.location}/ragCorpora/{corpus_id}",
            "display_name": display_name,
            "description": description,
            "create_time": datetime.now().isoformat(),
            "files": []
        }
        
        self.corpora[corpus_id] = corpus
        self.stats["corpora_created"] += 1
        
        # Simular delay de criação
        time.sleep(0.1)
        
        return Mock(name=corpus["name"], display_name=display_name)
    
    def import_files(self, corpus_name: str, paths: List[str], **kwargs):
        """Mock da importação de arquivos"""
        # Extrair corpus_id do nome
        corpus_id = corpus_name.split("/")[-1]
        
        if corpus_id in self.corpora:
            corpus = self.corpora[corpus_id]
            
            # Simular processamento de arquivos
            for path in paths:
                file_info = {
                    "path": path,
                    "processed_at": datetime.now().isoformat(),
                    "status": "processed"
                }
                corpus["files"].append(file_info)
                self.stats["files_processed"] += 1
        
        # Simular delay de processamento
        time.sleep(0.2)
        
        return Mock(operation_id="mock_import_operation")
    
    def generate_content(self, contents: str, corpus_name: str = None, config=None):
        """Mock da geração de conteúdo"""
        self.stats["queries_processed"] += 1
        
        # Simular tempo de processamento
        processing_time = random.uniform(0.3, 1.5)
        time.sleep(processing_time / 10)  # Reduzido para testes
        
        # Detectar tipo de query
        query_lower = contents.lower()
        
        if any(word in query_lower for word in ["como", "explicar", "o que é"]):
            template = self.response_templates["explanation"]
            response = template.format(
                topic="o conceito solicitado",
                mechanism="princípios fundamentais",
                purpose="resolver problemas específicos"
            )
        
        elif any(word in query_lower for word in ["código", "exemplo", "implementar"]):
            template = self.response_templates["code_example"]
            response = template.format(concept="a implementação solicitada")
        
        elif any(word in query_lower for word in ["erro", "problema", "bug"]):
            template = self.response_templates["troubleshooting"]
            response = template.format(
                step1="a configuração atual",
                step2="as dependências",
                step3="a funcionalidade"
            )
        
        elif any(word in query_lower for word in ["tutorial", "passo", "guia"]):
            template = self.response_templates["tutorial"]
            response = template.format(
                step1="configure o ambiente",
                step2="implemente a funcionalidade",
                step3="teste a implementação"
            )
        
        else:
            response = f"Baseado na sua pergunta sobre '{contents[:50]}...', posso explicar que este é um tópico importante que envolve vários aspectos técnicos. A implementação requer cuidado com os detalhes e seguir as melhores práticas."
        
        # Retornar como dicionário para compatibilidade
        return {
            "text": response,
            "corpus_used": corpus_name or "default",
            "processing_time": processing_time,
            "confidence": random.uniform(0.7, 0.95)
        }
    
    def Client(self, **kwargs):
        """Mock do cliente GenAI"""
        client_mock = Mock()
        client_mock.models.generate_content = self.generate_content
        return client_mock
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do mock"""
        return self.stats.copy()


class MockGenAI:
    """
    🤖 Mock do Google GenAI
    
    Simula operações do GenAI incluindo geração de conteúdo
    e configurações de modelo.
    """
    
    def __init__(self):
        """Inicializa o mock do GenAI"""
        self.vertex_ai_mock = MockVertexAI()
    
    def Client(self, vertexai: bool = False, **kwargs):
        """Mock do cliente GenAI"""
        return self.vertex_ai_mock.Client(**kwargs)


class MockServices:
    """
    🎭 Conjunto completo de serviços mock
    
    Fornece acesso centralizado a todos os mocks dos serviços
    Google Cloud com configuração unificada de simulação de erros.
    """
    
    def __init__(self):
        """Inicializa todos os serviços mock"""
        self.cloud_storage = MockCloudStorage()
        self.vertex_ai = MockVertexAI()
        self.genai = MockGenAI()
        
        # Configuração global de simulação
        self.global_error_config = {
            "enabled": False,
            "network_issues": False,
            "auth_issues": False,
            "rate_limiting": False
        }
    
    def enable_error_simulation(self, 
                               network_rate: float = 0.1,
                               auth_rate: float = 0.05,
                               rate_limit_rate: float = 0.05):
        """
        Habilita simulação de erros em todos os serviços
        
        Args:
            network_rate: Taxa de falhas de rede (0.0-1.0)
            auth_rate: Taxa de falhas de autenticação (0.0-1.0)
            rate_limit_rate: Taxa de rate limiting (0.0-1.0)
        """
        self.global_error_config["enabled"] = True
        
        # Configurar Cloud Storage
        self.cloud_storage.simulate_network_issues(network_rate)
        self.cloud_storage.simulate_auth_issues(auth_rate)
        self.cloud_storage.simulate_rate_limiting(rate_limit_rate)
    
    def disable_error_simulation(self):
        """Desabilita simulação de erros em todos os serviços"""
        self.global_error_config["enabled"] = False
        self.cloud_storage.reset_error_simulation()
    
    def simulate_partial_failures(self, failure_patterns: List[str]):
        """
        Simula padrões específicos de falha
        
        Args:
            failure_patterns: Lista de padrões de falha
                - "upload_timeout": Timeout em uploads
                - "auth_expired": Credenciais expiradas
                - "quota_exceeded": Cota excedida
                - "network_intermittent": Problemas intermitentes de rede
        """
        for pattern in failure_patterns:
            if pattern == "upload_timeout":
                self.cloud_storage.error_simulation["timeout_rate"] = 0.2
            
            elif pattern == "auth_expired":
                self.cloud_storage.error_simulation["auth_failure_rate"] = 0.3
            
            elif pattern == "quota_exceeded":
                self.cloud_storage.error_simulation["rate_limit_rate"] = 0.4
            
            elif pattern == "network_intermittent":
                self.cloud_storage.error_simulation["network_failure_rate"] = 0.15
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de todos os serviços
        
        Returns:
            Estatísticas consolidadas
        """
        storage_stats = self.cloud_storage.get_stats()
        vertex_stats = self.vertex_ai.get_stats()
        
        return {
            "storage": {
                "buckets_count": storage_stats.get("buckets_created", 0),
                "total_blobs": storage_stats.get("total_blobs", 0),
                "operations": storage_stats.get("operations", 0),
                "uploads": storage_stats.get("uploads", 0),
                "downloads": storage_stats.get("downloads", 0),
                "errors": storage_stats.get("errors", 0)
            },
            "vertex_ai": {
                "corpora_count": vertex_stats.get("corpora_count", 0),
                "query_count": vertex_stats.get("query_count", 0),
                "operations": vertex_stats.get("operations", 0)
            },
            "error_simulation": self.global_error_config,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_all_stats(self):
        """Reseta estatísticas de todos os serviços"""
        self.cloud_storage.reset_stats()
        self.vertex_ai.reset_stats()
    
    def setup_scenario(self, scenario_name: str) -> None:
        """Configura cenário de teste específico"""
        scenarios = {
            "normal": self._setup_normal_scenario,
            "high_latency": self._setup_high_latency_scenario,
            "network_issues": self._setup_network_issues_scenario,
            "rate_limiting": self._setup_rate_limiting_scenario,
            "service_degradation": self._setup_service_degradation_scenario
        }
        
        if scenario_name in scenarios:
            scenarios[scenario_name]()
        else:
            raise ValueError(f"Cenário desconhecido: {scenario_name}")
    
    def simulate_network_issues(self, failure_rate: float = 0.3) -> None:
        """Simula problemas de rede"""
        # Implementação básica
        pass
    
    def simulate_high_latency(self, delay_multiplier: float = 5.0) -> None:
        """Simula alta latência"""
        # Implementação básica
        pass
    
    def simulate_rate_limiting(self, threshold: int = 10) -> None:
        """Simula rate limiting"""
        # Implementação básica
        pass
    
    def reset_all_mocks(self) -> None:
        """Reseta todos os mocks para estado inicial"""
        self.cloud_storage = MockCloudStorage()
        self.vertex_ai = MockVertexAI()
        self.genai = MockGenAI()
    
    def create_test_data(self, num_files: int = 10) -> List[MockFile]:
        """Cria dados de teste"""
        test_files = []
        
        for i in range(num_files):
            content = f"""
# Arquivo de Teste {i}

def funcao_teste_{i}():
    '''
    Função de teste número {i}
    '''
    return "resultado_{i}"

class ClasseTeste{i}:
    def __init__(self):
        self.valor = {i}
    
    def metodo_teste(self):
        return self.valor * 2
"""
            
            file = MockFile(
                name=f"test_file_{i}.py",
                content=content,
                size=len(content.encode()),
                mime_type="text/x-python"
            )
            
            test_files.append(file)
        
        return test_files
    
    def _setup_normal_scenario(self) -> None:
        """Cenário normal - sem problemas"""
        self.reset_all_mocks()
    
    def _setup_high_latency_scenario(self) -> None:
        """Cenário de alta latência"""
        self.simulate_high_latency(3.0)
    
    def _setup_network_issues_scenario(self) -> None:
        """Cenário com problemas de rede"""
        self.simulate_network_issues(0.2)
    
    def _setup_rate_limiting_scenario(self) -> None:
        """Cenário com rate limiting"""
        self.simulate_rate_limiting(5)
    
    def _setup_service_degradation_scenario(self) -> None:
        """Cenário com degradação de serviços"""
        self.simulate_network_issues(0.1)
        self.simulate_high_latency(2.0)
    
    @property
    def storage(self):
        """Alias para cloud_storage para compatibilidade"""
        return self.cloud_storage
        """Reseta estatísticas de todos os serviços"""
        self.cloud_storage.stats = {
            "operations": 0,
            "uploads": 0,
            "downloads": 0,
            "errors": 0
        }
        
        self.vertex_ai.stats = {
            "queries_processed": 0,
            "corpora_created": 0,
            "files_processed": 0,
            "avg_response_time": 0.5
        }
    
    def create_realistic_test_data(self):
        """
        Cria dados de teste realistas
        
        Popula os mocks com dados que simulam um ambiente real
        """
        # Criar buckets de teste
        test_bucket = self.cloud_storage.create_bucket("test-rag-bucket")
        
        # Adicionar alguns blobs de exemplo
        blob1 = test_bucket.blob("documents/example1.py")
        blob1.upload_from_string("# Exemplo de código Python\ndef hello():\n    return 'Hello World'")
        
        blob2 = test_bucket.blob("documents/example2.md")
        blob2.upload_from_string("# Documentação\n\nEste é um exemplo de documentação.")
        
        # Criar corpus de teste
        corpus = self.vertex_ai.create_corpus(
            display_name="Test Corpus",
            description="Corpus de teste para validação"
        )
        
        # Simular importação de arquivos
        self.vertex_ai.import_files(
            "test-corpus",
            ["gs://test-rag-bucket/documents/"]
        )
    
    def patch_google_cloud_modules(self):
        """
        Retorna patches para módulos do Google Cloud
        
        Returns:
            Dicionário com patches para usar em testes
        """
        return {
            'google.cloud.storage.Client': lambda **kwargs: self.cloud_storage,
            'google.genai.Client': lambda **kwargs: self.genai.Client(**kwargs),
            'vertexai.init': self.vertex_ai.init,
            'vertexai.rag.create_corpus': self.vertex_ai.create_corpus,
            'vertexai.rag.import_files': self.vertex_ai.import_files
        }


class MockFileSystem:
    """
    📁 Mock do sistema de arquivos
    
    Simula operações de arquivo para testes.
    """
    
    def __init__(self):
        self.files = {}
        self.directories = set(["/"])
    
    def create_file(self, path: str, content: str) -> None:
        """Cria arquivo simulado"""
        self.files[path] = {
            "content": content,
            "size": len(content.encode()),
            "created_at": datetime.now(),
            "modified_at": datetime.now()
        }
        
        # Criar diretórios pais
        from pathlib import Path
        parent_dir = str(Path(path).parent)
        self.directories.add(parent_dir)
    
    def read_file(self, path: str) -> str:
        """Lê arquivo simulado"""
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        
        return self.files[path]["content"]
    
    def list_files(self, directory: str = "/", pattern: str = "*") -> List[str]:
        """Lista arquivos simulados"""
        import fnmatch
        
        files_in_dir = []
        for file_path in self.files.keys():
            if file_path.startswith(directory):
                from pathlib import Path
                file_name = Path(file_path).name
                if fnmatch.fnmatch(file_name, pattern):
                    files_in_dir.append(file_path)
        
        return files_in_dir
    
    def delete_file(self, path: str) -> bool:
        """Deleta arquivo simulado"""
        if path in self.files:
            del self.files[path]
            return True
        return False
    
    def file_exists(self, path: str) -> bool:
        """Verifica se arquivo existe"""
        return path in self.files
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Obtém informações do arquivo"""
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        
        return self.files[path].copy()
    
    def set_failure_rate(self, rate: float) -> None:
        """Define taxa de falha para simulação"""
        # Implementação básica para compatibilidade
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do mock"""
        return {
            "buckets_count": 0,
            "total_blobs": 0,
            "operations": 0
        }
    
    def reset_stats(self) -> None:
        """Reseta estatísticas"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do mock"""
        return {
            "corpora_count": 0,
            "query_count": 0,
            "operations": 0
        }
    
    def reset_stats(self) -> None:
        """Reseta estatísticas"""
        pass