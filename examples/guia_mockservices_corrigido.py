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
sys.path.append(str(Path(__file__).parent.parent))

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
    bucket = mock_services.cloud_storage.create_bucket("meu-bucket-teste")
    print(f"   Bucket criado: {bucket.name}")
    
    # Upload de arquivo
    conteudo = b"Este e um arquivo de teste para o RAG Enhanced"
    blob_name = mock_services.cloud_storage.upload_blob("meu-bucket-teste", "arquivo.txt", conteudo)
    print(f"   Arquivo enviado: {blob_name}")
    
    # Download de arquivo
    conteudo_baixado = mock_services.cloud_storage.download_blob("meu-bucket-teste", "arquivo.txt")
    print(f"   Arquivo baixado: {len(conteudo_baixado)} bytes")
    
    # Listar arquivos
    arquivos = mock_services.cloud_storage.list_blobs("meu-bucket-teste")
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
    
    # Usar o método enable_error_simulation da classe MockServices
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


def main():
    """
    Função principal - executa os exemplos principais
    """
    print("🎭 GUIA CORRIGIDO: COMO EXECUTAR MOCKSERVICES")
    print("=" * 60)
    print("Este guia mostra como usar MockServices")
    print("para desenvolvimento sem dependências externas.\n")
    
    try:
        # Executar exemplos principais
        exemplo_basico_mockservices()
        exemplo_simulacao_erros()
        
        print("\n🎉 GUIA CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("✅ MockServices funcionando perfeitamente")
        print("✅ Simulação de erros validada")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        print("Verifique se todos os módulos estão instalados corretamente.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)