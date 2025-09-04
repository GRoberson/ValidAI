#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📚 Exemplo Completo do Sistema RAG ValidAI

Este script demonstra como usar o sistema RAG avançado do ValidAI
de forma programática, incluindo setup, configuração e consultas.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports do sistema RAG
from validai_rag_system import (
    ValidAIRAGManager, 
    ValidAIRAGInterface, 
    criar_configuracao_rag_padrao
)


def demonstrar_sistema_rag():
    """
    Demonstração completa do sistema RAG
    """
    print("\n" + "="*70)
    print("📚 Demonstração do Sistema RAG ValidAI Enhanced")
    print("="*70)
    
    try:
        # 1. Configuração inicial
        print("\n🔧 1. Configurando sistema RAG...")
        config = criar_configuracao_rag_padrao()
        
        # Ajustar configurações se necessário
        config.update({
            'project_id': os.getenv('VALIDAI_PROJECT_ID', 'bv-cdip-des'),
            'bucket_name': os.getenv('VALIDAI_RAG_BUCKET', 'validai-rag-bucket')
        })
        
        print(f"   • Projeto: {config['project_id']}")
        print(f"   • Bucket: {config['bucket_name']}")
        print(f"   • Modelo: {config['modelo_ia']}")
        
        # 2. Inicializar gerenciador RAG
        print("\n🧠 2. Inicializando gerenciador RAG...")
        rag_manager = ValidAIRAGManager(config)
        
        # 3. Criar interface
        print("\n🎨 3. Criando interface RAG...")
        rag_interface = ValidAIRAGInterface(rag_manager)
        
        # 4. Listar corpus disponíveis
        print("\n📋 4. Corpus disponíveis:")
        corpus_info = rag_manager.listar_corpus_disponiveis()
        
        for info in corpus_info:
            status = "✅" if info['tem_arquivos'] else "⚠️"
            print(f"   {status} {info['nome']}")
            print(f"      ID: {info['id']}")
            print(f"      Descrição: {info['descricao']}")
        
        # 5. Verificar arquivos de um corpus específico
        corpus_exemplo = "instrucoes_normativas"
        print(f"\n🔍 5. Verificando arquivos do corpus: {corpus_exemplo}")
        
        try:
            info_arquivos = rag_manager.verificar_arquivos_corpus(corpus_exemplo)
            print(f"   • Arquivos válidos: {info_arquivos['arquivos_validos']}")
            print(f"   • Tamanho total: {info_arquivos['tamanho_total_mb']:.1f} MB")
            print(f"   • Tipos encontrados: {info_arquivos['tipos_encontrados']}")
            print(f"   • Status: {info_arquivos['status']}")
            
            if info_arquivos['arquivos_validos'] == 0:
                print("\n💡 Dica: Adicione documentos PDF, TXT ou MD no diretório:")
                print(f"   {rag_manager.corpus_configs[corpus_exemplo].diretorio_local}")
                return
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar arquivos: {e}")
            return
        
        # 6. Demonstrar fluxo completo (se arquivos disponíveis)
        if info_arquivos['arquivos_validos'] > 0:
            print(f"\n🚀 6. Demonstrando fluxo completo para: {corpus_exemplo}")
            
            # 6.1 Upload de arquivos
            print("\n📤 6.1 Enviando arquivos para Google Cloud...")
            try:
                enviados, ignorados = rag_manager.enviar_arquivos_corpus(corpus_exemplo)
                print(f"   ✅ Enviados: {enviados}, Ignorados: {ignorados}")
            except Exception as e:
                print(f"   ❌ Erro no upload: {e}")
                return
            
            # 6.2 Criar corpus RAG
            print("\n🧠 6.2 Criando corpus no Vertex AI...")
            try:
                corpus_name = rag_manager.criar_corpus_rag(corpus_exemplo)
                print(f"   ✅ Corpus criado: {corpus_name}")
            except Exception as e:
                print(f"   ❌ Erro ao criar corpus: {e}")
                return
            
            # 6.3 Processar arquivos
            print("\n📚 6.3 Processando arquivos (pode demorar alguns minutos)...")
            try:
                rag_manager.processar_arquivos_corpus(corpus_exemplo)
                print("   ✅ Processamento iniciado")
                
                # Aguardar um pouco para o processamento
                print("   ⏳ Aguardando processamento inicial...")
                time.sleep(30)  # Aguardar 30 segundos
                
            except Exception as e:
                print(f"   ❌ Erro no processamento: {e}")
                return
            
            # 6.4 Criar ferramenta de busca
            print("\n🔧 6.4 Criando ferramenta de busca...")
            try:
                ferramenta = rag_manager.criar_ferramenta_busca(corpus_exemplo)
                print("   ✅ Ferramenta de busca criada")
            except Exception as e:
                print(f"   ❌ Erro ao criar ferramenta: {e}")
                return
            
            # 6.5 Fazer consultas de exemplo
            print("\n💬 6.5 Fazendo consultas de exemplo...")
            
            perguntas_exemplo = [
                "Qual é o processo de validação de modelos?",
                "Quais são os principais riscos em modelos de ML?",
                "Como deve ser feito o monitoramento de modelos?",
                "Quais são as responsabilidades da área de validação?"
            ]
            
            for i, pergunta in enumerate(perguntas_exemplo, 1):
                print(f"\n❓ Pergunta {i}: {pergunta}")
                
                try:
                    # Usar interface para consulta
                    rag_interface.selecionar_corpus(corpus_exemplo)
                    resposta = rag_interface.processar_consulta(pergunta)
                    
                    # Mostrar resposta resumida
                    resposta_resumida = resposta[:200] + "..." if len(resposta) > 200 else resposta
                    print(f"🤖 Resposta: {resposta_resumida}")
                    
                except Exception as e:
                    print(f"   ❌ Erro na consulta: {e}")
                
                # Pequena pausa entre consultas
                time.sleep(2)
        
        # 7. Estatísticas finais
        print("\n📊 7. Estatísticas finais:")
        try:
            stats = rag_manager.obter_estatisticas_corpus(corpus_exemplo)
            print(f"   • Nome: {stats['nome']}")
            print(f"   • Corpus criado: {stats['corpus_criado']}")
            print(f"   • Ferramenta disponível: {stats['ferramenta_disponivel']}")
            print(f"   • Arquivos válidos: {stats['arquivos_validos']}")
        except Exception as e:
            print(f"   ❌ Erro ao obter estatísticas: {e}")
        
        print("\n✅ Demonstração concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Execute o ValidAI Enhanced com RAG: python validai_enhanced_with_rag.py")
        print("   2. Use a interface gráfica para configurar outros corpus")
        print("   3. Adicione mais documentos às bases de conhecimento")
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        print("\n🔧 Verifique:")
        print("   • Configurações do Google Cloud")
        print("   • Permissões do Vertex AI")
        print("   • Conectividade com a internet")


def verificar_prerequisitos():
    """Verifica se os pré-requisitos estão atendidos"""
    print("🔍 Verificando pré-requisitos...")
    
    # Verificar imports
    try:
        import google.genai
        import vertexai
        from google.cloud import storage
        print("   ✅ Bibliotecas Google Cloud OK")
    except ImportError as e:
        print(f"   ❌ Biblioteca faltando: {e}")
        return False
    
    # Verificar configuração
    project_id = os.getenv('VALIDAI_PROJECT_ID', 'bv-cdip-des')
    if project_id == 'bv-cdip-des':
        print("   ⚠️ Usando projeto padrão. Configure VALIDAI_PROJECT_ID se necessário.")
    else:
        print(f"   ✅ Projeto configurado: {project_id}")
    
    # Verificar estrutura de arquivos
    arquivos_necessarios = [
        'validai_rag_system.py',
        'rag_corpus_config.json'
    ]
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ Arquivo faltando: {arquivo}")
            return False
    
    return True


def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🚀 Exemplo Completo - Sistema RAG ValidAI Enhanced")
    print("="*70)
    
    # Verificar pré-requisitos
    if not verificar_prerequisitos():
        print("\n❌ Pré-requisitos não atendidos. Verifique a instalação.")
        return 1
    
    # Confirmar execução
    print("\n⚠️ Esta demonstração irá:")
    print("   • Conectar com Google Cloud")
    print("   • Criar recursos no Vertex AI")
    print("   • Fazer upload de arquivos")
    print("   • Processar documentos")
    
    resposta = input("\nContinuar? (s/N): ").lower().strip()
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("Demonstração cancelada.")
        return 0
    
    # Executar demonstração
    try:
        demonstrar_sistema_rag()
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração interrompida pelo usuário")
        return 0
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())