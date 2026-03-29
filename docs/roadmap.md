# Roadmap — Escolha seu Caminho

Esta página ajuda você a navegar pela documentação de acordo com o que busca — e mostra os próximos passos do projeto.

> O campo de busca no topo do site funciona em todas as páginas. Se quiser encontrar um termo específico — RAG, temperatura, zazen, curl — basta digitar lá.

---

## Caminho 1 — Quero usar o Chizu

Para quem quer conversar com o Mestre Chizu, entender como fazer perguntas e aproveitar ao máximo a experiência.

* [O que é o Chizu](visao-geral.md) — como funciona e o que esperar
* [Consultar um Mestre](consultar-mestre.md) — como usar o comando `@nome` para falar com um mestre específico
* [Voz](voz.md) — como falar e ouvir respostas no navegador
* [Alexa](alexa.md) — como usar a skill de voz
* [WhatsApp](whatsapp.md) — como conversar pelo WhatsApp

Acesse agora: [chizu.ia.br](http://chizu.ia.br)

---

## Caminho 2 — Quero entender os conceitos de IA

Para quem quer aprender o que está por baixo do Chizu — inteligência artificial, busca semântica, RAG — sem precisar entrar no código.

* [Glossário](glossario.md) — os principais termos explicados de forma simples
* [Inteligência Artificial](inteligencia-artificial.md) — o que é IA e como ela aprende
* [Modelos e LLMs](modelos-e-llms.md) — o que são modelos de linguagem e como geram texto
* [Embeddings e Chunks](embeddings-e-chunks.md) — como os textos são fragmentados e indexados
* [Busca Semântica](busca-semantica.md) — como o sistema encontra textos pelo significado
* [RAG — A Mágica por Trás das Respostas](rag.md) — onde acontece a transformação de dados em sabedoria
* [Metáfora Zen](metafora-zen.md) — a visão poética de tudo isso

---

## Caminho 3 — Quero entender o projeto tecnicamente

Para quem quer entender a arquitetura, rodar localmente, contribuir ou construir algo parecido.

* [Arquitetura](arquitetura.md) — estrutura de pastas e camadas do sistema
* [Ferramentas](ferramentas.md) — o que foi usado para construir o Chizu
* [Organização dos Textos](organizacao-dos-textos.md) — como os PDFs e TXTs viraram o acervo
* [Pipeline](pipeline.md) — o fluxo completo de ingestão e consulta
* [Engenharia de Prompts](engenharia-de-prompts.md) — como o system prompt é construído
* [Ajustes do Sistema](ajustes.md) — parâmetros das IAs e do RAG com seus significados
* [Validação de Perguntas](validacao-perguntas.md) — como testar a qualidade das respostas
* [Protocolo de Testes](protocolo-de-testes.md) — como validar o sistema antes do deploy
* [Bibliotecas Usadas](dependencias-importacoes.md) — as dependências Python e para que servem

---

## Caminho 4 — Sou o mantenedor do site

Para quem cuida do projeto no dia a dia — deploy, infraestrutura, atualizações e documentação.

* [Fluxo de Trabalho](fluxo-de-trabalho.md) — o ciclo diário de desenvolvimento e deploy
* [Comandos Úteis](comandos-uteis.md) — referência rápida de terminal, git, curl e MkDocs
* [Cloudflare — DNS, Proxy e Firewall](cloudflare.md) — gestão do domínio e proteção
* [Verificação de DNS](verificacao-dns.md) — como checar e diagnosticar DNS
* [Caixa Postal](caixa-postal.md) — como funciona o e-mail sem servidor próprio
* [Monitoramento](monitoramento.md) — UptimeRobot e disponibilidade do Render
* [Firewall e Resiliência](firewall.md) — proteção contra bots e scanners

---

## Próximos passos do projeto

**Em andamento**
* Calibração contínua dos perfis de mestres
* Expansão do acervo com novos autores

**Concluído recentemente**
* Migração completa para o Cloudflare ✅
* Arquivo renomeado para `acervo_zen.json` ✅
* Voz no navegador — microfone e síntese ✅
* Domínio `docs.chizu.ia.br` para a documentação ✅

**Próxima fase**
* Suporte a voz em Firefox e Safari via Whisper
* Histórico de conversa persistente por sessão

**Futuro**
* Múltiplos bots temáticos com acervos diferentes
* Ambiente colaborativo aberto para novos acervos

---

*Ver também: [Por que Chizu?](por-que-chizu.md) · [Jornada do Projeto](jornada.md)*
