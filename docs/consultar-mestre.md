#  Expansão do Acervo e Filtro por Autor

## Contexto

Nesta sessão expandimos o acervo do Chizu com dois novos mestres — **Eihei Dogen** e **Osho** — e implementamos a capacidade de o usuário direcionar perguntas a um mestre específico usando o comando `@`.

---

## Fase 1 — Expansão do Acervo (Novos Embeddings)

### Problema

O acervo original continha apenas 5 autores (Haemin Sunim, Shunmyo Masuno, Shunryu Suzuki, Thich Nhat Hanh e uma versão anterior sem Dogen e Osho). Além disso, os chunks do `embeddings_bge.json` não tinham os campos `autor` e `fonte` devidamente estruturados, causando erros de grafia nas citações.

### Solução

Criamos dois scripts Python que rodam **localmente** (fora do Render) e geram o `embeddings_bge.json` final:

```text
CLAUDE_LIVROS/
├── sripts/
│   ├── preparar_textos.py    ← converte PDFs/TXTs em chunks
│   └── gerar_embeddings.py   ← monta o JSON final com metadados
├── textos/                   ← PDFs e TXTs dos autores
└── data/
    ├── chunks_preparados.txt ← intermediário (inspecionável)
    └── embeddings_bge.json   ← arquivo final → vai para o Render
```

### Script `preparar_textos.py`

- Lê PDFs com **PyMuPDF** e TXTs diretamente
- Limpa ruídos comuns de PDFs (hífens de quebra, números de página, espaços duplos)
- Divide o texto em chunks de **1000 caracteres com overlap de 200** (garante que ensinamentos não sejam cortados no meio)
- Salva em `data/chunks_preparados.txt` com metadados explícitos por chunk:

```text
==== NOVO CHUNK ====
AUTOR: Eihei Dogen
FONTE: Shobogenzo Zuimonki — Livro 1
TEXTO:
[conteúdo do chunk]
---
```

### Script `gerar_embeddings.py`

- Lê o `chunks_preparados.txt`
- Descarta chunks com menos de 100 caracteres (ruído de PDF)
- Gera o `embeddings_bge.json` com campos `id`, `autor`, `fonte`, `texto`
- Exibe relatório de distribuição por autor ao final

### Resultado obtido

```text
Eihei Dogen          624 chunks
Haemin Sunim         694 chunks
Osho                 320 chunks
Shunmyo Masuno       516 chunks
Shunryu Suzuki       312 chunks
Thich Nhat Hanh      232 chunks
─────────────────────────────
Total              2.698 chunks
```

### Como executar

```text
cd /Volumes/CT500MX5/Downloads/Chizu.ZenBot/CLAUDE_LIVROS/sripts
python3 preparar_textos.py   # gera chunks_preparados.txt
python3 gerar_embeddings.py  # gera embeddings_bge.json
```

Após validar, copiar para o projeto:

```text
cp ../data/embeddings_bge.json /Volumes/CT500MX5/SITE/chizu/data/embeddings_bge.json
```

### Observação técnica

O nome `embeddings_bge.json` é histórico — o arquivo **não contém vetores BGE**. A busca por similaridade é feita em runtime pelo `engine.py` usando **TF-IDF (sklearn)**, que reconstrói a matriz a cada inicialização do servidor. Isso mantém o sistema leve e sem dependência de API externa.

---

## Fase 2 — Filtro por Autor

### Problema

O Chizu sempre buscava no acervo completo, sem possibilidade de direcionar a pergunta a um mestre específico. Para testes e para o usuário que quer ouvir um mestre em particular, era necessário um mecanismo de filtro.

### Solução

Implementamos o filtro em três camadas:

#### 1. `core/engine.py` — `buscar_contexto`

Adicionado o parâmetro `autor_filtro: str = None`. Quando informado, a busca TF-IDF é feita apenas nos chunks daquele autor:

```text
def buscar_contexto(pergunta, biblioteca, top_k=3,
                    threshold=0.05, autor_filtro=None):
    if autor_filtro:
        indices_autor = [
            i for i, item in enumerate(biblioteca)
            if item.get("autor", "").lower() == autor_filtro.lower()
        ]
        sub_matrix = _corpus_matrix[indices_autor]
        # busca TF-IDF apenas no sub_matrix do autor
```

#### 2. `core/engine.py` — `montar_prompt`

Adicionado reforço no system prompt quando há filtro ativo:

```text
def montar_prompt(pergunta, contexto, autor_filtro=None):
    ...
    if autor_filtro:
        system_prompt += (
            f"\n\n### AUTOR EXCLUSIVO — REGRA ABSOLUTA ###\n"
            f"O usuário pediu ESPECIFICAMENTE por {autor_filtro}.\n"
            f"Cite ÚNICA e EXCLUSIVAMENTE {autor_filtro}.\n"
            f"PROIBIDO citar qualquer outro autor.\n"
            f"Se o contexto tiver outros autores, IGNORE-OS completamente."
        )
```

#### 3. `static/script.js` — Comando `@`

O usuário digita `@NomeMestre pergunta` na interface. O JavaScript detecta o `@`, extrai o autor e envia o campo `autor` no payload:

```text
const AUTORES_MAP = {
    'dogen':   'Eihei Dogen',
    'osho':    'Osho',
    'haemin':  'Haemin Sunim',
    'sunim':   'Haemin Sunim',
    'masuno':  'Shunmyo Masuno',
    'suzuki':  'Shunryu Suzuki',
    'thich':   'Thich Nhat Hanh',
    'hanh':    'Thich Nhat Hanh',
};

// Payload enviado ao /ask:
// { "pergunta": "o que é zazen?", "autor": "Eihei Dogen" }
```

Sem `@`, o comportamento é idêntico ao original — Chizu busca no acervo completo.

#### 4. `core/ai_provider.py` — Exceção Sagrada

A `_BASE` (system prompt base de todas as IAs) foi atualizada para não bloquear os nomes dos mestres pela regra absoluta:

```text
_BASE = (
    ...
    "EXCEÇÃO SAGRADA: Os nomes Eihei Dogen, Haemin Sunim, Osho, Shunmyo Masuno, "
    "Shunryu Suzuki e Thich Nhat Hanh são mestres zen do acervo sagrado. "
    "NUNCA os bloqueie — responda normalmente quando citados.\n"
    ...
)
```

### Exemplos de uso

| Comando | Mestre consultado |
|---|---|
| `@Dogen o que é zazen?` | Eihei Dogen |
| `@Osho o que é iluminação?` | Osho |
| `@Suzuki o que é mente zen?` | Shunryu Suzuki |
| `@Masuno como viver simples?` | Shunmyo Masuno |
| `@Haemin como lidar com a pressa?` | Haemin Sunim |
| `@Sunim como desacelerar?` | Haemin Sunim |
| `@Thich como meditar?` | Thich Nhat Hanh |
| `o que é paz?` | Chizu escolhe |

### Problemas conhecidos (pendentes)

- **Osho** — alguns modelos (Cerebras, Groq) ainda bloqueiam o nome apesar da exceção sagrada, por associarem "Osho" a figura controversa fora do Zen.
- **Alucinação de títulos** — modelos menores (Cerebras, SambaNova) ocasionalmente inventam títulos de livros não presentes no acervo (ex: *"A Arte do Amor"* de Thich Nhat Hanh).
- **Cerebras** — mais resistente à instrução de autor exclusivo; tende a misturar autores mesmo com filtro ativo.

---

## Arquivos modificados nesta sessão

| Arquivo | Alteração |
|---|---|
| `CLAUDE_LIVROS/sripts/preparar_textos.py` | Novo — converte PDFs/TXTs em chunks |
| `CLAUDE_LIVROS/sripts/gerar_embeddings.py` | Novo — gera embeddings_bge.json |
| `data/embeddings_bge.json` | Recriado com 2.698 chunks e metadados corretos |
| `core/engine.py` | Filtro por autor em `buscar_contexto` e `montar_prompt` |
| `core/ai_provider.py` | Exceção sagrada na `_BASE` + modelo Gemini 2.5-flash |
| `static/script.js` | Suporte ao comando `@` na interface |
