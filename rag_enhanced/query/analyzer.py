#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 Analysis Engine - Motor de análise avançada de código

Este módulo fornece análise profunda de código incluindo padrões,
qualidade, dependências e métricas de complexidade.
"""

import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
from datetime import datetime

from ..core.models import RAGConfig
from ..core.exceptions import ProcessingError


@dataclass
class CodePattern:
    """
    🎯 Padrão de código identificado
    """
    name: str
    type: str  # design_pattern, architectural_pattern, anti_pattern
    description: str
    examples: List[str]
    confidence: float
    locations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "examples": self.examples,
            "confidence": self.confidence,
            "locations": self.locations
        }


@dataclass
class QualityMetric:
    """
    📊 Métrica de qualidade de código
    """
    name: str
    value: float
    max_value: float
    description: str
    severity: str  # low, medium, high, critical
    suggestions: List[str]
    
    @property
    def score_percentage(self) -> float:
        """Score como percentual"""
        if self.max_value == 0:
            return 0.0
        return (self.value / self.max_value) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "max_value": self.max_value,
            "score_percentage": self.score_percentage,
            "description": self.description,
            "severity": self.severity,
            "suggestions": self.suggestions
        }


@dataclass
class DependencyNode:
    """
    🔗 Nó no grafo de dependências
    """
    name: str
    type: str  # module, class, function, file
    dependencies: Set[str]
    dependents: Set[str]
    complexity_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "complexity_score": self.complexity_score,
            "dependency_count": len(self.dependencies),
            "dependent_count": len(self.dependents)
        }


class AnalysisEngine:
    """
    🔬 Motor de análise avançada de código
    
    Fornece análise profunda incluindo:
    - Detecção de padrões de design
    - Análise de qualidade de código
    - Mapeamento de dependências
    - Métricas de complexidade
    - Identificação de code smells
    - Sugestões de refatoração
    """
    
    def __init__(self, config: RAGConfig):
        """
        Inicializa o motor de análise
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        
        # Padrões conhecidos
        self.design_patterns = self._load_design_patterns()
        self.anti_patterns = self._load_anti_patterns()
        
        # Cache de análises
        self.analysis_cache = {}
        
        # Estatísticas
        self.analysis_stats = {
            "files_analyzed": 0,
            "patterns_found": 0,
            "issues_detected": 0,
            "last_analysis": None
        }
    
    def analyze_patterns(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analisa padrões de código na base
        
        Args:
            focus_areas: Áreas específicas para focar a análise
            
        Returns:
            Análise de padrões encontrados
        """
        try:
            print("🔍 Analisando padrões de código...")
            
            # Coletar arquivos para análise
            files_to_analyze = self._collect_code_files(focus_areas)
            
            if not files_to_analyze:
                return {
                    "status": "no_files",
                    "message": "Nenhum arquivo de código encontrado para análise"
                }
            
            # Analisar cada arquivo
            all_patterns = []
            file_analyses = {}
            
            for file_path in files_to_analyze:
                try:
                    patterns = self._analyze_file_patterns(file_path)
                    all_patterns.extend(patterns)
                    file_analyses[str(file_path)] = patterns
                except Exception as e:
                    print(f"⚠️ Erro ao analisar {file_path}: {e}")
                    continue
            
            # Consolidar resultados
            pattern_summary = self._consolidate_patterns(all_patterns)
            
            # Gerar insights
            insights = self._generate_pattern_insights(pattern_summary, file_analyses)
            
            result = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "files_analyzed": len(file_analyses),
                "total_patterns": len(all_patterns),
                "pattern_summary": pattern_summary,
                "insights": insights,
                "recommendations": self._generate_pattern_recommendations(pattern_summary)
            }
            
            # Atualizar estatísticas
            self.analysis_stats.update({
                "files_analyzed": len(file_analyses),
                "patterns_found": len(all_patterns),
                "last_analysis": datetime.now()
            })
            
            return result
            
        except Exception as e:
            raise ProcessingError(
                operation="pattern_analysis",
                message=f"Erro na análise de padrões: {str(e)}",
                suggestion="Verifique se há arquivos de código válidos no diretório"
            )
    
    def assess_quality(self) -> Dict[str, Any]:
        """
        Avalia qualidade do código
        
        Returns:
            Avaliação de qualidade com métricas e recomendações
        """
        try:
            print("📊 Avaliando qualidade do código...")
            
            # Coletar arquivos
            files_to_analyze = self._collect_code_files()
            
            if not files_to_analyze:
                return {
                    "status": "no_files",
                    "message": "Nenhum arquivo encontrado para avaliação"
                }
            
            # Métricas de qualidade
            quality_metrics = []
            file_scores = {}
            
            for file_path in files_to_analyze:
                try:
                    metrics = self._analyze_file_quality(file_path)
                    quality_metrics.extend(metrics)
                    
                    # Calcular score do arquivo
                    file_score = self._calculate_file_quality_score(metrics)
                    file_scores[str(file_path)] = file_score
                    
                except Exception as e:
                    print(f"⚠️ Erro ao avaliar {file_path}: {e}")
                    continue
            
            # Consolidar métricas
            consolidated_metrics = self._consolidate_quality_metrics(quality_metrics)
            
            # Calcular score geral
            overall_score = self._calculate_overall_quality_score(consolidated_metrics)
            
            result = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "files_analyzed": len(file_scores),
                "overall_score": overall_score,
                "grade": self._score_to_grade(overall_score),
                "metrics": [metric.to_dict() for metric in consolidated_metrics],
                "file_scores": file_scores,
                "recommendations": self._generate_quality_recommendations(consolidated_metrics),
                "summary": self._generate_quality_summary(overall_score, consolidated_metrics)
            }
            
            return result
            
        except Exception as e:
            raise ProcessingError(
                operation="quality_assessment",
                message=f"Erro na avaliação de qualidade: {str(e)}",
                suggestion="Verifique se há arquivos de código válidos"
            )
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analisa dependências da base de código
        
        Returns:
            Análise de dependências e estrutura
        """
        try:
            print("🔗 Analisando dependências...")
            
            # Coletar arquivos
            files_to_analyze = self._collect_code_files()
            
            if not files_to_analyze:
                return {
                    "status": "no_files",
                    "message": "Nenhum arquivo encontrado para análise de dependências"
                }
            
            # Construir grafo de dependências
            dependency_graph = self._build_dependency_graph(files_to_analyze)
            
            # Analisar estrutura
            structure_analysis = self._analyze_dependency_structure(dependency_graph)
            
            # Detectar problemas
            issues = self._detect_dependency_issues(dependency_graph)
            
            # Calcular métricas
            metrics = self._calculate_dependency_metrics(dependency_graph)
            
            result = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "files_analyzed": len(files_to_analyze),
                "total_dependencies": sum(len(node.dependencies) for node in dependency_graph.values()),
                "dependency_graph": {name: node.to_dict() for name, node in dependency_graph.items()},
                "structure_analysis": structure_analysis,
                "issues": issues,
                "metrics": metrics,
                "recommendations": self._generate_dependency_recommendations(dependency_graph, issues)
            }
            
            return result
            
        except Exception as e:
            raise ProcessingError(
                operation="dependency_analysis",
                message=f"Erro na análise de dependências: {str(e)}",
                suggestion="Verifique se os arquivos são válidos e acessíveis"
            )
    
    def _collect_code_files(self, focus_areas: Optional[List[str]] = None) -> List[Path]:
        """Coleta arquivos de código para análise"""
        code_extensions = {'.py', '.java', '.js', '.ts', '.cpp', '.c', '.cs', '.rb', '.go', '.rs'}
        
        files = []
        base_path = self.config.codebase_path
        
        # Se há áreas de foco, filtrar por elas
        if focus_areas:
            for area in focus_areas:
                area_path = base_path / area
                if area_path.exists():
                    for file_path in area_path.rglob('*'):
                        if file_path.is_file() and file_path.suffix.lower() in code_extensions:
                            files.append(file_path)
        else:
            # Analisar toda a base
            for file_path in base_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in code_extensions:
                    files.append(file_path)
        
        return files[:100]  # Limitar para evitar análises muito longas
    
    def _analyze_file_patterns(self, file_path: Path) -> List[CodePattern]:
        """Analisa padrões em um arquivo específico"""
        patterns = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detectar padrões baseados na linguagem
            if file_path.suffix.lower() == '.py':
                patterns.extend(self._detect_python_patterns(content, file_path))
            elif file_path.suffix.lower() in ['.js', '.ts']:
                patterns.extend(self._detect_javascript_patterns(content, file_path))
            elif file_path.suffix.lower() == '.java':
                patterns.extend(self._detect_java_patterns(content, file_path))
            
            # Padrões genéricos
            patterns.extend(self._detect_generic_patterns(content, file_path))
            
        except Exception as e:
            print(f"Erro ao analisar padrões em {file_path}: {e}")
        
        return patterns
    
    def _detect_python_patterns(self, content: str, file_path: Path) -> List[CodePattern]:
        """Detecta padrões específicos do Python"""
        patterns = []
        
        try:
            tree = ast.parse(content)
            
            # Singleton Pattern
            if self._has_singleton_pattern(tree):
                patterns.append(CodePattern(
                    name="Singleton",
                    type="design_pattern",
                    description="Padrão Singleton detectado",
                    examples=["__new__ method override"],
                    confidence=0.8,
                    locations=[str(file_path)]
                ))
            
            # Factory Pattern
            if self._has_factory_pattern(tree):
                patterns.append(CodePattern(
                    name="Factory",
                    type="design_pattern",
                    description="Padrão Factory detectado",
                    examples=["create_* methods"],
                    confidence=0.7,
                    locations=[str(file_path)]
                ))
            
            # Observer Pattern
            if self._has_observer_pattern(tree):
                patterns.append(CodePattern(
                    name="Observer",
                    type="design_pattern",
                    description="Padrão Observer detectado",
                    examples=["notify, subscribe methods"],
                    confidence=0.6,
                    locations=[str(file_path)]
                ))
            
        except SyntaxError:
            pass  # Arquivo com erro de sintaxe
        
        return patterns
    
    def _detect_javascript_patterns(self, content: str, file_path: Path) -> List[CodePattern]:
        """Detecta padrões específicos do JavaScript/TypeScript"""
        patterns = []
        
        # Module Pattern
        if re.search(r'\(function\s*\([^)]*\)\s*{.*}\)\s*\([^)]*\)', content, re.DOTALL):
            patterns.append(CodePattern(
                name="Module Pattern",
                type="design_pattern",
                description="Padrão Module (IIFE) detectado",
                examples=["(function() { ... })()"],
                confidence=0.9,
                locations=[str(file_path)]
            ))
        
        # Prototype Pattern
        if re.search(r'\.prototype\s*=', content):
            patterns.append(CodePattern(
                name="Prototype",
                type="design_pattern",
                description="Padrão Prototype detectado",
                examples=[".prototype assignments"],
                confidence=0.8,
                locations=[str(file_path)]
            ))
        
        return patterns
    
    def _detect_java_patterns(self, content: str, file_path: Path) -> List[CodePattern]:
        """Detecta padrões específicos do Java"""
        patterns = []
        
        # Singleton Pattern
        if re.search(r'private\s+static.*getInstance\s*\(', content):
            patterns.append(CodePattern(
                name="Singleton",
                type="design_pattern",
                description="Padrão Singleton detectado",
                examples=["getInstance() method"],
                confidence=0.9,
                locations=[str(file_path)]
            ))
        
        # Builder Pattern
        if re.search(r'\.build\s*\(\s*\)', content) and re.search(r'public\s+\w+\s+\w+\s*\([^)]*\)\s*{[^}]*return\s+this', content):
            patterns.append(CodePattern(
                name="Builder",
                type="design_pattern",
                description="Padrão Builder detectado",
                examples=["fluent interface with build()"],
                confidence=0.8,
                locations=[str(file_path)]
            ))
        
        return patterns
    
    def _detect_generic_patterns(self, content: str, file_path: Path) -> List[CodePattern]:
        """Detecta padrões genéricos independentes de linguagem"""
        patterns = []
        
        # God Class (anti-pattern)
        lines = content.split('\n')
        if len(lines) > 500:  # Arquivo muito grande
            patterns.append(CodePattern(
                name="God Class",
                type="anti_pattern",
                description="Classe/arquivo muito grande detectado",
                examples=[f"{len(lines)} lines of code"],
                confidence=0.7,
                locations=[str(file_path)]
            ))
        
        # Magic Numbers (anti-pattern)
        magic_numbers = re.findall(r'\b(?<![\w.])\d{2,}\b(?![\w.])', content)
        if len(magic_numbers) > 5:
            patterns.append(CodePattern(
                name="Magic Numbers",
                type="anti_pattern",
                description="Muitos números mágicos detectados",
                examples=magic_numbers[:3],
                confidence=0.6,
                locations=[str(file_path)]
            ))
        
        return patterns
    
    def _analyze_file_quality(self, file_path: Path) -> List[QualityMetric]:
        """Analisa qualidade de um arquivo específico"""
        metrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Métrica: Tamanho do arquivo
            line_count = len(lines)
            metrics.append(QualityMetric(
                name="File Size",
                value=line_count,
                max_value=500,  # Limite recomendado
                description=f"Número de linhas no arquivo",
                severity="high" if line_count > 500 else "medium" if line_count > 200 else "low",
                suggestions=["Considere dividir em arquivos menores"] if line_count > 500 else []
            ))
            
            # Métrica: Complexidade ciclomática (aproximada)
            complexity = self._calculate_cyclomatic_complexity(content)
            metrics.append(QualityMetric(
                name="Cyclomatic Complexity",
                value=complexity,
                max_value=10,
                description="Complexidade ciclomática aproximada",
                severity="critical" if complexity > 15 else "high" if complexity > 10 else "medium" if complexity > 5 else "low",
                suggestions=["Refatore métodos complexos", "Use padrões de design"] if complexity > 10 else []
            ))
            
            # Métrica: Duplicação de código
            duplication = self._detect_code_duplication(content)
            metrics.append(QualityMetric(
                name="Code Duplication",
                value=duplication,
                max_value=20,
                description="Percentual de código duplicado",
                severity="high" if duplication > 20 else "medium" if duplication > 10 else "low",
                suggestions=["Extraia métodos comuns", "Use herança ou composição"] if duplication > 10 else []
            ))
            
            # Métrica: Cobertura de comentários
            comment_coverage = self._calculate_comment_coverage(content)
            metrics.append(QualityMetric(
                name="Comment Coverage",
                value=comment_coverage,
                max_value=100,
                description="Percentual de linhas com comentários",
                severity="medium" if comment_coverage < 10 else "low",
                suggestions=["Adicione mais comentários explicativos"] if comment_coverage < 10 else []
            ))
            
        except Exception as e:
            print(f"Erro ao analisar qualidade de {file_path}: {e}")
        
        return metrics
    
    def _build_dependency_graph(self, files: List[Path]) -> Dict[str, DependencyNode]:
        """Constrói grafo de dependências"""
        graph = {}
        
        for file_path in files:
            try:
                dependencies = self._extract_file_dependencies(file_path)
                
                node_name = str(file_path.relative_to(self.config.codebase_path))
                node = DependencyNode(
                    name=node_name,
                    type="file",
                    dependencies=set(dependencies),
                    dependents=set()
                )
                
                graph[node_name] = node
                
            except Exception as e:
                print(f"Erro ao processar dependências de {file_path}: {e}")
                continue
        
        # Calcular dependentes (reverse dependencies)
        for node_name, node in graph.items():
            for dep in node.dependencies:
                if dep in graph:
                    graph[dep].dependents.add(node_name)
        
        return graph
    
    def _extract_file_dependencies(self, file_path: Path) -> List[str]:
        """Extrai dependências de um arquivo"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Python imports
            if file_path.suffix.lower() == '.py':
                imports = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', content)
                for imp in imports:
                    dep = imp[0] or imp[1]
                    if dep and not dep.startswith('.'):  # Ignorar imports relativos
                        dependencies.append(dep.split('.')[0])
            
            # JavaScript/TypeScript imports
            elif file_path.suffix.lower() in ['.js', '.ts']:
                imports = re.findall(r'(?:import.*from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\))', content)
                for imp in imports:
                    dep = imp[0] or imp[1]
                    if dep and not dep.startswith('.'):
                        dependencies.append(dep)
            
            # Java imports
            elif file_path.suffix.lower() == '.java':
                imports = re.findall(r'import\s+([^;]+);', content)
                for imp in imports:
                    if not imp.startswith('java.'):  # Ignorar imports padrão
                        dependencies.append(imp.split('.')[0])
        
        except Exception:
            pass
        
        return dependencies
    
    def _has_singleton_pattern(self, tree: ast.AST) -> bool:
        """Detecta padrão Singleton em AST Python"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == '__new__':
                return True
        return False
    
    def _has_factory_pattern(self, tree: ast.AST) -> bool:
        """Detecta padrão Factory em AST Python"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('create_'):
                return True
        return False
    
    def _has_observer_pattern(self, tree: ast.AST) -> bool:
        """Detecta padrão Observer em AST Python"""
        methods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                methods.add(node.name)
        
        observer_methods = {'notify', 'subscribe', 'unsubscribe', 'add_observer', 'remove_observer'}
        return len(observer_methods.intersection(methods)) >= 2
    
    def _calculate_cyclomatic_complexity(self, content: str) -> int:
        """Calcula complexidade ciclomática aproximada"""
        # Contar estruturas de controle
        control_structures = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bwhile\b', r'\bfor\b',
            r'\btry\b', r'\bcatch\b', r'\bexcept\b', r'\bswitch\b', r'\bcase\b'
        ]
        
        complexity = 1  # Complexidade base
        
        for pattern in control_structures:
            matches = re.findall(pattern, content, re.IGNORECASE)
            complexity += len(matches)
        
        return complexity
    
    def _detect_code_duplication(self, content: str) -> float:
        """Detecta duplicação de código (aproximada)"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 10:
            return 0.0
        
        # Contar linhas duplicadas
        line_counts = Counter(lines)
        duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        
        return (duplicated_lines / len(lines)) * 100
    
    def _calculate_comment_coverage(self, content: str) -> float:
        """Calcula cobertura de comentários"""
        lines = content.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines == 0:
            return 0.0
        
        # Contar linhas com comentários (aproximado)
        comment_patterns = [r'#', r'//', r'/\*', r'\*', r'"""', r"'''"]
        comment_lines = 0
        
        for line in lines:
            if any(re.search(pattern, line) for pattern in comment_patterns):
                comment_lines += 1
        
        return (comment_lines / total_lines) * 100
    
    def _consolidate_patterns(self, patterns: List[CodePattern]) -> Dict[str, Any]:
        """Consolida padrões encontrados"""
        pattern_counts = defaultdict(int)
        pattern_types = defaultdict(int)
        
        for pattern in patterns:
            pattern_counts[pattern.name] += 1
            pattern_types[pattern.type] += 1
        
        return {
            "total_patterns": len(patterns),
            "unique_patterns": len(pattern_counts),
            "pattern_counts": dict(pattern_counts),
            "pattern_types": dict(pattern_types),
            "most_common": pattern_counts.most_common(5)
        }
    
    def _consolidate_quality_metrics(self, metrics: List[QualityMetric]) -> List[QualityMetric]:
        """Consolida métricas de qualidade"""
        metric_groups = defaultdict(list)
        
        # Agrupar métricas por nome
        for metric in metrics:
            metric_groups[metric.name].append(metric)
        
        # Calcular médias
        consolidated = []
        for name, group in metric_groups.items():
            avg_value = sum(m.value for m in group) / len(group)
            max_value = group[0].max_value
            
            # Determinar severidade baseada na média
            severities = [m.severity for m in group]
            severity_priority = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            avg_severity = max(severities, key=lambda s: severity_priority.get(s, 0))
            
            # Combinar sugestões
            all_suggestions = []
            for m in group:
                all_suggestions.extend(m.suggestions)
            unique_suggestions = list(set(all_suggestions))
            
            consolidated.append(QualityMetric(
                name=name,
                value=avg_value,
                max_value=max_value,
                description=group[0].description,
                severity=avg_severity,
                suggestions=unique_suggestions
            ))
        
        return consolidated
    
    def _calculate_overall_quality_score(self, metrics: List[QualityMetric]) -> float:
        """Calcula score geral de qualidade"""
        if not metrics:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        # Pesos por tipo de métrica
        weights = {
            "File Size": 0.2,
            "Cyclomatic Complexity": 0.3,
            "Code Duplication": 0.3,
            "Comment Coverage": 0.2
        }
        
        for metric in metrics:
            weight = weights.get(metric.name, 0.1)
            
            # Inverter score para métricas onde menor é melhor
            if metric.name in ["File Size", "Cyclomatic Complexity", "Code Duplication"]:
                score = max(0, 100 - metric.score_percentage)
            else:
                score = metric.score_percentage
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _score_to_grade(self, score: float) -> str:
        """Converte score numérico para nota"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_pattern_insights(self, summary: Dict[str, Any], file_analyses: Dict) -> List[str]:
        """Gera insights sobre padrões"""
        insights = []
        
        if summary["total_patterns"] == 0:
            insights.append("Nenhum padrão de design detectado. Considere aplicar padrões para melhorar a arquitetura.")
        else:
            insights.append(f"Detectados {summary['total_patterns']} padrões em {len(file_analyses)} arquivos.")
        
        # Insights sobre tipos de padrões
        pattern_types = summary.get("pattern_types", {})
        if "anti_pattern" in pattern_types:
            insights.append(f"⚠️ Encontrados {pattern_types['anti_pattern']} anti-padrões que precisam de atenção.")
        
        if "design_pattern" in pattern_types:
            insights.append(f"✅ Bom uso de {pattern_types['design_pattern']} padrões de design.")
        
        return insights
    
    def _generate_pattern_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos padrões"""
        recommendations = []
        
        pattern_types = summary.get("pattern_types", {})
        
        if pattern_types.get("anti_pattern", 0) > pattern_types.get("design_pattern", 0):
            recommendations.append("Refatore código para eliminar anti-padrões detectados")
        
        if summary["total_patterns"] < 5:
            recommendations.append("Considere aplicar mais padrões de design para melhorar a arquitetura")
        
        return recommendations
    
    def _generate_quality_recommendations(self, metrics: List[QualityMetric]) -> List[str]:
        """Gera recomendações de qualidade"""
        recommendations = []
        
        for metric in metrics:
            if metric.severity in ["high", "critical"]:
                recommendations.extend(metric.suggestions)
        
        return list(set(recommendations))  # Remove duplicatas
    
    def _generate_quality_summary(self, score: float, metrics: List[QualityMetric]) -> str:
        """Gera resumo da qualidade"""
        grade = self._score_to_grade(score)
        
        critical_issues = len([m for m in metrics if m.severity == "critical"])
        high_issues = len([m for m in metrics if m.severity == "high"])
        
        summary = f"Qualidade geral: {grade} ({score:.1f}/100). "
        
        if critical_issues > 0:
            summary += f"{critical_issues} problemas críticos encontrados. "
        
        if high_issues > 0:
            summary += f"{high_issues} problemas de alta prioridade. "
        
        if score >= 80:
            summary += "Código em boa qualidade!"
        elif score >= 60:
            summary += "Código precisa de algumas melhorias."
        else:
            summary += "Código precisa de refatoração significativa."
        
        return summary
    
    def _analyze_dependency_structure(self, graph: Dict[str, DependencyNode]) -> Dict[str, Any]:
        """Analisa estrutura de dependências"""
        if not graph:
            return {"status": "empty"}
        
        # Calcular métricas básicas
        total_nodes = len(graph)
        total_edges = sum(len(node.dependencies) for node in graph.values())
        
        # Encontrar nós mais conectados
        most_dependencies = max(graph.values(), key=lambda n: len(n.dependencies))
        most_dependents = max(graph.values(), key=lambda n: len(n.dependents))
        
        # Detectar ciclos (simplificado)
        cycles = self._detect_dependency_cycles(graph)
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "density": total_edges / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0,
            "most_dependencies": {
                "name": most_dependencies.name,
                "count": len(most_dependencies.dependencies)
            },
            "most_dependents": {
                "name": most_dependents.name,
                "count": len(most_dependents.dependents)
            },
            "cycles_detected": len(cycles),
            "cycles": cycles[:5]  # Mostrar apenas os primeiros 5
        }
    
    def _detect_dependency_cycles(self, graph: Dict[str, DependencyNode]) -> List[List[str]]:
        """Detecta ciclos de dependência (algoritmo simplificado)"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_name: str, path: List[str]) -> None:
            if node_name in rec_stack:
                # Ciclo detectado
                cycle_start = path.index(node_name)
                cycle = path[cycle_start:] + [node_name]
                cycles.append(cycle)
                return
            
            if node_name in visited:
                return
            
            visited.add(node_name)
            rec_stack.add(node_name)
            
            if node_name in graph:
                for dep in graph[node_name].dependencies:
                    if dep in graph:  # Apenas dependências internas
                        dfs(dep, path + [node_name])
            
            rec_stack.remove(node_name)
        
        for node_name in graph:
            if node_name not in visited:
                dfs(node_name, [])
        
        return cycles
    
    def _detect_dependency_issues(self, graph: Dict[str, DependencyNode]) -> List[Dict[str, Any]]:
        """Detecta problemas nas dependências"""
        issues = []
        
        for node_name, node in graph.items():
            # Muitas dependências
            if len(node.dependencies) > 10:
                issues.append({
                    "type": "high_coupling",
                    "severity": "high",
                    "node": node_name,
                    "description": f"Arquivo tem {len(node.dependencies)} dependências",
                    "suggestion": "Considere dividir em módulos menores"
                })
            
            # Muitos dependentes
            if len(node.dependents) > 15:
                issues.append({
                    "type": "high_fan_in",
                    "severity": "medium",
                    "node": node_name,
                    "description": f"Arquivo é usado por {len(node.dependents)} outros arquivos",
                    "suggestion": "Verifique se não é um God Object"
                })
        
        return issues
    
    def _calculate_dependency_metrics(self, graph: Dict[str, DependencyNode]) -> Dict[str, float]:
        """Calcula métricas de dependência"""
        if not graph:
            return {}
        
        # Métricas básicas
        total_nodes = len(graph)
        total_dependencies = sum(len(node.dependencies) for node in graph.values())
        
        # Instabilidade média (dependencies / (dependencies + dependents))
        instabilities = []
        for node in graph.values():
            total_connections = len(node.dependencies) + len(node.dependents)
            if total_connections > 0:
                instability = len(node.dependencies) / total_connections
                instabilities.append(instability)
        
        avg_instability = sum(instabilities) / len(instabilities) if instabilities else 0
        
        return {
            "average_dependencies": total_dependencies / total_nodes,
            "average_instability": avg_instability,
            "coupling_factor": total_dependencies / (total_nodes ** 2) if total_nodes > 0 else 0
        }
    
    def _generate_dependency_recommendations(self, 
                                          graph: Dict[str, DependencyNode], 
                                          issues: List[Dict]) -> List[str]:
        """Gera recomendações para dependências"""
        recommendations = []
        
        # Baseado nos problemas encontrados
        high_coupling_count = len([i for i in issues if i["type"] == "high_coupling"])
        if high_coupling_count > 0:
            recommendations.append(f"Refatore {high_coupling_count} arquivos com alto acoplamento")
        
        # Baseado na estrutura geral
        if len(graph) > 50:
            recommendations.append("Considere organizar código em módulos ou pacotes")
        
        return recommendations
    
    def _load_design_patterns(self) -> Dict[str, Dict]:
        """Carrega definições de padrões de design"""
        return {
            "singleton": {
                "description": "Garante uma única instância de uma classe",
                "indicators": ["__new__", "getInstance", "instance"]
            },
            "factory": {
                "description": "Cria objetos sem especificar suas classes exatas",
                "indicators": ["create", "make", "build"]
            },
            "observer": {
                "description": "Define dependência um-para-muitos entre objetos",
                "indicators": ["notify", "subscribe", "observer"]
            }
        }
    
    def _load_anti_patterns(self) -> Dict[str, Dict]:
        """Carrega definições de anti-padrões"""
        return {
            "god_class": {
                "description": "Classe que faz muitas coisas",
                "indicators": ["large_file", "many_methods"]
            },
            "magic_numbers": {
                "description": "Números literais sem explicação",
                "indicators": ["numeric_literals"]
            }
        }
    
    def _calculate_file_quality_score(self, metrics: List[QualityMetric]) -> float:
        """Calcula score de qualidade para um arquivo"""
        if not metrics:
            return 0.0
        
        scores = []
        for metric in metrics:
            if metric.name in ["File Size", "Cyclomatic Complexity", "Code Duplication"]:
                # Para estas métricas, menor é melhor
                score = max(0, 100 - metric.score_percentage)
            else:
                score = metric.score_percentage
            
            scores.append(score)
        
        return sum(scores) / len(scores)