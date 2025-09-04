# 📊 Diagramas PlantUML - ValidAI Enhanced

Este diretório contém os diagramas de sequência e arquitetura do sistema ValidAI Enhanced em formato PlantUML.

## 📁 Arquivos de Diagrama

### 1. [DIAGRAMA_SEQUENCIA_VALIDAI.puml](./DIAGRAMA_SEQUENCIA_VALIDAI.puml)
**Diagrama principal de sequência** que mostra os fluxos completos do sistema:

- **Inicialização do Sistema**: Configuração, cache, carregamento
- **Chat Multimodal**: Upload de arquivos e processamento
- **Pré-Validador**: Análise de documentos e código
- **Sistema RAG**: Retrieval-Augmented Generation
- **Gerenciamento de Cache**: Performance e otimização
- **Exportação**: Geração de PDFs das conversas
- **Tratamento de Erros**: Estratégias de recuperação

### 2. [DIAGRAMA_ARQUITETURA_VALIDAI.puml](./DIAGRAMA_ARQUITETURA_VALIDAI.puml)
**Diagrama de arquitetura** mostrando os componentes internos:

- **Interface Layer**: Gradio e frontend
- **Business Logic Layer**: Lógica de negócio principal
- **Processing Layer**: Processamento e validação
- **Data Layer**: Manipulação de dados
- **External Services**: APIs externas (Google Cloud)
- **Storage & Config**: Configurações e armazenamento

### 3. [DIAGRAMA_PROCESSAMENTO_ARQUIVOS.puml](./DIAGRAMA_PROCESSAMENTO_ARQUIVOS.puml)
**Diagrama específico** para processamento de diferentes tipos de arquivo:

- **Validação de Segurança**: Verificações iniciais
- **Processamento por Tipo**: Python, SAS, Jupyter, PDF, Excel, CSV, Imagens, Vídeos
- **Múltiplos Arquivos**: Tratamento de uploads em lote
- **Tratamento de Erros**: Arquivos não suportados ou muito grandes

## 🔧 Como Visualizar os Diagramas

### Opção 1: PlantUML Online
1. Acesse [PlantUML Online Server](http://www.plantuml.com/plantuml)
2. Copie o conteúdo de qualquer arquivo `.puml`
3. Cole no editor online
4. Visualize o diagrama gerado

### Opção 2: VS Code com Extension
1. Instale a extensão "PlantUML" no VS Code
2. Abra qualquer arquivo `.puml`
3. Use `Ctrl+Shift+P` → "PlantUML: Preview Current Diagram"
4. Ou use `Alt+D` para preview

### Opção 3: PlantUML Local (Java)
```bash
# Baixar plantuml.jar
wget http://sourceforge.net/projects/plantuml/files/plantuml.jar/download

# Gerar imagem PNG
java -jar plantuml.jar DIAGRAMA_SEQUENCIA_VALIDAI.puml

# Gerar SVG
java -jar plantuml.jar -tsvg DIAGRAMA_SEQUENCIA_VALIDAI.puml
```

### Opção 4: Ferramentas Online
- [PlantText](https://www.planttext.com/)
- [PlantUML Web Server](https://plantuml-server.kkeisuke.dev/)
- [Gravizo](http://www.gravizo.com/)

## 📋 Legenda dos Diagramas

### Símbolos Utilizados
- 👤 **Usuário**: Ator principal do sistema
- 🌐 **Interface**: Gradio web interface
- 🤖 **Chat**: Lógica de conversação
- 📁 **Processador**: Manipulação de arquivos
- 🔒 **Segurança**: Validação e proteção
- 🗄️ **Cache**: Sistema de cache
- ⚙️ **Config**: Configurações
- 🧠 **RAG**: Sistema de recuperação
- 🔮 **Gemini**: API Google Gemini
- ☁️ **Cloud**: Google Cloud Storage

### Cores e Temas
- **Azul**: Fluxos principais
- **Verde**: Operações bem-sucedidas  
- **Vermelho**: Erros e validações
- **Amarelo**: Operações de cache/performance

## 🚀 Fluxos Principais Documentados

### 1. Fluxo de Upload e Análise
```
Usuário → Interface → Validação → Processamento → Gemini → Resposta
```

### 2. Fluxo de Pré-Validação
```
Upload → Extração → Análise Estruturada → Relatório → Exportação
```

### 3. Fluxo RAG
```
Pergunta → Seleção Base → Busca Contexto → Resposta Aumentada
```

### 4. Fluxo de Cache
```
Requisição → Verificar Cache → [Hit: Retornar | Miss: Processar + Armazenar]
```

## 📊 Estatísticas dos Diagramas

- **Total de participantes**: 15+ componentes
- **Fluxos documentados**: 5 principais + subfluxos
- **Tipos de arquivo suportados**: 10+ formatos
- **Cenários de erro**: 8+ situações tratadas
- **APIs externas**: 3 (Gemini, Cloud Storage, Search)

## 🔄 Atualizações e Manutenção

Para manter os diagramas atualizados:

1. **Após mudanças no código**: Revisar fluxos afetados
2. **Novos recursos**: Adicionar sequências correspondentes
3. **Refatorações**: Atualizar nomes de componentes
4. **Correções de bugs**: Documentar novos tratamentos de erro

## 📞 Suporte

Para dúvidas sobre os diagramas:
1. Consulte a documentação do sistema em `GUIA_USUARIO_COMPLETO.md`
2. Verifique os comentários nos próprios arquivos `.puml`
3. Execute o sistema e compare com os fluxos documentados

---

🎯 **Objetivo**: Facilitar o entendimento da arquitetura e fluxos do ValidAI Enhanced através de representação visual clara e detalhada.

📝 **Nota**: Os diagramas são atualizados conforme evolução do sistema e devem ser consultados como referência para desenvolvimento e manutenção.