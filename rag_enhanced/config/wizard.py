#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙 Setup Wizard - Wizard interativo de configuração

Este módulo fornece um wizard passo-a-passo para configurar o sistema
de forma amigável, com validação em tempo real e sugestões inteligentes.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from ..core.models import RAGConfig, ValidationResult
from ..core.exceptions import ConfigurationError
from .validator import ConfigValidator


class SetupWizard:
    """
    🧙 Wizard interativo de configuração
    
    Guia o usuário através do processo de configuração com
    validação em tempo real e sugestões contextuais.
    """
    
    def __init__(self, config_manager):
        """
        Inicializa o wizard
        
        Args:
            config_manager: Instância do gerenciador de configuração
        """
        self.config_manager = config_manager
        self.validator = ConfigValidator()
        
        # Estado do wizard
        self.current_config = {}
        self.step_history = []
    
    def run_wizard(self) -> RAGConfig:
        """
        Executa o wizard completo de configuração
        
        Returns:
            Configuração criada pelo wizard
        """
        print("\n" + "="*70)
        print("🧙 Bem-vindo ao Wizard de Configuração RAG Enhanced!")
        print("="*70)
        print("\nVou te ajudar a configurar o sistema passo a passo.")
        print("Você pode digitar 'voltar' para retornar ao passo anterior,")
        print("ou 'sair' para cancelar a configuração.\n")
        
        try:
            # Detectar configuração existente
            self._detect_existing_config()
            
            # Executar passos do wizard
            self._step_welcome()
            self._step_google_cloud_project()
            self._step_bucket_configuration()
            self._step_codebase_path()
            self._step_processing_settings()
            self._step_ai_models()
            self._step_advanced_settings()
            self._step_validation()
            self._step_save_profile()
            
            # Criar configuração final
            config = self._create_final_config()
            
            print("\n🎉 Configuração concluída com sucesso!")
            print("Você pode começar a usar o sistema agora.")
            
            return config
            
        except KeyboardInterrupt:
            print("\n\n❌ Configuração cancelada pelo usuário.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Erro durante configuração: {str(e)}")
            sys.exit(1)
    
    def _detect_existing_config(self) -> None:
        """Detecta configurações existentes"""
        try:
            # Tentar auto-detecção
            auto_config = self.config_manager.auto_detect_config()
            if auto_config:
                print("🔍 Detectei algumas configurações automaticamente:")
                if auto_config.project_id != "seu-projeto-aqui":
                    print(f"   📋 Projeto Google Cloud: {auto_config.project_id}")
                    self.current_config["project_id"] = auto_config.project_id
                
                if auto_config.codebase_path != Path("."):
                    print(f"   📁 Base de código: {auto_config.codebase_path}")
                    self.current_config["codebase_path"] = str(auto_config.codebase_path)
                
                print()
            
            # Verificar perfis existentes
            profiles = self.config_manager.list_profiles()
            if profiles:
                print(f"📋 Encontrei {len(profiles)} perfil(is) existente(s): {', '.join(profiles)}")
                
                if self._ask_yes_no("Deseja carregar um perfil existente como base?"):
                    profile_name = self._select_from_list("Selecione o perfil:", profiles)
                    if profile_name:
                        try:
                            existing_config = self.config_manager.get_config(profile_name)
                            self._load_from_existing_config(existing_config)
                            print(f"✅ Configuração carregada do perfil '{profile_name}'")
                        except Exception as e:
                            print(f"⚠️ Erro ao carregar perfil: {e}")
                
                print()
        
        except Exception:
            pass  # Falha silenciosa na detecção
    
    def _step_welcome(self) -> None:
        """Passo de boas-vindas"""
        print("📋 Vamos configurar seu sistema RAG Enhanced!")
        print("\nEste wizard vai configurar:")
        print("   🔧 Conexão com Google Cloud")
        print("   📁 Localização da sua base de código")
        print("   🤖 Modelos de IA para análise")
        print("   ⚙️ Configurações de processamento")
        
        if not self._ask_yes_no("\nDeseja continuar?", default=True):
            print("❌ Configuração cancelada.")
            sys.exit(0)
        
        print()
    
    def _step_google_cloud_project(self) -> None:
        """Configuração do projeto Google Cloud"""
        print("🔧 Configuração do Google Cloud")
        print("="*40)
        
        # Project ID
        current_project = self.current_config.get("project_id", "")
        if current_project and current_project != "seu-projeto-aqui":
            print(f"📋 Projeto detectado: {current_project}")
            if self._ask_yes_no("Usar este projeto?", default=True):
                self.current_config["project_id"] = current_project
            else:
                self.current_config["project_id"] = self._ask_project_id()
        else:
            self.current_config["project_id"] = self._ask_project_id()
        
        # Location
        print("\n🌍 Região do Google Cloud:")
        print("Recomendado: us-central1 (melhor suporte e preços)")
        
        location = self._ask_input(
            "Região", 
            default="us-central1",
            validator=self._validate_location
        )
        self.current_config["location"] = location
        
        print()
    
    def _step_bucket_configuration(self) -> None:
        """Configuração do bucket"""
        print("🪣 Configuração do Google Cloud Storage")
        print("="*40)
        
        project_id = self.current_config["project_id"]
        
        # Sugerir nome do bucket
        suggested_bucket = f"{project_id}-rag-codebase"
        
        print(f"📦 Vou criar/usar um bucket para armazenar seus arquivos.")
        print(f"Sugestão: {suggested_bucket}")
        
        bucket_name = self._ask_input(
            "Nome do bucket",
            default=suggested_bucket,
            validator=self._validate_bucket_name
        )
        
        self.current_config["bucket_name"] = bucket_name
        
        # Verificar se bucket existe
        print("\n🔍 Verificando acesso ao bucket...")
        if self._test_bucket_access(project_id, bucket_name):
            print("✅ Bucket acessível!")
        else:
            print("⚠️ Bucket não encontrado ou sem acesso.")
            print("💡 O sistema tentará criar o bucket automaticamente.")
        
        print()
    
    def _step_codebase_path(self) -> None:
        """Configuração do caminho da base de código"""
        print("📁 Localização da Base de Código")
        print("="*40)
        
        current_path = self.current_config.get("codebase_path", ".")
        
        print("📂 Onde está localizada sua base de código?")
        print("Pode ser um diretório local com seus arquivos de código.")
        
        while True:
            path_str = self._ask_input(
                "Caminho da base de código",
                default=current_path
            )
            
            path = Path(path_str)
            
            if not path.exists():
                print(f"❌ Caminho não existe: {path}")
                if not self._ask_yes_no("Tentar outro caminho?", default=True):
                    break
                continue
            
            if not path.is_dir():
                print(f"❌ Caminho não é um diretório: {path}")
                if not self._ask_yes_no("Tentar outro caminho?", default=True):
                    break
                continue
            
            # Analisar arquivos no diretório
            analysis = self._analyze_codebase(path)
            print(f"\n📊 Análise do diretório:")
            print(f"   📄 Total de arquivos: {analysis['total_files']}")
            print(f"   ✅ Arquivos suportados: {analysis['supported_files']}")
            print(f"   🔤 Linguagens encontradas: {', '.join(analysis['languages'][:5])}")
            
            if analysis['supported_files'] == 0:
                print("⚠️ Nenhum arquivo suportado encontrado.")
                if not self._ask_yes_no("Usar este diretório mesmo assim?"):
                    continue
            
            self.current_config["codebase_path"] = str(path)
            break
        
        print()
    
    def _step_processing_settings(self) -> None:
        """Configurações de processamento"""
        print("⚙️ Configurações de Processamento")
        print("="*40)
        
        # Tamanho máximo de arquivo
        print("📏 Tamanho máximo de arquivo:")
        print("Arquivos maiores que este limite serão ignorados.")
        
        max_size = self._ask_number(
            "Tamanho máximo (MB)",
            default=10,
            min_val=1,
            max_val=100
        )
        self.current_config["max_file_size_mb"] = max_size
        
        # Uploads paralelos
        print("\n🚀 Uploads paralelos:")
        print("Mais uploads paralelos = mais rápido, mas usa mais rede.")
        
        parallel = self._ask_number(
            "Número de uploads paralelos",
            default=5,
            min_val=1,
            max_val=20
        )
        self.current_config["parallel_uploads"] = parallel
        
        print()
    
    def _step_ai_models(self) -> None:
        """Configuração dos modelos de IA"""
        print("🤖 Modelos de Inteligência Artificial")
        print("="*40)
        
        # Modelo de geração
        print("🧠 Modelo de geração (para responder perguntas):")
        generation_models = [
            ("gemini-2.5-flash", "Mais rápido e econômico (recomendado)"),
            ("gemini-1.5-pro-002", "Mais poderoso, mas mais caro"),
            ("gemini-1.5-flash-002", "Balanceado")
        ]
        
        print("Opções disponíveis:")
        for i, (model, desc) in enumerate(generation_models, 1):
            print(f"   {i}. {model} - {desc}")
        
        choice = self._ask_number(
            "Escolha o modelo",
            default=1,
            min_val=1,
            max_val=len(generation_models)
        )
        
        self.current_config["generation_model"] = generation_models[choice-1][0]
        
        # Temperatura
        print(f"\n🌡️ Temperatura do modelo:")
        print("0.1 = Mais determinístico, 1.0 = Mais criativo")
        
        temperature = self._ask_number(
            "Temperatura",
            default=0.2,
            min_val=0.0,
            max_val=2.0,
            is_float=True
        )
        self.current_config["temperature"] = temperature
        
        print()
    
    def _step_advanced_settings(self) -> None:
        """Configurações avançadas"""
        print("🔧 Configurações Avançadas")
        print("="*40)
        
        if not self._ask_yes_no("Deseja configurar opções avançadas?"):
            return
        
        # Chunk size
        print("\n📄 Tamanho dos chunks (pedaços de texto):")
        chunk_size = self._ask_number(
            "Tamanho do chunk",
            default=1024,
            min_val=256,
            max_val=4096
        )
        self.current_config["chunk_size"] = chunk_size
        
        # Chunk overlap
        overlap = self._ask_number(
            "Sobreposição entre chunks",
            default=256,
            min_val=0,
            max_val=chunk_size // 2
        )
        self.current_config["chunk_overlap"] = overlap
        
        # Max output tokens
        print("\n💬 Tamanho máximo das respostas:")
        max_tokens = self._ask_number(
            "Máximo de tokens de saída",
            default=8000,
            min_val=1000,
            max_val=32000
        )
        self.current_config["max_output_tokens"] = max_tokens
        
        print()
    
    def _step_validation(self) -> None:
        """Validação da configuração"""
        print("✅ Validação da Configuração")
        print("="*40)
        
        # Criar configuração temporária para validação
        temp_config = self._create_temp_config()
        
        print("🔍 Validando configuração...")
        validation = self.validator.validate_config(temp_config, check_connectivity=True)
        
        if validation.is_valid:
            print("✅ Configuração válida!")
        else:
            print("⚠️ Problemas encontrados:")
            print(validation.get_error_summary())
            
            if not self._ask_yes_no("\nDeseja continuar mesmo assim?"):
                print("Voltando para corrigir configurações...")
                # Aqui poderia implementar lógica para voltar aos passos
                raise ConfigurationError(
                    field="validation",
                    message="Configuração cancelada pelo usuário",
                    suggestion="Execute o wizard novamente"
                )
        
        print()
    
    def _step_save_profile(self) -> None:
        """Salvar perfil de configuração"""
        print("💾 Salvar Configuração")
        print("="*40)
        
        profiles = self.config_manager.list_profiles()
        
        if "default" in profiles:
            print("⚠️ Já existe um perfil 'default'.")
            if self._ask_yes_no("Sobrescrever o perfil default?", default=True):
                profile_name = "default"
            else:
                profile_name = self._ask_input("Nome do novo perfil", default="meu-perfil")
        else:
            profile_name = "default"
            print(f"💾 Salvando como perfil '{profile_name}'")
        
        self.current_config["profile_name"] = profile_name
        
        print()
    
    def _create_final_config(self) -> RAGConfig:
        """Cria a configuração final"""
        config_dict = {
            "project_id": self.current_config["project_id"],
            "bucket_name": self.current_config["bucket_name"],
            "location": self.current_config.get("location", "us-central1"),
            "codebase_path": Path(self.current_config["codebase_path"]),
            "max_file_size_mb": self.current_config.get("max_file_size_mb", 10),
            "parallel_uploads": self.current_config.get("parallel_uploads", 5),
            "generation_model": self.current_config.get("generation_model", "gemini-2.5-flash"),
            "temperature": self.current_config.get("temperature", 0.2),
            "chunk_size": self.current_config.get("chunk_size", 1024),
            "chunk_overlap": self.current_config.get("chunk_overlap", 256),
            "max_output_tokens": self.current_config.get("max_output_tokens", 8000)
        }
        
        config = RAGConfig(**config_dict)
        
        # Salvar perfil
        profile_name = self.current_config.get("profile_name", "default")
        self.config_manager.save_config(config, profile_name)
        
        return config
    
    def _create_temp_config(self) -> RAGConfig:
        """Cria configuração temporária para validação"""
        return RAGConfig(
            project_id=self.current_config["project_id"],
            bucket_name=self.current_config["bucket_name"],
            location=self.current_config.get("location", "us-central1"),
            codebase_path=Path(self.current_config["codebase_path"])
        )
    
    def _ask_input(self, prompt: str, default: str = "", validator=None) -> str:
        """Solicita entrada do usuário com validação"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            try:
                response = input(full_prompt).strip()
                
                if response.lower() == "sair":
                    print("❌ Configuração cancelada.")
                    sys.exit(0)
                
                if response.lower() == "voltar":
                    # Implementar lógica de voltar
                    continue
                
                if not response and default:
                    response = default
                
                if not response:
                    print("❌ Este campo é obrigatório.")
                    continue
                
                if validator:
                    is_valid, message = validator(response)
                    if not is_valid:
                        print(f"❌ {message}")
                        continue
                
                return response
                
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Configuração cancelada.")
                sys.exit(0)
    
    def _ask_yes_no(self, prompt: str, default: bool = None) -> bool:
        """Solicita resposta sim/não"""
        if default is True:
            options = "[S/n]"
        elif default is False:
            options = "[s/N]"
        else:
            options = "[s/n]"
        
        while True:
            response = input(f"{prompt} {options}: ").strip().lower()
            
            if response in ["sair", "exit"]:
                sys.exit(0)
            
            if not response and default is not None:
                return default
            
            if response in ["s", "sim", "y", "yes"]:
                return True
            elif response in ["n", "não", "nao", "no"]:
                return False
            else:
                print("❌ Responda com 's' para sim ou 'n' para não.")
    
    def _ask_number(self, prompt: str, default: float, min_val: float = None, max_val: float = None, is_float: bool = False) -> float:
        """Solicita número do usuário"""
        while True:
            response = self._ask_input(prompt, str(default))
            
            try:
                if is_float:
                    value = float(response)
                else:
                    value = int(response)
                
                if min_val is not None and value < min_val:
                    print(f"❌ Valor deve ser maior ou igual a {min_val}")
                    continue
                
                if max_val is not None and value > max_val:
                    print(f"❌ Valor deve ser menor ou igual a {max_val}")
                    continue
                
                return value
                
            except ValueError:
                print("❌ Digite um número válido.")
    
    def _select_from_list(self, prompt: str, options: List[str]) -> Optional[str]:
        """Permite seleção de uma lista"""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"   {i}. {option}")
        
        while True:
            try:
                choice = self._ask_number("Escolha", 1, 1, len(options))
                return options[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Escolha inválida.")
    
    def _ask_project_id(self) -> str:
        """Solicita Project ID com validação"""
        print("\n📋 ID do Projeto Google Cloud:")
        print("Exemplo: meu-projeto-123")
        print("💡 Você pode encontrar no console: https://console.cloud.google.com")
        
        return self._ask_input(
            "Project ID",
            validator=self._validate_project_id
        )
    
    def _validate_project_id(self, project_id: str) -> Tuple[bool, str]:
        """Valida Project ID"""
        if not project_id or project_id in ["seu-projeto-aqui", "your-project-here"]:
            return False, "Digite o ID real do seu projeto"
        
        if not self.validator._is_valid_project_id(project_id):
            return False, "Project ID deve ter 6-30 caracteres, começar com letra, apenas letras minúsculas, números e hífens"
        
        return True, ""
    
    def _validate_bucket_name(self, bucket_name: str) -> Tuple[bool, str]:
        """Valida nome do bucket"""
        if not bucket_name or bucket_name in ["seu-bucket-aqui", "your-bucket-here"]:
            return False, "Digite o nome real do bucket"
        
        if not self.validator._is_valid_bucket_name(bucket_name):
            return False, "Nome do bucket deve ter 3-63 caracteres, apenas letras minúsculas, números, hífens e underscores"
        
        return True, ""
    
    def _validate_location(self, location: str) -> Tuple[bool, str]:
        """Valida location"""
        valid_locations = self.validator._get_valid_locations()
        if location not in valid_locations:
            return False, f"Location deve ser uma das: {', '.join(valid_locations[:5])}..."
        
        return True, ""
    
    def _test_bucket_access(self, project_id: str, bucket_name: str) -> bool:
        """Testa acesso ao bucket"""
        return self.validator._check_bucket_access(project_id, bucket_name)
    
    def _analyze_codebase(self, path: Path) -> Dict[str, Any]:
        """Analisa base de código"""
        total_files = 0
        supported_files = 0
        languages = set()
        
        # Extensões suportadas padrão
        supported_extensions = [
            ".py", ".java", ".js", ".ts", ".go", ".c", ".cpp", ".h", ".hpp",
            ".cs", ".rb", ".php", ".swift", ".kt", ".scala", ".rs", ".dart",
            ".md", ".txt", ".rst", ".html", ".css", ".scss", ".json", ".yaml", ".yml"
        ]
        
        # Mapeamento de extensões para linguagens
        ext_to_lang = {
            ".py": "Python", ".java": "Java", ".js": "JavaScript", ".ts": "TypeScript",
            ".go": "Go", ".c": "C", ".cpp": "C++", ".cs": "C#", ".rb": "Ruby",
            ".php": "PHP", ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
            ".rs": "Rust", ".dart": "Dart", ".md": "Markdown", ".html": "HTML",
            ".css": "CSS", ".scss": "SCSS", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML"
        }
        
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    
                    ext = file_path.suffix.lower()
                    if ext in supported_extensions:
                        supported_files += 1
                        if ext in ext_to_lang:
                            languages.add(ext_to_lang[ext])
                    
                    # Limitar análise para não demorar muito
                    if total_files > 1000:
                        break
        
        except Exception:
            pass
        
        return {
            "total_files": total_files,
            "supported_files": supported_files,
            "languages": sorted(list(languages))
        }
    
    def _load_from_existing_config(self, config: RAGConfig) -> None:
        """Carrega configuração existente"""
        self.current_config.update({
            "project_id": config.project_id,
            "bucket_name": config.bucket_name,
            "location": config.location,
            "codebase_path": str(config.codebase_path),
            "max_file_size_mb": config.max_file_size_mb,
            "parallel_uploads": config.parallel_uploads,
            "generation_model": config.generation_model,
            "temperature": config.temperature,
            "chunk_size": config.chunk_size,
            "chunk_overlap": config.chunk_overlap,
            "max_output_tokens": config.max_output_tokens
        })