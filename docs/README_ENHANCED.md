# 🚀 ValidAI Enhanced + RAG Avançado

Uma versão revolucionária do ValidAI que incorpora os melhores padrões de experiência do usuário, configuração flexível e um sistema RAG baseado em Vertex AI nativo.

## ✨ Principais Melhorias

### 🎯 **Experiência do Usuário**
- **Feedback humanizado** com emojis e mensagens claras
- **Validação proativa** de arquivos e configurações
- **Interface aprimorada** com status em tempo real
- **Dicas contextuais** e orientações inteligentes

### ⚙️ **Configuração Flexível**
- **Arquivo JSON** para configurações personalizadas
- **Variáveis de ambiente** para diferentes ambientes
- **Validação automática** de configurações
- **Valores padrão** inteligentes

### 🛡️ **Robustez Técnica**
- **Tratamento de erros** detalhado e útil
- **Logging estruturado** para debugging
- **Validação de arquivos** com feedback rico
- **Gestão de recursos** otimizada

### 🧠 **Sistema RAG Revolucionário**
- **Vertex AI Nativo** - Tecnologia de ponta do Google Cloud
- **Múltiplos Corpus** - Bases de conhecimento especializadas
- **Processamento Inteligente** - Chunking otimizado e embeddings avançados
- **Consultas Contextuais** - Respostas baseadas em documentos específicos

## 🚀 Instalação e Configuração

### 1. **Pré-requisitos**
```bash
# Instalar dependências
pip install gradio google-genai google-cloud-storage vertexai pandas openpyxl
```

### 2. **Configuração**
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações (opcional)
nano validai_config.json
```

### 3. **Configuração do RAG**
```bash
# Configurar corpus RAG
python setup_rag_corpus.py --all

# Verificar estrutura
python setup_rag_corpus.py --check

# Criar diretórios
python setup_rag_corpus.py --create-dirs
```

### 4. **Execução**
```bash
# Execução padrão (com RAG avançado)
python validai_enhanced_with_rag.py

# Execução original (sem RAG avançado)
python run_validai_enhanced.py

# Com debug
python validai_enhanced_with_rag.py --debug

# Verificar sistema apenas
python run_validai_enhanced.py --check-only
```

## 📋 Configurações Disponíveis

### **Arquivo JSON** (`validai_config.json`)
```json
{
  "project_id": "seu-projeto-gcp",
  "modelo_versao": "gemini-1.5-pro-002",
  "temperatura": 0.2,
  "max_output_tokens": 8000,
  "tamanho_max_arquivo_mb": 50
}
```

### **Variáveis de Ambiente**
```bash
VALIDAI_PROJECT_ID=seu-projeto
VALIDAI_MODELO=gemini-1.5-pro-002
VALIDAI_TEMPERATURA=0.2
VALIDAI_MAX_TOKENS=8000
```

## 📚 Sistema RAG Avançado

### **Bases de Conhecimento Disponíveis**

| Base | Descrição | Tipos de Arquivo |
|------|-----------|------------------|
| **Instruções Normativas** | INs 706, 1253, 1146 | PDF, TXT, MD |
| **Validações de Mercado** | Relatórios de risco de mercado | PDF, TXT, MD, DOCX |
| **Validações de Crédito** | Relatórios de risco de crédito | PDF, TXT, MD, DOCX |
| **Metodologias** | Frameworks e boas práticas | PDF, TXT, MD |
| **Casos de Uso** | Exemplos práticos | PDF, TXT, MD, IPYNB |

### **Configuração de Corpus**

```bash
# Setup completo
python setup_rag_corpus.py --all

# Operações específicas
python setup_rag_corpus.py --create-dirs    # Criar estrutura
python setup_rag_corpus.py --migrate        # Migrar arquivos antigos
python setup_rag_corpus.py --validate       # Validar configuração
python setup_rag_corpus.py --check          # Verificar arquivos
```

### **Fluxo de Uso do RAG**

1. **Preparar Documentos**: Colocar arquivos nos diretórios apropriados
2. **Configurar Corpus**: Usar interface gráfica ou script de setup
3. **Upload**: Enviar arquivos para Google Cloud Storage
4. **Processar**: Criar embeddings e índices no Vertex AI
5. **Consultar**: Fazer perguntas contextualizadas

## 🎯 Funcionalidades

### 💬 **Chat Multimodal Enhanced**
- Interface mais intuitiva com status em tempo real
- Validação de arquivos antes do processamento
- Feedback rico sobre tipos e tamanhos de arquivo
- Dicas contextuais de uso

### 🔍 **Pré-Validador Aprimorado**
- Status de validação em tempo real
- Feedback detalhado sobre problemas encontrados
- Interface mais clara para upload de arquivos
- Relatórios PDF com melhor formatação

### 📚 **Sistema RAG Avançado**
- **Múltiplas Bases**: Instruções Normativas, Validações de Mercado/Crédito, Metodologias
- **Vertex AI Nativo**: Embeddings e processamento de última geração
- **Configuração Visual**: Interface gráfica para setup de corpus
- **Consultas Inteligentes**: Respostas contextualizadas por base específica
- **Gestão Completa**: Upload, processamento e consulta integrados

### ⚙️ **Painel de Configurações**
- Interface gráfica para ajustar parâmetros
- Validação em tempo real
- Salvamento de configurações
- Restauração de padrões

## 🔧 Argumentos da Linha de Comando

```bash
# Execução básica
python run_validai_enhanced.py

# Configuração personalizada
python run_validai_enhanced.py --config minha_config.json

# Modo debug
python run_validai_enhanced.py --debug

# Porta específica
python run_validai_enhanced.py --port 7860

# Link público (CUIDADO!)
python run_validai_enhanced.py --share

# Apenas verificar sistema
python run_validai_enhanced.py --check-only
```

## 📊 Comparação com ValidAI Original

| Aspecto | ValidAI Original | ValidAI Enhanced |
|---------|------------------|------------------|
| **Configuração** | Hardcoded | Arquivo JSON + Env Vars |
| **Feedback** | Técnico | Humanizado com emojis |
| **Validação** | Básica | Proativa e detalhada |
| **Erros** | Silenciosos | Informativos com dicas |
| **Interface** | Funcional | Aprimorada com status |
| **Logging** | Prints simples | Estruturado |
| **Documentação** | Básica | Rica e didática |

## 🛠️ Estrutura do Projeto

```
ValidAI Enhanced/
├── validai_enhanced.py          # Aplicação principal aprimorada
├── run_validai_enhanced.py      # Script de inicialização
├── validai_config.json          # Configurações personalizáveis
├── .env.example                 # Exemplo de variáveis de ambiente
├── README_ENHANCED.md           # Esta documentação
│
├── config/                      # Configurações originais
├── backend/                     # Lógica de negócio
├── src/                         # Utilitários
├── frontend/                    # Interface
└── base_conhecimento/           # Base RAG
```

## 🎯 Casos de Uso

### **Desenvolvimento Local**
```bash
# Configuração para desenvolvimento
export VALIDAI_DEBUG=true
export VALIDAI_TEMPERATURA=0.1
python run_validai_enhanced.py --debug
```

### **Ambiente de Produção**
```bash
# Configuração otimizada
export VALIDAI_TEMPERATURA=0.2
export VALIDAI_MAX_TOKENS=8000
python run_validai_enhanced.py --config producao.json
```

### **Demonstração/Treinamento**
```bash
# Interface amigável para apresentações
python run_validai_enhanced.py --share
```

## 🔍 Troubleshooting

### **Problema: Dependências faltando**
```bash
# Verificar sistema
python run_validai_enhanced.py --check-only

# Instalar dependências
pip install -r requirements.txt
```

### **Problema: Configuração inválida**
```bash
# Usar configuração padrão
python run_validai_enhanced.py --config ""

# Verificar logs
python run_validai_enhanced.py --debug
```

### **Problema: Arquivos não encontrados**
```bash
# Verificar estrutura
ls -la config/ backend/ src/ frontend/

# Executar do diretório correto
cd /caminho/para/validai
python run_validai_enhanced.py
```

## 🚀 Próximos Passos

### **Melhorias Planejadas**
- [ ] Testes automatizados
- [ ] API REST complementar
- [ ] Dashboard de métricas
- [ ] Integração com CI/CD
- [ ] Suporte a múltiplos idiomas

### **Contribuindo**
1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente com testes
4. Submeta um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique os logs com `--debug`
- Execute `--check-only` para diagnóstico
- Consulte a documentação original do ValidAI
- Entre em contato com a equipe de desenvolvimento

---

**ValidAI Enhanced** - Validação de Modelos ML com Experiência Aprimorada 🚀