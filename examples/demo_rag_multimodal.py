#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 Demonstração do Sistema RAG Multimodal

Script para demonstrar as capacidades multimodais do ValidAI Enhanced,
incluindo processamento de imagens, vídeos e áudios.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imports do sistema RAG multimodal
from validai_rag_multimodal import (
    ValidAIRAGMultimodal, 
    ProcessadorMultimodal,
    criar_configuracao_rag_multimodal
)


def demonstrar_processamento_multimodal():
    """
    Demonstra o processamento de diferentes tipos de mídia
    """
    print("\n" + "="*70)
    print("🎭 Demonstração do Sistema RAG Multimodal")
    print("="*70)
    
    try:
        # 1. Configuração
        print("\n🔧 1. Configurando sistema multimodal...")
        config = criar_configuracao_rag_multimodal()
        
        # Ajustar configurações
        config.update({
            'project_id': os.getenv('VALIDAI_PROJECT_ID', 'bv-cdip-des'),
            'bucket_name': os.getenv('VALIDAI_RAG_BUCKET', 'validai-rag-multimodal')
        })
        
        print(f"   • Projeto: {config['project_id']}")
        print(f"   • Bucket: {config['bucket_name']}")
        print(f"   • Modelo Vision: {config['modelo_vision']}")
        
        # 2. Inicializar sistema
        print("\n🎭 2. Inicializando sistema RAG multimodal...")
        rag_multimodal = ValidAIRAGMultimodal(config)
        
        # 3. Inicializar processador
        print("\n🎨 3. Inicializando processador de mídia...")
        processador = ProcessadorMultimodal(config)
        
        # 4. Listar corpus multimodais
        print("\n📋 4. Corpus multimodais disponíveis:")
        for corpus_id, config_corpus in rag_multimodal.corpus_configs.items():
            status = "✅" if config_corpus.suporte_multimodal else "📄"
            print(f"   {status} {config_corpus.nome}")
            print(f"      Tipos texto: {config_corpus.tipos_arquivo}")
            print(f"      Tipos mídia: {config_corpus.tipos_multimodal[:5]}...")
        
        # 5. Demonstrar detecção de tipos
        print("\n🔍 5. Demonstrando detecção de tipos de mídia:")
        
        arquivos_exemplo = [
            "exemplo.jpg", "apresentacao.mp4", "audio.mp3", 
            "documento.pdf", "planilha.xlsx", "video.avi"
        ]
        
        for arquivo in arquivos_exemplo:
            tipo = processador.detectar_tipo_midia(arquivo)
            print(f"   📁 {arquivo} → {tipo}")
        
        # 6. Demonstrar capacidades por tipo
        print("\n🎯 6. Capacidades por tipo de mídia:")
        
        print("\n   📸 IMAGENS:")
        print("      • Extração de texto (OCR)")
        print("      • Análise de gráficos e dashboards")
        print("      • Interpretação de diagramas")
        print("      • Descrição detalhada do conteúdo")
        
        print("\n   🎥 VÍDEOS:")
        print("      • Análise de apresentações")
        print("      • Extração de slides e texto")
        print("      • Transcrição de narração")
        print("      • Identificação de momentos importantes")
        
        print("\n   🎵 ÁUDIOS:")
        print("      • Transcrição de fala")
        print("      • Análise de treinamentos")
        print("      • Extração de insights técnicos")
        print("      • Identificação de conceitos")
        
        # 7. Simular processamento de corpus
        corpus_exemplo = "apresentacoes_validacao"
        print(f"\n📚 7. Simulando processamento do corpus: {corpus_exemplo}")
        
        if corpus_exemplo in rag_multimodal.corpus_configs:
            config_corpus = rag_multimodal.corpus_configs[corpus_exemplo]
            
            print(f"   📁 Diretório: {config_corpus.diretorio_local}")
            print(f"   🎭 Suporte multimodal: {config_corpus.suporte_multimodal}")
            
            # Verificar se diretório existe
            if os.path.exists(config_corpus.diretorio_local):
                print("   ✅ Diretório encontrado")
                
                # Simular processamento
                try:
                    estatisticas = rag_multimodal.processar_arquivos_multimodais(corpus_exemplo)
                    
                    print(f"\n   📊 Estatísticas do processamento:")
                    print(f"      • Total de arquivos: {estatisticas['total_arquivos']}")
                    print(f"      • Arquivos de texto: {estatisticas['arquivos_texto']}")
                    print(f"      • Imagens: {estatisticas['arquivos_imagem']}")
                    print(f"      • Vídeos: {estatisticas['arquivos_video']}")
                    print(f"      • Áudios: {estatisticas['arquivos_audio']}")
                    print(f"      • Processados: {estatisticas['arquivos_processados']}")
                    print(f"      • Erros: {estatisticas['erros']}")
                    
                    # Mostrar alguns textos extraídos
                    if estatisticas['textos_extraidos']:
                        print(f"\n   📝 Exemplos de textos extraídos:")
                        for i, item in enumerate(estatisticas['textos_extraidos'][:2]):
                            print(f"      {i+1}. {Path(item['arquivo']).name} ({item['tipo']})")
                            texto_resumido = item['texto'][:100] + "..." if len(item['texto']) > 100 else item['texto']
                            print(f"         {texto_resumido}")
                    
                except Exception as e:
                    print(f"   ⚠️ Simulação de processamento: {e}")
            else:
                print(f"   ⚠️ Diretório não existe: {config_corpus.diretorio_local}")
                print("   💡 Crie o diretório e adicione arquivos multimodais para testar")
        
        # 8. Demonstrar consultas multimodais
        print(f"\n💬 8. Exemplos de consultas multimodais:")
        
        consultas_exemplo = [
            "Mostre-me gráficos de performance de modelos",
            "Quais são os principais pontos da apresentação sobre validação?",
            "Há algum vídeo explicando o processo de monitoramento?",
            "Que informações visuais temos sobre riscos de mercado?",
            "Transcreva o áudio da reunião sobre metodologias"
        ]
        
        for i, consulta in enumerate(consultas_exemplo, 1):
            print(f"   {i}. \"{consulta}\"")
            print(f"      → Busca em textos, imagens, vídeos e áudios")
        
        # 9. Vantagens do sistema multimodal
        print(f"\n🌟 9. Vantagens do sistema multimodal:")
        print("   ✅ Análise completa de documentos com elementos visuais")
        print("   ✅ Extração de informações de apresentações em vídeo")
        print("   ✅ Transcrição e análise de treinamentos em áudio")
        print("   ✅ Interpretação de gráficos e dashboards")
        print("   ✅ Consultas contextuais sobre qualquer tipo de mídia")
        print("   ✅ Base de conhecimento verdadeiramente multimodal")
        
        # 10. Próximos passos
        print(f"\n🚀 10. Como usar o sistema multimodal:")
        print("   1. Execute: python validai_enhanced_multimodal.py")
        print("   2. Configure os corpus multimodais")
        print("   3. Adicione arquivos de mídia aos diretórios")
        print("   4. Processe os corpus usando a interface")
        print("   5. Faça consultas multimodais no chat")
        
        print("\n✅ Demonstração concluída!")
        print("\n💡 O sistema RAG multimodal oferece capacidades únicas:")
        print("   • Análise de imagens com Gemini Vision")
        print("   • Processamento de vídeos e áudios")
        print("   • Extração inteligente de conteúdo")
        print("   • Consultas contextuais avançadas")
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        print("\n🔧 Verifique:")
        print("   • Configurações do Google Cloud")
        print("   • Permissões do Vertex AI e Gemini")
        print("   • Conectividade com a internet")


def criar_estrutura_exemplo():
    """Cria estrutura de exemplo para testar o sistema multimodal"""
    print("\n📁 Criando estrutura de exemplo...")
    
    diretorios_exemplo = [
        "base_conhecimento/ins_multimodal",
        "base_conhecimento/apresentacoes", 
        "base_conhecimento/graficos",
        "base_conhecimento/casos_visuais",
        "base_conhecimento/treinamentos_audio",
        "base_conhecimento/documentos_visuais"
    ]
    
    for diretorio in diretorios_exemplo:
        Path(diretorio).mkdir(parents=True, exist_ok=True)
        
        # Criar README em cada diretório
        readme_path = Path(diretorio) / "README.md"
        readme_content = f"""# {Path(diretorio).name.replace('_', ' ').title()}

Este diretório é para arquivos multimodais do ValidAI Enhanced.

## Tipos de arquivo suportados:

### Documentos:
- PDF, DOCX, PPTX, TXT, MD

### Imagens:
- JPG, PNG, GIF, BMP, WebP, TIFF

### Vídeos:
- MP4, AVI, MOV, WMV, WebM, MKV

### Áudios:
- MP3, WAV, FLAC, AAC, OGG, M4A

## Como usar:
1. Coloque seus arquivos neste diretório
2. Execute o setup do corpus RAG multimodal
3. Use no ValidAI Enhanced Multimodal

Criado automaticamente pelo sistema de demonstração.
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"   ✅ {diretorio}")
    
    print("✅ Estrutura de exemplo criada!")


def verificar_prerequisitos_multimodal():
    """Verifica pré-requisitos para o sistema multimodal"""
    print("🔍 Verificando pré-requisitos multimodais...")
    
    # Verificar imports
    try:
        import google.genai
        import vertexai
        from google.cloud import storage
        print("   ✅ Bibliotecas Google Cloud OK")
    except ImportError as e:
        print(f"   ❌ Biblioteca faltando: {e}")
        return False
    
    # Verificar arquivos do sistema
    arquivos_necessarios = [
        'validai_rag_multimodal.py',
        'rag_multimodal_config.json'
    ]
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ Arquivo faltando: {arquivo}")
            return False
    
    # Verificar configuração
    project_id = os.getenv('VALIDAI_PROJECT_ID', 'bv-cdip-des')
    print(f"   ℹ️ Projeto: {project_id}")
    
    return True


def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🎭 Demonstração RAG Multimodal - ValidAI Enhanced")
    print("="*70)
    
    # Verificar pré-requisitos
    if not verificar_prerequisitos_multimodal():
        print("\n❌ Pré-requisitos não atendidos")
        return 1
    
    # Menu de opções
    print("\n📋 Opções disponíveis:")
    print("1. 🎭 Demonstração completa do sistema multimodal")
    print("2. 📁 Criar estrutura de exemplo")
    print("3. 🔍 Apenas verificar pré-requisitos")
    
    try:
        opcao = input("\nEscolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            # Confirmar execução
            print("\n⚠️ Esta demonstração irá:")
            print("   • Conectar com Google Cloud")
            print("   • Inicializar sistema multimodal")
            print("   • Simular processamento de mídia")
            
            resposta = input("\nContinuar? (s/N): ").lower().strip()
            if resposta in ['s', 'sim', 'y', 'yes']:
                demonstrar_processamento_multimodal()
            else:
                print("Demonstração cancelada.")
        
        elif opcao == "2":
            criar_estrutura_exemplo()
        
        elif opcao == "3":
            print("✅ Pré-requisitos verificados!")
        
        else:
            print("Opção inválida.")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração interrompida")
        return 0
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())