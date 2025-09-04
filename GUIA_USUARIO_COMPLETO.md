# 📖 Guia de Usuário Completo - ValidAI Enhanced

## 🎯 Visão Geral

O **ValidAI Enhanced** é um sistema avançado de validação baseado em inteligência artificial que utiliza o Google Gemini para análise multimodal de códigos, documentos e dados. O sistema oferece validação automática, análise de qualidade e suporte para múltiplos formatos de arquivo.

### 🌟 Principais Características

- **IA Avançada**: Powered by Google Gemini 1.5 Pro 002
- **Multimodal**: Suporte a texto, imagens, documentos, vídeos
- **RAG Enhanced**: Sistema de recuperação aumentada para respostas contextualizadas
- **Interface Web**: Interface intuitiva com Gradio
- **Segurança Robusta**: Validação de arquivos e prevenção de ataques
- **Cache Inteligente**: Otimização de performance com cache TTL

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Conta Google Cloud com Vertex AI habilitado
- Mínimo 4GB RAM
- 2GB espaço livre em disco

### 1. Instalação das Dependências

```bash
# Instalar dependências principais
pip install -r requirements.txt

# Verificar instalação
python -c "import google.cloud.storage, vertexai, gradio; print('✅ Dependências OK')"
```

### 2. Configuração da Autenticação Google Cloud

```bash
# Definir credenciais (substitua pelo caminho do seu arquivo JSON)
set GOOGLE_APPLICATION_CREDENTIALS=caminho\para\seu\service-account.json

# Ou configurar via gcloud CLI
gcloud auth application-default login
```

### 3. Configuração do Projeto

Edite o arquivo `config/validai_config.json`:

```json
{
  "project_id": "seu-projeto-gcp",
  "location": "us-central1",
  "modelo_versao": "gemini-1.5-pro-002",
  "temperatura": 0.2,
  "max_output_tokens": 8000
}
```

### 4. Executando o Sistema

```bash
# Executar ValidAI
python app.py

# O sistema será iniciado em http://localhost:7860
```

## 💻 Interface do Sistema

### Tela Principal

A interface é dividida em três seções principais:

1. **🤖 Assistente AI**: Chat principal com o ValidAI
2. **📁 Upload de Arquivos**: Área para envio de documentos
3. **⚙️ Configurações**: Painel de configurações avançadas

### Tipos de Entrada Suportados

- **Texto**: Perguntas diretas, código para análise
- **Arquivos**: PDF, Word, Excel, Python, SAS, Jupyter notebooks
- **Imagens**: PNG, JPG, GIF para análise visual
- **Múltiplos arquivos**: Até 10 arquivos simultâneos (50MB cada)

## 🔧 Funcionalidades Principais

### 1. Validação de Código

**Como usar:**
1. Cole seu código na área de texto ou faça upload do arquivo
2. O ValidAI analisa automaticamente:
   - Sintaxe e estrutura
   - Boas práticas de programação
   - Potenciais bugs e vulnerabilidades
   - Sugestões de melhoria

**Exemplo de pergunta:**
```
"Analise este código Python e identifique possíveis problemas de performance"
```

### 2. Análise de Documentos

**Formatos suportados:** PDF, DOCX, TXT, MD

**Funcionalidades:**
- Extração e análise de conteúdo
- Verificação de conformidade
- Sumarização automática
- Detecção de inconsistências

### 3. Validação de Dados

**Para arquivos CSV/Excel:**
- Análise de qualidade dos dados
- Detecção de valores ausentes
- Identificação de outliers
- Sugestões de limpeza

### 4. Sistema RAG (Recuperação Aumentada)

O sistema mantém uma base de conhecimento que é consultada automaticamente para fornecer respostas mais precisas e contextualizadas.

## 📋 Casos de Uso Práticos

### Caso 1: Validação de Modelo Estatístico

1. **Upload** do arquivo .py ou .ipynb
2. **Pergunta**: "Valide este modelo de machine learning"
3. **Análise**: O ValidAI verifica:
   - Preparação dos dados
   - Seleção de features
   - Validação cruzada
   - Métricas de avaliação
   - Overfitting/Underfitting

### Caso 2: Revisão de Documentação

1. **Upload** de documento PDF/Word
2. **Pergunta**: "Revise esta documentação técnica"
3. **Análise**: Verificação de:
   - Clareza e completude
   - Estrutura e organização
   - Consistência terminológica
   - Exemplos práticos

### Caso 3: Análise de Base de Dados

1. **Upload** de arquivo CSV/Excel
2. **Pergunta**: "Analise a qualidade destes dados"
3. **Análise**: Relatório sobre:
   - Distribuição das variáveis
   - Valores ausentes e outliers
   - Correlações suspeitas
   - Sugestões de limpeza

## ⚙️ Configurações Avançadas

### Personalização do Modelo

No arquivo `config/variaveis.py`:

```python
# Configurações de criatividade
temperatura = 0.2  # 0.0 (conservador) a 2.0 (criativo)
top_p = 0.8        # 0.0 a 1.0 (diversidade de respostas)

# Para análise de código: temperatura = 0.2
# Para texto criativo: temperatura = 1.0
```

### Configurações de Cache

```json
{
  "cache_ttl_segundos": 1800,  // 30 minutos
  "cache_max_size": 1000       // Máximo 1000 itens
}
```

### Configurações de Segurança

```json
{
  "tamanho_max_arquivo_mb": 50,
  "max_arquivos_processo": 10,
  "extensoes_permitidas": [".pdf", ".py", ".txt", ".csv"]
}
```

## 🛠️ Solução de Problemas

### Problema: "Erro de autenticação Google Cloud"

**Solução:**
1. Verifique se as credenciais estão corretas
2. Confirme que o projeto tem Vertex AI habilitado
3. Execute: `gcloud auth application-default login`

### Problema: "Arquivo muito grande"

**Solução:**
1. Verifique o limite em `validai_config.json`
2. Comprima arquivos grandes
3. Divida documentos extensos em partes menores

### Problema: "Interface não carrega"

**Solução:**
1. Verifique se a porta 7860 está livre
2. Execute `python app.py --debug` para mais detalhes
3. Tente acessar via `http://127.0.0.1:7860`

### Problema: "Resposta lenta do modelo"

**Solução:**
1. Reduza `max_output_tokens` para respostas mais rápidas
2. Use cache para consultas repetidas
3. Otimize o tamanho dos arquivos enviados

## 🔒 Segurança e Privacidade

### Proteções Implementadas

- **Validação de Path**: Prevenção contra path traversal attacks
- **Verificação MIME**: Validação de tipos de arquivo
- **Detecção de Malware**: Análise de assinaturas suspeitas
- **Sanitização**: Limpeza automática de inputs

### Boas Práticas

1. **Não envie dados sensíveis** em ambiente de desenvolvimento
2. **Use variáveis de ambiente** para credenciais
3. **Mantenha backups** dos arquivos importantes
4. **Monitore logs** para atividades suspeitas

## 📊 Monitoramento e Performance

### Métricas Disponíveis

- **Tempo de resposta**: Média de processamento
- **Cache hit rate**: Eficiência do cache
- **Uso de tokens**: Consumo da API Gemini
- **Arquivos processados**: Estatísticas de uso

### Logs do Sistema

Logs são salvos em:
- `logs/validai.log`: Log principal
- `logs/security.log`: Eventos de segurança
- `logs/performance.log`: Métricas de performance

## 🆘 Perguntas Frequentes

### Q: Posso usar ValidAI offline?
**R:** Não, o sistema requer conexão com Google Cloud Vertex AI.

### Q: Qual o limite de arquivos por vez?
**R:** Até 10 arquivos, 50MB cada (configurável).

### Q: O sistema salva meus dados?
**R:** Apenas temporariamente para processamento. Configure TTL conforme necessário.

### Q: Posso integrar com outros sistemas?
**R:** Sim, use a API REST disponível em `/api/v1/`.

### Q: Como atualizar o modelo Gemini?
**R:** Altere `modelo_versao` em `validai_config.json`.

## 📞 Suporte

Para suporte técnico:
1. **Verifique logs** em `logs/`
2. **Execute diagnóstico**: `python verificar_correcoes.py`
3. **Consulte documentação** adicional em `docs/`

---

**ValidAI Enhanced** - Validação inteligente para códigos e documentos.
Versão 2.0 | © 2024 | Powered by Google Gemini