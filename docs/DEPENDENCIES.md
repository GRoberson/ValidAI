# 📦 Dependências do RAG Enhanced

Este documento descreve todas as dependências do projeto RAG Enhanced, suas finalidades e opções de instalação.

## 🎯 Visão Geral

O projeto oferece **3 níveis de instalação** para diferentes necessidades:

| Arquivo | Finalidade | Tamanho | Tempo de Instalação |
|---------|------------|---------|-------------------|
| `requirements-minimal.txt` | Apenas funcionalidades core | ~50MB | ~2 minutos |
| `requirements.txt` | Instalação completa | ~200MB | ~5 minutos |
| `requirements-dev.txt` | Desenvolvimento completo | ~500MB | ~10 minutos |

## 🚀 Instalação Rápida

### Instalação Mínima (Recomendada para Produção)
```bash
pip install -r requirements-minimal.txt
```

### Instalação Completa
```bash
pip install -r requirements.txt
```

### Instalação para Desenvolvimento
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## 📋 Dependências por Categoria

### 🔴 **Core (Obrigatórias)**

#### Google Cloud e AI
- **`google-cloud-storage`** - Armazenamento de arquivos no GCS
- **`google-generativeai`** - Cliente para Gemini API
- **`vertexai`** - Plataforma de AI do Google Cloud

#### Interface de Usuário
- **`gradio`** - Interface web interativa

#### Processamento de Dados
- **`pandas`** - Manipulação de dados estruturados
- **`PyYAML`** - Parsing de arquivos YAML
- **`pydantic`** - Validação de dados

#### Rede e HTTP
- **`requests`** - Cliente HTTP

---

### 🟡 **Opcionais (Recomendadas)**

#### Análise de Dados
- **`numpy`** - Computação científica
- **`matplotlib`** - Visualização de dados
- **`seaborn`** - Gráficos estatísticos
- **`plotly`** - Gráficos interativos

#### Processamento de Texto
- **`nltk`** - Processamento de linguagem natural
- **`spacy`** - NLP avançado

#### Manipulação de Arquivos
- **`openpyxl`** - Arquivos Excel
- **`python-docx`** - Documentos Word
- **`PyPDF2`** - Arquivos PDF
- **`Pillow`** - Processamento de imagens

#### Sistema e Monitoramento
- **`psutil`** - Informações do sistema
- **`rich`** - Output colorido no terminal
- **`tqdm`** - Barras de progresso

---

### 🔵 **Desenvolvimento**

#### Testes
- **`pytest`** - Framework de testes
- **`pytest-cov`** - Cobertura de testes
- **`pytest-mock`** - Mocks para testes

#### Qualidade de Código
- **`black`** - Formatação automática
- **`flake8`** - Linting
- **`mypy`** - Type checking
- **`isort`** - Organização de imports

#### Debugging e Profiling
- **`memory-profiler`** - Análise de memória
- **`py-spy`** - Profiling de performance
- **`ipdb`** - Debugger interativo

#### Documentação
- **`sphinx`** - Geração de documentação
- **`mkdocs`** - Documentação em Markdown

---

## 🔍 Verificação de Dependências

### Verificação Automática
```bash
python check_dependencies.py
```

### Verificação Manual
```python
# Teste básico
python -c "
import google.cloud.storage
import vertexai
import gradio
import pandas
print('✅ Dependências core OK')
"

# Teste do framework de testes
python -c "
from rag_enhanced.testing import run_quick_test
results = run_quick_test()
print(f'✅ Framework de testes: {results[\"success_rate\"]:.1f}% sucesso')
"
```

---

## 🛠️ Resolução de Problemas

### Problemas Comuns

#### 1. **Erro de Importação do Google Cloud**
```bash
# Problema
ImportError: No module named 'google.cloud'

# Solução
pip install google-cloud-storage google-generativeai vertexai
```

#### 2. **Conflitos de Versão**
```bash
# Problema
ERROR: pip's dependency resolver does not currently consider all the ways...

# Solução
pip install --upgrade --force-reinstall -r requirements.txt
```

#### 3. **Problemas com Gradio**
```bash
# Problema
ModuleNotFoundError: No module named 'gradio'

# Solução
pip install gradio>=4.0.0
```

#### 4. **Erro de Permissão (Linux/Mac)**
```bash
# Problema
Permission denied

# Solução
pip install --user -r requirements.txt
# ou
sudo pip install -r requirements.txt
```

#### 5. **Problemas no Windows**
```bash
# Problema com Visual C++
error: Microsoft Visual C++ 14.0 is required

# Solução
# Instalar Visual Studio Build Tools ou usar conda
conda install -c conda-forge <package-name>
```

### Ambientes Virtuais

#### Usando venv (Recomendado)
```bash
# Criar ambiente
python -m venv rag_env

# Ativar (Linux/Mac)
source rag_env/bin/activate

# Ativar (Windows)
rag_env\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Desativar
deactivate
```

#### Usando conda
```bash
# Criar ambiente
conda create -n rag_env python=3.9

# Ativar
conda activate rag_env

# Instalar dependências
pip install -r requirements.txt

# Desativar
conda deactivate
```

---

## 📊 Análise de Dependências

### Tamanhos Aproximados
```
Core (minimal):     ~50MB
Completo:          ~200MB
Desenvolvimento:   ~500MB
```

### Tempo de Instalação
```
Conexão rápida:    2-5 minutos
Conexão média:     5-10 minutos
Conexão lenta:     10-20 minutos
```

### Compatibilidade
```
Python:            3.8+
Sistemas:          Windows, Linux, macOS
Arquiteturas:      x86_64, ARM64
```

---

## 🎯 Instalações Específicas

### Para Produção (Docker)
```dockerfile
FROM python:3.9-slim

COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

COPY . .
CMD ["python", "run_validai_enhanced.py"]
```

### Para CI/CD
```yaml
# GitHub Actions
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
```

### Para Jupyter Notebooks
```bash
pip install -r requirements.txt jupyter ipykernel
python -m ipykernel install --user --name=rag_enhanced
```

---

## 🔄 Atualizações

### Verificar Atualizações
```bash
pip list --outdated
```

### Atualizar Todas
```bash
pip install --upgrade -r requirements.txt
```

### Atualizar Específica
```bash
pip install --upgrade gradio
```

---

## 📋 Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] pip atualizado (`pip install --upgrade pip`)
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Verificação executada (`python check_dependencies.py`)
- [ ] Teste básico funcionando
- [ ] Configuração do Google Cloud (se necessário)

---

## 🆘 Suporte

### Se nada funcionar:

1. **Reinstalação limpa:**
   ```bash
   pip uninstall -y -r requirements.txt
   pip install -r requirements.txt
   ```

2. **Ambiente novo:**
   ```bash
   python -m venv fresh_env
   source fresh_env/bin/activate  # Linux/Mac
   # fresh_env\Scripts\activate   # Windows
   pip install -r requirements-minimal.txt
   ```

3. **Usar conda:**
   ```bash
   conda create -n rag_conda python=3.9
   conda activate rag_conda
   pip install -r requirements.txt
   ```

4. **Reportar problema:**
   - Execute: `python check_dependencies.py > dependency_report.txt`
   - Inclua o arquivo `dependency_report.txt` no seu report

---

## 📚 Recursos Adicionais

- [Documentação do pip](https://pip.pypa.io/en/stable/)
- [Guia de ambientes virtuais](https://docs.python.org/3/tutorial/venv.html)
- [Troubleshooting do Google Cloud](https://cloud.google.com/docs/authentication/getting-started)
- [Documentação do Gradio](https://gradio.app/docs/)

---

**💡 Dica:** Para uma experiência mais suave, sempre use ambientes virtuais e mantenha as dependências atualizadas!