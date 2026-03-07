import os
import time
import random
import requests
import traceback
from core.engine import montar_prompt
from core.ai_provider import FreeAIProvider
from sentence_transformers import SentenceTransformer

# Usamos o 'all-MiniLM-L6-v2' por ser leve para o plano gratuito do Render
model = SentenceTransformer('all-MiniLM-L6-v2')

# =============================
# Configurações da API
# =============================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
TIMEOUT = 30

# =============================
# Mensagens zen
# =============================

RESPOSTAS_ZEN = [
    "A resposta não está nas palavras, mas no silêncio entre elas.",
    "A mente que pergunta já contém a resposta.",
    "Quando nada surge, o vazio se revela.",
    "Talvez não haja nada a buscar.",
    "Observe este instante antes de perguntar novamente.",
    "O caminho não se revela ao ser forçado.",
    "A pergunta correta dissolve a necessidade da resposta.",
    "A resposta está no silêncio, não nas palavras.",
    "Observe sua própria mente enquanto pergunta.",
    "Talvez a pergunta seja mais importante que a resposta.",
    "O vento levou a resposta... tente novamente mais tarde.",
    "Não há palavras para isso, apenas prática."
]

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
# Estilo
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
# Motor de resposta
# =============================


ai_provider = FreeAIProvider()

import random

# Adicionamos os novos parâmetros com valores padrão (default)
def responder(pergunta, historico=None, temperature=0.4, max_tokens=180, 
              top_p=0.9, frequency_penalty=0.0, presence_penalty=0.0):
    """
    Orquestra a resposta do Mestre Chizu.
    Aceita parâmetros de tuning quando chamados pela oficina, 
    mas mantém os padrões para o uso normal via web.py.
    """
    estilo = detectar_estilo(pergunta)
    pergunta_limpa = limpar_comando(pergunta)

    try:
        # 1. Monta o prompt (System + RAG + Pergunta)
        messages = montar_prompt(pergunta_limpa, estilo)
        
        # 2. Normaliza o histórico
        # Juça, aqui a memória já vem limitada pelo 'context_count' da oficina!
        def normalizar_historico(hist, max_chars=300):
            if not hist: return []
            return [
                {
                    "role": m.get("role", "user"), 
                    "content": str(m.get("content", ""))[:max_chars]
                } for m in hist if isinstance(m, dict)
            ]

        memoria = normalizar_historico(historico)
        full_messages = [messages[0]] + memoria + [messages[-1]]

        # 3. MÁGICA DO FALLBACK: Repassa TODOS os parâmetros para o ai_provider
        # O ai_provider.chat agora recebe a "mesa de som" completa
        resposta_llm, ia_nome = ai_provider.chat(
            full_messages, 
            temperature=temperature, 
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        # 4. Polimento Zen na resposta
        if isinstance(resposta_llm, tuple):
            resposta_llm = resposta_llm[0]
            
        resposta_llm = str(resposta_llm).strip()
        
        if "</think>" in resposta_llm:
            resposta_llm = resposta_llm.split("</think>")[-1].strip()

        if not resposta_llm.endswith((".", "。", "!", "?", "...", "—")):
            resposta_llm += "..."

        return resposta_llm, ia_nome

    except Exception as e:
        print(f"[LOG CHIZU] Falha total no sistema: {e}")
        return random.choice(RESPOSTAS_ZEN)
       
# =============================
# Inicialização
# =============================

def verificar_chave():
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY não configurada.")
        exit(1)


def aquecer_modelo():
    print(random.choice(AQUECIMENTO))
    