# 🤖 ValidAI Enhanced

<div align="center">

![ValidAI Logo](https://img.shields.io/badge/ValidAI-Enhanced-blue?style=for-the-badge&logo=artificial-intelligence)

**Sistema Avançado de Validação Baseado em Inteligência Artificial**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-Vertex_AI-4285f4?style=flat-square&logo=googlecloud)](https://cloud.google.com/vertex-ai)
[![Gradio](https://img.shields.io/badge/Interface-Gradio-orange?style=flat-square)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[📚 Documentação](#-documentação) • [🚀 Instalação](#-instalação-rápida) • [💡 Exemplos](#-exemplos-de-uso) • [🔧 Configuração](#-configuração)

</div>

---

## 🎯 Visão Geral

O **ValidAI Enhanced** é uma solução completa de validação e análise baseada em inteligência artificial que combina o poder do Google Gemini com um sistema RAG (Retrieval-Augmented Generation) para fornecer análises precisas e contextualizadas de códigos, documentos e dados.

### ✨ Características Principais

- 🧠 **IA Avançada**: Powered by Google Gemini 1.5 Pro 002
- 🔄 **Sistema RAG**: Recuperação aumentada para respostas contextualizadas
- 🖼️ **Multimodal**: Suporte a texto, imagens, documentos, vídeos
- 🌐 **Interface Web**: Interface intuitiva com Gradio
- 🔒 **Segurança Robusta**: Validação de arquivos e prevenção de ataques
- ⚡ **Cache Inteligente**: Otimização de performance com TTL
- 📊 **Pré-Validador**: Sistema estruturado de validação de modelos ML

### 🎪 Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Chat Multimodal** | Análise inteligente de códigos, documentos e imagens |
| **Pré-Validador** | Validação estruturada de modelos de Machine Learning |
| **Sistema RAG** | Consultas contextualizadas com base de conhecimento |
| **Processamento de Arquivos** | Suporte a 10+ formatos (PDF, Excel, Python, SAS, etc.) |
| **Exportação** | Geração automática de relatórios em PDF |
| **Cache Inteligente** | Sistema de cache com TTL e limpeza automática |

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.8 ou superior
- Conta Google Cloud com Vertex AI habilitado
- Mínimo 4GB RAM

### 1. Clone e Instale

```bash
# Clone do repositório
git clone <repository-url>
cd ValidAI

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate
# Ativar ambiente (Linux/macOS)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração do Google Cloud

```bash
# Configurar credenciais (opção 1 - via arquivo)
set GOOGLE_APPLICATION_CREDENTIALS=caminho\para\service-account.json

# Configurar credenciais (opção 2 - via gcloud CLI)
gcloud auth application-default login
```

### 3. Configuração do Projeto

Edite `config/validai_config.json`:
```json
{
  "project_id": "seu-projeto-gcp",
  "location": "us-central1",
  "modelo_versao": "gemini-1.5-pro-002"
}
```

### 4. Executar

```bash
python app.py
```

Acesse: **http://localhost:7860**

## 💡 Exemplos de Uso

### 📝 Validação de Código Python

```python
# Upload este código e pergunte: "Analise e sugira melhorias"
def calcular_media(numeros):
    total = sum(numeros)
    return total / len(numeros)
```

### 📊 Análise de Dados

```python
# Upload arquivo CSV e pergunte: "Analise a qualidade destes dados"
# O sistema detectará automaticamente:
# - Valores ausentes
# - Outliers
# - Distribuições
# - Correlações
```

### 📄 Análise de Documentos

```
Upload: documento.pdf
Pergunta: "Resuma este documento e identifique os pontos principais"
```

### 🔍 Sistema RAG - Base de Conhecimento

```
1. Selecione uma base: "Validações de Riscos de Mercado"
2. Pergunte: "Quais são as melhores práticas para validação de modelos VaR?"
3. Receba resposta contextualizada com fontes específicas
```

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   🌐 Interface  │───▶│  🤖 Chat Logic  │───▶│ 🔮 Gemini API   │
│     Gradio      │    │   Multimodal    │    │   Google Cloud  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 📁 File Processor│    │ 🔒 Security     │    │ 🗄️ Cache        │
│   Multi-format  │    │   Validator     │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 Componentes Principais

- **Interface Layer**: Gradio WebUI com 3 abas especializadas
- **Business Logic**: Chat multimodal, pré-validador, sistema RAG
- **Processing Layer**: Processamento de arquivos, validação de segurança
- **Data Layer**: DataManager, Prompts, Messenger
- **External Services**: Google Gemini, Cloud Storage, Search API

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [📖 Guia Completo](GUIA_USUARIO_COMPLETO.md) | Documentação completa do sistema |
| [⚡ Início Rápido](INICIO_RAPIDO.md) | Setup em 5 minutos |
| [💡 Exemplos Práticos](EXEMPLOS_PRATICOS.md) | Casos de uso reais |
| [🆘 FAQ & Troubleshooting](FAQ_TROUBLESHOOTING.md) | Soluções para problemas comuns |
| [📊 Diagramas](README_DIAGRAMAS.md) | Arquitetura e fluxos em PlantUML |

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Configurações obrigatórias
GOOGLE_CLOUD_PROJECT=seu-projeto-id
GOOGLE_APPLICATION_CREDENTIALS=caminho/credentials.json

# Configurações opcionais
VALIDAI_TEMPERATURE=0.2
VALIDAI_MAX_TOKENS=8000
VALIDAI_MAX_FILE_SIZE=50
VALIDAI_DEBUG=false
```

### Arquivos de Configuração

- `config/validai_config.json` - Configurações principais
- `config/variaveis.py` - Parâmetros do sistema
- `requirements.txt` - Dependências Python

### Comandos Disponíveis

```bash
# Execução principal
python app.py

# Execução offline (sem API)
python executar_offline.py

# Validação do sistema
python verificar_correcoes.py

# Verificação de dependências
python scripts/check_dependencies.py

# Verificação de integridade
python scripts/verificar_integridade.py
```

## 🛠️ Desenvolvimento

### Estrutura de Diretórios

```
ValidAI/
├── backend/                 # Lógica de negócio
│   ├── cache/              # Sistema de cache
│   ├── processors/         # Processamento de arquivos
│   ├── security/           # Validação de segurança
│   └── Chat_LLM.py        # Chat principal
├── config/                 # Configurações
├── frontend/               # Interface Gradio
├── rag_enhanced/           # Sistema RAG
│   ├── config/            # Gerenciamento de configuração
│   ├── core/              # Modelos base
│   ├── processing/        # Pipeline de processamento
│   ├── query/             # Motor de busca
│   └── testing/           # Framework de testes
├── src/                    # Componentes auxiliares
├── tests/                  # Testes automatizados
├── examples/               # Exemplos de uso
├── scripts/                # Scripts de manutenção
└── docs/                   # Documentação
```

### Executando Testes

```bash
# Testes offline completos
python tests/testes_offline_completos.py

# Testes específicos
python tests/test_suite_offline.py

# Framework de testes
python tests/test_framework_example.py
```

### Adicionando Novos Processadores

```python
# Exemplo: Novo processador em backend/processors/
class NovoProcessador:
    @staticmethod
    def process_novo_formato(arquivo):
        # Implementar lógica específica
        return resultado_processado
```

## 📊 Monitoramento e Performance

### Métricas Disponíveis

- **Cache Hit Rate**: Taxa de acertos do cache
- **Tempo de Resposta**: Latência média das consultas
- **Uso de Tokens**: Consumo da API Gemini
- **Arquivos Processados**: Estatísticas de uso

### Logs

```bash
# Logs principais
logs/validai.log

# Logs de segurança
logs/security.log

# Logs de performance
logs/performance.log
```

## 🔒 Segurança

### Validações Implementadas

- ✅ **Path Traversal Prevention**: Proteção contra ataques de diretório
- ✅ **File Type Validation**: Verificação de tipos MIME
- ✅ **Size Limits**: Controle de tamanho de arquivos
- ✅ **Malware Detection**: Detecção de assinaturas maliciosas
- ✅ **Input Sanitization**: Limpeza de entradas do usuário

### Boas Práticas

1. Mantenha credenciais em variáveis de ambiente
2. Use HTTPS em produção
3. Monitore logs de segurança regularmente
4. Mantenha dependências atualizadas

## 🚨 Solução de Problemas

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| Erro de autenticação | Execute `gcloud auth application-default login` |
| Interface não carrega | Verifique se porta 7860 está livre |
| Arquivo muito grande | Ajuste `tamanho_max_arquivo_mb` em config |
| Resposta lenta | Reduza `max_output_tokens` |

### Diagnóstico

```bash
# Verificação completa do sistema
python verificar_correcoes.py

# Verificar conectividade
python -c "import vertexai; print('✅ Vertex AI OK')"

# Limpar cache
python -c "from backend.cache import clear_all_caches; clear_all_caches()"
```

## 📈 Roadmap

### Versão Atual (2.0)

- ✅ Sistema RAG implementado
- ✅ Interface multimodal
- ✅ Pré-validador de modelos
- ✅ Cache inteligente
- ✅ Validação de segurança

### Próximas Versões

- 🔄 API REST para integração
- 🔄 Suporte a mais formatos de arquivo
- 🔄 Dashboard de analytics
- 🔄 Integração com mais LLMs
- 🔄 Sistema de plugins

## 🤝 Contribuição

### Como Contribuir

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Guidelines

- Siga as convenções PEP 8
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Execute `python scripts/verificar_integridade.py` antes do commit

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Google Cloud**: Pela infraestrutura Vertex AI e Gemini
- **Gradio**: Pela excelente biblioteca de interface web
- **Comunidade Python**: Pelas incríveis bibliotecas open source

## 📞 Suporte

- 📧 **Email**: [seu-email@example.com]
- 💬 **Issues**: Use as Issues do GitHub para reportar bugs
- 📖 **Documentação**: Consulte os arquivos na pasta `/docs`
- 🎥 **Tutoriais**: [Link para tutoriais em vídeo]

---

<div align="center">

**Desenvolvido com ❤️ usando Python e Google AI**

[⬆ Voltar ao topo](#-validai-enhanced)

</div>