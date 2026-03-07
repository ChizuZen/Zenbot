from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from zen import responder
import os

router = APIRouter()

# ============================================
# Histórico em memória (Limpa ao reiniciar)
# ============================================
MESSAGES = []

def get_last_messages(n: int):
    return MESSAGES[-n:]

def add_to_history(user_msg: str, assistant_msg: str):
    MESSAGES.append({"role": "user", "content": user_msg})
    MESSAGES.append({"role": "assistant", "content": assistant_msg})

# ============================================
# Página HTML do formulário de tuning
# ============================================
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
            
            /* CSS para Respeitar Quebras de Linha e Estética Zen */
            pre {{ 
                background: #fdfdfd; 
                padding: 20px; 
                border-left: 6px solid #27ae60; 
                border-radius: 8px; 
                white-space: pre-wrap;       /* Aceita quebras de linha reais */
                word-wrap: break-word;       /* Evita estouro de texto */
                color: #2c3e50; 
                font-family: 'Segoe UI', serif; 
                font-size: 1.15em;
                box-shadow: inset 0 0 10px rgba(0,0,0,0.02);
            }}
            
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
                <label>Estilo (Personalidade do Arquivo):</label>
                <select name="style">
                    <option value="system_prompt.txt" selected>System Prompt (Base)</option>
                    <option value="koans_classicos.txt">Koans Clássicos</option>
                    <option value="aforismos_zen.txt">Aforismos Zen</option>
                    <option value="meditacoes_guiadas.txt">Meditações Guiadas</option>
                </select>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                    <div>
                        <label>Temperature: <small>(0.0 a 1.0)</small></label>
                        <input type="number" step="0.05" name="temperature" value="0.4">
                        <span style="font-size: 0.8em; color: #666;"><i>Baixa = Focado/Rígido | Alta = Criativo/Caótico</i></span>

                        <label>Top P: <small>(0.0 a 1.0)</small></label>
                        <input type="number" step="0.05" name="top_p" value="0.9">
                        <span style="font-size: 0.8em; color: #666;"><i>Filtro de diversidade de palavras (Nucleus Sampling)</i></span>

                        <label>Context Count:</label>
                        <input type="number" name="context_count" value="4">
                        <span style="font-size: 0.8em; color: #666;"><i>Quantas mensagens passadas o mestre "lembra"</i></span>
                    </div>

                    <div>
                        <label>Max Tokens:</label>
                        <input type="number" name="max_tokens" value="180">
                        <span style="font-size: 0.8em; color: #666;"><i>Limite de tamanho da resposta</i></span>

                        <label>Frequency Penalty: <small>(-2.0 a 2.0)</small></label>
                        <input type="number" step="0.1" name="frequency_penalty" value="0.0">
                        <span style="font-size: 0.8em; color: #666;"><i>Evita repetir as mesmas palavras exatas</i></span>

                        <label>Presence Penalty: <small>(-2.0 a 2.0)</small></label>
                        <input type="number" step="0.1" name="presence_penalty" value="0.0">
                        <span style="font-size: 0.8em; color: #666;"><i>Incentiva o mestre a falar sobre novos temas</i></span>
                    </div>
                </div>

                <label>Sua Pergunta:</label>
                <input type="text" id="question_input" name="question" placeholder="O que é o silêncio?" required>

                <button type="submit">Calibrar e Perguntar</button>
            </form>

            <h3>Resposta do Mestre:</h3>
            <pre>{resposta if resposta else "O mestre aguarda sua indagação no silêncio da oficina..."}</pre>

            <div class="historico">
                <h3>Diálogo Recente:</h3>
                {historico_html}
            </div>
        </div>
    </body>
    </html>
    """

@router.get("/", response_class=HTMLResponse)
async def tuning_page():
    # Carrega o histórico vazio ou existente ao abrir a página
    historico_html = "".join([
        f"<div class='msg-box {msg['role']}'><b>{msg['role'].capitalize()}:</b> {msg['content']}</div>" 
        for msg in MESSAGES[-10:]
    ])
    return HTMLResponse(render_form_html(historico_html=historico_html))

# ... (parte superior do arquivo igual)

@router.post("/")
async def tuning_submit(
    style: str = Form(...),
    temperature: float = Form(...),
    top_p: float = Form(...),
    max_tokens: int = Form(...),
    frequency_penalty: float = Form(...),
    presence_penalty: float = Form(...),
    context_count: int = Form(...),
    question: str = Form(...)
):
    try:
        style_path = os.path.join("styles", style)
        style_content = "Aja como o Mestre Chizu."
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                style_content = f.read()

        historico_selecionado = get_last_messages(context_count)
        pergunta_com_estilo = f"Contexto/Estilo: {style_content}\n\nPergunta: {question}"

        # Chamada única com todos os novos parâmetros
        resultado_bruto = responder(
            pergunta_com_estilo, 
            historico=historico_selecionado,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )

        if isinstance(resultado_bruto, tuple):
            resposta_limpa = resultado_bruto[0]
        else:
            resposta_limpa = resultado_bruto

        resposta_final = str(resposta_limpa).strip("()").strip("'").strip('"')
        resposta_final = resposta_final.replace("\\n", "\n")
        
        add_to_history(question, resposta_final)
        resposta = resposta_final

    except Exception as e:
        resposta = f"Distração na montanha (Erro): {str(e)}"

    # Renderiza o histórico uma única vez no final
    historico_html = "".join([
        f<div class='msg-box {msg['role']}'><b>{msg['role'].capitalize()}:</b> {msg['content']}</div>" 
        for msg in MESSAGES[-10:]
    ])
    
    return HTMLResponse(render_form_html(resposta=resposta, historico_html=historico_html))
