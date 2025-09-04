#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 DEMONSTRAÇÃO COMPLETA - Framework de Testes RAG Enhanced

Este script demonstra todas as funcionalidades do framework de testes
desenvolvido para o sistema RAG Enhanced, incluindo:

- Testes unitários, integração e performance
- Mocks completos dos serviços Google Cloud
- Geração de dados de teste realistas
- Validação automática
- Relatórios detalhados
- Cenários de erro e recuperação

🚀 EXECUÇÃO: python demo_framework_testes.py
"""

import sys
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from rag_enhanced.testing.framework import TestRunner, TestFramework
from rag_enhanced.testing.mocks import MockServices
from rag_enhanced.testing.generators import TestDataGenerator
from rag_enhanced.testing.validators import TestValidators


def print_header(title: str, char: str = "=", width: int = 60):
    """Imprime cabeçalho formatado"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")


def print_section(title: str):
    """Imprime seção"""
    print(f"\n🔹 {title}")
    print("-" * (len(title) + 4))


def demo_test_runner():
    """Demonstra o TestRunner - interface principal"""
    print_header("🏃 DEMO: TEST RUNNER", "🚀")
    
    print("O TestRunner é a interface principal para executar testes.")
    print("Oferece diferentes tipos de execução:")
    
    runner = TestRunner()
    
    # Teste rápido (apenas unitários)
    print_section("Teste Rápido (Unitários)")
    result = runner.run_quick_test()
    print(f"✅ Resultado: {result['success_rate']:.1f}% de sucesso")
    print(f"⏱️ Tempo: {result['total_time']:.2f}s")
    print(f"📊 Testes: {result['passed_tests']}/{result['total_tests']}")
    
    # Verificação de saúde do sistema
    print_section("Verificação de Saúde")
    health = runner.check_system_health()
    status = "✅ Saudável" if health['overall_healthy'] else "❌ Problemas"
    print(f"🏥 Status do sistema: {status}")
    
    # Teste com cenário específico
    print_section("Teste com Cenário de Alta Latência")
    scenario_result = runner.run_with_scenario("high_latency")
    print(f"⚡ Resultado com alta latência: {scenario_result['summary']['success_rate']:.1f}%")


def demo_mock_services():
    """Demonstra os MockServices - simulação completa"""
    print_header("🎭 DEMO: MOCK SERVICES", "🎪")
    
    print("Os MockServices simulam completamente os serviços Google Cloud")
    print("sem necessidade de conexão real ou credenciais.")
    
    mock_services = MockServices()
    
    # Operações básicas
    print_section("Operações Básicas")
    
    # Cloud Storage
    bucket = mock_services.storage.create_bucket("demo-bucket")
    print(f"📦 Bucket criado: {bucket.name}")
    
    # Upload de arquivo
    content = b"Conteudo de demonstracao do RAG Enhanced"
    blob = mock_services.storage.upload_blob("demo-bucket", "demo.txt", content)
    print(f"📄 Arquivo enviado: {blob}")
    
    # Vertex AI
    corpus = mock_services.vertex_ai.create_corpus("demo-corpus", "Corpus de demonstração")
    print(f"🧠 Corpus criado: {corpus}")
    
    # Query
    response = mock_services.vertex_ai.generate_content("Como funciona o RAG?", "demo-corpus")
    print(f"💬 Resposta gerada: {response['text'][:50]}...")
    
    # Estatísticas
    print_section("Estatísticas dos Mocks")
    stats = mock_services.get_comprehensive_stats()
    print(f"📊 Buckets: {stats['storage']['buckets_count']}")
    print(f"📊 Blobs: {stats['storage']['total_blobs']}")
    print(f"📊 Corpora: {stats['vertex_ai']['corpora_count']}")
    
    # Simulação de erros
    print_section("Simulação de Erros")
    mock_services.enable_error_simulation(network_rate=0.3, auth_rate=0.1)
    print("⚠️ Simulação de erros habilitada (30% rede, 10% auth)")
    
    # Tentar operação com falhas
    try:
        for i in range(5):
            mock_services.storage.upload_blob("demo-bucket", f"test_{i}.txt", b"test")
            print(f"  ✅ Upload {i+1} bem-sucedido")
    except Exception as e:
        print(f"  ❌ Falha simulada: {type(e).__name__}")
    
    mock_services.disable_error_simulation()
    print("✅ Simulação de erros desabilitada")


def demo_test_data_generator():
    """Demonstra o TestDataGenerator - geração de dados realistas"""
    print_header("🎲 DEMO: TEST DATA GENERATOR", "🎯")
    
    print("O TestDataGenerator cria dados de teste realistas para diferentes")
    print("linguagens de programação e tipos de arquivo.")
    
    generator = TestDataGenerator()
    
    # Gerar arquivos de código
    print_section("Geração de Arquivos de Código")
    test_files = generator.generate_test_files(3, languages=["python", "javascript"])
    
    for file in test_files:
        print(f"📄 {file.name} ({file.language}, {file.complexity})")
        print(f"   Tamanho: {file.size_mb:.2f}MB")
        print(f"   Prévia: {file.content[:100]}...")
        print()
    
    # Gerar documentação
    print_section("Geração de Documentação")
    docs = generator.generate_documentation_files(2)
    
    for doc in docs:
        print(f"📚 {doc.name}")
        print(f"   Tamanho: {doc.size} bytes")
        print(f"   Prévia: {doc.content[:80]}...")
        print()
    
    # Gerar queries de exemplo
    print_section("Geração de Queries")
    queries = generator.generate_query_examples(3)
    
    for query in queries:
        print(f"❓ {query['text']}")
        print(f"   Categoria: {query['category']}, Complexidade: {query['complexity']}")
        print()
    
    # Cenários de erro
    print_section("Cenários de Erro")
    error_scenarios = generator.generate_error_scenarios()
    
    for scenario in error_scenarios[:3]:
        print(f"⚠️ {scenario['name']}: {scenario['description']}")
        print(f"   Tipo: {scenario['error_type']}")
        print(f"   Recuperação: {scenario['recovery_action']}")
        print()


def demo_validators():
    """Demonstra os TestValidators - validação automática"""
    print_header("✅ DEMO: TEST VALIDATORS", "🔍")
    
    print("Os TestValidators fornecem validação automática de configurações,")
    print("dados e estruturas do sistema.")
    
    validators = TestValidators()
    
    # Validação de configuração
    print_section("Validação de Configuração")
    
    # Configuração válida
    valid_config = {
        "project_id": "meu-projeto-rag",
        "location": "us-central1",
        "bucket_name": "meu-bucket-rag"
    }
    
    result = validators.validate_config(valid_config)
    print(f"✅ Configuração válida: {result.is_valid}")
    
    # Configuração inválida
    invalid_config = {
        "project_id": "",  # Vazio
        "location": "invalid-location",  # Inválida
        "bucket_name": "INVALID_BUCKET_NAME"  # Maiúsculas não permitidas
    }
    
    result = validators.validate_config(invalid_config)
    print(f"❌ Configuração inválida: {result.is_valid}")
    print(f"   Erros: {len(result.errors)}")
    for error in result.errors[:2]:
        print(f"   - {error}")
    
    # Validação de estrutura de dados
    print_section("Validação de Estrutura")
    
    # Dados válidos
    valid_data = {
        "files": [
            {"name": "test.py", "size": 1024, "type": "python"},
            {"name": "doc.md", "size": 512, "type": "markdown"}
        ],
        "metadata": {
            "created_at": "2024-01-01T12:00:00Z",
            "version": "1.0.0"
        }
    }
    
    structure_result = validators.validate_data_structure(valid_data)
    print(f"✅ Estrutura válida: {structure_result.is_valid}")
    
    # Validação de performance
    print_section("Validação de Performance")
    
    performance_data = {
        "response_time": 150,  # ms
        "memory_usage": 256,   # MB
        "cpu_usage": 45,       # %
        "throughput": 1000     # req/s
    }
    
    perf_result = validators.validate_performance_metrics(performance_data)
    print(f"⚡ Performance adequada: {perf_result.is_valid}")
    
    if not perf_result.is_valid:
        for warning in perf_result.warnings:
            print(f"   ⚠️ {warning}")


def demo_complete_workflow():
    """Demonstra um fluxo completo de teste"""
    print_header("🔄 DEMO: FLUXO COMPLETO", "🌟")
    
    print("Demonstração de um fluxo completo de teste do sistema RAG Enhanced")
    print("simulando um cenário real de desenvolvimento.")
    
    # 1. Configurar ambiente de teste
    print_section("1. Configuração do Ambiente")
    framework = TestFramework()
    print("✅ Framework de testes inicializado")
    
    # 2. Gerar dados de teste
    print_section("2. Geração de Dados de Teste")
    generator = TestDataGenerator()
    test_files = generator.generate_test_files(5)
    queries = generator.generate_query_examples(3)
    print(f"✅ Gerados {len(test_files)} arquivos e {len(queries)} queries")
    
    # 3. Executar testes unitários
    print_section("3. Testes Unitários")
    unit_results = framework.run_unit_tests()
    print(f"✅ Unitários: {unit_results['success_rate']:.1f}% sucesso")
    
    # 4. Executar testes de integração
    print_section("4. Testes de Integração")
    integration_results = framework.run_integration_tests()
    print(f"✅ Integração: {integration_results['success_rate']:.1f}% sucesso")
    
    # 5. Testes de performance
    print_section("5. Testes de Performance")
    performance_results = framework.run_performance_tests()
    print(f"✅ Performance: {performance_results['success_rate']:.1f}% sucesso")
    
    # 6. Validação de saúde
    print_section("6. Validação de Saúde")
    health_results = framework.validate_system_health()
    status = "✅ Saudável" if health_results['overall_healthy'] else "❌ Problemas"
    print(f"🏥 Sistema: {status}")
    
    # 7. Relatório final
    print_section("7. Relatório Final")
    total_tests = (unit_results['total_tests'] + 
                  integration_results['total_tests'] + 
                  performance_results['total_tests'])
    
    total_passed = (unit_results['passed_tests'] + 
                   integration_results['passed_tests'] + 
                   performance_results['passed_tests'])
    
    overall_success = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total de testes: {total_tests}")
    print(f"✅ Sucessos: {total_passed}")
    print(f"📈 Taxa geral de sucesso: {overall_success:.1f}%")


def demo_advanced_scenarios():
    """Demonstra cenários avançados de teste"""
    print_header("🚀 DEMO: CENÁRIOS AVANÇADOS", "⚡")
    
    print("Demonstração de cenários avançados incluindo simulação de falhas,")
    print("recuperação automática e testes de stress.")
    
    mock_services = MockServices()
    
    # Cenário 1: Falhas de rede intermitentes
    print_section("Cenário 1: Falhas de Rede Intermitentes")
    mock_services.setup_scenario("network_issues")
    
    success_count = 0
    total_attempts = 10
    
    for i in range(total_attempts):
        try:
            mock_services.storage.upload_blob("test-bucket", f"file_{i}.txt", b"test")
            success_count += 1
        except Exception:
            pass  # Falha esperada
    
    print(f"📊 Sucessos: {success_count}/{total_attempts} ({success_count/total_attempts*100:.1f}%)")
    
    # Cenário 2: Alta latência
    print_section("Cenário 2: Alta Latência")
    mock_services.setup_scenario("high_latency")
    
    start_time = time.time()
    try:
        mock_services.vertex_ai.generate_content("Test query with high latency")
        response_time = (time.time() - start_time) * 1000
        print(f"⏱️ Tempo de resposta: {response_time:.0f}ms")
    except Exception as e:
        print(f"❌ Falha: {e}")
    
    # Cenário 3: Rate limiting
    print_section("Cenário 3: Rate Limiting")
    mock_services.setup_scenario("rate_limiting")
    
    rate_limited = 0
    for i in range(15):  # Tentar mais que o limite
        try:
            mock_services.storage.create_bucket(f"bucket-{i}")
        except Exception:
            rate_limited += 1
    
    print(f"🚫 Requisições limitadas: {rate_limited}/15")
    
    # Cenário 4: Degradação de serviço
    print_section("Cenário 4: Degradação de Serviço")
    mock_services.setup_scenario("service_degradation")
    
    degraded_performance = []
    for i in range(5):
        start = time.time()
        try:
            mock_services.vertex_ai.generate_content(f"Query {i}")
            elapsed = (time.time() - start) * 1000
            degraded_performance.append(elapsed)
        except Exception:
            degraded_performance.append(float('inf'))
    
    avg_time = sum(t for t in degraded_performance if t != float('inf')) / len([t for t in degraded_performance if t != float('inf')])
    print(f"⚡ Tempo médio degradado: {avg_time:.0f}ms")


def main():
    """Função principal da demonstração"""
    print_header("🎯 FRAMEWORK DE TESTES RAG ENHANCED", "🌟", 80)
    
    print("""
Este é o framework de testes completo desenvolvido para o sistema RAG Enhanced.
Ele oferece capacidades avançadas de teste sem dependências externas:

🧪 Testes Unitários, Integração e Performance
🎭 Mocks completos dos serviços Google Cloud  
🎲 Geração automática de dados de teste realistas
✅ Validação automática de configurações e dados
📊 Relatórios detalhados e métricas de performance
⚠️ Simulação de cenários de erro e recuperação
🔄 Fluxos completos de teste end-to-end

Vamos explorar cada funcionalidade:
""")
    
    try:
        # Executar todas as demonstrações
        demo_test_runner()
        demo_mock_services()
        demo_test_data_generator()
        demo_validators()
        demo_complete_workflow()
        demo_advanced_scenarios()
        
        # Conclusão
        print_header("🎉 DEMONSTRAÇÃO CONCLUÍDA", "✨", 80)
        print("""
✅ Todas as funcionalidades do framework foram demonstradas com sucesso!

O framework de testes RAG Enhanced está pronto para uso e oferece:

🚀 Desenvolvimento rápido sem dependências externas
🛡️ Testes robustos com simulação de cenários reais  
📈 Métricas detalhadas para otimização de performance
🔧 Ferramentas completas para debugging e validação

Para usar o framework em seus projetos:

1. Importe as classes necessárias:
   from rag_enhanced.testing.framework import TestRunner
   
2. Execute testes:
   runner = TestRunner()
   results = runner.run_full_test()
   
3. Analise os resultados e otimize seu código!

🎯 Framework de Testes RAG Enhanced - Pronto para produção! 🎯
""")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        print("Verifique se todos os módulos estão instalados corretamente.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)