#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎲 Test Data Generators - Geradores de dados para testes

Este módulo fornece geradores de dados de teste realistas para
diferentes cenários de teste do sistema RAG.
"""

import random
import string
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from .mocks import MockFile


@dataclass
class TestFile:
    """
    📄 Arquivo de teste gerado
    """
    name: str
    content: str
    size: int
    file_type: str
    language: Optional[str] = None
    complexity: str = "medium"  # low, medium, high
    
    @property
    def extension(self) -> str:
        return Path(self.name).suffix
    
    @property
    def size_mb(self) -> float:
        return self.size / (1024 * 1024)


class TestDataGenerator:
    """
    🎲 Gerador de dados de teste
    
    Gera dados realistas para diferentes cenários de teste incluindo:
    - Arquivos de código em diferentes linguagens
    - Documentação técnica
    - Configurações
    - Dados de query e resposta
    - Cenários de erro
    """
    
    def __init__(self):
        """Inicializa o gerador de dados"""
        self.random = random.Random(42)  # Seed fixo para reprodutibilidade
        
        # Templates de código
        self.code_templates = {
            "python": self._get_python_templates(),
            "javascript": self._get_javascript_templates(),
            "java": self._get_java_templates(),
            "markdown": self._get_markdown_templates(),
            "json": self._get_json_templates()
        }
        
        # Vocabulário técnico
        self.tech_vocabulary = {
            "functions": ["process", "analyze", "validate", "transform", "execute", "handle", "manage", "create"],
            "classes": ["Manager", "Handler", "Processor", "Analyzer", "Validator", "Controller", "Service"],
            "variables": ["data", "result", "config", "params", "options", "settings", "context", "state"],
            "concepts": ["authentication", "authorization", "validation", "processing", "analysis", "optimization"]
        }
    
    def generate_test_files(self, count: int = 10, languages: Optional[List[str]] = None) -> List[TestFile]:
        """
        Gera arquivos de teste
        
        Args:
            count: Número de arquivos a gerar
            languages: Linguagens específicas (None para todas)
            
        Returns:
            Lista de arquivos de teste gerados
        """
        if languages is None:
            languages = list(self.code_templates.keys())
        
        files = []
        
        for i in range(count):
            language = self.random.choice(languages)
            complexity = self.random.choice(["low", "medium", "high"])
            
            file = self._generate_file_for_language(language, i, complexity)
            files.append(file)
        
        return files
    
    def generate_code_file(self, language: str, complexity: str = "medium", 
                          topic: Optional[str] = None) -> TestFile:
        """
        Gera arquivo de código específico
        
        Args:
            language: Linguagem de programação
            complexity: Nível de complexidade (low, medium, high)
            topic: Tópico específico (opcional)
            
        Returns:
            Arquivo de teste gerado
        """
        return self._generate_file_for_language(language, 0, complexity, topic)
    
    def generate_documentation_files(self, count: int = 5) -> List[TestFile]:
        """
        Gera arquivos de documentação
        
        Args:
            count: Número de arquivos de documentação
            
        Returns:
            Lista de arquivos de documentação
        """
        docs = []
        
        doc_types = [
            ("README.md", self._generate_readme_content),
            ("API.md", self._generate_api_doc_content),
            ("TUTORIAL.md", self._generate_tutorial_content),
            ("FAQ.md", self._generate_faq_content),
            ("CHANGELOG.md", self._generate_changelog_content)
        ]
        
        for i in range(min(count, len(doc_types))):
            doc_name, generator_func = doc_types[i]
            content = generator_func()
            
            doc = TestFile(
                name=doc_name,
                content=content,
                size=len(content.encode()),
                file_type="documentation",
                language="markdown",
                complexity="medium"
            )
            docs.append(doc)
        
        return docs
    
    def generate_config_files(self, count: int = 3) -> List[TestFile]:
        """
        Gera arquivos de configuração
        
        Args:
            count: Número de arquivos de configuração
            
        Returns:
            Lista de arquivos de configuração
        """
        configs = []
        
        config_types = [
            ("config.json", self._generate_json_config),
            ("settings.yaml", self._generate_yaml_config),
            (".env", self._generate_env_config)
        ]
        
        for i in range(min(count, len(config_types))):
            config_name, generator_func = config_types[i]
            content = generator_func()
            
            config = TestFile(
                name=config_name,
                content=content,
                size=len(content.encode()),
                file_type="configuration",
                complexity="low"
            )
            configs.append(config)
        
        return configs
    
    def generate_query_dataset(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        Gera dataset de queries para teste
        
        Args:
            count: Número de queries a gerar
            
        Returns:
            Lista de queries com metadados
        """
        queries = []
        
        query_patterns = [
            "Como implementar {concept} em {language}?",
            "O que é {concept} e como funciona?",
            "Qual a diferença entre {concept1} e {concept2}?",
            "Como resolver erro de {concept}?",
            "Exemplo prático de {concept}",
            "Melhores práticas para {concept}",
            "Como otimizar {concept}?",
            "Tutorial de {concept} para iniciantes"
        ]
        
        for i in range(count):
            pattern = self.random.choice(query_patterns)
            
            # Substituir placeholders
            query = pattern.format(
                concept=self.random.choice(self.tech_vocabulary["concepts"]),
                language=self.random.choice(list(self.code_templates.keys())),
                concept1=self.random.choice(self.tech_vocabulary["concepts"]),
                concept2=self.random.choice(self.tech_vocabulary["concepts"])
            )
            
            query_data = {
                "id": f"query_{i}",
                "text": query,
                "category": self._categorize_query(query),
                "complexity": self.random.choice(["low", "medium", "high"]),
                "expected_sources": self.random.randint(1, 5),
                "language": self.random.choice(list(self.code_templates.keys())),
                "created_at": datetime.now().isoformat()
            }
            
            queries.append(query_data)
        
        return queries
    
    def generate_error_scenarios(self) -> List[Dict[str, Any]]:
        """
        Gera cenários de erro para teste
        
        Returns:
            Lista de cenários de erro
        """
        scenarios = [
            {
                "name": "network_timeout",
                "description": "Timeout de rede durante upload",
                "error_type": "NetworkError",
                "trigger_condition": "upload_large_file",
                "expected_behavior": "retry_with_backoff"
            },
            {
                "name": "invalid_credentials",
                "description": "Credenciais inválidas para GCP",
                "error_type": "AuthenticationError",
                "trigger_condition": "api_call",
                "expected_behavior": "prompt_for_credentials"
            },
            {
                "name": "quota_exceeded",
                "description": "Quota da API excedida",
                "error_type": "QuotaError",
                "trigger_condition": "multiple_requests",
                "expected_behavior": "rate_limiting"
            },
            {
                "name": "file_not_found",
                "description": "Arquivo não encontrado",
                "error_type": "FileNotFoundError",
                "trigger_condition": "file_access",
                "expected_behavior": "error_message"
            },
            {
                "name": "invalid_format",
                "description": "Formato de arquivo inválido",
                "error_type": "ValidationError",
                "trigger_condition": "file_processing",
                "expected_behavior": "skip_with_warning"
            }
        ]
        
        return scenarios
    
    def generate_performance_data(self) -> Dict[str, Any]:
        """
        Gera dados para testes de performance
        
        Returns:
            Dados de performance simulados
        """
        return {
            "file_sizes": [
                {"size_mb": 0.1, "count": 50},
                {"size_mb": 1.0, "count": 20},
                {"size_mb": 5.0, "count": 10},
                {"size_mb": 10.0, "count": 5}
            ],
            "query_loads": [
                {"concurrent_users": 1, "queries_per_minute": 10},
                {"concurrent_users": 5, "queries_per_minute": 50},
                {"concurrent_users": 10, "queries_per_minute": 100},
                {"concurrent_users": 20, "queries_per_minute": 200}
            ],
            "expected_response_times": {
                "file_upload": {"p50": 2.0, "p95": 5.0, "p99": 10.0},
                "query_processing": {"p50": 1.0, "p95": 3.0, "p99": 8.0},
                "corpus_creation": {"p50": 30.0, "p95": 60.0, "p99": 120.0}
            }
        }
    
    def generate_config_profile(self, profile_name: str = "test") -> Dict[str, Any]:
        """
        Gera perfil de configuração para teste
        
        Args:
            profile_name: Nome do perfil
            
        Returns:
            Configuração de perfil
        """
        return {
            "name": profile_name,
            "description": f"Perfil de teste {profile_name}",
            "settings": {
                "project_id": f"test-project-{self.random.randint(1000, 9999)}",
                "location": self.random.choice(["us-central1", "us-east1", "europe-west1"]),
                "bucket_name": f"test-bucket-{profile_name}-{self.random.randint(100, 999)}",
                "corpus_name": f"test-corpus-{profile_name}",
                "max_file_size_mb": self.random.choice([10, 50, 100]),
                "supported_extensions": [".py", ".js", ".md", ".txt", ".json"],
                "batch_size": self.random.choice([10, 20, 50]),
                "retry_attempts": 3,
                "timeout_seconds": 30
            },
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def _generate_file_for_language(self, language: str, index: int, 
                                  complexity: str, topic: Optional[str] = None) -> TestFile:
        """Gera arquivo para linguagem específica"""
        if language not in self.code_templates:
            language = "python"  # Fallback
        
        templates = self.code_templates[language]
        template = self.random.choice(templates[complexity])
        
        # Substituir placeholders no template
        content = self._fill_template(template, language, topic)
        
        # Gerar nome do arquivo
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "java": ".java",
            "markdown": ".md",
            "json": ".json"
        }
        
        name = f"test_file_{index}_{language}_{complexity}{extensions.get(language, '.txt')}"
        
        return TestFile(
            name=name,
            content=content,
            size=len(content.encode()),
            file_type="code",
            language=language,
            complexity=complexity
        )
    
    def _fill_template(self, template: str, language: str, topic: Optional[str] = None) -> str:
        """Preenche template com dados gerados"""
        replacements = {
            "{function_name}": self.random.choice(self.tech_vocabulary["functions"]),
            "{class_name}": self.random.choice(self.tech_vocabulary["classes"]),
            "{variable_name}": self.random.choice(self.tech_vocabulary["variables"]),
            "{concept}": topic or self.random.choice(self.tech_vocabulary["concepts"]),
            "{number}": str(self.random.randint(1, 100)),
            "{string_value}": f"test_value_{self.random.randint(1, 1000)}",
            "{description}": self._generate_description()
        }
        
        content = template
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def _generate_description(self) -> str:
        """Gera descrição técnica"""
        templates = [
            "Implementa funcionalidade de {concept} com suporte a {feature}",
            "Gerencia {resource} de forma eficiente e segura",
            "Processa {data_type} utilizando algoritmo otimizado",
            "Valida {input} conforme especificações técnicas"
        ]
        
        template = self.random.choice(templates)
        return template.format(
            concept=self.random.choice(self.tech_vocabulary["concepts"]),
            feature=self.random.choice(["cache", "logging", "monitoring", "validation"]),
            resource=self.random.choice(["dados", "arquivos", "conexões", "recursos"]),
            data_type=self.random.choice(["JSON", "XML", "CSV", "binário"]),
            input=self.random.choice(["parâmetros", "configuração", "dados", "entrada"])
        )
    
    def _categorize_query(self, query: str) -> str:
        """Categoriza query baseada no conteúdo"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["como", "implementar", "fazer"]):
            return "how_to"
        elif any(word in query_lower for word in ["o que", "que é", "definição"]):
            return "definition"
        elif any(word in query_lower for word in ["diferença", "comparar", "vs"]):
            return "comparison"
        elif any(word in query_lower for word in ["erro", "problema", "bug"]):
            return "troubleshooting"
        elif any(word in query_lower for word in ["exemplo", "tutorial", "demo"]):
            return "example"
        else:
            return "general"
    
    def _get_python_templates(self) -> Dict[str, List[str]]:
        """Templates de código Python"""
        return {
            "low": [
                '''#!/usr/bin/env python3
"""
{description}
"""

def {function_name}(data):
    """
    Função simples para {concept}
    """
    result = data * {number}
    return result

if __name__ == "__main__":
    test_data = {number}
    output = {function_name}(test_data)
    print(f"Resultado: {output}")
''',
                '''class Simple{class_name}:
    """
    Classe simples para {concept}
    """
    
    def __init__(self, {variable_name}):
        self.{variable_name} = {variable_name}
    
    def get_{variable_name}(self):
        return self.{variable_name}
    
    def set_{variable_name}(self, value):
        self.{variable_name} = value
'''
            ],
            "medium": [
                '''#!/usr/bin/env python3
"""
{description}
"""

import json
import logging
from typing import Dict, List, Optional

class {class_name}:
    """
    Classe para {concept} com funcionalidades avançadas
    """
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.{variable_name} = []
    
    def {function_name}(self, data: List[Dict]) -> Optional[Dict]:
        """
        Processa dados de entrada
        """
        try:
            processed_data = []
            for item in data:
                if self._validate_item(item):
                    processed_item = self._transform_item(item)
                    processed_data.append(processed_item)
            
            return {
                "status": "success",
                "processed_count": len(processed_data),
                "data": processed_data
            }
        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            return None
    
    def _validate_item(self, item: Dict) -> bool:
        """Valida item individual"""
        required_fields = ["id", "name", "type"]
        return all(field in item for field in required_fields)
    
    def _transform_item(self, item: Dict) -> Dict:
        """Transforma item"""
        return {
            **item,
            "processed_at": "2024-01-01T00:00:00Z",
            "processor": "{class_name}"
        }
''',
                '''#!/usr/bin/env python3
"""
{description}
"""

import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class {class_name}Config:
    """Configuração para {class_name}"""
    base_url: str
    timeout: int = 30
    max_retries: int = 3

class Async{class_name}:
    """
    Cliente assíncrono para {concept}
    """
    
    def __init__(self, config: {class_name}Config):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def {function_name}(self, {variable_name}: str) -> Dict[str, Any]:
        """
        Executa operação assíncrona
        """
        url = f"{self.config.base_url}/{variable_name}"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise aiohttp.ClientError(f"Status: {response.status}")
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
'''
            ],
            "high": [
                '''#!/usr/bin/env python3
"""
{description}
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import json

T = TypeVar('T')

class ProcessingStatus(Enum):
    """Status de processamento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessingResult(Generic[T]):
    """Resultado de processamento tipado"""
    status: ProcessingStatus
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class {class_name}Protocol(Protocol):
    """Protocol para {concept}"""
    
    async def {function_name}(self, data: T) -> ProcessingResult[T]:
        """Processa dados"""
        ...

class Abstract{class_name}(ABC):
    """
    Classe abstrata para {concept} com padrões avançados
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._processors: List[{class_name}Protocol] = []
        self._metrics = {
            "processed_count": 0,
            "error_count": 0,
            "avg_processing_time": 0.0
        }
    
    @abstractmethod
    async def _process_item(self, item: T) -> ProcessingResult[T]:
        """Processa item individual - deve ser implementado"""
        pass
    
    async def {function_name}_batch(self, items: List[T], 
                                  batch_size: int = 10) -> List[ProcessingResult[T]]:
        """
        Processa lote de itens com controle de concorrência
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Processar batch em paralelo
            tasks = [self._process_item(item) for item in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Processar resultados
            for result in batch_results:
                if isinstance(result, Exception):
                    error_result = ProcessingResult(
                        status=ProcessingStatus.FAILED,
                        error=str(result)
                    )
                    results.append(error_result)
                    self._metrics["error_count"] += 1
                else:
                    results.append(result)
                    self._metrics["processed_count"] += 1
        
        return results
    
    @asynccontextmanager
    async def processing_context(self):
        """Context manager para processamento"""
        self.logger.info("Iniciando contexto de processamento")
        try:
            yield self
        except Exception as e:
            self.logger.error(f"Erro no contexto: {e}")
            raise
        finally:
            self.logger.info("Finalizando contexto de processamento")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de processamento"""
        return self._metrics.copy()

class Concrete{class_name}(Abstract{class_name}):
    """
    Implementação concreta de {class_name}
    """
    
    async def _process_item(self, item: T) -> ProcessingResult[T]:
        """Implementação específica do processamento"""
        try:
            # Simular processamento complexo
            await asyncio.sleep(0.1)
            
            # Validação
            if not self._validate_item(item):
                return ProcessingResult(
                    status=ProcessingStatus.FAILED,
                    error="Validação falhou"
                )
            
            # Transformação
            processed_item = await self._transform_item(item)
            
            return ProcessingResult(
                status=ProcessingStatus.COMPLETED,
                data=processed_item,
                metadata={"processor": self.__class__.__name__}
            )
            
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILED,
                error=str(e)
            )
    
    def _validate_item(self, item: T) -> bool:
        """Validação específica"""
        return item is not None
    
    async def _transform_item(self, item: T) -> T:
        """Transformação específica"""
        # Implementar transformação específica
        return item
'''
            ]
        }
    
    def _get_javascript_templates(self) -> Dict[str, List[str]]:
        """Templates de código JavaScript"""
        return {
            "low": [
                '''/**
 * {description}
 */

function {function_name}(data) {
    const result = data * {number};
    return result;
}

class Simple{class_name} {
    constructor({variable_name}) {
        this.{variable_name} = {variable_name};
    }
    
    get{class_name}() {
        return this.{variable_name};
    }
    
    set{class_name}(value) {
        this.{variable_name} = value;
    }
}

// Exemplo de uso
const instance = new Simple{class_name}("{string_value}");
console.log(instance.get{class_name}());
'''
            ],
            "medium": [
                '''/**
 * {description}
 */

class {class_name} {
    constructor(config) {
        this.config = config;
        this.{variable_name} = [];
        this.logger = console;
    }
    
    async {function_name}(data) {
        try {
            const processedData = [];
            
            for (const item of data) {
                if (this.validateItem(item)) {
                    const processedItem = await this.transformItem(item);
                    processedData.push(processedItem);
                }
            }
            
            return {
                status: 'success',
                processedCount: processedData.length,
                data: processedData
            };
        } catch (error) {
            this.logger.error('Erro no processamento:', error);
            return null;
        }
    }
    
    validateItem(item) {
        const requiredFields = ['id', 'name', 'type'];
        return requiredFields.every(field => field in item);
    }
    
    async transformItem(item) {
        return {
            ...item,
            processedAt: new Date().toISOString(),
            processor: '{class_name}'
        };
    }
}

module.exports = {class_name};
'''
            ],
            "high": [
                '''/**
 * {description}
 */

const EventEmitter = require('events');

class ProcessingStatus {
    static PENDING = 'pending';
    static PROCESSING = 'processing';
    static COMPLETED = 'completed';
    static FAILED = 'failed';
}

class ProcessingResult {
    constructor(status, data = null, error = null, metadata = {}) {
        this.status = status;
        this.data = data;
        this.error = error;
        this.metadata = metadata;
    }
}

class Abstract{class_name} extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.processors = [];
        this.metrics = {
            processedCount: 0,
            errorCount: 0,
            avgProcessingTime: 0.0
        };
    }
    
    async {function_name}Batch(items, batchSize = 10) {
        const results = [];
        
        for (let i = 0; i < items.length; i += batchSize) {
            const batch = items.slice(i, i + batchSize);
            
            const promises = batch.map(item => this.processItem(item));
            const batchResults = await Promise.allSettled(promises);
            
            for (const result of batchResults) {
                if (result.status === 'fulfilled') {
                    results.push(result.value);
                    this.metrics.processedCount++;
                } else {
                    const errorResult = new ProcessingResult(
                        ProcessingStatus.FAILED,
                        null,
                        result.reason.message
                    );
                    results.push(errorResult);
                    this.metrics.errorCount++;
                }
            }
            
            this.emit('batchProcessed', { batchIndex: Math.floor(i / batchSize), results: batchResults });
        }
        
        return results;
    }
    
    async processItem(item) {
        throw new Error('processItem must be implemented by subclass');
    }
    
    getMetrics() {
        return { ...this.metrics };
    }
}

class Concrete{class_name} extends Abstract{class_name} {
    async processItem(item) {
        try {
            // Simular processamento
            await new Promise(resolve => setTimeout(resolve, 100));
            
            if (!this.validateItem(item)) {
                return new ProcessingResult(
                    ProcessingStatus.FAILED,
                    null,
                    'Validação falhou'
                );
            }
            
            const processedItem = await this.transformItem(item);
            
            return new ProcessingResult(
                ProcessingStatus.COMPLETED,
                processedItem,
                null,
                { processor: this.constructor.name }
            );
            
        } catch (error) {
            return new ProcessingResult(
                ProcessingStatus.FAILED,
                null,
                error.message
            );
        }
    }
    
    validateItem(item) {
        return item !== null && item !== undefined;
    }
    
    async transformItem(item) {
        return {
            ...item,
            processedAt: new Date().toISOString(),
            processor: this.constructor.name
        };
    }
}

module.exports = { Abstract{class_name}, Concrete{class_name}, ProcessingStatus, ProcessingResult };
'''
            ]
        }
    
    def _get_java_templates(self) -> Dict[str, List[str]]:
        """Templates de código Java"""
        return {
            "low": [
                '''/**
 * {description}
 */
public class Simple{class_name} {
    private String {variable_name};
    
    public Simple{class_name}(String {variable_name}) {
        this.{variable_name} = {variable_name};
    }
    
    public String get{class_name}() {
        return {variable_name};
    }
    
    public void set{class_name}(String value) {
        this.{variable_name} = value;
    }
    
    public static int {function_name}(int data) {
        return data * {number};
    }
    
    public static void main(String[] args) {
        Simple{class_name} instance = new Simple{class_name}("{string_value}");
        System.out.println(instance.get{class_name}());
        System.out.println({function_name}({number}));
    }
}
'''
            ],
            "medium": [
                '''/**
 * {description}
 */
import java.util.*;
import java.util.logging.Logger;

public class {class_name} {
    private static final Logger logger = Logger.getLogger({class_name}.class.getName());
    private Map<String, Object> config;
    private List<Object> {variable_name};
    
    public {class_name}(Map<String, Object> config) {
        this.config = config;
        this.{variable_name} = new ArrayList<>();
    }
    
    public ProcessingResult {function_name}(List<Map<String, Object>> data) {
        try {
            List<Map<String, Object>> processedData = new ArrayList<>();
            
            for (Map<String, Object> item : data) {
                if (validateItem(item)) {
                    Map<String, Object> processedItem = transformItem(item);
                    processedData.add(processedItem);
                }
            }
            
            return new ProcessingResult("success", processedData.size(), processedData);
        } catch (Exception e) {
            logger.severe("Erro no processamento: " + e.getMessage());
            return null;
        }
    }
    
    private boolean validateItem(Map<String, Object> item) {
        String[] requiredFields = {"id", "name", "type"};
        for (String field : requiredFields) {
            if (!item.containsKey(field)) {
                return false;
            }
        }
        return true;
    }
    
    private Map<String, Object> transformItem(Map<String, Object> item) {
        Map<String, Object> transformed = new HashMap<>(item);
        transformed.put("processedAt", new Date().toString());
        transformed.put("processor", "{class_name}");
        return transformed;
    }
    
    public static class ProcessingResult {
        public String status;
        public int processedCount;
        public List<Map<String, Object>> data;
        
        public ProcessingResult(String status, int processedCount, List<Map<String, Object>> data) {
            this.status = status;
            this.processedCount = processedCount;
            this.data = data;
        }
    }
}
'''
            ],
            "high": [
                '''/**
 * {description}
 */
import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Logger;
import java.util.stream.Collectors;

public abstract class Abstract{class_name}<T> {
    private static final Logger logger = Logger.getLogger(Abstract{class_name}.class.getName());
    
    protected Map<String, Object> config;
    protected ExecutorService executorService;
    protected Map<String, Integer> metrics;
    
    public Abstract{class_name}(Map<String, Object> config) {
        this.config = config;
        this.executorService = Executors.newFixedThreadPool(
            (Integer) config.getOrDefault("threadPoolSize", 10)
        );
        this.metrics = new ConcurrentHashMap<>();
        initializeMetrics();
    }
    
    private void initializeMetrics() {
        metrics.put("processedCount", 0);
        metrics.put("errorCount", 0);
    }
    
    public CompletableFuture<List<ProcessingResult<T>>> {function_name}Batch(
            List<T> items, int batchSize) {
        
        List<CompletableFuture<ProcessingResult<T>>> futures = new ArrayList<>();
        
        for (int i = 0; i < items.size(); i += batchSize) {
            List<T> batch = items.subList(i, Math.min(i + batchSize, items.size()));
            
            for (T item : batch) {
                CompletableFuture<ProcessingResult<T>> future = 
                    CompletableFuture.supplyAsync(() -> processItem(item), executorService)
                    .handle((result, throwable) -> {
                        if (throwable != null) {
                            metrics.merge("errorCount", 1, Integer::sum);
                            return new ProcessingResult<>(
                                ProcessingStatus.FAILED, 
                                null, 
                                throwable.getMessage()
                            );
                        } else {
                            metrics.merge("processedCount", 1, Integer::sum);
                            return result;
                        }
                    });
                
                futures.add(future);
            }
        }
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList()));
    }
    
    protected abstract ProcessingResult<T> processItem(T item);
    
    public Map<String, Integer> getMetrics() {
        return new HashMap<>(metrics);
    }
    
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    public enum ProcessingStatus {
        PENDING, PROCESSING, COMPLETED, FAILED
    }
    
    public static class ProcessingResult<T> {
        public ProcessingStatus status;
        public T data;
        public String error;
        public Map<String, Object> metadata;
        
        public ProcessingResult(ProcessingStatus status, T data, String error) {
            this.status = status;
            this.data = data;
            this.error = error;
            this.metadata = new HashMap<>();
        }
    }
}
'''
            ]
        }
    
    def _get_markdown_templates(self) -> Dict[str, List[str]]:
        """Templates de documentação Markdown"""
        return {
            "low": [
                '''# {concept}

## Descrição

{description}

## Uso Básico

```python
def {function_name}():
    return "{string_value}"
```

## Exemplo

Este é um exemplo simples de como usar {concept}.
'''
            ],
            "medium": [
                '''# {concept} - Guia Completo

## Visão Geral

{description}

## Instalação

```bash
pip install {concept}-package
```

## Configuração

```python
config = {
    "{variable_name}": "{string_value}",
    "timeout": {number}
}
```

## API Reference

### Classe {class_name}

#### Métodos

- `{function_name}(data)`: Processa dados de entrada
- `validate()`: Valida configuração
- `get_status()`: Retorna status atual

## Exemplos

### Exemplo Básico

```python
from {concept} import {class_name}

processor = {class_name}(config)
result = processor.{function_name}(data)
```

### Exemplo Avançado

```python
with {class_name}(config) as processor:
    for item in data_stream:
        result = processor.{function_name}(item)
        if result.success:
            print(f"Processado: {result.data}")
```

## Troubleshooting

### Erro Comum 1

**Problema**: Timeout na conexão

**Solução**: Aumentar valor de timeout na configuração

### Erro Comum 2

**Problema**: Dados inválidos

**Solução**: Validar dados antes do processamento
'''
            ],
            "high": [
                '''# {concept} - Documentação Técnica Avançada

## Arquitetura

{description}

### Componentes Principais

1. **{class_name}**: Componente principal de processamento
2. **Validator**: Sistema de validação
3. **Monitor**: Sistema de monitoramento
4. **Cache**: Sistema de cache distribuído

## Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Redis (para cache)
- PostgreSQL (para persistência)

### Instalação

```bash
# Instalação básica
pip install {concept}-advanced

# Instalação com dependências opcionais
pip install {concept}-advanced[redis,postgres,monitoring]
```

### Configuração Avançada

```yaml
{concept}:
  core:
    {variable_name}: "{string_value}"
    max_workers: {number}
    timeout: 30
  
  cache:
    backend: "redis"
    url: "redis://localhost:6379/0"
    ttl: 3600
  
  monitoring:
    enabled: true
    metrics_port: 9090
    log_level: "INFO"
  
  database:
    url: "postgresql://user:pass@localhost/db"
    pool_size: 10
```

## API Reference

### Core Classes

#### {class_name}

```python
class {class_name}:
    def __init__(self, config: Config) -> None
    async def {function_name}(self, data: T) -> ProcessingResult[T]
    def get_metrics(self) -> Dict[str, Any]
    async def health_check(self) -> HealthStatus
```

**Parâmetros:**
- `config`: Configuração do processador
- `data`: Dados para processamento

**Retorna:**
- `ProcessingResult[T]`: Resultado tipado do processamento

#### ProcessingResult

```python
@dataclass
class ProcessingResult(Generic[T]):
    status: ProcessingStatus
    data: Optional[T]
    error: Optional[str]
    metadata: Dict[str, Any]
    processing_time: float
```

### Interfaces

#### ProcessorProtocol

```python
class ProcessorProtocol(Protocol):
    async def process(self, data: T) -> ProcessingResult[T]: ...
    def validate(self, data: T) -> bool: ...
```

## Padrões de Uso

### Processamento Assíncrono

```python
import asyncio
from {concept} import {class_name}, Config

async def main():
    config = Config.from_file("config.yaml")
    
    async with {class_name}(config) as processor:
        tasks = []
        
        for item in data_stream:
            task = processor.{function_name}(item)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result.status == ProcessingStatus.COMPLETED:
                await handle_success(result)
            else:
                await handle_error(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Processamento em Lote

```python
from {concept} import BatchProcessor

async def process_batch():
    processor = BatchProcessor(
        batch_size=100,
        max_concurrent=10,
        retry_policy=ExponentialBackoff()
    )
    
    async for batch_result in processor.process_stream(data_stream):
        success_count = sum(1 for r in batch_result if r.success)
        print(f"Batch processado: {success_count}/{len(batch_result)} sucessos")
```

### Monitoramento e Métricas

```python
from {concept}.monitoring import MetricsCollector, HealthChecker

# Configurar métricas
metrics = MetricsCollector()
health_checker = HealthChecker()

# Registrar métricas customizadas
@metrics.timer("custom_operation")
async def custom_operation():
    # Sua lógica aqui
    pass

# Health checks
@health_checker.register("database")
async def check_database():
    # Verificar conexão com banco
    return HealthStatus.HEALTHY
```

## Performance e Otimização

### Benchmarks

| Operação | Throughput | Latência P95 | Memória |
|----------|------------|--------------|---------|
| Processamento Simples | 10k ops/s | 5ms | 50MB |
| Processamento Complexo | 1k ops/s | 50ms | 200MB |
| Processamento em Lote | 50k ops/s | 100ms | 500MB |

### Tuning

```python
# Configuração otimizada para alta throughput
config = Config(
    max_workers=multiprocessing.cpu_count() * 2,
    batch_size=1000,
    prefetch_count=100,
    connection_pool_size=20,
    cache_size=10000
)
```

## Troubleshooting

### Problemas Comuns

#### 1. Alta Latência

**Sintomas:**
- Tempo de resposta > 1s
- Acúmulo de tarefas na fila

**Diagnóstico:**
```python
metrics = processor.get_metrics()
if metrics["avg_processing_time"] > 1.0:
    print("Alta latência detectada")
```

**Soluções:**
- Aumentar número de workers
- Otimizar queries de banco
- Implementar cache

#### 2. Memory Leaks

**Sintomas:**
- Uso crescente de memória
- OOM errors

**Diagnóstico:**
```python
import tracemalloc
tracemalloc.start()

# Seu código aqui

current, peak = tracemalloc.get_traced_memory()
print(f"Memória atual: {current / 1024 / 1024:.1f} MB")
```

**Soluções:**
- Implementar cleanup adequado
- Usar context managers
- Configurar garbage collection

## Extensibilidade

### Plugins Customizados

```python
from {concept}.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)
    
    async def before_process(self, data):
        # Lógica antes do processamento
        pass
    
    async def after_process(self, result):
        # Lógica após o processamento
        pass

# Registrar plugin
processor.register_plugin(CustomPlugin(config))
```

### Middlewares

```python
from {concept}.middleware import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(f"Processamento concluído em {duration:.2f}s")
            return response
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            raise
```

## Changelog

### v2.0.0 (2024-01-01)
- **Breaking**: Nova API assíncrona
- **Feature**: Suporte a processamento em lote
- **Feature**: Sistema de plugins
- **Improvement**: Performance 3x melhor

### v1.5.0 (2023-12-01)
- **Feature**: Sistema de cache distribuído
- **Feature**: Métricas avançadas
- **Fix**: Correção de memory leak

### v1.0.0 (2023-10-01)
- **Feature**: Release inicial
- **Feature**: Processamento básico
- **Feature**: Validação de dados
'''
            ]
        }
    
    def _get_json_templates(self) -> Dict[str, List[str]]:
        """Templates de arquivos JSON"""
        return {
            "low": [
                '''{
  "name": "{concept}",
  "version": "1.0.0",
  "description": "{description}",
  "config": {
    "{variable_name}": "{string_value}",
    "timeout": {number}
  }
}'''
            ],
            "medium": [
                '''{
  "name": "{concept}",
  "version": "2.0.0",
  "description": "{description}",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "jest",
    "build": "webpack --mode production"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21",
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "webpack": "^5.0.0"
  },
  "config": {
    "{variable_name}": "{string_value}",
    "port": {number},
    "database": {
      "host": "localhost",
      "port": 5432,
      "name": "test_db"
    },
    "features": {
      "caching": true,
      "logging": true,
      "monitoring": false
    }
  }
}'''
            ],
            "high": [
                '''{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "{concept} Configuration",
  "description": "{description}",
  "type": "object",
  "properties": {
    "application": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "default": "{concept}"
        },
        "version": {
          "type": "string",
          "pattern": "^\\\\d+\\\\.\\\\d+\\\\.\\\\d+$"
        },
        "environment": {
          "type": "string",
          "enum": ["development", "staging", "production"]
        }
      },
      "required": ["name", "version", "environment"]
    },
    "server": {
      "type": "object",
      "properties": {
        "host": {
          "type": "string",
          "format": "hostname"
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        },
        "ssl": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean"
            },
            "cert_path": {
              "type": "string"
            },
            "key_path": {
              "type": "string"
            }
          }
        }
      }
    },
    "database": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["postgresql", "mysql", "sqlite"]
        },
        "connection": {
          "type": "object",
          "properties": {
            "host": {
              "type": "string"
            },
            "port": {
              "type": "integer"
            },
            "database": {
              "type": "string"
            },
            "username": {
              "type": "string"
            },
            "password": {
              "type": "string"
            }
          },
          "required": ["host", "database", "username"]
        },
        "pool": {
          "type": "object",
          "properties": {
            "min": {
              "type": "integer",
              "minimum": 0
            },
            "max": {
              "type": "integer",
              "minimum": 1
            },
            "idle_timeout": {
              "type": "integer",
              "minimum": 1000
            }
          }
        }
      },
      "required": ["type", "connection"]
    },
    "cache": {
      "type": "object",
      "properties": {
        "backend": {
          "type": "string",
          "enum": ["redis", "memcached", "memory"]
        },
        "connection": {
          "type": "object",
          "properties": {
            "host": {
              "type": "string"
            },
            "port": {
              "type": "integer"
            },
            "database": {
              "type": "integer",
              "minimum": 0
            }
          }
        },
        "ttl": {
          "type": "integer",
          "minimum": 1
        }
      }
    },
    "logging": {
      "type": "object",
      "properties": {
        "level": {
          "type": "string",
          "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        },
        "format": {
          "type": "string"
        },
        "handlers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": {
                "type": "string",
                "enum": ["console", "file", "syslog"]
              },
              "level": {
                "type": "string",
                "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
              },
              "filename": {
                "type": "string"
              }
            },
            "required": ["type"]
          }
        }
      }
    },
    "monitoring": {
      "type": "object",
      "properties": {
        "enabled": {
          "type": "boolean"
        },
        "metrics": {
          "type": "object",
          "properties": {
            "port": {
              "type": "integer"
            },
            "path": {
              "type": "string"
            }
          }
        },
        "health_check": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean"
            },
            "path": {
              "type": "string"
            },
            "interval": {
              "type": "integer",
              "minimum": 1
            }
          }
        }
      }
    },
    "features": {
      "type": "object",
      "properties": {
        "authentication": {
          "type": "boolean"
        },
        "rate_limiting": {
          "type": "boolean"
        },
        "caching": {
          "type": "boolean"
        },
        "compression": {
          "type": "boolean"
        }
      }
    }
  },
  "required": ["application", "server"],
  "additionalProperties": false
}'''
            ]
        }
    
    def _generate_readme_content(self) -> str:
        """Gera conteúdo de README"""
        return f'''# {self.random.choice(self.tech_vocabulary["concepts"]).title()} System

## Descrição

{self._generate_description()}

## Instalação

```bash
pip install {self.random.choice(self.tech_vocabulary["concepts"])}-system
```

## Uso Básico

```python
from system import {self.random.choice(self.tech_vocabulary["classes"])}

# Criar instância
processor = {self.random.choice(self.tech_vocabulary["classes"])}()

# Processar dados
result = processor.{self.random.choice(self.tech_vocabulary["functions"])}(data)
```

## Funcionalidades

- ✅ Processamento eficiente
- ✅ Validação automática
- ✅ Monitoramento integrado
- ✅ Cache distribuído

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT License
'''
    
    def _generate_api_doc_content(self) -> str:
        """Gera documentação de API"""
        return f'''# API Documentation

## Endpoints

### POST /api/{self.random.choice(self.tech_vocabulary["functions"])}

Processa dados de entrada.

**Request:**
```json
{{
  "data": "string",
  "options": {{
    "validate": true,
    "timeout": {self.random.randint(10, 60)}
  }}
}}
```

**Response:**
```json
{{
  "status": "success",
  "result": "processed_data",
  "metadata": {{
    "processing_time": 0.5,
    "processor": "{self.random.choice(self.tech_vocabulary["classes"])}"
  }}
}}
```

### GET /api/status

Retorna status do sistema.

**Response:**
```json
{{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600
}}
```

## Códigos de Erro

- `400` - Bad Request
- `401` - Unauthorized
- `429` - Rate Limited
- `500` - Internal Server Error
'''
    
    def _generate_tutorial_content(self) -> str:
        """Gera conteúdo de tutorial"""
        return f'''# Tutorial: Getting Started

## Passo 1: Instalação

Instale o pacote usando pip:

```bash
pip install {self.random.choice(self.tech_vocabulary["concepts"])}-toolkit
```

## Passo 2: Configuração Básica

Crie um arquivo de configuração:

```python
config = {{
    "{self.random.choice(self.tech_vocabulary["variables"])}": "{self.random.choice(["development", "production"])}",
    "timeout": {self.random.randint(10, 60)},
    "max_retries": {self.random.randint(3, 10)}
}}
```

## Passo 3: Primeiro Exemplo

```python
from toolkit import {self.random.choice(self.tech_vocabulary["classes"])}

# Inicializar
processor = {self.random.choice(self.tech_vocabulary["classes"])}(config)

# Processar dados
data = "exemplo de dados"
result = processor.{self.random.choice(self.tech_vocabulary["functions"])}(data)

print(f"Resultado: {{result}}")
```

## Passo 4: Exemplo Avançado

```python
# Processamento em lote
batch_data = ["item1", "item2", "item3"]

for item in batch_data:
    try:
        result = processor.{self.random.choice(self.tech_vocabulary["functions"])}(item)
        print(f"Processado: {{result}}")
    except Exception as e:
        print(f"Erro: {{e}}")
```

## Próximos Passos

- Explore a documentação da API
- Veja exemplos avançados
- Configure monitoramento
'''
    
    def _generate_faq_content(self) -> str:
        """Gera conteúdo de FAQ"""
        return f'''# Frequently Asked Questions

## Q: Como configurar {self.random.choice(self.tech_vocabulary["concepts"])}?

A: Use o arquivo de configuração padrão e ajuste os parâmetros conforme necessário:

```python
config = {{
    "{self.random.choice(self.tech_vocabulary["variables"])}": "valor",
    "timeout": {self.random.randint(10, 60)}
}}
```

## Q: O que fazer quando ocorre erro de timeout?

A: Aumente o valor de timeout na configuração ou verifique a conectividade de rede.

## Q: Como otimizar performance?

A: Considere:
- Aumentar o número de workers
- Implementar cache
- Usar processamento em lote
- Otimizar queries

## Q: É possível usar em produção?

A: Sim, o sistema foi projetado para ambientes de produção com:
- Monitoramento integrado
- Tratamento de erros robusto
- Escalabilidade horizontal

## Q: Como contribuir com o projeto?

A: Veja o guia de contribuição no README.md
'''
    
    def _generate_changelog_content(self) -> str:
        """Gera conteúdo de changelog"""
        return f'''# Changelog

## [2.0.0] - 2024-01-01

### Added
- Nova funcionalidade de {self.random.choice(self.tech_vocabulary["concepts"])}
- Suporte a processamento assíncrono
- Sistema de cache distribuído

### Changed
- API refatorada para melhor usabilidade
- Performance melhorada em {self.random.randint(20, 50)}%

### Fixed
- Correção de memory leak
- Tratamento de erro aprimorado

## [1.5.0] - 2023-12-01

### Added
- Monitoramento de métricas
- Validação automática de dados

### Fixed
- Correção de bug na {self.random.choice(self.tech_vocabulary["functions"])}

## [1.0.0] - 2023-10-01

### Added
- Release inicial
- Funcionalidades básicas de processamento
- Documentação completa
'''
    
    def _generate_json_config(self) -> str:
        """Gera configuração JSON"""
        config = {
            "application": {
                "name": f"{self.random.choice(self.tech_vocabulary['concepts'])}_app",
                "version": "1.0.0",
                "environment": self.random.choice(["development", "staging", "production"])
            },
            "server": {
                "host": "localhost",
                "port": self.random.randint(3000, 9000),
                "timeout": self.random.randint(30, 120)
            },
            "database": {
                "type": self.random.choice(["postgresql", "mysql", "sqlite"]),
                "host": "localhost",
                "port": 5432,
                "name": f"test_{self.random.choice(self.tech_vocabulary['concepts'])}_db"
            },
            "features": {
                "caching": True,
                "logging": True,
                "monitoring": self.random.choice([True, False])
            }
        }
        
        return json.dumps(config, indent=2)
    
    def _generate_yaml_config(self) -> str:
        """Gera configuração YAML"""
        return f'''application:
  name: {self.random.choice(self.tech_vocabulary["concepts"])}_service
  version: "1.0.0"
  environment: {self.random.choice(["development", "production"])}

server:
  host: localhost
  port: {self.random.randint(3000, 9000)}
  workers: {self.random.randint(2, 8)}

database:
  type: postgresql
  connection:
    host: localhost
    port: 5432
    database: {self.random.choice(self.tech_vocabulary["concepts"])}_db
    username: user
    password: password

cache:
  backend: redis
  host: localhost
  port: 6379
  ttl: {self.random.randint(300, 3600)}

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
monitoring:
  enabled: true
  metrics_port: {self.random.randint(9000, 9999)}
'''
    
    def _generate_env_config(self) -> str:
        """Gera configuração .env"""
        return f'''# Environment Configuration
APP_NAME={self.random.choice(self.tech_vocabulary["concepts"])}_app
APP_VERSION=1.0.0
APP_ENV={self.random.choice(["development", "production"])}

# Server Configuration
SERVER_HOST=localhost
SERVER_PORT={self.random.randint(3000, 9000)}
SERVER_TIMEOUT={self.random.randint(30, 120)}

# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME={self.random.choice(self.tech_vocabulary["concepts"])}_db
DB_USER=user
DB_PASSWORD=password

# Cache Configuration
CACHE_BACKEND=redis
CACHE_HOST=localhost
CACHE_PORT=6379
CACHE_TTL={self.random.randint(300, 3600)}

# Feature Flags
ENABLE_CACHING=true
ENABLE_LOGGING=true
ENABLE_MONITORING={str(self.random.choice([True, False])).lower()}

# API Keys (example)
API_KEY=test_key_{self.random.randint(1000, 9999)}
SECRET_KEY=test_secret_{self.random.randint(1000, 9999)}
'''  
      
        return configs
    
    def generate_query_examples(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Gera exemplos de queries para teste
        
        Args:
            count: Número de queries a gerar
            
        Returns:
            Lista de queries de exemplo
        """
        query_templates = [
            "Como implementar {concept} em {language}?",
            "Qual a diferença entre {concept1} e {concept2}?",
            "Explique o padrão {pattern} com exemplo",
            "Como otimizar {operation} em {context}?",
            "Quais são as melhores práticas para {topic}?",
            "Como debugar problemas de {issue_type}?",
            "Exemplo de {feature} usando {technology}",
            "Tutorial de {skill} para iniciantes",
            "Comparação entre {tool1} e {tool2}",
            "Como configurar {service} no {environment}?"
        ]
        
        queries = []
        
        for i in range(count):
            template = self.random.choice(query_templates)
            
            # Substituir placeholders
            query = template.format(
                concept=self.random.choice(self.tech_vocabulary["concepts"]),
                concept1=self.random.choice(self.tech_vocabulary["concepts"]),
                concept2=self.random.choice(self.tech_vocabulary["concepts"]),
                language=self.random.choice(["Python", "JavaScript", "Java", "Go"]),
                pattern=self.random.choice(["Singleton", "Factory", "Observer", "Strategy"]),
                operation=self.random.choice(["busca", "ordenação", "cache", "indexação"]),
                context=self.random.choice(["produção", "desenvolvimento", "teste"]),
                topic=self.random.choice(["segurança", "performance", "escalabilidade"]),
                issue_type=self.random.choice(["memória", "performance", "concorrência"]),
                feature=self.random.choice(["API REST", "autenticação", "logging"]),
                technology=self.random.choice(["Flask", "Django", "FastAPI", "Express"]),
                skill=self.random.choice(["Docker", "Kubernetes", "CI/CD", "Git"]),
                tool1=self.random.choice(["Redis", "MongoDB", "PostgreSQL"]),
                tool2=self.random.choice(["MySQL", "Elasticsearch", "Cassandra"]),
                service=self.random.choice(["nginx", "apache", "docker", "kubernetes"]),
                environment=self.random.choice(["AWS", "GCP", "Azure", "local"])
            )
            
            query_data = {
                "id": f"query_{i+1}",
                "text": query,
                "complexity": self.random.choice(["low", "medium", "high"]),
                "category": self.random.choice(["how-to", "explanation", "comparison", "troubleshooting"]),
                "expected_response_length": self.random.choice(["short", "medium", "long"]),
                "tags": self.random.sample(
                    ["programming", "tutorial", "best-practices", "debugging", "configuration"],
                    k=self.random.randint(1, 3)
                )
            }
            
            queries.append(query_data)
        
        return queries
    
    def generate_error_scenarios(self) -> List[Dict[str, Any]]:
        """
        Gera cenários de erro para teste
        
        Returns:
            Lista de cenários de erro
        """
        error_scenarios = [
            {
                "name": "network_timeout",
                "description": "Timeout de rede durante upload",
                "error_type": "NetworkError",
                "trigger_condition": "upload_large_file",
                "expected_behavior": "retry_with_backoff",
                "recovery_action": "split_file_chunks"
            },
            {
                "name": "invalid_credentials",
                "description": "Credenciais inválidas para GCS",
                "error_type": "AuthenticationError",
                "trigger_condition": "expired_token",
                "expected_behavior": "refresh_token",
                "recovery_action": "re_authenticate"
            },
            {
                "name": "quota_exceeded",
                "description": "Quota de API excedida",
                "error_type": "QuotaError",
                "trigger_condition": "high_request_rate",
                "expected_behavior": "rate_limiting",
                "recovery_action": "exponential_backoff"
            },
            {
                "name": "file_not_found",
                "description": "Arquivo não encontrado no bucket",
                "error_type": "FileNotFoundError",
                "trigger_condition": "invalid_file_path",
                "expected_behavior": "graceful_error",
                "recovery_action": "suggest_alternatives"
            },
            {
                "name": "insufficient_permissions",
                "description": "Permissões insuficientes",
                "error_type": "PermissionError",
                "trigger_condition": "restricted_resource",
                "expected_behavior": "clear_error_message",
                "recovery_action": "request_permissions"
            }
        ]
        
        return error_scenarios
    
    def generate_performance_scenarios(self) -> List[Dict[str, Any]]:
        """
        Gera cenários de performance para teste
        
        Returns:
            Lista de cenários de performance
        """
        performance_scenarios = [
            {
                "name": "high_load",
                "description": "Alta carga de requisições simultâneas",
                "parameters": {
                    "concurrent_requests": 100,
                    "request_rate": "10/second",
                    "duration": "5 minutes"
                },
                "expected_metrics": {
                    "avg_response_time": "< 2s",
                    "success_rate": "> 95%",
                    "error_rate": "< 5%"
                }
            },
            {
                "name": "large_files",
                "description": "Upload de arquivos grandes",
                "parameters": {
                    "file_sizes": ["10MB", "50MB", "100MB"],
                    "concurrent_uploads": 5,
                    "timeout": "30 minutes"
                },
                "expected_metrics": {
                    "upload_speed": "> 1MB/s",
                    "success_rate": "> 90%",
                    "memory_usage": "< 500MB"
                }
            },
            {
                "name": "memory_stress",
                "description": "Teste de uso intensivo de memória",
                "parameters": {
                    "data_size": "1GB",
                    "processing_chunks": "10MB",
                    "iterations": 100
                },
                "expected_metrics": {
                    "max_memory": "< 2GB",
                    "memory_leaks": "none",
                    "gc_frequency": "acceptable"
                }
            }
        ]
        
        return performance_scenarios 
   
    def generate_config_profile(self, profile_type: str = "development") -> Dict[str, Any]:
        """
        Gera perfil de configuração para teste
        
        Args:
            profile_type: Tipo do perfil (development, staging, production)
            
        Returns:
            Configuração do perfil
        """
        base_config = {
            "profile_name": profile_type,
            "project_id": f"test-project-{profile_type}",
            "location": "us-central1",
            "bucket_name": f"test-bucket-{profile_type}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        if profile_type == "development":
            base_config.update({
                "debug": True,
                "log_level": "DEBUG",
                "cache_enabled": False,
                "rate_limit": 1000,
                "timeout": 30
            })
        elif profile_type == "staging":
            base_config.update({
                "debug": False,
                "log_level": "INFO",
                "cache_enabled": True,
                "rate_limit": 500,
                "timeout": 60
            })
        elif profile_type == "production":
            base_config.update({
                "debug": False,
                "log_level": "WARNING",
                "cache_enabled": True,
                "rate_limit": 100,
                "timeout": 120
            })
        
        return base_config
    
    def _generate_file_for_language(self, language: str, index: int, 
                                   complexity: str, topic: Optional[str] = None) -> TestFile:
        """Gera arquivo para linguagem específica"""
        templates = self.code_templates.get(language, self.code_templates["python"])
        
        if complexity == "low":
            template = self.random.choice(templates["simple"])
        elif complexity == "high":
            template = self.random.choice(templates["complex"])
        else:
            template = self.random.choice(templates["medium"])
        
        # Substituir placeholders no template
        content = self._fill_template(template, language, topic)
        
        # Gerar nome do arquivo
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "java": ".java",
            "markdown": ".md",
            "json": ".json"
        }
        
        extension = extensions.get(language, ".txt")
        name = f"test_file_{index+1}_{language}_{complexity}{extension}"
        
        return TestFile(
            name=name,
            content=content,
            size=len(content.encode()),
            file_type="code",
            language=language,
            complexity=complexity
        )    

    def _fill_template(self, template: str, language: str, topic: Optional[str] = None) -> str:
        """Preenche template com dados gerados"""
        # Gerar nomes aleatórios
        function_name = self.random.choice(self.tech_vocabulary["functions"])
        class_name = self.random.choice(self.tech_vocabulary["classes"])
        variable_name = self.random.choice(self.tech_vocabulary["variables"])
        
        # Gerar valores
        random_number = self.random.randint(1, 100)
        random_string = ''.join(self.random.choices(string.ascii_lowercase, k=8))
        
        # Substituir placeholders
        content = template.format(
            function_name=function_name,
            class_name=class_name,
            variable_name=variable_name,
            random_number=random_number,
            random_string=random_string,
            topic=topic or "exemplo"
        )
        
        return content
    
    def _get_python_templates(self) -> Dict[str, List[str]]:
        """Templates de código Python"""
        return {
            "simple": [
                '''def {function_name}({variable_name}):
    """
    Função simples para {topic}
    """
    return {variable_name} * {random_number}

# Exemplo de uso
result = {function_name}("test")
print(f"Resultado: {{result}}")
''',
                '''class {class_name}:
    """Classe simples para {topic}"""
    
    def __init__(self, {variable_name}):
        self.{variable_name} = {variable_name}
    
    def get_{variable_name}(self):
        return self.{variable_name}

# Exemplo
obj = {class_name}("{random_string}")
print(obj.get_{variable_name}())
'''
            ],
            "medium": [
                '''import json
from typing import Dict, List, Optional

class {class_name}:
    """
    Classe para {topic} com funcionalidades médias
    """
    
    def __init__(self, config: Dict[str, any]):
        self.config = config
        self.{variable_name} = []
    
    def {function_name}(self, data: List[str]) -> Dict[str, any]:
        """Processa dados de entrada"""
        results = {{}}
        
        for item in data:
            processed = self._process_item(item)
            results[item] = processed
        
        return results
    
    def _process_item(self, item: str) -> str:
        """Processa item individual"""
        return f"{{item}}_processed_{random_number}"
    
    def save_results(self, results: Dict[str, any], filename: str):
        """Salva resultados em arquivo"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

# Exemplo de uso
processor = {class_name}({{"debug": True}})
data = ["item1", "item2", "item3"]
results = processor.{function_name}(data)
processor.save_results(results, "output.json")
'''
            ],
            "complex": [
                '''import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from contextlib import asynccontextmanager

@dataclass
class {class_name}Config:
    """Configuração para {class_name}"""
    max_workers: int = {random_number}
    timeout: float = 30.0
    retry_attempts: int = 3
    debug: bool = False

class {class_name}Interface(ABC):
    """Interface abstrata para {topic}"""
    
    @abstractmethod
    async def {function_name}(self, data: Any) -> Any:
        """Método abstrato para processamento"""
        pass
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Valida dados de entrada"""
        pass

class {class_name}({class_name}Interface):
    """
    Implementação complexa para {topic}
    
    Características:
    - Processamento assíncrono
    - Pool de workers
    - Retry automático
    - Logging estruturado
    """
    
    def __init__(self, config: {class_name}Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.{variable_name}_cache = {{}}
    
    def _setup_logging(self):
        """Configura logging"""
        level = logging.DEBUG if self.config.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def {function_name}(self, data: Any) -> Any:
        """Processa dados com retry automático"""
        for attempt in range(self.config.retry_attempts):
            try:
                if not await self.validate(data):
                    raise ValueError("Dados inválidos")
                
                result = await self._process_with_timeout(data)
                self.logger.info(f"Processamento concluído: {{result}}")
                return result
                
            except Exception as e:
                self.logger.warning(f"Tentativa {{attempt + 1}} falhou: {{e}}")
                if attempt == self.config.retry_attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _process_with_timeout(self, data: Any) -> Any:
        """Processa com timeout"""
        try:
            return await asyncio.wait_for(
                self._do_processing(data),
                timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Processamento excedeu {{self.config.timeout}}s")
    
    async def _do_processing(self, data: Any) -> Any:
        """Lógica principal de processamento"""
        # Simular processamento assíncrono
        await asyncio.sleep(0.1)
        
        # Cache lookup
        cache_key = str(hash(str(data)))
        if cache_key in self.{variable_name}_cache:
            return self.{variable_name}_cache[cache_key]
        
        # Processamento real
        result = {{
            "input": data,
            "processed_at": asyncio.get_event_loop().time(),
            "worker_id": "{random_string}",
            "result": f"{{data}}_processed_{random_number}"
        }}
        
        # Cache result
        self.{variable_name}_cache[cache_key] = result
        return result
    
    async def validate(self, data: Any) -> bool:
        """Valida dados de entrada"""
        if data is None:
            return False
        
        if isinstance(data, str) and len(data) == 0:
            return False
        
        return True
    
    @asynccontextmanager
    async def batch_processor(self, batch_size: int = 10):
        """Context manager para processamento em lote"""
        batch = []
        try:
            yield batch
            if batch:
                tasks = [self.{function_name}(item) for item in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                self.logger.info(f"Lote processado: {{len(results)}} itens")
        except Exception as e:
            self.logger.error(f"Erro no processamento em lote: {{e}}")
            raise

# Exemplo de uso
async def main():
    config = {class_name}Config(max_workers=5, debug=True)
    processor = {class_name}(config)
    
    # Processamento individual
    result = await processor.{function_name}("test_data")
    print(f"Resultado: {{result}}")
    
    # Processamento em lote
    async with processor.batch_processor() as batch:
        batch.extend(["item1", "item2", "item3"])

if __name__ == "__main__":
    asyncio.run(main())
'''
            ]
        }
    
    def _get_javascript_templates(self) -> Dict[str, List[str]]:
        """Templates de código JavaScript"""
        return {
            "simple": [
                '''function {function_name}({variable_name}) {{
    // Função simples para {topic}
    return {variable_name} * {random_number};
}}

// Exemplo de uso
const result = {function_name}("test");
console.log(`Resultado: ${{result}}`);
''',
                '''class {class_name} {{
    constructor({variable_name}) {{
        this.{variable_name} = {variable_name};
    }}
    
    get{class_name}() {{
        return this.{variable_name};
    }}
}}

// Exemplo
const obj = new {class_name}("{random_string}");
console.log(obj.get{class_name}());
'''
            ],
            "medium": [
                '''const fs = require('fs').promises;

class {class_name} {{
    constructor(config) {{
        this.config = config;
        this.{variable_name} = [];
    }}
    
    async {function_name}(data) {{
        const results = {{}};
        
        for (const item of data) {{
            const processed = await this._processItem(item);
            results[item] = processed;
        }}
        
        return results;
    }}
    
    async _processItem(item) {{
        return `${{item}}_processed_{random_number}`;
    }}
    
    async saveResults(results, filename) {{
        await fs.writeFile(filename, JSON.stringify(results, null, 2));
    }}
}}

// Exemplo de uso
(async () => {{
    const processor = new {class_name}({{debug: true}});
    const data = ["item1", "item2", "item3"];
    const results = await processor.{function_name}(data);
    await processor.saveResults(results, "output.json");
}})();
'''
            ],
            "complex": [
                '''const EventEmitter = require('events');
const {{ Worker, isMainThread, parentPort, workerData }} = require('worker_threads');

class {class_name} extends EventEmitter {{
    constructor(config = {{}}) {{
        super();
        this.config = {{
            maxWorkers: {random_number},
            timeout: 30000,
            retryAttempts: 3,
            debug: false,
            ...config
        }};
        
        this.workers = [];
        this.{variable_name}Cache = new Map();
        this._setupWorkers();
    }}
    
    _setupWorkers() {{
        for (let i = 0; i < this.config.maxWorkers; i++) {{
            const worker = new Worker(__filename, {{
                workerData: {{ isWorker: true, workerId: i }}
            }});
            
            worker.on('message', (result) => {{
                this.emit('workerResult', result);
            }});
            
            worker.on('error', (error) => {{
                this.emit('workerError', error);
            }});
            
            this.workers.push(worker);
        }}
    }}
    
    async {function_name}(data) {{
        for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {{
            try {{
                if (!this.validate(data)) {{
                    throw new Error('Dados inválidos');
                }}
                
                const result = await this._processWithTimeout(data);
                
                if (this.config.debug) {{
                    console.log(`Processamento concluído: ${{JSON.stringify(result)}}`);
                }}
                
                return result;
                
            }} catch (error) {{
                console.warn(`Tentativa ${{attempt + 1}} falhou: ${{error.message}}`);
                
                if (attempt === this.config.retryAttempts - 1) {{
                    throw error;
                }}
                
                await this._sleep(Math.pow(2, attempt) * 1000);
            }}
        }}
    }}
    
    async _processWithTimeout(data) {{
        return new Promise((resolve, reject) => {{
            const timeout = setTimeout(() => {{
                reject(new Error(`Processamento excedeu ${{this.config.timeout}}ms`));
            }}, this.config.timeout);
            
            this._doProcessing(data)
                .then(result => {{
                    clearTimeout(timeout);
                    resolve(result);
                }})
                .catch(error => {{
                    clearTimeout(timeout);
                    reject(error);
                }});
        }});
    }}
    
    async _doProcessing(data) {{
        // Cache lookup
        const cacheKey = JSON.stringify(data);
        if (this.{variable_name}Cache.has(cacheKey)) {{
            return this.{variable_name}Cache.get(cacheKey);
        }}
        
        // Simular processamento assíncrono
        await this._sleep(100);
        
        const result = {{
            input: data,
            processedAt: Date.now(),
            workerId: "{random_string}",
            result: `${{data}}_processed_{random_number}`
        }};
        
        // Cache result
        this.{variable_name}Cache.set(cacheKey, result);
        return result;
    }}
    
    validate(data) {{
        return data !== null && data !== undefined && data !== '';
    }}
    
    async _sleep(ms) {{
        return new Promise(resolve => setTimeout(resolve, ms));
    }}
    
    async close() {{
        for (const worker of this.workers) {{
            await worker.terminate();
        }}
    }}
}}

// Worker thread code
if (!isMainThread && workerData?.isWorker) {{
    parentPort.on('message', async (data) => {{
        try {{
            // Simular processamento no worker
            const result = {{
                workerId: workerData.workerId,
                data: data,
                processedAt: Date.now()
            }};
            
            parentPort.postMessage(result);
        }} catch (error) {{
            parentPort.postMessage({{ error: error.message }});
        }}
    }});
}}

// Exemplo de uso (apenas no thread principal)
if (isMainThread) {{
    (async () => {{
        const processor = new {class_name}({{
            maxWorkers: 3,
            debug: true
        }});
        
        try {{
            const result = await processor.{function_name}("test_data");
            console.log('Resultado:', result);
        }} catch (error) {{
            console.error('Erro:', error.message);
        }} finally {{
            await processor.close();
        }}
    }})();
}}

module.exports = {class_name};
'''
            ]
        } 
   
    def _get_java_templates(self) -> Dict[str, List[str]]:
        """Templates de código Java"""
        return {
            "simple": [
                '''public class {class_name} {{
    private String {variable_name};
    
    public {class_name}(String {variable_name}) {{
        this.{variable_name} = {variable_name};
    }}
    
    public String {function_name}() {{
        return this.{variable_name} + "_{random_number}";
    }}
    
    public static void main(String[] args) {{
        {class_name} obj = new {class_name}("{random_string}");
        System.out.println(obj.{function_name}());
    }}
}}
'''
            ],
            "medium": [
                '''import java.util.*;
import java.io.*;

public class {class_name} {{
    private Map<String, Object> config;
    private List<String> {variable_name};
    
    public {class_name}(Map<String, Object> config) {{
        this.config = config;
        this.{variable_name} = new ArrayList<>();
    }}
    
    public Map<String, String> {function_name}(List<String> data) {{
        Map<String, String> results = new HashMap<>();
        
        for (String item : data) {{
            String processed = processItem(item);
            results.put(item, processed);
        }}
        
        return results;
    }}
    
    private String processItem(String item) {{
        return item + "_processed_{random_number}";
    }}
    
    public void saveResults(Map<String, String> results, String filename) throws IOException {{
        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {{
            for (Map.Entry<String, String> entry : results.entrySet()) {{
                writer.println(entry.getKey() + ": " + entry.getValue());
            }}
        }}
    }}
    
    public static void main(String[] args) {{
        try {{
            Map<String, Object> config = new HashMap<>();
            config.put("debug", true);
            
            {class_name} processor = new {class_name}(config);
            List<String> data = Arrays.asList("item1", "item2", "item3");
            Map<String, String> results = processor.{function_name}(data);
            processor.saveResults(results, "output.txt");
        }} catch (IOException e) {{
            e.printStackTrace();
        }}
    }}
}}
'''
            ],
            "complex": [
                '''import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.*;
import java.time.LocalDateTime;
import java.util.logging.Logger;
import java.util.logging.Level;

public class {class_name} {{
    private static final Logger LOGGER = Logger.getLogger({class_name}.class.getName());
    
    private final ExecutorService executorService;
    private final Map<String, Object> config;
    private final ConcurrentHashMap<String, Object> {variable_name}Cache;
    private final AtomicInteger processedCount;
    
    public {class_name}(Map<String, Object> config) {{
        this.config = config;
        this.{variable_name}Cache = new ConcurrentHashMap<>();
        this.processedCount = new AtomicInteger(0);
        
        int maxWorkers = (Integer) config.getOrDefault("maxWorkers", {random_number});
        this.executorService = Executors.newFixedThreadPool(maxWorkers);
        
        setupLogging();
    }}
    
    private void setupLogging() {{
        boolean debug = (Boolean) config.getOrDefault("debug", false);
        LOGGER.setLevel(debug ? Level.FINE : Level.INFO);
    }}
    
    public CompletableFuture<Map<String, Object>> {function_name}(Object data) {{
        return CompletableFuture.supplyAsync(() -> {{
            int retryAttempts = (Integer) config.getOrDefault("retryAttempts", 3);
            
            for (int attempt = 0; attempt < retryAttempts; attempt++) {{
                try {{
                    if (!validate(data)) {{
                        throw new IllegalArgumentException("Dados inválidos");
                    }}
                    
                    Map<String, Object> result = processWithTimeout(data);
                    LOGGER.info("Processamento concluído: " + result);
                    return result;
                    
                }} catch (Exception e) {{
                    LOGGER.warning("Tentativa " + (attempt + 1) + " falhou: " + e.getMessage());
                    
                    if (attempt == retryAttempts - 1) {{
                        throw new RuntimeException(e);
                    }}
                    
                    try {{
                        Thread.sleep((long) Math.pow(2, attempt) * 1000);
                    }} catch (InterruptedException ie) {{
                        Thread.currentThread().interrupt();
                        throw new RuntimeException(ie);
                    }}
                }}
            }}
            
            throw new RuntimeException("Todas as tentativas falharam");
        }}, executorService);
    }}
    
    private Map<String, Object> processWithTimeout(Object data) {{
        int timeout = (Integer) config.getOrDefault("timeout", 30);
        
        CompletableFuture<Map<String, Object>> future = CompletableFuture.supplyAsync(() -> {{
            return doProcessing(data);
        }}, executorService);
        
        try {{
            return future.get(timeout, TimeUnit.SECONDS);
        }} catch (TimeoutException e) {{
            future.cancel(true);
            throw new RuntimeException("Processamento excedeu " + timeout + "s");
        }} catch (InterruptedException | ExecutionException e) {{
            throw new RuntimeException(e);
        }}
    }}
    
    private Map<String, Object> doProcessing(Object data) {{
        // Cache lookup
        String cacheKey = String.valueOf(data.hashCode());
        if ({variable_name}Cache.containsKey(cacheKey)) {{
            return (Map<String, Object>) {variable_name}Cache.get(cacheKey);
        }}
        
        // Simular processamento
        try {{
            Thread.sleep(100);
        }} catch (InterruptedException e) {{
            Thread.currentThread().interrupt();
            throw new RuntimeException(e);
        }}
        
        Map<String, Object> result = new HashMap<>();
        result.put("input", data);
        result.put("processedAt", LocalDateTime.now());
        result.put("workerId", "{random_string}");
        result.put("result", data.toString() + "_processed_{random_number}");
        result.put("processedCount", processedCount.incrementAndGet());
        
        // Cache result
        {variable_name}Cache.put(cacheKey, result);
        return result;
    }}
    
    private boolean validate(Object data) {{
        return data != null && !data.toString().isEmpty();
    }}
    
    public CompletableFuture<List<Map<String, Object>>> processBatch(List<Object> dataList) {{
        List<CompletableFuture<Map<String, Object>>> futures = new ArrayList<>();
        
        for (Object data : dataList) {{
            futures.add({function_name}(data));
        }}
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .collect(java.util.stream.Collectors.toList()));
    }}
    
    public void shutdown() {{
        executorService.shutdown();
        try {{
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {{
                executorService.shutdownNow();
            }}
        }} catch (InterruptedException e) {{
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }}
    }}
    
    public static void main(String[] args) {{
        Map<String, Object> config = new HashMap<>();
        config.put("maxWorkers", 5);
        config.put("debug", true);
        config.put("timeout", 30);
        config.put("retryAttempts", 3);
        
        {class_name} processor = new {class_name}(config);
        
        try {{
            // Processamento individual
            CompletableFuture<Map<String, Object>> future = processor.{function_name}("test_data");
            Map<String, Object> result = future.get();
            System.out.println("Resultado: " + result);
            
            // Processamento em lote
            List<Object> batch = Arrays.asList("item1", "item2", "item3");
            CompletableFuture<List<Map<String, Object>>> batchFuture = processor.processBatch(batch);
            List<Map<String, Object>> batchResults = batchFuture.get();
            System.out.println("Resultados do lote: " + batchResults.size() + " itens");
            
        }} catch (InterruptedException | ExecutionException e) {{
            e.printStackTrace();
        }} finally {{
            processor.shutdown();
        }}
    }}
}}
'''
            ]
        }    

    def _get_markdown_templates(self) -> Dict[str, List[str]]:
        """Templates de documentação Markdown"""
        return {
            "simple": [
                '''# {class_name}

Documentação simples para {topic}.

## Descrição

Esta é uma documentação básica que explica como usar {function_name}.

## Exemplo

```python
result = {function_name}("{random_string}")
print(result)
```

## Parâmetros

- `{variable_name}`: Parâmetro de entrada (string)

## Retorno

Retorna o resultado processado.
''',
                '''# Guia de {topic}

## Introdução

Este guia explica os conceitos básicos de {topic}.

## Passos

1. Configurar o ambiente
2. Executar {function_name}
3. Verificar resultados

## Código de exemplo

```javascript
const {variable_name} = "{random_string}";
console.log({variable_name});
```
'''
            ],
            "medium": [
                '''# {class_name} - Documentação Completa

## Visão Geral

O {class_name} é uma ferramenta para {topic} que oferece funcionalidades avançadas.

## Instalação

```bash
pip install {random_string}-package
```

## Configuração

```json
{{
  "debug": true,
  "timeout": {random_number},
  "workers": 4
}}
```

## API Reference

### {function_name}(data)

Processa dados de entrada e retorna resultado.

**Parâmetros:**
- `data` (any): Dados para processamento

**Retorno:**
- `object`: Resultado processado

**Exemplo:**

```python
from {random_string} import {class_name}

processor = {class_name}()
result = processor.{function_name}("input_data")
print(result)
```

### Tratamento de Erros

```python
try:
    result = processor.{function_name}(data)
except ValidationError as e:
    print(f"Erro de validação: {{e}}")
except ProcessingError as e:
    print(f"Erro de processamento: {{e}}")
```

## Melhores Práticas

1. **Validação**: Sempre valide dados de entrada
2. **Logging**: Configure logs apropriados
3. **Timeout**: Defina timeouts adequados
4. **Cache**: Use cache para melhor performance

## Troubleshooting

### Problema: Timeout durante processamento

**Solução:** Aumente o valor de timeout na configuração.

### Problema: Erro de validação

**Solução:** Verifique o formato dos dados de entrada.
'''
            ],
            "complex": [
                '''# {class_name} - Documentação Técnica Avançada

## Arquitetura

O {class_name} implementa um padrão de processamento assíncrono com as seguintes características:

- **Pool de Workers**: Processamento paralelo com {random_number} workers
- **Cache Inteligente**: Sistema de cache com TTL configurável
- **Retry Automático**: Retry com exponential backoff
- **Monitoramento**: Métricas e logging estruturado

## Diagrama de Arquitetura

```mermaid
graph TD
    A[Input] --> B[Validator]
    B --> C[Load Balancer]
    C --> D[Worker Pool]
    D --> E[Cache Layer]
    E --> F[Output]
    
    G[Monitor] --> D
    G --> H[Metrics]
```

## Configuração Avançada

### Arquivo de Configuração

```yaml
{random_string}:
  workers:
    pool_size: {random_number}
    timeout: 30
    retry_attempts: 3
  
  cache:
    enabled: true
    ttl: 3600
    max_size: 1000
  
  monitoring:
    metrics_enabled: true
    log_level: INFO
    
  performance:
    batch_size: 100
    queue_size: 1000
```

### Configuração Programática

```python
from {random_string}.config import {class_name}Config
from {random_string}.monitoring import MetricsCollector

config = {class_name}Config(
    workers={{
        'pool_size': {random_number},
        'timeout': 30
    }},
    cache={{
        'enabled': True,
        'ttl': 3600
    }}
)

metrics = MetricsCollector()
processor = {class_name}(config, metrics_collector=metrics)
```

## API Detalhada

### Classe Principal: {class_name}

#### Construtor

```python
{class_name}(config: {class_name}Config, metrics_collector: Optional[MetricsCollector] = None)
```

**Parâmetros:**
- `config`: Configuração do processador
- `metrics_collector`: Coletor de métricas (opcional)

#### Métodos Principais

##### {function_name}(data, options=None)

Processa dados com configurações avançadas.

```python
async def {function_name}(
    self, 
    data: Union[str, Dict, List], 
    options: Optional[ProcessingOptions] = None
) -> ProcessingResult
```

**Parâmetros:**
- `data`: Dados para processamento (string, dict ou lista)
- `options`: Opções de processamento

**Retorno:**
- `ProcessingResult`: Objeto com resultado e metadados

**Exemplo Avançado:**

```python
import asyncio
from {random_string} import {class_name}, ProcessingOptions

async def main():
    processor = {class_name}(config)
    
    options = ProcessingOptions(
        timeout=60,
        retry_attempts=5,
        cache_key="custom_key",
        priority="high"
    )
    
    result = await processor.{function_name}(
        data={{"input": "complex_data"}},
        options=options
    )
    
    print(f"Status: {{result.status}}")
    print(f"Tempo: {{result.execution_time}}ms")
    print(f"Cache Hit: {{result.cache_hit}}")

asyncio.run(main())
```

##### batch_process(data_list, batch_size=None)

Processamento em lote otimizado.

```python
async def batch_process(
    self,
    data_list: List[Any],
    batch_size: Optional[int] = None
) -> List[ProcessingResult]
```

##### get_metrics()

Retorna métricas de performance.

```python
def get_metrics(self) -> Dict[str, Any]:
    return {{
        "total_processed": self.stats.total_processed,
        "avg_processing_time": self.stats.avg_time,
        "cache_hit_rate": self.stats.cache_hit_rate,
        "error_rate": self.stats.error_rate
    }}
```

## Monitoramento e Observabilidade

### Métricas Disponíveis

| Métrica | Descrição | Tipo |
|---------|-----------|------|
| `processing_time` | Tempo de processamento | Histogram |
| `cache_hits` | Cache hits | Counter |
| `errors_total` | Total de erros | Counter |
| `queue_size` | Tamanho da fila | Gauge |

### Logging Estruturado

```python
import logging
import json

# Configurar logging estruturado
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

# Logs são emitidos em formato JSON
{{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "component": "{class_name}",
  "event": "processing_completed",
  "data": {{
    "input_size": 1024,
    "processing_time": 150,
    "cache_hit": false
  }}
}}
```

## Performance e Otimização

### Benchmarks

| Cenário | Throughput | Latência P95 | Memória |
|---------|------------|--------------|---------|
| Carga Normal | 1000 req/s | 50ms | 256MB |
| Alta Carga | 5000 req/s | 200ms | 512MB |
| Batch Processing | 10000 items/s | 100ms | 1GB |

### Tuning de Performance

```python
# Configuração otimizada para alta performance
config = {class_name}Config(
    workers={{
        'pool_size': 20,  # Ajustar baseado em CPU cores
        'timeout': 10,    # Timeout agressivo
        'queue_size': 5000
    }},
    cache={{
        'enabled': True,
        'ttl': 300,       # TTL menor para dados dinâmicos
        'max_size': 10000
    }},
    batch={{
        'size': 500,      # Batch size otimizado
        'flush_interval': 1.0
    }}
)
```

## Troubleshooting Avançado

### Problemas Comuns

#### 1. Alta Latência

**Sintomas:**
- Tempo de resposta > 1s
- Queue size crescendo

**Diagnóstico:**
```python
metrics = processor.get_metrics()
if metrics['avg_processing_time'] > 1000:
    print("Alta latência detectada")
    print(f"Queue size: {{metrics['queue_size']}}")
```

**Soluções:**
- Aumentar pool de workers
- Otimizar cache
- Implementar circuit breaker

#### 2. Memory Leaks

**Sintomas:**
- Uso de memória crescente
- GC frequente

**Diagnóstico:**
```python
import psutil
import gc

def check_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > 1000:  # > 1GB
        print(f"Alto uso de memória: {{memory_mb:.1f}}MB")
        print(f"Objetos no GC: {{len(gc.get_objects())}}")
```

**Soluções:**
- Configurar TTL do cache
- Implementar cleanup periódico
- Usar weak references

## Extensibilidade

### Custom Processors

```python
from {random_string}.base import BaseProcessor

class Custom{class_name}(BaseProcessor):
    async def process_item(self, item):
        # Lógica customizada
        return await super().process_item(item)
    
    def validate_input(self, data):
        # Validação customizada
        return custom_validation(data)
```

### Plugins

```python
from {random_string}.plugins import PluginInterface

class MetricsPlugin(PluginInterface):
    def on_processing_start(self, data):
        self.start_time = time.time()
    
    def on_processing_complete(self, result):
        duration = time.time() - self.start_time
        self.emit_metric('processing_duration', duration)

# Registrar plugin
processor.register_plugin(MetricsPlugin())
```

## Changelog

### v2.0.0 (2024-01-01)
- **BREAKING**: Nova API assíncrona
- **NEW**: Sistema de plugins
- **NEW**: Métricas avançadas
- **IMPROVED**: Performance 3x melhor

### v1.5.0 (2023-12-01)
- **NEW**: Processamento em lote
- **NEW**: Cache inteligente
- **FIXED**: Memory leaks

## Licença

MIT License - veja LICENSE.md para detalhes.
'''
            ]
        }    

    def _get_json_templates(self) -> Dict[str, List[str]]:
        """Templates de arquivos JSON"""
        return {
            "simple": [
                '''{{
  "name": "{class_name}",
  "version": "1.0.0",
  "description": "Configuração simples para {topic}",
  "settings": {{
    "{variable_name}": "{random_string}",
    "enabled": true,
    "count": {random_number}
  }}
}}''',
                '''{{
  "config": {{
    "debug": true,
    "timeout": {random_number},
    "workers": 4
  }},
  "features": [
    "{function_name}",
    "validation",
    "logging"
  ]
}}'''
            ],
            "medium": [
                '''{{
  "application": {{
    "name": "{class_name}",
    "version": "2.1.0",
    "environment": "development"
  }},
  "database": {{
    "host": "localhost",
    "port": 5432,
    "name": "{random_string}_db",
    "pool_size": {random_number}
  }},
  "cache": {{
    "enabled": true,
    "ttl": 3600,
    "max_size": 1000
  }},
  "logging": {{
    "level": "INFO",
    "format": "json",
    "handlers": ["console", "file"]
  }},
  "features": {{
    "{function_name}": {{
      "enabled": true,
      "timeout": 30,
      "retry_attempts": 3
    }},
    "monitoring": {{
      "metrics": true,
      "health_check": true,
      "alerts": {{
        "email": "admin@example.com",
        "slack": "#alerts"
      }}
    }}
  }}
}}'''
            ],
            "complex": [
                '''{{
  "metadata": {{
    "schema_version": "3.0",
    "generated_at": "2024-01-01T12:00:00Z",
    "generator": "{class_name}",
    "checksum": "sha256:{random_string}"
  }},
  "application": {{
    "name": "{class_name}",
    "version": "3.2.1",
    "build": "{random_number}",
    "environment": "production",
    "region": "us-central1"
  }},
  "infrastructure": {{
    "compute": {{
      "instances": {{
        "web": {{
          "count": 3,
          "type": "n1-standard-2",
          "auto_scaling": {{
            "min": 2,
            "max": 10,
            "target_cpu": 70
          }}
        }},
        "worker": {{
          "count": 5,
          "type": "n1-standard-4",
          "queue_size": 1000
        }}
      }}
    }},
    "storage": {{
      "database": {{
        "type": "postgresql",
        "version": "13.0",
        "instance_class": "db.r5.xlarge",
        "storage": {{
          "size": "100GB",
          "type": "gp2",
          "encrypted": true
        }},
        "backup": {{
          "retention": 30,
          "window": "03:00-04:00"
        }}
      }},
      "cache": {{
        "type": "redis",
        "version": "6.2",
        "node_type": "cache.r6g.large",
        "num_nodes": 3,
        "ttl_default": 3600
      }},
      "object_storage": {{
        "bucket": "{random_string}-data",
        "lifecycle": {{
          "transition_ia": 30,
          "transition_glacier": 90,
          "expiration": 2555
        }}
      }}
    }},
    "networking": {{
      "vpc": {{
        "cidr": "10.0.0.0/16",
        "subnets": [
          {{
            "name": "public",
            "cidr": "10.0.1.0/24",
            "availability_zone": "us-central1-a"
          }},
          {{
            "name": "private",
            "cidr": "10.0.2.0/24",
            "availability_zone": "us-central1-b"
          }}
        ]
      }},
      "load_balancer": {{
        "type": "application",
        "scheme": "internet-facing",
        "health_check": {{
          "path": "/health",
          "interval": 30,
          "timeout": 5,
          "healthy_threshold": 2
        }}
      }}
    }}
  }},
  "services": {{
    "{function_name}_service": {{
      "image": "gcr.io/project/{random_string}:latest",
      "port": 8080,
      "replicas": 3,
      "resources": {{
        "requests": {{
          "cpu": "500m",
          "memory": "512Mi"
        }},
        "limits": {{
          "cpu": "1000m",
          "memory": "1Gi"
        }}
      }},
      "environment": {{
        "LOG_LEVEL": "INFO",
        "DATABASE_URL": "${{DATABASE_URL}}",
        "REDIS_URL": "${{REDIS_URL}}",
        "API_KEY": "${{API_KEY}}"
      }},
      "health_check": {{
        "http_get": {{
          "path": "/health",
          "port": 8080
        }},
        "initial_delay": 30,
        "period": 10
      }}
    }},
    "worker_service": {{
      "image": "gcr.io/project/{random_string}-worker:latest",
      "replicas": 2,
      "resources": {{
        "requests": {{
          "cpu": "1000m",
          "memory": "1Gi"
        }},
        "limits": {{
          "cpu": "2000m",
          "memory": "2Gi"
        }}
      }},
      "queue": {{
        "name": "{variable_name}_queue",
        "max_size": 10000,
        "visibility_timeout": 300
      }}
    }}
  }},
  "monitoring": {{
    "metrics": {{
      "enabled": true,
      "retention": "30d",
      "custom_metrics": [
        {{
          "name": "processing_time",
          "type": "histogram",
          "labels": ["service", "method"]
        }},
        {{
          "name": "queue_size",
          "type": "gauge",
          "labels": ["queue_name"]
        }}
      ]
    }},
    "logging": {{
      "level": "INFO",
      "format": "json",
      "retention": "7d",
      "aggregation": {{
        "enabled": true,
        "index_pattern": "app-logs-*"
      }}
    }},
    "alerting": {{
      "rules": [
        {{
          "name": "high_error_rate",
          "condition": "error_rate > 0.05",
          "duration": "5m",
          "severity": "critical",
          "notifications": ["email", "slack"]
        }},
        {{
          "name": "high_latency",
          "condition": "p95_latency > 1000",
          "duration": "10m",
          "severity": "warning",
          "notifications": ["slack"]
        }}
      ]
    }}
  }},
  "security": {{
    "authentication": {{
      "type": "oauth2",
      "provider": "google",
      "scopes": ["openid", "email", "profile"]
    }},
    "authorization": {{
      "rbac": {{
        "enabled": true,
        "roles": [
          {{
            "name": "admin",
            "permissions": ["*"]
          }},
          {{
            "name": "user",
            "permissions": ["read", "write"]
          }},
          {{
            "name": "readonly",
            "permissions": ["read"]
          }}
        ]
      }}
    }},
    "encryption": {{
      "at_rest": {{
        "enabled": true,
        "algorithm": "AES-256"
      }},
      "in_transit": {{
        "enabled": true,
        "tls_version": "1.3"
      }}
    }}
  }},
  "compliance": {{
    "gdpr": {{
      "enabled": true,
      "data_retention": "2y",
      "anonymization": true
    }},
    "audit": {{
      "enabled": true,
      "retention": "7y",
      "events": ["login", "data_access", "configuration_change"]
    }}
  }},
  "deployment": {{
    "strategy": "rolling",
    "max_unavailable": "25%",
    "max_surge": "25%",
    "rollback": {{
      "enabled": true,
      "revision_history_limit": 10
    }},
    "canary": {{
      "enabled": true,
      "steps": [10, 25, 50, 100],
      "analysis": {{
        "success_rate": 0.95,
        "latency_p95": 1000
      }}
    }}
  }}
}}'''
            ]
        }
    
    def _generate_readme_content(self) -> str:
        """Gera conteúdo de README"""
        return f'''# {self.random.choice(self.tech_vocabulary["classes"])}

Sistema avançado para processamento e análise de dados.

## Características

- ⚡ Processamento assíncrono
- 🔄 Retry automático
- 📊 Métricas integradas
- 🛡️ Tratamento robusto de erros

## Instalação

```bash
pip install {self.random.choice(self.tech_vocabulary["variables"])}-package
```

## Uso Básico

```python
from package import {self.random.choice(self.tech_vocabulary["classes"])}

processor = {self.random.choice(self.tech_vocabulary["classes"])}()
result = processor.{self.random.choice(self.tech_vocabulary["functions"])}("data")
```

## Licença

MIT
'''
    
    def _generate_api_doc_content(self) -> str:
        """Gera documentação de API"""
        return f'''# API Documentation

## Endpoints

### POST /api/{self.random.choice(self.tech_vocabulary["functions"])}

Processa dados de entrada.

**Request:**
```json
{{
  "data": "input_data",
  "options": {{
    "timeout": {self.random.randint(10, 60)}
  }}
}}
```

**Response:**
```json
{{
  "status": "success",
  "result": "processed_data",
  "execution_time": {self.random.randint(100, 1000)}
}}
```

### GET /api/status

Retorna status do sistema.

**Response:**
```json
{{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": {self.random.randint(1000, 10000)}
}}
```
'''
    
    def _generate_tutorial_content(self) -> str:
        """Gera conteúdo de tutorial"""
        return f'''# Tutorial: Como usar {self.random.choice(self.tech_vocabulary["classes"])}

## Passo 1: Configuração

Primeiro, configure o ambiente:

```bash
export API_KEY="your_api_key"
export DEBUG=true
```

## Passo 2: Inicialização

```python
from package import {self.random.choice(self.tech_vocabulary["classes"])}

config = {{
    "timeout": {self.random.randint(30, 120)},
    "workers": {self.random.randint(2, 8)}
}}

processor = {self.random.choice(self.tech_vocabulary["classes"])}(config)
```

## Passo 3: Processamento

```python
data = "exemplo de dados"
result = processor.{self.random.choice(self.tech_vocabulary["functions"])}(data)
print(f"Resultado: {{result}}")
```

## Dicas

- Use cache para melhor performance
- Configure timeouts adequados
- Monitore métricas regularmente
'''
    
    def _generate_faq_content(self) -> str:
        """Gera conteúdo de FAQ"""
        return f'''# FAQ - Perguntas Frequentes

## Como configurar timeout?

Configure o timeout na inicialização:

```python
config = {{"timeout": {self.random.randint(30, 120)}}}
processor = {self.random.choice(self.tech_vocabulary["classes"])}(config)
```

## Como tratar erros?

Use try/catch:

```python
try:
    result = processor.{self.random.choice(self.tech_vocabulary["functions"])}(data)
except ProcessingError as e:
    print(f"Erro: {{e}}")
```

## Como otimizar performance?

1. Use cache
2. Configure workers adequadamente
3. Monitore métricas
4. Ajuste batch size

## Problemas comuns

### Timeout Error
- Aumente o timeout
- Verifique conectividade
- Reduza tamanho dos dados

### Memory Error
- Configure cache TTL
- Reduza batch size
- Monitore uso de memória
'''
    
    def _generate_changelog_content(self) -> str:
        """Gera conteúdo de changelog"""
        return f'''# Changelog

## [2.0.0] - 2024-01-01

### Added
- Nova API assíncrona
- Sistema de cache inteligente
- Métricas avançadas
- Suporte a {self.random.choice(self.tech_vocabulary["concepts"])}

### Changed
- **BREAKING**: API completamente reescrita
- Performance melhorada em {self.random.randint(200, 500)}%
- Uso de memória reduzido

### Fixed
- Correção de memory leaks
- Tratamento de timeout melhorado
- Validação de entrada mais robusta

## [1.5.0] - 2023-12-01

### Added
- Processamento em lote
- Retry automático
- Logging estruturado

### Fixed
- Correção de race conditions
- Melhoria na estabilidade

## [1.0.0] - 2023-10-01

### Added
- Versão inicial
- Funcionalidades básicas de {self.random.choice(self.tech_vocabulary["functions"])}
- Documentação inicial
'''
    
    def _generate_json_config(self) -> str:
        """Gera configuração JSON"""
        return f'''{{
  "version": "1.0.0",
  "environment": "development",
  "debug": true,
  "logging": {{
    "level": "INFO",
    "format": "json"
  }},
  "database": {{
    "host": "localhost",
    "port": {self.random.randint(5000, 6000)},
    "name": "{self.random.choice(self.tech_vocabulary['variables'])}_db"
  }},
  "cache": {{
    "enabled": true,
    "ttl": {self.random.randint(300, 3600)},
    "max_size": {self.random.randint(100, 1000)}
  }},
  "workers": {{
    "count": {self.random.randint(2, 8)},
    "timeout": {self.random.randint(30, 120)}
  }}
}}'''
    
    def _generate_yaml_config(self) -> str:
        """Gera configuração YAML"""
        return f'''version: "1.0.0"
environment: development
debug: true

logging:
  level: INFO
  format: json
  handlers:
    - console
    - file

database:
  host: localhost
  port: {self.random.randint(5000, 6000)}
  name: {self.random.choice(self.tech_vocabulary['variables'])}_db
  pool_size: {self.random.randint(5, 20)}

cache:
  enabled: true
  ttl: {self.random.randint(300, 3600)}
  max_size: {self.random.randint(100, 1000)}
  
workers:
  count: {self.random.randint(2, 8)}
  timeout: {self.random.randint(30, 120)}
  queue_size: {self.random.randint(100, 1000)}

features:
  {self.random.choice(self.tech_vocabulary['functions'])}:
    enabled: true
    timeout: {self.random.randint(10, 60)}
  
  monitoring:
    metrics: true
    health_check: true
'''
    
    def _generate_env_config(self) -> str:
        """Gera configuração .env"""
        return f'''# Environment Configuration
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_HOST=localhost
DATABASE_PORT={self.random.randint(5000, 6000)}
DATABASE_NAME={self.random.choice(self.tech_vocabulary['variables'])}_db
DATABASE_USER=admin
DATABASE_PASSWORD=secret123

# Cache
CACHE_ENABLED=true
CACHE_TTL={self.random.randint(300, 3600)}
CACHE_MAX_SIZE={self.random.randint(100, 1000)}

# Workers
WORKER_COUNT={self.random.randint(2, 8)}
WORKER_TIMEOUT={self.random.randint(30, 120)}

# API Keys
API_KEY=sk-{self.random.choice(string.ascii_letters + string.digits) * 32}
SECRET_KEY={self.random.choice(string.ascii_letters + string.digits) * 64}

# External Services
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200
'''


if __name__ == "__main__":
    # Exemplo de uso
    generator = TestDataGenerator()
    
    print("🎲 Gerador de Dados de Teste")
    print("=" * 50)
    
    # Gerar arquivos de teste
    test_files = generator.generate_test_files(5)
    print(f"\\n📄 Gerados {len(test_files)} arquivos de teste:")
    for file in test_files:
        print(f"  - {file.name} ({file.language}, {file.complexity}, {file.size_mb:.2f}MB)")
    
    # Gerar queries de exemplo
    queries = generator.generate_query_examples(3)
    print(f"\\n❓ Geradas {len(queries)} queries de exemplo:")
    for query in queries:
        print(f"  - {query['text'][:50]}...")
    
    # Gerar cenários de erro
    error_scenarios = generator.generate_error_scenarios()
    print(f"\\n⚠️ Gerados {len(error_scenarios)} cenários de erro:")
    for scenario in error_scenarios:
        print(f"  - {scenario['name']}: {scenario['description']}")