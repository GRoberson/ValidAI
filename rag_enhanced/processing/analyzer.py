#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 File Analyzer - Análise inteligente de arquivos

Este módulo fornece análise avançada de arquivos com detecção automática
de linguagens, categorização e estimativa de requisitos de processamento.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import chardet
import hashlib
from datetime import datetime

from ..core.models import RAGConfig, FileAnalysis, CodebaseAnalysis
from ..core.exceptions import ProcessingError


class FileAnalyzer:
    """
    🔍 Analisador inteligente de arquivos
    
    Fornece análise detalhada de arquivos incluindo:
    - Detecção automática de linguagem de programação
    - Análise de encoding e estrutura
    - Categorização por tipo e complexidade
    - Estimativa de requisitos de processamento
    """
    
    def __init__(self, config: RAGConfig):
        """
        Inicializa o analisador
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        
        # Mapeamentos de extensões para linguagens
        self.extension_to_language = {
            # Linguagens principais
            ".py": "Python",
            ".java": "Java", 
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".go": "Go",
            ".c": "C",
            ".cpp": "C++",
            ".cxx": "C++",
            ".cc": "C++",
            ".h": "C/C++ Header",
            ".hpp": "C++ Header",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".rs": "Rust",
            ".dart": "Dart",
            
            # Linguagens funcionais
            ".hs": "Haskell",
            ".elm": "Elm",
            ".clj": "Clojure",
            ".cljs": "ClojureScript",
            ".ex": "Elixir",
            ".exs": "Elixir",
            ".erl": "Erlang",
            ".ml": "OCaml",
            ".fs": "F#",
            ".jl": "Julia",
            ".r": "R",
            ".R": "R",
            ".lua": "Lua",
            
            # Web e frontend
            ".html": "HTML",
            ".htm": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "Sass",
            ".less": "Less",
            ".vue": "Vue.js",
            ".svelte": "Svelte",
            ".jsx": "React JSX",
            ".tsx": "React TSX",
            
            # Mobile
            ".m": "Objective-C",
            ".mm": "Objective-C++",
            ".xaml": "XAML",
            
            # Configuração e dados
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".xml": "XML",
            ".toml": "TOML",
            ".ini": "INI",
            ".cfg": "Config",
            ".conf": "Config",
            
            # Documentação
            ".md": "Markdown",
            ".txt": "Text",
            ".rst": "reStructuredText",
            ".adoc": "AsciiDoc",
            ".tex": "LaTeX",
            
            # Scripts
            ".sh": "Shell Script",
            ".bash": "Bash Script",
            ".zsh": "Zsh Script",
            ".fish": "Fish Script",
            ".ps1": "PowerShell",
            ".bat": "Batch",
            ".cmd": "Command Script",
            
            # Banco de dados
            ".sql": "SQL",
            ".hql": "HiveQL",
            
            # Notebooks
            ".ipynb": "Jupyter Notebook",
            ".rmd": "R Markdown",
        }
        
        # Arquivos especiais sem extensão
        self.special_files = {
            "Dockerfile": "Docker",
            "Makefile": "Makefile",
            "Rakefile": "Ruby Rakefile",
            "Gemfile": "Ruby Gemfile",
            "Pipfile": "Python Pipfile",
            "requirements.txt": "Python Requirements",
            "package.json": "Node.js Package",
            "composer.json": "PHP Composer",
            "Cargo.toml": "Rust Cargo",
            "go.mod": "Go Module",
            "pom.xml": "Maven POM",
            "build.gradle": "Gradle Build",
            ".gitignore": "Git Ignore",
            ".gitattributes": "Git Attributes",
            "README": "README",
            "LICENSE": "License",
            "CHANGELOG": "Changelog",
        }
        
        # Categorias de complexidade
        self.complexity_categories = {
            "simple": ["txt", "md", "json", "yaml", "yml", "xml", "ini", "cfg"],
            "medium": ["py", "js", "ts", "rb", "php", "go", "cs", "kt"],
            "complex": ["java", "cpp", "c", "scala", "rs", "hs", "ml"],
            "special": ["ipynb", "html", "css", "scss", "vue", "svelte"]
        }
    
    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """
        Analisa um arquivo individual
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Análise detalhada do arquivo
            
        Raises:
            ProcessingError: Se não conseguir analisar o arquivo
        """
        try:
            if not file_path.exists():
                raise ProcessingError(
                    operation="file_analysis",
                    message="Arquivo não encontrado",
                    file_path=str(file_path)
                )
            
            if not file_path.is_file():
                raise ProcessingError(
                    operation="file_analysis", 
                    message="Caminho não é um arquivo",
                    file_path=str(file_path)
                )
            
            # Informações básicas
            stat = file_path.stat()
            size_bytes = stat.st_size
            
            # Detectar tipo e linguagem
            file_type, language = self._detect_language(file_path)
            
            # Verificar se é suportado
            is_supported, skip_reason = self._is_file_supported(file_path, size_bytes)
            
            # Detectar encoding (apenas para arquivos de texto)
            encoding = self._detect_encoding(file_path) if is_supported else "unknown"
            
            # Contar linhas (apenas para arquivos de texto pequenos)
            line_count = self._count_lines(file_path) if is_supported and size_bytes < 1024*1024 else None
            
            return FileAnalysis(
                path=file_path,
                size_bytes=size_bytes,
                file_type=file_type,
                language=language,
                encoding=encoding,
                line_count=line_count,
                is_supported=is_supported,
                skip_reason=skip_reason
            )
            
        except Exception as e:
            if isinstance(e, ProcessingError):
                raise
            raise ProcessingError(
                operation="file_analysis",
                message=f"Erro ao analisar arquivo: {str(e)}",
                file_path=str(file_path)
            )
    
    def analyze_codebase(self, codebase_path: Path, max_files: int = 10000) -> CodebaseAnalysis:
        """
        Analisa uma base de código completa
        
        Args:
            codebase_path: Caminho da base de código
            max_files: Máximo de arquivos a analisar
            
        Returns:
            Análise completa da base de código
        """
        start_time = datetime.now()
        
        try:
            if not codebase_path.exists():
                raise ProcessingError(
                    operation="codebase_analysis",
                    message="Diretório da base de código não encontrado",
                    file_path=str(codebase_path)
                )
            
            # Contadores e estatísticas
            total_files = 0
            supported_files = 0
            total_size_bytes = 0
            language_count = {}
            file_type_count = {}
            largest_files = []
            
            # Analisar arquivos
            for file_path in codebase_path.rglob('*'):
                if total_files >= max_files:
                    break
                
                if not file_path.is_file():
                    continue
                
                try:
                    analysis = self.analyze_file(file_path)
                    total_files += 1
                    total_size_bytes += analysis.size_bytes
                    
                    # Contar por tipo
                    file_type_count[analysis.file_type] = file_type_count.get(analysis.file_type, 0) + 1
                    
                    if analysis.is_supported:
                        supported_files += 1
                        
                        # Contar por linguagem
                        if analysis.language:
                            language_count[analysis.language] = language_count.get(analysis.language, 0) + 1
                        
                        # Manter lista dos maiores arquivos
                        largest_files.append(analysis)
                        largest_files.sort(key=lambda x: x.size_bytes, reverse=True)
                        largest_files = largest_files[:10]  # Manter apenas os 10 maiores
                
                except Exception:
                    # Ignorar arquivos que não conseguimos analisar
                    total_files += 1
                    continue
            
            # Calcular tempo de análise
            analysis_time = (datetime.now() - start_time).total_seconds()
            
            return CodebaseAnalysis(
                total_files=total_files,
                supported_files=supported_files,
                total_size_mb=total_size_bytes / (1024 * 1024),
                language_distribution=dict(sorted(language_count.items(), key=lambda x: x[1], reverse=True)),
                file_type_distribution=dict(sorted(file_type_count.items(), key=lambda x: x[1], reverse=True)),
                largest_files=largest_files,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            if isinstance(e, ProcessingError):
                raise
            raise ProcessingError(
                operation="codebase_analysis",
                message=f"Erro ao analisar base de código: {str(e)}",
                file_path=str(codebase_path)
            )
    
    def get_processing_estimate(self, analysis: CodebaseAnalysis) -> Dict[str, Any]:
        """
        Estima requisitos de processamento baseado na análise
        
        Args:
            analysis: Análise da base de código
            
        Returns:
            Estimativas de processamento
        """
        # Estimativas baseadas em experiência
        avg_processing_time_per_mb = 30  # segundos por MB
        avg_upload_time_per_mb = 10      # segundos por MB (depende da conexão)
        
        # Calcular estimativas
        estimated_upload_time = analysis.total_size_mb * avg_upload_time_per_mb
        estimated_processing_time = analysis.total_size_mb * avg_processing_time_per_mb
        
        # Ajustar baseado no número de arquivos paralelos
        parallel_factor = min(self.config.parallel_uploads, 10) / 10
        estimated_upload_time *= (1 - parallel_factor * 0.5)  # Redução por paralelismo
        
        # Estimar custos (aproximados)
        # Baseado em preços do Vertex AI (valores aproximados)
        embedding_cost_per_1k_tokens = 0.00002  # USD
        generation_cost_per_1k_tokens = 0.0005   # USD
        
        # Estimar tokens (aproximadamente 4 caracteres por token)
        estimated_tokens = (analysis.total_size_mb * 1024 * 1024) / 4
        estimated_embedding_cost = (estimated_tokens / 1000) * embedding_cost_per_1k_tokens
        
        return {
            "files_to_process": analysis.supported_files,
            "total_size_mb": analysis.total_size_mb,
            "estimated_upload_time_minutes": estimated_upload_time / 60,
            "estimated_processing_time_minutes": estimated_processing_time / 60,
            "estimated_total_time_minutes": (estimated_upload_time + estimated_processing_time) / 60,
            "estimated_tokens": int(estimated_tokens),
            "estimated_embedding_cost_usd": estimated_embedding_cost,
            "complexity_score": self._calculate_complexity_score(analysis),
            "recommendations": self._generate_recommendations(analysis)
        }
    
    def filter_files_by_criteria(self, files: List[Path], criteria: Dict[str, Any]) -> List[Path]:
        """
        Filtra arquivos baseado em critérios específicos
        
        Args:
            files: Lista de arquivos
            criteria: Critérios de filtro
            
        Returns:
            Lista de arquivos filtrados
        """
        filtered = []
        
        for file_path in files:
            try:
                analysis = self.analyze_file(file_path)
                
                # Aplicar filtros
                if not analysis.is_supported:
                    continue
                
                # Filtro por tamanho
                if "max_size_mb" in criteria:
                    if analysis.size_mb > criteria["max_size_mb"]:
                        continue
                
                # Filtro por linguagem
                if "languages" in criteria:
                    if analysis.language not in criteria["languages"]:
                        continue
                
                # Filtro por tipo
                if "file_types" in criteria:
                    if analysis.file_type not in criteria["file_types"]:
                        continue
                
                # Filtro por padrão de nome
                if "name_patterns" in criteria:
                    matches_pattern = False
                    for pattern in criteria["name_patterns"]:
                        if pattern in file_path.name.lower():
                            matches_pattern = True
                            break
                    if not matches_pattern:
                        continue
                
                filtered.append(file_path)
                
            except Exception:
                continue  # Ignorar arquivos com erro
        
        return filtered
    
    def _detect_language(self, file_path: Path) -> Tuple[str, Optional[str]]:
        """Detecta linguagem de programação do arquivo"""
        # Verificar arquivos especiais primeiro
        file_name = file_path.name
        if file_name in self.special_files:
            return self.special_files[file_name], self.special_files[file_name]
        
        # Verificar por extensão
        extension = file_path.suffix.lower()
        if extension in self.extension_to_language:
            language = self.extension_to_language[extension]
            return extension[1:], language  # Remove o ponto da extensão
        
        # Tentar detectar por conteúdo (para arquivos sem extensão)
        if not extension:
            detected_type = self._detect_by_content(file_path)
            if detected_type:
                return detected_type, detected_type
        
        # Usar mimetype como fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('text/'):
                return "text", "Text"
            elif mime_type.startswith('application/'):
                return mime_type.split('/')[-1], mime_type.split('/')[-1].title()
        
        return "unknown", None
    
    def _detect_by_content(self, file_path: Path) -> Optional[str]:
        """Detecta tipo por conteúdo do arquivo"""
        try:
            # Ler apenas as primeiras linhas
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = []
                for i, line in enumerate(f):
                    if i >= 10:  # Ler apenas as primeiras 10 linhas
                        break
                    first_lines.append(line.strip())
            
            content = '\n'.join(first_lines).lower()
            
            # Detectar por shebang
            if first_lines and first_lines[0].startswith('#!'):
                shebang = first_lines[0]
                if 'python' in shebang:
                    return "Python"
                elif 'node' in shebang or 'javascript' in shebang:
                    return "JavaScript"
                elif 'ruby' in shebang:
                    return "Ruby"
                elif 'bash' in shebang or 'sh' in shebang:
                    return "Shell Script"
            
            # Detectar por palavras-chave
            if any(keyword in content for keyword in ['def ', 'import ', 'from ', 'class ']):
                return "Python"
            elif any(keyword in content for keyword in ['function ', 'var ', 'let ', 'const ']):
                return "JavaScript"
            elif any(keyword in content for keyword in ['public class', 'private class', 'package ']):
                return "Java"
            elif '<?php' in content:
                return "PHP"
            
        except Exception:
            pass
        
        return None
    
    def _is_file_supported(self, file_path: Path, size_bytes: int) -> Tuple[bool, Optional[str]]:
        """Verifica se arquivo é suportado"""
        # Verificar extensão
        extension = file_path.suffix.lower()
        file_name = file_path.name
        
        # Verificar se está na lista de extensões suportadas ou arquivos especiais
        if extension not in self.config.supported_extensions and file_name not in self.special_files:
            return False, f"Extensão '{extension}' não suportada"
        
        # Verificar tamanho
        max_size_bytes = self.config.max_file_size_mb * 1024 * 1024
        if max_size_bytes > 0 and size_bytes > max_size_bytes:
            return False, f"Arquivo muito grande ({size_bytes / (1024*1024):.1f} MB > {self.config.max_file_size_mb} MB)"
        
        # Verificar se é arquivo binário (heurística simples)
        if self._is_likely_binary(file_path):
            return False, "Arquivo binário detectado"
        
        return True, None
    
    def _is_likely_binary(self, file_path: Path) -> bool:
        """Verifica se arquivo é provavelmente binário"""
        try:
            # Ler uma pequena amostra
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
            
            # Verificar por bytes nulos (indicativo de arquivo binário)
            if b'\x00' in sample:
                return True
            
            # Verificar proporção de caracteres não-ASCII
            try:
                sample.decode('utf-8')
                return False
            except UnicodeDecodeError:
                # Tentar outros encodings comuns
                for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                    try:
                        sample.decode(encoding)
                        return False
                    except UnicodeDecodeError:
                        continue
                return True
        
        except Exception:
            return True  # Se não conseguir ler, assumir que é binário
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detecta encoding do arquivo"""
        try:
            # Ler amostra do arquivo
            with open(file_path, 'rb') as f:
                sample = f.read(10000)  # Ler até 10KB
            
            # Usar chardet para detectar encoding
            result = chardet.detect(sample)
            
            if result and result['confidence'] > 0.7:
                return result['encoding']
            
            # Fallback para UTF-8
            return 'utf-8'
            
        except Exception:
            return 'unknown'
    
    def _count_lines(self, file_path: Path) -> Optional[int]:
        """Conta linhas do arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return None
    
    def _calculate_complexity_score(self, analysis: CodebaseAnalysis) -> float:
        """Calcula score de complexidade da base de código"""
        score = 0.0
        
        # Baseado no número de arquivos
        if analysis.total_files > 1000:
            score += 3.0
        elif analysis.total_files > 100:
            score += 2.0
        elif analysis.total_files > 10:
            score += 1.0
        
        # Baseado no tamanho
        if analysis.total_size_mb > 100:
            score += 3.0
        elif analysis.total_size_mb > 10:
            score += 2.0
        elif analysis.total_size_mb > 1:
            score += 1.0
        
        # Baseado na diversidade de linguagens
        num_languages = len(analysis.language_distribution)
        if num_languages > 10:
            score += 2.0
        elif num_languages > 5:
            score += 1.0
        
        # Baseado na complexidade das linguagens
        complex_languages = ["C++", "Java", "Scala", "Haskell", "Rust"]
        for lang in analysis.language_distribution:
            if lang in complex_languages:
                score += 0.5
        
        return min(score, 10.0)  # Máximo 10
    
    def _generate_recommendations(self, analysis: CodebaseAnalysis) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações baseadas no tamanho
        if analysis.total_size_mb > 50:
            recommendations.append("Base de código grande detectada. Considere filtrar apenas os diretórios mais importantes.")
        
        if analysis.supported_files < analysis.total_files * 0.5:
            recommendations.append("Muitos arquivos não suportados. Considere adicionar mais extensões à configuração.")
        
        # Recomendações baseadas nas linguagens
        if "JavaScript" in analysis.language_distribution and "TypeScript" in analysis.language_distribution:
            recommendations.append("Projeto JavaScript/TypeScript detectado. Considere focar apenas nos arquivos .ts para melhor análise.")
        
        if len(analysis.language_distribution) > 5:
            recommendations.append("Múltiplas linguagens detectadas. Considere analisar cada linguagem separadamente para melhores resultados.")
        
        # Recomendações de performance
        if analysis.total_files > 1000:
            recommendations.append("Muitos arquivos detectados. Aumente o número de uploads paralelos para melhor performance.")
        
        return recommendations