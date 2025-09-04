# Importando os pacotes necessários
import pandas as pd
import base64
import nbformat
import chardet
import io
import csv
import openpyxl
import os
import Markdown2docx
from Markdown2docx import Markdown2docx
from google.genai import types

# Pacotes para Linux e GCP
# import weasyprint
# from weasyprint import HTML

# Alternativa para Windows
from xhtml2pdf import pisa

# Função para processar imagem
def convert_png_to_base64(png_file):
    with open(png_file, "rb") as f:
        image_bytes = f.read()
    base64_bytes = base64.b64encode(image_bytes)
    base_img = base64_bytes.decode("utf-8")
    return types.Part.from_bytes(
        mime_type="image/png",
        data=base64.b64decode(base_img))

# Função para processar notebook (ipynb)
def convert_notebook_text(notebook):
    # Verifica o encoding
    with open(notebook, 'rb') as f:
        resultado = chardet.detect(f.read())
        codificacao = resultado['encoding']

    # Abra o arquivo ipynb
    with open(notebook, 'r', encoding = codificacao) as f:
        notebook = nbformat.read(f, as_version=4)

    # Extraia o código e os comentários de cada célula
    codigo = []
    comentarios = []
    for cell in notebook.cells:
        if cell.cell_type == 'code' or cell.cell_type == 'markdown':
            codigo.append(cell.source)

    # Junte o código e os comentários em uma única string
    texto = '\n'.join(codigo + comentarios)
    return texto

# Função para processar código SAS
def converte_sas(arquivo):
    # Verifica o encoding
    with open(arquivo, 'rb') as f:
        resultado = chardet.detect(f.read())
        codificacao = resultado['encoding']

    with open(arquivo, 'r', encoding = codificacao) as f:
            # Leia o conteúdo do código SAS
        codigo_sas = f.read()
        return codigo_sas

# Função para processar PDF
def converte_pdf(document):
    with open(document, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    base_code = base64.b64encode(pdf_bytes).decode('utf-8')
    return types.Part.from_bytes(
        mime_type="application/pdf",
        data=base64.b64decode(base_code))

# Função para processar código python puro
def convert_python(nome_do_arquivo):
    # Verifica o encoding
    with open(nome_do_arquivo, 'rb') as f:
        resultado = chardet.detect(f.read())
        codificacao = resultado['encoding']

    with open(nome_do_arquivo, 'r', encoding = codificacao) as arquivo:
        codigo = arquivo.read()
    return codigo

# Função para exportar conversa
def exporta_conversa(historico_chat, id_chat):
    string_formatada = "<center>**Conversa com o ValidAI**</center>"
    # print(historico_chat)
    # Itera pelas duplas de diálogo na lista
    for i, dupla in enumerate(historico_chat):
        # Se for mensagem com anexo
        if type(dupla[0]) == tuple:
            if dupla[0][0] != None:
                string_formatada += "<br><br>**Usuário:**<br><br>" + dupla[0][0]
        else:
            if dupla[0] != None:
                string_formatada += "<br><br>**Usuário:**<br><br>" + dupla[0]
        if dupla[1] != None:
            string_formatada += """<br><br>**ValidAI:**<br>
""" + dupla[1]
    
    # Gera o arquivo PDF
    gera_pdf(string_formatada, "historico_conversas/conversa_" + id_chat)
    

# Função para converter DataFrame em texto
def convert_df(df_input):
    # Converta o DataFrame para CSV
    csv_buffer = io.StringIO()
    df_input.to_csv(csv_buffer, index=False, sep = ";")
    return csv_buffer.getvalue()

# Função para obter o separador utilizado no CSV
def get_sep(arq_input):
    with open(arq_input, 'r') as arquivo:
        dialeto = csv.Sniffer().sniff(arquivo.read(1024))
        separador = dialeto.delimiter
    return separador

# Função para converter CSV em Dataframe e depois em texto
def convert_csv(arquivo):
    df = pd.read_csv(arquivo, sep = "" + get_sep(arquivo) + "")
    return convert_df(df)

# Função para converter XLSX
def convert_excel(arquivo, nome_aba):
    df = pd.read_excel(arquivo, sheet_name = nome_aba)
    return convert_df(df)  

# Função para obter a relação de abas do arquivo XLSX
def get_abas(arquivo):
    workbook = openpyxl.load_workbook(arquivo)
    # Obtém a lista de nomes das abas
    return workbook.sheetnames

# Função para processar video
def converte_video(arquivo):
    with open(arquivo, "rb") as video:
        video_bytes = video.read()
    base_code = base64.b64encode(video_bytes).decode('utf-8')
    return types.Part.from_bytes(mime_type="video/mp4",data=base64.b64decode(base_code))

# Função para importar base do RAG
def importa_base(diretorio):
    try:
        df = pd.read_csv(diretorio + "/dicionario_base.csv")
    except:
        diretorio = "../" + diretorio
        df = pd.read_csv(diretorio + "/dicionario_base.csv")
    return df, diretorio

# Função para deletar arquivos
def deletar_arquivo(nome_arquivo):
    try:
        os.remove(nome_arquivo)
    except:
        a = 1

# Função para gerar markdown formatado
def salvar_markdown(texto, nome_arquivo):
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

# Função para gerar PDF
def gera_pdf(texto, nome_arquivo):

    # Gera um arquivo md temporário
    salvar_markdown(texto, nome_arquivo + ".md")

    # Lê o arquivo md temporário
    project = Markdown2docx(nome_arquivo)

    # Gera um html temporário
    project.write_html()

    # Lê o arquivo html temporário
    with open(nome_arquivo + '.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Insere a formatação das tabelas
    aux_1 = """
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {
          font-family: 'Arial', sans-serif;
          font-size: 11px;
        }
        
        code {
          font-size: 11px;
        }

        table {
          border-collapse: collapse;
          width: 100%;
        }

        table td, table th {
          border: 1px solid black;
          padding: 8px;
          font-size: 11px;
        }
      </style>
    </head>
    <body>
    """
    aux_2 = """    
    </body>
    </html>
    """

    html_content = aux_1 + html_content + aux_2
    
    # Gera o arquivo PDF a partir do html
    # Comando via HTML (Linux e GCP)
    # html = HTML(string=html_content)
    # html.write_pdf(nome_arquivo + ".pdf")

    # Comando via pisa (windows)
    pdf_path = nome_arquivo + ".pdf"

    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file, encoding='utf-8')

    # Deleta os arquivos temporários
    deletar_arquivo(nome_arquivo + ".md")
    deletar_arquivo(nome_arquivo + ".html")

# Função para processar
def trata_texto(mensagem):
    return types.Part.from_text(mensagem)

# Função para inserir conteúdo em uma lista do Gemini
def put_conteudo(conversa, origem, lista_mensagens):
    # origem deve ser "user" ou "model"
    conteudo_temp = types.Content(
              role=origem,
              parts=lista_mensagens
            )
    conversa = conversa.append(conteudo_temp)
    return None