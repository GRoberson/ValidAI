#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 Gerador Automático de Docstrings para ValidAI Enhanced

Script para identificar e adicionar docstrings faltantes nas funções
públicas mais importantes do projeto ValidAI Enhanced.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class GeradorDocstrings:
    """
    📝 Gerador automático de docstrings
    
    Analisa código Python e gera docstrings apropriados baseados
    no contexto e padrões do projeto ValidAI Enhanced.
    """
    
    def __init__(self):
        self.docstrings_gerados = []
        self.funcoes_processadas = 0
        
        # Templates de docstrings por contexto
        self.templates = {
            'config': {
                'carregar': 'Carrega configurações do sistema',
                'salvar': 'Salva configurações no arquivo',
                'validar': 'Valida configurações do sistema',
                'criar': 'Cria nova configuração'
            },
            'arquivo': {
                'processar': 'Processa arquivo de entrada',
                'validar': 'Valida arquivo de entrada',
                'converter': 'Converte arquivo para formato específico',
                'ler': 'Lê conteúdo do arquivo'
            },
            'interface': {
                'criar': 'Cria componente da interface',
                'conectar': 'Conecta eventos da interface',
                'atualizar': 'Atualiza estado da interface',
                'renderizar': 'Renderiza componente visual'
            },
            'rag': {
                'consultar': 'Executa consulta no sistema RAG',
                'processar': 'Processa documentos para RAG',
                'criar': 'Cria corpus RAG',
                'indexar': 'Indexa documentos no sistema'
            },
            'multimodal': {
                'analisar': 'Analisa conteúdo multimodal',
                'extrair': 'Extrai informações de mídia',
                'processar': 'Processa arquivo multimodal',
                'detectar': 'Detecta tipo de mídia'
            }
        }
    
    def detectar_contexto(self, nome_funcao: str, nome_arquivo: str) -> str:
        """
        Detecta o contexto da função baseado no nome e arquivo
        
        Args:
            nome_funcao: Nome da função
            nome_arquivo: Nome do arquivo
            
        Returns:
            Contexto detectado
        """
        nome_lower = nome_funcao.lower()
        arquivo_lower = nome_arquivo.lower()
        
        # Detectar por arquivo
        if 'config' in arquivo_lower:
            return 'config'
        elif 'multimodal' in arquivo_lower:
            return 'multimodal'
        elif 'rag' in arquivo_lower:
            return 'rag'
        elif 'interface' in arquivo_lower or 'front' in arquivo_lower:
            return 'interface'
        
        # Detectar por nome da função
        if any(palavra in nome_lower for palavra in ['config', 'configurar']):
            return 'config'
        elif any(palavra in nome_lower for palavra in ['arquivo', 'file', 'processar']):
            return 'arquivo'
        elif any(palavra in nome_lower for palavra in ['interface', 'criar_aba', 'conectar']):
            return 'interface'
        elif any(palavra in nome_lower for palavra in ['rag', 'corpus', 'consultar']):
            return 'rag'
        elif any(palavra in nome_lower for palavra in ['multimodal', 'midia', 'imagem', 'video']):
            return 'multimodal'
        
        return 'geral'
    
    def gerar_docstring_por_contexto(self, nome_funcao: str, contexto: str, 
                                   parametros: List[str], retorno: str = None) -> str:
        """
        Gera docstring baseado no contexto da função
        
        Args:
            nome_funcao: Nome da função
            contexto: Contexto detectado
            parametros: Lista de parâmetros
            retorno: Tipo de retorno (opcional)
            
        Returns:
            Docstring gerado
        """
        nome_lower = nome_funcao.lower()
        
        # Detectar ação principal
        acao = 'executa operação'
        if contexto in self.templates:
            for palavra_chave, descricao in self.templates[contexto].items():
                if palavra_chave in nome_lower:
                    acao = descricao.lower()
                    break
        
        # Gerar descrição principal
        if nome_funcao.startswith('_'):
            descricao = f"Método interno que {acao}"
        else:
            descricao = f"Função que {acao}"
        
        # Capitalizar primeira letra
        descricao = descricao[0].upper() + descricao[1:]
        
        # Construir docstring
        docstring_parts = [f'        """', f'        {descricao}']
        
        # Adicionar parâmetros se houver
        if parametros and len(parametros) > 1:  # Ignorar 'self'
            docstring_parts.append('        ')
            docstring_parts.append('        Args:')
            
            for param in parametros[1:]:  # Pular 'self'
                if param == 'self':
                    continue
                
                # Gerar descrição do parâmetro
                if 'config' in param.lower():
                    desc_param = 'Configurações do sistema'
                elif 'arquivo' in param.lower() or 'file' in param.lower():
                    desc_param = 'Caminho do arquivo'
                elif 'corpus' in param.lower():
                    desc_param = 'ID do corpus RAG'
                elif 'message' in param.lower() or 'msg' in param.lower():
                    desc_param = 'Mensagem do usuário'
                elif 'history' in param.lower():
                    desc_param = 'Histórico da conversa'
                elif param.endswith('_id'):
                    desc_param = 'Identificador único'
                else:
                    desc_param = f'Parâmetro {param}'
                
                docstring_parts.append(f'            {param}: {desc_param}')
        
        # Adicionar retorno se especificado
        if retorno:
            docstring_parts.append('        ')
            docstring_parts.append('        Returns:')
            
            if 'bool' in retorno.lower():
                desc_retorno = 'True se operação foi bem-sucedida, False caso contrário'
            elif 'str' in retorno.lower():
                desc_retorno = 'String com resultado da operação'
            elif 'dict' in retorno.lower():
                desc_retorno = 'Dicionário com dados processados'
            elif 'list' in retorno.lower():
                desc_retorno = 'Lista com resultados'
            else:
                desc_retorno = 'Resultado da operação'
            
            docstring_parts.append(f'            {desc_retorno}')
        
        docstring_parts.append('        """')
        
        return '\n'.join(docstring_parts)
    
    def analisar_funcao(self, node: ast.FunctionDef, nome_arquivo: str) -> Tuple[str, List[str], str]:
        """
        Analisa uma função AST para extrair informações
        
        Args:
            node: Nó AST da função
            nome_arquivo: Nome do arquivo
            
        Returns:
            Tupla com (nome, parâmetros, tipo_retorno)
        """
        nome = node.name
        
        # Extrair parâmetros
        parametros = []
        for arg in node.args.args:
            parametros.append(arg.arg)
        
        # Tentar detectar tipo de retorno
        tipo_retorno = None
        if node.returns:
            if hasattr(node.returns, 'id'):
                tipo_retorno = node.returns.id
            elif hasattr(node.returns, 'attr'):
                tipo_retorno = node.returns.attr
        
        return nome, parametros, tipo_retorno
    
    def processar_arquivo(self, caminho_arquivo: Path) -> List[Dict]:
        """
        Processa um arquivo Python e identifica funções sem docstring
        
        Args:
            caminho_arquivo: Caminho do arquivo Python
            
        Returns:
            Lista de funções que precisam de docstring
        """
        funcoes_sem_docstring = []
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            tree = ast.parse(conteudo)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Verificar se é função pública (não começa com _)
                    if not node.name.startswith('__'):  # Permitir métodos especiais
                        # Verificar se tem docstring
                        docstring = ast.get_docstring(node)
                        
                        if not docstring:
                            nome, parametros, tipo_retorno = self.analisar_funcao(node, caminho_arquivo.name)
                            contexto = self.detectar_contexto(nome, caminho_arquivo.name)
                            
                            docstring_gerado = self.gerar_docstring_por_contexto(
                                nome, contexto, parametros, tipo_retorno
                            )
                            
                            funcoes_sem_docstring.append({
                                'nome': nome,
                                'linha': node.lineno,
                                'parametros': parametros,
                                'contexto': contexto,
                                'docstring': docstring_gerado,
                                'eh_publica': not nome.startswith('_')
                            })
        
        except Exception as e:
            print(f"❌ Erro ao processar {caminho_arquivo}: {e}")
        
        return funcoes_sem_docstring
    
    def gerar_relatorio_docstrings(self) -> str:
        """
        Gera relatório das funções que precisam de docstrings
        
        Returns:
            Relatório formatado
        """
        arquivos_principais = [
            'validai_enhanced.py',
            'validai_enhanced_with_rag.py', 
            'validai_enhanced_multimodal.py',
            'validai_rag_system.py',
            'validai_rag_multimodal.py'
        ]
        
        relatorio = []
        relatorio.append("=" * 70)
        relatorio.append("📝 RELATÓRIO DE DOCSTRINGS FALTANTES")
        relatorio.append("=" * 70)
        
        total_funcoes = 0
        total_sem_docstring = 0
        
        for arquivo in arquivos_principais:
            if os.path.exists(arquivo):
                relatorio.append(f"\n📄 {arquivo}:")
                
                funcoes = self.processar_arquivo(Path(arquivo))
                funcoes_publicas = [f for f in funcoes if f['eh_publica']]
                
                total_funcoes += len(funcoes)
                total_sem_docstring += len(funcoes_publicas)
                
                if funcoes_publicas:
                    relatorio.append(f"   🔍 {len(funcoes_publicas)} funções públicas sem docstring:")
                    
                    for func in funcoes_publicas[:5]:  # Mostrar apenas as primeiras 5
                        relatorio.append(f"      • {func['nome']}() - linha {func['linha']} ({func['contexto']})")
                    
                    if len(funcoes_publicas) > 5:
                        relatorio.append(f"      ... e mais {len(funcoes_publicas) - 5} funções")
                else:
                    relatorio.append("   ✅ Todas as funções públicas têm docstring")
        
        relatorio.append(f"\n📊 RESUMO:")
        relatorio.append(f"   • Total de funções analisadas: {total_funcoes}")
        relatorio.append(f"   • Funções públicas sem docstring: {total_sem_docstring}")
        
        if total_sem_docstring > 0:
            relatorio.append(f"\n💡 RECOMENDAÇÃO:")
            relatorio.append(f"   Adicionar docstrings às {total_sem_docstring} funções públicas")
        else:
            relatorio.append(f"\n✅ EXCELENTE:")
            relatorio.append(f"   Todas as funções públicas têm documentação!")
        
        relatorio.append("=" * 70)
        
        return "\n".join(relatorio)


def main():
    """Função principal do gerador de docstrings"""
    print("\n" + "="*70)
    print("📝 Gerador de Docstrings - ValidAI Enhanced")
    print("="*70)
    
    try:
        gerador = GeradorDocstrings()
        
        # Gerar relatório
        relatorio = gerador.gerar_relatorio_docstrings()
        print(relatorio)
        
        # Salvar relatório
        with open("relatorio_docstrings.txt", "w", encoding="utf-8") as f:
            f.write(relatorio)
        
        print(f"\n💾 Relatório salvo em: relatorio_docstrings.txt")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())