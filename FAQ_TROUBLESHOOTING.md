# 🆘 FAQ e Troubleshooting - ValidAI

## ❓ Perguntas Frequentes

### 🚀 Instalação e Configuração

**Q: O ValidAI funciona offline?**
A: Não, o sistema requer conexão com Google Cloud Vertex AI para funcionar.

**Q: Preciso de uma conta paga do Google Cloud?**
A: Sim, é necessário ter créditos ou billing habilitado para usar Vertex AI.

**Q: Posso usar outros modelos além do Gemini?**
A: Atualmente o sistema está otimizado para Gemini, mas pode ser adaptado.

**Q: Qual o consumo aproximado de tokens?**
A: Varia conforme uso, mas análises típicas consomem 1000-5000 tokens.

### 📁 Upload e Processamento

**Q: Posso fazer upload de arquivos ZIP?**
A: Não diretamente. Extraia os arquivos primeiro ou envie individualmente.

**Q: O sistema processa arquivos em lote?**
A: Sim, até 10 arquivos simultâneos de 50MB cada.

**Q: Dados sensíveis são seguros?**
A: Arquivos são processados temporariamente e removidos após uso.

**Q: Posso cancelar um processamento em andamento?**
A: Sim, recarregue a página ou use o botão "Parar" se disponível.

### 🔧 Performance e Uso

**Q: Por que as respostas estão lentas?**
A: Pode ser devido a arquivos grandes, alta demanda da API ou configurações.

**Q: Como otimizar o uso de tokens?**
A: Use perguntas específicas, ative cache e processe arquivos menores.

**Q: O sistema tem limite de uso diário?**
A: Depende dos limites da sua conta Google Cloud.

## 🛠️ Guia de Troubleshooting

### ❌ Erros de Autenticação

#### Erro: "Could not automatically determine credentials"
```bash
# Solução 1: Configurar credenciais via variável de ambiente
set GOOGLE_APPLICATION_CREDENTIALS=caminho\para\service-account.json

# Solução 2: Login via gcloud CLI
gcloud auth application-default login

# Solução 3: Verificar se o arquivo de credenciais existe
dir %GOOGLE_APPLICATION_CREDENTIALS%
```

#### Erro: "Permission denied on project"
```bash
# Verificar se o projeto está correto
gcloud config get-value project

# Definir projeto correto
gcloud config set project SEU_PROJETO_ID

# Verificar permissões
gcloud auth list
```

### 🌐 Erros de Rede e Conectividade

#### Erro: "Connection timeout"
1. Verificar conexão com internet
2. Verificar se firewalls não estão bloqueando
3. Tentar em horários de menor tráfego
4. Considerar usar proxy se necessário

#### Erro: "Port 7860 already in use"
```bash
# Verificar qual processo está usando a porta
netstat -ano | findstr :7860

# Encerrar processo (substitua PID)
taskkill /PID 1234 /F

# Ou usar porta diferente
python app.py --server-port 7861
```

### 📁 Problemas com Arquivos

#### Erro: "File too large"
**Causa**: Arquivo excede limite configurado
**Solução**:
1. Reduzir tamanho do arquivo
2. Aumentar limite em `validai_config.json`:
```json
{
  "tamanho_max_arquivo_mb": 100
}
```

#### Erro: "Unsupported file type"
**Causa**: Extensão não permitida
**Solução**: Adicionar extensão em `validai_config.json`:
```json
{
  "extensoes_permitidas": [".pdf", ".py", ".txt", ".csv", ".sua_extensao"]
}
```

#### Erro: "File encoding error"
**Causa**: Problemas de codificação
**Solução**:
1. Salvar arquivo em UTF-8
2. Converter codificação:
```python
# Script para converter
with open('arquivo.txt', 'r', encoding='latin1') as f:
    content = f.read()
with open('arquivo_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(content)
```

### 🧠 Problemas com IA/Modelo

#### Respostas inconsistentes ou estranhas
**Causa**: Configurações de temperatura/prompt
**Solução**:
1. Ajustar temperatura em `config/variaveis.py`:
```python
temperatura = 0.2  # Mais conservador
```
2. Ser mais específico nas perguntas
3. Limpar cache se necessário

#### Erro: "Model quota exceeded"
**Causa**: Limite de uso da API atingido
**Solução**:
1. Aguardar reset do limite
2. Verificar quotas no Google Cloud Console
3. Solicitar aumento de limite se necessário

### 💾 Problemas de Cache e Performance

#### Sistema lento após uso prolongado
**Solução**:
```python
# Limpar cache manualmente
python -c "from backend.cache import clear_all_caches; clear_all_caches()"
```

#### Erro: "Cache corruption"
**Solução**:
```bash
# Deletar pasta de cache
rmdir /s cache_dir

# Reiniciar sistema
python app.py
```

### 🔍 Problemas de Importação

#### Erro: "Module not found"
```bash
# Verificar se todas as dependências estão instaladas
pip install -r requirements.txt

# Verificar versões
pip list | findstr "google\|gradio\|pandas"

# Reinstalar dependência específica
pip uninstall nome_modulo
pip install nome_modulo
```

#### Erro: "ImportError: cannot import name"
**Causa**: Conflito de versões
**Solução**:
```bash
# Verificar conflitos
pip check

# Atualizar dependências
pip install --upgrade -r requirements.txt

# Reinstalar em ambiente limpo
python -m venv novo_env
novo_env\Scripts\activate
pip install -r requirements.txt
```

## 🔧 Scripts de Diagnóstico

### Script de Verificação Completa
```bash
# Executar diagnóstico automático
python verificar_correcoes.py

# Verificar configurações
python -c "
from config.config_loader import get_config_value
print('Projeto:', get_config_value('project_id'))
print('Localização:', get_config_value('location'))
"
```

### Script de Teste de Conectividade
```python
# Salvar como test_connection.py
import vertexai
from config.config_loader import get_config_value

try:
    project_id = get_config_value("project_id")
    location = get_config_value("location")
    vertexai.init(project=project_id, location=location)
    print("✅ Conexão com Vertex AI OK")
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
```

### Script de Limpeza
```python
# Salvar como cleanup.py
import os
import shutil

# Limpar arquivos temporários
temp_dirs = ['temp_files', 'cache', '__pycache__']
for temp_dir in temp_dirs:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"🧹 Removido: {temp_dir}")

# Limpar logs antigos (manter últimos 7 dias)
import time
log_dir = 'logs'
if os.path.exists(log_dir):
    for file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file)
        if os.path.getctime(file_path) < time.time() - 7*24*3600:
            os.remove(file_path)
            print(f"🗑️ Log antigo removido: {file}")
```

## 📞 Suporte e Comunidade

### Quando Buscar Ajuda
1. **Primeiro**: Consulte este FAQ
2. **Segundo**: Execute `python verificar_correcoes.py`
3. **Terceiro**: Verifique logs em `logs/`
4. **Quarto**: Teste com configuração mínima

### Informações Úteis para Suporte
Quando reportar problemas, inclua:
- Versão do Python (`python --version`)
- Sistema operacional
- Conteúdo de `validai_config.json` (sem credenciais)
- Últimas linhas dos logs
- Passos para reproduzir o problema

### Logs Importantes
```bash
# Log principal
type logs\validai.log | findstr "ERROR"

# Log de segurança  
type logs\security.log

# Log de performance
type logs\performance.log | findstr "SLOW"
```

---

🚨 **Lembre-se**: Mantenha sempre backups de suas configurações e dados importantes antes de fazer alterações no sistema!