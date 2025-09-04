#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📚 Query History - Sistema de histórico de consultas

Este módulo gerencia o histórico de consultas com busca inteligente,
análise de padrões e persistência de conversas.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
from collections import defaultdict, Counter

from ..core.models import QueryResponse
from ..core.exceptions import ProcessingError
from .engine import QueryContext


@dataclass
class QueryHistoryEntry:
    """
    📝 Entrada no histórico de consultas
    """
    id: str
    query: str
    response: str
    confidence: float
    processing_time: float
    timestamp: datetime
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context_data: Optional[Dict] = None
    feedback_rating: Optional[int] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryHistoryEntry':
        """Cria instância a partir de dicionário"""
        return cls(**data)


class QueryHistory:
    """
    📚 Gerenciador de histórico de consultas
    
    Fornece funcionalidades avançadas incluindo:
    - Persistência em SQLite
    - Busca semântica por similaridade
    - Análise de padrões de uso
    - Agrupamento por sessões
    - Estatísticas detalhadas
    - Export/import de dados
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializa o gerenciador de histórico
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path or Path(".rag_history") / "query_history.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória para consultas recentes
        self.memory_cache: Dict[str, QueryHistoryEntry] = {}
        self.cache_size = 100
        
        # Estatísticas
        self.stats = {
            "total_queries": 0,
            "unique_sessions": 0,
            "avg_confidence": 0.0,
            "avg_processing_time": 0.0,
            "most_common_topics": [],
            "query_frequency": defaultdict(int)
        }
        
        # Inicializar banco de dados
        self._init_database()
        self._load_stats()
    
    def add_query(self, 
                  query: str, 
                  response: QueryResponse, 
                  context: Optional[QueryContext] = None) -> str:
        """
        Adiciona consulta ao histórico
        
        Args:
            query: Consulta realizada
            response: Resposta obtida
            context: Contexto da consulta
            
        Returns:
            ID da entrada criada
        """
        try:
            # Gerar ID único
            entry_id = self._generate_entry_id(query, response.timestamp)
            
            # Criar entrada
            entry = QueryHistoryEntry(
                id=entry_id,
                query=query,
                response=response.answer,
                confidence=response.confidence_score,
                processing_time=response.processing_time,
                timestamp=response.timestamp,
                session_id=context.session_id if context else None,
                user_id=context.user_id if context else None,
                context_data=self._serialize_context(context) if context else None,
                tags=self._extract_tags(query, response.answer)
            )
            
            # Adicionar ao cache
            self.memory_cache[entry_id] = entry
            self._manage_cache_size()
            
            # Persistir no banco
            self._save_to_database(entry)
            
            # Atualizar estatísticas
            self._update_stats(entry)
            
            return entry_id
            
        except Exception as e:
            raise ProcessingError(
                operation="add_query_history",
                message=f"Erro ao adicionar consulta ao histórico: {str(e)}",
                suggestion="Verifique permissões de escrita no diretório"
            )
    
    def get_query(self, entry_id: str) -> Optional[QueryHistoryEntry]:
        """
        Obtém consulta específica por ID
        
        Args:
            entry_id: ID da entrada
            
        Returns:
            Entrada do histórico ou None se não encontrada
        """
        # Verificar cache primeiro
        if entry_id in self.memory_cache:
            return self.memory_cache[entry_id]
        
        # Buscar no banco
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM query_history WHERE id = ?",
                    (entry_id,)
                )
                
                row = cursor.fetchone()
                if row:
                    entry = self._row_to_entry(row)
                    self.memory_cache[entry_id] = entry
                    return entry
                
        except Exception as e:
            print(f"Erro ao buscar consulta {entry_id}: {e}")
        
        return None
    
    def search_queries(self, 
                      search_term: str, 
                      limit: int = 10,
                      session_id: Optional[str] = None) -> List[QueryHistoryEntry]:
        """
        Busca consultas por termo
        
        Args:
            search_term: Termo de busca
            limit: Número máximo de resultados
            session_id: Filtrar por sessão específica
            
        Returns:
            Lista de entradas encontradas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Construir query SQL
                sql = """
                    SELECT * FROM query_history 
                    WHERE (query LIKE ? OR response LIKE ? OR tags LIKE ?)
                """
                params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
                
                if session_id:
                    sql += " AND session_id = ?"
                    params.append(session_id)
                
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [self._row_to_entry(row) for row in rows]
                
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    def get_similar_queries(self, 
                           query: str, 
                           limit: int = 5,
                           min_similarity: float = 0.3) -> List[QueryHistoryEntry]:
        """
        Encontra consultas similares usando similaridade textual
        
        Args:
            query: Consulta de referência
            limit: Número máximo de resultados
            min_similarity: Similaridade mínima (0-1)
            
        Returns:
            Lista de consultas similares ordenadas por similaridade
        """
        try:
            # Buscar todas as consultas recentes
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM query_history ORDER BY timestamp DESC LIMIT 100"
                )
                rows = cursor.fetchall()
                
                # Calcular similaridade
                similar_queries = []
                query_words = set(query.lower().split())
                
                for row in rows:
                    entry = self._row_to_entry(row)
                    similarity = self._calculate_similarity(query, entry.query)
                    
                    if similarity >= min_similarity:
                        similar_queries.append((similarity, entry))
                
                # Ordenar por similaridade e retornar
                similar_queries.sort(key=lambda x: x[0], reverse=True)
                return [entry for _, entry in similar_queries[:limit]]
                
        except Exception as e:
            print(f"Erro ao buscar consultas similares: {e}")
            return []
    
    def get_session_history(self, 
                           session_id: str, 
                           limit: int = 50) -> List[QueryHistoryEntry]:
        """
        Obtém histórico de uma sessão específica
        
        Args:
            session_id: ID da sessão
            limit: Número máximo de entradas
            
        Returns:
            Lista de entradas da sessão ordenadas por tempo
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    SELECT * FROM query_history 
                    WHERE session_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                    """,
                    (session_id, limit)
                )
                
                rows = cursor.fetchall()
                return [self._row_to_entry(row) for row in rows]
                
        except Exception as e:
            print(f"Erro ao buscar histórico da sessão: {e}")
            return []
    
    def get_recent_queries(self, 
                          hours: int = 24, 
                          limit: int = 20) -> List[QueryHistoryEntry]:
        """
        Obtém consultas recentes
        
        Args:
            hours: Número de horas para considerar como "recente"
            limit: Número máximo de consultas
            
        Returns:
            Lista de consultas recentes
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    SELECT * FROM query_history 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                    """,
                    (cutoff_time.isoformat(), limit)
                )
                
                rows = cursor.fetchall()
                return [self._row_to_entry(row) for row in rows]
                
        except Exception as e:
            print(f"Erro ao buscar consultas recentes: {e}")
            return []
    
    def add_feedback(self, entry_id: str, rating: int) -> bool:
        """
        Adiciona feedback para uma consulta
        
        Args:
            entry_id: ID da entrada
            rating: Avaliação (1-5)
            
        Returns:
            True se adicionou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE query_history SET feedback_rating = ? WHERE id = ?",
                    (rating, entry_id)
                )
                
                # Atualizar cache se presente
                if entry_id in self.memory_cache:
                    self.memory_cache[entry_id].feedback_rating = rating
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Erro ao adicionar feedback: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do histórico
        
        Returns:
            Dicionário com estatísticas
        """
        return self.stats.copy()
    
    def analyze_usage_patterns(self) -> Dict[str, Any]:
        """
        Analisa padrões de uso
        
        Returns:
            Análise de padrões de uso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Consultas por hora do dia
                cursor.execute("""
                    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                    FROM query_history 
                    GROUP BY hour 
                    ORDER BY hour
                """)
                hourly_distribution = {row['hour']: row['count'] for row in cursor.fetchall()}
                
                # Consultas por dia da semana
                cursor.execute("""
                    SELECT strftime('%w', timestamp) as day, COUNT(*) as count
                    FROM query_history 
                    GROUP BY day 
                    ORDER BY day
                """)
                daily_distribution = {row['day']: row['count'] for row in cursor.fetchall()}
                
                # Tópicos mais comuns
                cursor.execute("""
                    SELECT tags, COUNT(*) as count
                    FROM query_history 
                    WHERE tags IS NOT NULL AND tags != ''
                    GROUP BY tags 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                common_topics = [(row['tags'], row['count']) for row in cursor.fetchall()]
                
                # Sessões mais longas
                cursor.execute("""
                    SELECT session_id, COUNT(*) as query_count
                    FROM query_history 
                    WHERE session_id IS NOT NULL
                    GROUP BY session_id 
                    ORDER BY query_count DESC 
                    LIMIT 5
                """)
                longest_sessions = [(row['session_id'], row['query_count']) for row in cursor.fetchall()]
                
                return {
                    "hourly_distribution": hourly_distribution,
                    "daily_distribution": daily_distribution,
                    "common_topics": common_topics,
                    "longest_sessions": longest_sessions,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Erro na análise de padrões: {e}")
            return {}
    
    def export_history(self, 
                      output_path: Path, 
                      format: str = "json",
                      date_range: Optional[Tuple[datetime, datetime]] = None) -> bool:
        """
        Exporta histórico para arquivo
        
        Args:
            output_path: Caminho do arquivo de saída
            format: Formato de exportação (json, csv)
            date_range: Range de datas opcional (início, fim)
            
        Returns:
            True se exportou com sucesso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Construir query com filtro de data se necessário
                sql = "SELECT * FROM query_history"
                params = []
                
                if date_range:
                    sql += " WHERE timestamp BETWEEN ? AND ?"
                    params.extend([date_range[0].isoformat(), date_range[1].isoformat()])
                
                sql += " ORDER BY timestamp DESC"
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                # Converter para formato desejado
                if format.lower() == "json":
                    data = [dict(row) for row in rows]
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                elif format.lower() == "csv":
                    import csv
                    with open(output_path, 'w', newline='', encoding='utf-8') as f:
                        if rows:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            for row in rows:
                                writer.writerow(dict(row))
                
                return True
                
        except Exception as e:
            print(f"Erro ao exportar histórico: {e}")
            return False
    
    def clear_history(self, 
                     older_than_days: Optional[int] = None,
                     session_id: Optional[str] = None) -> int:
        """
        Limpa histórico baseado em critérios
        
        Args:
            older_than_days: Remove entradas mais antigas que X dias
            session_id: Remove apenas entradas de uma sessão específica
            
        Returns:
            Número de entradas removidas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if older_than_days:
                    cutoff_date = datetime.now() - timedelta(days=older_than_days)
                    cursor.execute(
                        "DELETE FROM query_history WHERE timestamp < ?",
                        (cutoff_date.isoformat(),)
                    )
                elif session_id:
                    cursor.execute(
                        "DELETE FROM query_history WHERE session_id = ?",
                        (session_id,)
                    )
                else:
                    cursor.execute("DELETE FROM query_history")
                
                deleted_count = cursor.rowcount
                
                # Limpar cache
                self.memory_cache.clear()
                
                # Recarregar estatísticas
                self._load_stats()
                
                return deleted_count
                
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}")
            return 0
    
    def _init_database(self) -> None:
        """Inicializa banco de dados SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS query_history (
                        id TEXT PRIMARY KEY,
                        query TEXT NOT NULL,
                        response TEXT NOT NULL,
                        confidence REAL,
                        processing_time REAL,
                        timestamp TEXT NOT NULL,
                        session_id TEXT,
                        user_id TEXT,
                        context_data TEXT,
                        feedback_rating INTEGER,
                        tags TEXT
                    )
                """)
                
                # Criar índices para performance
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_timestamp ON query_history(timestamp)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_session ON query_history(session_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_query ON query_history(query)"
                )
                
                conn.commit()
                
        except Exception as e:
            raise ProcessingError(
                operation="database_init",
                message=f"Erro ao inicializar banco de dados: {str(e)}",
                suggestion="Verifique permissões de escrita no diretório"
            )
    
    def _generate_entry_id(self, query: str, timestamp: datetime) -> str:
        """Gera ID único para entrada"""
        content = f"{query}_{timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _serialize_context(self, context: QueryContext) -> str:
        """Serializa contexto para armazenamento"""
        try:
            context_dict = {
                'user_id': context.user_id,
                'session_id': context.session_id,
                'focus_areas': context.focus_areas,
                'analysis_depth': context.analysis_depth,
                'include_code_examples': context.include_code_examples,
                'max_response_length': context.max_response_length
            }
            return json.dumps(context_dict)
        except Exception:
            return "{}"
    
    def _extract_tags(self, query: str, response: str) -> List[str]:
        """Extrai tags automáticas da consulta e resposta"""
        tags = []
        
        # Tags baseadas em palavras-chave na query
        query_lower = query.lower()
        
        tag_keywords = {
            'python': ['python', 'py', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue'],
            'java': ['java', 'spring', 'maven'],
            'database': ['sql', 'database', 'db', 'mysql', 'postgres'],
            'api': ['api', 'rest', 'endpoint', 'http'],
            'error': ['erro', 'error', 'bug', 'problema'],
            'tutorial': ['como', 'tutorial', 'passo', 'guia'],
            'optimization': ['otimizar', 'performance', 'melhorar']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # Limitar a 5 tags
    
    def _save_to_database(self, entry: QueryHistoryEntry) -> None:
        """Salva entrada no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO query_history 
                    (id, query, response, confidence, processing_time, timestamp, 
                     session_id, user_id, context_data, feedback_rating, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    entry.query,
                    entry.response,
                    entry.confidence,
                    entry.processing_time,
                    entry.timestamp.isoformat(),
                    entry.session_id,
                    entry.user_id,
                    entry.context_data,
                    entry.feedback_rating,
                    ','.join(entry.tags) if entry.tags else None
                ))
                
                conn.commit()
                
        except Exception as e:
            raise ProcessingError(
                operation="save_history",
                message=f"Erro ao salvar no banco: {str(e)}"
            )
    
    def _row_to_entry(self, row: sqlite3.Row) -> QueryHistoryEntry:
        """Converte linha do banco para entrada"""
        tags = row['tags'].split(',') if row['tags'] else []
        
        return QueryHistoryEntry(
            id=row['id'],
            query=row['query'],
            response=row['response'],
            confidence=row['confidence'],
            processing_time=row['processing_time'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            session_id=row['session_id'],
            user_id=row['user_id'],
            context_data=row['context_data'],
            feedback_rating=row['feedback_rating'],
            tags=tags
        )
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calcula similaridade entre duas queries (Jaccard)"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _manage_cache_size(self) -> None:
        """Gerencia tamanho do cache em memória"""
        if len(self.memory_cache) > self.cache_size:
            # Remove entradas mais antigas
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].timestamp
            )
            
            # Manter apenas as mais recentes
            entries_to_keep = sorted_entries[-self.cache_size:]
            self.memory_cache = dict(entries_to_keep)
    
    def _update_stats(self, entry: QueryHistoryEntry) -> None:
        """Atualiza estatísticas com nova entrada"""
        self.stats["total_queries"] += 1
        
        # Atualizar média de confiança
        current_avg = self.stats["avg_confidence"]
        total = self.stats["total_queries"]
        self.stats["avg_confidence"] = ((current_avg * (total - 1)) + entry.confidence) / total
        
        # Atualizar média de tempo de processamento
        current_avg_time = self.stats["avg_processing_time"]
        self.stats["avg_processing_time"] = ((current_avg_time * (total - 1)) + entry.processing_time) / total
        
        # Atualizar frequência de queries
        query_words = entry.query.lower().split()[:3]  # Primeiras 3 palavras
        query_key = ' '.join(query_words)
        self.stats["query_frequency"][query_key] += 1
    
    def _load_stats(self) -> None:
        """Carrega estatísticas do banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de queries
                cursor.execute("SELECT COUNT(*) FROM query_history")
                self.stats["total_queries"] = cursor.fetchone()[0]
                
                # Sessões únicas
                cursor.execute("SELECT COUNT(DISTINCT session_id) FROM query_history WHERE session_id IS NOT NULL")
                self.stats["unique_sessions"] = cursor.fetchone()[0]
                
                # Média de confiança
                cursor.execute("SELECT AVG(confidence) FROM query_history")
                result = cursor.fetchone()[0]
                self.stats["avg_confidence"] = result if result else 0.0
                
                # Média de tempo de processamento
                cursor.execute("SELECT AVG(processing_time) FROM query_history")
                result = cursor.fetchone()[0]
                self.stats["avg_processing_time"] = result if result else 0.0
                
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")