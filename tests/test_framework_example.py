#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Exemplo de Uso do Framework de Testes RAG Enhanced

Este arquivo demonstra como usar o framework de testes completo
para validar o sistema RAG Enhanced.
"""

import asyncio
import json
from pathlib import Path

# Importar o framework de testes
from rag_enhanced.testing import (
    TestRunner, 
    TestFramework,
    MockServices,
    TestDataGenerator,
    TestValidators,
    create_test_suite,
    run_quick_test,
    run_full_test,
    validate_system
)


def exemplo_teste_rapido():
    """
    🚀 Exemplo de teste rápido
    
    Executa apenas testes unitários básicos.
    """
    print("🚀 Executando Teste Rápido")
    print("=" * 50)
    
    # Usar função de conveniência
    results = run_quick_test()
    
    # Exibir resultados
    print(f"\n📊 Resultados:")
    print(f"  • Total de testes: {results['total_tests']}")
    print(f"  • Testes aprovados: {results['passed_tests']}")
    print(f"  • Testes falharam: {results['failed_tests']}")
    print(f"  • Taxa de sucesso: {results['success_rate']:.1f}%")
    print(f"  • Tempo total: {results['total_time']:.2f}s")
    
    return results


def exemplo_teste_completo():
    """
    🎯 Exemplo de teste completo
    
    Executa todos os tipos de teste: unitários, integração e performance.
    """
    print("\n🎯 Executando Teste Completo")
    print("=" * 50)
    
    # Usar função de conveniência
    results = run_full_test()
    
    # Exibir resumo
    summary = results['summary']
    print(f"\n📈 Resumo Geral:")
    print(f"  • Total de testes: {summary['total_tests']}")
    print(f"  • Testes aprovados: {summary['passed_tests']}")
    print(f"  • Testes falharam: {summary['failed_tests']}")
    print(f"  • Taxa de sucesso: {summary['success_rate']:.1f}%")
    print(f"  • Tempo total: {summary['total_time']:.2f}s")
    
    # Exibir detalhes por tipo
    for test_type in ['unit_tests', 'integration_tests', 'performance_tests']:
        if test_type in results:
            test_results = results[test_type]
            print(f"\n  📋 {test_type.replace('_', ' ').title()}:")
            print(f"    - Testes: {test_results['total_tests']}")
            print(f"    - Sucesso: {test_results['success_rate']:.1f}%")
            print(f"    - Tempo: {test_results['total_time']:.2f}s")
    
    return results


def exemplo_teste_customizado():
    """
    🔧 Exemplo de teste customizado
    
    Demonstra como criar e executar testes personalizados.
    """
    print("\n🔧 Executando Teste Customizado")
    print("=" * 50)
    
    # Criar framework personalizado
    framework = create_test_suite("custom_test_suite")
    
    # Configurar cenário específico
    framework.mock_services.setup_scenario("high_latency")
    
    # Executar apenas testes de performance
    results = framework.run_performance_tests()
    
    print(f"\n⚡ Resultados de Performance:")
    print(f"  • Cenário: Alta Latência")
    print(f"  • Testes executados: {results['total_tests']}")
    print(f"  • Taxa de sucesso: {results['success_rate']:.1f}%")
    print(f"  • Tempo total: {results['total_time']:.2f}s")
    
    # Exibir detalhes das suítes
    for suite in results['suites']:
        print(f"\n    📋 {suite['suite_name']}:")
        print(f"      - Testes: {suite['total_tests']}")
        print(f"      - Aprovados: {suite['passed_tests']}")
        print(f"      - Falharam: {suite['failed_tests']}")
        print(f"      - Tempo: {suite['total_time']:.2f}s")
    
    return results


def exemplo_geracao_dados():
    """
    🎲 Exemplo de geração de dados de teste
    
    Demonstra como gerar dados realistas para testes.
    """
    print("\n🎲 Gerando Dados de Teste")
    print("=" * 50)
    
    # Criar gerador
    generator = TestDataGenerator()
    
    # Gerar arquivos de código
    print("\n📄 Gerando arquivos de código...")
    code_files = generator.generate_test_files(count=5, languages=["python", "javascript"])
    
    for file in code_files:
        print(f"  • {file.name} ({file.language}, {file.complexity}) - {file.size_mb:.2f}MB")
    
    # Gerar documentação
    print("\n📚 Gerando documentação...")
    doc_files = generator.generate_documentation_files(count=3)
    
    for doc in doc_files:
        print(f"  • {doc.name} - {doc.size_mb:.2f}MB")
    
    # Gerar queries de teste
    print("\n❓ Gerando queries de teste...")
    queries = generator.generate_query_dataset(count=5)
    
    for query in queries:
        print(f"  • [{query['category']}] {query['text'][:50]}...")
    
    # Gerar cenários de erro
    print("\n⚠️ Gerando cenários de erro...")
    error_scenarios = generator.generate_error_scenarios()
    
    for scenario in error_scenarios:
        print(f"  • {scenario['name']}: {scenario['description']}")
    
    return {
        "code_files": code_files,
        "doc_files": doc_files,
        "queries": queries,
        "error_scenarios": error_scenarios
    }


def exemplo_validacao():
    """
    ✅ Exemplo de validação de dados
    
    Demonstra como validar diferentes tipos de dados.
    """
    print("\n✅ Validando Dados")
    print("=" * 50)
    
    # Criar validador
    validators = TestValidators()
    
    # Validar configuração
    print("\n🔧 Validando configuração...")
    config = {
        "project_id": "test-project-123",
        "location": "us-central1",
        "bucket_name": "test-bucket-valid",
        "max_file_size_mb": 50
    }
    
    config_result = validators.validate_config(config)
    print(f"  • Configuração válida: {config_result.is_valid}")
    if config_result.errors:
        print(f"  • Erros: {config_result.errors}")
    if config_result.warnings:
        print(f"  • Warnings: {config_result.warnings}")
    
    # Validar dados de arquivo
    print("\n📄 Validando arquivo...")
    file_data = {
        "name": "test_file.py",
        "content": "def hello(): return 'world'",
        "size": 1024,
        "mime_type": "text/x-python"
    }
    
    file_result = validators.validate_file_data(file_data)
    print(f"  • Arquivo válido: {file_result.is_valid}")
    if file_result.errors:
        print(f"  • Erros: {file_result.errors}")
    
    # Validar resultado de processamento
    print("\n⚙️ Validando resultado de processamento...")
    processing_result = {
        "status": "success",
        "timestamp": "2024-01-01T12:00:00Z",
        "data": {"processed_files": 10},
        "metrics": {"processing_time": 2.5, "success_rate": 0.95}
    }
    
    proc_result = validators.validate_processing_result(processing_result)
    print(f"  • Resultado válido: {proc_result.is_valid}")
    if proc_result.errors:
        print(f"  • Erros: {proc_result.errors}")
    
    return {
        "config_validation": config_result,
        "file_validation": file_result,
        "processing_validation": proc_result
    }


def exemplo_mocks():
    """
    🎭 Exemplo de uso de mocks
    
    Demonstra como usar os serviços simulados.
    """
    print("\n🎭 Testando com Mocks")
    print("=" * 50)
    
    # Criar serviços mock
    mock_services = MockServices()
    
    # Testar Google Cloud Storage
    print("\n☁️ Testando Google Cloud Storage...")
    try:
        # Criar bucket
        bucket = mock_services.storage.create_bucket("test-bucket")
        print(f"  • Bucket criado: {bucket['name']}")
        
        # Upload de arquivo
        content = b"Conteudo de teste para o arquivo"
        upload_result = mock_services.storage.upload_blob(
            "test-bucket", "test-file.txt", content
        )
        print(f"  • Arquivo enviado: {upload_result['name']} ({upload_result['size']} bytes)")
        
        # Listar arquivos
        blobs = mock_services.storage.list_blobs("test-bucket")
        print(f"  • Arquivos no bucket: {len(blobs)}")
        
    except Exception as e:
        print(f"  • Erro: {e}")
    
    # Testar Vertex AI
    print("\n🧠 Testando Vertex AI...")
    try:
        # Criar corpus
        corpus = mock_services.vertex_ai.create_corpus("test-corpus", "Test Corpus")
        print(f"  • Corpus criado: {corpus['name']}")
        
        # Importar documentos
        import_result = mock_services.vertex_ai.import_documents(
            "test-corpus", "gs://test-bucket/*"
        )
        print(f"  • Documentos importados: {import_result['documents_imported']}")
        
        # Fazer query
        query_result = mock_services.vertex_ai.generate_content(
            "Como funciona o sistema?", "test-corpus"
        )
        print(f"  • Query executada: {len(query_result['text'])} caracteres de resposta")
        print(f"  • Confiança: {query_result['confidence']:.2f}")
        
    except Exception as e:
        print(f"  • Erro: {e}")
    
    # Testar cenários de erro
    print("\n⚠️ Testando cenários de erro...")
    
    # Configurar alta taxa de falha
    mock_services.storage.set_failure_rate(0.8)
    
    success_count = 0
    error_count = 0
    
    for i in range(5):
        try:
            mock_services.storage.upload_blob(
                "test-bucket", f"error-test-{i}.txt", b"test"
            )
            success_count += 1
        except Exception:
            error_count += 1
    
    print(f"  • Sucessos: {success_count}, Erros: {error_count}")
    print(f"  • Taxa de erro real: {error_count / (success_count + error_count) * 100:.1f}%")
    
    # Obter estatísticas
    stats = mock_services.get_comprehensive_stats()
    print(f"\n📊 Estatísticas dos mocks:")
    print(f"  • Storage: {stats['storage']['total_blobs']} blobs, {stats['storage']['buckets_count']} buckets")
    print(f"  • Vertex AI: {stats['vertex_ai']['query_count']} queries, {stats['vertex_ai']['corpora_count']} corpora")
    
    return stats


def exemplo_health_check():
    """
    🏥 Exemplo de health check
    
    Demonstra como verificar a saúde do sistema.
    """
    print("\n🏥 Verificando Saúde do Sistema")
    print("=" * 50)
    
    # Usar função de conveniência
    health_results = validate_system()
    
    # Exibir status geral
    overall_status = "✅ Saudável" if health_results['overall_healthy'] else "❌ Problemas"
    print(f"\n🎯 Status Geral: {overall_status}")
    
    # Exibir detalhes dos checks
    print(f"\n🔍 Detalhes dos Health Checks:")
    for check_name, check_result in health_results['checks'].items():
        status_icon = "✅" if check_result['healthy'] else "❌"
        print(f"  {status_icon} {check_name}: {check_result.get('message', 'OK')}")
        
        if not check_result['healthy'] and 'details' in check_result:
            for key, value in check_result['details'].items():
                print(f"    - {key}: {value}")
    
    return health_results


def exemplo_relatorio_completo():
    """
    📊 Exemplo de relatório completo
    
    Gera um relatório abrangente de todos os testes.
    """
    print("\n📊 Gerando Relatório Completo")
    print("=" * 60)
    
    # Executar todos os testes
    all_results = {
        "quick_test": exemplo_teste_rapido(),
        "full_test": exemplo_teste_completo(),
        "data_generation": exemplo_geracao_dados(),
        "validation": exemplo_validacao(),
        "mocks": exemplo_mocks(),
        "health_check": exemplo_health_check()
    }
    
    # Salvar relatório
    report_path = Path("test_report_complete.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Relatório salvo em: {report_path}")
    
    # Resumo final
    print(f"\n🎉 Resumo Final:")
    print(f"  • Teste rápido: {all_results['quick_test']['success_rate']:.1f}% sucesso")
    print(f"  • Teste completo: {all_results['full_test']['summary']['success_rate']:.1f}% sucesso")
    print(f"  • Sistema saudável: {'Sim' if all_results['health_check']['overall_healthy'] else 'Não'}")
    print(f"  • Dados gerados: {len(all_results['data_generation']['code_files'])} arquivos de código")
    print(f"  • Validações: {len(all_results['validation'])} tipos testados")
    
    return all_results


def main():
    """
    🚀 Função principal - executa todos os exemplos
    """
    print("🧪 Framework de Testes RAG Enhanced - Exemplos")
    print("=" * 60)
    print("Este script demonstra todas as funcionalidades do framework de testes.")
    
    try:
        # Executar todos os exemplos
        exemplo_teste_rapido()
        exemplo_teste_customizado()
        exemplo_geracao_dados()
        exemplo_validacao()
        exemplo_mocks()
        exemplo_health_check()
        
        # Gerar relatório final
        exemplo_relatorio_completo()
        
        print(f"\n🎉 Todos os exemplos executados com sucesso!")
        print(f"📋 Verifique o arquivo 'test_report_complete.json' para detalhes completos.")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()