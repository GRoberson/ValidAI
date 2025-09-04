#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Assistente RAG para Análise de Código Local

Ei! Este é seu assistente pessoal para analisar código usando IA.
Ele pega seus arquivos de código, joga na nuvem do Google e depois
você pode fazer perguntas sobre o código como se fosse um chat!

Super útil para entender projetos grandes ou código legado! 🚀
"""

import os
import uuid
import sys
from pathlib import Path
from typing import List, Optional

# Bibliotecas do Google Cloud - não se preocupe, é mais simples do que parece!
from google import genai
from google.cloud import storage
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore
import vertexai
from vertexai import rag


class AssistenteRAG:
    """
    🎯 Seu assistente pessoal para conversar com código!
    
    Pense nele como um ChatGPT que conhece seu código de cor.
    Ele lê todos os seus arquivos, entende o contexto e responde
    suas perguntas de forma inteligente.
    """
    
    def __init__(self, config: dict):
        """
        Vamos configurar seu assistente!
        
        Args:
            config: Um dicionário com suas configurações (não se preocupe, é fácil!)
        """
        self.config = config
        self._verificar_configuracoes()
        self._conectar_google_cloud()
        
        # Variáveis que vamos usar depois
        self.corpus_rag = None
        self.ferramenta_busca = None
        
    def _verificar_configuracoes(self) -> None:
        """
        Vamos checar se você configurou tudo certinho!
        
        Não queremos surpresas desagradáveis depois, né? 😅
        """
        print("🔍 Verificando suas configurações...")
        
        # Essas são obrigatórias - sem elas não rola!
        campos_obrigatorios = [
            'PROJECT_ID', 'LOCATION', 'BUCKET_NAME', 'CAMINHO_CODIGO',
            'MODELO_EMBEDDING', 'MODELO_IA'
        ]
        
        for campo in campos_obrigatorios:
            if not self.config.get(campo):
                raise ValueError(f"Opa! Você esqueceu de configurar: {campo}")
        
        # Vamos verificar se você não esqueceu de trocar os valores padrão
        if self.config['PROJECT_ID'] == "seu-projeto-aqui":
            raise ValueError("🚨 Você precisa colocar o ID real do seu projeto Google Cloud!")
            
        if self.config['BUCKET_NAME'] == "seu-bucket-aqui":
            raise ValueError("🚨 Você precisa colocar o nome real do seu bucket!")
            
        if not os.path.exists(self.config['CAMINHO_CODIGO']):
            raise ValueError(f"🚨 Não encontrei o diretório: {self.config['CAMINHO_CODIGO']}")
            
        print("✅ Tudo certo! Suas configurações estão perfeitas.")
    
    def _conectar_google_cloud(self) -> None:
        """
        Conectando com o Google Cloud... É como fazer login, mas para robôs! 🤖
        """
        try:
            print("🔗 Conectando com o Google Cloud...")
            
            # Inicializar o Vertex AI
            vertexai.init(
                project=self.config['PROJECT_ID'], 
                location=self.config['LOCATION']
            )
            
            # Criar nossos clientes (são como "telefones" para falar com a Google)
            self.cliente_ia = genai.Client(
                vertexai=True, 
                project=self.config['PROJECT_ID'], 
                location=self.config['LOCATION']
            )
            
            self.cliente_storage = storage.Client(project=self.config['PROJECT_ID'])
            
            print("✅ Conectado! Agora posso conversar com a Google.")
            
        except Exception as e:
            raise RuntimeError(f"😵 Deu ruim na conexão: {e}")
    
    def verificar_bucket(self) -> bool:
        """
        Vamos ver se conseguimos acessar seu bucket no Google Cloud.
        
        É como verificar se você tem a chave da sua casa! 🔑
        """
        try:
            print(f"🔍 Verificando acesso ao bucket '{self.config['BUCKET_NAME']}'...")
            bucket = self.cliente_storage.get_bucket(self.config['BUCKET_NAME'])
            print(f"✅ Perfeito! Consegui acessar o bucket: {bucket.name}")
            return True
        except Exception as e:
            print(f"❌ Ops! Não consegui acessar o bucket: {e}")
            print("💡 Dica: Verifique se o bucket existe e se você tem permissão!")
            return False
    
    def enviar_arquivos(self) -> tuple[int, int]:
        """
        Hora de enviar seus arquivos para a nuvem! ☁️
        
        É como fazer backup, mas mais inteligente.
        
        Returns:
            Uma tupla com (arquivos enviados, arquivos ignorados)
        """
        print("📤 Preparando para enviar seus arquivos...")
        
        enviados = 0
        ignorados = 0
        
        # Calcular limite de tamanho
        limite_bytes = 0
        if self.config['TAMANHO_MAX_MB'] > 0:
            limite_bytes = self.config['TAMANHO_MAX_MB'] * 1024 * 1024
            print(f"📏 Limite de tamanho: {self.config['TAMANHO_MAX_MB']} MB")
        
        # Pegar o bucket
        bucket = self.cliente_storage.get_bucket(self.config['BUCKET_NAME'])
        caminho_local = Path(self.config['CAMINHO_CODIGO'])
        
        print(f"🔍 Procurando arquivos em: {caminho_local}")
        
        # Vamos passear pelos arquivos!
        for arquivo in caminho_local.rglob('*'):
            if arquivo.is_file() and self._arquivo_suportado(arquivo):
                try:
                    # Verificar se o arquivo não é muito grande
                    if limite_bytes > 0:
                        tamanho = arquivo.stat().st_size
                        if tamanho > limite_bytes:
                            print(f"⏭️  Arquivo muito grande, pulando: {arquivo.name} ({tamanho / (1024*1024):.1f} MB)")
                            ignorados += 1
                            continue
                    
                    # Criar caminho no bucket mantendo a estrutura
                    caminho_relativo = arquivo.relative_to(caminho_local)
                    
                    pasta_gcs = self.config.get('PASTA_GCS', '').strip('/')
                    if pasta_gcs:
                        nome_no_bucket = f"{pasta_gcs}/{caminho_relativo}"
                    else:
                        nome_no_bucket = str(caminho_relativo)
                    
                    # Normalizar para o formato do GCS
                    nome_no_bucket = nome_no_bucket.replace("\\", "/")
                    
                    # Enviar o arquivo
                    blob = bucket.blob(nome_no_bucket)
                    blob.upload_from_filename(str(arquivo))
                    enviados += 1
                    
                    # Mostrar progresso de vez em quando
                    if enviados % 25 == 0:
                        print(f"📤 Já enviei {enviados} arquivos...")
                        
                except Exception as e:
                    print(f"❌ Erro ao enviar {arquivo.name}: {e}")
                    ignorados += 1
        
        # Relatório final
        print(f"\n🎉 Pronto! Enviei {enviados} arquivos")
        if ignorados > 0:
            print(f"⏭️  Ignorei {ignorados} arquivos (muito grandes ou com erro)")
        
        if enviados == 0:
            print("\n🤔 Hmm, não encontrei nenhum arquivo para enviar...")
            print("💡 Verifique se o caminho está certo e se há arquivos suportados!")
        
        return enviados, ignorados
    
    def _arquivo_suportado(self, arquivo: Path) -> bool:
        """
        Verifica se o arquivo é do tipo que sabemos processar.
        
        É como um filtro - só deixa passar o que interessa! 🔍
        """
        nome_arquivo = arquivo.name.lower()
        extensao = arquivo.suffix.lower()
        
        # Verificar se a extensão está na nossa lista
        for ext_suportada in self.config['EXTENSOES_SUPORTADAS']:
            if ext_suportada.startswith('.'):
                if extensao == ext_suportada.lower():
                    return True
            else:
                # Arquivos especiais sem extensão (tipo Dockerfile)
                if arquivo.name == ext_suportada:
                    return True
        
        return False
    
    def criar_corpus_rag(self) -> None:
        """
        Agora vamos criar o "cérebro" que vai entender seu código! 🧠
        
        É aqui que a mágica acontece - transformamos código em conhecimento.
        """
        try:
            print("🧠 Criando o cérebro da IA...")
            
            # Gerar um nome único
            id_unico = uuid.uuid4()
            nome_corpus = f"corpus-codigo-{id_unico}"
            
            self.corpus_rag = rag.create_corpus(
                display_name=nome_corpus,
                description=f"Conhecimento extraído do código em {self.config['CAMINHO_CODIGO']}",
                backend_config=rag.RagVectorDbConfig(
                    rag_embedding_model_config=rag.RagEmbeddingModelConfig(
                        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                            publisher_model=self.config['MODELO_EMBEDDING']
                        )
                    )
                )
            )
            
            print(f"✅ Cérebro criado: {self.corpus_rag.display_name}")
            
        except Exception as e:
            raise RuntimeError(f"😵 Erro ao criar o cérebro: {e}")
    
    def processar_arquivos(self) -> None:
        """
        Hora de ensinar a IA sobre seu código! 📚
        
        É como dar aulas particulares para a IA sobre seu projeto.
        """
        try:
            print("📚 Ensinando a IA sobre seu código...")
            
            # Montar o caminho dos arquivos no GCS
            pasta_gcs = self.config.get('PASTA_GCS', '').strip('/')
            bucket_uri = f"gs://{self.config['BUCKET_NAME']}"
            
            if pasta_gcs:
                caminho_importacao = f"{bucket_uri}/{pasta_gcs}/"
            else:
                caminho_importacao = f"{bucket_uri}/"
            
            print(f"📂 Lendo arquivos de: {caminho_importacao}")
            
            # Começar o processo de aprendizado
            resposta_importacao = rag.import_files(
                corpus_name=self.corpus_rag.name,
                paths=[caminho_importacao],
                transformation_config=rag.TransformationConfig(
                    chunking_config=rag.ChunkingConfig(
                        chunk_size=self.config.get('TAMANHO_PEDACO', 1024),
                        chunk_overlap=self.config.get('SOBREPOSICAO_PEDACO', 256)
                    )
                ),
            )
            
            print("✅ Processo de aprendizado iniciado!")
            print("⏳ Isso pode demorar alguns minutos... A IA está estudando seu código!")
            
        except Exception as e:
            raise RuntimeError(f"😵 Erro no processo de aprendizado: {e}")
    
    def criar_ferramenta_busca(self) -> None:
        """
        Criando a ferramenta que permite à IA buscar informações no seu código! 🔧
        
        É como dar uma lupa super poderosa para a IA.
        """
        try:
            print("🔧 Criando ferramenta de busca inteligente...")
            
            self.ferramenta_busca = Tool(
                retrieval=Retrieval(
                    vertex_rag_store=VertexRagStore(
                        rag_corpora=[self.corpus_rag.name],
                        similarity_top_k=self.config.get('TOP_RESULTADOS', 10),
                        vector_distance_threshold=self.config.get('LIMITE_SIMILARIDADE', 0.5),
                    )
                )
            )
            
            print("✅ Ferramenta de busca pronta!")
            
        except Exception as e:
            raise RuntimeError(f"😵 Erro ao criar ferramenta de busca: {e}")
    
    def perguntar(self, pergunta: str) -> str:
        """
        Agora você pode conversar com seu código! 💬
        
        Faça qualquer pergunta sobre seu projeto e a IA vai responder
        baseada no conhecimento que ela adquiriu.
        
        Args:
            pergunta: Sua pergunta sobre o código
            
        Returns:
            A resposta da IA
        """
        try:
            if not self.ferramenta_busca:
                raise RuntimeError("Ops! A ferramenta de busca não foi criada ainda. Execute criar_ferramenta_busca() primeiro!")
            
            print(f"🤔 Pensando na sua pergunta: '{pergunta}'")
            
            resposta = self.cliente_ia.models.generate_content(
                model=self.config['MODELO_IA'],
                contents=pergunta,
                config=GenerateContentConfig(tools=[self.ferramenta_busca]),
            )
            
            return resposta.text
            
        except Exception as e:
            raise RuntimeError(f"😵 Erro ao processar sua pergunta: {e}")
    
    def gerar_link_studio(self) -> str:
        """
        Gera um link direto para testar no Vertex AI Studio! 🌐
        
        É como ter um playground online para brincar com a IA.
        """
        if not self.corpus_rag:
            raise RuntimeError("Corpus RAG não foi criado ainda!")
        
        # Codificar o nome para URL
        nome_codificado = self.corpus_rag.name.replace("/", "%2F")
        
        # Montar a URL
        url_studio = (
            f"https://console.cloud.google.com/vertex-ai/studio/multimodal"
            f";ragCorpusName={nome_codificado}"
            f"?project={self.config['PROJECT_ID']}"
        )
        
        return url_studio
    
    def limpar_recursos(self) -> None:
        """
        Remove os recursos criados para não gerar custos desnecessários! 🗑️
        
        ⚠️ Cuidado: isso vai apagar permanentemente o conhecimento da IA!
        """
        try:
            if self.corpus_rag:
                print("🗑️ Removendo recursos...")
                rag.delete_corpus(self.corpus_rag.name)
                print(f"✅ Corpus {self.corpus_rag.name} removido com sucesso!")
                self.corpus_rag = None
            else:
                print("🤷 Não há recursos para remover.")
                
        except Exception as e:
            print(f"❌ Erro ao remover recursos: {e}")


def obter_configuracao_padrao() -> dict:
    """
    Aqui estão as configurações padrão! 📋
    
    Você só precisa alterar algumas coisinhas e já está pronto para usar!
    """
    return {
        # 🚨 IMPORTANTE: Você PRECISA alterar estes valores!
        'PROJECT_ID': "seu-projeto-aqui",  # Coloque o ID do seu projeto Google Cloud
        'BUCKET_NAME': "seu-bucket-aqui",  # Nome do seu bucket no Google Cloud Storage
        'CAMINHO_CODIGO': "./meu_codigo",  # Onde está seu código
        
        # Configurações do Google Cloud (pode deixar assim)
        'LOCATION': "us-central1",
        'PASTA_GCS': "codigo-para-analise",
        
        # Configurações de processamento
        'TAMANHO_MAX_MB': 10,  # Arquivos maiores que isso serão ignorados (0 = sem limite)
        
        # Modelos de IA (estes são bons, pode deixar)
        'MODELO_EMBEDDING': "publishers/google/models/text-embedding-005",
        'MODELO_IA': "gemini-2.5-flash",
        
        # Como dividir os arquivos para análise
        'TAMANHO_PEDACO': 1024,
        'SOBREPOSICAO_PEDACO': 256,
        
        # Configurações de busca
        'TOP_RESULTADOS': 10,
        'LIMITE_SIMILARIDADE': 0.5,
        
        # Tipos de arquivo que sabemos processar
        'EXTENSOES_SUPORTADAS': [
            # Linguagens de programação populares (existentes)
            ".py", ".java", ".js", ".ts", ".go", ".c", ".cpp", ".h", ".hpp",
            ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".rs", ".dart",
            
            # Linguagens funcionais e especializadas
            ".hs", ".elm", ".clj", ".cljs", ".ex", ".exs", ".erl", ".ml", ".fs",
            ".jl", ".r", ".R", ".lua", ".nim", ".zig", ".v", ".cr",
            
            # Web e frontend moderno
            ".vue", ".svelte", ".jsx", ".tsx", ".astro", ".liquid", ".hbs",
            ".mustache", ".ejs", ".pug", ".sass", ".less", ".styl",
            
            # Mobile
            ".xaml", ".storyboard", ".xib", ".plist", ".kts", ".aidl",
            
            # Data Science
            ".ipynb", ".rmd", ".qmd", ".sql", ".hql", ".pig",
            
            # Documentação e markup (existentes + novos)
            ".md", ".txt", ".rst", ".html", ".css", ".scss",
            ".adoc", ".tex", ".org", ".wiki",
            
            # Arquivos de configuração (existentes + novos)
            ".yaml", ".yml", ".json", ".xml", ".toml", ".ini", ".cfg",
            ".proto", "Dockerfile", ".sh", ".bat", ".ps1", ".hcl",
            ".avsc", ".jsonschema", ".graphql", ".gql", ".prisma",
            
            # Arquivos de build e dependências (existentes)
            ".tf", ".tfvars", ".bicep", ".gradle", "pom.xml", 
            "requirements.txt", "package.json", "go.mod", "go.sum", 
            "Cargo.toml", "Pipfile", "poetry.lock", "yarn.lock"
        ]
    }


def conversar_com_usuario():
    """
    Interface de chat amigável! 💬
    
    Aqui você pode fazer várias perguntas sobre seu código de forma natural.
    """
    print("\n🎯 Modo Conversa Ativado!")
    print("Agora você pode fazer perguntas sobre seu código. Digite 'sair' para terminar.\n")
    
    return input("💭 Sua pergunta: ").strip()


def main():
    """
    Função principal - é aqui que tudo acontece! 🚀
    """
    print("\n" + "="*60)
    print("🤖 Bem-vindo ao seu Assistente RAG de Código!")
    print("="*60)
    print("\nVou te ajudar a conversar com seu código usando IA! 🎉")
    
    # Pegar configurações
    config = obter_configuracao_padrao()
    
    # Verificar se o usuário configurou tudo
    if config['PROJECT_ID'] == "seu-projeto-aqui" or config['BUCKET_NAME'] == "seu-bucket-aqui":
        print("\n🚨 Opa! Você precisa configurar algumas coisas primeiro:")
        print("\n📝 Edite estas variáveis no código:")
        print(f"   • PROJECT_ID: '{config['PROJECT_ID']}'")
        print(f"   • BUCKET_NAME: '{config['BUCKET_NAME']}'")
        print(f"   • CAMINHO_CODIGO: '{config['CAMINHO_CODIGO']}'")
        print("\n💡 Depois é só rodar de novo!")
        return
    
    try:
        # Criar o assistente
        print("\n🔧 Inicializando seu assistente...")
        assistente = AssistenteRAG(config)
        
        # Verificar se conseguimos acessar o bucket
        if not assistente.verificar_bucket():
            print("\n❌ Não consegui acessar seu bucket. Verifique as configurações!")
            return
        
        # Enviar arquivos
        print("\n📤 Enviando seus arquivos para a nuvem...")
        enviados, ignorados = assistente.enviar_arquivos()
        
        if enviados == 0:
            print("\n❌ Nenhum arquivo foi enviado. Verifique o caminho e os tipos de arquivo!")
            return
        
        # Criar o cérebro da IA
        print("\n🧠 Criando a inteligência artificial...")
        assistente.criar_corpus_rag()
        
        # Ensinar a IA sobre o código
        print("\n📚 Ensinando a IA sobre seu código...")
        assistente.processar_arquivos()
        
        # Criar ferramenta de busca
        print("\n🔧 Preparando ferramentas de busca...")
        assistente.criar_ferramenta_busca()
        
        # Fazer uma pergunta de exemplo
        print("\n❓ Vou fazer uma pergunta de exemplo...")
        pergunta_exemplo = "Me explique o que este código faz de forma geral."
        resposta = assistente.perguntar(pergunta_exemplo)
        
        print(f"\n🤔 Pergunta: {pergunta_exemplo}")
        print(f"🤖 Resposta: {resposta}")
        
        # Mostrar link do Studio
        link_studio = assistente.gerar_link_studio()
        print(f"\n🌐 Quer testar no navegador? Acesse: {link_studio}")
        
        # Modo conversa
        while True:
            pergunta = conversar_com_usuario()
            
            if pergunta.lower() in ['sair', 'exit', 'quit', 'tchau']:
                print("\n👋 Tchau! Foi um prazer ajudar!")
                break
            
            if pergunta:
                try:
                    resposta = assistente.perguntar(pergunta)
                    print(f"\n🤖 {resposta}\n")
                except Exception as e:
                    print(f"\n❌ Ops, deu erro: {e}\n")
        
        # Perguntar sobre limpeza
        limpar = input("\n🗑️ Quer que eu remova os recursos criados? (s/N): ").lower().strip()
        if limpar in ['s', 'sim', 'y', 'yes']:
            assistente.limpar_recursos()
            print("\n✅ Recursos removidos! Até a próxima!")
        else:
            print("\n💡 Os recursos ficaram salvos. Você pode usar de novo depois!")
        
    except Exception as e:
        print(f"\n💥 Ops! Algo deu errado: {e}")
        print("\n🔧 Dicas para resolver:")
        print("   • Verifique suas configurações")
        print("   • Confirme se você tem permissões no Google Cloud")
        print("   • Tente rodar novamente")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())