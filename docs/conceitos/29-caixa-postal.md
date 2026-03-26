#  Caixa Postal sem Servidor de E-mail

## O Desafio

O Mestre Chizu tem um domínio próprio — `chizu.ia.br` — mas não tem um servidor de e-mail.  
Ainda assim, precisávamos que o endereço `mestre@chizu.ia.br` funcionasse de verdade:  
receber mensagens e responder com esse remetente, tudo de dentro do Gmail.

A solução veio com dois serviços gratuitos trabalhando juntos.

---

## A Arquitetura

```
Alguém envia para mestre@chizu.ia.br
        ↓
ForwardEmail.net recebe e encaminha
        ↓
chizuzenbot@gmail.com recebe no Gmail
        ↓
Resposta enviada via Brevo (SMTP)
        ↓
Destinatário vê: Mestre Chizu <mestre@chizu.ia.br>
```

---

## Serviço 1 — Receber: ForwardEmail

[ForwardEmail.net](https://forwardemail.net) é um serviço gratuito e open source  
que recebe e-mails do seu domínio e os encaminha para qualquer caixa Gmail.

### Configuração DNS

Adicione os registros abaixo na zona DNS do domínio:

| Tipo | Nome | Dados |
|------|------|-------|
| MX | chizu.ia.br | `10 mx1.forwardemail.net` |
| MX | chizu.ia.br | `10 mx2.forwardemail.net` |
| TXT | chizu.ia.br | `"forward-email=mestre:chizuzenbot@gmail.com"` |

O registro TXT instrui o ForwardEmail a encaminhar qualquer mensagem  
enviada para `mestre@chizu.ia.br` direto para `chizuzenbot@gmail.com`.

---

## Serviço 2 — Enviar: Brevo

[Brevo](https://brevo.com) (antigo Sendinblue) oferece um relay SMTP gratuito  
que permite enviar e-mails autenticados usando o seu domínio como remetente.

### Configuração no Brevo

1. Crie uma conta gratuita em [brevo.com](https://brevo.com)
2. Vá em **Configurações → Senders & IP → Domains**
3. Adicione o domínio `chizu.ia.br`
4. O Brevo vai solicitar a adição de registros DNS para autenticação

### Registros DNS do Brevo

| Tipo | Nome | Dados |
|------|------|-------|
| TXT | chizu.ia.br | `"v=spf1 include:spf.brevo.com ~all"` |
| TXT | chizu.ia.br | `"brevo-code:cf8b487b875b1b3d29a5a6ed91e1fccb"` |
| TXT | _dmarc.chizu.ia.br | `"v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com"` |
| CNAME | brevo1._domainkey.chizu.ia.br | `b1.chizu-ia-br.dkim.brevo.com` |
| CNAME | brevo2._domainkey.chizu.ia.br | `b2.chizu-ia-br.dkim.brevo.com` |

### Configuração no Gmail

1. No Gmail, vá em **Configurações → Contas e importação**
2. Em **Enviar e-mail como**, clique em **Adicionar outro endereço de e-mail**
3. Preencha:
   - **Nome:** Mestre Chizu
   - **Endereço:** `mestre@chizu.ia.br`
4. Configure o SMTP do Brevo:
   - **Servidor SMTP:** `smtp-relay.brevo.com`
   - **Porta:** `587`
   - **Segurança:** TLS
   - **Usuário e senha:** gerados no painel do Brevo
5. Confirme o código de verificação enviado pelo Gmail

---

## Resultado

Após a propagação do DNS (pode levar até 24h), o fluxo funciona assim:

- **Receber:** qualquer e-mail enviado para `@chizu.ia.br` chega no Gmail
- **Enviar:** ao responder, basta escolher `mestre@chizu.ia.br` como remetente
- **Autenticação:** SPF, DKIM e DMARC garantem que o e-mail não caia no spam

O destinatário vê apenas:

```
Mestre Chizu <mestre@chizu.ia.br>
Enviado por: smtp-relay.brevo.com
Conexão segura na porta 587 usando TLS
```

---

## Por que essa solução?

| Critério | Resultado |
|----------|-----------|
| Custo | Gratuito |
| Servidor de e-mail próprio | Não necessário |
| Domínio personalizado | ✅ |
| Autenticação (SPF/DKIM/DMARC) | ✅ |
| Funciona dentro do Gmail | ✅ |

Uma solução zen: simples, elegante, sem peso desnecessário. 🙏