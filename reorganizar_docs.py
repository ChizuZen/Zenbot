"""
reorganizar_docs.py
Move todos os arquivos de docs/conceitos/ para docs/,
renomeia sem números e gera novo mkdocs.yml.

Uso:
  python reorganizar_docs.py --dry-run   # só mostra o que seria feito
  python reorganizar_docs.py             # executa de verdade
"""

import os
import re
import sys
import shutil
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
DOCS = Path("docs")
CONCEITOS = DOCS / "conceitos"

# Mapeamento: arquivo atual → novo nome (tudo em docs/)
MAPA = {
    # Da raiz docs/
    "00-por-que-chizu.md":          "por-que-chizu.md",
    "01-motivacao.md":              "motivacao.md",
    "02-visao-geral.md":            "visao-geral.md",
    "03-evolucao-do-projeto.md":    "evolucao.md",
    "04-arquitetura.md":            "arquitetura.md",
    "05-ferramentas.md":            "ferramentas.md",
    "06-fluxo-de-trabalho.md":      "fluxo-de-trabalho.md",
    "07-comandos-uteis.md":         "comandos-uteis.md",
    "08-organizacao-dos-textos.md": "organizacao-dos-textos.md",
    "09-roadmap.md":                "roadmap.md",
    "10-jornada-de-aprendizado.md": "jornada.md",
    # Da pasta conceitos/
    "conceitos/01-sistemas-operacionais.md":          "sistemas-operacionais.md",
    "conceitos/02-ferramentas-de-desenvolvimento.md": "ferramentas-de-desenvolvimento.md",
    "conceitos/03-servidores-e-deploy.md":            "servidores-e-deploy.md",
    "conceitos/04-arquitetura.md":                    "arquitetura-interna.md",
    "conceitos/04-inteligencia-artificial.md":        "inteligencia-artificial.md",
    "conceitos/05-modelos-e-llms.md":                 "modelos-e-llms.md",
    "conceitos/06-embeddings-e-chunks.md":            "embeddings-e-chunks.md",
    "conceitos/07-busca-semantica.md":                "busca-semantica.md",
    "conceitos/07-comandos-uteis.md":                 "comandos-uteis-dev.md",
    "conceitos/08-organizacao-dos-textos.md":         "organizacao-dos-textos-dev.md",
    "conceitos/08-pipeline.md":                       "pipeline.md",
    "conceitos/09-metafora-zen.md":                   "metafora-zen.md",
    "conceitos/09-roadmap.md":                        "roadmap-detalhado.md",
    "conceitos/10-validacao-perguntas.md":            "validacao-perguntas.md",
    "conceitos/11-ajustes.md":                        "ajustes.md",
    "conceitos/14-rag-no-zenbot.md":                  "rag.md",
    "conceitos/16-dependencias-importacoes.md":       "dependencias-importacoes.md",
    "conceitos/17-engenharia-de-prompts.md":          "engenharia-de-prompts.md",
    "conceitos/18-documentacao_testes.md":            "protocolo-de-testes.md",
    "conceitos/19-verificacao_dns.md":                "verificacao-dns.md",
    "conceitos/20-monitoramento.md":                  "monitoramento.md",
    "conceitos/21-firewall.md":                       "firewall.md",
    "conceitos/22-cloudflare.md":                     "cloudflare.md",
    "conceitos/23-copyright.md":                      "copyright.md",
    "conceitos/24-aviso-legal.md":                    "aviso-legal.md",
    "conceitos/25-apoio.md":                          "apoio.md",
    "conceitos/26-alexa.md":                          "alexa.md",
    "conceitos/27-whatsapp.md":                       "whatsapp.md",
    "conceitos/28-expansao-acervo-e-filtro-autor.md": "outros-mestres.md",
    "conceitos/29-caixa-postal.md":                   "caixa-postal.md",
    "conceitos/30-glossario.md":                      "glossario.md",
    "conceitos/31-voz.md":                            "voz.md",
    "conceitos/32-marco-identidade.md":               "marco-identidade.md",
    "conceitos/index.md":                             "conceitos-introducao.md",
}

MKDOCS = """site_name: Chizu Mestre Zen
site_description: Documentação do projeto Chizu — Mestre Zen
site_author: Projeto Chizu
site_url: https://docs.chizu.ia.br/
theme:
  name: mkdocs
  language: pt
extra_css:
  - style.css
nav:
  - Início: index.md
  - Projeto:
    - Por que Chizu?: por-que-chizu.md
    - Motivação: motivacao.md
    - Visão geral: visao-geral.md
    - Evolução: evolucao.md
    - Marco — Identidade Própria: marco-identidade.md
    - Arquitetura: arquitetura.md
    - Roadmap: roadmap.md
    - Diário de construção: jornada.md
  - Desenvolvimento:
    - Ferramentas: ferramentas.md
    - Fluxo de trabalho: fluxo-de-trabalho.md
    - Comandos úteis: comandos-uteis.md
    - Comandos úteis (dev): comandos-uteis-dev.md
    - Organização dos textos: organizacao-dos-textos.md
    - Organização dos textos (dev): organizacao-dos-textos-dev.md
    - Pipeline: pipeline.md
    - Arquitetura e Importações: dependencias-importacoes.md
    - Engenharia de Prompts: engenharia-de-prompts.md
    - Ajustes do Sistema: ajustes.md
    - Protocolo de Teste: protocolo-de-testes.md
  - Conceitos:
    - Introdução: conceitos-introducao.md
    - Glossário: glossario.md
    - Sistemas operacionais: sistemas-operacionais.md
    - Ferramentas de desenvolvimento: ferramentas-de-desenvolvimento.md
    - Servidores e deploy: servidores-e-deploy.md
    - Inteligência artificial: inteligencia-artificial.md
    - Modelos e LLMs: modelos-e-llms.md
    - Embeddings e Chunks: embeddings-e-chunks.md
    - Busca semântica: busca-semantica.md
    - RAG: rag.md
    - Metáfora Zen: metafora-zen.md
    - Validação de Perguntas: validacao-perguntas.md
    - Arquitetura interna: arquitetura-interna.md
    - Roadmap detalhado: roadmap-detalhado.md
    - Outros Mestres: outros-mestres.md
  - Infraestrutura:
    - Verificação de DNS: verificacao-dns.md
    - Monitoramento do Sistema: monitoramento.md
    - Firewall e Resiliência: firewall.md
    - Web Application Firewall: cloudflare.md
    - Caixa Postal: caixa-postal.md
  - Canais:
    - Voz: voz.md
    - Alexa: alexa.md
    - Whatsapp: whatsapp.md
  - Sobre:
    - Copyright: copyright.md
    - Aviso Legal: aviso-legal.md
    - Apoie o Projeto: apoio.md
"""

def main():
    print(f"{'[DRY-RUN] ' if DRY_RUN else ''}Reorganizando documentação...\n")

    # Mover e renomear arquivos
    for origem_rel, destino_nome in MAPA.items():
        origem = DOCS / origem_rel
        destino = DOCS / destino_nome

        if not origem.exists():
            print(f"  ⚠️  Não encontrado: {origem}")
            continue

        print(f"  {'→' if not DRY_RUN else '~'} {origem_rel} → {destino_nome}")
        if not DRY_RUN:
            shutil.copy2(origem, destino)

    if not DRY_RUN:
        # Remover arquivos originais da raiz docs/
        for origem_rel in MAPA:
            origem = DOCS / origem_rel
            novo = DOCS / MAPA[origem_rel]
            if origem.exists() and origem != novo:
                origem.unlink()

        # Remover pasta conceitos se vazia
        if CONCEITOS.exists() and not any(CONCEITOS.iterdir()):
            CONCEITOS.rmdir()
            print("\n  🗑️  Pasta conceitos/ removida (estava vazia)")

        # Gerar mkdocs.yml
        with open("mkdocs.yml", "w", encoding="utf-8") as f:
            f.write(MKDOCS)
        print("\n  ✅ mkdocs.yml gerado!")

    print(f"\n{'─'*50}")
    if DRY_RUN:
        print("🔍 Dry-run concluído. Rode sem --dry-run para aplicar.")
    else:
        print("✅ Reorganização concluída! Teste com: mkdocs serve")

if __name__ == "__main__":
    main()