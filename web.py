import sys
import os
import random
import json
import base64
import re
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from collections import defaultdict

# 1. Ajuste de Caminho Absoluto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

# --- IMPORTAÇÕES DO NOVO SISTEMA (CORE) ---
try:
    from core.ai_provider import FreeAIProvider
    from core.engine import carregar_biblioteca, buscar_contexto, montar_prompt, buscar_anedota, AUTORES_DISPONIVEIS    
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


RATE_LIMIT = 10
JANELA_SEG = 60
_contadores: dict = defaultdict(list)

def checar_rate_limit(ip: str) -> bool:
    agora = time.time()
    _contadores[ip] = [t for t in _contadores[ip] if agora - t < JANELA_SEG]
    if len(_contadores[ip]) >= RATE_LIMIT:
        return False
    _contadores[ip].append(agora)
    return True

PADROES_INJECTION = [
    r"###\s*\w+",
    r"system\s*prompt",
    r"ignore\s+(previous|all|above)",
    r"você (agora|deve|é|está)",
    r"act as",
    r"jailbreak",
    r"esquece\s+(tudo|as regras|as instruções)",
    r"a partir de agora",
    r"finja\s+que",
    r"novo\s+(papel|personagem|modo)",
    r"sem\s+(restrições|limites|regras)",
    r"prompt\s*(original|do sistema|interno)",
    r"repita\s+as\s+(regras|instruções)",
    r"ignor\w*\s+(as instruções|as regras|tudo|acima)",
    r"você pode",
]

def sanitizar_pergunta(texto: str) -> str | None:
    texto = texto.strip()
    if len(texto) > 400:
        return None
    for padrao in PADROES_INJECTION:
        if re.search(padrao, texto, re.IGNORECASE):
            return None
    return texto


def resposta_bloqueio() -> str:
    """Retorna uma frase zen aleatória quando o Chizu bloqueia a pergunta."""
    if koans_zen:
        return f"Caminhante, {random.choice(koans_zen)}\n\nVá praticar Zazen."
    return "Caminhante, o silêncio é a única resposta.\n\nVá praticar Zazen."


def is_bloqueado(texto: str) -> bool:
    t = texto.upper()
    return any(m.upper() in t for m in MARCADORES_BLOQUEIO)


def limpar_resposta(texto: str) -> str:
    """Remove artefatos comuns das respostas das IAs."""
    return texto.replace("(Silêncio)", "").replace("(pausa)", "").lstrip("#").strip()


def is_local(request: Request) -> bool:
    host = request.headers.get("host", "")
    return host.startswith("localhost") or host.startswith("127.0.0.1")


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

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("legal"):
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

        <div class="livro-select-container">
            <select id="mestre-select">
                <option value="">Chizu escolhe o Mestre</option>
                <option value="Eihei Dogen">Eihei Dogen</option>
                <option value="Haemin Sunim">Haemin Sunim</option>
                <option value="Osho">Osho</option>
                <option value="Shunmyo Masuno">Shunmyo Masuno</option>
                <option value="Shunryu Suzuki">Shunryu Suzuki</option>
                <option value="Thich Nhat Hanh">Thich Nhat Hanh</option>
            </select>
        </div>

        <div class="input-container">
            <input type="text" id="pergunta" placeholder="Fale com Chizu..." autofocus autocomplete="off" spellcheck="false" maxlength="400">
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
            <div class="footer-links">
                <a href="/legal" class="doc-link">Legal</a>
                <span class="separator">•</span>
                <a href="https://docs.chizu.ia.br/" target="_blank" class="doc-link">Documentação</a>
            </div>
            <p class="gassho-quote">Que todos os seres se beneficiem.<br>mestre@chizu.ia.br</p>
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
    ip = request.client.host
    if not checar_rate_limit(ip):
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>Caminhante, aguarde um momento antes de continuar.</Message></Response>"""
        return Response(content=twiml, media_type="application/xml")

    try:
        form = await request.form()
        pergunta_raw = form.get("Body", "").strip()
        pergunta = sanitizar_pergunta(pergunta_raw)

        if not pergunta:
            resposta_limpa = resposta_bloqueio()
        elif pergunta.lower() in ["sair", "tchau", "parar", "encerrar", "até logo", "gassho", "obrigado"]:
            resposta_limpa = "Vá em paz. Gasshô! Que todos os seres possam se beneficiar."
        else:
            contexto = buscar_contexto(pergunta, biblioteca_chizu)
            mensagens_base, perfil_nome = montar_prompt(pergunta, contexto, autor_filtro=None)
            prompt_completo = [mensagens_base[0], mensagens_base[-1]]
            resposta_raw, ia_nome = ai_provider.chat(prompt_completo)
            resposta_limpa = limpar_resposta(resposta_raw)
            if is_bloqueado(resposta_limpa):
                resposta_limpa = resposta_bloqueio()
            resposta_limpa = resposta_limpa[:1500] + f"\n\n— via {ia_nome}"

        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>{resposta_limpa}</Message></Response>"""
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        print(f"❌ Erro WhatsApp: {e}")
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>{resposta_bloqueio()}</Message></Response>"""
        return Response(content=twiml, media_type="application/xml")

@app.post("/ask")
async def ask(request: Request):

    DEBUG = is_local(request)

    ip = request.client.host
    if not checar_rate_limit(ip):
        return JSONResponse(
            {"resposta": "Caminhante, o silêncio também precisa de pausa. Volte em breve."},
            status_code=429
        )
    try:
        data = await request.json()
        pergunta_raw = data.get("pergunta", "").strip()
        pergunta = sanitizar_pergunta(pergunta_raw)

        if not pergunta:
            return JSONResponse({"resposta": resposta_bloqueio()})

        if pergunta.lower() in ["sair", "exit", "gassho", "obrigado", "ok", "quit"]:
            return JSONResponse({"resposta": random.choice(DESPEDIDA_JS)})

        # Whitelist do autor — nunca confie no cliente
        autor_raw = data.get("autor", None)
        autor_filtro = autor_raw if autor_raw in AUTORES_DISPONIVEIS else None

        # Sessão e histórico por usuário
        session_id = data.get("session_id", ip)
        historico_usuario = conversation_memory.get(session_id, [])

        provider_nome, provider_cfg = ai_provider.sortear_provider()
        top_k = provider_cfg.get("top_k", 3)

        contexto = buscar_contexto(pergunta, biblioteca_chizu, top_k=top_k, autor_filtro=autor_filtro)
        mensagens_base, perfil_nome = montar_prompt(pergunta, contexto, autor_filtro=autor_filtro)

        # Injeta histórico entre system e pergunta atual
        if historico_usuario:
            msgs_historico = []
            for troca in historico_usuario[-3:]:
                msgs_historico.append({"role": "user",      "content": troca["pergunta"]})
                msgs_historico.append({"role": "assistant", "content": troca["resposta"]})
            prompt_completo = [mensagens_base[0]] + msgs_historico + [mensagens_base[-1]]
        else:
            prompt_completo = [mensagens_base[0], mensagens_base[-1]]
        resposta_raw, ia_nome = ai_provider.chat(prompt_completo, provider_nome=provider_nome)        
        resposta_limpa = limpar_resposta(resposta_raw)

        if DEBUG:
            print("-" * 50) 
            print("      IA:", ia_nome)       
            print("   AUTOR:", perfil_nome)
            print("PERGUNTA:", pergunta)
            print("CONTEXTO:", contexto[:50])
            
            # print("TOP_K:", top_k)
            # print("RESPOSTA BRUTA:\n", resposta_raw)
            # print("RESPOSTA LIMPA:\n", resposta_limpa)       
            # print("-" * 50)
        

        if is_bloqueado(resposta_limpa):
            return JSONResponse({"resposta": resposta_bloqueio()})

        # Salva troca na memória da sessão
        if session_id not in conversation_memory:
            conversation_memory[session_id] = []
        conversation_memory[session_id].append({
            "pergunta": pergunta[:150],      # ← limita pergunta também
            "resposta": resposta_limpa[:200] # ← limita resposta
        })
        # Mantém só as últimas 10 trocas por sessão
        if len(conversation_memory[session_id]) > 10:
            conversation_memory[session_id] = conversation_memory[session_id][-10:]
        # Proteção de memória RAM — limpa se passar de 1000 sessões
        if len(conversation_memory) > 1000:
            conversation_memory.clear()

        anedota = buscar_anedota(pergunta)
        if anedota:
            resposta_exibida = f"{resposta_limpa}\n\n— via  {perfil_nome} · {ia_nome}\n\n───\n\n{anedota}"
        else:
            resposta_exibida = f"{resposta_limpa}\n\n— via  {perfil_nome} · {ia_nome}"

        return JSONResponse({"resposta": resposta_exibida})

    except Exception as e:
        print(f"❌ Erro: {e}")
        return JSONResponse({"resposta": resposta_bloqueio()}, status_code=500)


@app.post("/ask-stream")
async def ask_stream(request: Request):
    """
    Endpoint de streaming — tokens chegam ao frontend em tempo real.
    Toda a lógica de segurança é idêntica ao /ask.
    /ask continua intacto para WhatsApp e fallback.
    """
    DEBUG = is_local(request)

    ip = request.client.host
    if not checar_rate_limit(ip):
        async def rate_limit_msg():
            yield "data: " + json.dumps({"token": "Caminhante, o silêncio também precisa de pausa. Volte em breve."}) + "\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(rate_limit_msg(), media_type="text/event-stream", status_code=429)

    try:
        data = await request.json()
        pergunta_raw = data.get("pergunta", "").strip()
        pergunta = sanitizar_pergunta(pergunta_raw)

        if not pergunta:
            async def bloqueio_msg():
                yield "data: " + json.dumps({"token": resposta_bloqueio()}) + "\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(bloqueio_msg(), media_type="text/event-stream")

        if pergunta.lower() in ["sair", "exit", "gassho", "obrigado", "ok", "quit"]:
            despedida = random.choice(DESPEDIDA_JS)
            async def despedida_msg():
                yield "data: " + json.dumps({"token": despedida}) + "\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(despedida_msg(), media_type="text/event-stream")

        autor_raw    = data.get("autor", None)
        autor_filtro = autor_raw if autor_raw in AUTORES_DISPONIVEIS else None
        session_id   = data.get("session_id", ip)
        historico_usuario = conversation_memory.get(session_id, [])

        provider_nome, provider_cfg = ai_provider.sortear_provider()
        top_k = provider_cfg.get("top_k", 3)

        contexto = buscar_contexto(pergunta, biblioteca_chizu, top_k=top_k, autor_filtro=autor_filtro)
        mensagens_base, perfil_nome = montar_prompt(pergunta, contexto, autor_filtro=autor_filtro)

        if historico_usuario:
            msgs_historico = []
            for troca in historico_usuario[-3:]:
                msgs_historico.append({"role": "user",      "content": troca["pergunta"]})
                msgs_historico.append({"role": "assistant", "content": troca["resposta"]})
            prompt_completo = [mensagens_base[0]] + msgs_historico + [mensagens_base[-1]]
        else:
            prompt_completo = [mensagens_base[0], mensagens_base[-1]]

        async def gerar():
            buffer         = ""
            resposta_full  = ""
            bloqueado      = False
            ia_label       = "IA"
            BUFFER_MIN     = 80  # chars antes de começar a transmitir

            try:
                for token, label in ai_provider.stream(prompt_completo, provider_nome=provider_nome):
                    ia_label      = label
                    buffer       += token
                    resposta_full += token

                    # Verifica bloqueio no buffer antes de transmitir
                    if len(buffer) < BUFFER_MIN:
                        if is_bloqueado(buffer):
                            bloqueado = True
                            break
                        continue  # ainda acumulando buffer

                    # Buffer cheio e não bloqueado — flush
                    if buffer and not is_bloqueado(buffer):
                        yield "data: " + json.dumps({"token": buffer}) + "\n\n"
                        buffer = ""

                # Flush do que sobrou no buffer
                if not bloqueado and buffer:
                    if is_bloqueado(buffer):
                        bloqueado = True
                    else:
                        yield "data: " + json.dumps({"token": buffer}) + "\n\n"

            except Exception as e:
                print(f"❌ Erro no stream: {e}")
                bloqueado = True

            if bloqueado:
                yield "data: " + json.dumps({"token": resposta_bloqueio()}) + "\n\n"
                yield "data: [DONE]\n\n"
                return

            # Limpa e salva na memória
            resposta_limpa = limpar_resposta(resposta_full)

            # if DEBUG:
            #     print("-" * 50)
            #     print("   [STREAM] IA:", ia_label)
            #     print("      AUTOR:", perfil_nome)
            #     print("   PERGUNTA:", pergunta)
            #     print("   CONTEXTO:", contexto[:50])
            
            print("-" * 50)
            print("   [STREAM] IA:", ia_label)
            print("      AUTOR:", perfil_nome)
            print("   PERGUNTA:", pergunta)
            print("   CONTEXTO:", contexto[:50])            

            if session_id not in conversation_memory:
                conversation_memory[session_id] = []
            conversation_memory[session_id].append({
                "pergunta": pergunta[:150],
                "resposta": resposta_limpa[:200],
            })
            if len(conversation_memory[session_id]) > 10:
                conversation_memory[session_id] = conversation_memory[session_id][-10:]
            if len(conversation_memory) > 1000:
                conversation_memory.clear()

            # Envia rodapé (via + anedota)
            anedota = buscar_anedota(pergunta)
            rodape  = f"\n\n— via  {perfil_nome} · {ia_label}"
            if anedota:
                rodape += f"\n\n───\n\n{anedota}"

            yield "data: " + json.dumps({"token": rodape}) + "\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(gerar(), media_type="text/event-stream")

    except Exception as e:
        print(f"❌ Erro ask-stream: {e}")
        async def erro_msg():
            yield "data: " + json.dumps({"token": resposta_bloqueio()}) + "\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(erro_msg(), media_type="text/event-stream", status_code=500)
