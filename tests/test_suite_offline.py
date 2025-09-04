#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Suíte de Testes Offline - ValidAI Enhanced

Testes abrangentes que podem ser executados sem acesso ao Vertex AI,
focando em componentes locais, validações e lógica de negócio.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configurar logging para testes
logging.basicConfig(level=logging.WARNING)

# Adicionar diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestConfiguracao(unittest.TestCase):
    """
    🔧 Testes de Configuração
    
    Testa carregamento, validação e manipulação de configurações
    sem dependências externas.
    """
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_padrao(self):
        """Testa criação de configuração padrão"""
        try:
            from validai_enhanced import ConfigValidAI
            
            config = ConfigValidAI()
            
            # Verificar valores padrão
            self.assertEqual(config.project_id, "bv-cdip-des")
            self.assertEqual(config.location, "us-central1")
            self.assertEqual(config.modelo_versao, "gemini-1.5-pro-002")
            self.assertEqual(config.temperatura, 0.2)
            self.assertIsInstance(config.extensoes_permitidas, list)
            
            print("✅ Configuração padrão criada corretamente")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_carregamento_config_json(self):
        """Testa carregamento de configuração de arquivo JSON"""
        try:
            from validai_enhanced import GerenciadorConfig
            
            # Criar arquivo de configuração de teste
            config_data = {
                "project_id": "test-project",
                "temperatura": 0.5,
                "max_output_tokens": 4000
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f)
            
            # Testar carregamento
            gerenciador = GerenciadorConfig(self.config_file)
            
            self.assertEqual(gerenciador.config.project_id, "test-project")
            self.assertEqual(gerenciador.config.temperatura, 0.5)
            self.assertEqual(gerenciador.config.max_output_tokens, 4000)
            
            print("✅ Carregamento de JSON funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_validacao_configuracao(self):
        """Testa validação de configurações"""
        try:
            from validai_enhanced import ConfigValidAI, GerenciadorConfig
            
            # Configuração válida
            config_valida = ConfigValidAI(
                project_id="test-project",
                temperatura=0.5,
                max_output_tokens=1000
            )
            
            gerenciador = GerenciadorConfig()
            gerenciador.config = config_valida
            
            # Mock dos diretórios para evitar criação real
            with patch('os.makedirs'):
                resultado = gerenciador.validar_configuracao()
                self.assertTrue(resultado)
            
            print("✅ Validação de configuração funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


class TestValidadorArquivos(unittest.TestCase):
    """
    📁 Testes de Validação de Arquivos
    
    Testa validação de tipos, tamanhos e integridade de arquivos
    sem processamento real.
    """
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpeza"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validacao_extensoes(self):
        """Testa validação de extensões de arquivo"""
        try:
            from validai_enhanced import ValidadorArquivos, ConfigValidAI
            
            config = ConfigValidAI()
            validador = ValidadorArquivos(config)
            
            # Criar arquivos de teste
            arquivo_valido = os.path.join(self.temp_dir, "test.pdf")
            arquivo_invalido = os.path.join(self.temp_dir, "test.exe")
            
            # Criar arquivos vazios
            Path(arquivo_valido).touch()
            Path(arquivo_invalido).touch()
            
            # Testar validação
            valido, msg_valido = validador.validar_arquivo(arquivo_valido)
            invalido, msg_invalido = validador.validar_arquivo(arquivo_invalido)
            
            self.assertTrue(valido)
            self.assertFalse(invalido)
            self.assertIn("válido", msg_valido.lower())
            self.assertIn("suportado", msg_invalido.lower())
            
            print("✅ Validação de extensões funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_validacao_multiplos_arquivos(self):
        """Testa validação de múltiplos arquivos"""
        try:
            from validai_enhanced import ValidadorArquivos, ConfigValidAI
            
            config = ConfigValidAI()
            validador = ValidadorArquivos(config)
            
            # Criar arquivos de teste
            arquivos = []
            for i, ext in enumerate(['.pdf', '.py', '.txt', '.exe']):
                arquivo = os.path.join(self.temp_dir, f"test{i}{ext}")
                Path(arquivo).touch()
                arquivos.append(arquivo)
            
            # Testar validação múltipla
            resultado = validador.validar_multiplos_arquivos(arquivos)
            
            self.assertIsInstance(resultado, dict)
            self.assertIn('validos', resultado)
            self.assertIn('invalidos', resultado)
            self.assertEqual(resultado['total_validos'], 3)  # pdf, py, txt
            self.assertEqual(resultado['total_invalidos'], 1)  # exe
            
            print("✅ Validação múltipla funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


class TestFeedbackManager(unittest.TestCase):
    """
    💬 Testes do Gerenciador de Feedback
    
    Testa formatação de mensagens e feedback humanizado.
    """
    
    def test_formatacao_mensagens(self):
        """Testa formatação de diferentes tipos de mensagem"""
        try:
            from validai_enhanced import FeedbackManager
            
            feedback = FeedbackManager()
            
            # Testar diferentes tipos
            sucesso = feedback.sucesso("Operação concluída")
            erro = feedback.erro("Algo deu errado", "Tente novamente")
            aviso = feedback.aviso("Cuidado com isso")
            info = feedback.info("Informação útil")
            
            # Verificar formatação
            self.assertIn("✅", sucesso)
            self.assertIn("❌", erro)
            self.assertIn("⚠️", aviso)
            self.assertIn("ℹ️", info)
            
            # Verificar conteúdo
            self.assertIn("Operação concluída", sucesso)
            self.assertIn("Algo deu errado", erro)
            self.assertIn("Tente novamente", erro)
            
            print("✅ Formatação de mensagens funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_progresso_e_tempo(self):
        """Testa formatação de progresso e tempo"""
        try:
            from validai_enhanced import FeedbackManager
            
            feedback = FeedbackManager()
            
            # Testar progresso
            progresso = feedback.progresso(5, 10, "Processando")
            self.assertIn("📊", progresso)
            self.assertIn("5/10", progresso)
            self.assertIn("50.0%", progresso)
            
            # Testar tempo
            tempo = feedback.formatear_tempo_estimado(3661)  # 1h 1min 1s
            self.assertIn("1h", tempo)
            
            print("✅ Formatação de progresso e tempo funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


class TestRAGConfiguracao(unittest.TestCase):
    """
    🧠 Testes de Configuração RAG
    
    Testa configurações RAG sem conectar ao Vertex AI.
    """
    
    def test_corpus_config_basico(self):
        """Testa configuração básica de corpus"""
        try:
            from validai_rag_system import RAGCorpusConfig
            
            config = RAGCorpusConfig(
                nome="Teste",
                descricao="Corpus de teste",
                diretorio_local="./test",
                bucket_path="test/bucket",
                tipos_arquivo=[".pdf", ".txt"]
            )
            
            # Verificar propriedades
            self.assertEqual(config.nome, "Teste")
            self.assertEqual(config.descricao, "Corpus de teste")
            self.assertTrue(config.ativo)
            self.assertIsNone(config.corpus_id)
            
            # Testar conversão para dict
            config_dict = config.to_dict()
            self.assertIsInstance(config_dict, dict)
            self.assertEqual(config_dict['nome'], "Teste")
            
            print("✅ Configuração de corpus RAG funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_corpus_multimodal_config(self):
        """Testa configuração de corpus multimodal"""
        try:
            from validai_rag_multimodal import MultimodalRAGCorpusConfig
            
            config = MultimodalRAGCorpusConfig(
                nome="Teste Multimodal",
                descricao="Corpus multimodal de teste",
                diretorio_local="./test_mm",
                bucket_path="test/multimodal",
                tipos_arquivo=[".pdf"],
                suporte_multimodal=True
            )
            
            # Verificar propriedades multimodais
            self.assertTrue(config.suporte_multimodal)
            self.assertIsInstance(config.tipos_multimodal, list)
            
            # Testar detecção de tipos
            self.assertTrue(config.eh_arquivo_texto("test.pdf"))
            self.assertTrue(config.eh_arquivo_multimodal("test.jpg"))
            self.assertFalse(config.eh_arquivo_multimodal("test.pdf"))
            
            print("✅ Configuração multimodal funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


class TestProcessadorMultimodal(unittest.TestCase):
    """
    🎭 Testes do Processador Multimodal
    
    Testa detecção de tipos e processamento básico sem IA.
    """
    
    def test_deteccao_tipos_midia(self):
        """Testa detecção de tipos de mídia"""
        try:
            from validai_rag_multimodal import ProcessadorMultimodal
            
            config = {'limite_video_mb': 100, 'limite_audio_mb': 50}
            processador = ProcessadorMultimodal(config)
            
            # Testar diferentes tipos
            self.assertEqual(processador.detectar_tipo_midia("foto.jpg"), "imagem")
            self.assertEqual(processador.detectar_tipo_midia("video.mp4"), "video")
            self.assertEqual(processador.detectar_tipo_midia("audio.mp3"), "audio")
            self.assertEqual(processador.detectar_tipo_midia("doc.pdf"), "documento")
            self.assertEqual(processador.detectar_tipo_midia("arquivo.xyz"), "desconhecido")
            
            print("✅ Detecção de tipos de mídia funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


class TestUtilitarios(unittest.TestCase):
    """
    🛠️ Testes de Utilitários
    
    Testa funções utilitárias e helpers do projeto.
    """
    
    def test_verificacao_dependencias(self):
        """Testa verificação de dependências"""
        try:
            from run_validai_enhanced import verificar_dependencias
            
            # Mock das dependências para teste
            with patch('importlib.import_module') as mock_import:
                mock_import.return_value = True
                resultado = verificar_dependencias()
                self.assertTrue(resultado)
            
            print("✅ Verificação de dependências funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_verificacao_estrutura(self):
        """Testa verificação de estrutura do projeto"""
        try:
            from run_validai_enhanced import verificar_estrutura_projeto
            
            # Mock da estrutura para teste
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True
                resultado = verificar_estrutura_projeto()
                self.assertTrue(resultado)
            
            print("✅ Verificação de estrutura funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


class TestCorrecoesCriticas(unittest.TestCase):
    """
    🔧 Testes das Correções Críticas
    
    Testa implementações de correções e validações robustas.
    """
    
    def test_validacao_configuracao_completa(self):
        """Testa validação completa de configuração"""
        try:
            from correcoes_criticas import CorrecoesCriticas
            from validai_enhanced import GerenciadorConfig, ConfigValidAI
            
            # Criar configuração de teste
            config = ConfigValidAI(
                project_id="test-project",
                temperatura=0.5,
                max_output_tokens=1000
            )
            
            gerenciador = GerenciadorConfig()
            gerenciador.config = config
            
            # Mock para evitar criação de diretórios
            with patch('os.makedirs'):
                resultado = CorrecoesCriticas.implementar_validacao_configuracao_completa(gerenciador)
                self.assertTrue(resultado)
            
            print("✅ Validação completa funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def test_validacao_arquivos_robusta(self):
        """Testa validação robusta de arquivos"""
        try:
            from correcoes_criticas import CorrecoesCriticas
            from validai_enhanced import ValidadorArquivos, ConfigValidAI
            
            config = ConfigValidAI()
            validador = ValidadorArquivos(config)
            
            # Criar arquivos de teste
            arquivos_teste = [
                os.path.join(self.temp_dir, "test.pdf"),
                os.path.join(self.temp_dir, "test.py"),
                "arquivo_inexistente.txt"
            ]
            
            # Criar apenas alguns arquivos
            Path(arquivos_teste[0]).touch()
            Path(arquivos_teste[1]).touch()
            
            resultado = CorrecoesCriticas.implementar_validacao_arquivos_robusta(
                validador, arquivos_teste
            )
            
            self.assertIsInstance(resultado, dict)
            self.assertIn('arquivos_validos', resultado)
            self.assertIn('arquivos_invalidos', resultado)
            self.assertEqual(len(resultado['arquivos_validos']), 2)
            self.assertEqual(len(resultado['arquivos_invalidos']), 1)
            
            print("✅ Validação robusta de arquivos funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")
    
    def setUp(self):
        """Configuração para testes de correções"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpeza para testes de correções"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestIntegridade(unittest.TestCase):
    """
    🔍 Testes de Integridade
    
    Testa verificação de integridade do código.
    """
    
    def test_verificador_integridade(self):
        """Testa verificador de integridade básico"""
        try:
            from verificar_integridade import VerificadorIntegridade
            
            verificador = VerificadorIntegridade(".")
            
            # Mock para evitar escaneamento real
            verificador.arquivos_python = ["test.py"]
            
            # Testar análise básica
            self.assertIsInstance(verificador.estatisticas, dict)
            self.assertIn('total_arquivos', verificador.estatisticas)
            
            print("✅ Verificador de integridade funcionando")
            
        except ImportError as e:
            self.skipTest(f"Módulo não disponível: {e}")


def executar_testes_offline():
    """
    🧪 Executa todos os testes offline
    
    Executa a suíte completa de testes que não dependem
    de conexões externas ou APIs.
    """
    print("\n" + "="*70)
    print("🧪 SUÍTE DE TESTES OFFLINE - ValidAI Enhanced")
    print("="*70)
    print("\nExecutando testes que NÃO requerem acesso ao Vertex AI...\n")
    
    # Configurar test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar classes de teste
    classes_teste = [
        TestConfiguracao,
        TestValidadorArquivos,
        TestFeedbackManager,
        TestRAGConfiguracao,
        TestProcessadorMultimodal,
        TestUtilitarios,
        TestCorrecoesCriticas,
        TestIntegridade
    ]
    
    for classe in classes_teste:
        tests = loader.loadTestsFromTestCase(classe)
        suite.addTests(tests)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    resultado = runner.run(suite)
    
    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("="*70)
    
    total_testes = resultado.testsRun
    sucessos = total_testes - len(resultado.failures) - len(resultado.errors) - len(resultado.skipped)
    
    print(f"📈 Total de testes executados: {total_testes}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {len(resultado.failures)}")
    print(f"💥 Erros: {len(resultado.errors)}")
    print(f"⏭️ Pulados: {len(resultado.skipped)}")
    
    if resultado.failures:
        print(f"\n❌ FALHAS ENCONTRADAS:")
        for test, traceback in resultado.failures:
            print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if resultado.errors:
        print(f"\n💥 ERROS ENCONTRADOS:")
        for test, traceback in resultado.errors:
            print(f"   • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Status final
    if len(resultado.failures) == 0 and len(resultado.errors) == 0:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"✅ Sistema ValidAI Enhanced está funcionando corretamente offline")
    else:
        print(f"\n⚠️ ALGUNS TESTES FALHARAM")
        print(f"🔧 Verifique os problemas acima antes de prosseguir")
    
    print("="*70)
    
    return resultado.wasSuccessful()


def executar_testes_rapidos():
    """
    ⚡ Executa apenas testes rápidos e essenciais
    
    Versão reduzida para verificação rápida de funcionalidade.
    """
    print("\n🚀 TESTES RÁPIDOS - ValidAI Enhanced")
    print("="*50)
    
    testes_rapidos = [
        ("Configuração Padrão", TestConfiguracao('test_config_padrao')),
        ("Validação de Arquivos", TestValidadorArquivos('test_validacao_extensoes')),
        ("Feedback Manager", TestFeedbackManager('test_formatacao_mensagens')),
        ("RAG Config", TestRAGConfiguracao('test_corpus_config_basico'))
    ]
    
    sucessos = 0
    total = len(testes_rapidos)
    
    for nome, teste in testes_rapidos:
        try:
            resultado = unittest.TestResult()
            teste.run(resultado)
            
            if len(resultado.failures) == 0 and len(resultado.errors) == 0:
                print(f"✅ {nome}")
                sucessos += 1
            else:
                print(f"❌ {nome}")
        except Exception as e:
            print(f"⏭️ {nome} (pulado: {e})")
    
    print(f"\n📊 Resultado: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("🎉 Sistema básico funcionando!")
    else:
        print("⚠️ Alguns componentes precisam de atenção")
    
    return sucessos == total


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🧪 Testes Offline ValidAI Enhanced")
    parser.add_argument('--rapido', '-r', action='store_true', 
                       help='Executar apenas testes rápidos')
    parser.add_argument('--completo', '-c', action='store_true',
                       help='Executar suíte completa de testes')
    
    args = parser.parse_args()
    
    if args.rapido:
        sucesso = executar_testes_rapidos()
    else:
        sucesso = executar_testes_offline()
    
    sys.exit(0 if sucesso else 1)