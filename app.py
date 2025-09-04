
# Remover warning deprecated - usar configuração adequada do Gradio
# warnings.filterwarnings("ignore", message="The 'tuples' format for chatbot messages is deprecated")

# Importa funções de processamento
import gradio as gr
import os

from config.variaveis import (
    nome_exib    
)

from frontend.variaveis_front import (
    logo_img,
    theme,
    css_interface,
    logo_validai,
    logo_validai_pre,
    logo_validai_rag,
    informacoes
)

from frontend.funcoes_front import (
    bt_exportar,
    altera_bt,
    on_dropdown_change   
)

from backend.Chat_LLM import chat_multimodal, chat_compare, fn_chat_rag_manual

# Definindo o diretório temporário
os.environ["GRADIO_TEMP_DIR"] = "./temp_files"


chatbot = gr.Chatbot(avatar_images = (None, logo_img),
                    height = "55vh", elem_id = "espaco_chat", label = nome_exib)
chatbot_rag = gr.Chatbot(avatar_images = (None, logo_img),
                    height = "55vh", elem_id = "espaco_chat", label = nome_exib)

multimodal_text = gr.MultimodalTextbox(file_count = 'multiple')

# Criando a interface com gr.Blocks()
with gr.Blocks(title="ValidAI - Docs, Códigos e RAG", theme = theme, css = css_interface, fill_height=True,fill_width=True) as validai:
    
    # Define as variáveis persistentes
    
    # Inputs adicionais para o Stream (chatbot normal)
    lista_abas = gr.State(None)
    block_chat = gr.State(0)
    arquivo_excel = gr.State("")
    chat = gr.State(None)
    
    # Inputs adicionais para o Compare
    historico_compare = gr.State("")
    
    # Inputs adicionais para o RAG
    selected_rag = gr.State(None)
    selected_rag_antes = gr.State(None)
    diretorio_rag = gr.State('base_conhecimento') 
    lista_arquivos = gr.State([])
    df_resumo = gr.State(None)
    chat_rag = gr.State(None)
    
    with gr.Tab("ValidAI"):
        output_3 = gr.ChatInterface(fn=chat_multimodal, 
                            title="""<img src='""" + logo_validai + """' style="height: 42px;">""", 
                            multimodal=True,
                            description = """<p style="margin-bottom: 9px !important;">Gestão de Risco de Modelos</p>""",
                            chatbot = chatbot,
                            additional_inputs=[lista_abas, block_chat, arquivo_excel, chat],
                            additional_outputs=[lista_abas, block_chat, arquivo_excel, chat],
                            textbox = multimodal_text
                       )
    with gr.Tab("ValidAI - Pré-Validador"):
        iface = gr.Interface(
            title="""<img src='""" + logo_validai_pre + """' style="height: 42px;">""", 
            fn=chat_compare,
            inputs=[
                gr.Files(label="Documentos", file_types = [".pdf"]),
                gr.Files(label="Códigos", file_types = [".ipynb", ".sas", ".py"]),
                historico_compare
            ],
            clear_btn = "Limpar",
            submit_btn = "Enviar",
            outputs=[gr.Markdown(max_height= "380px", elem_id = "saida_pre"), 
                     historico_compare],
            description="Envie os arquivos para a validação.",
            flagging_mode = "never",
            
        )
        botao = gr.Button("Gerar PDF")
        bt_d = gr.DownloadButton("Download the file", visible=False)
        botao.click(fn=bt_exportar, inputs = historico_compare, outputs= [botao, bt_d])
        bt_d.click(fn=altera_bt, outputs= [botao, bt_d])
        
    with gr.Tab("ValidAI - RAG"):
        output_4 = gr.ChatInterface(fn=fn_chat_rag_manual, 
                                title="""<img src='""" + logo_validai_rag + """' style="height: 42px;">""", 
                                multimodal=False,
                                description = """<p style="margin-bottom: 9px !important;">Gestão de Risco de Modelos</p>""",
                                chatbot = chatbot_rag,
                                additional_inputs=[selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag],
                                additional_outputs=[selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag]
                           )
        dropdown = gr.Dropdown(choices=["Conteúdos de 'INs'", 
                                        "Validações de Riscos de Mercado",
                                        "Validações de Riscos de Crédito",
                                       "Google Search"],
                               value=None,
                        label="Selecione uma opção de conteúdo", elem_id = "dropdown123")
        dropdown.change(fn=on_dropdown_change, inputs=[dropdown, selected_rag], outputs = selected_rag)
    with gr.Tab("Informações"):
        gr.Markdown(informacoes)

# validai.launch(share=True, show_api=False, allowed_paths=["../historico_conversas/"], quiet=True)
validai.launch(show_api=False, allowed_paths=["../historico_conversas/"], quiet=True)