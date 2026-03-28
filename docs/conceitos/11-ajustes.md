# Ajustes do Sistema

Esta página documenta os parâmetros que controlam o comportamento das IAs no Chizu — o que cada um significa, qual o valor atual e o efeito prático nas respostas.

Todos os valores ficam em `core/ai_provider.py` no dicionário `CONFIGS`.

---

## O que são parâmetros de geração

Quando o Chizu envia uma pergunta para uma IA, junto com o prompt vai um conjunto de instruções numéricas que controlam como a resposta será gerada. São esses parâmetros que determinam se a resposta será mais criativa ou mais conservadora, mais longa ou mais curta, mais variada ou mais repetitiva.

Cada provedor tem sua própria calibração — porque cada modelo responde de forma diferente aos mesmos valores.

---

## Parâmetros e seus significados

### temperature — criatividade

Controla o grau de aleatoriedade na escolha das palavras.

* Valores baixos (0.2 – 0.4) — respostas mais previsíveis, precisas, conservadoras
* Valores altos (0.7 – 1.0) — respostas mais criativas, variadas, às vezes surpreendentes

Para o Chizu, um valor médio equilibra a poesia zen com a coerência do conteúdo.

---

### max_tokens — tamanho da resposta

Define o limite máximo de tokens que a IA pode gerar.
Um token equivale aproximadamente a 3/4 de uma palavra em português.

* Valores baixos (200 – 300) — respostas curtas, dentro das 3 frases exigidas pelo prompt
* Valores altos (1000+) — respostas longas, risco de ultrapassar o limite e ser cortada no meio

Se uma resposta aparecer cortada no meio de uma frase, aumentar `max_tokens` é a primeira correção.

---

### top_p — diversidade do vocabulário

Trabalha junto com a temperature. Define a fatia de palavras mais prováveis que o modelo considera a cada escolha.

* `top_p = 1.0` — considera todas as palavras possíveis
* `top_p = 0.85` — considera apenas as palavras mais prováveis, excluindo as muito improváveis

Valores entre 0.85 e 0.95 são os mais equilibrados para texto poético.

---

### frequency_penalty — penalidade de repetição de palavras

Penaliza palavras que já foram usadas na resposta, reduzindo a chance de repetirem.

* `0.0` — sem penalidade, o modelo pode repetir palavras livremente
* `0.5` — penalidade moderada, reduz repetições visíveis
* `1.0` — penalidade forte, força variedade de vocabulário

Útil para evitar respostas que repetem "caminhante", "silêncio" ou "zen" em excesso.

---

### presence_penalty — penalidade de repetição de temas

Penaliza tópicos que já foram abordados, incentivando o modelo a explorar novos ângulos.

* `0.0` — sem penalidade, o modelo pode ficar no mesmo tema
* `0.3` — penalidade leve, suave incentivo à variedade temática

Valores altos podem fazer o modelo mudar de assunto de forma abrupta — usar com moderação.

---

## Configuração atual por provedor

Os valores foram calibrados individualmente para cada IA, respeitando as características de cada modelo.

```python
CONFIGS = {
    "Gemini":    {
        "temperature": 0.75,
        "max_tokens": 2048,
        "top_p": 0.95,
        "frequency_penalty": 0.20,
        "presence_penalty": 0.10
    },
    "Groq":      {
        "temperature": 0.30,
        "max_tokens": 600,
        "top_p": 0.85,
        "frequency_penalty": 0.50,
        "presence_penalty": 0.30
    },
    "Cerebras":  {
        "temperature": 0.50,
        "max_tokens": 512,
        "top_p": 0.90,
        "frequency_penalty": 0.35,
        "presence_penalty": 0.20
    },
    "SambaNova": {
        "temperature": 0.60,
        "max_tokens": 600,
        "top_p": 0.92,
        "frequency_penalty": 0.30,
        "presence_penalty": 0.15
    },
}
```

---

## Tabela comparativa

| Provedor | temperature | max_tokens | top_p | freq_penalty | pres_penalty |
|---|---|---|---|---|---|
| Gemini | 0.75 | 2048 | 0.95 | 0.20 | 0.10 |
| Groq | 0.30 | 600 | 0.85 | 0.50 | 0.30 |
| Cerebras | 0.50 | 512 | 0.90 | 0.35 | 0.20 |
| SambaNova | 0.60 | 600 | 0.92 | 0.30 | 0.15 |

---

## Leitura da tabela

**Gemini** — temperature mais alta e max_tokens generoso. Respostas mais criativas e longas. Pode ocasionalmente ultrapassar as 3 frases — o prompt precisa ser rigoroso.

**Groq** — temperature mais baixa e frequency_penalty alto. Respostas mais diretas e menos repetitivas. Ideal para respostas concisas e precisas.

**Cerebras** — valores intermediários. Equilibrado entre criatividade e coerência.

**SambaNova** — temperature moderada com presence_penalty baixo. Tende a aprofundar o tema escolhido com mais consistência.

---

## Erro 429 — Too Many Requests

Ocorre quando o limite de requisições de um provedor é atingido. O Chizu trata esse erro automaticamente:

* Pausa de 2 segundos (`time.sleep(2)`)
* Tenta o próximo provedor na fila

Se todos os provedores falharem, retorna uma frase do `koans.txt` + "Vá praticar Zazen."

Para reduzir a frequência de erros 429, diminuir `max_tokens` é a medida mais eficaz — respostas menores consomem menos cota.

---

## Parâmetros do RAG

Além dos parâmetros das IAs, há dois parâmetros em `core/engine.py` que controlam a busca no acervo:

| Parâmetro | Valor atual | Significado |
|---|---|---|
| `top_k` | 3 | Número de chunks recuperados por pergunta |
| `threshold` | 0.05 | Score mínimo de similaridade para incluir um chunk |

Se as respostas estiverem retornando `VAZIO` com frequência, reduzir o `threshold` para `0.03` pode ajudar. Se estiverem trazendo trechos pouco relevantes, aumentar para `0.1`.

---

*Ver também: [Engenharia de Prompts](17-engenharia-de-prompts.md) · [Protocolo de Testes](18-documentacao_testes.md) · [Glossário](30-glossario.md)*
