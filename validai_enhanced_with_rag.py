#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ValidAI Enhanced com Sistema RAG Avançado

Versão completa do ValidAI Enhanced integrando o novo sistema RAG
baseado em Vertex AI nativo, substituindo o RAG original.
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

# Imports do ValidAI Enhanced original
from validai_enhanced import (
    ConfigValidAI, GerenciadorConfig, ValidadorArquivos, 
    FeedbackManager, ValidAIEnhanced
)

# Import do novo sistema RAG
from validai_rag_system import ValidAIRAGManager, ValidAIRAGInterface, criar_configuracao_rag_padrao

logger = logging.getLogger(__name__)


class ValidAIEnhancedWithRAG(ValidAIEnhanced):
    """
    🚀 ValidAI Enhanced com Sistema RAG Avançado
    
    Extensão do ValidAI Enhanced que integra o novo sistema RAG
    baseado em Vertex AI nativo.
    """
    
    def __init__(self, arquivo_config: Optional[str] = None):
        """
        Inicializa ValidAI Enhanced com RAG avançado
        
        Args:
            arquivo_config: Caminho para arquivo de configuração
        """
        # Inicializar ValidAI Enhanced base
        super().__init__(arquivo_config)
        
        # Inicializar sistema RAG avançado
        self._inicializar_rag_avancado()
        
        logger.info("🚀 ValidAI Enhanced com RAG Avançado inicializado!")
    
    def _inicializar_rag_avancado(self) -> None:
        """Inicializa o sistema RAG avançado"""
        try:
            logger.info("📚 Inicializando sistema RAG avançado...")
            
            # Criar configuração RAG baseada na config principal
            config_rag = criar_configuracao_rag_padrao()
            config_rag.update({
                'project_id': self.config.project_id,
                'location': self.config.location,
                'bucket_name': getattr(self.config, 'rag_bucket_name', 'validai-rag-bucket')
            })
            
            # Inicializar gerenciador RAG
            self.rag_manager = ValidAIRAGManager(config_rag)
            
            # Criar interface RAG
            self.rag_interface = ValidAIRAGInterface(self.rag_manager)
            
            logger.info("✅ Sistema RAG avançado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar RAG: {e}")
            # Continuar sem RAG se houver erro
            self.rag_manager = None
            self.rag_interface = None
    
    def _criar_aba_rag_avancada(self) -> gr.Column:
        """
        Cria a aba RAG avançada substituindo a original
        
        Returns:
            Componente Gradio da aba RAG
        """
        with gr.Column() as aba_rag:
            # Cabeçalho
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>📚 Sistema RAG Avançado</h3>
                <p>Base de conhecimento inteligente com Vertex AI nativo</p>
            </div>
            """)
            
            if not self.rag_manager:
                # Mostrar erro se RAG não foi inicializado
                gr.HTML("""
                <div style="background: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h4>❌ Sistema RAG Indisponível</h4>
                    <p>O sistema RAG avançado não pôde ser inicializado. Verifique:</p>
                    <ul>
                        <li>Configurações do Google Cloud</li>
                        <li>Permissões do Vertex AI</li>
                        <li>Conectividade com a internet</li>
                    </ul>
                </div>
                """)
                return aba_rag
            
            # Painel de controle do RAG
            with gr.Accordion("🎛️ Painel de Controle RAG", open=True):
                with gr.Row():
                    with gr.Column(scale=2):
                        # Seletor de corpus
                        opcoes_corpus = self.rag_interface.obter_opcoes_corpus()
                        corpus_dropdown = gr.Dropdown(
                            choices=opcoes_corpus,
                            label="📚 Selecionar Base de Conhecimento",
                            info="Escolha a base mais adequada para sua consulta",
                            elem_id="rag_corpus_selector"
                        )
                    
                    with gr.Column(scale=1):
                        # Botões de ação
                        refresh_btn = gr.Button("🔄 Atualizar", size="sm")
                        setup_btn = gr.Button("⚙️ Configurar Corpus", size="sm")
                
                # Status do corpus selecionado
                corpus_status = gr.HTML(
                    value=self.feedback.info("Selecione uma base de conhecimento para começar"),
                    elem_id="corpus_status"
                )
            
            # Área de configuração de corpus (inicialmente oculta)
            with gr.Accordion("⚙️ Configuração de Corpus", open=False, visible=False) as config_accordion:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📤 Preparar Corpus")
                        
                        corpus_info_display = gr.JSON(
                            label="Informações do Corpus",
                            value={}
                        )
                        
                        with gr.Row():
                            upload_files_btn = gr.Button("📤 Enviar Arquivos", variant="primary")
                            create_corpus_btn = gr.Button("🧠 Criar Corpus", variant="secondary")
                            process_files_btn = gr.Button("📚 Processar", variant="secondary")
                        
                        setup_status = gr.HTML(
                            value="",
                            elem_id="setup_status"
                        )
            
            # Interface de chat RAG
            with gr.Row():
                with gr.Column():
                    # Chatbot RAG
                    chatbot_rag = gr.Chatbot(
                        label="💬 Consultas RAG",
                        height="400px",
                        show_copy_button=True,
                        avatar_images=[None, self.componentes_originais['logo_img']]
                    )
                    
                    # Input de mensagem
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="",
                            placeholder="Faça sua pergunta sobre a base de conhecimento selecionada...",
                            scale=4
                        )
                        send_btn = gr.Button("📤 Enviar", scale=1, variant="primary")
                    
                    # Botões de ação
                    with gr.Row():
                        clear_chat_btn = gr.Button("🗑️ Limpar Chat", size="sm")
                        export_chat_btn = gr.Button("📄 Exportar", size="sm")
            
            # Painel de estatísticas
            with gr.Accordion("📊 Estatísticas e Status", open=False):
                stats_display = gr.HTML(
                    value=self._gerar_estatisticas_rag(),
                    elem_id="rag_stats"
                )
                
                update_stats_btn = gr.Button("🔄 Atualizar Estatísticas")
            
            # Estados para o RAG
            corpus_selecionado_state = gr.State(None)
            chat_history_state = gr.State([])
            
            # Conectar eventos
            self._conectar_eventos_rag(
                corpus_dropdown, corpus_status, corpus_selecionado_state,
                config_accordion, corpus_info_display, setup_status,
                upload_files_btn, create_corpus_btn, process_files_btn,
                chatbot_rag, msg_input, send_btn, chat_history_state,
                clear_chat_btn, export_chat_btn, stats_display,
                refresh_btn, setup_btn, update_stats_btn
            )
        
        return aba_rag
    
    def _conectar_eventos_rag(self, *components):
        """Conecta todos os eventos da interface RAG"""
        (corpus_dropdown, corpus_status, corpus_selecionado_state,
         config_accordion, corpus_info_display, setup_status,
         upload_files_btn, create_corpus_btn, process_files_btn,
         chatbot_rag, msg_input, send_btn, chat_history_state,
         clear_chat_btn, export_chat_btn, stats_display,
         refresh_btn, setup_btn, update_stats_btn) = components
        
        # Seleção de corpus
        corpus_dropdown.change(
            fn=self._on_corpus_change,
            inputs=[corpus_dropdown],
            outputs=[corpus_status, corpus_selecionado_state, corpus_info_display]
        )
        
        # Mostrar/ocultar configuração
        setup_btn.click(
            fn=lambda: gr.Accordion(visible=True, open=True),
            outputs=config_accordion
        )
        
        # Atualizar opções
        refresh_btn.click(
            fn=self._refresh_corpus_options,
            outputs=[corpus_dropdown, stats_display]
        )
        
        # Configuração de corpus
        upload_files_btn.click(
            fn=self._upload_corpus_files,
            inputs=[corpus_selecionado_state],
            outputs=[setup_status]
        )
        
        create_corpus_btn.click(
            fn=self._create_corpus,
            inputs=[corpus_selecionado_state],
            outputs=[setup_status]
        )
        
        process_files_btn.click(
            fn=self._process_corpus_files,
            inputs=[corpus_selecionado_state],
            outputs=[setup_status]
        )
        
        # Chat
        send_btn.click(
            fn=self._process_rag_message,
            inputs=[msg_input, chat_history_state, corpus_selecionado_state],
            outputs=[chatbot_rag, msg_input, chat_history_state]
        )
        
        msg_input.submit(
            fn=self._process_rag_message,
            inputs=[msg_input, chat_history_state, corpus_selecionado_state],
            outputs=[chatbot_rag, msg_input, chat_history_state]
        )
        
        # Limpar chat
        clear_chat_btn.click(
            fn=lambda: ([], []),
            outputs=[chatbot_rag, chat_history_state]
        )
        
        # Atualizar estatísticas
        update_stats_btn.click(
            fn=self._gerar_estatisticas_rag,
            outputs=stats_display
        )
    
    def _on_corpus_change(self, corpus_id: str) -> Tuple[str, str, Dict]:
        """Manipula mudança de corpus selecionado"""
        if not corpus_id or not self.rag_interface:
            return (
                self.feedback.aviso("Nenhum corpus selecionado"),
                None,
                {}
            )
        
        try:
            # Selecionar corpus
            status_msg = self.rag_interface.selecionar_corpus(corpus_id)
            
            # Obter informações do corpus
            info = self.rag_manager.obter_estatisticas_corpus(corpus_id)
            
            return status_msg, corpus_id, info
            
        except Exception as e:
            return (
                self.feedback.erro(f"Erro ao selecionar corpus: {e}"),
                None,
                {}
            )
    
    def _refresh_corpus_options(self) -> Tuple[gr.Dropdown, str]:
        """Atualiza opções de corpus disponíveis"""
        if not self.rag_interface:
            return gr.Dropdown(choices=[]), "❌ Sistema RAG indisponível"
        
        try:
            opcoes = self.rag_interface.obter_opcoes_corpus()
            stats = self._gerar_estatisticas_rag()
            
            return (
                gr.Dropdown(choices=opcoes),
                stats
            )
            
        except Exception as e:
            return (
                gr.Dropdown(choices=[]),
                f"❌ Erro ao atualizar: {e}"
            )
    
    def _upload_corpus_files(self, corpus_id: str) -> str:
        """Faz upload dos arquivos de um corpus"""
        if not corpus_id or not self.rag_manager:
            return self.feedback.erro("Nenhum corpus selecionado")
        
        try:
            enviados, ignorados = self.rag_manager.enviar_arquivos_corpus(corpus_id)
            
            if enviados > 0:
                return self.feedback.sucesso(
                    f"Upload concluído: {enviados} arquivos enviados, {ignorados} ignorados"
                )
            else:
                return self.feedback.aviso("Nenhum arquivo foi enviado. Verifique o diretório.")
                
        except Exception as e:
            return self.feedback.erro(f"Erro no upload: {e}")
    
    def _create_corpus(self, corpus_id: str) -> str:
        """Cria um corpus no Vertex AI"""
        if not corpus_id or not self.rag_manager:
            return self.feedback.erro("Nenhum corpus selecionado")
        
        try:
            corpus_name = self.rag_manager.criar_corpus_rag(corpus_id)
            return self.feedback.sucesso(f"Corpus criado: {corpus_name}")
            
        except Exception as e:
            return self.feedback.erro(f"Erro ao criar corpus: {e}")
    
    def _process_corpus_files(self, corpus_id: str) -> str:
        """Processa arquivos de um corpus"""
        if not corpus_id or not self.rag_manager:
            return self.feedback.erro("Nenhum corpus selecionado")
        
        try:
            self.rag_manager.processar_arquivos_corpus(corpus_id)
            
            # Criar ferramenta de busca
            self.rag_manager.criar_ferramenta_busca(corpus_id)
            
            return self.feedback.sucesso(
                "Processamento iniciado! Aguarde alguns minutos para conclusão."
            )
            
        except Exception as e:
            return self.feedback.erro(f"Erro no processamento: {e}")
    
    def _process_rag_message(self, message: str, history: List, corpus_id: str) -> Tuple[List, str, List]:
        """Processa mensagem do chat RAG"""
        if not message.strip():
            return history, "", history
        
        if not corpus_id or not self.rag_interface:
            error_msg = "⚠️ Selecione um corpus antes de fazer perguntas"
            history.append([message, error_msg])
            return history, "", history
        
        try:
            # Processar consulta
            resposta = self.rag_interface.processar_consulta(message)
            
            # Adicionar ao histórico
            history.append([message, resposta])
            
            return history, "", history
            
        except Exception as e:
            error_msg = f"❌ Erro na consulta: {e}"
            history.append([message, error_msg])
            return history, "", history
    
    def _gerar_estatisticas_rag(self) -> str:
        """Gera estatísticas do sistema RAG"""
        if not self.rag_manager:
            return "❌ Sistema RAG indisponível"
        
        try:
            corpus_info = self.rag_manager.listar_corpus_disponiveis()
            
            html = """
            <div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">
                <h4>📊 Status dos Corpus RAG</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #e0e0e0;">
                        <th style="padding: 8px; text-align: left;">Corpus</th>
                        <th style="padding: 8px; text-align: center;">Arquivos</th>
                        <th style="padding: 8px; text-align: center;">Status</th>
                    </tr>
            """
            
            for info in corpus_info:
                status_icon = "✅" if info['corpus_criado'] else "⚠️"
                arquivos_text = "N/A" if not info['tem_arquivos'] else "Disponível"
                
                html += f"""
                    <tr>
                        <td style="padding: 8px;">{info['nome']}</td>
                        <td style="padding: 8px; text-align: center;">{arquivos_text}</td>
                        <td style="padding: 8px; text-align: center;">{status_icon}</td>
                    </tr>
                """
            
            html += """
                </table>
            </div>
            """
            
            return html
            
        except Exception as e:
            return f"❌ Erro ao gerar estatísticas: {e}"
    
    def criar_interface_aprimorada(self) -> gr.Blocks:
        """
        Cria interface com RAG avançado integrado
        
        Returns:
            Interface Gradio completa
        """
        logger.info("🎨 Criando interface com RAG avançado...")
        
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
            placeholder="Digite sua mensagem ou arraste arquivos aqui... 📎"
        )
        
        # Interface principal
        with gr.Blocks(
            title="ValidAI Enhanced - Sistema Completo de Validação",
            theme=self.componentes_originais['theme'],
            css=self.componentes_originais['css_interface'],
            fill_height=True,
            fill_width=True
        ) as interface:
            
            # Cabeçalho
            with gr.Row():
                gr.HTML(f"""
                <div style="text-align: center; padding: 20px;">
                    <h1>🚀 ValidAI Enhanced + RAG Avançado</h1>
                    <p style="color: #666;">Sistema Completo de Validação de Modelos ML</p>
                    <p style="font-size: 0.9em; color: #888;">
                        Modelo: {self.config.modelo_versao} | 
                        RAG: Vertex AI Nativo | 
                        Temperatura: {self.config.temperatura}
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
            with gr.Tab("💬 ValidAI Chat"):
                self._criar_aba_chat(chatbot, multimodal_text, lista_abas, block_chat, arquivo_excel, chat)
            
            with gr.Tab("🔍 Pré-Validador"):
                self._criar_aba_pre_validador(historico_compare)
            
            with gr.Tab("📚 RAG Avançado"):
                self._criar_aba_rag_avancada()
            
            with gr.Tab("⚙️ Configurações"):
                self._criar_aba_configuracoes()
            
            with gr.Tab("ℹ️ Informações"):
                self._criar_aba_informacoes_completa()
        
        logger.info("✅ Interface com RAG avançado criada!")
        return interface
    
    def _criar_aba_informacoes_completa(self):
        """Cria aba de informações incluindo RAG avançado"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2>🚀 ValidAI Enhanced + RAG Avançado</h2>
                <p style="font-size: 1.2em; color: #666;">Sistema Completo de Validação de Modelos ML</p>
            </div>
            """)
            
            with gr.Accordion("🆕 Novidades do RAG Avançado", open=True):
                gr.Markdown(f"""
                ### 🎯 **Sistema RAG Revolucionário**
                - **Vertex AI Nativo**: Tecnologia de ponta do Google Cloud
                - **Múltiplos Corpus**: Bases de conhecimento especializadas
                - **Processamento Inteligente**: Chunking otimizado e embeddings avançados
                - **Consultas Contextuais**: Respostas baseadas em documentos específicos
                
                ### 📚 **Bases de Conhecimento Disponíveis**
                - **Instruções Normativas**: INs 706, 1253, 1146
                - **Validações de Mercado**: Relatórios especializados
                - **Validações de Crédito**: Documentação técnica
                - **Metodologias**: Frameworks e boas práticas
                - **Casos de Uso**: Exemplos práticos
                
                ### 🔧 **Configuração Atual**
                - **Projeto**: {self.config.project_id}
                - **Localização**: {self.config.location}
                - **Modelo IA**: {self.config.modelo_versao}
                - **Embedding**: text-embedding-005
                """)
            
            # Incluir informações originais
            with gr.Accordion("📋 Informações Gerais", open=False):
                gr.Markdown(self.componentes_originais['informacoes'])


def main():
    """Função principal do ValidAI Enhanced com RAG"""
    print("\n" + "="*80)
    print("🚀 ValidAI Enhanced + RAG Avançado")
    print("="*80)
    print("\nSistema completo com RAG baseado em Vertex AI nativo! 🎉\n")
    
    try:
        # Verificar argumentos
        debug = '--debug' in sys.argv
        share = '--share' in sys.argv
        
        # Inicializar aplicação
        app = ValidAIEnhancedWithRAG()
        
        # Executar
        app.executar(share=share, debug=debug)
        
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        logger.info("\n🔧 Dicas para resolver:")
        logger.info("   • Verifique configurações do Google Cloud")
        logger.info("   • Confirme permissões do Vertex AI")
        logger.info("   • Execute com --debug para mais detalhes")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())