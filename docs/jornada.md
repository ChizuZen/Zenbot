# Jornada do Projeto

Este documento registra o caminho percorrido na construção do Chizu — as decisões técnicas, os erros, as descobertas e as mudanças de direção ao longo do tempo.

Não é um diário de conquistas. É um registro de prática — da mesma forma que um monge zen anota os ensinamentos recebidos, não para guardar troféus, mas para lembrar o caminho.

---

## O começo — mente de principiante

O Chizu começou sem saber exatamente o que seria. A única certeza era aprender construindo.

As primeiras perguntas que guiaram o projeto:

* Como funciona, de fato, a inteligência artificial moderna?
* Como transformar textos em conhecimento acessível?
* Como um sistema encontra a informação certa para responder uma pergunta?
* Como tudo isso pode ser feito por alguém sem formação técnica formal?

A partir dessas perguntas, o projeto tomou forma — aos poucos, com erros frequentes e aprendizado constante.

---

## As fases do caminho

### Fase 1 — Primeiros experimentos

* Exploração de APIs de IA
* Primeiros protótipos de chatbot
* Testes com diferentes arquiteturas
* Muito código experimental, muitas mudanças

### Fase 2 — O acervo zen

* Decisão de usar textos reais dos mestres zen como base
* Extração de PDFs com PyMuPDF
* Criação do pipeline de chunking e indexação
* Primeiro sistema RAG funcionando com embeddings vetoriais

### Fase 3 — Simplificação

* Substituição de embeddings vetoriais por TF-IDF em memória
* Código mais simples, mais rápido, sem dependências pesadas
* Arquivo `acervo_zen.json` como memória permanente do sistema

### Fase 4 — Personalidade e voz

* Criação dos perfis de personalidade dos seis mestres
* Sorteio por afinidade — o mestre é escolhido conforme o conteúdo encontrado
* Conselho de IAs — Gemini, Groq, Cerebras, SambaNova em rodízio
* Adição de voz no navegador — microfone e síntese

### Fase 5 — Infraestrutura própria

* Domínio `chizu.ia.br` com identidade completa
* Migração para o Cloudflare — DNS, firewall e e-mail centralizados
* Documentação publicada em `docs.chizu.ia.br`
* Skill publicada na Alexa Skill Store

---

## O que o caminho ensinou

Cada fase trouxe um aprendizado que vai além do técnico:

* Simplicidade é mais poderosa que sofisticação
* Um sistema que funciona hoje vale mais que um sistema perfeito amanhã
* Documentar é parte da prática — não um extra
* Errar rápido e ajustar é o ritmo certo
* O projeto que serve a outros tem mais vida do que o projeto que impressiona

---

## O estado atual

O Chizu hoje tem:

* 2.698 ensinamentos zen no acervo
* 6 perfis de mestres com sorteio por afinidade
* 4 provedores de IA em rodízio com fallback automático
* Voz no navegador, WhatsApp e Alexa
* Infraestrutura completa no Cloudflare e Render
* Documentação viva em `docs.chizu.ia.br`

---

*O caminho continua. Gassho 🙏*

---

*Ver também: [Por que Chizu?](por-que-chizu.md) · [Arquitetura](arquitetura.md)*
