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


# =============================
# Avatar e Arquivos Estáticos (AJUSTADO)
# =============================
AVATAR_B64 = ""
# Agora buscamos o avatar dentro da pasta /static
avatar_path = os.path.join(BASE_DIR, "static", "avatar.png")

if os.path.exists(avatar_path):
    with open(avatar_path, "rb") as img_file:
        AVATAR_B64 = f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

# Montagem de rotas para CSS, JS e Documentação
if os.path.exists("site"):
    app.mount("/docs", StaticFiles(directory="site", html=True), name="docs")

# AJUSTE: Agora servimos a pasta /static corretamente
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================
# Textos da Interface
# ============================================
DESPEDIDA_JS = ["Que o silêncio te acompanhe.", "O caminho se abre diante de ti.", "Vá em paz."]
AGUARDANDO_JS = ["Chizu medita...", "O mestre contempla...", "O silêncio se aprofunda..."]

HTML_PAGE = f"""
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chizu · Mestre Zen</title>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="stylesheet" href="/static/style.css">
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
            <div class="header-quote">
                Inspirado em<br>Shunryu Suzuki<br>Thich Nhat Hanh<br>Shunmyo Masuno<br>Haemin Sunim
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="pergunta" placeholder="Fale com Chizu..." autofocus>
        </div>
        <div class="resposta" id="resposta"><em>O silêncio precede a resposta...</em></div>
        <div class="footer">
            digite "sair", "ok" ou "gassho" para encerrar<br>
            <a href="https://chizuzen.github.io/Zenbot/" target="_blank" class="doc-link">📖 Documentação do Projeto</a>
            © 2026 • Chizu.Zenbot@gmail.com
        </div>
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

@app.post("/ask")                 
async def ask(request: Request):
    try:
        data     = await request.json()
        pergunta = data.get("pergunta", "").strip()

        if not pergunta:
            return JSONResponse({"resposta": "O silêncio é a resposta."})

        if pergunta.lower() in ["sair", "exit", "gassho", "obrigado", "ok", "quit"]:
            return JSONResponse({"resposta": random.choice(DESPEDIDA_JS)})

        session_id = request.cookies.get("chizu_session") or str(uuid4())
        historico  = conversation_memory.setdefault(session_id, [])

        # Gera embedding via API (sem modelo local)
        contexto = buscar_contexto(pergunta, biblioteca_chizu)

        mensagens_base   = montar_prompt(pergunta, contexto)
        prompt_completo  = [mensagens_base[0]] + historico[-8:] + [mensagens_base[-1]]

        resposta_raw, ia_nome = ai_provider.chat(prompt_completo)
        resposta_limpa   = resposta_raw.replace("(Silêncio)", "").replace("(pausa)", "").strip()
        resposta_exibida = f"{resposta_limpa}\n\n— via {ia_nome}"

        historico.append({"role": "user",      "content": pergunta})
        historico.append({"role": "assistant", "content": resposta_limpa})
        conversation_memory[session_id] = historico[-8:]

        response = JSONResponse({"resposta": resposta_exibida})
        response.set_cookie("chizu_session", session_id, max_age=60*60*24*7)
        return response

    except Exception as e:
        print(f"❌ Erro: {e}")
        return JSONResponse({"resposta": "Tremor na montanha digital."}, status_code=500)