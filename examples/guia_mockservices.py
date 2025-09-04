#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 GUIA COMPLETO: Como Executar MockServices

Este guia mostra todas as formas de usar o MockServices
para desenvolvimento e testes sem dependências externas.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def exemplo_basico_mockservices():
    """
    🚀 Exemplo Básico - Primeiros Passos com MockServices
    """
    print("🚀 EXEMPLO BÁSICO - MockServices")
    print("=" * 50)
    
    # 1. Importar MockServices
    from rag_enhanced.testing.mocks import MockServices
    
    # 2. Inicializar
    mock_services = MockServices()
    print("✅ MockServices inicializado")
    
    # 3. Usar Cloud Storage Mock
    print("\n📦 Testando Cloud Storage:")
    
    # Criar bucket
    bucket = mock_services.storage.create_bucket("meu-bucket-teste")
    print(f"   Bucket criado: {bucket.name}")
    
    # Upload de arquivo
    conteudo = b"Este e um arquivo de teste para o RAG Enhanced"
    blob_name = mock_services.storage.upload_blob("meu-bucket-teste", "arquivo.txt", conteudo)
    print(f"   Arquivo enviado: {blob_name}")
    
    # Download de arquivo
    conteudo_baixado = mock_services.storage.download_blob("meu-bucket-teste", "arquivo.txt")
    print(f"   Arquivo baixado: {len(conteudo_baixado)} bytes")
    
    # Listar arquivos
    arquivos = mock_services.storage.list_blobs("meu-bucket-teste")
    print(f"   Arquivos no bucket: {len(arquivos)}")
    
    # 4. Usar Vertex AI Mock
    print("\n🧠 Testando Vertex AI:")
    
    # Criar corpus
    corpus = mock_services.vertex_ai.create_corpus("meu-corpus", "Corpus de teste")
    print(f"   Corpus criado: {corpus}")
    
    # Fazer query
    resposta = mock_services.vertex_ai.generate_content("Como funciona o RAG?")
    print(f"   Resposta gerada: {resposta['text'][:60]}...")
    print(f"   Confiança: {resposta['confidence']:.2f}")
    
    # 5. Estatísticas
    print("\n📊 Estatísticas:")
    stats = mock_services.get_comprehensive_stats()
    print(f"   Buckets: {stats['storage']['buckets_count']}")
    print(f"   Blobs: {stats['storage']['total_blobs']}")
    print(f"   Corpora: {stats['vertex_ai']['corpora_count']}")


def exemplo_simulacao_erros():
    """
    ⚠️ Simulação de Erros - Testando Cenários de Falha
    """
    print("\n⚠️ SIMULAÇÃO DE ERROS")
    print("=" * 50)
    
    from rag_enhanced.testing.mocks import MockServices
    
    mock_services = MockServices()
    
    # 1. Configurar simulação de erros
    print("🔧 Configurando simulação de erros...")
    mock_services.enable_error_simulation(
        network_rate=0.3,    # 30% de falhas de rede
        auth_rate=0.1,       # 10% de falhas de autenticação
        rate_limit_rate=0.2  # 20% de rate limiting
    )
    
    # 2. Testar operações com falhas
    print("\n🧪 Testando operações com falhas simuladas:")
    
    sucessos = 0
    falhas = 0
    
    for i in range(10):
        try:
            mock_services.storage.upload_blob(
                "bucket-teste", 
                f"arquivo_{i}.txt", 
                b"conteudo de teste"
            )
            sucessos += 1
            print(f"   ✅ Upload {i+1}: Sucesso")
        except Exception as e:
            falhas += 1
            print(f"   ❌ Upload {i+1}: {type(e).__name__}")
    
    print(f"\n📊 Resultados:")
    print(f"   Sucessos: {sucessos}/10 ({sucessos*10}%)")
    print(f"   Falhas: {falhas}/10 ({falhas*10}%)")
    
    # 3. Desabilitar simulação
    mock_services.disable_error_simulation()
    print("\n✅ Simulação de erros desabilitada")


def exemplo_cenarios_avancados():
    """
    🎭 Cenários Avançados - Configurações Específicas
    """
    print("\n🎭 CENÁRIOS AVANÇADOS")
    print("=" * 50)
    
    from rag_enhanced.testing.mocks import MockServices
    
    mock_services = MockServices()
    
    # 1. Cenário de alta latência
    print("⏱️ Testando cenário de alta latência:")
    mock_services.setup_scenario("high_latency")
    
    import time
    start = time.time()
    resposta = mock_services.vertex_ai.generate_content("Query com alta latência")
    tempo = time.time() - start
    print(f"   Tempo de resposta: {tempo:.2f}s")
    
    # 2. Cenário de problemas de rede
    print("\n🌐 Testando problemas de rede:")
    mock_services.setup_scenario("network_issues")
    
    tentativas = 5
    sucessos = 0
    
    for i in range(tentativas):
        try:
            mock_services.storage.create_bucket(f"bucket-rede-{i}")
            sucessos += 1
        except:
            pass
    
    print(f"   Sucessos com problemas de rede: {sucessos}/{tentativas}")
    
    # 3. Cenário de rate limiting
    print("\n🚫 Testando rate limiting:")
    mock_services.setup_scenario("rate_limiting")
    
    rate_limited = 0
    for i in range(8):  # Tentar mais que o limite
        try:
            mock_services.storage.create_bucket(f"bucket-rate-{i}")
        except:
            rate_limited += 1
    
    print(f"   Operações limitadas: {rate_limited}/8")
    
    # 4. Resetar para cenário normal
    mock_services.setup_scenario("normal")
    print("\n✅ Cenário resetado para normal")


def exemplo_dados_teste():
    """
    🎲 Geração de Dados de Teste
    """
    print("\n🎲 GERAÇÃO DE DADOS DE TESTE")
    print("=" * 50)
    
    from rag_enhanced.testing.mocks import MockServices
    
    mock_services = MockServices()
    
    # 1. Criar dados de teste realistas
    print("📄 Criando dados de teste:")
    arquivos_teste = mock_services.create_test_data(5)
    
    for i, arquivo in enumerate(arquivos_teste, 1):
        print(f"   {i}. {arquivo.name} ({arquivo.size} bytes)")
        print(f"      Tipo: {arquivo.mime_type}")
        print(f"      Prévia: {arquivo.content[:50]}...")
        print()
    
    # 2. Popular mock com dados realistas
    print("🏗️ Populando ambiente com dados realistas:")
    mock_services.create_realistic_test_data()
    
    # Verificar o que foi criado
    stats = mock_services.get_comprehensive_stats()
    print(f"   Buckets criados: {stats['storage']['buckets_count']}")
    print(f"   Arquivos: {stats['storage']['total_blobs']}")
    print(f"   Corpora: {stats['vertex_ai']['corpora_count']}")


def exemplo_integracao_completa():
    """
    🔄 Integração Completa - Fluxo End-to-End
    """
    print("\n🔄 INTEGRAÇÃO COMPLETA")
    print("=" * 50)
    
    from rag_enhanced.testing.mocks import MockServices
    from rag_enhanced.testing.generators import TestDataGenerator
    
    # 1. Inicializar componentes
    mock_services = MockServices()
    generator = TestDataGenerator()
    
    print("🚀 Simulando fluxo completo de RAG:")
    
    # 2. Preparar dados
    print("\n1️⃣ Preparando dados:")
    arquivos = generator.generate_test_files(3, ["python", "markdown"])
    
    for arquivo in arquivos:
        print(f"   📄 {arquivo.name} ({arquivo.language})")
    
    # 3. Criar infraestrutura
    print("\n2️⃣ Criando infraestrutura:")
    bucket = mock_services.storage.create_bucket("rag-pipeline-bucket")
    print(f"   📦 Bucket: {bucket.name}")
    
    corpus = mock_services.vertex_ai.create_corpus("rag-corpus", "Corpus principal")
    print(f"   🧠 Corpus: {corpus}")
    
    # 4. Upload de arquivos
    print("\n3️⃣ Fazendo upload dos arquivos:")
    for arquivo in arquivos:
        blob_name = mock_services.storage.upload_blob(
            "rag-pipeline-bucket",
            arquivo.name,
            arquivo.content.encode()
        )
        print(f"   ⬆️ {blob_name}")
    
    # 5. Importar para RAG
    print("\n4️⃣ Importando para RAG:")
    import_result = mock_services.vertex_ai.import_files(
        "rag-corpus",
        ["gs://rag-pipeline-bucket/*"]
    )
    print(f"   📥 Importação: {import_result}")
    
    # 6. Executar queries
    print("\n5️⃣ Executando queries:")
    queries = generator.generate_query_examples(3)
    
    for i, query_data in enumerate(queries, 1):
        query = query_data['text']
        resposta = mock_services.vertex_ai.generate_content(query, "rag-corpus")
        
        print(f"   {i}. Query: {query[:40]}...")
        print(f"      Resposta: {resposta['text'][:50]}...")
        print(f"      Confiança: {resposta['confidence']:.2f}")
        print()
    
    # 7. Estatísticas finais
    print("6️⃣ Estatísticas finais:")
    stats = mock_services.get_comprehensive_stats()
    print(f"   📊 Total de operações: {stats['storage']['operations']}")
    print(f"   📊 Arquivos processados: {stats['storage']['total_blobs']}")
    print(f"   📊 Queries executadas: {stats['vertex_ai']['query_count']}")


def exemplo_uso_com_framework():
    """
    🧪 Uso com Framework de Testes
    """
    print("\n🧪 USO COM FRAMEWORK DE TESTES")
    print("=" * 50)
    
    from rag_enhanced.testing.framework import TestRunner
    from rag_enhanced.testing.mocks import MockServices
    
    # 1. Integração com TestRunner
    print("🔧 Integrando MockServices com TestRunner:")
    
    runner = TestRunner()
    
    # O TestRunner já usa MockServices internamente
    resultado = runner.run_quick_test()
    
    print(f"   ✅ Testes executados: {resultado['total_tests']}")
    print(f"   ✅ Taxa de sucesso: {resultado['success_rate']:.1f}%")
    print(f"   ⏱️ Tempo total: {resultado['total_time']:.2f}s")
    
    # 2. Verificar saúde do sistema
    print("\n🏥 Verificando saúde do sistema:")
    saude = runner.check_system_health()
    
    status = "✅ Saudável" if saude['overall_healthy'] else "❌ Problemas"
    print(f"   Status: {status}")
    
    # 3. Teste com cenário específico
    print("\n🎭 Teste com cenário específico:")
    resultado_cenario = runner.run_with_scenario("high_latency")
    
    print(f"   ⚡ Sucesso com alta latência: {resultado_cenario['summary']['success_rate']:.1f}%")


def main():
    """
    Função principal - executa todos os exemplos
    """
    print("🎭 GUIA COMPLETO: COMO EXECUTAR MOCKSERVICES")
    print("=" * 60)
    print("Este guia mostra todas as formas de usar MockServices")
    print("para desenvolvimento sem dependências externas.\n")
    
    try:
        # Executar todos os exemplos
        exemplo_basico_mockservices()
        exemplo_simulacao_erros()
        exemplo_cenarios_avancados()
        exemplo_dados_teste()
        exemplo_integracao_completa()
        exemplo_uso_com_framework()
        
        print("\n🎉 GUIA CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("✅ MockServices funcionando perfeitamente")
        print("✅ Todos os cenários testados")
        print("✅ Simulação de erros validada")
        print("✅ Integração com framework confirmada")
        
        print("\n🚀 COMO USAR EM SEUS PROJETOS:")
        print("1. Importe: from rag_enhanced.testing.mocks import MockServices")
        print("2. Inicialize: mock_services = MockServices()")
        print("3. Use como se fosse o serviço real!")
        print("4. Configure cenários conforme necessário")
        print("5. Monitore com get_comprehensive_stats()")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        print("Verifique se todos os módulos estão instalados corretamente.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)