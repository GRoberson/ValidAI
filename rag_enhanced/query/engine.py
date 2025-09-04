#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Advanced Query Engine - Motor de consultas avançado

Este módulo fornece processamento inteligente de consultas com
análise contextual, otimização e recursos avançados de RAG.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from google import genai
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
import vertexai

from ..core.interfaces import QueryEngineInterface
from ..core.models import RAGConfig, QueryResponse
from ..core.exceptions import QueryError, NetworkError, AuthenticationError
from .analyzer import AnalysisEngine
from .formatter import ResponseFormatter
from .history import QueryHistory


@dataclass
class QueryContext:
    """
    🔍 Contexto de uma consulta
    """
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: List[Dict] = None
    focus_areas: List[str] = None
    analysis_depth: str = "medium"  # shallow, medium, deep
    include_code_examples: bool = True
    max_response_length: int = 2000
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.focus_areas is None:
            self.focus_areas = []


class AdvancedQueryEngine(QueryEngineInterface):
    """
    🔍 Motor de consultas avançado
    
    Fornece processamento inteligente de consultas com:
    - Análise contextual e otimização de queries
    - Integração com Vertex AI RAG
    - Análise de padrões de código
    - Geração de documentação
    - Histórico de conversas
    - Formatação inteligente de respostas
    """
    
    def __init__(self, config: RAGConfig, corpus_name: Optional[str] = None):
        """
        Inicializa o motor de consultas
        
        Args:
            config: Configuração do sistema
            corpus_name: Nome do corpus RAG (opcional)
        """
        self.config = config
        self.corpus_name = corpus_name
        
        # Componentes especializados
        self.analysis_engine = AnalysisEngine(config)
        self.response_formatter = ResponseFormatter()
        self.query_history = QueryHistory()
        
        # Cliente Vertex AI
        self.genai_client = None
        self.rag_tool = None
        
        # Cache de respostas
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Estatísticas
        self.query_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0
        }
    
    def initialize_client(self) -> None:
        """
        Inicializa cliente Vertex AI
        
        Raises:
            AuthenticationError: Se não conseguir autenticar
            QueryError: Se não conseguir inicializar
        """
        try:
            # Inicializar Vertex AI
            vertexai.init(
                project=self.config.project_id,
                location=self.config.location
            )
            
            # Criar cliente GenAI
            self.genai_client = genai.Client(
                vertexai=True,
                project=self.config.project_id,
                location=self.config.location
            )
            
            # Configurar ferramenta RAG se corpus disponível
            if self.corpus_name:
                self._setup_rag_tool()
            
        except Exception as e:
            if "authentication" in str(e).lower() or "credentials" in str(e).lower():
                raise AuthenticationError(
                    service="Vertex AI",
                    message="Falha na autenticação",
                    suggestion="Verifique suas credenciais do Google Cloud"
                )
            else:
                raise QueryError(
                    query="initialization",
                    message=f"Erro ao inicializar cliente: {str(e)}",
                    suggestion="Verifique configurações do Vertex AI"
                )
    
    def process_query(self, 
                     query: str, 
                     context: Optional[QueryContext] = None) -> QueryResponse:
        """
        Processa uma consulta com contexto opcional
        
        Args:
            query: Consulta a ser processada
            context: Contexto adicional para a consulta
            
        Returns:
            Resposta estruturada da consulta
        """
        if not self.genai_client:
            self.initialize_client()
        
        start_time = time.time()
        
        try:
            # Usar contexto padrão se não fornecido
            if context is None:
                context = QueryContext()
            
            # Verificar cache primeiro
            cache_key = self._generate_cache_key(query, context)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.query_stats["cache_hits"] += 1
                return cached_response
            
            # Pré-processar consulta
            processed_query = self._preprocess_query(query, context)
            
            # Executar consulta
            raw_response = self._execute_query(processed_query, context)
            
            # Pós-processar resposta
            formatted_response = self._postprocess_response(raw_response, query, context)
            
            # Calcular métricas
            processing_time = time.time() - start_time
            
            # Criar resposta final
            response = QueryResponse(
                query=query,
                answer=formatted_response["answer"],
                confidence_score=formatted_response.get("confidence", 0.8),
                processing_time=processing_time,
                sources=formatted_response.get("sources", []),
                suggestions=formatted_response.get("suggestions", []),
                related_queries=formatted_response.get("related_queries", []),
                metadata=formatted_response.get("metadata", {})
            )
            
            # Armazenar no cache
            self._cache_response(cache_key, response)
            
            # Adicionar ao histórico
            self.query_history.add_query(query, response, context)
            
            # Atualizar estatísticas
            self._update_stats(True, processing_time)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            
            if isinstance(e, (QueryError, AuthenticationError, NetworkError)):
                raise
            
            raise QueryError(
                query=query,
                message=f"Erro ao processar consulta: {str(e)}",
                suggestion="Tente reformular a pergunta ou verifique a conectividade"
            )
    
    def analyze_code_patterns(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analisa padrões de código na base
        
        Args:
            focus_areas: Áreas específicas para focar a análise
            
        Returns:
            Análise de padrões encontrados
        """
        return self.analysis_engine.analyze_patterns(focus_areas)
    
    def generate_documentation(self, 
                             doc_type: str, 
                             options: Optional[Dict] = None) -> str:
        """
        Gera documentação baseada no código
        
        Args:
            doc_type: Tipo de documentação (api, architecture, etc.)
            options: Opções específicas para o tipo de documentação
            
        Returns:
            Documentação gerada
        """
        if not options:
            options = {}
        
        # Preparar contexto para geração de documentação
        context = QueryContext(
            focus_areas=[doc_type],
            analysis_depth="deep",
            include_code_examples=options.get("include_examples", True),
            max_response_length=options.get("max_length", 5000)
        )
        
        # Gerar query baseada no tipo de documentação
        doc_queries = {
            "api": "Gere documentação completa da API, incluindo endpoints, parâmetros e exemplos de uso.",
            "architecture": "Descreva a arquitetura do sistema, componentes principais e suas interações.",
            "setup": "Crie um guia de instalação e configuração passo a passo.",
            "usage": "Gere exemplos de uso e tutoriais para as principais funcionalidades.",
            "contributing": "Crie um guia para contribuidores com padrões de código e processo de desenvolvimento."
        }
        
        query = doc_queries.get(doc_type, f"Gere documentação sobre {doc_type}")
        
        # Processar consulta
        response = self.process_query(query, context)
        
        return response.answer
    
    def assess_code_quality(self) -> Dict[str, Any]:
        """
        Avalia qualidade do código
        
        Returns:
            Avaliação de qualidade com métricas e recomendações
        """
        return self.analysis_engine.assess_quality()
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analisa dependências da base de código
        
        Returns:
            Análise de dependências e estrutura
        """
        return self.analysis_engine.analyze_dependencies()
    
    def get_query_suggestions(self, partial_query: str) -> List[str]:
        """
        Obtém sugestões de consulta baseadas em entrada parcial
        
        Args:
            partial_query: Consulta parcial
            
        Returns:
            Lista de sugestões
        """
        # Sugestões baseadas no histórico
        history_suggestions = self.query_history.get_similar_queries(partial_query)
        
        # Sugestões baseadas em padrões comuns
        common_patterns = [
            "Como funciona o {component}?",
            "Explique a arquitetura do {module}",
            "Quais são as dependências de {file}?",
            "Como usar a função {function}?",
            "Qual é o propósito da classe {class}?",
            "Mostre exemplos de {pattern}",
            "Como implementar {feature}?",
            "Quais são os testes para {component}?"
        ]
        
        # Combinar sugestões
        suggestions = history_suggestions[:3]  # Top 3 do histórico
        
        # Adicionar padrões relevantes
        for pattern in common_patterns:
            if any(word in partial_query.lower() for word in pattern.lower().split()):
                suggestions.append(pattern)
        
        return suggestions[:8]  # Máximo 8 sugestões
    
    def get_conversation_context(self, session_id: str) -> List[Dict]:
        """
        Obtém contexto de conversa para uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Histórico de conversa
        """
        return self.query_history.get_session_history(session_id)
    
    def clear_cache(self) -> None:
        """Limpa cache de respostas"""
        self.response_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do motor de consultas
        
        Returns:
            Dicionário com estatísticas
        """
        stats = self.query_stats.copy()
        
        # Adicionar estatísticas do histórico
        history_stats = self.query_history.get_stats()
        stats.update(history_stats)
        
        # Adicionar informações do cache
        stats["cache_size"] = len(self.response_cache)
        
        return stats
    
    def _setup_rag_tool(self) -> None:
        """Configura ferramenta RAG"""
        try:
            self.rag_tool = Tool(
                retrieval=Retrieval(
                    vertex_rag_store=VertexRagStore(
                        rag_corpora=[self.corpus_name],
                        similarity_top_k=10,
                        vector_distance_threshold=0.5
                    )
                )
            )
        except Exception as e:
            raise QueryError(
                query="rag_setup",
                message=f"Erro ao configurar RAG: {str(e)}",
                suggestion="Verifique se o corpus existe e está acessível"
            )
    
    def _preprocess_query(self, query: str, context: QueryContext) -> str:
        """Pré-processa consulta para otimização"""
        processed_query = query.strip()
        
        # Adicionar contexto de conversa se disponível
        if context.conversation_history:
            recent_context = context.conversation_history[-3:]  # Últimas 3 interações
            context_summary = self._summarize_conversation_context(recent_context)
            processed_query = f"Contexto: {context_summary}\n\nPergunta: {processed_query}"
        
        # Adicionar áreas de foco se especificadas
        if context.focus_areas:
            focus_text = ", ".join(context.focus_areas)
            processed_query += f"\n\nFoque especialmente em: {focus_text}"
        
        # Ajustar baseado na profundidade de análise
        if context.analysis_depth == "deep":
            processed_query += "\n\nForneça uma análise detalhada e abrangente."
        elif context.analysis_depth == "shallow":
            processed_query += "\n\nForneça uma resposta concisa e direta."
        
        return processed_query
    
    def _execute_query(self, query: str, context: QueryContext) -> str:
        """Executa consulta no Vertex AI"""
        try:
            # Configurar parâmetros de geração
            config = GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=min(context.max_response_length, self.config.max_output_tokens),
                tools=[self.rag_tool] if self.rag_tool else None
            )
            
            # Executar consulta
            response = self.genai_client.models.generate_content(
                model=self.config.generation_model,
                contents=query,
                config=config
            )
            
            return response.text
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise NetworkError(
                    operation="query_execution",
                    message="Limite de API atingido",
                    suggestion="Aguarde alguns minutos antes de tentar novamente"
                )
            else:
                raise QueryError(
                    query=query,
                    message=f"Erro na execução: {str(e)}",
                    suggestion="Verifique conectividade e configurações"
                )
    
    def _postprocess_response(self, 
                            raw_response: str, 
                            original_query: str, 
                            context: QueryContext) -> Dict[str, Any]:
        """Pós-processa resposta para formatação"""
        return self.response_formatter.format_response(
            raw_response, 
            original_query, 
            context
        )
    
    def _generate_cache_key(self, query: str, context: QueryContext) -> str:
        """Gera chave de cache para consulta"""
        import hashlib
        
        # Incluir elementos relevantes do contexto
        context_str = f"{context.analysis_depth}_{context.include_code_examples}_{len(context.focus_areas)}"
        
        # Gerar hash
        cache_input = f"{query}_{context_str}_{self.corpus_name or ''}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[QueryResponse]:
        """Obtém resposta do cache se válida"""
        if cache_key not in self.response_cache:
            return None
        
        cached_item = self.response_cache[cache_key]
        
        # Verificar TTL
        if time.time() - cached_item["timestamp"] > self.cache_ttl:
            del self.response_cache[cache_key]
            return None
        
        return cached_item["response"]
    
    def _cache_response(self, cache_key: str, response: QueryResponse) -> None:
        """Armazena resposta no cache"""
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Limitar tamanho do cache
        if len(self.response_cache) > 100:
            # Remover item mais antigo
            oldest_key = min(self.response_cache.keys(), 
                           key=lambda k: self.response_cache[k]["timestamp"])
            del self.response_cache[oldest_key]
    
    def _summarize_conversation_context(self, recent_history: List[Dict]) -> str:
        """Sumariza contexto de conversa recente"""
        if not recent_history:
            return ""
        
        summary_parts = []
        for item in recent_history:
            if "query" in item and "response" in item:
                # Resumir pergunta e resposta
                query_summary = item["query"][:100] + "..." if len(item["query"]) > 100 else item["query"]
                summary_parts.append(f"P: {query_summary}")
        
        return " | ".join(summary_parts)
    
    def _update_stats(self, success: bool, processing_time: float) -> None:
        """Atualiza estatísticas de consulta"""
        self.query_stats["total_queries"] += 1
        
        if success:
            self.query_stats["successful_queries"] += 1
        else:
            self.query_stats["failed_queries"] += 1
        
        # Atualizar tempo médio de resposta
        total_successful = self.query_stats["successful_queries"]
        if total_successful > 0:
            current_avg = self.query_stats["avg_response_time"]
            new_avg = ((current_avg * (total_successful - 1)) + processing_time) / total_successful
            self.query_stats["avg_response_time"] = new_avg