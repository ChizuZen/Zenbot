# Organização dos Textos

Este documento descreve como os livros zen foram transformados em base de conhecimento do Chizu —
desde os PDFs e TXTs originais até o arquivo `acervo_zen.json` que alimenta o sistema em produção.

---

## Visão geral do processo

O fluxo completo acontece em duas etapas, executadas localmente antes do deploy:

```
PDFs e TXTs → preparar_textos.py → chunks_preparados.txt
chunks_preparados.txt → gerar_embeddings.py → acervo_zen.json
```

O arquivo `acervo_zen.json` é o único que vai para o servidor. Os textos originais e os scripts ficam na máquina local.

---

## Estrutura de pastas local

Os scripts e textos ficam organizados numa pasta separada do projeto principal:

```
CLAUDE_LIVROS/
├── data/
│   ├── chunks_preparados.txt
│   └── acervo_zen.json
├── sripts/
│   ├── preparar_textos.py
│   └── gerar_embeddings.py
└── textos/
    ├── Eihei_Dogen/
    ├── Haemin_Sunim/
    ├── Osho/
    ├── Shunmyo_Masuno/
    ├── Shunryu Suzuki/
    └── Thich_Nhat_Hanh/
```

Cada pasta de autor contém os PDFs e TXTs originais das obras.

---

## Acervo atual

| Autor | Obras |
|---|---|
| Eihei Dogen | Cem e Oito Portais da Lei Maravilhosa, Instruções para o Cozinheiro-Chefe, Shobogenzo Zuimonki (introdução + 5 livros), Textos de Mestre Dogen |
| Haemin Sunim | As Coisas que Você Só Vê Quando Desacelera, Amor pelas Coisas Imperfeitas, Quando as Coisas Não Saem Como Você Espera |
| Osho | Zen: Sua História e Seus Ensinamentos |
| Shunmyo Masuno | A Arte de Viver Simples, Não se Preocupe |
| Shunryu Suzuki | Mente Zen, Mente de Principiante |
| Thich Nhat Hanh | Silêncio |

---

## Etapa 1 — preparar_textos.py

O script `preparar_textos.py` percorre todas as obras do acervo e gera o arquivo intermediário `chunks_preparados.txt`.

### Extração do texto

Para PDFs, o script usa a biblioteca **PyMuPDF** (`fitz`):

```python
import fitz

with fitz.open(str(caminho)) as doc:
    for pagina in doc:
        texto.append(pagina.get_text())
```

Para arquivos TXT, lê diretamente com encoding UTF-8.

### Limpeza

Após a extração, o texto passa por limpeza para remover ruídos comuns de PDFs:

```python
texto = re.sub(r'\n{3,}', '\n\n', texto)   # múltiplas linhas em branco
texto = re.sub(r'-\n', '', texto)           # hífens de quebra de linha
texto = re.sub(r' {2,}', ' ', texto)        # espaços duplos
texto = re.sub(r'^\s*\d+\s*$', '', texto,   # números de página isolados
               flags=re.MULTILINE)
```

### Fragmentação — chunks

O texto limpo é dividido em blocos de **1000 caracteres** com **200 caracteres de sobreposição** (overlap).

O overlap garante que ideias que atravessam a fronteira entre dois chunks não se percam — o final de um chunk aparece também no início do próximo.

Chunks com menos de 100 caracteres são descartados como ruído.

### Formato de saída

O arquivo `chunks_preparados.txt` usa um formato legível, pensado para inspeção antes de gerar o JSON final:

```
==== NOVO CHUNK ====
AUTOR: Thich Nhat Hanh
FONTE: Silêncio
TEXTO:
Quando nos libertamos de nossas ideias e pensamentos...
---
```

Esse formato intermediário permite revisar os chunks e corrigir problemas antes de gerar o banco definitivo.

---

## Etapa 2 — gerar_embeddings.py

O script `gerar_embeddings.py` lê o `chunks_preparados.txt` e gera o `acervo_zen.json`.

### O que o script faz

Lê cada bloco do arquivo intermediário, extrai autor, fonte e texto, adiciona um ID sequencial e salva em JSON:

```json
{
  "id": 1,
  "autor": "Thich Nhat Hanh",
  "fonte": "Silêncio",
  "texto": "Quando nos libertamos de nossas ideias e pensamentos..."
}
```

### O que o arquivo armazena

O `acervo_zen.json` não contém vetores ou embeddings — armazena apenas os chunks de texto com metadados de autor e fonte. Os vetores TF-IDF são calculados em memória quando o servidor sobe, a partir dos textos deste arquivo.

### Relatório gerado

Ao final da execução o script exibe a distribuição por autor:

```
✅ 847 chunks salvos em data/acervo_zen.json

📊 Distribuição por autor:
   Eihei Dogen              312 chunks
   Haemin Sunim             198 chunks
   Osho                      87 chunks
   Shunmyo Masuno           124 chunks
   Shunryu Suzuki            63 chunks
   Thich Nhat Hanh           63 chunks
```

---

## Como executar

Instale a dependência necessária:

```bash
pip install pymupdf
```

Execute na ordem:

```bash
python sripts/preparar_textos.py
python sripts/gerar_embeddings.py
```

Após a execução, copie o `acervo_zen.json` para a pasta `data/` do projeto principal e faça o deploy.

---

## Como adicionar um novo livro

Para incluir uma nova obra no acervo:

Adicione o arquivo PDF ou TXT na pasta do autor correspondente dentro de `textos/`.

Registre o livro no mapeamento dentro de `preparar_textos.py`:

```python
("Autor/nome-do-arquivo.pdf", "Nome do Autor", "Título da Obra"),
```

Execute os dois scripts novamente e substitua o `acervo_zen.json` em produção.

---

*Ver também: [Pipeline](pipeline.md) — como o `acervo_zen.json` é usado em runtime para responder perguntas.*
