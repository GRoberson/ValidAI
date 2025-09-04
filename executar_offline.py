"""
🔌 Execução Offline do ValidAI Enhanced
Executa a aplicação sem dependência do Vertex AI ou outros serviços externos
"""

import os
import sys
from pathlib import Path

# Configurar modo offline
os.environ["VALIDAI_OFFLINE_MODE"] = "True"
os.environ["USE_MOCK_SERVICES"] = "True"

# Adicionar o diretório atual ao PYTHONPATH para resolver problemas de importação
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    print("🔌 Iniciando ValidAI Enhanced em modo OFFLINE")
    print("✅ Usando MockServices para simular Vertex AI e Google Cloud")
    
    # Importar o script principal após configurar o ambiente
    from run_validai_enhanced import main
    
    # Executar a aplicação principal sem argumentos extras
    # Preservar quaisquer argumentos originais passados pelo usuário
    main()