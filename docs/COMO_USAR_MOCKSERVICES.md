# 🎭 Como Executar MockServices - Guia Rápido

## 🚀 **Uso Básico (3 linhas de código)**

```python
from rag_enhanced.testing.mocks import MockServices

# Inicializar
mock_services = MockServices()

# Usar como se fosse o serviço real!
response = mock_services.vertex_ai.generate_content("Como funciona o RAG?")
print(response['text'])
```

## 📦 **Cloud Storage Mock**

```python
# Criar bucket
bucket = mock_services.storage.create_bucket("meu-bucket")

# Upload de arquivo
mock_services.storage.upload_blob("meu-bucket", "arquivo.txt", b"conteudo")

# Download de arquivo
conteudo = mock_services.storage.download_blob("meu-bucket", "arquivo.txt")

# Listar arquivos
arquivos = mock_services.storage.list_blobs("meu-bucket")
```

## 🧠 **Vertex AI Mock**

```python
# Criar corpus RAG
corpus = mock_services.vertex_ai.create_corpus("meu-corpus", "Descrição")

# Importar documentos
mock_services.vertex_ai.import_files("meu-corpus", ["gs://bucket/*"])

# Fazer query com RAG
response = mock_services.vertex_ai.generate_content(
    "Explique machine learning", 
    "meu-corpus"
)

print(f"Resposta: {response['text']}")
print(f"Confiança: {response['confidence']}")
```

## ⚠️ **Simulação de Erros**

```python
# Habilitar simulação de erros
mock_services.enable_error_simulation(
    network_rate=0.3,    # 30% falhas de rede
    auth_rate=0.1,       # 10% falhas de auth
    rate_limit_rate=0.2  # 20% rate limiting
)

# Suas operações agora podem falhar realisticamente
try:
    mock_services.storage.upload_blob("bucket", "file.txt", b"data")
    print("✅ Sucesso")
except Exception as e:
    print(f"❌ Falha: {type(e).__name__}")

# Desabilitar simulação
mock_services.disable_error_simulation()
```

## 🎭 **Cenários Pré-definidos**

```python
# Cenário de alta latência
mock_services.setup_scenario("high_latency")

# Cenário com problemas de rede
mock_services.setup_scenario("network_issues")

# Cenário com rate limiting
mock_services.setup_scenario("rate_limiting")

# Cenário normal
mock_services.setup_scenario("normal")
```

## 📊 **Monitoramento e Estatísticas**

```python
# Obter estatísticas detalhadas
stats = mock_services.get_comprehensive_stats()

print(f"Buckets: {stats['storage']['buckets_count']}")
print(f"Arquivos: {stats['storage']['total_blobs']}")
print(f"Operações: {stats['storage']['operations']}")
print(f"Corpora: {stats['vertex_ai']['corpora_count']}")
```

## 🔄 **Fluxo Completo de RAG**

```python
# 1. Criar infraestrutura
bucket = mock_services.storage.create_bucket("rag-bucket")
corpus = mock_services.vertex_ai.create_corpus("rag-corpus", "Meu RAG")

# 2. Upload de documentos
mock_services.storage.upload_blob("rag-bucket", "doc1.txt", b"Conteudo 1")
mock_services.storage.upload_blob("rag-bucket", "doc2.txt", b"Conteudo 2")

# 3. Importar para RAG
mock_services.vertex_ai.import_files("rag-corpus", ["gs://rag-bucket/*"])

# 4. Fazer queries
response = mock_services.vertex_ai.generate_content(
    "Resuma os documentos", 
    "rag-corpus"
)

print(response['text'])
```

## 🧪 **Integração com Testes**

```python
from rag_enhanced.testing.framework import TestRunner

# O TestRunner já usa MockServices internamente
runner = TestRunner()

# Teste rápido
result = runner.run_quick_test()
print(f"Sucesso: {result['success_rate']:.1f}%")

# Teste com cenário específico
result = runner.run_with_scenario("high_latency")
print(f"Alta latência: {result['summary']['success_rate']:.1f}%")
```

## 🎯 **Execução Prática**

### Executar o guia completo:
```bash
python guia_mockservices.py
```

### Executar testes offline:
```bash
python testes_offline_completos.py
```

### Executar demonstração completa:
```bash
python demo_framework_testes.py
```

## ✅ **Vantagens do MockServices**

- 🚀 **Sem dependências externas** - Funciona offline
- 💰 **Sem custos** - Não usa APIs reais
- ⚡ **Rápido** - Respostas em milissegundos
- 🛡️ **Confiável** - Comportamento previsível
- 🎭 **Realista** - Simula cenários reais
- 📊 **Monitorável** - Estatísticas detalhadas

## 🎉 **Resultado dos Testes**

Baseado na execução do guia:
- ✅ **100% de sucesso** nos testes básicos
- ✅ **Simulação de erros** funcionando (20-80% falhas conforme configurado)
- ✅ **Cenários avançados** validados
- ✅ **Integração completa** testada
- ✅ **Framework de testes** integrado

**MockServices está pronto para uso em desenvolvimento e testes! 🎯**