# Arquitetura do Projeto Chizu

Este documento descreve como o Chizu está organizado internamente e como seus componentes se conectam.

---

## Visão Geral da Arquitetura

O Chizu segue uma arquitetura modular, organizada em camadas, com o objetivo de:

* Facilitar o entendimento do sistema.
* Tornar o código mais limpo.
* Permitir evolução e manutenção contínua.

De forma resumida, o fluxo principal é:

```
Usuário → API Web → Busca Semântica → IA → Resposta → Usuário
```

---

## Estrutura Geral de Pastas

```
chizu/
├── core/
│   ├── __init__.py
│   ├── ai_provider.py
│   └── engine.py
├── data/
│   ├── acervo_zen.json
│   └── koans.txt
├── docs/
├── legal/
├── static/
│   ├── img/
│   ├── script.js
│   └── style.css
├── web.py
├── mkdocs.yml
├── Makefile
└── requirements.txt
```

---

## Camada de Interface (API Web)

A interface com o usuário é construída com **FastAPI**.

Arquivo principal: `web.py`

Funções principais:

* Receber perguntas via HTTP nos endpoints `/ask` e `/whatsapp`
* Gerenciar o histórico de conversa por sessão
* Acionar o motor interno e retornar a resposta ao usuário

---

## Camada de Processamento Central (core)

A pasta `core/` contém o núcleo lógico do Chizu.

```
core/
├── __init__.py
├── engine.py
└── ai_provider.py
```

### engine.py

É o cérebro do sistema. Concentra toda a lógica de conhecimento e prompt:

* Define os perfis de personalidade dos seis mestres zen
* Define as regras zen e os estilos por IA
* Carrega a biblioteca de ensinamentos (`acervo_zen.json`) em memória
* Executa a busca TF-IDF para encontrar os trechos mais relevantes
* Sorteia o perfil do mestre por afinidade com o contexto
* Monta o prompt completo para envio à IA

### ai_provider.py

Gerencia o Conselho de IAs:

* Mantém as configurações de temperatura e tokens por provedor
* Sorteia a ordem de tentativa entre Gemini, Groq, Cerebras e SambaNova
* Injeta o estilo de cada IA no system prompt
* Implementa fallback automático em caso de falha ou limite de requisições

---

## Camada de Dados

### data/acervo_zen.json

A memória permanente do Chizu. Contém todos os chunks de texto extraídos das obras dos mestres, com metadados de autor e fonte:

```json
{
  "id": 1,
  "autor": "Thich Nhat Hanh",
  "fonte": "Silêncio",
  "texto": "Quando nos libertamos de nossas ideias e pensamentos..."
}
```

Este arquivo é carregado em memória quando o servidor sobe e indexado via TF-IDF para busca em tempo real.

### data/koans.txt

Lista de frases zen usadas nas respostas de bloqueio e fallback. Uma frase é sorteada aleatoriamente cada vez que o sistema precisa recusar uma pergunta.

---

## Camada de Interface Web

### static/

Contém os arquivos servidos diretamente ao navegador:

* `script.js` — lógica do frontend, incluindo o parser do comando `@nome`
* `style.css` — estilos da interface
* `img/` — avatar, favicon e ícones da skill Alexa

### legal/

Página de termos legais servida em `/legal`.

---

## Fluxo Simplificado de Funcionamento

```
Pergunta do usuário
      ↓
web.py recebe via /ask ou /whatsapp
      ↓
engine.py busca contexto (TF-IDF sobre acervo_zen.json)
      ↓
engine.py sorteia perfil do mestre por afinidade
      ↓
engine.py monta o prompt (identidade + perfil + regras + contexto)
      ↓
ai_provider.py sorteia e aciona uma das IAs disponíveis
      ↓
Resposta retorna ao usuário com identificação do mestre e da IA
```

---

## Princípios de Arquitetura

* Simplicidade
* Modularidade
* Clareza
* Facilidade de evolução
* Foco educacional

---

*Ver também: [Pipeline](pipeline.md) — descrição detalhada de cada etapa do fluxo.*
