## Implementação do Cloudflare WAF (Web Application Firewall)

Configurar o Cloudflare é a solução mais **"Zen"** e eficiente. Como o bloqueio acontece na rede deles (na borda), as requisições maliciosas nem chegam ao Render, economizando 100% da banda, CPU e, principalmente, a memória que o **Chizu** precisa para processar IA.

---

### 1. Configuração Inicial (DNS)
Se você ainda não utiliza o Cloudflare:
* **Conta:** Crie uma conta gratuita em [cloudflare.com](https://www.cloudflare.com).
* **Domínio:** Adicione seu domínio (ex: `seudominio.com.br`).
* **Nameservers:** No **Registro.br**, altere os Nameservers para os indicados pelo Cloudflare.
* **Proxy Status:** Na aba **DNS**, certifique-se de que a nuvem na coluna "Proxy status" esteja **laranja (Proxied)**. Isso garante que o tráfego seja filtrado antes de chegar ao Render.

---

### 2. Criando a Regra de Bloqueio (WAF)
O plano gratuito permite até 5 regras. Vamos configurar uma específica para scanners:

1. Vá em **Security > WAF > Custom Rules**.
2. Clique em **Create rule**.
3. **Nome da regra:** `Bloqueio de Scanners WP`.
4. **Field:** Selecione `URI Path`.
5. **Operator:** Selecione `contains`.
6. **Value:** Digite `wp-`.
7. Clique em **OR** para adicionar outros padrões: `xmlrpc`, `.env`, `wlwmanifest`.
8. **Action:** Selecione **Block**.
9. Clique em **Deploy**.

---

### 3. Ativando o "Bot Fight Mode"
Para barrar robôs automáticos de forma global:
1. Vá em **Security > Bots**.
2. Ative o **Bot Fight Mode**.
   > Isso desafia bots conhecidos com um "JavaScript Challenge" antes mesmo de acessarem qualquer página.

---

### Vantagens para o Projeto no Render

* **Logs Limpos:** O console do Render mostrará apenas tráfego real e útil.
* **Memória Protegida:** O app Python não precisa instanciar nada para descartar a requisição.
* **Proteção contra DoS:** O Cloudflare absorve ataques de força bruta, mantendo o serviço estável.

---

### Comparação Final: Middleware vs. Cloudflare

| Recurso | Middleware (Python) | Cloudflare (DNS) |
| :--- | :--- | :--- |
| **Custo de Memória** | Pequeno (mas existe) | **Zero** |
| **Custo de Banda** | Você paga pelo tráfego | **Zero (bloqueia antes)** |
| **Dificuldade** | Alterar código/redeploy | Configuração de DNS |
| **Eficácia** | Bloqueia no app | **Bloqueia na fronteira** |