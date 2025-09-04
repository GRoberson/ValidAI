#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 Response Formatter - Formatador inteligente de respostas

Este módulo fornece formatação avançada de respostas com estruturação
automática, extração de código, e formatação para diferentes contextos.
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from .engine import QueryContext


@dataclass
class FormattedSection:
    """
    📝 Seção formatada de uma resposta
    """
    type: str  # text, code, list, table, diagram
    content: str
    language: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ResponseFormatter:
    """
    🎨 Formatador inteligente de respostas
    
    Fornece formatação avançada incluindo:
    - Extração automática de código
    - Estruturação de conteúdo
    - Formatação para diferentes contextos
    - Geração de metadados
    - Sugestões relacionadas
    """
    
    def __init__(self):
        """Inicializa o formatador"""
        # Padrões para extração de conteúdo
        self.code_patterns = {
            'python': r'```python\n(.*?)\n```',
            'javascript': r'```(?:javascript|js)\n(.*?)\n```',
            'java': r'```java\n(.*?)\n```',
            'generic': r'```(?:\w+)?\n(.*?)\n```'
        }
        
        # Padrões para estruturação
        self.structure_patterns = {
            'headers': r'^#{1,6}\s+(.+)$',
            'lists': r'^[\*\-\+]\s+(.+)$',
            'numbered_lists': r'^\d+\.\s+(.+)$',
            'code_blocks': r'```[\w]*\n(.*?)\n```',
            'inline_code': r'`([^`]+)`'
        }
        
        # Templates para diferentes tipos de resposta
        self.response_templates = {
            'explanation': self._format_explanation,
            'tutorial': self._format_tutorial,
            'api_doc': self._format_api_documentation,
            'troubleshooting': self._format_troubleshooting,
            'code_review': self._format_code_review
        }
    
    def format_response(self, 
                       raw_response: str, 
                       original_query: str, 
                       context: QueryContext) -> Dict[str, Any]:
        """
        Formata resposta bruta em estrutura organizada
        
        Args:
            raw_response: Resposta bruta da IA
            original_query: Query original do usuário
            context: Contexto da consulta
            
        Returns:
            Resposta formatada com metadados
        """
        # Detectar tipo de resposta
        response_type = self._detect_response_type(raw_response, original_query)
        
        # Extrair seções estruturadas
        sections = self._extract_sections(raw_response)
        
        # Extrair código
        code_blocks = self._extract_code_blocks(raw_response)
        
        # Gerar resposta principal formatada
        formatted_answer = self._apply_formatting(raw_response, response_type, context)
        
        # Extrair fontes mencionadas
        sources = self._extract_sources(raw_response)
        
        # Gerar sugestões relacionadas
        suggestions = self._generate_suggestions(original_query, raw_response, context)
        
        # Gerar queries relacionadas
        related_queries = self._generate_related_queries(original_query, raw_response)
        
        # Calcular score de confiança
        confidence = self._calculate_confidence_score(raw_response, sections, code_blocks)
        
        return {
            "answer": formatted_answer,
            "confidence": confidence,
            "response_type": response_type,
            "sections": [section.__dict__ for section in sections],
            "code_blocks": code_blocks,
            "sources": sources,
            "suggestions": suggestions,
            "related_queries": related_queries,
            "metadata": {
                "formatting_applied": True,
                "sections_count": len(sections),
                "code_blocks_count": len(code_blocks),
                "estimated_reading_time": self._estimate_reading_time(formatted_answer),
                "complexity_level": self._assess_complexity(raw_response),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def format_for_console(self, formatted_response: Dict[str, Any]) -> str:
        """
        Formata resposta para exibição no console
        
        Args:
            formatted_response: Resposta já formatada
            
        Returns:
            String formatada para console
        """
        output = []
        
        # Cabeçalho
        confidence = formatted_response.get("confidence", 0)
        confidence_emoji = "🎯" if confidence > 0.8 else "🤔" if confidence > 0.5 else "❓"
        
        output.append(f"{confidence_emoji} **Resposta** (Confiança: {confidence:.1%})")
        output.append("=" * 50)
        
        # Resposta principal
        output.append(formatted_response["answer"])
        
        # Blocos de código
        code_blocks = formatted_response.get("code_blocks", [])
        if code_blocks:
            output.append("\n📝 **Exemplos de Código:**")
            for i, block in enumerate(code_blocks, 1):
                lang = block.get("language", "text")
                output.append(f"\n{i}. {lang.title()}:")
                output.append("```" + lang)
                output.append(block["content"])
                output.append("```")
        
        # Fontes
        sources = formatted_response.get("sources", [])
        if sources:
            output.append("\n📚 **Fontes:**")
            for source in sources[:3]:  # Limitar a 3
                output.append(f"   • {source}")
        
        # Sugestões
        suggestions = formatted_response.get("suggestions", [])
        if suggestions:
            output.append("\n💡 **Sugestões:**")
            for suggestion in suggestions[:2]:  # Limitar a 2
                output.append(f"   • {suggestion}")
        
        # Queries relacionadas
        related = formatted_response.get("related_queries", [])
        if related:
            output.append("\n🔍 **Perguntas Relacionadas:**")
            for query in related[:3]:  # Limitar a 3
                output.append(f"   • {query}")
        
        return "\n".join(output)
    
    def format_for_markdown(self, formatted_response: Dict[str, Any]) -> str:
        """
        Formata resposta para Markdown
        
        Args:
            formatted_response: Resposta já formatada
            
        Returns:
            String em formato Markdown
        """
        output = []
        
        # Título
        confidence = formatted_response.get("confidence", 0)
        output.append(f"# Resposta (Confiança: {confidence:.1%})")
        
        # Resposta principal
        output.append(formatted_response["answer"])
        
        # Seções estruturadas
        sections = formatted_response.get("sections", [])
        for section in sections:
            if section["type"] == "code":
                lang = section.get("language", "")
                output.append(f"\n```{lang}")
                output.append(section["content"])
                output.append("```")
            elif section["type"] == "list":
                items = section["content"].split("\n")
                for item in items:
                    if item.strip():
                        output.append(f"- {item.strip()}")
            else:
                output.append(f"\n{section['content']}")
        
        # Metadados
        metadata = formatted_response.get("metadata", {})
        if metadata:
            output.append("\n---")
            output.append("## Metadados")
            output.append(f"- Tempo de leitura estimado: {metadata.get('estimated_reading_time', 'N/A')}")
            output.append(f"- Nível de complexidade: {metadata.get('complexity_level', 'N/A')}")
            output.append(f"- Seções encontradas: {metadata.get('sections_count', 0)}")
        
        return "\n".join(output)
    
    def _detect_response_type(self, response: str, query: str) -> str:
        """Detecta o tipo de resposta baseado no conteúdo"""
        response_lower = response.lower()
        query_lower = query.lower()
        
        # Palavras-chave para diferentes tipos
        type_keywords = {
            'explanation': ['explicar', 'como funciona', 'o que é', 'porque'],
            'tutorial': ['como fazer', 'passo a passo', 'tutorial', 'guia'],
            'api_doc': ['api', 'endpoint', 'método', 'parâmetro', 'documentação'],
            'troubleshooting': ['erro', 'problema', 'não funciona', 'debug', 'corrigir'],
            'code_review': ['revisar', 'melhorar', 'otimizar', 'refatorar', 'qualidade']
        }
        
        # Contar matches para cada tipo
        type_scores = {}
        for response_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower or keyword in response_lower)
            type_scores[response_type] = score
        
        # Retornar tipo com maior score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        
        return 'explanation'  # Padrão
    
    def _extract_sections(self, response: str) -> List[FormattedSection]:
        """Extrai seções estruturadas da resposta"""
        sections = []
        lines = response.split('\n')
        current_section = []
        current_type = 'text'
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Detectar cabeçalhos
            if re.match(r'^#{1,6}\s+', line):
                if current_section:
                    sections.append(FormattedSection(
                        type=current_type,
                        content='\n'.join(current_section)
                    ))
                    current_section = []
                
                sections.append(FormattedSection(
                    type='header',
                    content=line,
                    metadata={'level': len(line) - len(line.lstrip('#'))}
                ))
                current_type = 'text'
            
            # Detectar blocos de código
            elif line.startswith('```'):
                if current_section:
                    sections.append(FormattedSection(
                        type=current_type,
                        content='\n'.join(current_section)
                    ))
                    current_section = []
                
                # Extrair linguagem
                language = line[3:].strip() or 'text'
                
                # Coletar conteúdo do bloco
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                sections.append(FormattedSection(
                    type='code',
                    content='\n'.join(code_lines),
                    language=language
                ))
                current_type = 'text'
            
            # Detectar listas
            elif re.match(r'^[\*\-\+]\s+', line) or re.match(r'^\d+\.\s+', line):
                if current_type != 'list':
                    if current_section:
                        sections.append(FormattedSection(
                            type=current_type,
                            content='\n'.join(current_section)
                        ))
                        current_section = []
                    current_type = 'list'
                
                current_section.append(line)
            
            # Texto normal
            else:
                if current_type != 'text':
                    if current_section:
                        sections.append(FormattedSection(
                            type=current_type,
                            content='\n'.join(current_section)
                        ))
                        current_section = []
                    current_type = 'text'
                
                if line:  # Ignorar linhas vazias
                    current_section.append(line)
            
            i += 1
        
        # Adicionar última seção
        if current_section:
            sections.append(FormattedSection(
                type=current_type,
                content='\n'.join(current_section)
            ))
        
        return sections
    
    def _extract_code_blocks(self, response: str) -> List[Dict[str, Any]]:
        """Extrai blocos de código da resposta"""
        code_blocks = []
        
        # Padrão para blocos de código com linguagem
        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for language, content in matches:
            code_blocks.append({
                'language': language or 'text',
                'content': content.strip(),
                'lines': len(content.strip().split('\n')),
                'size': len(content)
            })
        
        # Também extrair código inline
        inline_pattern = r'`([^`\n]+)`'
        inline_matches = re.findall(inline_pattern, response)
        
        for match in inline_matches:
            if len(match) > 10:  # Apenas código inline significativo
                code_blocks.append({
                    'language': 'inline',
                    'content': match,
                    'lines': 1,
                    'size': len(match)
                })
        
        return code_blocks
    
    def _extract_sources(self, response: str) -> List[str]:
        """Extrai fontes mencionadas na resposta"""
        sources = []
        
        # Padrões para identificar fontes
        source_patterns = [
            r'(?:baseado em|segundo|conforme|de acordo com)\s+([^.]+)',
            r'(?:fonte|referência):\s*([^.\n]+)',
            r'(?:documentação|manual|guia)\s+(?:do|da|de)\s+([^.\n]+)',
            r'(?:arquivo|módulo|classe)\s+`([^`]+)`'
        ]
        
        for pattern in source_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            sources.extend(matches)
        
        # Limpar e filtrar fontes
        cleaned_sources = []
        for source in sources:
            source = source.strip()
            if len(source) > 3 and len(source) < 100:
                cleaned_sources.append(source)
        
        return list(set(cleaned_sources))  # Remover duplicatas
    
    def _generate_suggestions(self, 
                            query: str, 
                            response: str, 
                            context: QueryContext) -> List[str]:
        """Gera sugestões baseadas na query e resposta"""
        suggestions = []
        
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Sugestões baseadas no tipo de query
        if any(word in query_lower for word in ['como', 'tutorial', 'passo']):
            suggestions.append("Experimente executar o código em um ambiente de teste")
            suggestions.append("Consulte a documentação oficial para mais detalhes")
        
        if any(word in query_lower for word in ['erro', 'problema', 'bug']):
            suggestions.append("Verifique os logs para mais informações sobre o erro")
            suggestions.append("Teste em um ambiente isolado para reproduzir o problema")
        
        if any(word in query_lower for word in ['otimizar', 'melhorar', 'performance']):
            suggestions.append("Execute testes de performance antes e depois das mudanças")
            suggestions.append("Considere usar ferramentas de profiling para identificar gargalos")
        
        # Sugestões baseadas no conteúdo da resposta
        if 'import' in response_lower or 'biblioteca' in response_lower:
            suggestions.append("Verifique se todas as dependências estão instaladas")
        
        if 'configuração' in response_lower or 'config' in response_lower:
            suggestions.append("Faça backup das configurações antes de fazer alterações")
        
        # Sugestões baseadas no contexto
        if context.analysis_depth == "shallow":
            suggestions.append("Para uma análise mais detalhada, especifique 'análise profunda' na sua próxima pergunta")
        
        return suggestions[:4]  # Limitar a 4 sugestões
    
    def _generate_related_queries(self, query: str, response: str) -> List[str]:
        """Gera queries relacionadas"""
        related = []
        
        query_lower = query.lower()
        
        # Templates baseados no tipo de query
        if 'como' in query_lower:
            related.extend([
                "Quais são as melhores práticas para isso?",
                "Que erros comuns devo evitar?",
                "Existe uma forma mais eficiente de fazer isso?"
            ])
        
        if 'o que é' in query_lower or 'explicar' in query_lower:
            related.extend([
                "Como implementar isso na prática?",
                "Quais são as vantagens e desvantagens?",
                "Quando devo usar essa abordagem?"
            ])
        
        if 'erro' in query_lower or 'problema' in query_lower:
            related.extend([
                "Como prevenir esse tipo de erro?",
                "Quais são as causas mais comuns desse problema?",
                "Existe uma forma de debuggar isso automaticamente?"
            ])
        
        # Extrair conceitos da resposta para gerar queries específicas
        concepts = self._extract_concepts(response)
        for concept in concepts[:2]:
            related.append(f"Me explique mais sobre {concept}")
            related.append(f"Como usar {concept} em outros contextos?")
        
        return related[:5]  # Limitar a 5 queries
    
    def _extract_concepts(self, response: str) -> List[str]:
        """Extrai conceitos principais da resposta"""
        concepts = []
        
        # Padrões para identificar conceitos
        concept_patterns = [
            r'(?:padrão|pattern)\s+(\w+)',
            r'(?:classe|class)\s+`?(\w+)`?',
            r'(?:função|method|método)\s+`?(\w+)`?',
            r'(?:biblioteca|library|framework)\s+(\w+)',
            r'(?:algoritmo|algorithm)\s+(\w+)'
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            concepts.extend(matches)
        
        # Filtrar conceitos válidos
        valid_concepts = []
        for concept in concepts:
            if len(concept) > 2 and concept.isalnum():
                valid_concepts.append(concept)
        
        return list(set(valid_concepts))[:5]  # Remover duplicatas e limitar
    
    def _calculate_confidence_score(self, 
                                  response: str, 
                                  sections: List[FormattedSection], 
                                  code_blocks: List[Dict]) -> float:
        """Calcula score de confiança da resposta"""
        score = 0.5  # Base score
        
        # Fatores que aumentam confiança
        if len(response) > 100:  # Resposta substancial
            score += 0.1
        
        if len(sections) > 2:  # Resposta bem estruturada
            score += 0.1
        
        if code_blocks:  # Contém exemplos de código
            score += 0.15
        
        if any(word in response.lower() for word in ['exemplo', 'por exemplo', 'como mostrado']):
            score += 0.1
        
        # Fatores que diminuem confiança
        if any(word in response.lower() for word in ['talvez', 'possivelmente', 'não tenho certeza']):
            score -= 0.2
        
        if len(response) < 50:  # Resposta muito curta
            score -= 0.2
        
        # Normalizar entre 0 e 1
        return max(0.0, min(1.0, score))
    
    def _estimate_reading_time(self, text: str) -> str:
        """Estima tempo de leitura"""
        words = len(text.split())
        minutes = max(1, words // 200)  # ~200 palavras por minuto
        
        if minutes == 1:
            return "1 minuto"
        else:
            return f"{minutes} minutos"
    
    def _assess_complexity(self, response: str) -> str:
        """Avalia nível de complexidade da resposta"""
        # Indicadores de complexidade
        complex_indicators = [
            'algoritmo', 'complexidade', 'otimização', 'arquitetura',
            'padrão', 'design pattern', 'refatoração', 'performance'
        ]
        
        technical_terms = sum(1 for term in complex_indicators if term in response.lower())
        code_blocks = len(re.findall(r'```', response))
        
        if technical_terms >= 3 or code_blocks >= 2:
            return "Avançado"
        elif technical_terms >= 1 or code_blocks >= 1:
            return "Intermediário"
        else:
            return "Básico"
    
    def _apply_formatting(self, 
                         response: str, 
                         response_type: str, 
                         context: QueryContext) -> str:
        """Aplica formatação específica baseada no tipo"""
        if response_type in self.response_templates:
            return self.response_templates[response_type](response, context)
        
        return self._format_generic(response, context)
    
    def _format_explanation(self, response: str, context: QueryContext) -> str:
        """Formata resposta explicativa"""
        # Adicionar estrutura clara para explicações
        if not response.startswith('#') and not response.startswith('##'):
            response = f"## Explicação\n\n{response}"
        
        return response
    
    def _format_tutorial(self, response: str, context: QueryContext) -> str:
        """Formata resposta de tutorial"""
        # Garantir numeração de passos
        lines = response.split('\n')
        formatted_lines = []
        step_counter = 1
        
        for line in lines:
            if re.match(r'^\d+\.', line.strip()):
                formatted_lines.append(line)
                step_counter += 1
            elif line.strip() and not line.startswith('#'):
                # Adicionar numeração se parecer um passo
                if any(word in line.lower() for word in ['primeiro', 'segundo', 'depois', 'em seguida']):
                    formatted_lines.append(f"{step_counter}. {line.strip()}")
                    step_counter += 1
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_api_documentation(self, response: str, context: QueryContext) -> str:
        """Formata documentação de API"""
        # Estruturar documentação de API
        if 'parâmetros' in response.lower() or 'parameters' in response.lower():
            # Tentar estruturar parâmetros em tabela
            response = re.sub(
                r'(\w+)\s*:\s*([^\n]+)',
                r'| \1 | \2 |',
                response
            )
        
        return response
    
    def _format_troubleshooting(self, response: str, context: QueryContext) -> str:
        """Formata resposta de troubleshooting"""
        # Adicionar estrutura de diagnóstico
        if not '## Diagnóstico' in response and not '## Solução' in response:
            sections = response.split('\n\n')
            if len(sections) >= 2:
                response = f"## Diagnóstico\n\n{sections[0]}\n\n## Solução\n\n{sections[1]}"
                if len(sections) > 2:
                    response += f"\n\n## Informações Adicionais\n\n{chr(10).join(sections[2:])}"
        
        return response
    
    def _format_code_review(self, response: str, context: QueryContext) -> str:
        """Formata resposta de code review"""
        # Estruturar feedback de code review
        if not '## Análise' in response:
            response = f"## Análise do Código\n\n{response}"
        
        return response
    
    def _format_generic(self, response: str, context: QueryContext) -> str:
        """Formatação genérica"""
        # Aplicar formatação básica
        if context.include_code_examples and '```' not in response:
            # Tentar identificar código inline e convertê-lo em blocos
            response = re.sub(
                r'`([^`\n]{20,})`',  # Código inline longo
                r'```\n\1\n```',
                response
            )
        
        return response