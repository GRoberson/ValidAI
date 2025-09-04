#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 ValidAI Enhanced Multimodal - Sistema Completo com RAG Multimodal

Versão mais avançada do ValidAI Enhanced que integra o sistema RAG multimodal
com suporte a imagens, vídeos, áudios e outros tipos de mídia.
"""

import os
import sys
import warnings
import logging
import gradio as gr
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

# Suprimir warnings
warnings.filterwarnings("ignore", message="The 'tuples' format for chatbot messages is deprecated")

# Imports do ValidAI Enhanced
from validai_enhanced import (
    ConfigValidAI, GerenciadorConfig, ValidadorArquivos, 
    FeedbackManager
)

# Import do sistema RAG multimodal
from validai_rag_multimodal import (
    ValidAIRAGMultimodal, ProcessadorMultimodal, 
    criar_configuracao_rag_multimodal
)

logger = logging.getLogger(__name__)


class ValidAIEnhancedMultimodal:
    """
    🎭 ValidAI Enhanced com Sistema RAG Multimodal
    
    Sistema completo que combina validação de modelos ML com
    capacidades RAG multimodais avançadas.
    """
    
    def __init__(self, arquivo_config: Optional[str] = None):
        """
        Inicializa ValidAI Enhanced Multimodal
        
        Args:
            arquivo_config: Caminho para arquivo de configuração
        """
        logger.info("🎭 Inicializando ValidAI Enhanced Multimodal...")
        
        # Inicializar configurações
        self.gerenciador_config = GerenciadorConfig(arquivo_config)
        self.config = self.gerenciador_config.config
        
        # Validar configurações
        if not self.gerenciador_config.validar_configuracao():
            raise RuntimeError("❌ Configurações inválidas")
        
        # Inicializar componentes
        self.validador_arquivos = ValidadorArquivos(self.config)
        self.feedback = FeedbackManager()
        
        # Configurar ambiente
        self._configurar_ambiente()
        
        # Inicializar componentes originais do ValidAI
        self._inicializar_validai_original()
        
        # Inicializar sistema RAG multimodal
        self._inicializar_rag_multimodal()
        
        logger.info("✅ ValidAI Enhanced Multimodal inicializado!")
    
    def _configurar_ambiente(self) -> None:
        """Configura o ambiente de execução"""
        os.environ["GRADIO_TEMP_DIR"] = self.config.temp_dir
        
        for diretorio in [self.config.temp_dir, self.config.historico_dir]:
            os.makedirs(diretorio, exist_ok=True)
    
    def _inicializar_validai_original(self) -> None:
        """Inicializa componentes do ValidAI original"""
        try:
            from config.variaveis import nome_exib
            from frontend.variaveis_front import (
                logo_img, theme, css_interface, logo_validai,
                logo_validai_pre, logo_validai_rag, informacoes
            )
            from frontend.funcoes_front import bt_exportar, altera_bt, on_dropdown_change
            from backend.Chat_LLM import chat_multimodal, chat_compare, fn_chat_rag_manual
            
            self.componentes_originais = {
                'nome_exib': nome_exib,
                'logo_img': logo_img,
                'theme': theme,
                'css_interface': css_interface,
                'logos': {
                    'validai': logo_validai,
                    'pre': logo_validai_pre,
                    'rag': logo_validai_rag
                },
                'informacoes': informacoes,
                'funcoes': {
                    'bt_exportar': bt_exportar,
                    'altera_bt': altera_bt,
                    'on_dropdown_change': on_dropdown_change
                },
                'chat_functions': {
                    'multimodal': chat_multimodal,
                    'compare': chat_compare,
                    'rag': fn_chat_rag_manual
                }
            }
            
            logger.info("✅ Componentes ValidAI original carregados")
            
        except ImportError as e:
            logger.error(f"❌ Erro ao importar componentes: {e}")
            raise RuntimeError("Componentes do ValidAI original não encontrados")
    
    def _inicializar_rag_multimodal(self) -> None:
        """Inicializa o sistema RAG multimodal"""
        try:
            logger.info("🎭 Inicializando sistema RAG multimodal...")
            
            # Criar configuração RAG multimodal
            config_rag = criar_configuracao_rag_multimodal()
            config_rag.update({
                'project_id': self.config.project_id,
                'location': self.config.location,
                'bucket_name': getattr(self.config, 'rag_bucket_name', 'validai-rag-multimodal')
            })
            
            # Inicializar sistema RAG multimodal
            self.rag_multimodal = ValidAIRAGMultimodal(config_rag)
            
            # Inicializar processador multimodal
            self.processador_multimodal = ProcessadorMultimodal(config_rag)
            
            logger.info("✅ Sistema RAG multimodal inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar RAG multimodal: {e}")
            self.rag_multimodal = None
            self.processador_multimodal = None
    
    def criar_interface_multimodal(self) -> gr.Blocks:
        """
        Cria interface completa com RAG multimodal
        
        Returns:
            Interface Gradio configurada
        """
        logger.info("🎨 Criando interface multimodal...")
        
        # Criar chatbots
        chatbot = gr.Chatbot(
            avatar_images=[None, self.componentes_originais['logo_img']],
            type='tuples',
            height="55vh",
            elem_id="espaco_chat",
            label=self.config.nome_exibicao,
            show_copy_button=True,
            show_share_button=False
        )
        
        multimodal_text = gr.MultimodalTextbox(
            file_count='multiple',
            placeholder="Digite sua mensagem ou arraste arquivos (incluindo imagens e vídeos)... 📎🎭"
        )
        
        # Interface principal
        with gr.Blocks(
            title="ValidAI Enhanced Multimodal - Sistema Completo",
            theme=self.componentes_originais['theme'],
            css=self.componentes_originais['css_interface'],
            fill_height=True,
            fill_width=True
        ) as interface:
            
            # Cabeçalho
            with gr.Row():
                gr.HTML(f"""
                <div style="text-align: center; padding: 20px;">
                    <h1>🎭 ValidAI Enhanced Multimodal</h1>
                    <p style="color: #666;">Sistema Completo com RAG Multimodal</p>
                    <p style="font-size: 0.9em; color: #888;">
                        Modelo: {self.config.modelo_versao} | 
                        RAG: Vertex AI + Gemini Vision | 
                        Suporte: Texto, Imagem, Vídeo, Áudio
                    </p>
                </div>
                """)
            
            # Estados da aplicação
            lista_abas = gr.State(None)
            block_chat = gr.State(0)
            arquivo_excel = gr.State("")
            chat = gr.State(None)
            historico_compare = gr.State("")
            
            # Abas principais
            with gr.Tab("💬 Chat Multimodal"):
                self._criar_aba_chat_multimodal(chatbot, multimodal_text, lista_abas, block_chat, arquivo_excel, chat)
            
            with gr.Tab("🔍 Pré-Validador"):
                self._criar_aba_pre_validador(historico_compare)
            
            with gr.Tab("🎭 RAG Multimodal"):
                self._criar_aba_rag_multimodal()
            
            with gr.Tab("🎨 Processador de Mídia"):
                self._criar_aba_processador_midia()
            
            with gr.Tab("⚙️ Configurações"):
                self._criar_aba_configuracoes()
            
            with gr.Tab("ℹ️ Informações"):
                self._criar_aba_informacoes_multimodal()
        
        logger.info("✅ Interface multimodal criada!")
        return interface
    
    def _criar_aba_chat_multimodal(self, chatbot, multimodal_text, lista_abas, block_chat, arquivo_excel, chat):
        """Cria aba de chat com capacidades multimodais aprimoradas"""
        with gr.Column():
            # Status multimodal
            status_multimodal = gr.HTML(
                value=self.feedback.info("Chat multimodal pronto! Suporte a texto, imagens, vídeos e áudios."),
                elem_id="status_multimodal"
            )
            
            # Interface de chat aprimorada
            chat_interface = gr.ChatInterface(
                fn=self._processar_chat_multimodal,
                title=f"""<img src='{self.componentes_originais['logos']['validai']}' style="height: 42px;">""",
                multimodal=True,
                description="""<p style="margin-bottom: 9px !important;">Chat Multimodal - Texto, Imagem, Vídeo, Áudio</p>""",
                chatbot=chatbot,
                additional_inputs=[lista_abas, block_chat, arquivo_excel, chat],
                additional_outputs=[lista_abas, block_chat, arquivo_excel, chat],
                type='tuples',
                textbox=multimodal_text
            )
            
            # Painel de capacidades multimodais
            with gr.Accordion("🎭 Capacidades Multimodais", open=False):
                gr.Markdown("""
                ### 📸 **Análise de Imagens**
                - Extração de texto de imagens (OCR)
                - Análise de gráficos e dashboards
                - Interpretação de diagramas técnicos
                - Descrição detalhada de conteúdo visual
                
                ### 🎥 **Processamento de Vídeos**
                - Análise de apresentações em vídeo
                - Extração de informações de slides
                - Transcrição de narração (quando possível)
                - Identificação de momentos importantes
                
                ### 🎵 **Análise de Áudio**
                - Transcrição de gravações
                - Análise de treinamentos e reuniões
                - Extração de insights técnicos
                - Identificação de conceitos importantes
                
                ### 📊 **Documentos Visuais**
                - PDFs com gráficos e imagens
                - Apresentações PowerPoint
                - Planilhas com visualizações
                - Relatórios com elementos visuais
                """)
    
    def _criar_aba_rag_multimodal(self):
        """Cria aba do RAG multimodal"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>🎭 Sistema RAG Multimodal</h3>
                <p>Base de conhecimento inteligente com suporte a múltiplas mídias</p>
            </div>
            """)
            
            if not self.rag_multimodal:
                gr.HTML("""
                <div style="background: #ffebee; padding: 20px; border-radius: 8px;">
                    <h4>❌ Sistema RAG Multimodal Indisponível</h4>
                    <p>Verifique as configurações do Google Cloud e Vertex AI.</p>
                </div>
                """)
                return
            
            # Seletor de corpus multimodal
            with gr.Row():
                corpus_multimodal_dropdown = gr.Dropdown(
                    choices=self._obter_opcoes_corpus_multimodal(),
                    label="🎭 Selecionar Base Multimodal",
                    info="Bases com suporte a imagens, vídeos e áudios"
                )
                
                refresh_multimodal_btn = gr.Button("🔄 Atualizar", size="sm")
            
            # Status do corpus multimodal
            corpus_multimodal_status = gr.HTML(
                value=self.feedback.info("Selecione uma base multimodal para começar")
            )
            
            # Painel de processamento multimodal
            with gr.Accordion("🎨 Processamento de Mídia", open=False):
                with gr.Row():
                    with gr.Column():
                        process_media_btn = gr.Button("🎭 Processar Mídias", variant="primary")
                        extract_texts_btn = gr.Button("📝 Extrair Textos", variant="secondary")
                    
                    with gr.Column():
                        save_extracts_btn = gr.Button("💾 Salvar Extrações", variant="secondary")
                        view_stats_btn = gr.Button("📊 Ver Estatísticas", variant="secondary")
                
                processing_status = gr.HTML(value="")
                processing_output = gr.JSON(label="Resultados do Processamento", value={})
            
            # Chat multimodal
            with gr.Row():
                chatbot_multimodal = gr.Chatbot(
                    label="💬 Consultas Multimodais",
                    height="400px",
                    show_copy_button=True,
                    avatar_images=[None, self.componentes_originais['logo_img']]
                )
            
            with gr.Row():
                msg_multimodal_input = gr.Textbox(
                    placeholder="Pergunte sobre textos, imagens, vídeos ou áudios da base...",
                    scale=4
                )
                send_multimodal_btn = gr.Button("🎭 Enviar", scale=1, variant="primary")
            
            # Opções de consulta
            with gr.Row():
                include_visual_context = gr.Checkbox(
                    label="🎨 Incluir contexto visual",
                    value=True,
                    info="Incluir informações de imagens e vídeos na resposta"
                )
                
                clear_multimodal_btn = gr.Button("🗑️ Limpar", size="sm")
            
            # Estados para RAG multimodal
            corpus_multimodal_state = gr.State(None)
            chat_multimodal_history = gr.State([])
            
            # Conectar eventos
            self._conectar_eventos_rag_multimodal(
                corpus_multimodal_dropdown, corpus_multimodal_status, corpus_multimodal_state,
                process_media_btn, extract_texts_btn, save_extracts_btn, view_stats_btn,
                processing_status, processing_output,
                chatbot_multimodal, msg_multimodal_input, send_multimodal_btn,
                include_visual_context, clear_multimodal_btn, chat_multimodal_history,
                refresh_multimodal_btn
            )
    
    def _criar_aba_processador_midia(self):
        """Cria aba dedicada ao processamento de mídia"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>🎨 Processador de Mídia</h3>
                <p>Análise individual de imagens, vídeos e áudios</p>
            </div>
            """)
            
            # Upload de arquivo de mídia
            with gr.Row():
                media_file = gr.File(
                    label="📎 Selecionar Arquivo de Mídia",
                    file_types=["image", "video", "audio"]
                )
            
            # Tipo de análise
            with gr.Row():
                analysis_type = gr.Radio(
                    choices=[
                        "🔍 Análise Completa",
                        "📝 Extração de Texto",
                        "📊 Análise Técnica",
                        "🎯 Contexto Específico"
                    ],
                    value="🔍 Análise Completa",
                    label="Tipo de Análise"
                )
            
            # Prompt personalizado
            custom_prompt = gr.Textbox(
                label="📝 Prompt Personalizado (Opcional)",
                placeholder="Descreva o que você quer analisar especificamente...",
                lines=3
            )
            
            # Botão de análise
            analyze_media_btn = gr.Button("🎭 Analisar Mídia", variant="primary", size="lg")
            
            # Resultados
            media_analysis_output = gr.Markdown(
                label="📋 Resultado da Análise",
                value="",
                max_height="400px"
            )
            
            # Conectar evento
            analyze_media_btn.click(
                fn=self._analisar_midia_individual,
                inputs=[media_file, analysis_type, custom_prompt],
                outputs=media_analysis_output
            )
    
    def _criar_aba_pre_validador(self, historico_compare):
        """Cria aba do pré-validador (mantém funcionalidade original)"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>🔍 Pré-Validador Inteligente</h3>
                <p>Análise automatizada de documentos e códigos</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    docs_input = gr.Files(
                        label="📄 Documentos",
                        file_types=[".pdf"]
                    )
                
                with gr.Column(scale=1):
                    code_input = gr.Files(
                        label="💻 Códigos",
                        file_types=[".ipynb", ".sas", ".py"]
                    )
            
            validation_status = gr.HTML(
                value=self.feedback.info("Aguardando arquivos para validação...")
            )
            
            with gr.Row():
                validate_btn = gr.Button("🚀 Validar", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Limpar", variant="secondary")
            
            results_area = gr.Markdown(value="", max_height="380px")
            
            with gr.Row():
                export_btn = gr.Button("📄 Gerar PDF", visible=False)
                download_btn = gr.DownloadButton("⬇️ Download", visible=False)
            
            # Conectar eventos (usando função original)
            validate_btn.click(
                fn=self.componentes_originais['chat_functions']['compare'],
                inputs=[docs_input, code_input, historico_compare],
                outputs=[results_area, historico_compare]
            )
    
    def _criar_aba_configuracoes(self):
        """Cria aba de configurações multimodais"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>⚙️ Configurações Multimodais</h3>
                <p>Ajustes para processamento de mídia e RAG</p>
            </div>
            """)
            
            with gr.Accordion("🎭 Configurações de Mídia", open=True):
                limite_video = gr.Number(
                    label="📹 Limite de Vídeo (MB)",
                    value=100,
                    info="Tamanho máximo para arquivos de vídeo"
                )
                
                limite_audio = gr.Number(
                    label="🎵 Limite de Áudio (MB)",
                    value=50,
                    info="Tamanho máximo para arquivos de áudio"
                )
                
                modelo_vision = gr.Dropdown(
                    choices=["gemini-1.5-pro-002", "gemini-1.5-flash-002"],
                    value="gemini-1.5-pro-002",
                    label="👁️ Modelo Vision",
                    info="Modelo para análise de imagens e vídeos"
                )
            
            with gr.Accordion("🧠 Configurações RAG", open=False):
                chunk_size = gr.Number(
                    label="📄 Tamanho do Chunk",
                    value=1024,
                    info="Tamanho dos pedaços de texto para processamento"
                )
                
                similarity_threshold = gr.Slider(
                    label="🎯 Limite de Similaridade",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.5,
                    info="Limite mínimo de similaridade para busca"
                )
            
            save_config_btn = gr.Button("💾 Salvar Configurações", variant="primary")
            config_status = gr.HTML(value="")
            
            save_config_btn.click(
                fn=lambda: self.feedback.sucesso("Configurações salvas!"),
                outputs=config_status
            )
    
    def _criar_aba_informacoes_multimodal(self):
        """Cria aba de informações sobre capacidades multimodais"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2>🎭 ValidAI Enhanced Multimodal</h2>
                <p style="font-size: 1.2em; color: #666;">Sistema Completo com Capacidades Multimodais</p>
            </div>
            """)
            
            with gr.Accordion("🆕 Capacidades Multimodais", open=True):
                gr.Markdown(f"""
                ### 🎭 **Sistema RAG Multimodal**
                - **Gemini Vision**: Análise avançada de imagens e vídeos
                - **Processamento de Áudio**: Transcrição e análise de conteúdo
                - **Extração Inteligente**: Texto, dados e insights de qualquer mídia
                - **Consultas Contextuais**: Perguntas sobre conteúdo visual e auditivo
                
                ### 🎨 **Tipos de Mídia Suportados**
                - **Imagens**: JPG, PNG, GIF, BMP, WebP, TIFF
                - **Vídeos**: MP4, AVI, MOV, WMV, WebM, MKV
                - **Áudios**: MP3, WAV, FLAC, AAC, OGG, M4A
                - **Documentos**: PDF, DOCX, PPTX com elementos visuais
                
                ### 🔧 **Configuração Atual**
                - **Projeto**: {self.config.project_id}
                - **Modelo Vision**: gemini-1.5-pro-002
                - **Limite Vídeo**: 100 MB
                - **Limite Áudio**: 50 MB
                """)
    
    def _obter_opcoes_corpus_multimodal(self) -> List[Tuple[str, str]]:
        """Obtém opções de corpus multimodais"""
        if not self.rag_multimodal:
            return []
        
        opcoes = []
        for corpus_id, config in self.rag_multimodal.corpus_configs.items():
            if config.ativo and config.suporte_multimodal:
                nome_exibicao = f"🎭 {config.nome}"
                opcoes.append((nome_exibicao, corpus_id))
        
        return opcoes
    
    def _processar_chat_multimodal(self, message, history, *args):
        """Processa mensagens do chat multimodal com capacidades aprimoradas"""
        try:
            # Verificar se há arquivos de mídia na mensagem
            if hasattr(message, 'files') and message.files and self.processador_multimodal:
                # Processar arquivos de mídia primeiro
                arquivos_processados = []
                
                for arquivo in message.files:
                    if self.processador_multimodal.detectar_tipo_midia(arquivo.name) != 'desconhecido':
                        # Extrair informações da mídia
                        info_midia = self.processador_multimodal.extrair_texto_de_midia(
                            arquivo.name, self.rag_multimodal.cliente_ia if self.rag_multimodal else None
                        )
                        arquivos_processados.append(f"📎 {arquivo.name}: {info_midia[:200]}...")
                
                # Adicionar contexto multimodal à mensagem
                if arquivos_processados:
                    contexto_multimodal = "\n\n🎭 **Contexto Multimodal:**\n" + "\n".join(arquivos_processados)
                    
                    # Modificar a mensagem para incluir contexto
                    if hasattr(message, 'text'):
                        message.text += contexto_multimodal
                    elif isinstance(message, str):
                        message += contexto_multimodal
            
            # Processar com a função original, agora com contexto multimodal
            return self.componentes_originais['chat_functions']['multimodal'](message, history, *args)
            
        except Exception as e:
            # Fallback para função original em caso de erro
            logger.warning(f"⚠️ Erro no processamento multimodal: {e}. Usando função original.")
            return self.componentes_originais['chat_functions']['multimodal'](message, history, *args)
    
    def _analisar_midia_individual(self, arquivo, tipo_analise, prompt_personalizado):
        """Analisa um arquivo de mídia individual"""
        if not arquivo or not self.processador_multimodal:
            return self.feedback.erro("Selecione um arquivo e verifique se o sistema multimodal está ativo")
        
        try:
            # Detectar tipo de mídia
            tipo_midia = self.processador_multimodal.detectar_tipo_midia(arquivo.name)
            
            if tipo_midia == 'desconhecido':
                return self.feedback.erro("Tipo de arquivo não suportado")
            
            # Extrair texto/análise
            resultado = self.processador_multimodal.extrair_texto_de_midia(
                arquivo.name, self.rag_multimodal.cliente_ia
            )
            
            # Formatear resultado
            return f"""
# 🎭 Análise de Mídia

**Arquivo:** {Path(arquivo.name).name}  
**Tipo:** {tipo_midia.upper()}  
**Análise:** {tipo_analise}

## Resultado

{resultado}
"""
            
        except Exception as e:
            return self.feedback.erro(f"Erro na análise: {e}")
    
    def _on_corpus_multimodal_change(self, corpus_id: str) -> Tuple[str, str]:
        """Manipula mudança de corpus multimodal selecionado"""
        if not corpus_id or not self.rag_multimodal:
            return (
                self.feedback.aviso("Nenhum corpus multimodal selecionado"),
                None
            )
        
        try:
            # Verificar se corpus existe
            if corpus_id not in self.rag_multimodal.corpus_configs:
                return (
                    self.feedback.erro(f"Corpus não encontrado: {corpus_id}"),
                    None
                )
            
            config = self.rag_multimodal.corpus_configs[corpus_id]
            
            # Verificar arquivos disponíveis
            info = self.rag_multimodal.verificar_arquivos_corpus(corpus_id)
            
            if info['arquivos_validos'] == 0:
                return (
                    self.feedback.aviso(f"{config.nome} selecionado, mas não há arquivos válidos"),
                    corpus_id
                )
            
            return (
                self.feedback.sucesso(f"{config.nome} selecionado ({info['arquivos_validos']} arquivos, {info['arquivos_imagem']} imagens, {info['arquivos_video']} vídeos)"),
                corpus_id
            )
            
        except Exception as e:
            return (
                self.feedback.erro(f"Erro ao selecionar corpus: {e}"),
                None
            )
    
    def _refresh_corpus_multimodal_options(self) -> Tuple[gr.Dropdown, str]:
        """Atualiza opções de corpus multimodais"""
        if not self.rag_multimodal:
            return (
                gr.Dropdown(choices=[]),
                self.feedback.erro("Sistema RAG multimodal indisponível")
            )
        
        try:
            opcoes = self._obter_opcoes_corpus_multimodal()
            return (
                gr.Dropdown(choices=opcoes),
                self.feedback.sucesso(f"{len(opcoes)} corpus multimodais disponíveis")
            )
        except Exception as e:
            return (
                gr.Dropdown(choices=[]),
                self.feedback.erro(f"Erro ao atualizar opções: {e}")
            )
    
    def _process_multimodal_corpus(self, corpus_id: str) -> Tuple[str, Dict]:
        """Processa arquivos multimodais de um corpus"""
        if not corpus_id or not self.rag_multimodal:
            return (
                self.feedback.erro("Nenhum corpus selecionado ou sistema indisponível"),
                {}
            )
        
        try:
            # Processar arquivos multimodais
            estatisticas = self.rag_multimodal.processar_arquivos_multimodais(corpus_id)
            
            status_msg = self.feedback.sucesso(
                f"Processamento concluído: {estatisticas['arquivos_processados']} arquivos processados"
            )
            
            return (status_msg, estatisticas)
            
        except Exception as e:
            return (
                self.feedback.erro(f"Erro no processamento: {e}"),
                {}
            )
    
    def _extract_texts_from_media(self, corpus_id: str) -> Tuple[str, Dict]:
        """Extrai textos de arquivos de mídia"""
        if not corpus_id or not self.rag_multimodal:
            return (
                self.feedback.erro("Nenhum corpus selecionado"),
                {}
            )
        
        try:
            # Processar e extrair textos
            estatisticas = self.rag_multimodal.processar_arquivos_multimodais(corpus_id)
            
            textos_extraidos = len(estatisticas.get('textos_extraidos', []))
            
            return (
                self.feedback.sucesso(f"Textos extraídos de {textos_extraidos} arquivos de mídia"),
                estatisticas
            )
            
        except Exception as e:
            return (
                self.feedback.erro(f"Erro na extração: {e}"),
                {}
            )
    
    def _save_extracted_texts(self, corpus_id: str, processing_output: Dict) -> str:
        """Salva textos extraídos em arquivo"""
        if not corpus_id or not processing_output:
            return self.feedback.erro("Dados insuficientes para salvar")
        
        try:
            arquivo_salvo = self.rag_multimodal.salvar_textos_extraidos(corpus_id, processing_output)
            return self.feedback.sucesso(f"Textos salvos em: {arquivo_salvo}")
            
        except Exception as e:
            return self.feedback.erro(f"Erro ao salvar: {e}")
    
    def _view_multimodal_stats(self, corpus_id: str) -> Dict:
        """Visualiza estatísticas do corpus multimodal"""
        if not corpus_id or not self.rag_multimodal:
            return {"erro": "Corpus não selecionado"}
        
        try:
            stats = self.rag_multimodal.obter_estatisticas_corpus(corpus_id)
            return stats
            
        except Exception as e:
            return {"erro": f"Erro ao obter estatísticas: {e}"}
    
    def _process_multimodal_message(self, message: str, history: List, 
                                  corpus_id: str, include_visual: bool) -> Tuple[List, str, List]:
        """Processa mensagem do chat multimodal"""
        if not message.strip():
            return history, "", history
        
        if not corpus_id or not self.rag_multimodal:
            error_msg = "⚠️ Selecione um corpus multimodal antes de fazer perguntas"
            history.append([message, error_msg])
            return history, "", history
        
        try:
            # Processar consulta multimodal
            resposta = self.rag_multimodal.consultar_multimodal(
                corpus_id, message, include_visual
            )
            
            # Adicionar cabeçalho informativo
            config = self.rag_multimodal.corpus_configs[corpus_id]
            cabecalho = f"**🎭 Consultando: {config.nome}** (Multimodal)\n\n"
            
            history.append([message, cabecalho + resposta])
            return history, "", history
            
        except Exception as e:
            error_msg = f"❌ Erro na consulta multimodal: {e}"
            history.append([message, error_msg])
            return history, "", history
    
    def _conectar_eventos_rag_multimodal(self, *components):
        """Conecta eventos da interface RAG multimodal"""
        (corpus_multimodal_dropdown, corpus_multimodal_status, corpus_multimodal_state,
         process_media_btn, extract_texts_btn, save_extracts_btn, view_stats_btn,
         processing_status, processing_output,
         chatbot_multimodal, msg_multimodal_input, send_multimodal_btn,
         include_visual_context, clear_multimodal_btn, chat_multimodal_history,
         refresh_multimodal_btn) = components
        
        # Seleção de corpus multimodal
        corpus_multimodal_dropdown.change(
            fn=self._on_corpus_multimodal_change,
            inputs=[corpus_multimodal_dropdown],
            outputs=[corpus_multimodal_status, corpus_multimodal_state]
        )
        
        # Atualizar opções
        refresh_multimodal_btn.click(
            fn=self._refresh_corpus_multimodal_options,
            outputs=[corpus_multimodal_dropdown, corpus_multimodal_status]
        )
        
        # Processamento de mídia
        process_media_btn.click(
            fn=self._process_multimodal_corpus,
            inputs=[corpus_multimodal_state],
            outputs=[processing_status, processing_output]
        )
        
        extract_texts_btn.click(
            fn=self._extract_texts_from_media,
            inputs=[corpus_multimodal_state],
            outputs=[processing_status, processing_output]
        )
        
        save_extracts_btn.click(
            fn=self._save_extracted_texts,
            inputs=[corpus_multimodal_state, processing_output],
            outputs=[processing_status]
        )
        
        view_stats_btn.click(
            fn=self._view_multimodal_stats,
            inputs=[corpus_multimodal_state],
            outputs=[processing_output]
        )
        
        # Chat multimodal
        send_multimodal_btn.click(
            fn=self._process_multimodal_message,
            inputs=[msg_multimodal_input, chat_multimodal_history, 
                   corpus_multimodal_state, include_visual_context],
            outputs=[chatbot_multimodal, msg_multimodal_input, chat_multimodal_history]
        )
        
        msg_multimodal_input.submit(
            fn=self._process_multimodal_message,
            inputs=[msg_multimodal_input, chat_multimodal_history, 
                   corpus_multimodal_state, include_visual_context],
            outputs=[chatbot_multimodal, msg_multimodal_input, chat_multimodal_history]
        )
        
        # Limpar chat
        clear_multimodal_btn.click(
            fn=lambda: ([], []),
            outputs=[chatbot_multimodal, chat_multimodal_history]
        )
    
    def executar(self, share: bool = False, debug: bool = False, porta: Optional[int] = None):
        """Executa a aplicação multimodal"""
        logger.info("🎭 Iniciando ValidAI Enhanced Multimodal...")
        
        interface = self.criar_interface_multimodal()
        
        launch_params = {
            'show_api': False,
            'allowed_paths': [self.config.historico_dir],
            'quiet': not debug,
            'share': share
        }
        
        if porta:
            launch_params['server_port'] = porta
        
        logger.info("✅ ValidAI Enhanced Multimodal pronto!")
        logger.info(f"🎭 Capacidades: Texto, Imagem, Vídeo, Áudio")
        
        try:
            interface.launch(**launch_params)
        except KeyboardInterrupt:
            logger.info("👋 Aplicação encerrada")
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            raise


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("🎭 ValidAI Enhanced Multimodal")
    print("="*80)
    print("\nSistema completo com RAG multimodal! 🎉\n")
    
    try:
        debug = '--debug' in sys.argv
        share = '--share' in sys.argv
        
        app = ValidAIEnhancedMultimodal()
        app.executar(share=share, debug=debug)
        
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())