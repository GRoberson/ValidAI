# ------ Variáveis globais do projeto ------
import datetime
from google.genai import types
from .config_loader import get_config_value

# Carregar configurações
data_formatada = datetime.datetime.now().strftime("%d/%b/%Y")

# Instrução para envio ao Gemini
instrucao = """Você é um especialista de validação de modelos chamado ValidAI, no qual responderá questões associadas à modelos tradicionais e avançados, isso inclui também a análise de códigos e documentos.""" + "Hoje é " + data_formatada + "."

# Config para o Google Search
google_search = [types.Tool(google_search=types.GoogleSearch())]

# Carregar configurações dinamicamente
versao = get_config_value("modelo_versao", "gemini-1.5-pro-002")
nome_exib = get_config_value("nome_exibicao", "Gemini 1.5 Pro 002")
temperatura = get_config_value("temperatura", 0.2)
top_p = get_config_value("top_p", 0.8)
max_output_tokens = get_config_value("max_output_tokens", 8000)
time_sleep = get_config_value("time_sleep", 0.006)
time_sleep_compare = get_config_value("time_sleep_compare", 0.006)

# Configurações de segurança do conteúdo
safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )]

# Tempo de espera para a exibição das letras do output (carregado dinamicamente)
# time_sleep e time_sleep_compare são carregados acima

# Parâmetros carregados dinamicamente:
# - temperatura: Controla aleatoriedade (0.0-2.0)
# - top_p: Controla probabilidade de palavras comuns (0.0-1.0) 
# - max_output_tokens: Máximo de tokens de saída
# 
# Para geração de texto criativo: temperature = 1.0, top_p = 0.9
# Para geração de texto informativo: temperature = 0.5, top_p = 0.95
# Para geração de código: temperature = 0.2, top_p = 0.99