import json
import math
import random
import requests
import os
from pathlib import Path

# =============================
# Configurações gerais
# =============================

EMBED_URL = os.getenv("EMBED_URL", "http://localhost:11434/api/embeddings")
MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

THRESHOLD = 0.30

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================
# Prompts por estilo cognitivo
# =============================

STYLE_MAP = {
    "aforismo": BASE_DIR / "styles" / "aforismos_zen.txt",
    "koan": BASE_DIR / "styles" / "koans_classicos.txt",
    "meditacao": BASE_DIR / "styles" / "meditacoes_guiadas.txt",
    "padrao": BASE_DIR / "styles" / "system_prompt.txt"
}

def load_style_prompt(style: str) -> str:
    path = STYLE_MAP.get(style, STYLE_MAP["padrao"])
    return path.read_text(encoding="utf-8")

# =============================
# Fallback contemplativo
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

# =============================
# Funções matemáticas
# =============================

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-9)

# =============================
# Embeddings
# =============================

def gerar_embedding(texto):
    payload = {
        "model": MODEL,
        "input": texto
    }
    r = requests.post(EMBED_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["data"][0]["embedding"]

# =============================
# Busca semântica (RAG)
# =============================

def buscar_blocos(pergunta, top_k=3):
    with open("data/embeddings_bge.json", "r", encoding="utf-8") as f:
        base = json.load(f)

    emb_pergunta = gerar_embedding(pergunta)

    scores = []
    for item in base:
        sim = cosine_similarity(emb_pergunta, item["embedding"])
        scores.append((sim, item["texto"]))

    scores.sort(reverse=True, key=lambda x: x[0])

    if not scores:
        return [random.choice(RESPOSTAS_ZEN)]

    top_score = scores[0][0]

    if top_score < THRESHOLD:
        return [random.choice(RESPOSTAS_ZEN)]

    return [texto for _, texto in scores[:top_k]]

# =============================
# Motor cognitivo principal
# =============================

def montar_prompt(pergunta: str, estilo: str = "padrao") -> list:
    """
    Constrói o payload final para o LLM,
    combinando estilo cognitivo + RAG + pergunta.
    """

    style_prompt = load_style_prompt(estilo)
    blocos = buscar_blocos(pergunta)

    contexto = "\n\n".join(blocos)

    messages = [
        {
            "role": "system",
            "content": style_prompt
        },
        {
            "role": "system",
            "content": f"Contexto relevante:\n{contexto}"
        },
        {
            "role": "user",
            "content": pergunta
        }
    ]

    return messages