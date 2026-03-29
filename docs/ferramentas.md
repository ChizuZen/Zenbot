# Ferramentas

Esta página apresenta as principais ferramentas usadas no desenvolvimento e na operação do Chizu — o que cada uma faz e por que foi escolhida.

---

## Linguagem e servidor

**Python**
Linguagem principal do projeto. Simples, legível e com um ecossistema rico para IA e processamento de texto.

**FastAPI**
Framework web que transforma o código Python em uma API acessível pela internet. Rápido, assíncrono e com documentação automática das rotas.

**Uvicorn**
Servidor ASGI que executa o FastAPI. É quem coloca o sistema no ar localmente e no Render.

---

## Inteligência Artificial

**Gemini (Google)**
Modelo principal. Temperature mais alta, respostas mais criativas.

**Groq (Llama 3.3 70B)**
Modelo direto e muito rápido. Ideal para respostas concisas.

**Cerebras (Llama 3.1 8B)**
Latência baixíssima. Boa para respostas rápidas.

**SambaNova (Llama 3.1 8B)**
Consistente em diálogos. Bom para aprofundar temas.

Os quatro operam em rodízio automático com fallback — se um falhar, o próximo assume.

---

## Processamento de texto

**PyMuPDF (fitz)**
Extrai texto de arquivos PDF com alta fidelidade. Usado nos scripts de preparação do acervo.

**scikit-learn (TF-IDF)**
Indexa os chunks do acervo e calcula a similaridade entre a pergunta e os textos. É o motor da busca semântica do Chizu.

**NumPy**
Operações matemáticas sobre os vetores TF-IDF.

---

## Infraestrutura

**Render**
Hospedagem do servidor Python na nuvem. Plano gratuito com hibernação — o UptimeRobot mantém o servidor acordado.

**Cloudflare**
Gerencia DNS, proxy reverso, firewall WAF e roteamento de e-mail. Todo o tráfego passa pelo Cloudflare antes de chegar ao Render.

**GitHub**
Controle de versão do código. Cada `git push` dispara o deploy automático no Render.

**UptimeRobot**
Monitora o servidor a cada 13 minutos e envia alerta por e-mail se cair.

---

## Documentação

**MkDocs**
Gera o site de documentação a partir de arquivos Markdown. Simples, rápido e integrado ao GitHub Pages.

**GitHub Pages**
Hospeda a documentação estática em `docs.chizu.ia.br`.

---

## Desenvolvimento local

**VS Code**
Editor de código principal.

**Git**
Controle de versão — commits, branches e push para o GitHub.

**venv**
Ambiente virtual Python — isola as dependências do projeto do sistema operacional.

---

*Ver também: [Comandos Úteis](comandos-uteis.md) · [Arquitetura](arquitetura.md)*
