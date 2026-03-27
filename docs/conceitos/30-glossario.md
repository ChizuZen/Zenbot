# Glossário de Termos

Este glossário reúne os principais termos técnicos usados no projeto Chizu,
organizados por área para facilitar a consulta.

---

## Inteligência Artificial e LLMs

**IA — Inteligência Artificial**
Campo da computação dedicado a criar sistemas capazes de realizar tarefas que normalmente exigiriam inteligência humana, como compreender linguagem, reconhecer padrões e gerar texto.

**LLM — Large Language Model (Modelo de Linguagem de Grande Escala)**
Tipo de IA treinada em enormes volumes de texto para compreender e gerar linguagem natural. É o motor por trás das respostas do Chizu. Exemplos usados no projeto: Gemini, Llama, Claude.

**Model — Modelo**
A versão específica de uma LLM. Exemplos: `gemini-2.5-flash`, `llama-3.3-70b-versatile`. Cada modelo tem características próprias de velocidade, custo e qualidade de resposta.

**Token**
Unidade básica de processamento dos modelos de linguagem. Pode ser uma palavra, parte de uma palavra ou um caractere. Os modelos têm limites de tokens por requisição — tanto na entrada quanto na saída.

**Temperature (Temperatura)**
Parâmetro que controla o grau de criatividade das respostas. Valores baixos (ex: 0.3) geram respostas mais precisas e previsíveis. Valores altos (ex: 0.9) geram respostas mais variadas e criativas.

**Top-p**
Parâmetro que controla a diversidade do vocabulário usado nas respostas. Complementa a temperatura na calibração do estilo de cada IA.

**Max Tokens**
Limite máximo de tokens que a IA pode gerar numa resposta. No Chizu, cada provedor tem seu próprio limite configurado.

**System Prompt**
Instrução inicial enviada à IA antes da conversa, definindo seu comportamento, personalidade e regras. No Chizu, o system prompt inclui a identidade do Mestre Chizu, o perfil do mestre sorteado, as regras zen e o contexto recuperado pelo RAG.

**Prompt Engineering — Engenharia de Prompts**
Arte e técnica de construir instruções eficazes para guiar o comportamento de uma IA. No Chizu, envolve o equilíbrio entre identidade, regras de bloqueio, estilo poético e citação obrigatória de fontes.

**Fallback**
Mecanismo de segurança que aciona um provedor alternativo quando o principal falha ou atinge seu limite de requisições. O Chizu usa fallback automático entre Gemini, Groq, Cerebras e SambaNova.

**Alucinação**
Fenômeno em que a IA gera informações falsas com aparência de verdade — inventando citações, personagens ou fatos que não existem. No Chizu, o RAG e as regras do prompt buscam minimizar esse comportamento.

---

## RAG e Busca Semântica

**RAG — Retrieval-Augmented Generation (Geração Aumentada por Recuperação)**
Técnica que combina busca em uma base de conhecimento com geração de texto por IA. Em vez de depender apenas do que a IA aprendeu no treinamento, o RAG recupera trechos relevantes de um acervo real e os usa como contexto para a resposta. É o coração do Chizu.

**Chunk**
Fragmento de texto extraído de uma obra do acervo. Cada chunk tem entre 300 e 1000 caracteres e representa uma ideia ou trecho coerente. O Chizu usa chunks para indexar e recuperar ensinamentos.

**Chunking**
Processo de dividir textos longos em chunks menores para facilitar a indexação e a busca. No Chizu, é feito pelo script `preparar_textos.py`.

**Overlap**
Sobreposição entre chunks consecutivos. No Chizu, os chunks têm 200 caracteres de overlap, garantindo que ideias que cruzam a fronteira entre dois blocos não se percam.

**Embedding**
Representação matemática do significado de um texto, expressa como um vetor numérico. Permite comparar textos por significado e não apenas por palavras. O arquivo `embeddings_bge.json` do Chizu usa esse nome historicamente, embora atualmente armazene apenas os chunks de texto.

**TF-IDF — Term Frequency–Inverse Document Frequency**
Técnica de busca que pondera a importância de cada palavra num texto. Palavras comuns como "o" e "de" recebem peso baixo; palavras raras como "zazen" recebem peso alto. O Chizu usa TF-IDF em tempo real para encontrar os chunks mais relevantes para cada pergunta.

**Similaridade de Cosseno**
Medida matemática que calcula o ângulo entre dois vetores para determinar o quanto dois textos são semanticamente próximos. Valor próximo de 1 indica alta similaridade; próximo de 0 indica pouca relação.

**Threshold**
Valor mínimo de similaridade para que um chunk seja considerado relevante. No Chizu, o threshold é 0.05 — chunks abaixo desse score são descartados e o contexto retorna `VAZIO`.

**Top-k**
Número máximo de chunks recuperados pelo RAG para montar o contexto. No Chizu, `top_k = 3` — os três trechos mais relevantes são enviados para a IA.

**Contexto**
Conjunto de chunks recuperados pelo RAG e inseridos no system prompt para fundamentar a resposta da IA. No Chizu, cada chunk é identificado com autor e fonte antes de ser enviado.

**Vectorizer**
Componente que transforma textos em vetores numéricos para indexação. No Chizu, o `TfidfVectorizer` do scikit-learn é carregado na inicialização do servidor e mantido em memória.

---

## Web e API

**API — Application Programming Interface**
Interface que permite que sistemas diferentes se comuniquem. No Chizu, a API recebe perguntas via HTTP e devolve respostas em JSON ou XML.

**HTTP — HyperText Transfer Protocol**
Protocolo de comunicação usado na web. As perguntas ao Chizu chegam como requisições HTTP `POST` nos endpoints `/ask` e `/whatsapp`.

**Endpoint**
Endereço específico de uma API que recebe requisições. O Chizu tem dois endpoints principais: `/ask` para a interface web e `/whatsapp` para o Twilio.

**FastAPI**
Framework Python usado para construir a API do Chizu. É assíncrono, rápido e gera documentação automática das rotas.

**JSON — JavaScript Object Notation**
Formato leve de troca de dados, legível por humanos e máquinas. O Chizu usa JSON para receber perguntas, devolver respostas e armazenar o acervo de ensinamentos.

**Payload**
Dados enviados numa requisição HTTP. No Chizu, o payload de uma pergunta tem a forma `{"pergunta": "O que é zazen?"}`.

**Session — Sessão**
Mecanismo que identifica um usuário entre requisições diferentes. O Chizu usa cookies com UUID para manter o histórico de conversa de cada usuário separado em memória.

**Cookie**
Pequeno dado armazenado no navegador do usuário. O Chizu usa um cookie chamado `chizu_session` para identificar sessões.

**Static Files — Arquivos Estáticos**
Arquivos servidos diretamente ao navegador sem processamento — CSS, JavaScript, imagens. No Chizu, ficam na pasta `static/`.

**Deploy**
Processo de publicar o código num servidor para que fique acessível na internet. O Chizu é hospedado no Render.

**Render**
Plataforma de hospedagem em nuvem onde o Chizu está publicado. Executa o servidor FastAPI e serve o sistema continuamente.

**Variável de Ambiente**
Configuração armazenada fora do código, geralmente em arquivos `.env`. No Chizu, as chaves de API dos provedores de IA são variáveis de ambiente — nunca ficam no código-fonte.

**TLS — Transport Layer Security**
Protocolo de segurança que criptografa a comunicação entre cliente e servidor. Garante que as mensagens enviadas ao Chizu não possam ser interceptadas.

---

*Ver também: [Pipeline](08-pipeline.md) · [RAG no Chizu](14-rag-no-zenbot.md) · [Engenharia de Prompts](17-engenharia-de-prompts.md)*