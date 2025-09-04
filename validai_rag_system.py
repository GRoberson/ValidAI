#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📚 ValidAI RAG System - Sistema RAG Avançado para Documentos

Sistema RAG dedicado para documentos de validação de modelos, usando
Vertex AI RAG nativo do Google Cloud. Substitui o RAG original do ValidAI
com tecnologia mais avançada e flexível.
"""

import os
import uuid
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# Google Cloud imports
from google import genai
from google.cloud import storage
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
import vertexai
from vertexai import rag

logger = logging.getLogger(__name__)


@dataclass
class RAGCorpusConfig:
    """
    📋 Configuração de um corpus RAG
    """
    nome: str
    descricao: str
    diretorio_local: str
    bucket_path: str
    tipos_arquivo: List[str]
    ativo: bool = True
    corpus_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a configuração do corpus RAG para dicionário
        
        Returns:
            Dicionário com todas as configurações do corpus
        """
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'diretorio_local': self.diretorio_local,
            'bucket_path': self.bucket_path,
            'tipos_arquivo': self.tipos_arquivo,
            'ativo': self.ativo,
            'corpus_id': self.corpus_id
        }


class ValidAIRAGManager:
    """
    🧠 Gerenciador RAG Avançado para ValidAI
    
    Sistema completo para criar, gerenciar e consultar múltiplas bases
    de conhecimento usando Vertex AI RAG nativo.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador RAG
        
        Args:
            config: Configurações do sistema
        """
        self.config = config
        self.corpus_configs: Dict[str, RAGCorpusConfig] = {}
        self.corpus_ativos: Dict[str, Any] = {}
        self.ferramentas_busca: Dict[str, Tool] = {}
        
        # Inicializar Google Cloud
        self._inicializar_google_cloud()
        
        # Carregar configurações de corpus
        self._carregar_configuracoes_corpus()
        
        logger.info("✅ ValidAI RAG Manager inicializado")
    
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
        """Carrega configurações dos corpus disponíveis"""
        logger.info("📋 Carregando configurações de corpus...")
        
        # Configurações padrão dos corpus do ValidAI
        corpus_padrao = {
            'instrucoes_normativas': RAGCorpusConfig(
                nome="Instruções Normativas",
                descricao="INs 706, 1253 e 1146 sobre validação de modelos",
                diretorio_local="base_conhecimento/ins",
                bucket_path="validai-rag/ins",
                tipos_arquivo=[".pdf", ".txt", ".md"]
            ),
            'validacoes_mercado': RAGCorpusConfig(
                nome="Validações de Risco de Mercado",
                descricao="Relatórios e documentos de validação de modelos de mercado",
                diretorio_local="base_conhecimento/mercado",
                bucket_path="validai-rag/mercado",
                tipos_arquivo=[".pdf", ".txt", ".md", ".docx"]
            ),
            'validacoes_credito': RAGCorpusConfig(
                nome="Validações de Risco de Crédito",
                descricao="Relatórios e documentos de validação de modelos de crédito",
                diretorio_local="base_conhecimento/credito",
                bucket_path="validai-rag/credito",
                tipos_arquivo=[".pdf", ".txt", ".md", ".docx"]
            ),
            'metodologias_gerais': RAGCorpusConfig(
                nome="Metodologias e Frameworks",
                descricao="Documentos sobre metodologias de validação e frameworks",
                diretorio_local="base_conhecimento/metodologias",
                bucket_path="validai-rag/metodologias",
                tipos_arquivo=[".pdf", ".txt", ".md"]
            ),
            'casos_uso': RAGCorpusConfig(
                nome="Casos de Uso e Exemplos",
                descricao="Exemplos práticos e casos de uso de validação",
                diretorio_local="base_conhecimento/casos_uso",
                bucket_path="validai-rag/casos_uso",
                tipos_arquivo=[".pdf", ".txt", ".md", ".ipynb"]
            )
        }
        
        # Carregar configurações personalizadas se existirem
        config_file = self.config.get('corpus_config_file', 'rag_corpus_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                for nome, data in config_data.items():
                    corpus_padrao[nome] = RAGCorpusConfig(**data)
                
                logger.info(f"✅ Configurações carregadas de {config_file}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar config: {e}")
        
        self.corpus_configs = corpus_padrao
        logger.info(f"📋 {len(self.corpus_configs)} corpus configurados")
    
    def listar_corpus_disponiveis(self) -> List[Dict[str, Any]]:
        """
        Lista todos os corpus disponíveis
        
        Returns:
            Lista com informações dos corpus
        """
        corpus_info = []
        
        for nome, config in self.corpus_configs.items():
            info = {
                'id': nome,
                'nome': config.nome,
                'descricao': config.descricao,
                'ativo': config.ativo,
                'tem_arquivos': os.path.exists(config.diretorio_local),
                'corpus_criado': config.corpus_id is not None
            }
            corpus_info.append(info)
        
        return corpus_info
    
    def verificar_arquivos_corpus(self, corpus_id: str) -> Dict[str, Any]:
        """
        Verifica arquivos disponíveis para um corpus
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            Informações sobre os arquivos
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        diretorio = Path(config.diretorio_local)
        
        if not diretorio.exists():
            return {
                'total_arquivos': 0,
                'arquivos_validos': 0,
                'tamanho_total_mb': 0,
                'tipos_encontrados': [],
                'status': 'diretorio_nao_existe'
            }
        
        arquivos_validos = []
        tamanho_total = 0
        tipos_encontrados = set()
        
        for arquivo in diretorio.rglob('*'):
            if arquivo.is_file():
                extensao = arquivo.suffix.lower()
                if extensao in config.tipos_arquivo:
                    arquivos_validos.append(str(arquivo))
                    tamanho_total += arquivo.stat().st_size
                    tipos_encontrados.add(extensao)
        
        return {
            'total_arquivos': len(list(diretorio.rglob('*'))),
            'arquivos_validos': len(arquivos_validos),
            'tamanho_total_mb': tamanho_total / (1024 * 1024),
            'tipos_encontrados': list(tipos_encontrados),
            'arquivos': arquivos_validos[:10],  # Primeiros 10 para preview
            'status': 'ok' if arquivos_validos else 'sem_arquivos_validos'
        }
    
    def enviar_arquivos_corpus(self, corpus_id: str) -> Tuple[int, int]:
        """
        Envia arquivos de um corpus para o Google Cloud Storage
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            (arquivos_enviados, arquivos_ignorados)
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        logger.info(f"📤 Enviando arquivos do corpus: {config.nome}")
        
        # Verificar bucket
        bucket_name = self.config['bucket_name']
        try:
            bucket = self.cliente_storage.get_bucket(bucket_name)
        except Exception as e:
            raise RuntimeError(f"❌ Erro ao acessar bucket {bucket_name}: {e}")
        
        # Processar arquivos
        diretorio = Path(config.diretorio_local)
        if not diretorio.exists():
            raise ValueError(f"Diretório não existe: {diretorio}")
        
        enviados = 0
        ignorados = 0
        tamanho_max_mb = self.config.get('tamanho_max_arquivo_mb', 50)
        
        for arquivo in diretorio.rglob('*'):
            if arquivo.is_file():
                extensao = arquivo.suffix.lower()
                
                if extensao not in config.tipos_arquivo:
                    ignorados += 1
                    continue
                
                # Verificar tamanho
                tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
                if tamanho_mb > tamanho_max_mb:
                    logger.warning(f"⏭️ Arquivo muito grande: {arquivo.name} ({tamanho_mb:.1f}MB)")
                    ignorados += 1
                    continue
                
                try:
                    # Criar caminho no bucket
                    caminho_relativo = arquivo.relative_to(diretorio)
                    nome_no_bucket = f"{config.bucket_path}/{caminho_relativo}".replace("\\", "/")
                    
                    # Enviar arquivo
                    blob = bucket.blob(nome_no_bucket)
                    blob.upload_from_filename(str(arquivo))
                    enviados += 1
                    
                    if enviados % 10 == 0:
                        logger.info(f"📤 Enviados {enviados} arquivos...")
                
                except Exception as e:
                    logger.error(f"❌ Erro ao enviar {arquivo.name}: {e}")
                    ignorados += 1
        
        logger.info(f"✅ Corpus {config.nome}: {enviados} enviados, {ignorados} ignorados")
        return enviados, ignorados
    
    def criar_corpus_rag(self, corpus_id: str) -> str:
        """
        Cria um corpus RAG no Vertex AI
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            ID do corpus criado
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        logger.info(f"🧠 Criando corpus RAG: {config.nome}")
        
        try:
            # Gerar nome único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_corpus = f"validai_{corpus_id}_{timestamp}"
            
            # Criar corpus
            corpus_rag = rag.create_corpus(
                display_name=nome_corpus,
                description=f"{config.descricao} - Criado em {datetime.now().isoformat()}",
                backend_config=rag.RagVectorDbConfig(
                    rag_embedding_model_config=rag.RagEmbeddingModelConfig(
                        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                            publisher_model=self.config.get(
                                'modelo_embedding', 
                                'publishers/google/models/text-embedding-005'
                            )
                        )
                    )
                )
            )
            
            # Armazenar referência
            self.corpus_ativos[corpus_id] = corpus_rag
            config.corpus_id = corpus_rag.name
            
            logger.info(f"✅ Corpus criado: {nome_corpus}")
            return corpus_rag.name
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro ao criar corpus: {e}")
    
    def processar_arquivos_corpus(self, corpus_id: str) -> None:
        """
        Processa arquivos de um corpus no Vertex AI RAG
        
        Args:
            corpus_id: ID do corpus
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        if corpus_id not in self.corpus_ativos:
            raise ValueError(f"Corpus não foi criado ainda: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        corpus_rag = self.corpus_ativos[corpus_id]
        
        logger.info(f"📚 Processando arquivos do corpus: {config.nome}")
        
        try:
            # Montar caminho GCS
            bucket_uri = f"gs://{self.config['bucket_name']}"
            caminho_importacao = f"{bucket_uri}/{config.bucket_path}/"
            
            logger.info(f"📂 Importando de: {caminho_importacao}")
            
            # Configurar processamento
            chunk_size = self.config.get('chunk_size', 1024)
            chunk_overlap = self.config.get('chunk_overlap', 256)
            
            # Iniciar importação
            resposta_importacao = rag.import_files(
                corpus_name=corpus_rag.name,
                paths=[caminho_importacao],
                transformation_config=rag.TransformationConfig(
                    chunking_config=rag.ChunkingConfig(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                ),
            )
            
            logger.info(f"✅ Processamento iniciado para: {config.nome}")
            logger.info("⏳ Aguarde alguns minutos para conclusão...")
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro no processamento: {e}")
    
    def criar_ferramenta_busca(self, corpus_id: str) -> Tool:
        """
        Cria ferramenta de busca para um corpus
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            Ferramenta de busca configurada
        """
        if corpus_id not in self.corpus_ativos:
            raise ValueError(f"Corpus não ativo: {corpus_id}")
        
        corpus_rag = self.corpus_ativos[corpus_id]
        
        try:
            ferramenta = Tool(
                retrieval=Retrieval(
                    vertex_rag_store=VertexRagStore(
                        rag_corpora=[corpus_rag.name],
                        similarity_top_k=self.config.get('top_resultados', 10),
                        vector_distance_threshold=self.config.get('limite_similaridade', 0.5),
                    )
                )
            )
            
            self.ferramentas_busca[corpus_id] = ferramenta
            logger.info(f"🔧 Ferramenta de busca criada para: {corpus_id}")
            
            return ferramenta
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro ao criar ferramenta: {e}")
    
    def consultar_corpus(self, corpus_id: str, pergunta: str) -> str:
        """
        Faz uma consulta a um corpus específico
        
        Args:
            corpus_id: ID do corpus
            pergunta: Pergunta do usuário
            
        Returns:
            Resposta da IA
        """
        if corpus_id not in self.ferramentas_busca:
            raise ValueError(f"Ferramenta de busca não disponível para: {corpus_id}")
        
        ferramenta = self.ferramentas_busca[corpus_id]
        config = self.corpus_configs[corpus_id]
        
        logger.info(f"🤔 Consultando {config.nome}: {pergunta[:50]}...")
        
        try:
            # Criar prompt contextualizado
            prompt_contextualizado = f"""
            Você está consultando a base de conhecimento: {config.nome}
            Descrição: {config.descricao}
            
            Pergunta do usuário: {pergunta}
            
            Por favor, responda baseado exclusivamente no conteúdo desta base de conhecimento.
            Se a informação não estiver disponível, informe claramente.
            """
            
            resposta = self.cliente_ia.models.generate_content(
                model=self.config.get('modelo_ia', 'gemini-1.5-pro-002'),
                contents=prompt_contextualizado,
                config=GenerateContentConfig(tools=[ferramenta]),
            )
            
            return resposta.text
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro na consulta: {e}")
    
    def consultar_multiplos_corpus(self, corpus_ids: List[str], pergunta: str) -> str:
        """
        Consulta múltiplos corpus simultaneamente
        
        Args:
            corpus_ids: Lista de IDs dos corpus
            pergunta: Pergunta do usuário
            
        Returns:
            Resposta consolidada
        """
        if not corpus_ids:
            raise ValueError("Lista de corpus não pode estar vazia")
        
        # Verificar se todos os corpus estão disponíveis
        ferramentas = []
        nomes_corpus = []
        
        for corpus_id in corpus_ids:
            if corpus_id not in self.ferramentas_busca:
                raise ValueError(f"Corpus não disponível: {corpus_id}")
            
            ferramentas.append(self.ferramentas_busca[corpus_id])
            nomes_corpus.append(self.corpus_configs[corpus_id].nome)
        
        logger.info(f"🔍 Consultando múltiplos corpus: {', '.join(nomes_corpus)}")
        
        try:
            # Criar prompt para consulta múltipla
            prompt_multiplo = f"""
            Você está consultando múltiplas bases de conhecimento simultaneamente:
            {', '.join(nomes_corpus)}
            
            Pergunta do usuário: {pergunta}
            
            Por favor:
            1. Busque informações em todas as bases disponíveis
            2. Consolide as informações de forma coerente
            3. Indique quando informações vêm de bases específicas
            4. Se houver conflitos, mencione as diferentes perspectivas
            """
            
            resposta = self.cliente_ia.models.generate_content(
                model=self.config.get('modelo_ia', 'gemini-1.5-pro-002'),
                contents=prompt_multiplo,
                config=GenerateContentConfig(tools=ferramentas),
            )
            
            return resposta.text
            
        except Exception as e:
            raise RuntimeError(f"❌ Erro na consulta múltipla: {e}")
    
    def obter_estatisticas_corpus(self, corpus_id: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de um corpus
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            Dicionário com estatísticas
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        
        # Estatísticas básicas
        stats = {
            'nome': config.nome,
            'descricao': config.descricao,
            'ativo': config.ativo,
            'corpus_criado': config.corpus_id is not None,
            'ferramenta_disponivel': corpus_id in self.ferramentas_busca
        }
        
        # Estatísticas de arquivos
        info_arquivos = self.verificar_arquivos_corpus(corpus_id)
        stats.update(info_arquivos)
        
        return stats
    
    def limpar_corpus(self, corpus_id: str) -> None:
        """
        Remove um corpus e seus recursos
        
        Args:
            corpus_id: ID do corpus
        """
        if corpus_id not in self.corpus_configs:
            raise ValueError(f"Corpus não encontrado: {corpus_id}")
        
        config = self.corpus_configs[corpus_id]
        logger.info(f"🗑️ Removendo corpus: {config.nome}")
        
        try:
            # Remover corpus do Vertex AI
            if corpus_id in self.corpus_ativos:
                corpus_rag = self.corpus_ativos[corpus_id]
                rag.delete_corpus(corpus_rag.name)
                del self.corpus_ativos[corpus_id]
                logger.info("✅ Corpus removido do Vertex AI")
            
            # Remover ferramenta de busca
            if corpus_id in self.ferramentas_busca:
                del self.ferramentas_busca[corpus_id]
                logger.info("✅ Ferramenta de busca removida")
            
            # Limpar referência
            config.corpus_id = None
            
            logger.info(f"✅ Corpus {config.nome} limpo com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar corpus: {e}")
    
    def salvar_configuracoes(self) -> None:
        """Salva configurações atuais dos corpus"""
        config_file = self.config.get('corpus_config_file', 'rag_corpus_config.json')
        
        try:
            config_data = {}
            for nome, config in self.corpus_configs.items():
                config_data[nome] = config.to_dict()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Configurações salvas em: {config_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configurações: {e}")


class ValidAIRAGInterface:
    """
    🎨 Interface para o sistema RAG do ValidAI
    
    Fornece métodos para integração com Gradio e outras interfaces.
    """
    
    def __init__(self, rag_manager: ValidAIRAGManager):
        self.rag_manager = rag_manager
        self.corpus_selecionado = None
        self.historico_consultas = []
    
    def obter_opcoes_corpus(self) -> List[Tuple[str, str]]:
        """
        Obtém opções de corpus para dropdown
        
        Returns:
            Lista de tuplas (nome_exibicao, corpus_id)
        """
        opcoes = []
        
        for corpus_id, config in self.rag_manager.corpus_configs.items():
            if config.ativo:
                # Verificar se tem arquivos
                info = self.rag_manager.verificar_arquivos_corpus(corpus_id)
                status = "✅" if info['arquivos_validos'] > 0 else "⚠️"
                
                nome_exibicao = f"{status} {config.nome} ({info['arquivos_validos']} docs)"
                opcoes.append((nome_exibicao, corpus_id))
        
        return opcoes
    
    def selecionar_corpus(self, corpus_id: str) -> str:
        """
        Seleciona um corpus para consultas
        
        Args:
            corpus_id: ID do corpus
            
        Returns:
            Mensagem de status
        """
        if not corpus_id:
            return "⚠️ Nenhum corpus selecionado"
        
        if corpus_id not in self.rag_manager.corpus_configs:
            return f"❌ Corpus não encontrado: {corpus_id}"
        
        self.corpus_selecionado = corpus_id
        config = self.rag_manager.corpus_configs[corpus_id]
        
        # Verificar status
        info = self.rag_manager.verificar_arquivos_corpus(corpus_id)
        
        if info['arquivos_validos'] == 0:
            return f"⚠️ {config.nome} selecionado, mas não há arquivos válidos"
        
        # Verificar se corpus está pronto
        if corpus_id not in self.rag_manager.ferramentas_busca:
            return f"🔧 {config.nome} selecionado. Preparando para consultas..."
        
        return f"✅ {config.nome} pronto para consultas ({info['arquivos_validos']} documentos)"
    
    def processar_consulta(self, pergunta: str) -> str:
        """
        Processa uma consulta do usuário
        
        Args:
            pergunta: Pergunta do usuário
            
        Returns:
            Resposta da IA
        """
        if not self.corpus_selecionado:
            return "⚠️ Selecione um corpus antes de fazer perguntas"
        
        if not pergunta.strip():
            return "⚠️ Digite uma pergunta válida"
        
        try:
            # Verificar se ferramenta está disponível
            if self.corpus_selecionado not in self.rag_manager.ferramentas_busca:
                return "🔧 Corpus ainda não está pronto. Aguarde o processamento..."
            
            # Fazer consulta
            resposta = self.rag_manager.consultar_corpus(
                self.corpus_selecionado, 
                pergunta
            )
            
            # Adicionar ao histórico
            self.historico_consultas.append({
                'timestamp': datetime.now().isoformat(),
                'corpus': self.corpus_selecionado,
                'pergunta': pergunta,
                'resposta': resposta
            })
            
            # Adicionar cabeçalho informativo
            config = self.rag_manager.corpus_configs[self.corpus_selecionado]
            cabecalho = f"**📚 Consultando: {config.nome}**\n\n"
            
            return cabecalho + resposta
            
        except Exception as e:
            return f"❌ Erro na consulta: {str(e)}"
    
    def obter_status_sistema(self) -> str:
        """
        Obtém status geral do sistema RAG
        
        Returns:
            Status formatado em markdown
        """
        corpus_info = self.rag_manager.listar_corpus_disponiveis()
        
        status = "## 📊 Status do Sistema RAG\n\n"
        
        for info in corpus_info:
            emoji = "✅" if info['corpus_criado'] else "⚠️"
            status += f"- {emoji} **{info['nome']}**: "
            
            if info['corpus_criado']:
                status += "Pronto para consultas\n"
            elif info['tem_arquivos']:
                status += "Arquivos disponíveis, aguardando processamento\n"
            else:
                status += "Sem arquivos disponíveis\n"
        
        return status


def criar_configuracao_rag_padrao() -> Dict[str, Any]:
    """
    Cria configuração padrão para o sistema RAG
    
    Returns:
        Dicionário de configuração
    """
    return {
        'project_id': 'bv-cdip-des',
        'location': 'us-central1',
        'bucket_name': 'validai-rag-bucket',
        'modelo_embedding': 'publishers/google/models/text-embedding-005',
        'modelo_ia': 'gemini-1.5-pro-002',
        'chunk_size': 1024,
        'chunk_overlap': 256,
        'top_resultados': 10,
        'limite_similaridade': 0.5,
        'tamanho_max_arquivo_mb': 50,
        'corpus_config_file': 'rag_corpus_config.json'
    }


# Exemplo de uso
if __name__ == "__main__":
    # Configuração de exemplo
    config = criar_configuracao_rag_padrao()
    
    # Inicializar sistema RAG
    rag_manager = ValidAIRAGManager(config)
    
    # Criar interface
    interface = ValidAIRAGInterface(rag_manager)
    
    # Listar corpus disponíveis
    print("📚 Corpus disponíveis:")
    for nome, corpus_id in interface.obter_opcoes_corpus():
        print(f"  - {nome} ({corpus_id})")