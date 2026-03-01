from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import random
import json
import base64
import os
from zen import responder, verificar_chave, aquecer_modelo
from uuid import uuid4

AVATAR_B64 = ""
if os.path.exists("avatar.png"):
    with open("avatar.png", "rb") as img_file:
        AVATAR_B64 = f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

# Memória temporária em RAM
conversation_memory = {}

# ============================================
# INICIALIZAÇÃO
# ============================================
verificar_chave()
aquecer_modelo()
app = FastAPI()
app.mount("/static", StaticFiles(directory="."), name="static")

# Mensagens para o Frontend
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
# PÁGINA HTML (LIMPA E SEM DUPLICIDADE)
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
            <input type="text" id="pergunta" placeholder="Pressione Enter para falar com Chizu..." autofocus>
        </div>

        <div class="resposta" id="resposta">
            <em>O silêncio precede a resposta...</em>
        </div>

        <div class="footer">
            digite "sair", "ok" ou "gassho" para encerrar<br>
            <a href="https://chizuzen.github.io/Zenbot/" target="_blank" class="doc-link">📖 Ver Documentação do Projeto</a>
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
# ROTAS DA API
# ============================================
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_PAGE

@app.post("/ask")
async def ask(request: Request):
    try:
        data = await request.json()
        pergunta = data.get("pergunta", "").strip()
        
        if not pergunta:
            return JSONResponse({"resposta": "O silêncio é a resposta."})

        # Corrigindo a lista para evitar o Erro 500 anterior:
        palavras_saida = ["sair", "exit", "quit", "gassho", "obrigado", "ok"]
        if pergunta.lower() in palavras_saida:
            return JSONResponse({"resposta": random.choice(DESPEDIDA_JS)})

        session_id = request.cookies.get("chizu_session") or str(uuid4())
        historico = conversation_memory.setdefault(session_id, [])

        # Resposta do Mestre
        try:
            resposta = responder(pergunta, historico)
        except Exception as e:
            return JSONResponse({"resposta": f"O mestre medita. (Erro: {str(e)})"}, status_code=500)

        # Atualiza memória
        historico.append({"role": "user", "content": pergunta})
        historico.append({"role": "assistant", "content": resposta})
        conversation_memory[session_id] = historico[-8:]

        response = JSONResponse({"resposta": resposta})
        response.set_cookie("chizu_session", session_id, max_age=60*60*24*7)
        return response

    except Exception as e:
        return JSONResponse({"resposta": "Tremor na montanha digital."}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    # Importante: O Render usa a porta da variável de ambiente $PORT
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)