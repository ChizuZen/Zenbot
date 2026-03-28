#  Monitoramento e Alta Disponibilidade — Chizu no Render

Este documento registra a configuração de monitoramento do Chizu em produção,
garantindo que o servidor nunca hiberne e que falhas sejam detectadas imediatamente.

---

##  O Problema — Hibernação no Render Free

O Render no plano gratuito hiberna o servidor após **15 minutos de inatividade**.

Consequências:
- Primeira requisição após hibernação demora **30 a 60 segundos**
- O UptimeRobot registra o servidor como **Down** durante esse período
- A Alexa Skill pode receber timeout (limite de 8 segundos)

**Solução:** manter o servidor acordado com pings periódicos a cada 5 minutos.

---

##  Solução — UptimeRobot

O [UptimeRobot](https://uptimerobot.com) é um serviço gratuito que:

- faz ping no servidor a cada **5 minutos**
- monitora disponibilidade **24h por dia**
- envia **alerta por email** se o servidor cair
- funciona independente do seu computador estar ligado

---

##  Configuração do Monitor

###  Criar conta gratuita

Acesse [uptimerobot.com](https://uptimerobot.com) e crie sua conta.

###  Adicionar monitor

Clique em **+ Add New Monitor** e preencha:

| Campo | Valor |
|---|---|
| Monitor Type | HTTP(s) |
| Friendly Name | Chizu Zen |
| URL | https://chizu.ia.br |
| Monitoring Interval | Every 5 minutes |

Clique em **Create Monitor**.

###  Configurar alerta por email

Em **Alert Contacts**, adicione seu email para receber notificações imediatas
caso o Chizu fique fora do ar.

---

##  Como funciona
```
UptimeRobot → https://chizu.ia.br (a cada 5 min)
                    ↓
            Render permanece acordado
                    ↓
            Chizu responde em < 200ms
```

Com ping a cada 5 minutos, o servidor **nunca atinge os 15 minutos de inatividade**
e a hibernação nunca ocorre.

---

## Problema detectado — HEAD 405

Durante os primeiros testes, os logs do Render mostraram:
```
"HEAD / HTTP/1.1" 405 Method Not Allowed
```

O UptimeRobot faz requisições `HEAD` por padrão, e o FastAPI não respondia
a esse método na rota `/`, gerando falsos alarmes de **Down**.

### Solução aplicada no `web.py`
```python
@app.head("/")
async def head_index():
    return Response(status_code=200)
```

Adicionando a rota `HEAD /`, o FastAPI passa a responder corretamente ao
UptimeRobot, eliminando os falsos alarmes.

---

##  Primeiro incidente registrado

| Campo | Valor |
|---|---|
| Data | 15 de março de 2026 |
| Hora | 16:40 GMT-3 |
| Duração | 6 minutos e 34 segundos |
| Causa raiz | Hibernação do Render free |
| Status | Resolvido automaticamente |

O incidente ocorreu no primeiro acesso após o deploy — o servidor estava
hibernado e levou 6 minutos para acordar completamente. Com o UptimeRobot
ativo, esse cenário não se repetirá.

---

##  Domínio e DNS

| Tipo | Nome | Valor |
|---|---|---|
| A | chizu.ia.br | 216.24.57.1 |
| CNAME | www.chizu.ia.br | chizu.onrender.com |

Registros configurados no [Registro.br](https://registro.br) com propagação
via Cloudflare. Tempo de propagação observado: **menos de 30 minutos**.

---

##  Status atual

| Serviço | Status |
|---|---|
| https://chizu.ia.br | 🟢 Online |
| https://www.chizu.ia.br | 🟢 Online |
| UptimeRobot | 🟢 Monitorando |
| SSL/HTTPS | 🟢 Ativo |
| Render | 🟢 Acordado |

---

##  Lição aprendida

> O servidor não precisa ser pago para ser confiável.  
> Basta um monitor gratuito e um ping a cada 5 minutos.