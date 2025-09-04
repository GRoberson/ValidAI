#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Verificador de Integridade do ValidAI Enhanced

Script para verificar e reportar códigos incompletos, métodos vazios
e implementações faltantes no projeto ValidAI Enhanced.
"""

import os
import ast
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificadorIntegridade:
    """
    🔍 Verificador de integridade de código
    
    Analisa arquivos Python para identificar implementações incompletas,
    métodos vazios e código não utilizado.
    """
    
    def __init__(self, diretorio_projeto: str = "."):
        self.diretorio_projeto = Path(diretorio_projeto)
        self.arquivos_python = []
        self.problemas_encontrados = []
        self.estatisticas = {
            'total_arquivos': 0,
            'metodos_vazios': 0,
            'imports_nao_usados': 0,
            'classes_incompletas': 0,
            'funcoes_sem_docstring': 0
        }
    
    def escanear_projeto(self) -> None:
        """Escaneia o projeto em busca de arquivos Python"""
        logger.info("🔍 Escaneando projeto...")
        
        # Encontrar todos os arquivos Python
        for arquivo in self.diretorio_projeto.rglob("*.py"):
            # Ignorar arquivos de cache e temporários
            if "__pycache__" not in str(arquivo) and ".git" not in str(arquivo):
                self.arquivos_python.append(arquivo)
        
        self.estatisticas['total_arquivos'] = len(self.arquivos_python)
        logger.info(f"📁 Encontrados {len(self.arquivos_python)} arquivos Python")
    
    def analisar_arquivo(self, arquivo_path: Path) -> List[Dict[str, Any]]:
        """
        Analisa um arquivo Python em busca de problemas
        
        Args:
            arquivo_path: Caminho do arquivo
            
        Returns:
            Lista de problemas encontrados
        """
        problemas = []
        
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Analisar AST
            try:
                tree = ast.parse(conteudo)
                problemas.extend(self._analisar_ast(tree, arquivo_path))
            except SyntaxError as e:
                problemas.append({
                    'tipo': 'syntax_error',
                    'arquivo': str(arquivo_path),
                    'linha': e.lineno,
                    'descricao': f"Erro de sintaxe: {e.msg}",
                    'severidade': 'critica'
                })
            
            # Analisar texto
            problemas.extend(self._analisar_texto(conteudo, arquivo_path))
            
        except Exception as e:
            problemas.append({
                'tipo': 'erro_leitura',
                'arquivo': str(arquivo_path),
                'descricao': f"Erro ao ler arquivo: {e}",
                'severidade': 'alta'
            })
        
        return problemas
    
    def _analisar_ast(self, tree: ast.AST, arquivo_path: Path) -> List[Dict[str, Any]]:
        """Analisa a árvore AST em busca de problemas"""
        problemas = []
        
        class AnalisadorAST(ast.NodeVisitor):
            def __init__(self):
                self.imports = []
                self.nomes_usados = set()
                self.funcoes_definidas = []
                self.classes_definidas = []
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.append(alias.name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        self.imports.append(f"{node.module}.{alias.name}")
                self.generic_visit(node)
            
            def visit_Name(self, node):
                self.nomes_usados.add(node.id)
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                # Verificar se função está vazia (só tem pass)
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Pass)):
                    problemas.append({
                        'tipo': 'metodo_vazio',
                        'arquivo': str(arquivo_path),
                        'linha': node.lineno,
                        'nome': node.name,
                        'descricao': f"Método '{node.name}' está vazio (só contém 'pass')",
                        'severidade': 'alta' if not node.name.startswith('_') else 'media'
                    })
                
                # Verificar se tem docstring
                if not ast.get_docstring(node):
                    if not node.name.startswith('_'):  # Ignorar métodos privados
                        problemas.append({
                            'tipo': 'sem_docstring',
                            'arquivo': str(arquivo_path),
                            'linha': node.lineno,
                            'nome': node.name,
                            'descricao': f"Função '{node.name}' sem docstring",
                            'severidade': 'baixa'
                        })
                
                self.funcoes_definidas.append(node.name)
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Verificar se classe tem apenas pass
                if (len(node.body) == 1 and 
                    isinstance(node.body[0], ast.Pass)):
                    problemas.append({
                        'tipo': 'classe_vazia',
                        'arquivo': str(arquivo_path),
                        'linha': node.lineno,
                        'nome': node.name,
                        'descricao': f"Classe '{node.name}' está vazia",
                        'severidade': 'media'
                    })
                
                self.classes_definidas.append(node.name)
                self.generic_visit(node)
        
        analisador = AnalisadorAST()
        analisador.visit(tree)
        
        return problemas
    
    def _analisar_texto(self, conteudo: str, arquivo_path: Path) -> List[Dict[str, Any]]:
        """Analisa o texto do arquivo em busca de padrões problemáticos"""
        problemas = []
        linhas = conteudo.split('\n')
        
        for i, linha in enumerate(linhas, 1):
            linha_limpa = linha.strip()
            
            # Verificar TODOs e FIXMEs
            if 'TODO' in linha_limpa or 'FIXME' in linha_limpa:
                problemas.append({
                    'tipo': 'todo_fixme',
                    'arquivo': str(arquivo_path),
                    'linha': i,
                    'descricao': f"TODO/FIXME encontrado: {linha_limpa}",
                    'severidade': 'baixa'
                })
            
            # Verificar comentários indicando implementação incompleta
            comentarios_problematicos = [
                '# Implementação simplificada',
                '# pode ser expandida',
                '# Implementação parcial',
                '# não implementado',
                '# placeholder'
            ]
            
            for comentario in comentarios_problematicos:
                if comentario.lower() in linha_limpa.lower():
                    problemas.append({
                        'tipo': 'implementacao_incompleta',
                        'arquivo': str(arquivo_path),
                        'linha': i,
                        'descricao': f"Implementação incompleta: {linha_limpa}",
                        'severidade': 'alta'
                    })
            
            # Verificar prints em produção (possível debug esquecido)
            if linha_limpa.startswith('print(') and 'debug' in linha_limpa.lower():
                problemas.append({
                    'tipo': 'debug_esquecido',
                    'arquivo': str(arquivo_path),
                    'linha': i,
                    'descricao': f"Print de debug esquecido: {linha_limpa}",
                    'severidade': 'media'
                })
        
        return problemas
    
    def verificar_integridade_completa(self) -> Dict[str, Any]:
        """
        Executa verificação completa de integridade
        
        Returns:
            Relatório completo de integridade
        """
        logger.info("🔍 Iniciando verificação de integridade...")
        
        # Escanear projeto
        self.escanear_projeto()
        
        # Analisar cada arquivo
        todos_problemas = []
        
        for arquivo in self.arquivos_python:
            logger.info(f"   📄 Analisando: {arquivo.name}")
            problemas = self.analisar_arquivo(arquivo)
            todos_problemas.extend(problemas)
        
        # Categorizar problemas
        problemas_por_severidade = {
            'critica': [],
            'alta': [],
            'media': [],
            'baixa': []
        }
        
        problemas_por_tipo = {}
        
        for problema in todos_problemas:
            severidade = problema.get('severidade', 'baixa')
            tipo = problema.get('tipo', 'desconhecido')
            
            problemas_por_severidade[severidade].append(problema)
            
            if tipo not in problemas_por_tipo:
                problemas_por_tipo[tipo] = []
            problemas_por_tipo[tipo].append(problema)
        
        # Atualizar estatísticas
        self.estatisticas.update({
            'metodos_vazios': len(problemas_por_tipo.get('metodo_vazio', [])),
            'classes_incompletas': len(problemas_por_tipo.get('classe_vazia', [])),
            'funcoes_sem_docstring': len(problemas_por_tipo.get('sem_docstring', [])),
            'total_problemas': len(todos_problemas)
        })
        
        return {
            'estatisticas': self.estatisticas,
            'problemas_por_severidade': problemas_por_severidade,
            'problemas_por_tipo': problemas_por_tipo,
            'todos_problemas': todos_problemas
        }
    
    def gerar_relatorio(self, resultado: Dict[str, Any]) -> str:
        """
        Gera relatório formatado de integridade
        
        Args:
            resultado: Resultado da verificação
            
        Returns:
            Relatório formatado
        """
        relatorio = []
        
        relatorio.append("=" * 70)
        relatorio.append("🔍 RELATÓRIO DE INTEGRIDADE - ValidAI Enhanced")
        relatorio.append("=" * 70)
        
        # Estatísticas gerais
        stats = resultado['estatisticas']
        relatorio.append(f"\n📊 ESTATÍSTICAS GERAIS:")
        relatorio.append(f"   • Total de arquivos analisados: {stats['total_arquivos']}")
        relatorio.append(f"   • Total de problemas encontrados: {stats['total_problemas']}")
        relatorio.append(f"   • Métodos vazios: {stats['metodos_vazios']}")
        relatorio.append(f"   • Classes incompletas: {stats['classes_incompletas']}")
        relatorio.append(f"   • Funções sem docstring: {stats['funcoes_sem_docstring']}")
        
        # Problemas por severidade
        relatorio.append(f"\n🚨 PROBLEMAS POR SEVERIDADE:")
        
        severidades = ['critica', 'alta', 'media', 'baixa']
        emojis = {'critica': '🔴', 'alta': '🟠', 'media': '🟡', 'baixa': '🟢'}
        
        for severidade in severidades:
            problemas = resultado['problemas_por_severidade'][severidade]
            if problemas:
                relatorio.append(f"\n{emojis[severidade]} {severidade.upper()} ({len(problemas)} problemas):")
                
                for problema in problemas[:5]:  # Mostrar apenas os primeiros 5
                    arquivo = Path(problema['arquivo']).name
                    linha = problema.get('linha', '?')
                    descricao = problema['descricao']
                    relatorio.append(f"   • {arquivo}:{linha} - {descricao}")
                
                if len(problemas) > 5:
                    relatorio.append(f"   ... e mais {len(problemas) - 5} problemas")
        
        # Recomendações
        relatorio.append(f"\n💡 RECOMENDAÇÕES:")
        
        if stats['metodos_vazios'] > 0:
            relatorio.append("   🔧 Implementar métodos vazios críticos")
        
        if stats['classes_incompletas'] > 0:
            relatorio.append("   🏗️ Completar implementação de classes")
        
        if resultado['problemas_por_tipo'].get('implementacao_incompleta'):
            relatorio.append("   ⚠️ Finalizar implementações marcadas como incompletas")
        
        if stats['funcoes_sem_docstring'] > 10:
            relatorio.append("   📝 Adicionar documentação às funções públicas")
        
        # Status geral
        total_criticos = len(resultado['problemas_por_severidade']['critica'])
        total_altos = len(resultado['problemas_por_severidade']['alta'])
        
        relatorio.append(f"\n🎯 STATUS GERAL:")
        
        if total_criticos > 0:
            relatorio.append("   🔴 CRÍTICO - Problemas críticos impedem funcionamento")
        elif total_altos > 5:
            relatorio.append("   🟠 ATENÇÃO - Muitos problemas de alta prioridade")
        elif stats['total_problemas'] > 20:
            relatorio.append("   🟡 MODERADO - Projeto funcional mas precisa de melhorias")
        else:
            relatorio.append("   🟢 BOM - Poucos problemas encontrados")
        
        relatorio.append("=" * 70)
        
        return "\n".join(relatorio)


def main():
    """Função principal do verificador"""
    print("\n" + "="*70)
    print("🔍 Verificador de Integridade - ValidAI Enhanced")
    print("="*70)
    
    try:
        # Inicializar verificador
        verificador = VerificadorIntegridade()
        
        # Executar verificação
        resultado = verificador.verificar_integridade_completa()
        
        # Gerar e exibir relatório
        relatorio = verificador.gerar_relatorio(resultado)
        print(relatorio)
        
        # Salvar relatório em arquivo
        with open("relatorio_integridade.txt", "w", encoding="utf-8") as f:
            f.write(relatorio)
        
        print(f"\n💾 Relatório salvo em: relatorio_integridade.txt")
        
        # Retornar código de saída baseado na severidade
        total_criticos = len(resultado['problemas_por_severidade']['critica'])
        total_altos = len(resultado['problemas_por_severidade']['alta'])
        
        if total_criticos > 0:
            return 2  # Problemas críticos
        elif total_altos > 5:
            return 1  # Muitos problemas altos
        else:
            return 0  # OK
        
    except Exception as e:
        print(f"\n❌ Erro na verificação: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())