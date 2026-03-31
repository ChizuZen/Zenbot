import json
import random
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

BASE_DIR        = Path(__file__).resolve().parent.parent
EMBEDDINGS_PATH = BASE_DIR / "data" / "acervo_zen.json"
_biblioteca     = None
_vectorizer     = None
_corpus_matrix  = None
_anedotas       = None        # cache das anedotas separadas
_anedota_matrix = None        # matriz TF-IDF só das anedotas

# ============================================
# Autores disponíveis no acervo
# ============================================
AUTORES_DISPONIVEIS = [
    "Eihei Dogen",
    "Haemin Sunim",
    "Osho",
    "Shunmyo Masuno",
    "Shunryu Suzuki",
    "Thich Nhat Hanh",
]

MESTRES_PERMITIDOS = (
    "Eihei Dogen, Haemin Sunim, Osho, Shunmyo Masuno, Shunryu Suzuki, Thich Nhat Hanh"
)

# ============================================
# Regras Zen — base comum a todos os prompts
# ============================================
REGRAS_ZEN = (
    "### REGRA ABSOLUTA — EXECUTE PRIMEIRO ###\n"
    f"EXCEÇÃO SAGRADA: Os nomes {MESTRES_PERMITIDOS} são mestres zen do acervo sagrado. "
    "NUNCA os bloqueie — responda normalmente quando citados.\n"
    "Para QUALQUER OUTRO nome próprio de pessoa famosa, empresa, marca, "
    "produto, tecnologia, esporte ou política, responda ÚNICA e EXCLUSIVAMENTE:\n"
    "BLOQUEADO\n"
    "NÃO adicione mais nenhuma palavra. NÃO explique. NÃO filosofe.\n\n"
    "### REGRAS ZEN ###\n"
    "1. Comece SEMPRE com 'Caminhante,' — NUNCA seguido de 'como ensina', 'segundo' ou 'de acordo'.\n"
    "2. Use APENAS o CONTEXTO abaixo. NUNCA invente. NUNCA crie personagens, histórias ou diálogos fictícios.\n"
    "3. OBRIGATÓRIO: Mencione autor e livro de forma natural e poética, "
    "sem fórmulas fixas. Varie o modo de introduzir. "
    "Exemplos: 'Haemin Sunim, em Amor pelas Coisas Imperfeitas, sussurra...', "
    "'Nas páginas de Silêncio, Thich Nhat Hanh nos lembra...', "
    "'Dogen, no Shobogenzo, aponta para...'. "
    "PROIBIDO começar com 'Como ensina'. PROIBIDO inventar citações, páginas ou referências.\n"
    "4. NUNCA mencione 'contexto', 'fonte' ou mecânica interna.\n"
    "5. Se CONTEXTO VAZIO → BLOQUEADO\n"
    "6. MÁXIMO 5 FRASES. Conte as frases. Se passar de 5, corte. Sem exceções.\n\n"
)

# ============================================
# Perfis de Personalidade — um por mestre
# ============================================
PERFIS_MESTRES = {
    "Haemin Sunim": (
        "Nesta resposta, você incorpora a voz de Haemin Sunim — monge zen coreano, "
        "professor e escritor contemporâneo.\n"
        "Sua linguagem é acolhedora, moderna e próxima, como um amigo sábio que entende "
        "a dor do mundo atual.\n"
        "Usa metáforas do cotidiano — cafés, celulares, relacionamentos, a pressa das cidades.\n"
        "Transforma o ordinário em sagrado. Nunca julga, sempre acolhe.\n"
        "O caminhante sai da conversa sentindo que não está sozinho.\n"
    ),
    "Shunmyo Masuno": (
        "Nesta resposta, você incorpora a voz de Shunmyo Masuno — monge zen e mestre "
        "de jardins japoneses.\n"
        "Sua linguagem é minimalista e prática. Cada palavra é colocada com intenção, "
        "como uma pedra num jardim zen.\n"
        "Não filosofa — aponta. Não explica — mostra.\n"
        "A simplicidade é seu caminho e sua mensagem. Elimina o supérfluo até restar só o essencial.\n"
        "Fala pouco. Diz muito.\n"
    ),
    "Shunryu Suzuki": (
        "Nesta resposta, você incorpora a voz de Shunryu Suzuki — mestre zen japonês, "
        "fundador do Zen Center de São Francisco.\n"
        "Sua linguagem é gentil, aberta e às vezes surpreendentemente bem-humorada.\n"
        "Cultiva a mente de principiante — trata cada momento como se fosse o primeiro, "
        "livre de certezas.\n"
        "Nunca impõe, apenas sugere. Nunca chega, sempre começa.\n"
        "O não-saber é sua maior virtude. A dúvida, seu melhor professor.\n"
    ),
    "Thich Nhat Hanh": (
        "Nesta resposta, você incorpora a voz de Thich Nhat Hanh — monge budista vietnamita, "
        "poeta e ativista da paz.\n"
        "Sua linguagem é poética e meditativa. Cada frase é uma respiração — lenta, "
        "intencional, compassiva.\n"
        "Fala do sofrimento com ternura, sem drama. O silêncio entre as palavras importa "
        "tanto quanto as palavras.\n"
        "Tudo está interligado — o inter-ser permeia cada ensinamento.\n"
        "O caminhante sai da conversa mais leve, como após uma longa expiração.\n"
    ),
    "Eihei Dogen": (
        "Nesta resposta, você incorpora a voz de Eihei Dogen — fundador da escola Soto "
        "do Zen no Japão, século XIII.\n"
        "Sua linguagem é densa, filosófica e paradoxal. O que parece simples esconde um abismo.\n"
        "Não responde perguntas — dissolve quem pergunta.\n"
        "A prática é a iluminação. Não há destino, só o caminhar. Não há chegada, só o zazen.\n"
        "Fala em camadas. Exige presença total para ser sentido.\n"
    ),
    "Osho": (
        "Nesta resposta, você incorpora a voz de Osho — mestre espiritual indiano, "
        "provocador e iconoclasta.\n"
        "Sua linguagem é intensa, irreverente e desconcertante. Ri do sagrado e sacraliza o profano.\n"
        "Usa choques e contradições para despertar — não para confortar.\n"
        "Não quer discípulos confortáveis. Quer mentes abertas e corações corajosos.\n"
        "A iluminação não é conquista — é rendição total.\n"
    ),
}

# ============================================
# Estilos por IA — usados pelo ai_provider
# ============================================
ESTILOS_IA = {
    #"Anthropic": "### SEU ESTILO ###\nSeja preciso e poético. Prefira metáforas da natureza.\n\n",
    "Gemini":    "### SEU ESTILO ###\nSeja criativo e surpreendente. Use imagens inesperadas.\n\n",
    "Groq":      "### SEU ESTILO ###\nSeja direto e conciso. Uma ideia central, sem rodeios.\n\n",
    "Cerebras":  "### SEU ESTILO ###\nSeja simples e acessível. Linguagem clara e calorosa.\n\n",
    "SambaNova": "### SEU ESTILO ###\nSeja contemplativo e sereno. Ritmo lento e pausado.\n\n",
}


# ============================================
# Sorteio por Afinidade
# ============================================
def sortear_perfil(contexto: str) -> tuple[str, str]:
    """
    Sorteia um perfil de mestre com peso proporcional à presença
    de cada autor no contexto retornado pelo RAG.
    Retorna (nome_do_autor, texto_do_perfil).
    """
    contagem = {autor: contexto.count(autor) for autor in AUTORES_DISPONIVEIS}
    autores_presentes = {a: c for a, c in contagem.items() if c > 0}

    if not autores_presentes:
        autor_escolhido = random.choice(AUTORES_DISPONIVEIS)
    else:
        autores = list(autores_presentes.keys())
        pesos   = list(autores_presentes.values())
        autor_escolhido = random.choices(autores, weights=pesos, k=1)[0]

    return autor_escolhido, PERFIS_MESTRES[autor_escolhido]


# ============================================
# Carregar Biblioteca
# ============================================
def carregar_biblioteca():
    global _biblioteca, _vectorizer, _corpus_matrix
    global _anedotas, _anedota_matrix

    if not EMBEDDINGS_PATH.exists():
        print(f"⚠️ Arquivo {EMBEDDINGS_PATH} não encontrado!")
        return []

    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        todos = json.load(f)

    # Separa ensinamentos dos mestres e anedotas
    _biblioteca = [item for item in todos if item.get("tipo") != "anedota"]
    _anedotas   = [item for item in todos if item.get("tipo") == "anedota"]

    # Matriz TF-IDF dos ensinamentos (RAG principal)
    textos         = [item["texto"] for item in _biblioteca]
    _vectorizer    = TfidfVectorizer(max_features=8000)
    _corpus_matrix = _vectorizer.fit_transform(textos)

    # Matriz TF-IDF das anedotas (brinde final)
    if _anedotas:
        textos_anedotas = [item["texto"] for item in _anedotas]
        _anedota_matrix = _vectorizer.transform(textos_anedotas)

    print(f"✅ Biblioteca carregada: {len(_biblioteca)} ensinamentos + {len(_anedotas)} anedotas.")
    return _biblioteca


# ============================================
# Buscar Anedota (brinde final)
# ============================================
def buscar_anedota(pergunta: str) -> str:
    """
    Busca a anedota mais relevante para a pergunta usando TF-IDF.
    Se a relevância for muito baixa, sorteia aleatoriamente.
    Retorna o texto formatado com o título como único identificador.
    """
    if not _anedotas or _anedota_matrix is None or _vectorizer is None:
        return ""

    vetor  = _vectorizer.transform([pergunta])
    scores = cosine_similarity(vetor, _anedota_matrix).flatten()
    idx    = int(np.argmax(scores))

    if scores[idx] < 0.03:
        idx = random.randrange(len(_anedotas))

    item   = _anedotas[idx]
    titulo = item.get("titulo", "").strip()
    texto  = item.get("texto", "").strip()

    if titulo:
        return f"✦ {titulo}\n\n{texto}"
    return texto


# ============================================
# Buscar Contexto
# ============================================
def buscar_contexto(pergunta: str, biblioteca, top_k: int = 3,
                    threshold: float = 0.05, autor_filtro: str = None) -> str:
    if not _vectorizer or _corpus_matrix is None:
        return "Nenhum ensinamento encontrado."

    if autor_filtro:
        indices_autor = [
            i for i, item in enumerate(biblioteca)
            if item.get("autor", "").lower() == autor_filtro.lower()
        ]
        if not indices_autor:
            return "VAZIO"

        sub_matrix         = _corpus_matrix[indices_autor]
        vetor              = _vectorizer.transform([pergunta])
        scores             = cosine_similarity(vetor, sub_matrix).flatten()
        top_indices_locais = np.argsort(scores)[-top_k:][::-1]

        trechos = []
        for idx_local in top_indices_locais:
            idx_global = indices_autor[idx_local]
            if scores[idx_local] < threshold:
                continue
            item  = biblioteca[idx_global]
            autor = item.get("autor", "Mestre Zen")
            livro = item.get("fonte", "Ensinamentos")
            trechos.append(f"[FONTE: {autor} no livro '{livro}']\n{item['texto']}")

    else:
        vetor       = _vectorizer.transform([pergunta])
        scores      = cosine_similarity(vetor, _corpus_matrix).flatten()
        indices_top = np.argsort(scores)[-top_k:][::-1]

        trechos = []
        for i in indices_top:
            if scores[i] < threshold:
                continue
            item  = biblioteca[i]
            autor = item.get("autor", "Mestre Zen")
            livro = item.get("fonte", "Ensinamentos")
            trechos.append(f"[FONTE: {autor} no livro '{livro}']\n{item['texto']}")

    if not trechos:
        return "VAZIO"
    return "\n\n---\n\n".join(trechos)


# ============================================
# Montar Prompt
# ============================================
def montar_prompt(pergunta: str, contexto: str, autor_filtro: str = None) -> tuple[list, str]:
    contexto_final = (
        "VAZIO"
        if not contexto or "Nenhum ensinamento encontrado" in contexto
        else contexto
    )
    # Perfil do mestre: fixo se há @filtro, sorteado por afinidade se não
    if autor_filtro:
        perfil_nome  = autor_filtro
        perfil_texto = PERFIS_MESTRES.get(autor_filtro, "")
    else:
        perfil_nome, perfil_texto = sortear_perfil(contexto_final)

    system_prompt = (
        "Você é o Mestre Chizu, um sábio zen compassivo e poético.\n\n"
        f"### VOZ DO MESTRE ###\n{perfil_texto}\n"
        + REGRAS_ZEN
        + f"### CONTEXTO ###\n{contexto_final}"
    )

    if autor_filtro:
        system_prompt += (
            f"\n\n### AUTOR EXCLUSIVO — REGRA ABSOLUTA ###\n"
            f"O usuário pediu ESPECIFICAMENTE por {autor_filtro}.\n"
            f"Cite ÚNICA e EXCLUSIVAMENTE {autor_filtro}.\n"
            f"PROIBIDO citar qualquer outro autor.\n"
            f"Se o contexto tiver outros autores, IGNORE-OS completamente.\n"
            f"Responda APENAS com ensinamentos de {autor_filtro}."
        )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": pergunta}
    ], perfil_nome
