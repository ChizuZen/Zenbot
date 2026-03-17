# Considerações sobre Copyright e Uso de Dados

Esta página documenta a análise de conformidade e os riscos associados ao uso de obras protegidas por direitos autorais (PDFs) no treinamento e na base de conhecimento (RAG) deste projeto.

## 1. Natureza do Uso dos Dados
O projeto utiliza algumas obras literárias processadas em formato PDF para a geração de tokens e alimentação do banco de dados vetorial. É importante distinguir o contexto de uso:

* **Uso Privado/Experimental:** O processamento para fins de estudo, arquitetura de sistemas e testes de software possui baixo risco legal, uma vez que não há distribuição pública das obras originais.
* **Transformação de Dados:** A conversão de texto em *embeddings* (vetores numéricos) é considerada uma transformação técnica. O modelo não armazena o arquivo PDF original, mas sim uma representação matemática de seus conceitos.

## 2. Riscos Associados à Origem do Material
O uso de arquivos baixados da internet, sem a aquisição formal de licenças ou cópias físicas/digitais autorizadas, apresenta pontos de atenção:

* **Direito de Reprodução:** A legislação brasileira (Lei 9.610/98) e tratados internacionais protegem a obra contra reproduções não autorizadas.
* **Armazenamento em Nuvem:** O deploy em plataformas como Render ou o versionamento de dados brutos no GitHub pode expor o conteúdo a termos de serviço de terceiros.

## 3. Diretrizes para Mitigação de Riscos

Para garantir que o projeto permaneça no campo do "Fair Use" (Uso Justo) ou uso educacional, as seguintes diretrizes são aplicadas:

| Medida | Descrição |
| :--- | :--- |
| **Sintetização** | O chatbot deve ser configurado para resumir conceitos, evitando a reprodução literal de longos trechos dos livros. |
| **Não Comercialização** | Este projeto é estritamente experimental e sem fins lucrativos. |
| **Atribuição** | Todas as respostas geradas com base nos textos devem citar claramente o autor e a obra de origem. |
| **Bloqueio de Extração** | Implementação de travas no sistema (System Prompt) para impedir que usuários solicitem "copie o capítulo X do livro Y". |

## 4. Estratégia de Implementação Técnica
Para proteger a integridade do projeto, a arquitetura segue estes princípios:

1.  **Limitação de Contexto:** O sistema recupera apenas os *chunks* (pedaços) estritamente necessários para responder à dúvida, nunca a obra completa.
2.  **Disclaimer de Responsabilidade:** Inclusão de aviso legal na interface do usuário informando que as respostas são interpretações de IA baseadas em literatura de domínio público ou bibliografia de estudo.

---
*Nota: Este documento tem fins informativos e de registro de projeto, não substituindo aconselhamento jurídico formal.*