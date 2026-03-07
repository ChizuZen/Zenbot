from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import random
import json
import base64
import os
from web_tuning import router as tuning_router  # importa o router do arquivo de testes
from zen import responder, verificar_chave, aquecer_modelo
from uuid import uuid4

# =============================
# Avatar
# =============================
AVATAR_B64 = ""
if os.path.exists("avatar.png"):
    with open("avatar.png", "rb") as img_file:
        AVATAR_B64 = f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

# Memória temporária em RAM
conversation_memory = {}

# ============================================
# Inicialização
# ============================================
verificar_chave()
aquecer_modelo()
app = FastAPI()
app.include_router(tuning_router, prefix="/tuning")
app.mount("/static", StaticFiles(directory="."), name="static")

# ============================================
# Mensagens para o Frontend
# ============================================
DESPEDIDA_JS = [
    "Que o silêncio te acompanhe.",
    "O caminho se abre diante de ti.",
    "Vá em paz. O vazio te espera.",
    "Que a mente de principiante floresça.",
    "Lembre-se: a montanha também é caminho."
]

AGUARDANDO_JS = [
    "Chizu medita...",
    "O mestre contempla sua pergunta...",
    "O silêncio se aprofunda...",
    "Chizu respira fundo...",
    "As folhas balançam ao vento..."
]

# ============================================
# Página HTML
# ============================================
HTML_PAGE = f"""
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chizu · Mestre Zen</title>
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
                Inspirado em<br>
                <em>"Mente Zen, Mente de Principiante"</em><br>
                Shunryu Suzuki
            </div>
        </div>

        <div class="input-container">
            <input type="text" id="pergunta" placeholder="Fale com Chizu..." autofocus>
        </div>

        <div class="resposta" id="resposta">
            <em>O silêncio precede a resposta...</em>
        </div>

        <div class="footer">
            digite "sair", "ok" ou "gassho" para encerrar<br>
            <a href="https://chizuzen.github.io/Zenbot/" target="_blank" class="doc-link">📖 Documentação do Projeto</a>
            © 2026 • <a href="mailto:Chizu.Zenbot@gmail.com" style="color: inherit; text-decoration: none;">Chizu.Zenbot@gmail.com</a>
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
# Carrega Koans Clássicos
# ============================================
KOANS = []
koans_path = "src/styles/koans_classicos.txt"
if os.path.exists(koans_path):
    with open(koans_path, "r", encoding="utf-8") as f:
        KOANS = [k.strip() for k in f.read().split("\n") if k.strip()]

# ============================================
# Rotas
# ============================================
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_PAGE

@app.get("/koan")
async def get_koan():
    koan = random.choice(KOANS) if KOANS else "O silêncio é profundo."
    return JSONResponse({"koan": koan})

@app.post("/ask")
async def ask(request: Request):

    try:

        data = await request.json()

        pergunta = data.get("pergunta", "").strip()

        if not pergunta:
            return JSONResponse({"resposta": "O silêncio é a resposta."})

        palavras_saida = ["sair", "exit", "quit", "gassho", "obrigado", "ok"]

        if pergunta.lower() in palavras_saida:
            return JSONResponse({"resposta": random.choice(DESPEDIDA_JS)})

        session_id = request.cookies.get("chizu_session") or str(uuid4())

        historico = conversation_memory.setdefault(session_id, [])

        try:
            # Chamamos o mestre apenas UMA vez
            resposta_llm = responder(pergunta, historico)
            
            # Removemos marcas artificiais de silêncio para a resposta ficar pura
            resposta_llm = (
                resposta_llm
                .replace("(Silêncio)", "")  
                .replace("(silêncio)", "")
                .replace("(pausa)", "")
            )   
            
            # Definimos que a resposta final é a versão limpa
            resposta_final = resposta_llm          

        except RuntimeError as e:

            if str(e) == "RATE_LIMIT":

                koan_fallback = random.choice(KOANS) if KOANS else "O silêncio é profundo."

                aviso = "Estamos recebendo muitas requisições no momento."

                resposta_final = f"{aviso}\n\nKoan para reflexão:\n{koan_fallback}"

                return JSONResponse({"resposta": resposta_final})

            else:

                raise

        # =============================
        # Memória da conversa
        # =============================

        historico.append({
            "role": "user",
            "content": pergunta
        })

        historico.append({
            "role": "assistant",
            "content": resposta_llm
        })

        conversation_memory[session_id] = historico[-8:]

        response = JSONResponse({"resposta": resposta_final})

        response.set_cookie("chizu_session", session_id, max_age=60*60*24*7)

        return response

    except Exception:

        return JSONResponse({"resposta": "Tremor na montanha digital."}, status_code=500)