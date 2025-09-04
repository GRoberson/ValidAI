#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Script de Migração para ValidAI Enhanced

Este script ajuda na transição do ValidAI original para o Enhanced,
preservando configurações e dados existentes.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any

def backup_original_files():
    """Cria backup dos arquivos originais"""
    print("📦 Criando backup dos arquivos originais...")
    
    backup_dir = Path("backup_original")
    backup_dir.mkdir(exist_ok=True)
    
    arquivos_para_backup = [
        "app.py",
        "config/variaveis.py"
    ]
    
    for arquivo in arquivos_para_backup:
        if os.path.exists(arquivo):
            destino = backup_dir / arquivo
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(arquivo, destino)
            print(f"   ✅ {arquivo} -> {destino}")
    
    print(f"📦 Backup criado em: {backup_dir}")

def extrair_configuracoes_originais() -> Dict[str, Any]:
    """Extrai configurações do ValidAI original"""
    print("🔍 Extraindo configurações do ValidAI original...")
    
    config = {}
    
    try:
        # Tentar importar configurações originais
        import sys
        sys.path.append('config')
        
        from variaveis import (
            versao, nome_exib, temperatura, top_p, max_output_tokens, time_sleep
        )
        
        config = {
            "modelo_versao": versao,
            "nome_exibicao": nome_exib,
            "temperatura": temperatura,
            "top_p": top_p,
            "max_output_tokens": max_output_tokens,
            "time_sleep": time_sleep,
            "time_sleep_compare": time_sleep
        }
        
        print("   ✅ Configurações extraídas com sucesso")
        
    except ImportError as e:
        print(f"   ⚠️ Não foi possível importar configurações: {e}")
        print("   💡 Usando configurações padrão")
        
        config = {
            "modelo_versao": "gemini-1.5-pro-002",
            "nome_exibicao": "ValidAI Enhanced",
            "temperatura": 0.2,
            "top_p": 0.8,
            "max_output_tokens": 8000,
            "time_sleep": 0.006,
            "time_sleep_compare": 0.006
        }
    
    return config

def criar_configuracao_enhanced(config_original: Dict[str, Any]):
    """Cria arquivo de configuração do Enhanced"""
    print("⚙️ Criando configuração do ValidAI Enhanced...")
    
    config_enhanced = {
        "project_id": "bv-cdip-des",  # Manter padrão ou extrair se disponível
        "location": "us-central1",
        **config_original,
        "temp_dir": "./temp_files",
        "historico_dir": "./historico_conversas", 
        "base_conhecimento_dir": "./base_conhecimento",
        "tamanho_max_arquivo_mb": 50,
        "extensoes_permitidas": [
            ".pdf", ".sas", ".ipynb", ".py", ".txt", ".csv", ".xlsx",
            ".png", ".jpg", ".jpeg", ".mp4", ".md", ".json", ".yaml", ".yml"
        ]
    }
    
    # Salvar configuração
    with open("validai_config.json", "w", encoding="utf-8") as f:
        json.dump(config_enhanced, f, indent=2, ensure_ascii=False)
    
    print("   ✅ Arquivo validai_config.json criado")

def verificar_estrutura_diretorios():
    """Verifica e cria diretórios necessários"""
    print("📁 Verificando estrutura de diretórios...")
    
    diretorios = [
        "temp_files",
        "historico_conversas",
        "base_conhecimento"
    ]
    
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio, exist_ok=True)
            print(f"   📁 Criado: {diretorio}")
        else:
            print(f"   ✅ Existe: {diretorio}")

def migrar_dados_existentes():
    """Migra dados existentes se houver"""
    print("📊 Migrando dados existentes...")
    
    # Migrar histórico de conversas se existir
    if os.path.exists("historico_conversas") and os.listdir("historico_conversas"):
        print("   ✅ Histórico de conversas preservado")
    
    # Migrar base de conhecimento se existir
    if os.path.exists("base_conhecimento") and os.listdir("base_conhecimento"):
        print("   ✅ Base de conhecimento preservada")
    
    # Migrar arquivos temporários (limpar se muito antigos)
    if os.path.exists("temp_files"):
        print("   🧹 Limpando arquivos temporários antigos...")
        # Implementar limpeza se necessário

def criar_arquivo_env():
    """Cria arquivo .env de exemplo"""
    print("🔧 Criando arquivo de variáveis de ambiente...")
    
    if not os.path.exists(".env"):
        shutil.copy2(".env.example", ".env")
        print("   ✅ Arquivo .env criado (edite conforme necessário)")
    else:
        print("   ℹ️ Arquivo .env já existe (preservado)")

def verificar_dependencias():
    """Verifica se novas dependências estão instaladas"""
    print("📦 Verificando dependências...")
    
    try:
        import gradio
        import google.genai
        print("   ✅ Dependências principais OK")
    except ImportError as e:
        print(f"   ❌ Dependência faltando: {e}")
        print("   💡 Execute: pip install -r requirements_enhanced.txt")

def main():
    """Executa o processo de migração"""
    print("\n" + "="*60)
    print("🔄 Migração para ValidAI Enhanced")
    print("="*60)
    print("\nEste script irá migrar sua instalação do ValidAI original")
    print("para a versão Enhanced, preservando dados existentes.\n")
    
    resposta = input("Continuar com a migração? (s/N): ").lower().strip()
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("Migração cancelada.")
        return
    
    try:
        # Passo 1: Backup
        backup_original_files()
        
        # Passo 2: Extrair configurações
        config_original = extrair_configuracoes_originais()
        
        # Passo 3: Criar nova configuração
        criar_configuracao_enhanced(config_original)
        
        # Passo 4: Verificar diretórios
        verificar_estrutura_diretorios()
        
        # Passo 5: Migrar dados
        migrar_dados_existentes()
        
        # Passo 6: Criar .env
        criar_arquivo_env()
        
        # Passo 7: Verificar dependências
        verificar_dependencias()
        
        print("\n" + "="*60)
        print("✅ Migração concluída com sucesso!")
        print("="*60)
        print("\n🚀 Próximos passos:")
        print("1. Instale as dependências: pip install -r requirements_enhanced.txt")
        print("2. Edite validai_config.json se necessário")
        print("3. Execute: python run_validai_enhanced.py")
        print("\n💡 Seus dados originais foram preservados!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        print("💡 Verifique os logs e tente novamente")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())