from google import genai
from google.genai import types
from src import DataManager
from config.variaveis import (
    versao,
    temperatura,
    top_p,
    max_output_tokens,
    safety_settings,
    google_search,
    instrucao 
)

client = genai.Client(
      vertexai=True,
      project="bv-cdip-des",
      location="us-central1")

# Gera as configurações com parâmetros
# Google Search
config_search = types.GenerateContentConfig(
  temperature = temperatura,
  top_p = top_p,
  max_output_tokens = max_output_tokens,
  response_modalities = ["TEXT"],
  safety_settings = safety_settings,
  tools = google_search,
  system_instruction=[DataManager.trata_texto(instrucao)]
)

# Não possui o Google Search
config = types.GenerateContentConfig(
  temperature = temperatura,
  top_p = top_p,
  max_output_tokens = max_output_tokens,
  response_modalities = ["TEXT"],
  safety_settings = safety_settings,
  system_instruction=[DataManager.trata_texto(instrucao)]
)

class chat_2_0:
    
    def __init__(self):
        self.contexto = []

    def send_message(self, origem, message, config_chat=""):
        # origem pode ser user ou model
        # message deve ser uma lista, já tratada para a LLM
        conteudo_temp = types.Content(
              role=origem,
              parts=message
            )
        self.contexto.append(conteudo_temp)
        
        if config_chat=="Google Search":
            config_chat = config_search
        else: 
            config_chat = config
        
        # Se for mensagem do usuário, processa com a LLM
        if origem == "user":
            response = client.models.generate_content_stream(
                  model = versao,
                  contents = self.contexto,
                  config = config_chat)

            return response
        else:
            return None
        

# Código para o RAG
corpus_mercado = "projects/1055585204357/locations/us-central1/ragCorpora/7454583283205013504"

def atribui_rag(corpus):
    var_temp = [types.Tool(
                retrieval=types.Retrieval(
                    vertex_rag_store=types.VertexRagStore(
                        rag_resources=[
                            types.VertexRagStoreRagResource(
                                rag_corpus=corpus
                            )
                        ],
                        similarity_top_k=3,
                        vector_distance_threshold=0.5,
                    ),
                )
            )]
    return var_temp

rag_mercado = atribui_rag(corpus_mercado)

def get_file(mensagem, df_resumo):
    # Método de interação Single Turn
    prompt = """Considerando a seguinte pergunta e os dados disponíveis, 
    responda somente o nome do arquivo que seja o mais provável de conter o conteúdo perguntado, 
    caso entenda que a pergunta não esteja muito relacionado aos contextos fornecidos, retorne "Desculpe, não identifiquei o contexto da sua pergunta": Pergunta - """
    
    contexto_temp = []
    input_message = [DataManager.trata_texto(prompt + mensagem + " Tabela de dados - " + DataManager.convert_df(df_resumo))]
            
    # Acrescenta a mensagem
    DataManager.put_conteudo(contexto_temp, "user", input_message)

    return client.models.generate_content(
                    model = versao,
                    contents = contexto_temp,
                    config = config,
                ).text.strip().rstrip(';')

# Config para o RAG das validações de Risco de Mercado
config_mercado = types.GenerateContentConfig(
  temperature = temperatura,
  top_p = top_p,
  max_output_tokens = max_output_tokens,
  response_modalities = ["TEXT"],
  safety_settings = safety_settings,
  tools = rag_mercado,
  system_instruction=[DataManager.trata_texto(instrucao)]
)