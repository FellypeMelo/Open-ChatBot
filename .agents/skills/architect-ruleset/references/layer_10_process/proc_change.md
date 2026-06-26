# Seção 5 – Regras de Gestão de Mudanças e Prototipação (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-CHANGE  
**Status:** Definitivo  
**Escopo:** Diretrizes de prototipação e entrega incremental para mitigação de riscos de requisitos e design.

---

### REGPROC-005 – Uso de Prototipação para Reduzir Incertezas em Requisitos e Design

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-005 |
| **Nome** | Uso de Prototipação para Reduzir Incertezas em Requisitos e Design |
| **Descrição** | Quando houver incerteza significativa sobre os requisitos ou sobre a viabilidade de uma solução de design, o agente deve recomendar a criação de um protótipo (descartável ou evolutivo) para validação. O protótipo deve ser desenvolvido rapidamente, com foco em aspectos críticos (ex: interface com o usuário, integração com sistemas legados, performance). O agente deve definir os objetivos do protótipo (ex: validar requisitos, testar tecnologia, demonstrar conceito) e um plano de avaliação. |
| **Objetivo** | Reduzir o risco de especificação incorreta e evitar retrabalho dispendioso em fases posteriores. |
| **Motivação** | Cap. 2.3.1 – a prototipação ajuda a antecipar mudanças e validar requisitos. |
| **Justificativa** | Protótipos permitem que os stakeholders experimentem o sistema antes do desenvolvimento completo, refinando seus requisitos. |
| **Critérios de Aplicação** | Projetos com requisitos ambíguos, novos domínios, ou tecnologias desconhecidas. |
| **Critérios de Não Aplicação** | Projetos onde os requisitos são muito estáveis e conhecidos. |
| **Pré-condições** | Identificação de incertezas. |
| **Pós-condições** | Protótipo desenvolvido e avaliado, com lições incorporadas aos requisitos. |
| **Restrições** | O protótipo não deve ser entregue como produto final, a menos que explicitamente planejado (protótipo evolutivo). |
| **Dependências** | REGREQ-001 (identificação de stakeholders), REGRISK-001 (riscos de requisitos). |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Desenvolver protótipo de interface com o usuário para validar fluxos com médicos antes de codificar o sistema de prontuário." |
| **Exemplo Negativo** | "Não precisamos de protótipo; os requisitos estão no documento." (quando o documento é ambíguo). |
| **Anti-pattern** | Desenvolver protótipo com alta qualidade e depois descartá-lo, sem extrair lições. |
| **Métrica** | Percentual de projetos com incerteza que usaram prototipação. |
| **Critérios de Auditoria** | Revisar se projetos com requisitos ambíguos utilizaram prototipação. |

---

### REGPROC-006 – Planejamento de Entregas Incrementais para Feedback Precoce

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-006 |
| **Nome** | Planejamento de Entregas Incrementais para Feedback Precoce |
| **Descrição** | O agente deve recomendar a entrega incremental sempre que possível, mesmo em projetos plan-driven. As entregas devem ser planejadas em incrementos com valor de negócio identificável, priorizando as funcionalidades mais críticas para os primeiros incrementos. Cada incremento deve ser implantado em um ambiente de produção ou staging para que os usuários possam experimentá-lo e fornecer feedback. O agente deve documentar os incrementos, seus conteúdos e as datas previstas. |
| **Objetivo** | Obter feedback precoce dos stakeholders, reduzir o risco de desalinhamento e acelerar a entrega de valor. |
| **Motivação** | Cap. 2.3.2 – entrega incremental permite que os clientes usem o software mais cedo e refinem os requisitos. |
| **Justificativa** | Quanto mais cedo o software é entregue, mais cedo o cliente pode validar se está no caminho certo. |
| **Critérios de Aplicação** | Projetos onde o cliente pode interagir com versões parciais do sistema (a maioria dos projetos de software). |
| **Critérios de Não Aplicação** | Sistemas onde a entrega parcial é inviável (ex: sistemas com dependências físicas complexas). |
| **Pré-condições** | Requisitos priorizados e incrementos definidos. |
| **Pós-condições** | Cronograma de entregas incrementais acordado com o cliente. |
| **Restrições** | Cada incremento deve ser testado e validado antes da entrega. |
| **Dependências** | REGPROC-003. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Entregas incrementais: mês 1 – login e cadastro; mês 2 – busca; mês 3 – pedidos; mês 4 – pagamentos." |
| **Exemplo Negativo** | "Entregaremos tudo no final, pois é mais fácil gerenciar." |
| **Anti-pattern** | Planejar incrementos muito grandes (ex: > 3 meses) que não geram feedback útil. |
| **Métrica** | Número de incrementos entregues no prazo. |
| **Critérios de Auditoria** | Verificar se o cronograma de entregas incrementais foi cumprido. |
