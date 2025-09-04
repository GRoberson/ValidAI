#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Setup e Gerenciamento de Corpus RAG

Script para configurar, criar e gerenciar os corpus RAG do ValidAI.
Facilita a preparação das bases de conhecimento.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class RAGCorpusSetup:
    """
    🛠️ Configurador de Corpus RAG
    
    Facilita a criação e gerenciamento dos corpus RAG do ValidAI.
    """
    
    def __init__(self, config_file: str = "rag_corpus_config.json"):
        self.config_file = config_file
        self.corpus_config = self._carregar_configuracao()
    
    def _carregar_configuracao(self) -> Dict[str, Any]:
        """Carrega configuração dos corpus"""
        if not os.path.exists(self.config_file):
            logger.error(f"❌ Arquivo de configuração não encontrado: {self.config_file}")
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return {}
    
    def listar_corpus(self) -> None:
        """Lista todos os corpus configurados"""
        print("\n📚 Corpus RAG Configurados:")
        print("=" * 60)
        
        for corpus_id, config in self.corpus_config.items():
            status = "✅ Ativo" if config.get('ativo', True) else "⏸️ Inativo"
            
            print(f"\n🔹 {corpus_id}")
            print(f"   Nome: {config['nome']}")
            print(f"   Descrição: {config['descricao']}")
            print(f"   Diretório: {config['diretorio_local']}")
            print(f"   Status: {status}")
            
            # Verificar se diretório existe e tem arquivos
            dir_path = Path(config['diretorio_local'])
            if dir_path.exists():
                arquivos = list(dir_path.rglob('*'))
                arquivos_validos = [
                    f for f in arquivos 
                    if f.is_file() and f.suffix.lower() in config['tipos_arquivo']
                ]
                print(f"   Arquivos: {len(arquivos_validos)} válidos de {len(arquivos)} total")
            else:
                print(f"   Arquivos: ❌ Diretório não existe")
    
    def verificar_estrutura(self) -> Dict[str, Any]:
        """Verifica estrutura de diretórios e arquivos"""
        print("\n🔍 Verificando Estrutura dos Corpus:")
        print("=" * 50)
        
        resultado = {
            'total_corpus': len(self.corpus_config),
            'corpus_com_arquivos': 0,
            'total_arquivos': 0,
            'problemas': []
        }
        
        for corpus_id, config in self.corpus_config.items():
            if not config.get('ativo', True):
                continue
            
            dir_path = Path(config['diretorio_local'])
            
            print(f"\n📁 {config['nome']}:")
            
            if not dir_path.exists():
                problema = f"Diretório não existe: {dir_path}"
                print(f"   ❌ {problema}")
                resultado['problemas'].append(problema)
                continue
            
            # Contar arquivos
            arquivos = list(dir_path.rglob('*'))
            arquivos_validos = [
                f for f in arquivos 
                if f.is_file() and f.suffix.lower() in config['tipos_arquivo']
            ]
            
            if arquivos_validos:
                resultado['corpus_com_arquivos'] += 1
                resultado['total_arquivos'] += len(arquivos_validos)
                
                print(f"   ✅ {len(arquivos_validos)} arquivos válidos")
                
                # Mostrar tipos de arquivo encontrados
                tipos_encontrados = set(f.suffix.lower() for f in arquivos_validos)
                print(f"   📄 Tipos: {', '.join(sorted(tipos_encontrados))}")
                
                # Calcular tamanho total
                tamanho_total = sum(f.stat().st_size for f in arquivos_validos)
                tamanho_mb = tamanho_total / (1024 * 1024)
                print(f"   📊 Tamanho: {tamanho_mb:.1f} MB")
            else:
                problema = f"Nenhum arquivo válido em: {dir_path}"
                print(f"   ⚠️ {problema}")
                resultado['problemas'].append(problema)
        
        # Resumo
        print(f"\n📊 Resumo:")
        print(f"   • Total de corpus: {resultado['total_corpus']}")
        print(f"   • Corpus com arquivos: {resultado['corpus_com_arquivos']}")
        print(f"   • Total de arquivos: {resultado['total_arquivos']}")
        print(f"   • Problemas encontrados: {len(resultado['problemas'])}")
        
        return resultado
    
    def criar_estrutura_diretorios(self) -> None:
        """Cria estrutura de diretórios para os corpus"""
        print("\n📁 Criando Estrutura de Diretórios:")
        print("=" * 40)
        
        for corpus_id, config in self.corpus_config.items():
            dir_path = Path(config['diretorio_local'])
            
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"   ✅ Criado: {dir_path}")
                    
                    # Criar arquivo README
                    readme_path = dir_path / "README.md"
                    readme_content = f"""# {config['nome']}

{config['descricao']}

## Tipos de arquivo suportados:
{chr(10).join(f'- {tipo}' for tipo in config['tipos_arquivo'])}

## Como usar:
1. Coloque os documentos neste diretório
2. Execute o setup do corpus RAG
3. Use no ValidAI Enhanced

Criado automaticamente pelo ValidAI Enhanced.
"""
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    
                    print(f"   📄 README criado: {readme_path}")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao criar {dir_path}: {e}")
            else:
                print(f"   ℹ️ Já existe: {dir_path}")
    
    def validar_configuracao(self) -> bool:
        """Valida a configuração dos corpus"""
        print("\n✅ Validando Configuração:")
        print("=" * 30)
        
        erros = []
        
        for corpus_id, config in self.corpus_config.items():
            print(f"\n🔹 Validando {corpus_id}:")
            
            # Verificar campos obrigatórios
            campos_obrigatorios = ['nome', 'descricao', 'diretorio_local', 'bucket_path', 'tipos_arquivo']
            for campo in campos_obrigatorios:
                if campo not in config:
                    erro = f"{corpus_id}: Campo obrigatório ausente: {campo}"
                    erros.append(erro)
                    print(f"   ❌ {erro}")
            
            # Verificar tipos de arquivo
            if 'tipos_arquivo' in config:
                if not isinstance(config['tipos_arquivo'], list) or not config['tipos_arquivo']:
                    erro = f"{corpus_id}: tipos_arquivo deve ser uma lista não vazia"
                    erros.append(erro)
                    print(f"   ❌ {erro}")
                else:
                    print(f"   ✅ Tipos de arquivo: {len(config['tipos_arquivo'])}")
            
            # Verificar paths
            if 'diretorio_local' in config and 'bucket_path' in config:
                print(f"   ✅ Paths configurados")
        
        if erros:
            print(f"\n❌ {len(erros)} erro(s) encontrado(s)")
            return False
        else:
            print(f"\n✅ Configuração válida!")
            return True
    
    def gerar_script_exemplo(self) -> None:
        """Gera script de exemplo para usar os corpus"""
        script_content = '''#!/usr/bin/env python3
"""
Exemplo de uso do sistema RAG do ValidAI
"""

from validai_rag_system import ValidAIRAGManager, ValidAIRAGInterface, criar_configuracao_rag_padrao

def main():
    """
    Função de exemplo para demonstrar uso do sistema RAG
    
    Demonstra como inicializar e usar o ValidAI RAG Manager
    para listar corpus disponíveis e fazer consultas básicas.
    """
    # Configuração
    config = criar_configuracao_rag_padrao()
    
    # Inicializar sistema RAG
    rag_manager = ValidAIRAGManager(config)
    interface = ValidAIRAGInterface(rag_manager)
    
    # Listar corpus disponíveis
    print("📚 Corpus disponíveis:")
    opcoes = interface.obter_opcoes_corpus()
    for nome, corpus_id in opcoes:
        print(f"  - {nome}")
    
    # Exemplo de uso
    corpus_id = "instrucoes_normativas"  # Altere conforme necessário
    
    # 1. Verificar arquivos
    info = rag_manager.verificar_arquivos_corpus(corpus_id)
    print(f"\\n📊 Arquivos no corpus: {info['arquivos_validos']}")
    
    # 2. Enviar arquivos (se necessário)
    # enviados, ignorados = rag_manager.enviar_arquivos_corpus(corpus_id)
    
    # 3. Criar corpus
    # corpus_name = rag_manager.criar_corpus_rag(corpus_id)
    
    # 4. Processar arquivos
    # rag_manager.processar_arquivos_corpus(corpus_id)
    
    # 5. Criar ferramenta de busca
    # ferramenta = rag_manager.criar_ferramenta_busca(corpus_id)
    
    # 6. Fazer consulta
    # resposta = rag_manager.consultar_corpus(corpus_id, "Qual é o processo de validação?")
    # print(f"\\n🤖 Resposta: {resposta}")

if __name__ == "__main__":
    main()
'''
        
        script_path = "exemplo_uso_rag.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Script de exemplo criado: {script_path}")
    
    def migrar_arquivos_existentes(self) -> None:
        """Migra arquivos da estrutura antiga para a nova"""
        print("\n🔄 Migrando Arquivos Existentes:")
        print("=" * 35)
        
        # Mapeamento da estrutura antiga para nova
        mapeamento = {
            "base_conhecimento/dicionario_base.csv": "base_conhecimento/ins/",
            "base_conhecimento/Mercado/": "base_conhecimento/mercado/",
            "base_conhecimento/Credito/": "base_conhecimento/credito/"
        }
        
        for origem, destino in mapeamento.items():
            origem_path = Path(origem)
            destino_path = Path(destino)
            
            if origem_path.exists():
                print(f"📁 Migrando: {origem} -> {destino}")
                
                # Criar diretório de destino
                destino_path.mkdir(parents=True, exist_ok=True)
                
                if origem_path.is_file():
                    # Copiar arquivo único
                    import shutil
                    shutil.copy2(origem_path, destino_path / origem_path.name)
                    print(f"   ✅ Arquivo copiado: {origem_path.name}")
                
                elif origem_path.is_dir():
                    # Copiar diretório
                    import shutil
                    for item in origem_path.rglob('*'):
                        if item.is_file():
                            rel_path = item.relative_to(origem_path)
                            dest_file = destino_path / rel_path
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dest_file)
                    
                    print(f"   ✅ Diretório migrado")
            else:
                print(f"   ℹ️ Não encontrado: {origem}")


def main():
    parser = argparse.ArgumentParser(
        description="⚙️ Setup e Gerenciamento de Corpus RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python setup_rag_corpus.py --list                    # Listar corpus
  python setup_rag_corpus.py --check                   # Verificar estrutura
  python setup_rag_corpus.py --create-dirs             # Criar diretórios
  python setup_rag_corpus.py --validate                # Validar configuração
  python setup_rag_corpus.py --migrate                 # Migrar arquivos antigos
  python setup_rag_corpus.py --example                 # Gerar script exemplo
        """
    )
    
    parser.add_argument('--config', '-c', default='rag_corpus_config.json',
                       help='Arquivo de configuração dos corpus')
    parser.add_argument('--list', '-l', action='store_true',
                       help='Listar todos os corpus configurados')
    parser.add_argument('--check', action='store_true',
                       help='Verificar estrutura de arquivos')
    parser.add_argument('--create-dirs', action='store_true',
                       help='Criar estrutura de diretórios')
    parser.add_argument('--validate', '-v', action='store_true',
                       help='Validar configuração')
    parser.add_argument('--migrate', '-m', action='store_true',
                       help='Migrar arquivos da estrutura antiga')
    parser.add_argument('--example', '-e', action='store_true',
                       help='Gerar script de exemplo')
    parser.add_argument('--all', '-a', action='store_true',
                       help='Executar todas as operações de setup')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("⚙️ Setup de Corpus RAG - ValidAI Enhanced")
    print("="*60)
    
    # Inicializar setup
    setup = RAGCorpusSetup(args.config)
    
    if not setup.corpus_config:
        print("❌ Não foi possível carregar a configuração dos corpus")
        return 1
    
    try:
        if args.all:
            # Executar todas as operações
            setup.validar_configuracao()
            setup.criar_estrutura_diretorios()
            setup.migrar_arquivos_existentes()
            setup.verificar_estrutura()
            setup.listar_corpus()
            setup.gerar_script_exemplo()
        
        elif args.list:
            setup.listar_corpus()
        
        elif args.check:
            setup.verificar_estrutura()
        
        elif args.create_dirs:
            setup.criar_estrutura_diretorios()
        
        elif args.validate:
            if setup.validar_configuracao():
                print("✅ Configuração válida!")
            else:
                print("❌ Configuração inválida!")
                return 1
        
        elif args.migrate:
            setup.migrar_arquivos_existentes()
        
        elif args.example:
            setup.gerar_script_exemplo()
        
        else:
            # Operação padrão
            print("ℹ️ Executando verificação básica...")
            setup.validar_configuracao()
            setup.verificar_estrutura()
        
        print("\n✅ Operação concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a operação: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())