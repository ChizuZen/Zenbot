# Segurança e Resiliência: Proteção contra Scanners e Bots

Este documento descreve as estratégias de segurança implementadas e planejadas para proteger o projeto **Chizu** contra acessos maliciosos, garantindo a disponibilidade dos recursos (CPU e RAM) no ambiente Render.

---

## O Problema: Vulnerability Scanners
Logs de acesso revelaram tentativas sistemáticas de requisições buscando diretórios vulneráveis conhecidos (ex: WordPress), mesmo o sistema não utilizando tais tecnologias.

**Exemplo de Log de Ataque:**
`INFO: 45.94.31.197:0 - "GET //wp-includes/wlwmanifest.xml HTTP/1.1" 404 Not Found`

Essas requisições, embora resultem em erro 404, consomem:
1. **Banda de rede** no servidor.
2. **Memória RAM** para processar a requisição no FastAPI.
3. **CPU** para gerar a resposta de erro.

---

##  Estratégias de Mitigação

###  Middleware de Auto-Bloqueio (Nível de Aplicação)
Para ambientes onde não há acesso ao Firewall do Sistema Operacional (PaaS como Render), implementamos um middleware em Python que atua como um "Fail2Ban" interno.

* **Lógica:** Identifica padrões de URL (ex: `wp-admin`, `.env`) e bane o IP de origem temporariamente.
* **Gestão de Memória:** Utiliza um `OrderedDict` limitado a **30 IPs**, garantindo que a lista de banidos não cause estouro de memória (Memory Quota Exceeded).
```text
import time
from collections import OrderedDict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Configurações de Segurança
MAX_BANNED_IPS = 30
BAN_TIME = 3600  # 1 hora em segundos
FORBIDDEN_PATTERNS = [
    "wp-includes", "wp-admin", "xmlrpc", "wp-content", 
    ".env", "wordpress", "wlwmanifest.xml", "sito", "cms"
]

# Dicionário limitado para não estourar a RAM
banned_ips = OrderedDict()

class AntiScannerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # 1. Verifica se o IP está banido
        if client_ip in banned_ips:
            ban_timestamp = banned_ips[client_ip]
            if current_time - ban_timestamp < BAN_TIME:
                # Retorna 403 sem processar mais nada
                raise HTTPException(status_code=403, detail="Access denied.")
            else:
                # Tempo de banimento expirou, remove da lista
                del banned_ips[client_ip]

        # 2. Captura tentativas de acesso a caminhos suspeitos
        path = request.url.path.lower()
        if any(pattern in path for pattern in FORBIDDEN_PATTERNS):
            # Adiciona ao dicionário de banidos
            banned_ips[client_ip] = current_time
            
            # Mantém o limite de 30 IPs para preservar memória
            if len(banned_ips) > MAX_BANNED_IPS:
                banned_ips.popitem(last=False) # Remove o mais antigo (primeiro a entrar)
            
            print(f"🚫 IP {client_ip} banido por scan: {path}")
            raise HTTPException(status_code=403, detail="Security block.")

        return await call_next(request)
# Adicione o middleware ao seu app
# app.add_middleware(AntiScannerMiddleware)
```


###  Cloudflare (Nível de Borda) - Solução Recomendada
A solução definitiva move a segurança para a "borda" da rede (Edge), antes mesmo do tráfego chegar ao Render.

* **DNS Proxy:** O Cloudflare mascara o IP real do servidor.
* **WAF (Web Application Firewall):** Regras personalizadas para bloquear requisições suspeitas.
* **SSL/TLS:** Garante o protocolo HTTPS necessário para integrações externas (como a Alexa).

---

##  Configuração do Cloudflare WAF

Para proteger o sistema, as seguintes regras de bloqueio (Custom Rules) devem ser configuradas no painel da Cloudflare:

| Campo | Operador | Valor | Ação |
| :--- | :--- | :--- | :--- |
| URI Path | contains | `wp-` | Block |
| URI Path | contains | `xmlrpc` | Block |
| URI Path | contains | `.env` | Block |
| URI Path | contains | `wlwmanifest` | Block |

---

##  Integração com Alexa e SSL

A segurança via Cloudflare facilita a conformidade com os requisitos da Amazon Alexa:
1. **Certificado Válido:** A Alexa exige HTTPS com certificado assinado por CA confiável.
2. **Modo SSL:** Configurado como **Full** ou **Full (Strict)** no Cloudflare.
3. **Endpoint Seguro:** Garante que a Skill se comunique apenas com um servidor autenticado, protegendo a privacidade dos usuários.


---
###  Resumo da Recomendação

| Solução | Impacto na RAM | Eficácia |
| :--- | :--- | :--- |
| **Middleware Simples** | Baixo (se limitado) | Média (bloqueia após chegar no app) |
| **Middleware com Cache** | Controlado | Média |
| **Cloudflare (WAF)** | **Zero** | **Alta (bloqueia antes do app)** |

---

##  Conclusão
A combinação de um **Middleware leve** (para proteção interna residual) com o **Cloudflare WAF** (para proteção de borda) cria uma arquitetura de "Resiliência Total", permitindo que o Chizu foque seus recursos computacionais no processamento de IA e filosofia Zen.