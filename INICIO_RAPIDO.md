# ⚡ Guia de Início Rápido - ValidAI

## 🚀 Setup em 5 Minutos

### 1. Pré-requisitos
```bash
# Verificar Python
python --version  # Deve ser 3.8+
```

### 2. Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar Google Cloud (substitua pelo seu arquivo)
set GOOGLE_APPLICATION_CREDENTIALS=caminho\para\credentials.json
```

### 3. Configuração Mínima
Edite `config/validai_config.json`:
```json
{
  "project_id": "SEU_PROJETO_GCP",
  "location": "us-central1"
}
```

### 4. Executar
```bash
python app.py
```
Acesse: http://localhost:7860

## 🎯 Primeiros Passos

### Teste 1: Validação de Código
1. Cole este código Python na interface:
```python
def calcular(a, b):
    resultado = a + b
    print(resultado)
    return resultado
```
2. Pergunte: "Analise este código e sugira melhorias"

### Teste 2: Upload de Arquivo
1. Faça upload de um arquivo .py ou .txt
2. Pergunte: "Resuma o conteúdo deste arquivo"

### Teste 3: Análise de Dados
1. Upload de arquivo CSV/Excel
2. Pergunte: "Analise a qualidade destes dados"

## 🔧 Comandos Essenciais

```bash
# Verificar se tudo está funcionando
python verificar_correcoes.py

# Executar com debug
python app.py --debug

# Limpar cache
python -c "from backend.cache import clear_all_caches; clear_all_caches()"
```

## ⚠️ Problemas Comuns

**Erro de autenticação:** Execute `gcloud auth application-default login`
**Interface não carrega:** Verifique se a porta 7860 está livre
**Arquivo muito grande:** Limite padrão é 50MB por arquivo

## 📞 Ajuda Rápida

- 📖 Guia completo: `GUIA_USUARIO_COMPLETO.md`
- 🔍 Logs: pasta `logs/`
- ⚙️ Configurações: `config/validai_config.json`