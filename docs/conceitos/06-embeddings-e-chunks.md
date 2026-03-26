# Embeddings e Chunks

Este capítulo explica dois conceitos que formam a base da memória do Chizu:
**embeddings** e **chunks**.

Sem eles, o sistema não consegue encontrar nada — nem responder nada.

---

## O que são embeddings?

Embeddings são **representações matemáticas do significado dos textos**.

Eles transformam palavras, frases e parágrafos em **vetores numéricos**.

Esses vetores não capturam as palavras — capturam o **sentido**.

---

## O que é um vetor?

Um vetor é uma lista de números:

```text
[0.18, -0.33, 0.71, 0.04, -0.55, ...]
```

Cada número representa uma característica semântica aprendida pelo modelo.

Os modelos modernos usam vetores com centenas ou milhares de dimensões — 384, 768, 1536 ou mais.

---

## O que significa "representar o significado"?

Palavras com significados parecidos ficam **próximas no espaço vetorial**:

- carro
- automóvel
- veículo

Palavras com significados distantes ficam **muito afastadas**:

- carro
- meditação

Isso permite medir similaridade de forma matemática.

---

## Como se mede essa proximidade?

A métrica mais comum é a **similaridade do cosseno** — ela calcula o ângulo entre dois vetores.

- 1.0 → idênticos
- 0.8 → muito semelhantes
- 0.5 → relacionados
- 0.2 → pouco relacionados
- 0.0 → sem relação

---

## O que é um chunk?

Um **chunk** é um pequeno pedaço de texto retirado de um livro ou documento.

Em vez de consultar um livro inteiro, o sistema divide o conteúdo em partes menores.
Cada fragmento vira uma **unidade independente de conhecimento**.

Exemplos de chunks:

> A mente do principiante tem muitas possibilidades.

> O silêncio não é ausência de som, mas presença de atenção.

No Chizu, os chunks têm tipicamente entre 300 e 800 caracteres.

---

## Por que dividir em chunks?

- Modelos de linguagem têm limites de contexto
- Pedaços menores permitem busca mais precisa
- Cada fragmento pode ser indexado e recuperado separadamente

---

## Como o Chizu usa chunks e embeddings juntos

O processo funciona em duas fases.

**Fase de ingestão** — acontece uma vez, ao preparar os textos:

- O texto é dividido em chunks
- Cada chunk recebe um embedding
- Os dados são armazenados em `data/embeddings_bge.json`

Cada registro no arquivo tem esta estrutura:

```json
{
  "texto": "Respire e volte ao momento presente.",
  "embedding": [0.18, -0.33, 0.71, 0.04, -0.55],
  "autor": "Thich Nhat Hanh",
  "fonte": "Silêncio"
}
```

**Fase de consulta** — acontece a cada pergunta:

- A pergunta do usuário é convertida em embedding
- Esse vetor é comparado com todos os vetores armazenados
- Os chunks com maior proximidade semântica são recuperados
- Esses trechos alimentam o modelo de linguagem

---

## Por que isso é poderoso?

Porque o sistema não depende de palavras exatas.

Pergunta:

> Como acalmar a mente?

Mesmo sem essa frase nos textos, o sistema encontra:

- meditação
- silêncio
- atenção plena
- respiração consciente

Ele busca pelo **sentido**, não pelas letras.

---

## Embeddings não pensam

Eles não entendem de verdade.

Representam matematicamente padrões estatísticos da linguagem.
Mas isso já é suficiente para criar sistemas de busca incrivelmente precisos.

---

## Analogia

Chunks são pequenos trechos de livros espalhados pelas estantes de uma biblioteca.
Embeddings são as coordenadas num mapa que indicam o significado de cada trecho.

Quando surge uma pergunta, o sistema procura no mapa os trechos mais próximos daquele significado.

---

## Conceito-chave

> Embeddings são a ponte entre linguagem humana e matemática.  
> Chunks são as unidades que essa ponte conecta.
