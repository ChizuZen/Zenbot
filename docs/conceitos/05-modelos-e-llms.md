# Modelos e LLMs

Este capítulo explica o que são modelos de linguagem, o que significa LLM e como esses sistemas funcionam por dentro — de forma simples e direta.

---

## O que é um modelo

Em inteligência artificial, um modelo é uma estrutura matemática treinada para reconhecer padrões.

Ele aprende observando milhões ou bilhões de exemplos e, a partir disso, passa a prever a próxima palavra, a próxima frase, relações de significado e estruturas da linguagem.

Em termos simples: um modelo é uma máquina que aprende a prever o que vem depois.

---

## O que é um modelo de linguagem

Um modelo de linguagem é treinado especificamente com textos. Ele aprende gramática, vocabulário, estilo, contexto e relações de significado entre palavras.

Isso permite que ele responda perguntas, explique conceitos, produza textos coerentes e dialogue de forma natural.

---

## O que significa LLM

LLM significa **Large Language Model** — Modelo de Linguagem de Grande Escala.

"Grande" se refere a bilhões de parâmetros, trilhões de exemplos de texto usados no treinamento e infraestrutura computacional massiva.

Exemplos conhecidos: GPT, LLaMA, Claude, Gemini, Mistral.

---

## O que são parâmetros

Parâmetros são os números internos que o modelo ajusta durante o aprendizado. Funcionam como conexões neurais artificiais — quanto mais parâmetros, maior a capacidade de aprender e compreender contexto.

Modelos modernos possuem entre 7 bilhões e 175 bilhões de parâmetros ou mais.

---

## Como um LLM gera texto

O modelo responde sempre a uma pergunta fundamental: qual é a palavra mais provável a vir agora?

Ele não escolhe apenas a mais provável — equilibra probabilidade, coerência, variedade e criatividade. Por isso os textos parecem humanos.

De forma simplificada, o processo é:

```
Recebe texto de entrada
      ↓
Converte palavras em números
      ↓
Processa em várias camadas matemáticas
      ↓
Calcula probabilidades para cada palavra
      ↓
Escolha a próxima palavra
      ↓
Repete o processo até completar a resposta
```

Tudo isso acontece em milissegundos.

---

## O papel do prompt

O prompt é a instrução que você dá ao modelo — o ponto de partida de toda resposta.

Pequenas mudanças no prompt geram grandes diferenças no comportamento. No Chizu, o prompt define a identidade do Mestre, o perfil do mestre sorteado, as regras zen e o contexto recuperado do acervo.

---

## Limitações importantes

Apesar de poderosos, os LLMs têm limitações sérias:

* Podem inventar respostas com aparência de verdade — fenômeno chamado de **alucinação**
* Não sabem quando estão errados
* Não possuem consciência nem compreensão real do mundo
* Seu conhecimento tem uma data de corte — não sabem o que aconteceu depois do treinamento

Por isso o Chizu não depende apenas do LLM. Ele usa textos reais do acervo como base — o modelo escreve, mas a sabedoria vem dos mestres.

---

## Os modelos usados no Chizu

O Chizu não usa um único modelo — usa quatro provedores em rodízio, sorteados a cada pergunta:

| Provedor | Modelo | Característica |
|---|---|---|
| Google | Gemini 2.5 Flash | Criativo, respostas mais longas |
| Groq | Llama 3.3 70B | Direto, muito rápido |
| Cerebras | Llama 3.1 8B | Baixíssima latência |
| SambaNova | Llama 3.1 8B | Consistente em diálogos |

Se um provedor falhar ou atingir o limite de requisições, o Chizu tenta automaticamente o próximo. Isso garante que o sistema continue funcionando mesmo quando uma IA está indisponível.

---

## Como o Chizu usa o LLM

O Chizu combina dois sistemas:

* **TF-IDF** — busca os trechos mais relevantes do acervo para a pergunta feita
* **LLM** — recebe esses trechos como contexto e gera a resposta em linguagem natural

```
Pergunta do usuário
      ↓
TF-IDF busca os 3 chunks mais relevantes no acervo
      ↓
Chunks são inseridos no prompt como contexto
      ↓
LLM gera a resposta na voz do mestre sorteado
      ↓
Resposta chega ao usuário com identificação do mestre e da IA
```

Assim o LLM não precisa inventar — ele tem textos reais dos mestres zen para se basear.

---

## Metáfora Zen

O LLM é como um calígrafo extremamente habilidoso — escreve com beleza e fluidez qualquer pensamento que você colocar em sua mente.

Mas a sabedoria ainda vem dos textos. O LLM não é o sábio — é o instrumento que expressa a sabedoria.

---

*Ver também: [Embeddings e Chunks](06-embeddings-e-chunks.md) · [Pipeline](08-pipeline.md) · [Ajustes do Sistema](11-ajustes.md)*
