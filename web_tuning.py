from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from zen import responder
import os

router = APIRouter()

MESSAGES = []

def get_last_messages(n: int):
    return MESSAGES[-n:]

def add_to_history(user_msg: str, assistant_msg: str):
    MESSAGES.append({"role": "user", "content": user_msg})
    MESSAGES.append({"role": "assistant", "content": assistant_msg})

def render_form_html(resposta: str = "", historico_html: str = ""):
    return f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>ZenBot – Oficina de Tuning</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; padding: 20px; color: #333; }}
            .container {{ background: #fff; padding: 30px; border-radius: 15px; max-width: 850px; margin: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
            h2 {{ text-align: center; color: #1a5928; border-bottom: 2px solid #eee; padding-bottom: 15px; }}
            label {{ display: block; margin-top: 15px; font-weight: bold; color: #444; }}
            input, select {{ width: 100%; padding: 12px; margin-top: 8px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; font-size: 1rem; }}
            button {{ margin-top: 25px; padding: 15px; font-size: 18px; background: #27ae60; color: white; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; transition: 0.3s; }}
            button:hover {{ background: #1e8449; }}
            pre {{ background: #fdfdfd; padding: 20px; border-left: 6px solid #27ae60; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; color: #2c3e50; font-family: 'Segoe UI', serif; font-size: 1.15em; }}
            .historico {{ margin-top: 40px; border-top: 2px solid #eee; padding-top: 20px; }}
            .msg-box {{ margin-bottom: 15px; padding: 15px; border-radius: 10px; font-size: 0.95em; white-space: pre-wrap; }}
            .user {{ background: #e3f2fd; border-right: 4px solid #1976d2; text-align: right; }}
            .assistant {{ background: #f1f8e9; border-left: 4px solid #388e3c; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>ZenBot – Oficina de Tuning</h2>
            <form method="post">
                <label>Estilo:</label>
                <select name="style">
                    <option value="system_prompt.txt" selected>System Prompt (Base)</option>
                    <option value="koans_classicos.txt">Koans Clássicos</option>
                    <option value="aforismos_zen.txt">Aforismos Zen</option>
                    <option value="meditacoes_guiadas.txt">Meditações Guiadas</option> 
                </select>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                    <div>
                        <label>Temperature:</label> <input type="number" step="0.05" name="temperature" value="0.4">
                        <label>Top P:</label> <input type="number" step="0.05" name="top_p" value="0.9">
                        <label>Context Count:</label> <input type="number" name="context_count" value="4">
                    </div>
                    <div>
                        <label>Max Tokens:</label> <input type="number" name="max_tokens" value="250">
                        <label>Frequency Penalty:</label> <input type="number" step="0.1" name="frequency_penalty" value="0.1">
                        <label>Presence Penalty:</label> <input type="number" step="0.1" name="presence_penalty" value="0.1">
                    </div>
                </div>
                <label>Sua Pergunta:</label>
                <input type="text" name="question" placeholder="O que é o silêncio?" required>
                <button type="submit">Calibrar e Perguntar</button>
            </form>
            <h3>Resposta do Mestre:</h3>
            <pre>{resposta if resposta else "O mestre aguarda..."}</pre>
            <div class="historico"><h3>Diálogo Recente:</h3>{historico_html}</div>
        </div>
    </body>
    </html>
    """

# --- ROTAS DA OFICINA ---

@router.get("/", response_class=HTMLResponse)
async def tuning_page():
    # Apenas exibe a página inicial da oficina com o histórico atual
    hist_html = "".join([f"<div class='msg-box {m['role']}'><b>{m['role'].capitalize()}:</b> {m['content']}</div>" for m in MESSAGES[-10:]])
    return HTMLResponse(render_form_html(historico_html=hist_html))

@router.post("/")
async def tuning_submit(
    style: str = Form(...), temperature: float = Form(...), top_p: float = Form(...),
    max_tokens: int = Form(...), frequency_penalty: float = Form(...),
    presence_penalty: float = Form(...), context_count: int = Form(...), question: str = Form(...)
):
    try:
        # 1. BUSCA O ARQUIVO DE ESTILO (Lógica Dupla)
        style_path = os.path.join("styles", style)
        if not os.path.exists(style_path):
            style_path = os.path.join("src", "styles", style)

        style_content = "Aja como o Mestre Chizu." # Caso falhe
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                style_content = f.read()
            print(f"[LOG] Estilo carregado de: {style_path}")
        else:
            print(f"[LOG] AVISO: Estilo não encontrado em {style_path}")

        # 2. PREPARA O CONTEXTO E ENVIA PARA O ZEN.PY
        hist_sel = get_last_messages(context_count)
        pergunta_com_estilo = f"Estilo: {style_content}\n\nPergunta: {question}"

        resultado, ia_nome = responder(
                    pergunta_com_estilo, 
                    historico=hist_sel, 
                    temperature=temperature, 
                    max_tokens=max_tokens, 
                    top_p=top_p, 
                    frequency_penalty=frequency_penalty, 
                    presence_penalty=presence_penalty
                )

        # Agora imprimimos no log do Render/Terminal
        print(f"--- OFICINA DE TUNING ---")
        print(f"[LOG] Estilo: {style}")
        print(f"[LOG] Provedor Utilizado: {ia_nome}")
        print(f"-------------------------")

        if isinstance(resultado, tuple): resultado = resultado[0]
        resposta_final = str(resultado).replace("\\n", "\n")

        # 3. TRATA A RESPOSTA E ATUALIZA O SITE
        if isinstance(resultado, tuple): resultado = resultado[0]
        resposta_final = str(resultado).replace("\\n", "\n")
        add_to_history(question, resposta_final)
        
        hist_html = "".join([f"<div class='msg-box {m['role']}'><b>{m['role'].capitalize()}:</b> {m['content']}</div>" for m in MESSAGES[-10:]])
        
        return HTMLResponse(render_form_html(resposta=resposta_final, historico_html=hist_html))

    except Exception as e:
        print(f"[ERRO] {e}")
        return HTMLResponse(render_form_html(resposta=f"Erro na Oficina: {str(e)}"))