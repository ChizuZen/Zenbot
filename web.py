import sys
import os
import random
import json
import base64
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# 1. Ajuste de Caminho Absoluto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# --- IMPORTAÇÕES DO NOVO SISTEMA (CORE) ---
try:
    from core.ai_provider import FreeAIProvider
    from core.engine import carregar_biblioteca, buscar_contexto, montar_prompt
except ImportError as e:
    print(f"❌ Erro de importação: {e}. Verifique a pasta 'core'.")
    sys.exit(1)


# ============================================
# Inicialização do Sistema
# ============================================
app = FastAPI()

# Inicializa o Conselho de IAs e a Sabedoria
ai_provider = FreeAIProvider()
biblioteca_chizu = carregar_biblioteca()

# Memória temporária em RAM
conversation_memory = {}

# Carrega frases zen para respostas de bloqueio aleatórias
KOANS_PATH = os.path.join(BASE_DIR, "data", "koans.txt")
koans_zen = []
if os.path.exists(KOANS_PATH):
    koans_zen = [k.strip() for k in open(KOANS_PATH, encoding="utf-8").readlines() if k.strip()]
    print(f"✅ {len(koans_zen)} frases zen carregadas.")

# Marcadores de bloqueio — única fonte da verdade
MARCADORES_BLOQUEIO = ["BLOQUEADO", "VAZIO"]


def resposta_bloqueio() -> str:
    """Retorna uma frase zen aleatória quando o Chizu bloqueia a pergunta."""
    if koans_zen:
        return f"Caminhante, {random.choice(koans_zen)}\n\nVá praticar Zazen."
    return "Caminhante, o silêncio é a única resposta.\n\nVá praticar Zazen."


def is_bloqueado(texto: str) -> bool:
    """Verifica se a resposta da IA contém marcador de bloqueio."""
    return any(marcador in texto for marcador in MARCADORES_BLOQUEIO)


def limpar_resposta(texto: str) -> str:
    """Remove artefatos comuns das respostas das IAs."""
    return texto.replace("(Silêncio)", "").replace("(pausa)", "").lstrip("#").strip()


# =============================
# Avatar e Arquivos Estáticos
# =============================
AVATAR_B64 = ""
avatar_path = os.path.join(BASE_DIR, "static", "img", "avatar.png")

if os.path.exists(avatar_path):
    with open(avatar_path, "rb") as img_file:
        AVATAR_B64 = f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

# Montagem de rotas para CSS, JS e Documentação
if os.path.exists("site"):
    app.mount("/docs", StaticFiles(directory="site", html=True), name="docs")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/legal", StaticFiles(directory="legal", html=True), name="legal")


# ============================================
# Textos da Interface
# ============================================
DESPEDIDA_JS = ["Que o silêncio te acompanhe.", "O caminho se abre diante de ti.", "Vá em paz."]
AGUARDANDO_JS = [
    "Chizu medita...",
    "O mestre contempla...",
    "O silêncio se aprofunda...",
    "Chizu respira fundo...",
    "Os pensamentos se dissolvem...",
    "O vazio fala...",
    "Chizu ouve o invisível...",
    "A mente se aquieta...",
    "A resposta emerge...",
    "Chizu aguarda o momento...",
    "As palavras tomam forma...",
    "O mestre fecha os olhos...",
    "A sabedoria emerge...",
    "Chizu alinha os chakras...",
    "O universo processa...",
    "A névoa se dissipa...",
    "Chizu consulta os ventos...",
    "O eco ressoa...",
]

HTML_PAGE = f"""
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chizu · Mestre Zen</title>
    <link rel="icon" type="image/x-icon" href="/static/img/favicon.ico">
    <link rel="stylesheet" href="/static/style.css?v=3">
</head>
<body>
    <div class="container">
        <div class="header-card">
            <div class="header-info">
                <h1>Chizu</h1>
                <div class="sub">mestre zen digital</div>
            </div>
            <div class="header-avatar">
                <img src="{AVATAR_B64}" alt="Mestre Chizu">
            </div>
        </div>

        <div class="input-container">
            <input type="text" id="pergunta" placeholder="Fale com Chizu..." autofocus autocomplete="off" spellcheck="false">
            <button id="btn-mic" title="Falar com Chizu">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
            </button>
            <button id="btn-enviar" onclick="fazerPergunta()">&#10148;</button>
        </div>


        <div class="resposta" id="resposta"><em>O silêncio precede a resposta...</em></div>

        <footer class="footer">
            <p class="gassho-quote">Que todos os seres se beneficiem.<br>mestre@chizu.ia.br</p>            
            <div class="footer-links">
                <a href="/legal" class="doc-link">Legal</a>
                <span class="separator">•</span>
                <a href="https://docs.chizu.ia.br/" target="_blank" class="doc-link">Documentação</a>
            </div>
        </footer>            
    </div>
    <script>
        window.DESPEDIDA_JS = {json.dumps(DESPEDIDA_JS)};
        window.AGUARDANDO_JS = {json.dumps(AGUARDANDO_JS)};
    </script>
    <script src="/static/script.js"></script>
</body>
</html>
"""

# ============================================
# Rotas do Servidor
# ============================================
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_PAGE


@app.head("/")
async def head_index():
    return Response(status_code=200)


@app.post("/whatsapp")
async def whatsapp(request: Request):
    try:
        form = await request.form()
        pergunta = form.get("Body", "").strip()
        telefone = form.get("From", "")

        if not pergunta:
            resposta_limpa = "O silêncio é a resposta."
        elif pergunta.lower() in ["sair", "tchau", "parar", "encerrar", "até logo", "gassho", "obrigado"]:
            resposta_limpa = "Vá em paz. Gasshô! Que todos os seres possam se beneficiar."
        else:
            historico = conversation_memory.setdefault(telefone, [])
            contexto = buscar_contexto(pergunta, biblioteca_chizu)
            mensagens_base, perfil_nome = montar_prompt(pergunta, contexto, autor_filtro=autor_filtro)
            prompt_completo = [mensagens_base[0]] + historico[-8:] + [mensagens_base[-1]]

            resposta_raw, ia_nome = ai_provider.chat(prompt_completo)
            resposta_limpa = limpar_resposta(resposta_raw)

            if is_bloqueado(resposta_limpa):
                resposta_limpa = resposta_bloqueio()

            resposta_limpa = resposta_limpa[:1500] + f"\n\n— via {ia_nome}"
            historico.append({"role": "user", "content": pergunta})
            historico.append({"role": "assistant", "content": resposta_limpa})
            conversation_memory[telefone] = historico[-8:]

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{resposta_limpa}</Message>
</Response>"""
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        print(f"❌ Erro WhatsApp: {e}")
        koan = resposta_bloqueio()
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{koan}</Message>
</Response>"""
        return Response(content=twiml, media_type="application/xml")


@app.post("/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        pergunta = data.get("pergunta", "").strip()

        if not pergunta:
            return JSONResponse({"resposta": "O silêncio é a resposta."})

        if pergunta.lower() in ["sair", "exit", "gassho", "obrigado", "ok", "quit"]:
            return JSONResponse({"resposta": random.choice(DESPEDIDA_JS)})

        session_id = request.cookies.get("chizu_session") or str(uuid4())
        historico = conversation_memory.setdefault(session_id, [])

        autor_filtro = data.get("autor", None)
        contexto = buscar_contexto(pergunta, biblioteca_chizu, autor_filtro=autor_filtro)
        mensagens_base, perfil_nome = montar_prompt(pergunta, contexto, autor_filtro=autor_filtro)
        prompt_completo = [mensagens_base[0]] + historico[-8:] + [mensagens_base[-1]]

        resposta_raw, ia_nome = ai_provider.chat(prompt_completo)
        resposta_limpa = limpar_resposta(resposta_raw)

        if is_bloqueado(resposta_limpa):
            resposta_limpa = resposta_bloqueio()

        resposta_exibida = f"{resposta_limpa}\n\n— via  {perfil_nome} · {ia_nome}"

        historico.append({"role": "user", "content": pergunta})
        historico.append({"role": "assistant", "content": resposta_limpa})
        conversation_memory[session_id] = historico[-8:]

        response = JSONResponse({"resposta": resposta_exibida})
        response.set_cookie("chizu_session", session_id, max_age=60*60*24*7)
        return response

    except Exception as e:
        print(f"❌ Erro: {e}")
        return JSONResponse({"resposta": "Tremor na montanha digital."}, status_code=500)
