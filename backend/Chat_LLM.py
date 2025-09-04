from src.Messenger import chat_2_0, get_file
from src import DataManager
from src import Prompts
import pytz
import datetime
import time
import sys
import os

# Adicionar o diretório raiz ao path para importar o PreValidadorModelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pre_validator_system import PreValidadorModelos

# Importar os novos módulos
from backend.processors.file_processor import FileProcessor
from backend.processors.validator_service import ValidatorService

from config.variaveis import time_sleep, time_sleep_compare
from config.config_loader import get_config_value

import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Configurações dinâmicas
MAX_FILES_TO_PROCESS = get_config_value("max_arquivos_processo", 10)

# Inicializar o PreValidadorModelos e o ValidatorService
pre_validador = PreValidadorModelos()
validator_service = ValidatorService(pre_validador)

# ------ Função para o chat multimodal ------
def chat_multimodal(message, history, lista_abas, block_chat, arquivo_excel, chat):
    
    marc_export = 0
    codigo = ""
    qtd_arq = 0
    marc_resp = 0
    
    # Se não tem histórico, inicia um novo chat
    if len(history)== 0:
        chat = chat_2_0()
        lista_abas = []
        block_chat = 0
        arquivo_excel = ""
    
    # Se contém um arquivo
    if message["files"] != []:
        qtd_arq = 1
        arquivo = message['files'][0]
        
        # Verifica se é código, se sim, converte para string
        if arquivo.lower().endswith(".sas") or arquivo.lower().endswith(".ipynb") or arquivo.lower().endswith(".py"):
            max_files = min(len(message['files']), MAX_FILES_TO_PROCESS)  # Usar constante configurável
            for i in range(max_files):
                try:
                    arquivo = message['files'][i]
                    codigo, qtd_arq = FileProcessor.process_code_file(arquivo, codigo, qtd_arq - 1)
                except (IndexError, FileNotFoundError, PermissionError) as e:
                    logger.warning(f"Erro ao processar arquivo {i}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Erro inesperado ao processar arquivo {i}: {e}")
                    break
                
        # Se for imagem, transcreve o conteúdo
        elif arquivo.lower().endswith(".png") or arquivo.lower().endswith(".jpg") or arquivo.lower().endswith(".jpeg"):
            input_message, message["text"] = FileProcessor.process_image_file(arquivo, message["text"])
            responses = chat.send_message("user", input_message)
            marc_resp = 1
            
        # Se for txt
        elif arquivo.lower().endswith(".txt"):
            input_message = FileProcessor.process_text_file(arquivo, message["text"])
            responses = chat.send_message("user", input_message)
            marc_resp = 1
        
        # Se for um documento pdf
        elif arquivo.lower().endswith(".pdf"):
            input_message, message["text"] = FileProcessor.process_pdf_file(arquivo, message["text"], Prompts.documento())
            responses = chat.send_message("user", input_message)
            marc_resp = 1
        
        # Se for um arquivo CSV
        elif arquivo.lower().endswith(".csv"):
            input_message, message["text"] = FileProcessor.process_csv_file(arquivo, message["text"])
            responses = chat.send_message("user", input_message)
            marc_resp = 1
            
        # Se for um arquivo XLSX
        elif arquivo.lower().endswith(".xlsx"):
            arquivo_excel = arquivo
            lista_abas = FileProcessor.process_excel_file(arquivo)
             
            # Se possui mais de uma aba
            if len(lista_abas) > 1:
                # Se ainda não especificou qual a aba quer importar
                block_chat = 1
                output_mensagem = "Qual aba deseja importar?\n"
                for sheet_name in lista_abas:
                    output_mensagem = output_mensagem + sheet_name + "\n"
                yield output_mensagem, lista_abas, block_chat, arquivo_excel, chat
                        
            #Se possui uma aba
            else:
                input_message, message["text"] = FileProcessor.process_excel_sheet(arquivo_excel, lista_abas[0], message["text"])
                responses = chat.send_message("user", input_message)
                marc_resp = 1
                
        # Se for arquivo mp4
        elif arquivo.lower().endswith(".mp4"):
            input_message = FileProcessor.process_video_file(arquivo, message["text"])
            responses = chat.send_message("user", input_message)
            marc_resp = 1
        else:
            yield "Arquivo não suportado", lista_abas, block_chat, arquivo_excel, chat
        

    # se contém um código
    if len(codigo) > 0:
        input_message = [DataManager.trata_texto('Farei perguntas sobre o seguinte código:' + codigo)]
        
        # Acrescenta ao conteúdo sem processar para a LLM
        chat.send_message("user", input_message)
      
        # Acrescenta uma suposta mensagem da LLM
        chat.send_message("model", [DataManager.trata_texto("OK, irei respondê-las!")])
        
        # Se contém algum texto junto ao arquivo, considera a mensagem do usuário
        if message["text"] != "":
            input_message = [DataManager.trata_texto(message["text"])]
            responses = chat.send_message("user", input_message)
            
        else:
            message["text"] = "Avalie o código fornecido"
            input_message = [DataManager.trata_texto(Prompts.codigo(qtd_arq))]
            responses = chat.send_message("user", input_message)
        marc_resp = 1
            
                
    # Se for somente texto:        
    if message["files"] == []:
        # Se for para exportar conversa
        if message.get("text") and "exportar conversa" in message["text"].lower():
            marc_export = 1
            timezone = pytz.timezone('America/Sao_Paulo')
            now = datetime.datetime.now(timezone)
            date_time_str = now.strftime("%Y%m%d_%H_%M_%S")
            DataManager.exporta_conversa(history, date_time_str)
            yield "Conversa exportada com sucesso! Disponível no arquivo: conversa_" + date_time_str + ".pdf", lista_abas, block_chat, arquivo_excel, chat
        
        # Se for para importar Excel
        elif block_chat == 1:
            if message["text"] in lista_abas:
                block_chat = 0
                input_message, _ = FileProcessor.process_excel_sheet(arquivo_excel, message["text"], 
                                                                   "Armazene o conteúdo da tabela, pois irei realizar algumas consultas à respeito:")
                responses = chat.send_message("user", input_message)
                marc_resp = 1
                
            else:
                output_mensagem = "Aba não encontrada, por favor selecione uma das listadas abaixo:\n"
                for sheet_name in lista_abas:
                    output_mensagem = output_mensagem + sheet_name + "\n"
                yield output_mensagem, lista_abas, block_chat, arquivo_excel, chat
        # Se for outro texto
        else:
            input_message = [DataManager.trata_texto(message["text"])]                                         
            responses = chat.send_message("user", input_message)
            marc_resp = 1
                                                            
    if marc_resp == 1:
        # Exibe a mensagem ao usuário
        output_mensagem = ""
        responses = responses if 'responses' in locals() else None
        if responses:  # Verificar se responses não é None
            for chunk in responses:
                try:
                    msg_chunk = chunk.text
                    if msg_chunk:  # Verificar se msg_chunk não é None
                        for i in range(len(msg_chunk)):
                            time.sleep(time_sleep)
                            yield output_mensagem + msg_chunk[: i+1], lista_abas, block_chat, arquivo_excel, chat
                        output_mensagem = output_mensagem + msg_chunk
                except Exception as e:
                    logger.error(f"Erro ao processar chunk da resposta: {e}")
                    continue
        yield output_mensagem, lista_abas, block_chat, arquivo_excel, chat

        # Acrescenta a resposta da LLM ao contexto
        chat.send_message("model", [DataManager.trata_texto(output_mensagem)])


# ------ Função para o pré-validador ------
def chat_compare(documentos, codigos, historico_compare):
    codigo = ""
    qtd_arq = 0
    qtd_doc = 0
    marc_resp = 0
    
    # Reseta o chat
    chat_comp = chat_2_0()
    historico_compare = ""
    
    # Processar arquivos de código
    if codigos != None:
        qtd_arq = 1
        arquivo = codigos[0]

        # Verifica se é código, se sim, converte para string
        if arquivo.lower().endswith(".sas") or arquivo.lower().endswith(".ipynb") or arquivo.lower().endswith(".py"):
            max_files = min(len(codigos), MAX_FILES_TO_PROCESS)  # Usar constante configurável
            for i in range(max_files):
                try:
                    arquivo = codigos[i]
                    codigo, qtd_arq = FileProcessor.process_code_file(arquivo, codigo, qtd_arq - 1)
                except (IndexError, FileNotFoundError, PermissionError) as e:
                    logger.warning(f"Erro ao processar código {i}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Erro inesperado ao processar código {i}: {e}")
                    break

    # Verificar se há documentos
    if documentos != None:
        qtd_doc = 1
            
    # Determinar o tipo de validação com base nos arquivos disponíveis
    if qtd_arq == 0:
        # Não possui arquivos
        if qtd_doc == 0:
            return "Sem arquivos", historico_compare
        # Só possui documento
        else:
            logger.info("Validando apenas documento")
            responses = validator_service.validate_document(documentos[0], chat_comp)
            marc_resp = 1
            
    else:
        # Só possui código
        if qtd_doc == 0:
            logger.info("Validando apenas código")
            multiplos_arquivos = qtd_arq > 2  # Se tiver mais de 1 código (o primeiro é qtd_arq=1)
            responses = validator_service.validate_code(codigo, chat_comp, multiplos_arquivos)
            marc_resp = 1
            
        # Possui Código e Documentos
        else:
            logger.info("Validando consistência entre código e documento")
            responses = validator_service.validate_consistency(documentos[0], codigo, chat_comp)
            marc_resp = 1
 
    if marc_resp == 1:
        output_mensagem = ""
        responses = responses if 'responses' in locals() else None
        if responses:  # Verificar se responses não é None
            for chunk in responses:
                try:
                    msg_chunk = chunk.text
                    if msg_chunk:  # Verificar se msg_chunk não é None
                        for i in range(len(msg_chunk)):
                            time.sleep(time_sleep_compare)
                            yield output_mensagem + msg_chunk[: i+1], historico_compare
                        output_mensagem = output_mensagem + msg_chunk
                except Exception as e:
                    logger.error(f"Erro ao processar chunk da comparação: {e}")
                    continue
        historico_compare = output_mensagem
        yield output_mensagem, historico_compare


# ------ Função para o RAG ------
def fn_chat_rag_manual(message, history, selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag):
        
    # Se não tem histórico, inicia um novo chat
    if len(history)== 0:
        lista_arquivos = []
        chat_rag = chat_2_0()
        
        if selected_rag == None:
            yield "Selecione uma base de conhecimento", selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag
            return
        
        # Selecionar a base de conhecimento apropriada
        if selected_rag == "Conteúdos de 'INs'":
            if diretorio_rag != selected_rag_antes:
                selected_rag_antes = selected_rag
                diretorio_rag = 'base_conhecimento'
                df_resumo, diretorio_rag = DataManager.importa_base(diretorio_rag)
        elif selected_rag == "Validações de Riscos de Mercado":
            if selected_rag != selected_rag_antes:
                selected_rag_antes = selected_rag
                diretorio_rag = 'base_conhecimento/Mercado'
                df_resumo, diretorio_rag = DataManager.importa_base(diretorio_rag)
        elif selected_rag == "Validações de Riscos de Crédito":
            if selected_rag != selected_rag_antes:
                selected_rag_antes = selected_rag
                diretorio_rag = 'base_conhecimento/Credito'
                df_resumo, diretorio_rag = DataManager.importa_base(diretorio_rag)
        elif selected_rag == "Google Search":
            selected_rag_antes = selected_rag
    
    if selected_rag != selected_rag_antes:
        yield "Base de conhecimento alterada, por favor reinicie a conversa", selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag
        return
    
    # Se for para exportar conversa
    if "exportar conversa" in message.lower():
        timezone = pytz.timezone('America/Sao_Paulo')
        now = datetime.datetime.now(timezone)
        date_time_str = now.strftime("%Y%m%d_%H_%M_%S")
        DataManager.exporta_conversa(history, date_time_str)
        yield "Conversa exportada com sucesso! Disponível no arquivo: conversa_" + date_time_str + ".pdf", selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag
        
    # Se for outro texto
    else:
        if selected_rag != "Google Search":
            nome_arquivo = get_file(message, df_resumo)
            if nome_arquivo.lower().startswith("desculpe"):
                input_message = [DataManager.trata_texto(message)]
                responses = chat_rag.send_message("user", input_message)
                
                output_mensagem = "**Utilizando o contexto da conversa e o conhecimento pré-treinado do LLM**\n\n"
            else:
                output_mensagem = "**Resposta extraída do documento " + nome_arquivo + "**\n\n"
                # Se já importou o arquivo no contexto, não importa novamente
                if nome_arquivo in lista_arquivos:
                    input_message = [DataManager.trata_texto(message)]
                    responses = chat_rag.send_message("user", input_message)
                    
                else:
                    input_message = [DataManager.converte_pdf(diretorio_rag + "/" + nome_arquivo), DataManager.trata_texto(message)]
                    responses = chat_rag.send_message("user", input_message)
                    
                    lista_arquivos.append(nome_arquivo)
        else:
            input_message = [DataManager.trata_texto(message)]
            responses = chat_rag.send_message("user", input_message, "Google Search")
            
            output_mensagem = "**ValidAI com complemento do Google Search**\n\n"
    
    # Inicializar variáveis para evitar erros
    output_mensagem = output_mensagem if 'output_mensagem' in locals() else ""
    responses = responses if 'responses' in locals() else None
    
    if responses:  # Verificar se responses não é None
        for chunk in responses:
            try:
                msg_chunk = chunk.text
                if msg_chunk:  # Verificar se msg_chunk não é None
                    for i in range(len(msg_chunk)):
                        time.sleep(time_sleep)
                        yield output_mensagem + msg_chunk[: i+1], selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag
                    output_mensagem = output_mensagem + msg_chunk
            except Exception as e:
                logger.error(f"Erro ao processar chunk do RAG: {e}")
                continue
    yield output_mensagem, selected_rag, selected_rag_antes, diretorio_rag, lista_arquivos, df_resumo, chat_rag
    
    chat_rag.send_message("model", [DataManager.trata_texto(output_mensagem)])