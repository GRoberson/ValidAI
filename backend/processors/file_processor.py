# Processadores de arquivos para o ValidAI
from src import DataManager
from src import Prompts
from backend.security import validate_file_security
import logging

logger = logging.getLogger(__name__)

class FileProcessor:
    """
    Classe base para processamento de arquivos no ValidAI.
    Fornece métodos para processar diferentes tipos de arquivos.
    """
    
    @staticmethod
    def validate_file_security(arquivo):
        """Valida a segurança de um arquivo antes do processamento"""
        try:
            validation_result = validate_file_security(arquivo)
            if not validation_result['is_valid']:
                logger.warning(f"Arquivo rejeitado por segurança: {validation_result['error_message']}")
                return False, validation_result['error_message']
            
            logger.info(f"Arquivo validado: {validation_result['file_info']['name']} ({validation_result['file_info']['size_mb']:.2f}MB)")
            return True, "Arquivo válido"
            
        except Exception as e:
            logger.error(f"Erro na validação de segurança: {e}")
            return False, f"Erro na validação: {str(e)}"
    
    @staticmethod
    def process_code_file(arquivo, codigo="", qtd_arq=0):
        """Processa arquivos de código (SAS, IPYNB, PY)"""
        # Validar segurança do arquivo
        is_valid, error_msg = FileProcessor.validate_file_security(arquivo)
        if not is_valid:
            raise ValueError(f"Arquivo inválido: {error_msg}")
        
        if arquivo.lower().endswith(".sas"):
            codigo = codigo + "Codigo " + str(qtd_arq + 1) + ": " + DataManager.converte_sas(arquivo)
        elif arquivo.lower().endswith(".ipynb"):
            codigo = codigo + "Codigo " + str(qtd_arq + 1) + ": " + DataManager.convert_notebook_text(arquivo)
        elif arquivo.lower().endswith(".py"):
            codigo = codigo + "Codigo " + str(qtd_arq + 1) + ": " + DataManager.convert_python(arquivo)
        return codigo, qtd_arq + 1
    
    @staticmethod
    def process_image_file(arquivo, message_text):
        """Processa arquivos de imagem (PNG, JPG, JPEG)"""
        if message_text == "":
            message_text = "Descreva o conteúdo da imagem:"
        input_message = [DataManager.convert_png_to_base64(arquivo), DataManager.trata_texto(message_text)]
        return input_message, message_text
    
    @staticmethod
    def process_text_file(arquivo, message_text):
        """Processa arquivos de texto (TXT)"""
        input_message = [DataManager.trata_texto(message_text + ":" + DataManager.convert_python(arquivo))]
        return input_message
    
    @staticmethod
    def process_pdf_file(arquivo, message_text, prompt=None):
        """Processa arquivos PDF"""
        if message_text == "" and prompt:
            message_text = "Avalie o documento fornecido"
            input_message = [DataManager.converte_pdf(arquivo), DataManager.trata_texto(prompt)]
        else:
            input_message = [DataManager.converte_pdf(arquivo), DataManager.trata_texto(message_text)]
        return input_message, message_text
    
    @staticmethod
    def process_excel_file(arquivo):
        """Processa arquivos Excel e retorna lista de abas"""
        return DataManager.get_abas(arquivo)
    
    @staticmethod
    def process_excel_sheet(arquivo, sheet_name, message_text=""):
        """Processa uma aba específica de arquivo Excel"""
        if message_text == "":
            message_text = "Armazene o conteúdo da seguinte tabela:"
        input_message = [DataManager.trata_texto(message_text + DataManager.convert_excel(arquivo, sheet_name))]
        return input_message, message_text
    
    @staticmethod
    def process_csv_file(arquivo, message_text=""):
        """Processa arquivos CSV"""
        if message_text == "":
            message_text = "Armazene o conteúdo da seguinte tabela:"
        input_message = [DataManager.trata_texto(message_text + DataManager.convert_csv(arquivo))]
        return input_message, message_text
    
    @staticmethod
    def process_video_file(arquivo, message_text):
        """Processa arquivos de vídeo (MP4)"""
        input_message = [DataManager.converte_video(arquivo), DataManager.trata_texto(message_text)]
        return input_message