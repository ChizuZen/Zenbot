import os
import time
import random
import requests
import traceback
from core.engine import montar_prompt

# =============================
# Configurações da API LLM
# =============================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
TIMEOUT = 30

# =============================
# Mensagens de personalidade
# =============================

ERROS_ZEN = [
    "O vento sopra forte e Chizu se cala por instantes. Tente novamente.",
    "Uma folha cai entre nós e a resposta se perde. Pergunte outra vez.",
    "O silêncio de Chizu é mais profundo que o mar."
]

AQUECIMENTO = [
    "(Chizu prepara o incenso...)",
    "(O mestre ajusta a postura de zazen...)"
]

# =============================
# Detector simples de estilo
# =============================

def detectar_estilo(pergunta: str) -> str:
    p = pergunta.lower().strip()

    if p.startswith("/aforismo"):
        return "aforismo"
    if p.startswith("/koan"):
        return "koan"
    if p.startswith("/meditacao"):
        return "meditacao"

    return "padrao"

def limpar_comando(pergunta: str) -> str:
    if pergunta.startswith("/"):
        partes = pergunta.split(" ", 1)
        if len(partes) == 2:
            return partes[1]
        return ""
    return pergunta

# =============================
# Função principal
# =============================

def responder(pergunta, historico=None, tentativas=2):
    estilo = detectar_estilo(pergunta)
    pergunta = limpar_comando(pergunta)

    for tentativa in range(tentativas):
        try:
            messages = montar_prompt(pergunta, estilo)

            # opcional: memória curta
            def normalizar_historico(historico, limite_pares=2, max_chars=300):
                if not historico:
                    return []

                ultimos = historico[-limite_pares*2:]
                seguro = []
                for m in ultimos:
                    seguro.append({
                        "role": m["role"],
                        "content": m["content"][:max_chars]
                    })
                return seguro


            memoria = normalizar_historico(historico)
            messages = memoria + messages

            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.55,
                "max_tokens": 800,
                "frequency_penalty": 0.4,
                "presence_penalty": 0.25
            }

            r = requests.post(
                GROQ_URL,
                json=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=TIMEOUT
            )
            r.raise_for_status()

            return r.json()["choices"][0]["message"]["content"].strip()

        # except Exception:
        #     if tentativa < tentativas - 1:
        #         time.sleep(1.5)
        #     else:
        #         return f"({random.choice(ERROS_ZEN)})"
            
        except Exception as e:
            print("\n[ERRO REAL NO CHIZU]")
            traceback.print_exc()

            if tentativa < tentativas - 1:
                time.sleep(1.5)
            else:
                return f"({random.choice(ERROS_ZEN)})"
                    

# =============================
# Inicialização
# =============================

def verificar_chave():
    if not GROQ_API_KEY:
        print("❌ Erro: GROQ_API_KEY não configurada.")
        exit(1)

def aquecer_modelo():
    print(random.choice(AQUECIMENTO))

if __name__ == "__main__":
    verificar_chave()
    aquecer_modelo()
    print("\n🧘 Chizu Online. Digite 'sair' para encerrar.\n")
    while True:
        p = input("Discípulo: ")
        if p.lower() in ["sair", "ok", "gassho"]:
            break
        print(f"\nChizu: {responder(p)}\n")
