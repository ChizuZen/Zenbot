# Pipeline

Este capítulo descreve **todo o fluxo de funcionamento do Chizu**, desde a preparação dos textos até a entrega da resposta ao usuário.

---

## O que é um pipeline?

Pipeline é uma cadeia organizada de etapas onde a saída de uma etapa se torna a entrada da próxima.

No Chizu, o pipeline opera em dois momentos distintos:

- **Ingestão** — preparação dos textos, feita uma vez
- **Consulta** — resposta a cada pergunta do usuário

---

## Visão geral

```text
INGESTÃO
Textos brutos → Limpeza → Chunks → Embeddings → embeddings_bge.json

CONSULTA
Pergunta → Embedding → Busca semântica → Contexto → LLM → Resposta
```

---

## Fase de ingestão

### Coleta dos textos

O acervo do Chizu é composto por livros e textos zen digitalizados, organizados por autor.

Fontes aceitas:

- Livros em PDF
- Arquivos de texto
- Arquivos Markdown
- Anotações transcritas

### Limpeza

Antes de fragmentar, os textos passam por limpeza:

- Remoção de quebras desnecessárias
- Correção de caracteres estranhos
- Eliminação de ruído visual
- Padronização de encoding

### Fragmentação — chunking

O texto limpo é dividido em pequenos blocos chamados **chunks**.

Por quê fragmentar:

- Modelos de linguagem têm limites de contexto
- Blocos menores permitem busca mais precisa
- Cada fragmento pode ser recuperado individualmente

Tamanho típico: entre 300 e 800 caracteres.

### Geração de embeddings e armazenamento

Cada chunk é representado como um vetor numérico e armazenado em `data/embeddings_bge.json`.

Cada registro contém:

```json
{
  "texto": "Respire e volte ao momento presente.",
  "autor": "Thich Nhat Hanh",
  "fonte": "Silêncio",
  "embedding": [0.18, -0.33, 0.71, 0.04, -0.55]
}
```

Esse arquivo é a **memória permanente do Chizu**.

---

## Fase de consulta

### Recebimento da pergunta

A pergunta chega ao sistema via:

- Interface web — endpoint `/ask`
- WhatsApp — endpoint `/whatsapp`

Exemplo de payload:

```json
{
  "pergunta": "O que é mente zen?"
}
```

### Busca semântica

A função `buscar_contexto` em `core/engine.py` converte a pergunta em vetor e compara com os embeddings armazenados usando **TF-IDF** com similaridade de cosseno.

Parâmetros:

- `top_k = 3` — retorna os 3 trechos mais próximos
- `threshold = 0.05` — descarta resultados abaixo desse score

Se nenhum trecho superar o threshold, o contexto retorna `VAZIO`.

### Montagem do contexto

Os trechos recuperados são organizados com identificação de fonte:

```text
[FONTE: Thich Nhat Hanh no livro 'Silêncio']
Respire e volte ao momento presente.

---

[FONTE: Shunryu Suzuki no livro 'Mente Zen, Mente de Principiante']
Na mente do principiante há muitas possibilidades...
```

### Construção do prompt

A função `montar_prompt` em `core/engine.py` monta o prompt final com três camadas:

- **Identidade** — quem é o Chizu
- **Perfil do mestre** — a voz sorteada para aquela resposta
- **Regras Zen** — instruções de comportamento e bloqueio
- **Contexto** — os trechos recuperados pelo RAG

A estrutura detalhada do prompt está em [Engenharia de Prompts](17-engenharia-de-prompts.md).

### Geração da resposta

O prompt é enviado ao Conselho de IAs via `core/ai_provider.py`.

A IA recebe:

- O system prompt completo
- O histórico recente da conversa (até 8 mensagens)
- A pergunta do usuário

E gera uma resposta em no máximo 5 frases, na voz do mestre sorteado.

### Entrega ao usuário

A resposta passa por limpeza final — remoção de artefatos como `(Silêncio)` e `(pausa)` — e é devolvida com identificação do mestre e da IA que respondeu:

```text
Caminhante, Thich Nhat Hanh, em Silêncio, nos convida a...

— via Thich Nhat Hanh · Gemini 2.5 Flash · Google
```

---

## TF-IDF — a técnica de busca atual

O sistema atual usa **TF-IDF** (Term Frequency–Inverse Document Frequency) para indexar e buscar os ensinamentos.

**TF — Term Frequency**
Quantas vezes uma palavra aparece no texto.
"silêncio" aparece 5 vezes → tem peso alto.

**IDF — Inverse Document Frequency**
O quanto a palavra é rara no conjunto de todos os textos.
"o", "a", "de" aparecem em todo lugar → peso baixo.
"zazen" aparece em poucos textos → peso alto.

A multiplicação TF × IDF dá um score para cada palavra.
Com isso o sistema transforma pergunta e textos em vetores numéricos e calcula qual texto é mais próximo da pergunta.

**No Chizu:** quando o usuário pergunta *"como lidar com a ansiedade?"*, o TF-IDF percorre os ensinamentos e retorna os 3 mais relevantes como contexto para a resposta.

**Limitação:** o TF-IDF vê **palavras exatas** — não entende que "angústia" e "ansiedade" são semanticamente próximas. O sistema anterior com `sentence-transformers` fazia essa comparação semântica real. Se o contexto retornado estiver vazio com frequência, vale ajustar o `top_k` ou revisar a granularidade dos chunks.

---

## Analogia

O pipeline do Chizu funciona como uma biblioteca com um bibliotecário muito paciente.

- Os livros chegam e são organizados em pequenos trechos
- Cada trecho é catalogado por significado
- Quando alguém faz uma pergunta, o bibliotecário encontra os trechos relevantes
- Um mestre zen lê esses trechos e elabora a resposta
