import gradio as gr
import pytz
import datetime
from src import DataManager

# Função do Dropdown
def on_dropdown_change(value, selected_rag):
    return value

# Função do botão de exportar a conversa
def bt_exportar(historico_compare):
    if historico_compare == "":
        gr.Warning("Necessário executar o relatório!")
        return [gr.Button(visible=True), 
                gr.DownloadButton(visible=False)]
    timezone = pytz.timezone('America/Sao_Paulo')
    now = datetime.datetime.now(timezone)
    date_time_str = now.strftime("%Y%m%d_%H_%M_%S")
    string_formatada = """<center>**Documento gerado pelo ValidAI**</center><br>
""" + historico_compare
    DataManager.gera_pdf(string_formatada, "historico_conversas/conversa_" + date_time_str)
    gr.Info("Arquivo gerado com sucesso: conversa_" + date_time_str + ".pdf")
    return [gr.Button(visible=False), 
            gr.DownloadButton(label=f"Download conversa_{date_time_str}", 
                              value="historico_conversas/conversa_" + date_time_str + ".pdf", 
                              visible=True)]

def altera_bt():
    # print("botao limpa clicado")
    return [gr.Button(visible=True), 
            gr.DownloadButton(visible=False)]