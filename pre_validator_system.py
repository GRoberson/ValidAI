class PreValidadorModelos:
    """
    Sistema de pré-validação para modelos de Machine Learning.
    
    Este sistema implementa uma abordagem estruturada e eficiente para verificar
    se modelos contêm os elementos mínimos necessários antes da validação completa.
    """
    
    def __init__(self):
        self.criterios_minimos = {
            'documentacao': self._get_criterios_documentacao(),
            'codigo': self._get_criterios_codigo(),
            'consistencia': self._get_criterios_consistencia()
        }
        
    def _get_criterios_documentacao(self):
        """Define critérios mínimos para documentação."""
        return {
            'contexto_negocio': {
                'peso': 0.25,
                'itens': [
                    'Problema de negócio claramente definido',
                    'Objetivos específicos e mensuráveis',
                    'Público-alvo e stakeholders identificados',
                    'Critérios de sucesso estabelecidos'
                ]
            },
            'dados_e_features': {
                'peso': 0.30,
                'itens': [
                    'Fonte e origem dos dados documentada',
                    'Dicionário de variáveis completo (nome, tipo, descrição)',
                    'Estratégias de pré-processamento descritas',
                    'Features engineering documentada',
                    'Tratamento de valores ausentes especificado'
                ]
            },
            'metodologia': {
                'peso': 0.25,
                'itens': [
                    'Algoritmo/técnica escolhida justificada',
                    'Estratégia de validação definida',
                    'Métricas de avaliação estabelecidas',
                    'Baseline ou benchmark especificado'
                ]
            },
            'governanca': {
                'peso': 0.20,
                'itens': [
                    'Limitações e premissas explicitadas',
                    'Riscos e vieses identificados',
                    'Plano de monitoramento descrito',
                    'Critérios de retreinamento definidos'
                ]
            }
        }
    
    def _get_criterios_codigo(self):
        """Define critérios mínimos para código."""
        return {
            'estrutura_e_qualidade': {
                'peso': 0.25,
                'itens': [
                    'Código estruturado e organizado',
                    'Imports e dependências declaradas',
                    'Funções com docstrings',
                    'Convenções de nomenclatura seguidas'
                ]
            },
            'pipeline_dados': {
                'peso': 0.30,
                'itens': [
                    'Carregamento de dados implementado',
                    'Validação básica de dados presente',
                    'Pré-processamento codificado',
                    'Divisão treino/validação/teste implementada'
                ]
            },
            'modelagem': {
                'peso': 0.25,
                'itens': [
                    'Algoritmo implementado corretamente',
                    'Hiperparâmetros configuráveis',
                    'Processo de treinamento claro',
                    'Validação cruzada ou similar implementada'
                ]
            },
            'avaliacao_e_output': {
                'peso': 0.20,
                'itens': [
                    'Métricas de avaliação calculadas',
                    'Visualizações de resultados',
                    'Salvamento do modelo implementado',
                    'Logging e tratamento de erros'
                ]
            }
        }
    
    def _get_criterios_consistencia(self):
        """Define critérios para consistência entre código e documentação."""
        return {
            'alinhamento_tecnico': [
                'Variáveis documentadas presentes no código',
                'Algoritmo descrito corresponde ao implementado',
                'Métricas documentadas são calculadas no código',
                'Pré-processamentos descritos estão implementados'
            ],
            'alinhamento_negocio': [
                'Objetivos documentados refletidos na implementação',
                'Features relevantes para o problema são utilizadas',
                'Outputs do modelo atendem aos objetivos declarados'
            ]
        }

    def gerar_prompt_documentacao(self):
        """Gera prompt otimizado para pré-validação de documentação."""
        return """
        # PRÉ-VALIDADOR DE DOCUMENTAÇÃO DE MODELO ML

        Você é um especialista em pré-validação de documentação de modelos de Machine Learning. Seu objetivo é verificar se o documento contém **elementos mínimos essenciais** para prosseguir com uma validação completa.

        ## INSTRUÇÕES DE ANÁLISE

        Avalie cada seção abaixo usando a escala: **SUFICIENTE** | **INSUFICIENTE** | **AUSENTE**

        ### 🎯 CONTEXTO DE NEGÓCIO (Peso: 25%)
        - **Problema:** Definição clara do problema a ser resolvido
        - **Objetivos:** Metas específicas e mensuráveis do modelo
        - **Stakeholders:** Identificação de usuários finais e beneficiários
        - **Critérios de Sucesso:** Como o sucesso será medido

        ### 📊 DADOS E FEATURES (Peso: 30%)
        - **Fonte de Dados:** Origem e processo de coleta documentados
        - **Dicionário de Variáveis:** Nome, tipo, descrição e domínio das variáveis
        - **Pré-processamento:** Estratégias de limpeza e transformação
        - **Feature Engineering:** Criação e seleção de características
        - **Qualidade dos Dados:** Tratamento de missing values e outliers

        ### 🔬 METODOLOGIA (Peso: 25%)
        - **Algoritmo:** Técnica escolhida com justificativa
        - **Validação:** Estratégia de divisão e validação dos dados
        - **Métricas:** Indicadores de performance apropriados
        - **Baseline:** Benchmark ou modelo de comparação

        ### 🛡️ GOVERNANÇA (Peso: 20%)
        - **Limitações:** Restrições e premissas do modelo
        - **Riscos e Vieses:** Identificação de potenciais problemas
        - **Monitoramento:** Plano de acompanhamento em produção
        - **Manutenção:** Critérios e frequência de retreinamento

        ## FORMATO DE RESPOSTA

        Para cada item, forneça:
        1. **Classificação:** Suficiente/Insuficiente/Ausente
        2. **Justificativa:** Breve explicação da avaliação
        3. **Evidência:** Citação específica do documento (quando presente)

        ### RELATÓRIO FINAL
        - **Score Global:** Percentual de adequação (0-100%)
        - **Status:** APROVADO/APROVADO COM RESSALVAS/REPROVADO
        - **Top 3 Lacunas Críticas:** Principais problemas identificados
        - **Próximos Passos:** Recomendações específicas para melhoria

        ### TABELA RESUMO
        | Item | Status | Comentário | Ação Requerida |
        |------|--------|-----------|----------------|
        """

    def gerar_prompt_codigo(self, multiplos_arquivos=False):
        """Gera prompt otimizado para pré-validação de código."""
        prefixo = "Para cada código fornecido, " if multiplos_arquivos else ""
        
        return f"""
        # PRÉ-VALIDADOR DE CÓDIGO DE MODELO ML

        {prefixo}Você é um especialista em pré-validação de código de Machine Learning. Analise se o código contém os **elementos mínimos essenciais** para uma validação técnica completa.

        ## CRITÉRIOS DE ANÁLISE

        Avalie cada aspecto usando: **SUFICIENTE** | **INSUFICIENTE** | **AUSENTE**

        ### 🏗️ ESTRUTURA E QUALIDADE (Peso: 25%)
        - **Organização:** Código estruturado e legível
        - **Dependências:** Imports necessários declarados
        - **Documentação:** Docstrings e comentários adequados
        - **Convenções:** Padrões de nomenclatura e estilo

        ### 🔄 PIPELINE DE DADOS (Peso: 30%)
        - **Carregamento:** Leitura de dados implementada
        - **Validação:** Verificações básicas de integridade
        - **Pré-processamento:** Limpeza e transformação dos dados
        - **Split:** Divisão treino/validação/teste

        ### 🤖 MODELAGEM (Peso: 25%)
        - **Algoritmo:** Implementação correta da técnica escolhida
        - **Hiperparâmetros:** Configuração flexível de parâmetros
        - **Treinamento:** Processo de fit/treino implementado
        - **Validação:** Cross-validation ou validação holdout

        ### 📈 AVALIAÇÃO E ENTREGA (Peso: 20%)
        - **Métricas:** Cálculo de indicadores de performance
        - **Visualizações:** Gráficos de resultados e diagnósticos
        - **Persistência:** Salvamento do modelo treinado
        - **Robustez:** Tratamento de erros e logging

        ## ANÁLISE TÉCNICA ESPECÍFICA

        Para cada seção do código, identifique:
        - **Funcionalidades implementadas vs. esperadas**
        - **Potenciais bugs ou erros de execução**
        - **Dependências externas não declaradas**
        - **Hardcoding que deveria ser parametrizável**

        ## FORMATO DE RESPOSTA

        ### AVALIAÇÃO POR CRITÉRIO
        Para cada item:
        1. **Status:** Suficiente/Insuficiente/Ausente
        2. **Evidência:** Linha(s) de código relevante(s)
        3. **Observação:** Comentário técnico específico

        ### RELATÓRIO EXECUTIVO
        - **Score Técnico:** Percentual de adequação (0-100%)
        - **Executabilidade:** SIM/NÃO/COM AJUSTES
        - **Lacunas Críticas:** Top 3 problemas que impedem a validação
        - **Recomendações:** Ações específicas para correção

        ### MATRIZ DE VERIFICAÇÃO
        | Componente | Implementado | Funcional | Documentado | Ação |
        |------------|--------------|-----------|-------------|------|
        """

    def gerar_prompt_consistencia(self):
        """Gera prompt para verificação de consistência código-documentação."""
        return """
        # PRÉ-VALIDADOR DE CONSISTÊNCIA CÓDIGO-DOCUMENTAÇÃO

        Você é um especialista em validação cruzada de artefatos de ML. Analise a **consistência** entre o código fornecido e sua documentação, identificando divergências que possam comprometer a validação.

        ## MATRIZ DE CONSISTÊNCIA

        Para cada elemento, verifique:

        ### 🔍 ALINHAMENTO TÉCNICO
        | Elemento | Código | Documentação | Consistente? | Impacto |
        |----------|--------|--------------|--------------|---------|
        | Variáveis de entrada | | | | |
        | Algoritmo/técnica | | | | |
        | Pré-processamento | | | | |
        | Métricas de avaliação | | | | |
        | Hiperparâmetros | | | | |

        ### 🎯 ALINHAMENTO DE NEGÓCIO
        - **Problema Resolvido:** O código implementa solução para o problema documentado?
        - **Features Relevantes:** Variáveis usadas são adequadas ao contexto de negócio?
        - **Outputs:** Saídas do modelo atendem aos objetivos declarados?
        - **Limitações:** Restrições técnicas refletem limitações documentadas?

        ## ANÁLISE DE DIVERGÊNCIAS

        Para cada inconsistência encontrada:
        1. **Tipo:** Técnica/Negócio/Metodológica
        2. **Severidade:** Alta/Média/Baixa
        3. **Impacto:** Como afeta a validação
        4. **Recomendação:** Ação específica para correção

        ## RELATÓRIO DE CONSISTÊNCIA

        ### SCORE DE ALINHAMENTO
        - **Técnico:** ___% (variáveis, algoritmos, métricas)
        - **Negócio:** ___% (objetivos, contexto, aplicabilidade)
        - **Global:** ___% (média ponderada)

        ### STATUS FINAL
        - ✅ **CONSISTENTE:** Pronto para validação completa
        - ⚠️ **INCONSISTÊNCIAS MENORES:** Validação possível com ajustes
        - ❌ **INCONSISTÊNCIAS CRÍTICAS:** Requer alinhamento antes da validação

        ### PLANO DE AÇÃO
        1. **Correções Obrigatórias:** [Lista priorizada]
        2. **Melhorias Recomendadas:** [Sugestões de valor agregado]
        3. **Próximos Passos:** [Roteiro para validação completa]
        """

    def gerar_prompt_integrado(self):
        """
        Gera um prompt integrado que combina todos os aspectos de pré-validação
        de forma eficiente e estruturada.
        """
        return """
        # SISTEMA INTEGRADO DE PRÉ-VALIDAÇÃO DE MODELOS ML

        Você é um **Pré-Validador Sênior de Modelos ML**. Sua missão é realizar uma avaliação rápida mas abrangente para determinar se o modelo está pronto para validação completa.

        ## 🎯 OBJETIVO
        Verificar presença de **elementos mínimos essenciais** em máximo 15 minutos de análise, focando em **blockers críticos** que impediriam uma validação bem-sucedida.

        ## 📋 METODOLOGIA DE AVALIAÇÃO

        ### FASE 1: TRIAGEM RÁPIDA (5 min)
        #### Critérios Eliminatórios - Se ausentes, REPROVAR imediatamente:
        - [ ] Problema de negócio definido
        - [ ] Dados identificados com origem
        - [ ] Algoritmo especificado
        - [ ] Pelo menos uma métrica de avaliação
        - [ ] Código executável (sem erros óbvios)

        ### FASE 2: AVALIAÇÃO ESTRUTURADA (10 min)

        #### 🏢 CONTEXTO DE NEGÓCIO (Score: ___/25)
        | Critério | Status | Evidência | Gap |
        |----------|--------|-----------|-----|
        | Problema bem definido | | | |
        | Objetivos SMART | | | |
        | Stakeholders identificados | | | |
        | Success criteria claros | | | |

        #### 📊 DADOS E ENGENHARIA (Score: ___/30)
        | Critério | Status | Evidência | Gap |
        |----------|--------|-----------|-----|
        | Fonte de dados documentada | | | |
        | Dicionário de variáveis | | | |
        | Pré-processamento descrito | | | |
        | Feature engineering | | | |
        | Qualidade de dados abordada | | | |

        #### 🔬 METODOLOGIA TÉCNICA (Score: ___/25)
        | Critério | Status | Evidência | Gap |
        |----------|--------|-----------|-----|
        | Algoritmo justificado | | | |
        | Estratégia de validação | | | |
        | Métricas apropriadas | | | |
        | Baseline estabelecido | | | |
        | Hiperparâmetros configurados | | | |

        #### 🛡️ GOVERNANÇA E RISCOS (Score: ___/20)
        | Critério | Status | Evidência | Gap |
        |----------|--------|-----------|-----|
        | Limitações explicitadas | | | |
        | Riscos identificados | | | |
        | Monitoramento planejado | | | |
        | Manutenção definida | | | |

        ## 📊 SISTEMA DE SCORING

        **Score Global = (Σ(Score_Seção × Peso_Seção))**

        ### CLASSIFICAÇÃO FINAL:
        - **90-100%:** ✅ **APROVADO** - Pronto para validação completa
        - **70-89%:** ⚠️ **APROVADO COM RESSALVAS** - Validação possível com ajustes menores
        - **50-69%:** 🔄 **REQUER MELHORIAS** - Gaps significativos, mas viável
        - **<50%:** ❌ **REPROVADO** - Elementos essenciais ausentes

        ## 🚨 FLAGS CRÍTICOS - REPROVAÇÃO AUTOMÁTICA
        - Problema de negócio não identificado
        - Dados sem origem ou descrição
        - Código não executável
        - Nenhuma métrica de avaliação
        - Algoritmo não especificado

        ## 📋 RELATÓRIO EXECUTIVO

        ### RESUMO EXECUTIVO
        **Score Final:** ___% | **Status:** _____ | **Tempo estimado para correções:** _____

        ### TOP 3 GAPS CRÍTICOS
        1. **[Categoria]** - [Descrição] - **Impacto:** [Alto/Médio/Baixo]
        2. **[Categoria]** - [Descrição] - **Impacto:** [Alto/Médio/Baixo]  
        3. **[Categoria]** - [Descrição] - **Impacto:** [Alto/Médio/Baixo]

        ### PLANO DE AÇÃO IMEDIATO
        #### Correções Obrigatórias (para aprovar):
        - [ ] [Ação específica 1]
        - [ ] [Ação específica 2]
        - [ ] [Ação específica 3]

        #### Melhorias Recomendadas (para otimizar):
        - [ ] [Sugestão 1]
        - [ ] [Sugestão 2]

        ### PRÓXIMOS PASSOS
        - **Se Aprovado:** Pode prosseguir para validação completa
        - **Se Ressalvas:** Implementar correções obrigatórias primeiro
        - **Se Reprovado:** Refazer documentação/código conforme gaps identificados

        ## 🔧 TEMPLATE DE FEEDBACK ESTRUTURADO

        ```
        RESULTADO DA PRÉ-VALIDAÇÃO
        ========================
        Projeto: [Nome do Projeto]
        Data: [Data da Análise]  
        Analista: [Nome/ID]

        SCORE DETALHADO:
        - Contexto Negócio: ___/25
        - Dados & Features: ___/30  
        - Metodologia: ___/25
        - Governança: ___/20
        
        TOTAL: ___/100

        STATUS: [APROVADO/RESSALVAS/REPROVADO]

        LACUNAS CRÍTICAS:
        [Lista numerada]

        RECOMENDAÇÕES:
        [Ações específicas]
        ```

        ## ⚡ DICAS PARA EFICIÊNCIA
        - Foque em **evidências objetivas**, não suposições
        - Identifique **blockers críticos** primeiro
        - Use **citações específicas** do documento
        - Mantenha análise **concisa e acionável**
        - Priorize **gaps de alto impacto**
        """

    def gerar_checklist_rapido(self):
        """Gera um checklist de 5 minutos para triagem inicial."""
        return """
        # CHECKLIST RÁPIDO DE PRÉ-VALIDAÇÃO (5 min)

        ## ⚡ TRIAGEM EXPRESSA - PASS/FAIL

        ### 🔍 VERIFICAÇÃO INICIAL (30 segundos cada)
        - [ ] **Problema de Negócio:** Está claramente descrito em 1-2 parágrafos?
        - [ ] **Dados Identificados:** Origem e principais variáveis mencionadas?
        - [ ] **Algoritmo Especificado:** Técnica de ML claramente nomeada?
        - [ ] **Código Executável:** Sem erros óbvios de sintaxe/imports?
        - [ ] **Métrica de Sucesso:** Pelo menos 1 indicador de performance?

        ### ⚠️ SINAIS DE ALERTA (RED FLAGS)
        - [ ] Problema vago ou genérico demais
        - [ ] Dados mencionados sem contexto ou origem
        - [ ] "Modelo de IA" sem especificar algoritmo
        - [ ] Código com muitos TODOs ou comentários vazios
        - [ ] Ausência total de validação/teste

        ## 🎯 DECISÃO RÁPIDA

        **SE TODOS OS CHECKS ✅ E NENHUM RED FLAG ⚠️:**
        → **PROSSEGUIR** para avaliação detalhada

        **SE 1-2 CHECKS ❌ OU 1 RED FLAG ⚠️:**  
        → **FEEDBACK DIRECIONADO** + nova submissão

        **SE 3+ CHECKS ❌ OU 2+ RED FLAGS ⚠️:**
        → **REPROVAR** + orientação para restruturação

        ## 📝 TEMPLATE DE FEEDBACK RÁPIDO

        ```
        TRIAGEM: [APROVADO/REPROVAR/FEEDBACK]
        
        MISSING CRÍTICOS:
        - [Item 1]
        - [Item 2]
        
        AÇÃO REQUERIDA:
        [1-2 frases específicas]
        
        TEMPO ESTIMADO PARA CORREÇÃO: [horas/dias]
        ```
        """

# Exemplo de uso do sistema
def exemplo_uso():
    """Demonstra como usar o sistema de pré-validação."""
    
    pre_validador = PreValidadorModelos()
    
    # Para documentação apenas
    prompt_doc = pre_validador.gerar_prompt_documentacao()
    
    # Para código apenas  
    prompt_code = pre_validador.gerar_prompt_codigo(multiplos_arquivos=False)
    
    # Para múltiplos códigos
    prompt_multi_code = pre_validador.gerar_prompt_codigo(multiplos_arquivos=True)
    
    # Para consistência código-documentação
    prompt_consistencia = pre_validador.gerar_prompt_consistencia()
    
    # Para triagem rápida
    checklist_rapido = pre_validador.gerar_checklist_rapido()
    
    # Prompt integrado (recomendado)
    prompt_integrado = pre_validador.gerar_prompt_integrado()
    
    return {
        'documentacao': prompt_doc,
        'codigo': prompt_code,
        'codigo_multiplo': prompt_multi_code,
        'consistencia': prompt_consistencia,
        'triagem_rapida': checklist_rapido,
        'integrado': prompt_integrado
    }

# Configurações recomendadas para diferentes cenários
CONFIGURACOES_RECOMENDADAS = {
    'startup_agil': {
        'foco': 'triagem_rapida',
        'criterios_relaxados': True,
        'tempo_maximo': '5-10 min',
        'score_minimo': 60
    },
    'empresa_regulada': {
        'foco': 'integrado',
        'criterios_rigorosos': True,
        'tempo_maximo': '15-20 min', 
        'score_minimo': 85
    },
    'prototipo_poc': {
        'foco': 'codigo',
        'criterios_tecnicos': True,
        'tempo_maximo': '10 min',
        'score_minimo': 70
    },
    'producao_critica': {
        'foco': 'consistencia',
        'criterios_governanca': True,
        'tempo_maximo': '20-30 min',
        'score_minimo': 90
    }
}

class ConfiguradorPreValidacao:
    """Classe para aplicar configurações específicas ao pré-validador."""
    
    def __init__(self, contexto='geral'):
        self.contexto = contexto
        self.config = CONFIGURACOES_RECOMENDADAS.get(contexto, self._config_default())
        
    def _config_default(self):
        """Configuração padrão para contextos não especificados."""
        return {
            'foco': 'integrado',
            'criterios_balanceados': True,
            'tempo_maximo': '15 min',
            'score_minimo': 75
        }
    
    def aplicar_configuracao(self, prompt_base):
        """Aplica a configuração específica ao prompt base."""
        config = self.config
        
        # Cabeçalho personalizado
        cabecalho = f"""
        # PRÉ-VALIDAÇÃO CONFIGURADA PARA: {self.contexto.upper().replace('_', ' ')}
        
        ⚙️ **CONFIGURAÇÃO ATIVA:**
        - Foco: {config['foco']}
        - Tempo máximo: {config['tempo_maximo']}
        - Score mínimo para aprovação: {config['score_minimo']}%
        
        """
        
        # Ajustes específicos por contexto
        ajustes = self._gerar_ajustes_contexto()
        
        return cabecalho + ajustes + prompt_base
    
    def _gerar_ajustes_contexto(self):
        """Gera ajustes específicos baseados no contexto."""
        
        if self.contexto == 'startup_agil':
            return """
        ## 🚀 AJUSTES PARA STARTUP/AMBIENTE ÁGIL
        
        **CRITÉRIOS RELAXADOS:**
        - Documentação: Aceitar bullets e esquemas simples
        - Governança: Foco em limitações básicas, monitoramento simplificado
        - Código: Priorizar funcionalidade vs. elegância
        
        **FOCO PRINCIPAL:**
        - ✅ MVP funcional e executável
        - ✅ Problema bem definido  
        - ✅ Dados identificados e acessíveis
        - ⚠️ Documentação pode ser básica
        - ⚠️ Governança pode ser simplificada
        
        **DECISÃO RÁPIDA:** Use apenas o checklist de 5 minutos + score mínimo 60%
        """
        
        elif self.contexto == 'empresa_regulada':
            return """
        ## 🏛️ AJUSTES PARA EMPRESA REGULADA
        
        **CRITÉRIOS RIGOROSOS:**
        - Governança: OBRIGATÓRIA e detalhada
        - Documentação: Completa e auditável
        - Riscos: Identificação e mitigação obrigatórias
        
        **FOCO PRINCIPAL:**
        - ✅ Compliance e auditabilidade
        - ✅ Rastreabilidade completa
        - ✅ Documentação de riscos e limitações
        - ✅ Plano de monitoramento robusto
        
        **ZERO TOLERÂNCIA PARA:**
        - Ausência de documentação de riscos
        - Dados sem origem clara
        - Falta de plano de monitoramento
        
        **DECISÃO:** Use avaliação integrada completa + score mínimo 85%
        """
        
        elif self.contexto == 'prototipo_poc':
            return """
        ## 🔬 AJUSTES PARA PROTÓTIPO/POC
        
        **FOCO TÉCNICO:**
        - Código: Funcionalidade e execução prioritárias
        - Documentação: Técnica, pode ser concisa
        - Experimentação: Aceitar abordagens exploratórias
        
        **FOCO PRINCIPAL:**
        - ✅ Código executável e funcional
        - ✅ Metodologia técnica sólida
        - ✅ Resultados demonstráveis
        - ⚠️ Contexto de negócio pode ser simplificado
        - ⚠️ Governança pode ser básica
        
        **DECISÃO:** Foque na validação técnica do código + score mínimo 70%
        """
        
        elif self.contexto == 'producao_critica':
            return """
        ## ⚡ AJUSTES PARA PRODUÇÃO CRÍTICA
        
        **MÁXIMO RIGOR:**
        - Consistência código-documentação: OBRIGATÓRIA
        - Todos os critérios devem ser SUFICIENTES
        - Governança completa e robusta
        
        **FOCO PRINCIPAL:**
        - ✅ Alinhamento perfeito código-documentação
        - ✅ Governança completa (riscos, monitoramento, manutenção)
        - ✅ Qualidade de código enterprise
        - ✅ Rastreabilidade end-to-end
        
        **REPROVAÇÃO AUTOMÁTICA PARA:**
        - Qualquer inconsistência crítica
        - Ausência de plano de monitoramento
        - Código sem tratamento de erros
        - Limitações não documentadas
        
        **DECISÃO:** Validação cruzada obrigatória + score mínimo 90%
        """
        
        else:
            return """
        ## ⚖️ CONFIGURAÇÃO BALANCEADA (PADRÃO)
        
        **CRITÉRIOS EQUILIBRADOS:**
        - Todos os aspectos têm importância similar
        - Score mínimo: 75%
        - Tempo: até 15 minutos
        
        **DECISÃO:** Use avaliação integrada com critérios balanceados
        """

# Exemplo prático de uso das configurações
def exemplo_pratico_configuracoes():
    """
    Exemplo de como aplicar as configurações na prática.
    """
    
    print("=== COMO USAR AS CONFIGURAÇÕES ===")
    print()
    
    # Cenário 1: Startup ágil
    print("🚀 CENÁRIO: STARTUP ÁGIL")
    configurador_startup = ConfiguradorPreValidacao('startup_agil')
    prompt_startup = configurador_startup.aplicar_configuracao("")
    print("Uso: Equipes pequenas, desenvolvimento rápido, MVP")
    print("Prompt: Foca em triagem rápida + critérios relaxados")
    print()
    
    # Cenário 2: Empresa regulada  
    print("🏛️ CENÁRIO: EMPRESA REGULADA (Bancos, Saúde)")
    configurador_regulada = ConfiguradorPreValidacao('empresa_regulada')
    prompt_regulada = configurador_regulada.aplicar_configuracao("")
    print("Uso: Compliance rigoroso, auditoria obrigatória")
    print("Prompt: Avaliação completa + critérios rigorosos")
    print()
    
    # Cenário 3: Protótipo
    print("🔬 CENÁRIO: PROTÓTIPO/POC")
    configurador_poc = ConfiguradorPreValidacao('prototipo_poc')
    prompt_poc = configurador_poc.aplicar_configuracao("")
    print("Uso: Validação técnica, experimentação")
    print("Prompt: Foca no código + critérios técnicos")
    print()
    
    return {
        'startup': prompt_startup,
        'regulada': prompt_regulada, 
        'poc': prompt_poc
    }