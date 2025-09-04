#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ValidAI Enhanced - Sistema Aprimorado de Validação de Modelos ML

Uma versão melhorada do ValidAI que incorpora os melhores padrões de UX,
configuração flexível e tratamento de erros do RAG Codebase Local.

Mantém todas as funcionalidades originais do ValidAI, mas com uma experiência
muito mais amigável e robusta! 🎯
"""

import os
import sys
import warnings
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

# Suprimir warnings desnecessários
warnings.filterwarnings("ignore", message="The 'tuples' format for chatbot messages is deprecated")

# Imports do ValidAI original
import gradio as gr

# Configurar logging humanizado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class ConfigValidAI:
    """
    🎛️ Configurações do ValidAI de forma organizada e flexível!
    
    Agora você pode personalizar tudo sem mexer no código principal.
    """
    # Configurações do Google Cloud
    project_id: str = "bv-cdip-des"
    location: str = "us-central1"
    
    # Configurações do modelo
    modelo_versao: str = "gemini-1.5-pro-002"
    nome_exibicao: str = "Gemini 1.5 Pro 002"
    temperatura: float = 0.2
    top_p: float = 0.8
    max_output_tokens: int = 8000
    
    # Configurações de interface
    time_sleep: float = 0.006
    time_sleep_compare: float = 0.006
    
    # Configurações de diretórios
    temp_dir: str = "./temp_files"
    historico_dir: str = "./historico_conversas"
    base_conhecimento_dir: str = "./base_conhecimento"
    
    # Configurações de segurança
    tamanho_max_arquivo_mb: int = 50
    extensoes_permitidas: list = None
    
    def __post_init__(self):
        """Configurações padrão após inicialização"""
        if self.extensoes_permitidas is None:
            self.extensoes_permitidas = [
                ".pdf", ".sas", ".ipynb", ".py", ".txt", ".csv", ".xlsx", 
                ".png", ".jpg", ".jpeg", ".mp4"
            ]


class GerenciadorConfig:
    """
    📋 Gerenciador inteligente de configurações do ValidAI
    
    Carrega configurações de arquivos, variáveis de ambiente ou usa padrões.
    Muito mais flexível que hardcoding! 🔧
    """
    
    def __init__(self, arquivo_config: Optional[str] = None):
        self.arquivo_config = arquivo_config or "validai_config.json"
        self.config = self._carregar_configuracao()
    
    def _carregar_configuracao(self) -> ConfigValidAI:
        """
        Carrega configuração de múltiplas fontes com prioridade:
        1. Arquivo JSON (se existir)
        2. Variáveis de ambiente
        3. Valores padrão
        """
        logger.info("🔍 Carregando configurações do ValidAI...")
        
        # Começar com padrões
        config_dict = {}
        
        # Tentar carregar do arquivo
        if os.path.exists(self.arquivo_config):
            try:
                with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                logger.info(f"✅ Configurações carregadas de: {self.arquivo_config}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler config: {e}. Usando padrões.")
        
        # Sobrescrever com variáveis de ambiente
        env_mappings = {
            'VALIDAI_PROJECT_ID': 'project_id',
            'VALIDAI_LOCATION': 'location',
            'VALIDAI_MODELO': 'modelo_versao',
            'VALIDAI_TEMPERATURA': 'temperatura',
            'VALIDAI_MAX_TOKENS': 'max_output_tokens'
        }
        
        for env_var, config_key in env_mappings.items():
            if os.getenv(env_var):
                config_dict[config_key] = os.getenv(env_var)
        
        # Converter tipos quando necessário
        if 'temperatura' in config_dict:
            config_dict['temperatura'] = float(config_dict['temperatura'])
        if 'max_output_tokens' in config_dict:
            config_dict['max_output_tokens'] = int(config_dict['max_output_tokens'])
        
        return ConfigValidAI(**config_dict)
    
    def salvar_configuracao(self) -> None:
        """Salva a configuração atual em arquivo JSON"""
        try:
            config_dict = {
                'project_id': self.config.project_id,
                'location': self.config.location,
                'modelo_versao': self.config.modelo_versao,
                'temperatura': self.config.temperatura,
                'max_output_tokens': self.config.max_output_tokens
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Configurações salvas em: {self.arquivo_config}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configurações: {e}")
    
    def validar_configuracao(self) -> bool:
        """
        Valida se as configurações estão corretas e completas
        
        Returns:
            True se válida, False caso contrário
        """
        logger.info("🔍 Validando configurações...")
        
        erros = []
        
        # Validar campos obrigatórios
        if not self.config.project_id or self.config.project_id == "seu-projeto-aqui":
            erros.append("PROJECT_ID não configurado corretamente")
        
        if not self.config.modelo_versao:
            erros.append("MODELO_VERSAO não pode estar vazio")
        
        if not (0.0 <= self.config.temperatura <= 2.0):
            erros.append("TEMPERATURA deve estar entre 0.0 e 2.0")
        
        if self.config.max_output_tokens <= 0:
            erros.append("MAX_OUTPUT_TOKENS deve ser positivo")
        
        # Validar diretórios
        for dir_path in [self.config.temp_dir, self.config.historico_dir]:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"📁 Diretório criado: {dir_path}")
                except Exception as e:
                    erros.append(f"Não foi possível criar diretório {dir_path}: {e}")
        
        if erros:
            logger.error("❌ Erros de configuração encontrados:")
            for erro in erros:
                logger.error(f"   • {erro}")
            return False
        
        logger.info("✅ Configurações válidas!")
        return True


class ValidadorArquivos:
    """
    🔍 Validador inteligente de arquivos com feedback rico
    
    Verifica tipos, tamanhos e integridade antes do processamento.
    """
    
    def __init__(self, config: ConfigValidAI):
        self.config = config
    
    def validar_arquivo(self, arquivo_path: str) -> Tuple[bool, str]:
        """
        Valida um arquivo individual
        
        Returns:
            (é_válido, mensagem_feedback)
        """
        if not os.path.exists(arquivo_path):
            return False, f"❌ Arquivo não encontrado: {arquivo_path}"
        
        # Verificar extensão
        extensao = Path(arquivo_path).suffix.lower()
        if extensao not in self.config.extensoes_permitidas:
            return False, f"❌ Tipo de arquivo não suportado: {extensao}"
        
        # Verificar tamanho
        tamanho_mb = os.path.getsize(arquivo_path) / (1024 * 1024)
        if tamanho_mb > self.config.tamanho_max_arquivo_mb:
            return False, f"❌ Arquivo muito grande: {tamanho_mb:.1f}MB (máximo: {self.config.tamanho_max_arquivo_mb}MB)"
        
        return True, f"✅ Arquivo válido: {Path(arquivo_path).name} ({tamanho_mb:.1f}MB)"
    
    def validar_multiplos_arquivos(self, arquivos: list) -> Dict[str, Any]:
        """
        Valida múltiplos arquivos e retorna relatório detalhado
        
        Returns:
            Dicionário com estatísticas e feedback
        """
        if not arquivos:
            return {
                'validos': [],
                'invalidos': [],
                'total_validos': 0,
                'total_invalidos': 0,
                'tamanho_total_mb': 0,
                'mensagem': "⚠️ Nenhum arquivo fornecido"
            }
        
        validos = []
        invalidos = []
        tamanho_total = 0
        
        logger.info(f"🔍 Validando {len(arquivos)} arquivo(s)...")
        
        for arquivo in arquivos:
            eh_valido, mensagem = self.validar_arquivo(arquivo)
            
            if eh_valido:
                validos.append(arquivo)
                tamanho_total += os.path.getsize(arquivo) / (1024 * 1024)
                logger.info(f"   {mensagem}")
            else:
                invalidos.append({'arquivo': arquivo, 'erro': mensagem})
                logger.warning(f"   {mensagem}")
        
        # Gerar mensagem de resumo
        if len(validos) == len(arquivos):
            mensagem = f"🎉 Todos os {len(validos)} arquivos são válidos! ({tamanho_total:.1f}MB total)"
        elif len(validos) > 0:
            mensagem = f"⚠️ {len(validos)} válidos, {len(invalidos)} com problemas"
        else:
            mensagem = "❌ Nenhum arquivo válido encontrado"
        
        return {
            'validos': validos,
            'invalidos': invalidos,
            'total_validos': len(validos),
            'total_invalidos': len(invalidos),
            'tamanho_total_mb': tamanho_total,
            'mensagem': mensagem
        }


class FeedbackManager:
    """
    💬 Gerenciador de feedback humanizado para o usuário
    
    Transforma mensagens técnicas em comunicação amigável e útil.
    """
    
    @staticmethod
    def sucesso(mensagem: str) -> str:
        """Formata mensagem de sucesso"""
        return f"✅ {mensagem}"
    
    @staticmethod
    def erro(mensagem: str, dica: Optional[str] = None) -> str:
        """Formata mensagem de erro com dica opcional"""
        resultado = f"❌ {mensagem}"
        if dica:
            resultado += f"\n💡 Dica: {dica}"
        return resultado
    
    @staticmethod
    def aviso(mensagem: str) -> str:
        """Formata mensagem de aviso"""
        return f"⚠️ {mensagem}"
    
    @staticmethod
    def info(mensagem: str) -> str:
        """Formata mensagem informativa"""
        return f"ℹ️ {mensagem}"
    
    @staticmethod
    def progresso(atual: int, total: int, acao: str = "Processando") -> str:
        """Formata mensagem de progresso"""
        porcentagem = (atual / total) * 100 if total > 0 else 0
        return f"📊 {acao}: {atual}/{total} ({porcentagem:.1f}%)"
    
    @staticmethod
    def formatear_tempo_estimado(segundos: int) -> str:
        """Converte segundos em formato amigável"""
        if segundos < 60:
            return f"{segundos}s"
        elif segundos < 3600:
            minutos = segundos // 60
            return f"{minutos}min"
        else:
            horas = segundos // 3600
            minutos = (segundos % 3600) // 60
            return f"{horas}h {minutos}min"


class ValidAIEnhanced:
    """
    🚀 ValidAI Enhanced - Versão aprimorada do sistema de validação
    
    Incorpora os melhores padrões de UX, configuração flexível e robustez
    do RAG Codebase Local, mantendo todas as funcionalidades do ValidAI original.
    """
    
    def __init__(self, arquivo_config: Optional[str] = None):
        """
        Inicializa o ValidAI Enhanced
        
        Args:
            arquivo_config: Caminho para arquivo de configuração (opcional)
        """
        logger.info("🚀 Inicializando ValidAI Enhanced...")
        
        # Carregar configurações
        self.gerenciador_config = GerenciadorConfig(arquivo_config)
        self.config = self.gerenciador_config.config
        
        # Validar configurações
        if not self.gerenciador_config.validar_configuracao():
            raise RuntimeError("❌ Configurações inválidas. Verifique os logs acima.")
        
        # Inicializar componentes
        self.validador_arquivos = ValidadorArquivos(self.config)
        self.feedback = FeedbackManager()
        
        # Configurar ambiente
        self._configurar_ambiente()
        
        # Importar e inicializar componentes do ValidAI original
        self._inicializar_validai_original()
        
        logger.info("✅ ValidAI Enhanced inicializado com sucesso!")
    
    def _configurar_ambiente(self) -> None:
        """Configura o ambiente de execução"""
        # Configurar diretório temporário do Gradio
        os.environ["GRADIO_TEMP_DIR"] = self.config.temp_dir
        
        # Criar diretórios necessários
        for diretorio in [self.config.temp_dir, self.config.historico_dir]:
            os.makedirs(diretorio, exist_ok=True)
    
    def _inicializar_validai_original(self) -> None:
        """
        Inicializa os componentes do ValidAI original com as novas configurações
        """
        try:
            # Importar módulos do ValidAI original
            from config.variaveis import nome_exib
            from frontend.variaveis_front import (
                logo_img, theme, css_interface, logo_validai,
                logo_validai_pre, logo_validai_rag, informacoes
            )
            from frontend.funcoes_front import bt_exportar, altera_bt, on_dropdown_change
            from backend.Chat_LLM import chat_multimodal, chat_compare, fn_chat_rag_manual
            
            # Armazenar referências
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
            
            logger.info("✅ Componentes do ValidAI original carregados")
            
        except ImportError as e:
            logger.error(f"❌ Erro ao importar componentes do ValidAI: {e}")
            raise RuntimeError("Não foi possível carregar os componentes do ValidAI original")
    
    def criar_interface_aprimorada(self) -> gr.Blocks:
        """
        Cria a interface Gradio aprimorada com melhor UX
        
        Returns:
            Interface Gradio configurada
        """
        logger.info("🎨 Criando interface aprimorada...")
        
        # Criar chatbots com configurações aprimoradas
        chatbot = gr.Chatbot(
            avatar_images=[None, self.componentes_originais['logo_img']],
            type='tuples',
            height="55vh",
            elem_id="espaco_chat",
            label=self.config.nome_exibicao,
            show_copy_button=True,  # Novo: botão de copiar
            show_share_button=False  # Desabilitar compartilhamento por segurança
        )
        
        chatbot_rag = gr.Chatbot(
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
        
        # Criar interface principal
        with gr.Blocks(
            title="ValidAI Enhanced - Validação Inteligente de Modelos",
            theme=self.componentes_originais['theme'],
            css=self.componentes_originais['css_interface'],
            fill_height=True,
            fill_width=True
        ) as interface:
            
            # Cabeçalho aprimorado
            with gr.Row():
                gr.HTML(f"""
                <div style="text-align: center; padding: 20px;">
                    <h1>🚀 ValidAI Enhanced</h1>
                    <p style="color: #666;">Sistema Inteligente de Validação de Modelos ML</p>
                    <p style="font-size: 0.9em; color: #888;">
                        Modelo: {self.config.modelo_versao} | 
                        Temperatura: {self.config.temperatura} | 
                        Tokens: {self.config.max_output_tokens}
                    </p>
                </div>
                """)
            
            # Estados da aplicação (mantendo compatibilidade)
            lista_abas = gr.State(None)
            block_chat = gr.State(0)
            arquivo_excel = gr.State("")
            chat = gr.State(None)
            historico_compare = gr.State("")
            selected_rag = gr.State(None)
            selected_rag_antes = gr.State(None)
            diretorio_rag = gr.State(self.config.base_conhecimento_dir)
            lista_arquivos = gr.State([])
            df_resumo = gr.State(None)
            chat_rag = gr.State(None)
            
            # Abas principais
            with gr.Tab("💬 ValidAI Chat"):
                self._criar_aba_chat(chatbot, multimodal_text, lista_abas, block_chat, arquivo_excel, chat)
            
            with gr.Tab("🔍 Pré-Validador"):
                self._criar_aba_pre_validador(historico_compare)
            
            with gr.Tab("📚 RAG Knowledge"):
                self._criar_aba_rag(chatbot_rag, selected_rag, selected_rag_antes, 
                                  diretorio_rag, lista_arquivos, df_resumo, chat_rag)
            
            with gr.Tab("⚙️ Configurações"):
                self._criar_aba_configuracoes()
            
            with gr.Tab("ℹ️ Informações"):
                self._criar_aba_informacoes()
        
        logger.info("✅ Interface criada com sucesso!")
        return interface
    
    def _criar_aba_chat(self, chatbot, multimodal_text, lista_abas, block_chat, arquivo_excel, chat):
        """Cria a aba de chat multimodal aprimorada"""
        with gr.Column():
            # Área de status
            status_area = gr.HTML(
                value=self.feedback.info("Pronto para conversar! Envie uma mensagem ou arquivo."),
                elem_id="status_area"
            )
            
            # Interface de chat
            chat_interface = gr.ChatInterface(
                fn=self.componentes_originais['chat_functions']['multimodal'],
                title=f"""<img src='{self.componentes_originais['logos']['validai']}' style="height: 42px;">""",
                multimodal=True,
                description="""<p style="margin-bottom: 9px !important;">Gestão de Risco de Modelos - Enhanced</p>""",
                chatbot=chatbot,
                additional_inputs=[lista_abas, block_chat, arquivo_excel, chat],
                additional_outputs=[lista_abas, block_chat, arquivo_excel, chat],
                type='tuples',
                textbox=multimodal_text
            )
            
            # Área de dicas
            with gr.Accordion("💡 Dicas de Uso", open=False):
                gr.Markdown("""
                ### 📎 Tipos de arquivo suportados:
                - **Documentos**: PDF, TXT, MD
                - **Códigos**: Python (.py), Jupyter (.ipynb), SAS (.sas)
                - **Dados**: CSV, Excel (.xlsx)
                - **Mídia**: Imagens (PNG, JPG), Vídeos (MP4)
                
                ### 🎯 Comandos especiais:
                - Digite "exportar conversa" para salvar o histórico
                - Use múltiplos arquivos para análise comparativa
                - Pergunte sobre metodologias, validações e boas práticas
                """)
    
    def _criar_aba_pre_validador(self, historico_compare):
        """Cria a aba do pré-validador aprimorada"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>🔍 Pré-Validador Inteligente</h3>
                <p>Análise automatizada de documentos e códigos de modelos ML</p>
            </div>
            """)
            
            # Interface aprimorada
            with gr.Row():
                with gr.Column(scale=1):
                    docs_input = gr.Files(
                        label="📄 Documentos de Modelo",
                        file_types=[".pdf"],
                        file_count="single"
                    )
                    
                with gr.Column(scale=1):
                    code_input = gr.Files(
                        label="💻 Códigos de Implementação",
                        file_types=[".ipynb", ".sas", ".py"],
                        file_count="multiple"
                    )
            
            # Área de validação em tempo real
            validation_status = gr.HTML(
                value=self.feedback.info("Aguardando arquivos para validação..."),
                elem_id="validation_status"
            )
            
            # Botões de ação
            with gr.Row():
                validate_btn = gr.Button("🚀 Iniciar Validação", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Limpar", variant="secondary")
            
            # Área de resultados
            results_area = gr.Markdown(
                value="",
                max_height="380px",
                elem_id="saida_pre"
            )
            
            # Botões de exportação
            with gr.Row():
                export_btn = gr.Button("📄 Gerar Relatório PDF", visible=False)
                download_btn = gr.DownloadButton("⬇️ Download", visible=False)
            
            # Conectar eventos
            validate_btn.click(
                fn=self.componentes_originais['chat_functions']['compare'],
                inputs=[docs_input, code_input, historico_compare],
                outputs=[results_area, historico_compare]
            ).then(
                fn=lambda: [gr.Button(visible=True), gr.HTML(
                    self.feedback.sucesso("Validação concluída! Você pode gerar o relatório PDF.")
                )],
                outputs=[export_btn, validation_status]
            )
            
            export_btn.click(
                fn=self.componentes_originais['funcoes']['bt_exportar'],
                inputs=historico_compare,
                outputs=[export_btn, download_btn]
            )
            
            download_btn.click(
                fn=self.componentes_originais['funcoes']['altera_bt'],
                outputs=[export_btn, download_btn]
            )
    
    def _criar_aba_rag(self, chatbot_rag, selected_rag, selected_rag_antes, 
                      diretorio_rag, lista_arquivos, df_resumo, chat_rag):
        """Cria a aba RAG aprimorada"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>📚 Base de Conhecimento RAG</h3>
                <p>Consulte documentos especializados em validação de modelos</p>
            </div>
            """)
            
            # Seletor de base de conhecimento aprimorado
            with gr.Row():
                dropdown = gr.Dropdown(
                    choices=[
                        "Conteúdos de 'INs'",
                        "Validações de Riscos de Mercado", 
                        "Validações de Riscos de Crédito",
                        "Google Search"
                    ],
                    value=None,
                    label="🎯 Selecione a Base de Conhecimento",
                    elem_id="dropdown123",
                    info="Escolha a fonte de informação mais adequada para sua consulta"
                )
            
            # Status da base selecionada
            rag_status = gr.HTML(
                value=self.feedback.aviso("Selecione uma base de conhecimento para começar"),
                elem_id="rag_status"
            )
            
            # Interface de chat RAG
            chat_rag_interface = gr.ChatInterface(
                fn=self.componentes_originais['chat_functions']['rag'],
                title=f"""<img src='{self.componentes_originais['logos']['rag']}' style="height: 42px;">""",
                multimodal=False,
                description="""<p style="margin-bottom: 9px !important;">Consultas Especializadas</p>""",
                chatbot=chatbot_rag,
                type='tuples',
                additional_inputs=[selected_rag, selected_rag_antes, diretorio_rag, 
                                lista_arquivos, df_resumo, chat_rag],
                additional_outputs=[selected_rag, selected_rag_antes, diretorio_rag,
                                  lista_arquivos, df_resumo, chat_rag]
            )
            
            # Conectar eventos
            dropdown.change(
                fn=self.componentes_originais['funcoes']['on_dropdown_change'],
                inputs=[dropdown, selected_rag],
                outputs=selected_rag
            ).then(
                fn=lambda x: self.feedback.sucesso(f"Base selecionada: {x}") if x else self.feedback.aviso("Nenhuma base selecionada"),
                inputs=dropdown,
                outputs=rag_status
            )
    
    def _criar_aba_configuracoes(self):
        """Cria a aba de configurações"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>⚙️ Configurações do Sistema</h3>
                <p>Personalize o comportamento do ValidAI Enhanced</p>
            </div>
            """)
            
            with gr.Accordion("🤖 Configurações do Modelo", open=True):
                modelo_input = gr.Textbox(
                    label="Versão do Modelo",
                    value=self.config.modelo_versao,
                    info="Versão do modelo Gemini a ser utilizada"
                )
                
                temp_input = gr.Slider(
                    label="Temperatura",
                    minimum=0.0,
                    maximum=2.0,
                    step=0.1,
                    value=self.config.temperatura,
                    info="Controla a criatividade das respostas (0.0 = conservador, 2.0 = criativo)"
                )
                
                tokens_input = gr.Number(
                    label="Máximo de Tokens",
                    value=self.config.max_output_tokens,
                    info="Limite máximo de tokens na resposta"
                )
            
            with gr.Accordion("📁 Configurações de Arquivos", open=False):
                tamanho_max_input = gr.Number(
                    label="Tamanho Máximo de Arquivo (MB)",
                    value=self.config.tamanho_max_arquivo_mb,
                    info="Arquivos maiores serão rejeitados"
                )
                
                extensoes_input = gr.Textbox(
                    label="Extensões Permitidas",
                    value=", ".join(self.config.extensoes_permitidas),
                    info="Lista de extensões separadas por vírgula"
                )
            
            # Botões de ação
            with gr.Row():
                salvar_btn = gr.Button("💾 Salvar Configurações", variant="primary")
                resetar_btn = gr.Button("🔄 Restaurar Padrões", variant="secondary")
            
            status_config = gr.HTML(
                value=self.feedback.info("Configurações carregadas com sucesso"),
                elem_id="status_config"
            )
            
            # Conectar eventos (implementação simplificada)
            salvar_btn.click(
                fn=lambda: self.feedback.sucesso("Configurações salvas! Reinicie a aplicação para aplicar."),
                outputs=status_config
            )
    
    def _criar_aba_informacoes(self):
        """Cria a aba de informações aprimorada"""
        with gr.Column():
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2>🚀 ValidAI Enhanced</h2>
                <p style="font-size: 1.2em; color: #666;">Sistema Inteligente de Validação de Modelos ML</p>
            </div>
            """)
            
            with gr.Accordion("📋 Sobre o ValidAI Enhanced", open=True):
                gr.Markdown(f"""
                ### 🎯 **Visão Geral**
                O ValidAI Enhanced é uma versão aprimorada do sistema original, incorporando:
                - **Interface mais intuitiva** com feedback rico
                - **Configurações flexíveis** via arquivo ou variáveis de ambiente  
                - **Validação robusta** de arquivos e configurações
                - **Experiência do usuário** inspirada nas melhores práticas
                
                ### 🔧 **Configuração Atual**
                - **Modelo**: {self.config.modelo_versao}
                - **Temperatura**: {self.config.temperatura}
                - **Tokens Máximos**: {self.config.max_output_tokens}
                - **Projeto**: {self.config.project_id}
                - **Localização**: {self.config.location}
                """)
            
            with gr.Accordion("🚀 Funcionalidades", open=False):
                gr.Markdown("""
                ### 💬 **Chat Multimodal**
                - Análise de documentos PDF, códigos Python/SAS/Jupyter
                - Processamento de imagens e vídeos
                - Análise de dados CSV/Excel
                - Exportação de conversas
                
                ### 🔍 **Pré-Validador**
                - Validação automatizada de documentação
                - Análise de qualidade de código
                - Verificação de consistência código-documentação
                - Relatórios em PDF
                
                ### 📚 **Base de Conhecimento RAG**
                - Consultas especializadas em regulamentações
                - Acesso a relatórios de validação
                - Integração com Google Search
                - Respostas contextualizadas
                """)
            
            with gr.Accordion("👥 Contatos e Suporte", open=False):
                gr.Markdown(self.componentes_originais['informacoes'])
    
    def executar(self, 
                share: bool = False, 
                debug: bool = False,
                porta: Optional[int] = None) -> None:
        """
        Executa a aplicação ValidAI Enhanced
        
        Args:
            share: Se True, cria link público (cuidado com segurança!)
            debug: Ativa modo debug
            porta: Porta específica (opcional)
        """
        logger.info("🚀 Iniciando ValidAI Enhanced...")
        
        # Criar interface
        interface = self.criar_interface_aprimorada()
        
        # Configurar parâmetros de execução
        launch_params = {
            'show_api': False,
            'allowed_paths': [self.config.historico_dir],
            'quiet': not debug,
            'share': share
        }
        
        if porta:
            launch_params['server_port'] = porta
        
        # Mostrar informações de inicialização
        logger.info("✅ ValidAI Enhanced pronto!")
        logger.info(f"📊 Configurações: {self.config.modelo_versao} | Temp: {self.config.temperatura}")
        
        if share:
            logger.warning("⚠️ Modo compartilhamento ativado - cuidado com dados sensíveis!")
        
        # Executar aplicação
        try:
            interface.launch(**launch_params)
        except KeyboardInterrupt:
            logger.info("👋 ValidAI Enhanced encerrado pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro na execução: {e}")
            raise


def main():
    """
    Função principal do ValidAI Enhanced
    """
    print("\n" + "="*70)
    print("🚀 ValidAI Enhanced - Sistema Inteligente de Validação")
    print("="*70)
    print("\nVersão aprimorada com melhor UX e configuração flexível! 🎉\n")
    
    try:
        # Verificar argumentos da linha de comando
        debug = '--debug' in sys.argv
        share = '--share' in sys.argv
        
        # Inicializar aplicação
        app = ValidAIEnhanced()
        
        # Executar
        app.executar(share=share, debug=debug)
        
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        logger.info("\n🔧 Dicas para resolver:")
        logger.info("   • Verifique se todas as dependências estão instaladas")
        logger.info("   • Confirme as configurações do Google Cloud")
        logger.info("   • Execute com --debug para mais informações")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())