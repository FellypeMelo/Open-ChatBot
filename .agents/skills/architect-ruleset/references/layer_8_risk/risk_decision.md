# Seção 7 – Regras de Decisão Baseada em Risco (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-DECISION  
**Status:** Definitivo  
**Escopo:** Métodos de escolha informada (Trade-off) e documentação de riscos em ADRs (Architecture Decision Records).

---

### REGRISK-011 – Tomada de Decisão Baseada em Trade-off Risco x Benefício

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-011 |
| **Nome** | Tomada de Decisão Baseada em Trade-off Risco x Benefício |
| **Descrição** | O agente deve garantir que toda decisão arquitetural seja tomada com base em uma análise explícita de trade-offs entre riscos e benefícios. A análise deve incluir: **(1)** Benefícios esperados (ex: redução de custo, ganho de performance, flexibilidade); **(2)** Riscos identificados (REGRISK-001 a REGRISK-003); **(3)** Comparação entre alternativas (ex: "Alternativa A: risco alto, benefício alto; Alternativa B: risco baixo, benefício médio"); **(4)** Justificativa da escolha, com base na tolerância da organização. A decisão deve ser documentada no ADR (REGDOC-002). |
| **Objetivo** | Garantir que as decisões sejam tomadas de forma racional, considerando todos os aspectos, e não apenas por impulso ou "intuição". |
| **Motivação** | Cap. 8.1 (análise de alternativas), Cap. 9.4.2 (otimização global). |
| **Justificativa** | Decisões sem análise de trade-offs são frágeis e podem ser contestadas posteriormente. |
| **Critérios de Aplicação** | Toda decisão arquitetural de alto impacto. |
| **Critérios de Não Aplicação** | Decisões rotineiras e de baixo impacto. |
| **Pré-condições** | Riscos e benefícios identificados. |
| **Pós-condições** | Decisão documentada com rationale. |
| **Restrições** | Se a decisão envolver riscos Críticos, deve ser aprovada pelo Comitê de Arquitetura (REGGOV-002). |
| **Dependências** | REGDOC-002, REGRISK-001 a REGRISK-005. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Decisão: migrar para CockroachDB. Benefícios: escalabilidade +30%, redução de custo de licenciamento -20%. Riscos: R-001 (compatibilidade) – mitigado com camada de abstração; R-002 (curva de aprendizado) – treinamento. Decisão: aprovada, com ressalvas (plano de rollback)." |
| **Exemplo Negativo** | "Decisão: migrar para CockroachDB." (sem análise de trade-offs). |
| **Anti-pattern** | Tomar decisão baseada apenas em benefícios, ignorando riscos. |
| **Métrica** | Percentual de decisões com análise de trade-offs (meta: 100%). |
| **Critérios de Auditoria** | Revisar ADRs: se não houver análise de trade-offs, falha. |

---

### REGRISK-012 – Documentação de Decisões de Risco (ADRs com seção de Risco)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-012 |
| **Nome** | Documentação de Decisões de Risco (ADRs com seção de Risco) |
| **Descrição** | O agente deve garantir que cada ADR (REGDOC-002) inclua uma seção específica sobre riscos, contendo: **(1)** Riscos identificados associados à decisão; **(2)** Avaliação de probabilidade e impacto (REGRISK-003); **(3)** Estratégias de mitigação (REGRISK-007); **(4)** Plano de mitigação (REGRISK-006); **(5)** Risk Owner (REGRISK-008); **(6)** Status atual (aberto, mitigado, monitorado). A seção de riscos do ADR deve ser atualizada sempre que o risco for revisado (REGRISK-009). |
| **Objetivo** | Integrar a análise de riscos ao processo de decisão documental, garantindo que os riscos sejam considerados e rastreados ao longo do tempo. |
| **Motivação** | Cap. 6.2.3 (documentação de ações), Cap. 7.4.6 (rationale). |
| **Justificativa** | Riscos documentados junto com a decisão são mais fáceis de rastrear e monitorar do que em um registro separado. |
| **Critérios de Aplicação** | Todo ADR. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | ADR criado. |
| **Pós-condições** | Seção de riscos preenchida. |
| **Restrições** | A seção de riscos deve ser revisada e atualizada a cada revisão de risco. |
| **Dependências** | REGDOC-002, REGRISK-001 a REGRISK-008. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "ADR-012: Migração para CockroachDB. Riscos: R-001 (compatibilidade) – mitigado (camada de abstração), R-002 (curva de aprendizado) – mitigado (treinamento). Risk Owner: Time de Genômica. Status: mitigação em andamento." |
| **Exemplo Negativo** | "ADR-012 sem seção de riscos." |
| **Anti-pattern** | Ter uma seção de riscos, mas nunca atualizá-la. |
| **Métrica** | Percentual de ADRs com seção de riscos (meta: 100%). |
| **Critérios de Auditoria** | Revisar ADRs: se não houver seção de riscos, falha. |
