import gradio as gr

# Figuras utilizadas
logo_img = "https://i.postimg.cc/vHLWB2Yc/1000101704-removebg-preview.png"
logo_validai = "https://i.postimg.cc/P58YsMhj/imagem-1.png"
logo_bv = "https://upload.wikimedia.org/wikipedia/pt/7/78/Logo_Banco_BV.png"
logo_validai_rag = "https://i.postimg.cc/BvMxzLS9/imagem-validai-RAG.png"
logo_validai_pre = "https://i.postimg.cc/BbWRVQB3/imagem-validai-pre.png"

# Estilo do gradio
theme = gr.themes.Base(
    primary_hue="indigo",
    secondary_hue="indigo"
)

informacoes = """# Informações sobre o ValidAI
            <br>**Sobre o ValidAI:**
            O ValidAI é uma aplicação de uso do Gemini AI (IA Generativa do Google), configurado para o âmbito de modelos.
            A aplicação é capaz de interpretar textos, imagens, arquivos PDF, vídeos (.mp4) e códigos nas extensões .sas, .ipynb e .py..
            
            **Como usar:**
            Cada aba apresenta um método de interação com aplicação:
            * ValidAI - 
            Chat multimodal, que permite o usuário interagir via comando de texto, enviar arquivos PDF, MP4, SAS e Python (.py e .ipynb).
            As informações são processadas a partir do LLM Gemini 1.5 Pro, e portanto refletem a base de conhecimento pré-treinada do modelo.
            * ValidAI Pré-Validador - 
            Processa somente arquivos PDF e códigos, de modo a realizar testes predefinidos. 
            Caso forneça somente o documento, a ferramenta irá realizar testes sobre a qualidade do documento, caso envie somente códigos, a ferramenta aplicará testes referentes aos códigos.
            Por fim, caso envie tanto documento quanto códigos, a ferramenta realizará uma comparação entre ambos os contextos.
            Atualmente a ferramenta suporta somente um documento PDF e até dez códigos por vez.
            * ValidAI RAG - 
            Chat exclusivo para consultas, através de comandos em texto. 
            O RAG (Retrieval Augmented Generation) permite expandir a base de conhecimento do modelo, portanto, para interagir com esta funcionalidade é necessário definir sobre qual base pretende consultar.
            Atualmente a ferramenta oferece suporte sobre as seguintes bases:
                * Conteúdo das INs - IN_1253 (Framework de GRM), IN_706 (Validação de Modelos) e IN_1146 (Controles Internos);
                * Validações de Riscos de Mercado - Relatório das validações dos modelos de Riscos de Mercado em 2023;
                * Validações de Riscos de Crédito - Relatório das validações dos modelos de Riscos de Crédito em 2023;
                * Google Search - Complemento para buscas de conteúdo no Google, capaz de oferecer informações atualizadas em tempo real.
            
            **Contatos:**
            Para dúvidas ou sugestões, estamos à disposição:
            * Henrique Feo - henrique.emery@bv.com.br
            * Geraldo Robserson Costa Almeida - geraldo.almeida@bv.com.br
            
            <center><b>Gestão de Risco de Modelos</b></center>
            """

# Código CSS para a aplicação
css_interface = """

.gradio-container {
    background: url('""" + logo_bv + """');
    background-position: top right;
    background-repeat: no-repeat;
    background-size: 80px;
    background-position-y: 10px !important;
    background-position-x: calc(100% - 30px);
    padding-top: 20px !important;
    }

.gradio-container h1 {
    font-size: 30px !important;
    color: #223AD2 !important;
    margin-bottom: -18px !important;
    text-align: left !important;

}

/* Trecho do comentário para ajustar o ícone que fica cortado */
.hide-container.svelte-11xb1hd{
    overflow: visible !important;
}

div.svelte-tcemt9{
    padding: inherit !important;
}

/* código para ajustar o tamanho dos campos de upload de arquivo do pré-validador */
button.svelte-1b742ao {
    height: 130px !important;
}

#espaco_chat{
    flex-grow: 1;
}

.svelte-1ed2p3z{
    margin-bottom: -18px !important
}

.message-row.bubble.svelte-1e1jlin.svelte-1e1jlin.svelte-1e1jlin{
    margin-top: 10px !important;
    margin-bottom: 10px !important;
}

.prose.chatbot.md {
    opacity: 1 !important;
}

/* Código para ajustar o avatar */
.avatar-container.svelte-u94xf4 img{
    position: absolute;
    top: -1px !important;
    left: 1px !important;
    padding: 0 !important;
}

.avatar-container.svelte-u94xf4.svelte-u94xf4{
    border: none !important;
    position: relative;
}

#dropdown123{
    position: absolute !important;
    top: 0px !important;
    width: 400px !important;
    right: 10px !important;
} 

.unequal-height.svelte-hrj4a0{
    padding-top: 10px !important;
}

.message-row.bubble{
    margin-bottom:0px !important;
}

#saida_pre{
    overflow: auto !important;
}

.svelte-b8me0j{
    padding-left: 0px !important;
    padding-top: 0px !important;
    padding-right: 0px !important;
    padding-bottom: 0px !important;
}

"""