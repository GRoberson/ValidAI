def documento():
    prompt = """
    Analise o texto abaixo, extraído de um documento que descreve um modelo, e responda às perguntas a seguir da forma mais completa e informativa possível:

    I. Compreendendo o Modelo e Sua Concepção:

    1. **Objetivo:** Qual problema este modelo se propõe a resolver? 
    * Seja específico e forneça exemplos concretos.
    2. **Público-Alvo:** 
    * Para quem este modelo foi projetado? 
    * Quem são os usuários finais e como eles se beneficiarão da sua aplicação?
    3. **Dados:** 
    * O documento descreve a origem dos dados utilizados?
    * Quais são as variáveis (features) de entrada do modelo? 
    * Para cada variável, tente identificar:
        * Nome e descrição do seu significado no contexto do problema.
        * Tipo de dado (ex.: numérico, categórico, texto).
        * Há informações sobre o processo de pré-processamento dos dados (limpeza, tratamento de missings, etc.)?
    4. **Saída do Modelo:**
    * O que o modelo produz como resultado (predição, classificação, score, etc.)? 
    * Qual a estrutura de saída do modelo (valor numérico, classe, probabilidade, etc.)?
    * Como a saída do modelo se conecta com a resolução do problema ou com a tomada de decisão?

    II. Desvendando a Arquitetura e Implementação do Modelo:

    1. **Técnica Empregada:**
    * Qual algoritmo/técnica de modelagem foi utilizada (ex.: regressão logística, máquinas de vetores de suporte, redes neurais, etc.)? 
    * O documento justifica a escolha da técnica em relação ao problema e aos dados?
    2. **Etapas de Modelagem:**
    * O documento descreve as etapas de desenvolvimento do modelo? 
    * Quais são os principais passos, desde o pré-processamento dos dados até a avaliação do modelo?
    * Há informações sobre:
        * Seleção de features?
        * Engenharia de atributos?
        * Seleção de modelo e hiperparâmetros?
        * Treinamento e validação?
        * Métricas de performance utilizadas?
    3. **Equação/Parâmetros do Modelo:**
    * O documento apresenta a equação final do modelo (se aplicável)?
    * Há informações sobre os parâmetros ajustados durante o treinamento?
    * É possível interpretar a influência dos parâmetros na saída do modelo?

    III. Avaliando a Confiabilidade e Aplicabilidade do Modelo:

    1. **Premissas e Limitações:**
    * Quais são as principais premissas assumidas durante a construção do modelo? 
    * Quais as limitações do modelo em termos de dados, capacidade preditiva, generalização e interpretabilidade?
    2. **Manutenção e Monitoramento:**
    * Há um plano para monitorar o desempenho do modelo ao longo do tempo? 
    * O documento menciona a necessidade de atualização ou retreinamento do modelo?

    Observação: Se o documento não fornecer informações suficientes para responder a alguma pergunta, indique isso na sua resposta.

    Ao final, apresente um relatório detalhado com os seguintes pontos:
        *Sumário das validações realizadas e suas respectivas conclusões.
        *Lista detalhada de todas as discrepâncias encontradas entre o código e o documento, incluindo a localização no código e no documento, 
        descrição da divergência e nível de severidade.
        *Recomendações para corrigir as discrepâncias e melhorar a qualidade do código e sua correspondência com o documento.
        *Gere uma tabela com a análises, onde cada coluna seja, Item Analisado, Análise, Parecer (Suficiente, Não Suficiente), Pontos de Melhorias.
    """
    return prompt

def codigo(qtd):
    prompt = """
    Analise o código abaixo do modelo e responda às perguntas a seguir da forma mais completa e informativa possível:

    1. Objetivo do Código:

    * Qual é o objetivo principal deste código em relação ao modelo? 
        * *Ex.: Pré-processamento de dados, treinamento do modelo, avaliação de performance, etc.*
    * Que tipo de modelo ele se destina a construir ou avaliar?
        * *Ex.: Regressão linear, rede neural, árvore de decisão, etc.*

    2. Origem e Descrição dos Dados:

    * De onde se originam os dados utilizados no código? 
        * *Ex.: Arquivos locais, bancos de dados, APIs, etc.*
    * Qual o formato dos dados de entrada?
        * *Ex.: CSV, JSON, XML, etc.*
    * Os dados estão pré-processados? Se sim, descreva os passos de pré-processamento.
    * Forneça um dicionário de dados com a descrição de cada variável e seu tipo.

    3. Técnicas de Filtragem de Dados:

    * Quais filtros são aplicados aos dados durante o processo?
        * *Ex.: Remoção de valores ausentes, suavização, normalização, etc.*
    * Especifique os critérios utilizados em cada filtro.
        * *Ex.: Limite superior/inferior, valores específicos, expressões regulares, etc.*
    * Justifique a necessidade de cada filtro em relação ao objetivo do modelo.

    4. Erros, Bugs e Oportunidades de Melhoria:

    * O código executa sem erros? Se não, quais são os erros encontrados?
    * Existem potenciais bugs ou comportamentos inesperados no código?
    * Identifique trechos de código que podem ser otimizados em termos de performance ou legibilidade.
    * O código segue as melhores práticas de programação e estilo para a linguagem utilizada?

    5. Detalhes da Técnica de Modelagem:

    * Especifique a técnica de modelagem utilizada em detalhes.
        * *Ex.: Regressão Logística, Random Forest, Support Vector Machine, etc.*
    * Justifique a escolha da técnica de modelagem em relação ao problema e aos dados.
    * Quais são os hiperparâmetros da técnica de modelagem utilizada no código?

    6. Variáveis do Modelo:

    * Liste todas as variáveis de entrada (features) utilizadas pelo modelo.
    * Para cada variável, especifique o tipo de dado (numérico, categórico, texto, etc.).
    * Indique quais variáveis são consideradas mais importantes para o modelo e porquê.

    7. Engenharia de Atributos:

    * Descreva o processo de construção de cada variável (feature engineering).
        * *Ex.: Cálculo de médias móveis, combinação de variáveis, one-hot encoding, etc.*
    * Explique a lógica por trás da criação de novas variáveis e como elas se relacionam com o objetivo do modelo.

    Observação: Se o documento não fornecer informações suficientes para responder a alguma pergunta, indique isso na sua resposta.
    """
    if qtd >= 1:
        prompt = "Para cada código fornecido, responda as seguintes perguntas a seguir: "+ prompt
    return prompt
    
def codigo_documento():
    prompt = """
    Dado os seguintes códigos e a documentação do modelo, compare os códigos com a documentação em relação aos seguintes aspectos: variáveis utilizadas, cálculos do modelo e tratamento de dados. 
    Gere um relatório resumido que descreve as diferenças encontradas, incluindo uma tabela comparativa, exemplos de código discrepante e sugestões de correção.
    """
    return prompt