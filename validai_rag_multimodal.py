#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 ValidAI RAG Multimodal - Sistema RAG com Suporte Multimodal

Sistema RAG avançado que suporta documentos, imagens, vídeos e outros
tipos de mídia usando Vertex AI multimodal e Gemini Vision.
"""

import os
import uuid
import json
import base64
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import mimetypes

# Google Cloud imports
from google import genai
from google.cloud import storage
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore, Part
import vertexai
from vertexai import rag

logger = logging.getLogger(__name__)


@dataclass
class MultimodalRAGCorpusConfig:
    """
    🎭 Configuração de um corpus RAG multimodal
    """
    nome: str
    descricao: str
    diretorio_local: str
    bucket_path: str
    tipos_arquivo: List[str]
    tipos_multimodal: List[str] = field(default_factory=list)
    ativo: bool = True
    corpus_id: Optional[str] = None
    suporte_multimodal: bool = True
    
    def __post_init__(self):
        """Configurações automáticas após inicialização"""
        if not self.tipos_multimodal:
            self.tipos_multimodal = [
                # Imagens
                ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff",
                # Vídeos
                ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv",
                # Áudio
                ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"
            ]
    
    def eh_arquivo_multimodal(self, arquivo_path: str) -> bool:
        """Verifica se o arquivo é multimodal"""
        extensao = Path(arquivo_path).suffix.lower()
        return extensao in self.tipos_multimodal
    
    def eh_arquivo_texto(self, arquivo_path: str) -> bool:
        """Verifica se o arquivo é de texto/documento"""
        extensao = Path(arquivo_path).suffix.lower()
        return extensao in self.tipos_arquivo
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a configuração do corpus RAG multimodal para dicionário
        
        Returns:
            Dicionário com todas as configurações do corpus multimodal,
            incluindo tipos de arquivo e configurações de mídia
        """
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'diretorio_local': self.diretorio_local,
            'bucket_path': self.bucket_path,
            'tipos_arquivo': self.tipos_arquivo,
            'tipos_multimodal': self.tipos_multimodal,
            'ativo': self.ativo,
            'suporte_multimodal': self.suporte_multimodal,
            'corpus_id': self.corpus_id
        }


class ProcessadorMultimodal:
    """
    🎨 Processador de conteúdo multimodal
    
    Converte diferentes tipos de mídia para formatos compatíveis
    com o Gemini e Vertex AI.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tipos_suportados = {
            'imagem': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'documento': ['.pdf', '.txt', '.md', '.docx', '.doc', '.rtf']
        }
    
    def detectar_tipo_midia(self, arquivo_path: str) -> str:
        """
        Detecta o tipo de mídia do arquivo
        
        Args:
            arquivo_path: Caminho do arquivo
            
        Returns:
            Tipo de mídia ('imagem', 'video', 'audio', 'documento', 'desconhecido')
        """
        extensao = Path(arquivo_path).suffix.lower()
        
        for tipo, extensoes in self.tipos_suportados.items():
            if extensao in extensoes:
                return tipo
        
        return 'desconhecido'
    
    def processar_imagem(self, arquivo_path: str) -> Part:
        """
        Processa arquivo de imagem para o Gemini
        
        Args:
            arquivo_path: Caminho da imagem
            
        Returns:
            Part do Gemini com a imagem
        """
        try:
            # Detectar MIME type
            mime_type, _ = mimetypes.guess_type(arquivo_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'  # Fallback
            
            # Ler e codificar imagem
            with open(arquivo_path, 'rb') as f:
                image_bytes = f.read()
            
            # Verificar tamanho (limite de 20MB para Gemini)
            tamanho_mb = len(image_bytes) / (1024 * 1024)
            if tamanho_mb > 20:
                raise ValueError(f"Imagem muito grande: {tamanho_mb:.1f}MB (máximo: 20MB)")
            
            # Criar Part
            return Part.from_bytes(
                mime_type=mime_type,
                data=image_bytes
            )
            
        except Exception as e:
            raise RuntimeError(f"Erro ao processar imagem {arquivo_path}: {e}")
    
    def processar_video(self, arquivo_path: str) -> Part:
        """
        Processa arquivo de vídeo para o Gemini
        
        Args:
            arquivo_path: Caminho do vídeo
            
        Returns:
            Part do Gemini com o vídeo
        """
        try:
            # Detectar MIME type
            mime_type, _ = mimetypes.guess_type(arquivo_path)
            if not mime_type or not mime_type.startswith('video/'):
                mime_type = 'video/mp4'  # Fallback
            
            # Ler vídeo
            with open(arquivo_path, 'rb') as f:
                video_bytes = f.read()
            
            # Verificar tamanho (limite maior para vídeos)
            tamanho_mb = len(video_bytes) / (1024 * 1024)
            limite_mb = self.config.get('limite_video_mb', 100)
            
            if tamanho_mb > limite_mb:
                raise ValueError(f"Vídeo muito grande: {tamanho_mb:.1f}MB (máximo: {limite_mb}MB)")
            
            # Criar Part
            return Part.from_bytes(
                mime_type=mime_type,
                data=video_bytes
            )
            
        except Exception as e:
            raise RuntimeError(f"Erro ao processar vídeo {arquivo_path}: {e}")
    
    def processar_audio(self, arquivo_path: str) -> Part:
        """
        Processa arquivo de áudio para o Gemini
        
        Args:
            arquivo_path: Caminho do áudio
            
        Returns:
            Part do Gemini com o áudio
        """
        try:
            # Detectar MIME type
            mime_type, _ = mimetypes.guess_type(arquivo_path)
            if not mime_type or not mime_type.startswith('audio/'):
                mime_type = 'audio/mpeg'  # Fallback
            
            # Ler áudio
            with open(arquivo_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Verificar tamanho
            tamanho_mb = len(audio_bytes) / (1024 * 1024)
            limite_mb = self.config.get('limite_audio_mb', 50)
            
            if tamanho_mb > limite_mb:
                raise ValueError(f"Áudio muito grande: {tamanho_mb:.1f}MB (máximo: {limite_mb}MB)")
            
            # Criar Part
            return Part.from_bytes(
                mime_type=mime_type,
                data=audio_bytes
            )
            
        except Exception as e:
            raise RuntimeError(f"Erro ao processar áudio {arquivo_path}: {e}")
    
    def extrair_texto_de_midia(self, arquivo_path: str, cliente_ia) -> str:
        """
        Extrai texto/descrição de arquivos de mídia usando Gemini Vision
        
        Args:
            arquivo_path: Caminho do arquivo
            cliente_ia: Cliente do Gemini
            
        Returns:
            Texto extraído ou descrição da mídia
        """
        tipo_midia = self.detectar_tipo_midia(arquivo_path)
        
        try:
            if tipo_midia == 'imagem':
                return self._extrair_texto_imagem(arquivo_path, cliente_ia)
            elif tipo_midia == 'video':
                return self._extrair_texto_video(arquivo_path, cliente_ia)
            elif tipo_midia == 'audio':
                return self._extrair_texto_audio(arquivo_path, cliente_ia)
            else:
                return f"Arquivo de mídia não suportado: {tipo_midia}"
                
        except Exception as e:
            logger.error(f"Erro ao extrair texto de {arquivo_path}: {e}")
            return f"Erro ao processar arquivo de mídia: {Path(arquivo_path).name}"
    
    def _extrair_texto_imagem(self, arquivo_path: str, cliente_ia) -> str:
        """Extrai texto de imagem usando Gemini Vision"""
        try:
            image_part = self.processar_imagem(arquivo_path)
            
            prompt = """
            Analise esta imagem detalhadamente e forneça:
            
            1. **Descrição geral**: O que você vê na imagem
            2. **Texto visível**: Qualquer texto, números ou dados que aparecem
            3. **Elementos técnicos**: Gráficos, tabelas, diagramas, fórmulas
            4. **Contexto**: Possível relação com validação de modelos, riscos, ou análises financeiras
            5. **Informações relevantes**: Dados, métricas, ou insights importantes
            
            Seja detalhado e preciso, pois esta informação será usada para consultas futuras.
            """
            
            resposta = cliente_ia.models.generate_content(
                model=self.config.get('modelo_vision', 'gemini-1.5-pro-002'),
                contents=[image_part, prompt]
            )
            
            return f"IMAGEM: {Path(arquivo_path).name}\n\n{resposta.text}"
            
        except Exception as e:
            return f"Erro ao analisar imagem {Path(arquivo_path).name}: {e}"
    
    def _extrair_texto_video(self, arquivo_path: str, cliente_ia) -> str:
        """Extrai informações de vídeo usando Gemini"""
        try:
            video_part = self.processar_video(arquivo_path)
            
            prompt = """
            Analise este vídeo e forneça:
            
            1. **Resumo do conteúdo**: O que acontece no vídeo
            2. **Texto visível**: Qualquer texto, slides, ou dados mostrados
            3. **Áudio/Narração**: Principais pontos falados (se houver)
            4. **Elementos visuais**: Gráficos, apresentações, demonstrações
            5. **Contexto técnico**: Relação com modelos, validação, ou análises
            6. **Momentos importantes**: Timestamps de informações relevantes
            
            Foque em informações que seriam úteis para consultas sobre validação de modelos.
            """
            
            resposta = cliente_ia.models.generate_content(
                model=self.config.get('modelo_vision', 'gemini-1.5-pro-002'),
                contents=[video_part, prompt]
            )
            
            return f"VÍDEO: {Path(arquivo_path).name}\n\n{resposta.text}"
            
        except Exception as e:
            return f"Erro ao analisar vídeo {Path(arquivo_path).name}: {e}"
    
    def _extrair_texto_audio(self, arquivo_path: str, cliente_ia) -> str:
        """Extrai texto de áudio usando Gemini"""
        try:
            audio_part = self.processar_audio(arquivo_path)
            
            prompt = """
            Analise este áudio e forneça:
            
            1. **Transcrição**: Texto falado no áudio (se possível)
            2. **Resumo do conteúdo**: Principais tópicos abordados
            3. **Contexto**: Tipo de apresentação, reunião, ou explicação
            4. **Informações técnicas**: Dados, métricas, ou conceitos mencionados
            5. **Pontos importantes**: Insights relevantes para validação de modelos
            
            Seja preciso na transcrição e identifique informações técnicas importantes.
            """
            
            resposta = cliente_ia.models.generate_content(
                model=self.config.get('modelo_vision', 'gemini-1.5-pro-002'),
                contents=[audio_part, prompt]
            )
            
            return f"ÁUDIO: {Path(arquivo_path).name}\n\n{resposta.text}"
            
        except Exception as e:
            return f"Erro ao analisar áudio {Path(arquivo_path).name}: {e}"


class ValidAIRAGMultimodal:
    """
    🎭 Sistema RAG Multimodal para ValidAI
    
    Extensão do sistema RAG que suporta documentos, imagens, vídeos
    e outros tipos de mídia usando Gemini Vision e Vertex AI.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o sistema RAG multimodal
        
        Args:
            config: Configurações do sistema
        """
        self.config = config
        self.corpus_configs: Dict[str, MultimodalRAGCorpusConfig] = {}
        self.corpus_ativos: Dict[str, Any] = {}
        self.ferramentas_busca: Dict[str, Tool] = {}
        
        # Inicializar processador multimodal
        self.processador_multimodal = ProcessadorMultimodal(config)
        
        # Inicializar Google Cloud
        self._inicializar_google_cloud()
        
        # Carregar configurações de corpus
        self._carregar_configuracoes_corpus()
        
        logger.info("✅ ValidAI RAG Multimodal inicializado")
    
    def _inicializar_google_cloud(self) -> None:
        """Inicializa conexões com Google Cloud"""
        try:
            logger.info("🔗 Conectando com Google Cloud...")
            
            vertexai.init(
                project=self.config['project_id'],
                location=self.config['location']
            )
            
            self.cliente_ia = genai.Client(
                vertexai=True,
                project=self.config['project_id'],
                location=self.config['location']
            )
            
            self.cliente_storage = storage.Client(
                project=self.config['project_id']
            )
            
            logger.info("✅ Conectado ao Google Cloud")
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro na conexão Google Cloud: {e}")
    
    def _carregar_configuracoes_corpus(self) -> None:
        """Carrega configurações dos corpus multimodais"""
        logger.info("📋 Carregando configurações de corpus multimodais...")
        
        # Configurações padrão com suporte multimodal
        corpus_padrao = {
            'instrucoes_normativas': MultimodalRAGCorpusConfig(
                nome="Instruções Normativas",
                descricao="INs 706, 1253 e 1146 com imagens e diagramas",
                diretorio_local="base_conhecimento/ins",
                bucket_path="validai-rag/ins",
                tipos_arquivo=[".pdf", ".txt", ".md"],
                suporte_multimodal=True
            ),
            'apresentacoes_validacao': MultimodalRAGCorpusConfig(
                nome="Apresentações e Vídeos",
                descricao="Apresentações, vídeos explicativos e materiais visuais",
                diretorio_local="base_conhecimento/apresentacoes",
                bucket_path="validai-rag/apresentacoes",
                tipos_arquivo=[".pdf", ".pptx", ".txt", ".md"],
                suporte_multimodal=True
            ),
            'graficos_metricas': MultimodalRAGCorpusConfig(
                nome="Gráficos e Métricas",
                descricao="Visualizações, dashboards e gráficos de performance",
                diretorio_local="base_conhecimento/graficos",
                bucket_path="validai-rag/graficos",
                tipos_arquivo=[".pdf", ".txt", ".md"],
                suporte_multimodal=True
            ),
            'casos_uso_visuais': MultimodalRAGCorpusConfig(
                nome="Casos de Uso Visuais",
                descricao="Exemplos práticos com imagens, vídeos e demonstrações",
                diretorio_local="base_conhecimento/casos_visuais",
                bucket_path="validai-rag/casos_visuais",
                tipos_arquivo=[".pdf", ".txt", ".md", ".ipynb"],
                suporte_multimodal=True
            )
        }
        
        # Carregar configurações personalizadas
        config_file = self.config.get('corpus_config_file', 'rag_multimodal_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                for nome, data in config_data.items():
                    corpus_padrao[nome] = MultimodalRAGCorpusConfig(**data)
                
                logger.info(f"✅ Configurações carregadas de {config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar config: {e}")
        
        self.corpus_configs = corpus_padrao
        logger.info(f"📋 {len(self.corpus_configs)} corpus multimodais configurados")
    
    def processar_arquivos_multimodais(self, corpus_id: str) -> Dict[str, Any]:
        """
        Processa arquivos multimodais de um corpus
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            Estatísticas do processamento
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        diretorio = Path(config.diretorio_local)
        
        if not diretorio.exists():
            raise ValueError(f"Diretório não existe: {diretorio}")
        
        logger.info(f"🎭 Processando arquivos multimodais: {config.nome}")
        
        estatisticas = {
            'total_arquivos': 0,
            'arquivos_texto': 0,
            'arquivos_imagem': 0,
            'arquivos_video': 0,
            'arquivos_audio': 0,
            'arquivos_processados': 0,
            'erros': 0,
            'textos_extraidos': []
        }
        
        # Processar todos os arquivos
        for arquivo in diretorio.rglob('*'):
            if arquivo.is_file():
                estatisticas['total_arquivos'] += 1
                
                try:
                    if config.eh_arquivo_texto(str(arquivo)):
                        # Arquivo de texto normal
                        estatisticas['arquivos_texto'] += 1
                        estatisticas['arquivos_processados'] += 1
                        
                    elif config.eh_arquivo_multimodal(str(arquivo)):
                        # Arquivo multimodal - extrair texto
                        tipo_midia = self.processador_multimodal.detectar_tipo_midia(str(arquivo))
                        
                        if tipo_midia == 'imagem':
                            estatisticas['arquivos_imagem'] += 1
                        elif tipo_midia == 'video':
                            estatisticas['arquivos_video'] += 1
                        elif tipo_midia == 'audio':
                            estatisticas['arquivos_audio'] += 1
                        
                        # Extrair texto da mídia
                        texto_extraido = self.processador_multimodal.extrair_texto_de_midia(
                            str(arquivo), self.cliente_ia
                        )
                        
                        estatisticas['textos_extraidos'].append({
                            'arquivo': str(arquivo),
                            'tipo': tipo_midia,
                            'texto': texto_extraido
                        })
                        
                        estatisticas['arquivos_processados'] += 1
                        
                        logger.info(f"   🎨 Processado {tipo_midia}: {arquivo.name}")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar {arquivo.name}: {e}")
                    estatisticas['erros'] += 1
        
        logger.info(f"✅ Processamento concluído: {estatisticas['arquivos_processados']} arquivos")
        return estatisticas
    
    def consultar_multimodal(self, corpus_id: str, pergunta: str, 
                           incluir_contexto_visual: bool = True) -> str:
        """
        Faz consulta multimodal incluindo contexto de imagens/vídeos
        
        Args:
            corpus_id: ID do corpus
            pergunta: Pergunta do usuário
            incluir_contexto_visual: Se deve incluir contexto de mídias
            
        Returns:
            Resposta da IA com contexto multimodal
        """
        if corpus_id not in self.ferramentas_busca:
            raise ValueError(f"Ferramenta de busca não disponível para: {corpus_id}")
        
        ferramenta = self.ferramentas_busca[corpus_id]
        config = self.corpus_configs[corpus_id]
        
        logger.info(f"🎭 Consulta multimodal em {config.nome}: {pergunta[:50]}...")
        
        try:
            # Criar prompt contextualizado para multimodal
            prompt_base = f"""
            Você está consultando a base de conhecimento multimodal: {config.nome}
            Descrição: {config.descricao}
            
            Esta base contém documentos, imagens, vídeos e outros tipos de mídia.
            Quando relevante, faça referência a informações visuais, gráficos, ou 
            conteúdo extraído de mídias.
            
            Pergunta do usuário: {pergunta}
            """
            
            if incluir_contexto_visual:
                prompt_base += """
                
                IMPORTANTE: Se houver informações visuais relevantes (gráficos, imagens, 
                vídeos, apresentações), inclua essas informações na sua resposta e 
                mencione especificamente quando estiver se referindo a conteúdo visual.
                """
            
            resposta = self.cliente_ia.models.generate_content(
                model=self.config.get('modelo_ia', 'gemini-1.5-pro-002'),
                contents=prompt_base,
                config=GenerateContentConfig(tools=[ferramenta]),
            )
            
            return resposta.text
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro na consulta multimodal: {e}")
    
    def salvar_textos_extraidos(self, corpus_id: str, estatisticas: Dict[str, Any]) -> str:
        """
        Salva textos extraídos de mídias em arquivo para referência
        
        Args:
            corpus_id: ID do corpus
            estatisticas: Estatísticas do processamento
            
        Returns:
            Caminho do arquivo salvo
        """
        config = self.corpus_configs[corpus_id]
        
        # Criar arquivo de textos extraídos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = Path(config.diretorio_local) / f"textos_extraidos_{timestamp}.md"
        
        conteudo = f"""# Textos Extraídos - {config.nome}

Gerado em: {datetime.now().isoformat()}
Corpus: {corpus_id}

## Estatísticas
- Total de arquivos: {estatisticas['total_arquivos']}
- Arquivos de texto: {estatisticas['arquivos_texto']}
- Imagens processadas: {estatisticas['arquivos_imagem']}
- Vídeos processados: {estatisticas['arquivos_video']}
- Áudios processados: {estatisticas['arquivos_audio']}
- Erros: {estatisticas['erros']}

## Conteúdo Extraído

"""
        
        for item in estatisticas['textos_extraidos']:
            conteudo += f"""
### {item['arquivo']} ({item['tipo'].upper()})

{item['texto']}

---

"""
        
        # Salvar arquivo
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        logger.info(f"💾 Textos extraídos salvos em: {arquivo_saida}")
        return str(arquivo_saida)


def criar_configuracao_rag_multimodal() -> Dict[str, Any]:
    """
    Cria configuração padrão para o sistema RAG multimodal
    
    Returns:
        Dicionário de configuração
    """
    config_base = {
        'project_id': 'bv-cdip-des',
        'location': 'us-central1',
        'bucket_name': 'validai-rag-multimodal',
        'modelo_embedding': 'publishers/google/models/text-embedding-005',
        'modelo_ia': 'gemini-1.5-pro-002',
        'modelo_vision': 'gemini-1.5-pro-002',
        'chunk_size': 1024,
        'chunk_overlap': 256,
        'top_resultados': 10,
        'limite_similaridade': 0.5,
        'tamanho_max_arquivo_mb': 50,
        'limite_video_mb': 100,
        'limite_audio_mb': 50,
        'corpus_config_file': 'rag_multimodal_config.json'
    }
    
    return config_base


# Exemplo de uso
if __name__ == "__main__":
    # Configuração multimodal
    config = criar_configuracao_rag_multimodal()
    
    # Inicializar sistema RAG multimodal
    rag_multimodal = ValidAIRAGMultimodal(config)
    
    # Listar corpus disponíveis
    print("🎭 Corpus multimodais disponíveis:")
    for corpus_id, config in rag_multimodal.corpus_configs.items():
        print(f"  - {config.nome} ({corpus_id})")
        print(f"    Suporte multimodal: {config.suporte_multimodal}")
        print(f"    Tipos: {config.tipos_arquivo + config.tipos_multimodal}")