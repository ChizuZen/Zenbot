# Estado da Arte — Chizu

Este documento descreve o estado atual de implementação do Chizu — o que está em produção, como cada sistema funciona e qual o nível de maturidade de cada componente.

Restrições de projeto: **512MB de RAM** (Render Free), **custo zero** em infraestrutura de IA, **fidelidade total ao acervo** zen como princípio inegociável.

---

## Arquitetura

Aplicação **FastAPI** com três endpoints principais:

- `/` — interface web, serve o HTML completo com avatar e scripts
- `/ask` — endpoint principal, recebe perguntas da interface web
- `/whatsapp` — endpoint Twilio, recebe perguntas via WhatsApp

O núcleo fica em `core/` com dois arquivos independentes: `engine.py` (RAG, prompts e biblioteca) e `ai_provider.py` (conselho de IAs e configurações). O `web.py` orquestra os dois.

```
web.py  ──→  core/engine.py       (RAG + prompts)
        ──→  core/ai_provider.py  (IAs + configs)
        ──→  data/acervo_zen.json (biblioteca)
        ──→  data/koans.txt       (frases de bloqueio)
        ──→  static/              (CSS, JS, imagens)
```

---

## Busca e RAG

### TF-IDF Híbrido Light

O sistema de busca combina dois mecanismos sem usar RAM adicional:

**Busca semântica via TF-IDF** — converte pergunta e corpus em vetores numéricos e calcula similaridade de cosseno. Encontra trechos semanticamente próximos mesmo sem correspondência exata de palavras.

**Bônus por termo exato** — após o score semântico, aplica um multiplicador de 20% por cada termo da pergunta encontrado literalmente no chunk. Simula o comportamento do BM25 sem bibliotecas externas.

```python
scores[i] += scores[i] * bonus  # amplifica só quem já tem relevância semântica
```

O bônus é multiplicativo — um chunk irrelevante (score zero) não ganha nada. Apenas os já relevantes são amplificados.

### Normalização

Antes de qualquer comparação, pergunta e corpus passam por `_normalizar()`:

- Converte para minúsculas
- Remove acentos via `unicodedata.NFD`
- Remove pontuação
- Colapsa espaços múltiplos

Resultado: "Ansiedade", "ansiedade" e "ansiedade." encontram os mesmos chunks. "ansioso no emprego" e "ansiedade no trabalho" têm mais chance de retornar resultados comuns.

### top_k Dinâmico

Cada provider de IA tem seu `top_k` definido no `CONFIGS` do `ai_provider.py`. O `sortear_provider()` é chamado **antes** da busca, garantindo que o número de chunks recuperados seja compatível com a janela de contexto da IA sorteada:

| Provider | top_k | Motivo |
|---|---|---|
| Gemini | 5 | Janela grande (2048 tokens) |
| Groq | 5 | Janela confortável (512 tokens) |
| Cerebras | 4 | Janela menor (384 tokens) |
| SambaNova | 4 | Penalty alto, menor margem |

### Stopwords PT

O bônus híbrido ignora palavras irrelevantes via `_STOPWORDS_PT` — lista com termos normalizados (sem acentos) para coerência com a normalização do corpus:

```python
_STOPWORDS_PT = {
    "como", "para", "uma", "que", "nao", "com", "por", ...
}
```

Palavras curtas e funcionais não inflam o bônus. Termos com significado real — "zazen", "silencio", "impermanencia" — têm peso total.

---

## Prompt e Identidade

O system prompt é montado dinamicamente a cada resposta em 4 camadas encadeadas.

### Camada 1 — Identidade Base

```
Você é o Mestre Chizu, um sábio zen compassivo e poético.
```

Ponto de ancoragem de todas as respostas. Imutável.

### Camada 2 — Perfil do Mestre + Few-Shot

O mestre é **sorteado por afinidade** com o contexto recuperado: a função `sortear_perfil()` conta quantas vezes cada autor aparece nos chunks e sorteia com peso proporcional. Se o RAG trouxe Haemin Sunim, ele tem mais chance de ser sorteado.

Cada perfil inclui descrição de voz e **dois exemplos concretos** de pergunta/resposta ideal — o few-shot ancora o tom antes da resposta real:

```
### EXEMPLOS DE RESPOSTA IDEAL ###
Pergunta: Como lidar com a ansiedade?
Resposta: Caminhante, Haemin Sunim, em As Coisas que Você
Só Vê Quando Desacelera, sussurra que a ansiedade é como
chuva — não podemos impedi-la, mas podemos aprender a
dançar sob ela...
```

Os seis mestres disponíveis, cada um com voz distinta:

| Mestre | Voz |
|---|---|
| Haemin Sunim | Acolhedora, contemporânea, metáforas do cotidiano |
| Shunmyo Masuno | Minimalista e prática, cada palavra com intenção |
| Shunryu Suzuki | Gentil, bem-humorada, mente de principiante |
| Thich Nhat Hanh | Poética e meditativa, inter-ser |
| Eihei Dogen | Densa, filosófica, paradoxal |
| Osho | Irreverente, provocadora, iconoclasta |

### Camada 3 — REGRAS_ZEN

Bloco de instrução injetado em todo prompt após o perfil. Define comportamento, bloqueios e limites:

- Começar sempre com `"Caminhante,"` 
- Usar apenas o contexto recuperado — nunca inventar
- Mencionar autor e livro de forma natural e variada
- Máximo de 5 frases — contadas e cortadas sem exceção
- Se contexto `VAZIO` → responder `BLOQUEADO`
- Bloquear qualquer nome próprio famoso fora dos mestres do acervo

### Camada 4 — FONTES AUTORIZADAS

Após as REGRAS_ZEN, o sistema injeta automaticamente os autores e livros reais presentes nos chunks recuperados:

```
### FONTES AUTORIZADAS NESTA RESPOSTA ###
Cite APENAS os autores e livros listados abaixo:
  - Haemin Sunim · As Coisas que Você Só Vê Quando Desacelera
  - Thich Nhat Hanh · Silêncio
PROIBIDO citar qualquer outro livro ou autor, mesmo que
você os conheça do treinamento.
```

Isso impede que a IA cite "Silêncio" (Thich) quando o chunk recuperado é de outro livro — problema real identificado em testes.

### Estilo por IA

Além do perfil do mestre, cada provider recebe um bloco de estilo adicional injetado pelo `_ajustar_system()`:

| IA | Estilo |
|---|---|
| Gemini | Criativo e surpreendente, imagens inesperadas |
| Groq | Direto e conciso, uma ideia central |
| Cerebras | Simples e acessível, linguagem calorosa |
| SambaNova | Contemplativo e sereno, ritmo lento |

---

## Conselho de IAs

Quatro providers ativos em rodízio aleatório com fallback automático:

| Provider | Modelo | temperature | top_p |
|---|---|---|---|
| Google | Gemini 2.5 Flash | 0.35 | 0.40 |
| Groq | Llama 3.3 70B | 0.55 | 0.85 |
| Cerebras | Llama 3.1 8B | 0.35 | 0.85 |
| SambaNova | Llama 3.1 8B | 0.75 | 0.90 |

Anthropic (Claude Haiku) e Ollama (Phi4 Mini local) estão implementados e comentados — prontos para reativar sem alteração de arquitetura.

### Reforço Rebelde

Groq, Cerebras e SambaNova recebem um bloco adicional com exemplos explícitos de bloqueio — esses modelos têm histórico de ignorar regras de identidade:

```
Exemplos que devem retornar BLOQUEADO:
- 'o que Steve Jobs aprendeu com o zen' → BLOQUEADO
- 'o que Einstein pensava sobre meditação' → BLOQUEADO
```

### Tratamento de Erros

- **429** — dorme 2 segundos e tenta o próximo provider
- **503** — pula imediatamente para o próximo
- **Qualquer outro erro** — loga e tenta o próximo
- **Todos falharam** — retorna frase zen de fallback

---

## Memória de Conversa

### SESSION_ID

Gerado no frontend com `crypto.randomUUID()` ao abrir a aba. Some ao fechar o navegador. Garante sessões independentes por aba — dois usuários no mesmo IP têm históricos separados.

### Injeção no Prompt

As últimas 3 trocas da sessão são injetadas como mensagens `user/assistant` entre o system prompt e a pergunta atual:

```
[system]  → identidade + perfil + regras + contexto
[user]    → pergunta anterior
[assistant] → resposta anterior
[user]    → pergunta anterior 2
[assistant] → resposta anterior 2
[user]    → pergunta atual       ← a nova pergunta
```

### Proteção de RAM

- Máximo de 10 trocas salvas por sessão
- Pergunta truncada em 150 caracteres ao salvar
- Resposta truncada em 200 caracteres ao salvar
- Ao passar de 1000 sessões simultâneas em RAM, o dicionário é limpo

---

## Segurança

Quatro camadas independentes e cumulativas:

**1. Rate Limit** — máximo de 10 requests por minuto por IP. Implementado com janela deslizante em `_contadores`.

**2. Sanitização da Pergunta** — 15 padrões regex bloqueiam tentativas de injeção de prompt antes de qualquer processamento:

```python
r"ignore\s+(previous|all|above)",
r"a partir de agora",
r"finja\s+que",
r"jailbreak",
# + 11 outros padrões
```

Limite de 400 caracteres por pergunta. Retorna `None` em caso de violação — o sistema responde com koan aleatório.

**3. maxlength no Input** — `maxlength="400"` no HTML impede fisicamente digitar além do limite na interface web.

**4. Whitelist de Autor** — o `autor_filtro` só é aceito se estiver explicitamente em `AUTORES_DISPONIVEIS`. Qualquer valor não reconhecido é descartado silenciosamente.

### Interceptação de Resposta

`is_bloqueado()` verifica se a resposta da IA contém os marcadores `BLOQUEADO` ou `VAZIO` e os substitui automaticamente por uma frase aleatória do `data/koans.txt` + "Vá praticar Zazen."

---

## Debug Local

`is_local(request)` detecta automaticamente o ambiente pelo header `host`:

```python
def is_local(request: Request) -> bool:
    host = request.headers.get("host", "")
    return host.startswith("localhost") or host.startswith("127.0.0.1")
```

Em produção, `DEBUG = False` automaticamente — sem configuração manual, sem risco de logs vazarem em produção.

---

## Roadmap — Status Atual

| Funcionalidade | Status |
|---|---|
| Busca híbrida light (TF-IDF + bônus exato) | ✅ Produção |
| Normalização da pergunta antes do RAG | ✅ Produção |
| top_k dinâmico por provider | ✅ Produção |
| Few-shot nos PERFIS_MESTRES | ✅ Produção |
| Ancoragem de livros reais no prompt | ✅ Produção |
| Memória de conversa por sessão | ✅ Produção |
| Proteção de RAM do histórico | ✅ Produção |
| Segurança em 4 camadas | ✅ Produção |
| Reforço rebelde com exemplos explícitos | ✅ Produção |
| Limite 400 chars no input HTML | ✅ Produção |
| Limite 400 chars no microfone (script.js) | ⏳ Pendente |
| Embeddings semânticos (sentence-transformers) | 🔵 Nível PRO |
| BM25 híbrido real | 🔵 Nível PRO |
| Re-ranking por modelo | 🔵 Nível PRO |

**Legenda:** ✅ em produção · ⏳ pendente · 🔵 fora do escopo 512MB

---

*Ver também: [Pipeline](pipeline.md) · [RAG](rag.md) · [Modelos e LLMs](modelos-e-llms.md) · [Engenharia de Prompts](engenharia-de-prompts.md) · [Roadmap](roadmap.md)*
