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


def responder(pergunta, historico=None, tentativas=3, temperature=0.55, max_tokens=800):
    estilo = detectar_estilo(pergunta)
    pergunta = limpar_comando(pergunta)

    for tentativa in range(tentativas):
        try:
            # ===== Monta prompt e histórico =====
            messages = montar_prompt(pergunta, estilo)

            # Memória curta
            def normalizar_historico(historico, limite_pares=2, max_chars=300):
                if not historico:
                    return []
                ultimos = historico[-limite_pares*2:]
                seguro = []
                for m in ultimos:
                    # ignora mensagens sem content
                    content = m.get("content")
                    if content:
                        seguro.append({
                            "role": m.get("role", "user"),
                            "content": content[:max_chars]
                        })
                return seguro
            memoria = normalizar_historico(historico)
            messages = memoria + messages

            # ===== Payload =====
            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "frequency_penalty": 0.4,
                "presence_penalty": 0.25
            }

            # ===== Rate limit / backoff =====
            r = requests.post(
                GROQ_URL,
                json=payload,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=TIMEOUT
            )

            if r.status_code == 429:
                sleep_time = (2 ** tentativa) + random.random()
                print(f"[RATE LIMIT] HTTP 429. Tentativa {tentativa+1}/{tentativas}. Dormindo {sleep_time:.2f}s")
                time.sleep(sleep_time)
                continue

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

        except requests.exceptions.HTTPError as e:
            print(f"[HTTP ERROR] {e}")
            traceback.print_exc()
            if tentativa < tentativas - 1:
                time.sleep(1.5)
            else:
                return f"({random.choice(ERROS_ZEN)})"

        except Exception as e:
            print("[ERRO REAL NO CHIZU]")
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
