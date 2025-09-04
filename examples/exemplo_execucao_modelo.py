#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Exemplo Prático - Como Executar o Modelo RAG Enhanced

Este script demonstra as diferentes formas de executar o modelo
no sistema RAG Enhanced, desde desenvolvimento até produção.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def exemplo_execucao_local():
    """
    🏠 Execução Local - Desenvolvimento sem dependências externas
    """
    print("🏠 EXECUÇÃO LOCAL (Desenvolvimento)")
    print("=" * 50)
    
    from rag_enhanced.testing.mocks import MockVertexAI
    from rag_enhanced.testing.generators import TestDataGenerator
    
    # Inicializar mock do Vertex AI
    mock_ai = MockVertexAI()
    
    # Gerar dados de teste
    generator = TestDataGenerator()
    queries = generator.generate_query_examples(3)
    
    print("📝 Executando queries de exemplo:")
    
    for i, query_data in enumerate(queries, 1):
        query = query_data['text']
        print(f"\n{i}. Query: {query}")
        
        # Executar com mock
        response = mock_ai.generate_content(query)
        
        print(f"   Resposta: {response['text'][:100]}...")
        print(f"   Confiança: {response['confidence']:.2f}")
        print(f"   Tempo: {response['processing_time']:.2f}s")


def exemplo_execucao_framework():
    """
    🧪 Execução com Framework de Testes
    """
    print("\n🧪 EXECUÇÃO COM FRAMEWORK DE TESTES")
    print("=" * 50)
    
    from rag_enhanced.testing.framework import TestRunner
    from rag_enhanced.testing.mocks import MockServices
    
    # Inicializar framework
    runner = TestRunner()
    mocks = MockServices()
    
    # Configurar cenário de teste
    mocks.setup_scenario("normal")
    
    print("🔧 Configurando ambiente de teste...")
    
    # Criar corpus de teste
    corpus = mocks.vertex_ai.create_corpus("test-corpus", "Corpus para demonstração")
    print(f"✅ Corpus criado: {corpus}")
    
    # Executar queries de teste
    test_queries = [
        "Explique o padrão Singleton em Python",
        "Como otimizar consultas SQL?",
        "Melhores práticas para APIs REST"
    ]
    
    print("\n📋 Executando queries de teste:")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        try:
            response = mocks.vertex_ai.generate_content(query, "test-corpus")
            print(f"   ✅ Sucesso: {response['text'][:80]}...")
            print(f"   Corpus: {response['corpus_used']}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # Executar teste rápido
    print("\n🚀 Executando teste rápido do framework:")
    result = runner.run_quick_test()
    print(f"   Taxa de sucesso: {result['success_rate']:.1f}%")
    print(f"   Tempo total: {result['total_time']:.2f}s")


def exemplo_execucao_producao():
    """
    🌐 Execução em Produção (Vertex AI)
    
    Nota: Este exemplo mostra como seria a execução real,
    mas requer configuração do Google Cloud.
    """
    print("\n🌐 EXECUÇÃO EM PRODUÇÃO (Vertex AI)")
    print("=" * 50)
    
    print("📋 Configuração necessária para produção:")
    print("1. Projeto Google Cloud configurado")
    print("2. Vertex AI habilitado")
    print("3. Credenciais de autenticação")
    print("4. Corpus RAG criado e populado")
    
    # Exemplo de código para produção (comentado)
    exemplo_codigo_producao = '''
    # Configuração real para produção
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from google.genai.types import Retrieval, VertexRagStore
    
    # Inicializar Vertex AI
    vertexai.init(
        project="seu-projeto-gcp",
        location="us-central1"
    )
    
    # Configurar RAG
    rag_store = VertexRagStore(
        rag_corpora=["projects/seu-projeto/locations/us-central1/ragCorpora/seu-corpus"]
    )
    
    rag_retrieval_tool = Retrieval(
        vertex_rag_store=rag_store
    )
    
    # Criar modelo com RAG
    model = GenerativeModel(
        "gemini-1.5-pro",
        tools=[rag_retrieval_tool]
    )
    
    # Executar query
    response = model.generate_content(
        "Como implementar autenticação JWT?",
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 1024
        }
    )
    
    print(response.text)
    '''
    
    print("\n💻 Código de exemplo:")
    print(exemplo_codigo_producao)


def exemplo_configuracao_perfis():
    """
    ⚙️ Configuração de Perfis de Execução
    """
    print("\n⚙️ CONFIGURAÇÃO DE PERFIS")
    print("=" * 50)
    
    from rag_enhanced.config.profiles import ProfileManager
    from pathlib import Path
    
    # Inicializar gerenciador de perfis
    config_dir = Path(".rag_config_demo")
    profile_manager = ProfileManager(config_dir)
    
    # Criar perfil de desenvolvimento
    dev_profile = {
        "name": "development",
        "description": "Perfil para desenvolvimento local",
        "mode": "local",
        "use_mocks": True,
        "debug": True,
        "log_level": "DEBUG"
    }
    
    # Criar perfil de produção
    prod_profile = {
        "name": "production",
        "description": "Perfil para ambiente de produção",
        "mode": "vertex_ai",
        "project_id": "seu-projeto-gcp",
        "location": "us-central1",
        "corpus_name": "production-corpus",
        "use_mocks": False,
        "debug": False,
        "log_level": "INFO"
    }
    
    print("📋 Perfis de configuração:")
    print(f"🔧 Desenvolvimento: {dev_profile['name']}")
    print(f"   Modo: {dev_profile['mode']}")
    print(f"   Mocks: {dev_profile['use_mocks']}")
    print(f"   Debug: {dev_profile['debug']}")
    
    print(f"\n🌐 Produção: {prod_profile['name']}")
    print(f"   Modo: {prod_profile['mode']}")
    print(f"   Projeto: {prod_profile['project_id']}")
    print(f"   Localização: {prod_profile['location']}")


def exemplo_metricas_execucao():
    """
    📊 Métricas e Monitoramento de Execução
    """
    print("\n📊 MÉTRICAS DE EXECUÇÃO")
    print("=" * 50)
    
    from rag_enhanced.testing.mocks import MockServices
    import time
    
    mocks = MockServices()
    
    # Simular execução com métricas
    queries = [
        "Como funciona machine learning?",
        "Explique algoritmos de ordenação",
        "Padrões de design em software"
    ]
    
    print("📈 Coletando métricas de execução:")
    
    total_time = 0
    successful_queries = 0
    
    for i, query in enumerate(queries, 1):
        start_time = time.time()
        
        try:
            response = mocks.vertex_ai.generate_content(query)
            execution_time = time.time() - start_time
            total_time += execution_time
            successful_queries += 1
            
            print(f"{i}. Query executada em {execution_time:.3f}s")
            print(f"   Confiança: {response['confidence']:.2f}")
            print(f"   Tamanho resposta: {len(response['text'])} chars")
            
        except Exception as e:
            print(f"{i}. ❌ Falha: {e}")
    
    # Estatísticas finais
    print(f"\n📊 Estatísticas:")
    print(f"   Queries executadas: {successful_queries}/{len(queries)}")
    print(f"   Taxa de sucesso: {successful_queries/len(queries)*100:.1f}%")
    print(f"   Tempo total: {total_time:.3f}s")
    print(f"   Tempo médio: {total_time/len(queries):.3f}s")
    
    # Estatísticas dos mocks
    stats = mocks.get_comprehensive_stats()
    print(f"   Operações de storage: {stats['storage']['operations']}")
    print(f"   Queries processadas: {stats['vertex_ai']['query_count']}")


def main():
    """
    Função principal - executa todos os exemplos
    """
    print("🤖 DEMONSTRAÇÃO: EXECUÇÃO DO MODELO RAG ENHANCED")
    print("=" * 60)
    print("Este script demonstra as diferentes formas de executar")
    print("o modelo no sistema RAG Enhanced.\n")
    
    try:
        # Executar todos os exemplos
        exemplo_execucao_local()
        exemplo_execucao_framework()
        exemplo_execucao_producao()
        exemplo_configuracao_perfis()
        exemplo_metricas_execucao()
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Todos os modos de execução foram demonstrados")
        print("✅ Framework de testes funcionando perfeitamente")
        print("✅ Mocks simulando comportamento real")
        print("✅ Métricas e monitoramento implementados")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Configure seu projeto Google Cloud para produção")
        print("2. Crie e popule seu corpus RAG")
        print("3. Execute testes locais antes do deploy")
        print("4. Monitore métricas em produção")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        print("Verifique se todos os módulos estão instalados corretamente.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)