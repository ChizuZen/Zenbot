# Comandos Úteis

Esta página reúne os comandos usados no dia a dia do desenvolvimento do Chizu — uma referência rápida para consulta no terminal.

---

## Navegação e ambiente

### Entrar no projeto

```bash
cd /Volumes/CT500MX5/SITE/chizu
```

### Ativar o ambiente virtual

Sempre o primeiro passo antes de qualquer comando Python:

```bash
source venv/bin/activate
```

O terminal mostra `(venv)` no início da linha quando o ambiente está ativo.

### Abrir o projeto no VS Code

```bash
code . -n
```

### Limpar o terminal

```bash
clear
```

### Mostrar arquivos ocultos no Finder (macOS)

```
Command + Shift + . (ponto)
```

---

## Servidor local

### Subir o servidor do Chizu

```bash
uvicorn web:app --reload --port 8001
```

Acesse em: [http://localhost:8001](http://localhost:8001)

### Subir a documentação MkDocs

```bash
mkdocs serve
```

Acesse em: [http://localhost:8000/](http://localhost:8000/)

---

## Git — controle de versão

### Ver status dos arquivos modificados

```bash
git status
```

### Adicionar arquivo específico

```bash
git add web.py
```

### Adicionar todos os arquivos modificados

```bash
git add .
```

### Fazer commit com mensagem

```bash
git commit -m "descrição do que foi feito"
```

### Enviar para o GitHub

```bash
git push origin main
```

---

## Documentação MkDocs

### Gerar o site estático

```bash
mkdocs build
```

### Publicar no GitHub Pages

```bash
mkdocs gh-deploy
```

### Criar arquivo de documentação vazio

```bash
touch docs/conceitos/nome-do-arquivo.md
```

---

## Estrutura de arquivos

### Ver árvore de pastas (2 níveis)

```bash
tree -L 2
```

### Ver árvore incluindo arquivos ocultos (3 níveis)

```bash
tree -L 3 -a
```

### Remover arquivos .DS_Store do macOS

```bash
find textos -name ".DS_Store" -delete
```

---

## Testes com curl

### Testar pergunta simples

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "ansiedade"}'
```

### Teste da Casca de Banana (conhecimento externo)

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Mestre, o que Steve Jobs aprendeu com o Zen?"}'
```

### Teste de citação obrigatória (RAG)

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Caminhante busca entender por que não deve se preocupar tanto com o futuro."}'
```

### Teste de limite de tokens

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Mestre, me fale sobre a importância do silêncio e como ele nos ajuda a ver a verdade."}'
```

### Outros testes rápidos

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "como lidar com a raiva?"}'
```

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "o que é impermanência?"}'
```

### Testar filtro por mestre (@nome)

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "o que é zazen?", "autor": "Eihei Dogen"}'
```

---

## Verificar chave do Gemini

```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=SUA_CHAVE" \
  -H "Content-Type: application/json" \
  -d '{"contents": [{"role": "user", "parts": [{"text": "diga apenas: ok"}]}]}' \
  | python3 -m json.tool
```

Substitua `SUA_CHAVE` pela chave real. Deve retornar `"text": "ok"`.

---

## DNS

### Verificar resolução do domínio

```bash
nslookup chizu.ia.br
```

### Consulta detalhada de DNS

```bash
dig chizu.ia.br
```

---

## Links úteis

| Serviço | URL |
|---|---|
| Chizu local | http://localhost:8001 |
| Documentação local | http://localhost:8000/ |
| Render — painel | https://dashboard.render.com/web/srv-d6d5iknfte5s73d62img |
| GitHub Actions | https://github.com/chizu-ia/chizu/actions |
| Chizu em produção | http://chizu.ia.br |

---

*Ver também: [Fluxo de trabalho](fluxo-de-trabalho.md) · [Protocolo de Testes](protocolo-de-testes.md)*
