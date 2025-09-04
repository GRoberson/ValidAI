# Serviço de validação para o ValidAI
from src import DataManager

class ValidatorService:
    """
    Classe para gerenciar a validação de documentos e códigos.
    Integra com o PreValidadorModelos para fornecer análises especializadas.
    """
    
    def __init__(self, pre_validador):
        """Inicializa o serviço com uma instância do PreValidadorModelos"""
        self.pre_validador = pre_validador
    
    def validate_document(self, documento, chat):
        """Valida um documento usando o PreValidadorModelos"""
        input_message = [
            DataManager.converte_pdf(documento), 
            DataManager.trata_texto(self.pre_validador.gerar_prompt_documentacao())
        ]
        return chat.send_message("user", input_message)
    
    def validate_code(self, codigo, chat, multiplos_arquivos=False):
        """Valida código usando o PreValidadorModelos"""
        # Envia a instrução inicial
        chat.send_message("user", [DataManager.trata_texto('Farei perguntas sobre o seguinte código:' + codigo)])
        
        # Acrescenta uma suposta resposta
        chat.send_message("model", [DataManager.trata_texto("OK, irei respondê-las!")])
        
        # Envia o prompt de validação
        input_message = [
            DataManager.trata_texto(self.pre_validador.gerar_prompt_codigo(multiplos_arquivos=multiplos_arquivos))
        ]
        return chat.send_message("user", input_message)
    
    def validate_consistency(self, documento, codigo, chat):
        """Valida a consistência entre documento e código"""
        input_message = [
            DataManager.converte_pdf(documento), 
            DataManager.trata_texto(self.pre_validador.gerar_prompt_consistencia() + codigo)
        ]
        return chat.send_message("user", input_message)