# Busca Semântica

Este capítulo explica o que é **busca semântica**, como ela funciona e como o Chizu a implementa para encontrar ensinamentos relevantes antes de gerar uma resposta.

---

## O que é busca semântica?

Busca semântica é uma técnica que encontra informações **pelo significado**, não pelas palavras.

Ela responde à pergunta:

> O que a pessoa quer dizer — e não exatamente o que ela escreveu?

---

## Diferença entre busca tradicional e semântica

A **busca tradicional** procura termos exatos.

Exemplo — usuário pergunta:

> Como ter paz interior?

Se essa frase não existir literalmente nos textos, o sistema não encontra nada.

A **busca semântica** procura ideias e intenções relacionadas.

O sistema pode encontrar trechos sobre:

- meditação
- silêncio
- atenção plena
- desapego
- respiração consciente

Mesmo sem nenhuma coincidência literal.

---

## Como funciona

A busca semântica se baseia em **embeddings** — representações numéricas do significado dos textos.

O fluxo é:

- Todo texto é convertido em vetor numérico
- A pergunta do usuário também vira um vetor
- O sistema mede a distância entre os vetores
- Os textos mais próximos são selecionados

---

## Medindo similaridade

A métrica usada é a **similaridade de cosseno** — ela mede o ângulo entre dois vetores.

- Vetores próximos → significados semelhantes
- Vetores distantes → significados diferentes

Exemplo do fluxo:

```text
Pergunta: "Como acalmar a mente?"
        ↓
Embedding da pergunta
        ↓
Comparação com embeddings dos textos
        ↓
Seleção dos chunks mais próximos
```

---

## Exemplo prático

Suponha que exista este chunk no sistema:

> Observe sua respiração e permita que os pensamentos passem.

O usuário pergunta:

> Como posso acalmar minha mente?

As palavras são diferentes, mas o significado é próximo.
A busca semântica identifica essa proximidade e recupera o trecho como contexto para a resposta.

---

## Como o Chizu implementa

No Chizu, a busca semântica é feita pela função `buscar_contexto` em `core/engine.py`.

O sistema usa **TF-IDF** com `cosine_similarity` para comparar a pergunta com os ensinamentos armazenados em `data/embeddings_bge.json`.

Parâmetros atuais:

- `top_k = 3` — retorna os 3 trechos mais relevantes
- `threshold = 0.05` — descarta resultados abaixo desse score de similaridade

Se nenhum trecho superar o threshold, o sistema retorna `VAZIO` — e o Chizu responde com um koan em vez de inventar.

---

## Filtro por autor

O usuário pode direcionar a busca para um mestre específico usando `@autor` na interface.

Nesse caso, `buscar_contexto` restringe a comparação apenas aos chunks daquele autor.
Se não houver ensinamentos suficientes, retorna `VAZIO`.

---

## Por que isso melhora as respostas?

Porque o modelo não precisa inventar.

Ele responde com base nos textos reais — o que garante:

- Fidelidade ao conteúdo do acervo
- Coerência filosófica com os mestres
- Redução de alucinações

---

## Limitações

A qualidade da busca depende de:

- A qualidade dos textos no acervo
- A granularidade dos chunks
- O threshold configurado

Se os textos forem pobres ou os chunks muito grandes, a busca perde precisão.

---

## Metáfora Zen

Busca semântica é como um monge que escuta a pergunta além das palavras.

Ele percebe a intenção silenciosa por trás da frase.

---

## Conceito-chave

> Busca semântica é o elo entre o significado humano e a recuperação inteligente do conhecimento.
