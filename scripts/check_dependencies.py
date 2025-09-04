#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Verificador de Dependências - RAG Enhanced

Script para verificar se todas as dependências necessárias
estão instaladas e funcionando corretamente.
"""

import sys
import importlib
import subprocess
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DependencyCheck:
    """Resultado da verificação de uma dependência"""
    name: str
    required: bool
    installed: bool
    version: Optional[str] = None
    error: Optional[str] = None
    category: str = "core"


class DependencyChecker:
    """
    🔍 Verificador completo de dependências
    
    Verifica todas as dependências do projeto RAG Enhanced
    e fornece relatório detalhado do status.
    """
    
    def __init__(self):
        """Inicializa o verificador"""
        self.results: List[DependencyCheck] = []
        
        # Definir dependências por categoria
        self.dependencies = {
            "core": {
                # Google Cloud e AI
                "google.cloud.storage": True,
                "google.genai": True, 
                "vertexai": True,
                
                # Interface
                "gradio": True,
                
                # Processamento
                "pandas": True,
                "yaml": True,
                "pydantic": True,
                
                # Utilitários
                "requests": True,
                "pathlib": False,  # Built-in no Python 3.4+
            },
            
            "optional": {
                # Análise avançada
                "numpy": False,
                "matplotlib": False,
                "seaborn": False,
                "plotly": False,
                
                # Processamento de texto
                "nltk": False,
                "spacy": False,
                
                # Imagens
                "PIL": False,
                "cv2": False,
                
                # Documentos
                "docx": False,
                "PyPDF2": False,
                
                # Excel
                "openpyxl": False,
            },
            
            "development": {
                # Testes
                "pytest": False,
                "unittest": False,  # Built-in
                
                # Linting
                "flake8": False,
                "pylint": False,
                "black": False,
                "mypy": False,
                
                # Debugging
                "psutil": False,
                "memory_profiler": False,
                
                # Documentação
                "sphinx": False,
                "mkdocs": False,
            },
            
            "system": {
                # Monitoramento
                "psutil": False,
                
                # Async
                "asyncio": False,  # Built-in no Python 3.4+
                "aiohttp": False,
                "aiofiles": False,
                
                # CLI
                "click": False,
                "typer": False,
                "rich": False,
                "colorama": False,
            }
        }
    
    def check_all_dependencies(self) -> Dict[str, List[DependencyCheck]]:
        """
        Verifica todas as dependências
        
        Returns:
            Resultados organizados por categoria
        """
        print("🔍 Verificando Dependências do RAG Enhanced")
        print("=" * 60)
        
        results_by_category = {}
        
        for category, deps in self.dependencies.items():
            print(f"\n📦 Categoria: {category.title()}")
            print("-" * 40)
            
            category_results = []
            
            for dep_name, is_required in deps.items():
                result = self._check_single_dependency(dep_name, is_required, category)
                category_results.append(result)
                self.results.append(result)
                
                # Exibir resultado
                status = "✅" if result.installed else "❌" if result.required else "⚠️"
                req_text = "(obrigatória)" if result.required else "(opcional)"
                version_text = f" v{result.version}" if result.version else ""
                
                print(f"  {status} {result.name}{version_text} {req_text}")
                
                if result.error and not result.installed:
                    print(f"      💡 {result.error}")
            
            results_by_category[category] = category_results
        
        return results_by_category
    
    def _check_single_dependency(self, name: str, required: bool, category: str) -> DependencyCheck:
        """Verifica uma dependência específica"""
        try:
            # Tentar importar o módulo
            module = importlib.import_module(name)
            
            # Tentar obter versão
            version = None
            for attr in ['__version__', 'version', 'VERSION']:
                if hasattr(module, attr):
                    version = getattr(module, attr)
                    if isinstance(version, str):
                        break
                    elif hasattr(version, '__str__'):
                        version = str(version)
                        break
            
            return DependencyCheck(
                name=name,
                required=required,
                installed=True,
                version=version,
                category=category
            )
            
        except ImportError as e:
            error_msg = self._get_install_suggestion(name)
            
            return DependencyCheck(
                name=name,
                required=required,
                installed=False,
                error=error_msg,
                category=category
            )
        except Exception as e:
            return DependencyCheck(
                name=name,
                required=required,
                installed=False,
                error=f"Erro inesperado: {str(e)}",
                category=category
            )
    
    def _get_install_suggestion(self, module_name: str) -> str:
        """Obtém sugestão de instalação para um módulo"""
        # Mapeamento de nomes de módulos para pacotes pip
        pip_names = {
            "google.cloud.storage": "google-cloud-storage",
            "google.genai": "google-generativeai", 
            "vertexai": "vertexai",
            "yaml": "PyYAML",
            "PIL": "Pillow",
            "cv2": "opencv-python",
            "docx": "python-docx",
            "sklearn": "scikit-learn",
        }
        
        pip_name = pip_names.get(module_name, module_name)
        return f"pip install {pip_name}"
    
    def generate_summary(self) -> Dict[str, any]:
        """Gera resumo da verificação"""
        total = len(self.results)
        installed = sum(1 for r in self.results if r.installed)
        required_missing = sum(1 for r in self.results if r.required and not r.installed)
        optional_missing = sum(1 for r in self.results if not r.required and not r.installed)
        
        return {
            "total_dependencies": total,
            "installed": installed,
            "missing": total - installed,
            "required_missing": required_missing,
            "optional_missing": optional_missing,
            "success_rate": (installed / total * 100) if total > 0 else 0,
            "core_ready": required_missing == 0
        }
    
    def print_summary(self, summary: Dict[str, any]) -> None:
        """Imprime resumo da verificação"""
        print(f"\n📊 RESUMO DA VERIFICAÇÃO")
        print("=" * 60)
        print(f"📦 Total de dependências: {summary['total_dependencies']}")
        print(f"✅ Instaladas: {summary['installed']}")
        print(f"❌ Faltando: {summary['missing']}")
        print(f"🔴 Obrigatórias faltando: {summary['required_missing']}")
        print(f"🟡 Opcionais faltando: {summary['optional_missing']}")
        print(f"📈 Taxa de sucesso: {summary['success_rate']:.1f}%")
        
        if summary['core_ready']:
            print(f"\n🎉 SISTEMA PRONTO! Todas as dependências core estão instaladas.")
            print(f"🚀 Você pode executar o RAG Enhanced normalmente.")
        else:
            print(f"\n⚠️ AÇÃO NECESSÁRIA! Dependências obrigatórias estão faltando.")
            print(f"💡 Instale as dependências core antes de continuar.")
    
    def generate_install_commands(self) -> List[str]:
        """Gera comandos de instalação para dependências faltando"""
        missing_required = [r for r in self.results if r.required and not r.installed]
        missing_optional = [r for r in self.results if not r.required and not r.installed]
        
        commands = []
        
        if missing_required:
            required_packages = []
            for result in missing_required:
                pip_name = self._get_install_suggestion(result.name).replace("pip install ", "")
                required_packages.append(pip_name)
            
            if required_packages:
                commands.append(f"# Dependências obrigatórias:")
                commands.append(f"pip install {' '.join(required_packages)}")
        
        if missing_optional:
            optional_packages = []
            for result in missing_optional:
                pip_name = self._get_install_suggestion(result.name).replace("pip install ", "")
                optional_packages.append(pip_name)
            
            if optional_packages:
                commands.append(f"\n# Dependências opcionais (recomendadas):")
                commands.append(f"pip install {' '.join(optional_packages)}")
        
        return commands
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Verifica se a versão do Python é compatível"""
        version = sys.version_info
        
        if version.major < 3:
            return False, f"Python 2.x não é suportado. Versão atual: {version.major}.{version.minor}"
        
        if version.minor < 8:
            return False, f"Python 3.8+ é recomendado. Versão atual: {version.major}.{version.minor}"
        
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    
    def check_pip_version(self) -> Tuple[bool, str]:
        """Verifica se o pip está atualizado"""
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                pip_version = result.stdout.strip()
                return True, pip_version
            else:
                return False, "pip não encontrado"
                
        except Exception as e:
            return False, f"Erro ao verificar pip: {str(e)}"


def main():
    """Função principal"""
    print("🔍 RAG Enhanced - Verificador de Dependências")
    print("=" * 60)
    
    checker = DependencyChecker()
    
    # Verificar Python
    python_ok, python_info = checker.check_python_version()
    print(f"\n🐍 Python: {'✅' if python_ok else '❌'} {python_info}")
    
    # Verificar pip
    pip_ok, pip_info = checker.check_pip_version()
    print(f"📦 Pip: {'✅' if pip_ok else '❌'} {pip_info}")
    
    if not python_ok:
        print(f"\n❌ Versão do Python incompatível!")
        print(f"💡 Instale Python 3.8 ou superior.")
        return False
    
    # Verificar dependências
    results_by_category = checker.check_all_dependencies()
    
    # Gerar resumo
    summary = checker.generate_summary()
    checker.print_summary(summary)
    
    # Gerar comandos de instalação se necessário
    if summary['missing'] > 0:
        print(f"\n💡 COMANDOS DE INSTALAÇÃO:")
        print("-" * 40)
        
        install_commands = checker.generate_install_commands()
        for command in install_commands:
            print(command)
        
        print(f"\n📋 OU use os arquivos requirements:")
        print(f"pip install -r requirements-minimal.txt  # Apenas essencial")
        print(f"pip install -r requirements.txt          # Completo")
        print(f"pip install -r requirements-dev.txt      # Desenvolvimento")
    
    # Verificação final
    if summary['core_ready']:
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"1. Execute: python run_validai_enhanced.py")
        print(f"2. Ou teste: python -c 'from rag_enhanced.testing import run_quick_test; run_quick_test()'")
        return True
    else:
        print(f"\n⚠️ Instale as dependências obrigatórias antes de continuar.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)