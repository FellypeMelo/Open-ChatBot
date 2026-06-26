# Seção 5 – Regras de Mitigação e Planejamento (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-MITIGATE  
**Status:** Definitivo  
**Escopo:** Definição de planos de mitigação estruturados, seleção fundamentada de estratégias (Evitar, Transferir, Mitigar, Aceitar) e designação formal de responsabilidade (Risk Owner).

---

### REGRISK-006 – Plano de Mitigação Obrigatório para Riscos Críticos e Altos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-006 |
| **Nome** | Plano de Mitigação Obrigatório para Riscos Críticos e Altos |
| **Descrição** | O agente deve garantir que para todo risco classificado como **Crítico** ou **Alto** (REGRISK-003), um Plano de Mitigação formal seja elaborado. O plano deve conter: **(1)** Descrição da ação de mitigação (ex: "implementar circuito breaker", "contratar seguro", "realizar testes de carga"); **(2)** Estratégia de mitigação (Evitar, Transferir, Mitigar, Aceitar – REGRISK-007); **(3)** Responsável (Risk Owner – REGRISK-008); **(4)** Cronograma (data de início e conclusão); **(5)** Recursos necessários (orçamento, pessoal); **(6)** Critérios de sucesso (como saber se a mitigação foi eficaz); **(7)** Plano de contingência (caso a mitigação falhe). |
| **Objetivo** | Garantir que riscos críticos sejam gerenciados proativamente, com ações concretas e responsáveis claros. |
| **Motivação** | ISO 31000, Cap. 9.4.2. |
| **Justificativa** | Riscos sem plano de mitigação tendem a se materializar e causar danos desnecessários. |
| **Critérios de Aplicação** | Riscos Críticos e Altos. |
| **Critérios de Não Aplicação** | Riscos Baixos (que podem ser aceitos sem plano formal, mas monitorados). |
| **Pré-condições** | Risco identificado e classificado. |
| **Pós-condições** | Plano de mitigação aprovado e em execução. |
| **Restrições** | O plano deve ser revisado a cada revisão de risco (trimestral). |
| **Dependências** | REGRISK-003, REGRISK-008. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "R-001: Falha de compatibilidade com ORM. Mitigação: implementar camada de abstração (Adapter Pattern). Responsável: Time de Genômica. Prazo: 3 meses. Critério de sucesso: 100% das queries passam no teste de compatibilidade. Contingência: rollback para versão anterior." |
| **Exemplo Negativo** | "R-001 será tratado quando ocorrer." |
| **Anti-pattern** | Plano de mitigação vago (ex: "monitorar o risco"). |
| **Métrica** | Percentual de riscos Críticos/Altos com plano de mitigação (meta: 100%). |
| **Critérios de Auditoria** | Revisar Risk Register: se algum risco crítico não tiver plano, falha. |

---

### REGRISK-007 – Estratégias de Mitigação (Evitar, Transferir, Mitigar, Aceitar) – Escolha Justificada

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-007 |
| **Nome** | Estratégias de Mitigação (Evitar, Transferir, Mitigar, Aceitar) – Escolha Justificada |
| **Descrição** | O agente deve garantir que para cada risco, uma das quatro estratégias de mitigação seja escolhida e justificada: **(1) Evitar**: eliminar a causa (ex: não adotar a tecnologia arriscada); **(2) Transferir**: transferir o risco para terceiros (ex: seguro, outsourcing, SLA); **(3) Mitigar**: reduzir probabilidade e/ou impacto (ex: implementar controles); **(4) Aceitar**: reconhecer o risco e conviver com ele (ex: risco baixo ou de baixo impacto). A escolha deve ser baseada no custo da mitigação vs. o custo do risco (Risk Score) e na tolerância da organização. A justificativa deve ser documentada no ADR ou Risk Register. |
| **Objetivo** | Garantir que a abordagem de cada risco seja intencional, não por omissão. |
| **Motivação** | ISO 31000, Cap. 9.4.2. |
| **Justificativa** | Aceitar um risco sem justificativa é uma decisão implícita e potencialmente perigosa. |
| **Critérios de Aplicação** | Todo risco identificado. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Risco classificado. |
| **Pós-condições** | Estratégia escolhida e documentada. |
| **Restrições** | A estratégia "Aceitar" só é válida para riscos Baixos ou para riscos com custo de mitigação maior que o impacto esperado. |
| **Dependências** | REGRISK-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-002: Curva de aprendizado da equipe. Estratégia: Mitigar (treinamento de 2 semanas). Justificativa: custo do treinamento (R$ 20k) é menor que o atraso estimado (R$ 100k)." |
| **Exemplo Negativo** | "R-002: será monitorado." (sem justificativa). |
| **Anti-pattern** | Aceitar riscos altos sem justificativa, apenas para "manter o cronograma". |
| **Métrica** | Percentual de riscos com estratégia documentada (meta: 100%). |
| **Critérios de Auditoria** | Revisar se cada risco tem estratégia e justificativa. |

---

### REGRISK-008 – Designação de Risk Owner Obrigatória

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-008 |
| **Nome** | Designação de Risk Owner Obrigatória |
| **Descrição** | O agente deve garantir que para cada risco, um Risk Owner (pessoa ou time) seja designado. O Risk Owner é responsável por: **(1)** Implementar o plano de mitigação; **(2)** Monitorar o risco (probabilidade, impacto); **(3)** Reportar o status do risco ao Comitê de Arquitetura; **(4)** Escalar se o risco mudar de criticidade. A designação deve seguir a matriz RACI (REGGOV-001) e ser acordada com o designado. |
| **Objetivo** | Garantir que cada risco tenha um "dono" claramente responsável por sua gestão. |
| **Motivação** | Cap. 9.4.2 (governança), ISO 31000. |
| **Justificativa** | Riscos sem dono são gerenciados por ninguém. |
| **Critérios de Aplicação** | Todo risco identificado. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Estrutura organizacional definida. |
| **Pós-condições** | Risk Owner designado e ciente. |
| **Restrições** | O Risk Owner não pode ser o mesmo que o proponente da decisão (para evitar viés de otimismo). |
| **Dependências** | REGGOV-001, REGRISK-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-001: Risk Owner = Time de Genômica (responsável pela implementação da camada de abstração)." |
| **Exemplo Negativo** | "R-001: sem dono." |
| **Anti-pattern** | Designar um Risk Owner que não tem autoridade ou recursos para mitigar o risco. |
| **Métrica** | Percentual de riscos com Risk Owner (meta: 100%). |
| **Critérios de Auditoria** | Revisar Risk Register: se algum risco não tiver dono, falha. |
