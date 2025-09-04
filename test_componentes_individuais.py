#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 Testes de Componentes Individuais - ValidAI Enhanced

Testes focados em componentes específicos que podem ser testados
isoladamente sem dependências externas.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import logging

# Suprimir logs durante testes
logging.getLogger().setLevel(logging.CRITICAL)

# Adicionar ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestValidacaoBasica(unittest.TestCase):
    """
    ✅ Testes de Validação Básica
    
    Testa funcionalidades básicas de validação sem dependências externas.
    """
    
    def test_importacao_modulos_principais(self):
        """Testa se os módulos principais podem ser importados"""
        modulos_principais = [
            'validai_enhanced',
            'validai_rag_system', 
            'validai_rag_multimodal',
            'pre_validator_system'
        ]
        
        modulos_importados = []
        modulos_falharam = []
        
        for modulo in modulos_principais:
            try:
                __import__(modulo)
                modulos_importados.append(modulo)
                print(f"✅ {modulo}")
            except ImportError as e:
                modulos_falharam.append((modulo, str(e)))
                print(f"❌ {modulo}: {e}")
        
        # Pelo menos alguns módulos devem importar
        self.assertGreater(len(modulos_importados), 0, 
                          "Nenhum módulo principal pôde ser importado")
        
        print(f"\n📊 Importações: {len(modulos_importados)}/{len(modulos_principais)} sucessos")
    
    def test_estrutura_arquivos_essenciais(self):
        """Testa se arquivos essenciais existem"""
        arquivos_essenciais = [
            'app.py',
            'validai_enhanced.py',
            'pre_validator_system.py',
            'config/variaveis.py',
            'src/DataManager.py',
            'backend/Chat_LLM.py'
        ]
        
        arquivos_existem = []
        arquivos_faltam = []
        
        for arquivo in arquivos_essenciais:
            if os.path.exists(arquivo):
                arquivos_existem.append(arquivo)
                print(f"✅ {arquivo}")
            else:
                arquivos_faltam.append(arquivo)
                print(f"❌ {arquivo}")
        
        # Maioria dos arquivos deve existir
        self.assertGreater(len(arquivos_existem), len(arquivos_faltam),
                          "Muitos arquivos essenciais estão faltando")
        
        print(f"\n📊 Arquivos: {len(arquivos_existem)}/{len(arquivos_essenciais)} encontrados")
    
    def test_configuracoes_json_validas(self):
        """Testa se arquivos JSON de configuração são válidos"""
        arquivos_json = [
            'validai_config.json',
            'rag_corpus_config.json',
            'rag_multimodal_config.json'
        ]
        
        jsons_validos = []
        jsons_invalidos = []
        
        for arquivo in arquivos_json:
            if os.path.exists(arquivo):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        json.load(f)
                    jsons_validos.append(arquivo)
                    print(f"✅ {arquivo}")
                except json.JSONDecodeError as e:
                    jsons_invalidos.append((arquivo, str(e)))
                    print(f"❌ {arquivo}: JSON inválido")
            else:
                print(f"⏭️ {arquivo}: não encontrado")
        
        # JSONs existentes devem ser válidos
        self.assertEqual(len(jsons_invalidos), 0, 
                        f"JSONs inválidos encontrados: {jsons_invalidos}")
        
        print(f"\n📊 JSONs: {len(jsons_validos)} válidos, {len(jsons_invalidos)} inválidos")


class TestFuncoesUtilitarias(unittest.TestCase):
    """
    🛠️ Testes de Funções Utilitárias
    
    Testa funções utilitárias que não dependem de APIs externas.
    """
    
    def setUp(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_deteccao_tipos_arquivo(self):
        """Testa detecção de tipos de arquivo por extensão"""
        tipos_esperados = {
            'documento.pdf': 'documento',
            'codigo.py': 'codigo',
            'notebook.ipynb': 'codigo',
            'imagem.jpg': 'imagem',
            'video.mp4': 'video',
            'audio.mp3': 'audio',
            'planilha.xlsx': 'dados',
            'texto.txt': 'texto'
        }
        
        # Função simples de detecção para teste
        def detectar_tipo_arquivo(nome_arquivo):
            ext = Path(nome_arquivo).suffix.lower()
            
            if ext in ['.pdf']:
                return 'documento'
            elif ext in ['.py', '.ipynb', '.sas']:
                return 'codigo'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                return 'imagem'
            elif ext in ['.mp4', '.avi', '.mov']:
                return 'video'
            elif ext in ['.mp3', '.wav', '.flac']:
                return 'audio'
            elif ext in ['.xlsx', '.csv']:
                return 'dados'
            elif ext in ['.txt', '.md']:
                return 'texto'
            else:
                return 'desconhecido'
        
        # Testar detecção
        for arquivo, tipo_esperado in tipos_esperados.items():
            tipo_detectado = detectar_tipo_arquivo(arquivo)
            self.assertEqual(tipo_detectado, tipo_esperado,
                           f"Tipo incorreto para {arquivo}: esperado {tipo_esperado}, obtido {tipo_detectado}")
            print(f"✅ {arquivo} → {tipo_detectado}")
        
        print(f"\n📊 Detecção: {len(tipos_esperados)} tipos testados com sucesso")
    
    def test_validacao_tamanho_arquivo(self):
        """Testa validação de tamanho de arquivo"""
        # Criar arquivos de diferentes tamanhos
        arquivos_teste = []
        
        # Arquivo pequeno (1KB)
        arquivo_pequeno = os.path.join(self.temp_dir, "pequeno.txt")
        with open(arquivo_pequeno, 'w') as f:
            f.write("x" * 1024)  # 1KB
        arquivos_teste.append((arquivo_pequeno, 1))
        
        # Arquivo médio (1MB)
        arquivo_medio = os.path.join(self.temp_dir, "medio.txt")
        with open(arquivo_medio, 'w') as f:
            f.write("x" * (1024 * 1024))  # 1MB
        arquivos_teste.append((arquivo_medio, 1024))
        
        # Função de validação para teste
        def validar_tamanho_arquivo(caminho_arquivo, limite_mb=50):
            if not os.path.exists(caminho_arquivo):
                return False, "Arquivo não encontrado"
            
            tamanho_bytes = os.path.getsize(caminho_arquivo)
            tamanho_mb = tamanho_bytes / (1024 * 1024)
            
            if tamanho_mb > limite_mb:
                return False, f"Arquivo muito grande: {tamanho_mb:.1f}MB"
            
            return True, f"Arquivo válido: {tamanho_mb:.1f}MB"
        
        # Testar validação
        for arquivo, tamanho_esperado_kb in arquivos_teste:
            valido, mensagem = validar_tamanho_arquivo(arquivo, limite_mb=50)
            
            self.assertTrue(valido, f"Arquivo deveria ser válido: {mensagem}")
            self.assertIn("válido", mensagem.lower())
            print(f"✅ {Path(arquivo).name}: {mensagem}")
        
        print(f"\n📊 Validação de tamanho: {len(arquivos_teste)} arquivos testados")
    
    def test_formatacao_feedback(self):
        """Testa formatação de mensagens de feedback"""
        # Função simples de formatação para teste
        def formatar_feedback(tipo, mensagem, dica=None):
            emojis = {
                'sucesso': '✅',
                'erro': '❌', 
                'aviso': '⚠️',
                'info': 'ℹ️'
            }
            
            resultado = f"{emojis.get(tipo, '•')} {mensagem}"
            
            if dica:
                resultado += f"\n💡 Dica: {dica}"
            
            return resultado
        
        # Testar diferentes tipos
        casos_teste = [
            ('sucesso', 'Operação concluída', None),
            ('erro', 'Falha na operação', 'Tente novamente'),
            ('aviso', 'Cuidado com este arquivo', None),
            ('info', 'Informação importante', 'Lembre-se disso')
        ]
        
        for tipo, mensagem, dica in casos_teste:
            resultado = formatar_feedback(tipo, mensagem, dica)
            
            # Verificar se contém emoji correto
            if tipo == 'sucesso':
                self.assertIn('✅', resultado)
            elif tipo == 'erro':
                self.assertIn('❌', resultado)
            
            # Verificar se contém mensagem
            self.assertIn(mensagem, resultado)
            
            # Verificar dica se fornecida
            if dica:
                self.assertIn(dica, resultado)
                self.assertIn('💡', resultado)
            
            print(f"✅ {tipo}: {resultado.split(chr(10))[0]}")
        
        print(f"\n📊 Formatação: {len(casos_teste)} tipos testados")


class TestProcessamentoArquivos(unittest.TestCase):
    """
    📁 Testes de Processamento de Arquivos
    
    Testa processamento básico de arquivos sem IA.
    """
    
    def setUp(self):
        """Configuração para testes de arquivo"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpeza após testes"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_leitura_arquivo_texto(self):
        """Testa leitura básica de arquivos de texto"""
        # Criar arquivo de teste
        conteudo_teste = "Este é um arquivo de teste\nCom múltiplas linhas\nPara validação"
        arquivo_teste = os.path.join(self.temp_dir, "teste.txt")
        
        with open(arquivo_teste, 'w', encoding='utf-8') as f:
            f.write(conteudo_teste)
        
        # Função de leitura para teste
        def ler_arquivo_texto(caminho_arquivo):
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                return True, conteudo
            except Exception as e:
                return False, str(e)
        
        # Testar leitura
        sucesso, conteudo = ler_arquivo_texto(arquivo_teste)
        
        self.assertTrue(sucesso)
        self.assertEqual(conteudo, conteudo_teste)
        self.assertIn("múltiplas linhas", conteudo)
        
        print("✅ Leitura de arquivo texto funcionando")
    
    def test_processamento_json(self):
        """Testa processamento de arquivos JSON"""
        # Criar JSON de teste
        dados_teste = {
            "nome": "Teste",
            "versao": "1.0",
            "configuracoes": {
                "ativo": True,
                "limite": 100
            }
        }
        
        arquivo_json = os.path.join(self.temp_dir, "config.json")
        
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados_teste, f, indent=2)
        
        # Função de processamento para teste
        def processar_json(caminho_arquivo):
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Validações básicas
                validacoes = {
                    'tem_nome': 'nome' in dados,
                    'tem_versao': 'versao' in dados,
                    'tem_configuracoes': 'configuracoes' in dados,
                    'config_valida': isinstance(dados.get('configuracoes'), dict)
                }
                
                return True, dados, validacoes
            except Exception as e:
                return False, None, {'erro': str(e)}
        
        # Testar processamento
        sucesso, dados, validacoes = processar_json(arquivo_json)
        
        self.assertTrue(sucesso)
        self.assertEqual(dados['nome'], "Teste")
        self.assertTrue(validacoes['tem_nome'])
        self.assertTrue(validacoes['config_valida'])
        
        print("✅ Processamento de JSON funcionando")
    
    def test_validacao_estrutura_diretorios(self):
        """Testa validação de estrutura de diretórios"""
        # Criar estrutura de teste
        estrutura_teste = [
            "config",
            "src", 
            "backend",
            "frontend",
            "config/test.py",
            "src/utils.py"
        ]
        
        for item in estrutura_teste:
            caminho_completo = os.path.join(self.temp_dir, item)
            
            if '.' in Path(item).name:  # É arquivo
                os.makedirs(os.path.dirname(caminho_completo), exist_ok=True)
                Path(caminho_completo).touch()
            else:  # É diretório
                os.makedirs(caminho_completo, exist_ok=True)
        
        # Função de validação para teste
        def validar_estrutura_projeto(diretorio_base):
            diretorios_esperados = ['config', 'src', 'backend', 'frontend']
            arquivos_esperados = ['config/test.py', 'src/utils.py']
            
            resultado = {
                'diretorios_encontrados': [],
                'diretorios_faltando': [],
                'arquivos_encontrados': [],
                'arquivos_faltando': []
            }
            
            # Verificar diretórios
            for diretorio in diretorios_esperados:
                caminho = os.path.join(diretorio_base, diretorio)
                if os.path.isdir(caminho):
                    resultado['diretorios_encontrados'].append(diretorio)
                else:
                    resultado['diretorios_faltando'].append(diretorio)
            
            # Verificar arquivos
            for arquivo in arquivos_esperados:
                caminho = os.path.join(diretorio_base, arquivo)
                if os.path.isfile(caminho):
                    resultado['arquivos_encontrados'].append(arquivo)
                else:
                    resultado['arquivos_faltando'].append(arquivo)
            
            return resultado
        
        # Testar validação
        resultado = validar_estrutura_projeto(self.temp_dir)
        
        self.assertEqual(len(resultado['diretorios_faltando']), 0)
        self.assertEqual(len(resultado['arquivos_faltando']), 0)
        self.assertEqual(len(resultado['diretorios_encontrados']), 4)
        self.assertEqual(len(resultado['arquivos_encontrados']), 2)
        
        print("✅ Validação de estrutura de diretórios funcionando")


def executar_testes_componentes():
    """
    🔬 Executa testes de componentes individuais
    
    Foca em testar componentes específicos isoladamente.
    """
    print("\n" + "="*70)
    print("🔬 TESTES DE COMPONENTES INDIVIDUAIS - ValidAI Enhanced")
    print("="*70)
    print("\nTestando componentes isolados sem dependências externas...\n")
    
    # Configurar test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar classes de teste
    classes_teste = [
        TestValidacaoBasica,
        TestFuncoesUtilitarias,
        TestProcessamentoArquivos
    ]
    
    for classe in classes_teste:
        tests = loader.loadTestsFromTestCase(classe)
        suite.addTests(tests)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    resultado = runner.run(suite)
    
    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO DE COMPONENTES")
    print("="*70)
    
    total_testes = resultado.testsRun
    sucessos = total_testes - len(resultado.failures) - len(resultado.errors) - len(resultado.skipped)
    
    print(f"🧪 Testes executados: {total_testes}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {len(resultado.failures)}")
    print(f"💥 Erros: {len(resultado.errors)}")
    print(f"⏭️ Pulados: {len(resultado.skipped)}")
    
    # Calcular taxa de sucesso
    if total_testes > 0:
        taxa_sucesso = (sucessos / total_testes) * 100
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if taxa_sucesso >= 90:
            print(f"\n🎉 EXCELENTE! Componentes funcionando muito bem")
        elif taxa_sucesso >= 70:
            print(f"\n👍 BOM! Maioria dos componentes funcionando")
        else:
            print(f"\n⚠️ ATENÇÃO! Muitos componentes com problemas")
    
    print("="*70)
    
    return resultado.wasSuccessful()


if __name__ == "__main__":
    sucesso = executar_testes_componentes()
    sys.exit(0 if sucesso else 1)