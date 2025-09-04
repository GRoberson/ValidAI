from playwright.sync_api import sync_playwright
import subprocess
import time
import sys
import os
import socket
import requests
from urllib.error import URLError

def verificar_servidor_disponivel(url, max_tentativas=10, intervalo=2):
    """Verifica se o servidor está disponível, tentando várias vezes com intervalo"""
    print(f"Verificando disponibilidade do servidor em {url}...")
    
    for tentativa in range(max_tentativas):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"Servidor disponível após {tentativa + 1} tentativas!")
                return True
        except requests.RequestException:
            print(f"Tentativa {tentativa + 1}/{max_tentativas}: Servidor ainda não disponível...")
            time.sleep(intervalo)
    
    print(f"Servidor não disponível após {max_tentativas} tentativas.")
    return False

def executar_aplicacao():
    # Inicia a aplicação ValidAI Enhanced em um processo separado
    print("Iniciando a aplicação ValidAI Enhanced...")
    app_process = subprocess.Popen(
        ["python", "run_validai_enhanced.py"], 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Verifica se o processo iniciou corretamente
    if app_process.poll() is not None:
        print("Erro ao iniciar a aplicação!")
        stdout, stderr = app_process.communicate()
        print(f"Saída padrão: {stdout}")
        print(f"Erro: {stderr}")
        sys.exit(1)
    
    print("Processo da aplicação iniciado. Aguardando inicialização do servidor...")
    return app_process

def automatizar_com_playwright():
    # Inicia a aplicação
    app_process = executar_aplicacao()
    url = "http://localhost:7860"
    
    try:
        # Aguarda o servidor ficar disponível
        if not verificar_servidor_disponivel(url):
            print("Não foi possível conectar ao servidor. Encerrando...")
            app_process.terminate()
            sys.exit(1)
        
        # Inicia o Playwright
        with sync_playwright() as p:
            # Lança o navegador
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Navega para a aplicação
            print(f"Navegando para {url}...")
            page.goto(url)
            print("Navegador aberto na aplicação ValidAI Enhanced")
            
            # Mantém o navegador aberto até o usuário pressionar Enter
            input("Pressione Enter para fechar o navegador e encerrar a aplicação...")
            
            # Fecha o navegador
            browser.close()
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        # Encerra o processo da aplicação
        print("Encerrando a aplicação...")
        app_process.terminate()
        app_process.wait()

if __name__ == "__main__":
    automatizar_com_playwright()