#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Script de Inicialização do ValidAI Enhanced

Este script facilita a execução do ValidAI Enhanced com diferentes configurações
e modos de operação. Use os argumentos da linha de comando para personalizar!
"""

import argparse
import sys
import os
from pathlib import Path

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias_obrigatorias = [
        'gradio', 'google-genai', 'google-cloud-storage', 
        'vertexai', 'pandas', 'openpyxl'
    ]
    
    dependencias_faltando = []
    
    for dep in dependencias_obrigatorias:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            dependencias_faltando.append(dep)
    
    if dependencias_faltando:
        print("❌ Dependências faltando:")
        for dep in dependencias_faltando:
            print(f"   • {dep}")
        print("\n💡 Instale com: pip install " + " ".join(dependencias_faltando))
        return False
    
    return True

def verificar_estrutura_projeto():
    """Verifica se a estrutura do projeto está correta"""
    diretorios_necessarios = [
        'config', 'backend', 'src', 'frontend', 'base_conhecimento'
    ]
    
    arquivos_necessarios = [
        'app.py', 'pre_validator_system.py',
        'config/variaveis.py', 'backend/Chat_LLM.py'
    ]
    
    problemas = []
    
    # Verificar diretórios
    for diretorio in diretorios_necessarios:
        if not os.path.exists(diretorio):
            problemas.append(f"Diretório faltando: {diretorio}")
    
    # Verificar arquivos
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            problemas.append(f"Arquivo faltando: {arquivo}")
    
    if problemas:
        print("❌ Problemas na estrutura do projeto:")
        for problema in problemas:
            print(f"   • {problema}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="🚀 ValidAI Enhanced - Sistema Inteligente de Validação",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_validai_enhanced.py                    # Execução padrão
  python run_validai_enhanced.py --debug           # Com debug ativado
  python run_validai_enhanced.py --share           # Com link público
  python run_validai_enhanced.py --port 7860       # Porta específica
  python run_validai_enhanced.py --config custom.json  # Config personalizada
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='validai_config.json',
        help='Arquivo de configuração JSON (padrão: validai_config.json)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Ativa modo debug com logs detalhados'
    )
    
    parser.add_argument(
        '--share', '-s',
        action='store_true',
        help='Cria link público (CUIDADO: dados sensíveis!)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        help='Porta específica para execução'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Apenas verifica dependências e estrutura, não executa'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🚀 ValidAI Enhanced - Inicializador")
    print("="*70)
    
    # Verificações preliminares
    print("\n🔍 Verificando sistema...")
    
    if not verificar_dependencias():
        return 1
    
    if not verificar_estrutura_projeto():
        return 1
    
    print("✅ Sistema verificado com sucesso!")
    
    if args.check_only:
        print("\n✅ Verificação concluída. Sistema pronto para execução!")
        return 0
    
    # Verificar arquivo de configuração
    if not os.path.exists(args.config):
        print(f"\n⚠️ Arquivo de configuração não encontrado: {args.config}")
        print("💡 Usando configurações padrão...")
        args.config = None
    
    # Avisos de segurança
    if args.share:
        print("\n🚨 AVISO DE SEGURANÇA:")
        print("   Você está criando um link público!")
        print("   Dados sensíveis podem ser expostos!")
        resposta = input("   Continuar? (s/N): ").lower().strip()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("   Operação cancelada.")
            return 0
    
    # Importar e executar ValidAI Enhanced
    try:
        print(f"\n🚀 Iniciando ValidAI Enhanced...")
        if args.config:
            print(f"📋 Configuração: {args.config}")
        
        from validai_enhanced import ValidAIEnhanced
        
        # Inicializar aplicação
        app = ValidAIEnhanced(arquivo_config=args.config)
        
        # Executar com parâmetros
        app.executar(
            share=args.share,
            debug=args.debug,
            porta=args.port
        )
        
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
        return 0
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("💡 Verifique se todos os módulos do ValidAI original estão disponíveis")
        return 1
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())