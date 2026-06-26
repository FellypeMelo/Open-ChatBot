# Seção 3 – Regras de Gestão de Riscos (Layer 14 - PM-RISK)

---

### REGPM-001 – Identificação de Riscos com Checklist e Brainstorming

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-001 |
| **Nome** | Identificação de Riscos com Checklist e Brainstorming |
| **Descrição** | O agente deve iniciar a gestão de riscos identificando riscos potenciais usando duas técnicas complementares: **(1)** Checklist de Riscos: revisar categorias comuns (pessoas, tecnologia, requisitos, estimativas, organização, ferramentas) para identificar riscos conhecidos; **(2)** Brainstorming: realizar sessões com a equipe e stakeholders para identificar riscos específicos do projeto. O agente deve documentar cada risco com: ID, descrição, categoria, probabilidade estimada (baixa, média, alta) e impacto estimado (baixo, médio, alto). |
| **Objetivo** | Garantir que os riscos sejam identificados de forma abrangente, cobrindo tanto riscos comuns quanto específicos do projeto. |
| **Motivação** | Cap. 22.1.1 – a identificação de riscos é o primeiro passo para gerenciá-los. |
| **Justificativa** | Riscos não identificados não podem ser gerenciados; eles se tornam surpresas no meio do projeto. |
| **Critérios de Aplicação** | No início de todo projeto e em revisões periódicas (ex: trimestrais). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Informações sobre o projeto (escopo, equipe, tecnologia) disponíveis. |
| **Pós-condições** | Lista inicial de riscos documentada. |
| **Restrições** | O brainstorming deve incluir participantes de diferentes áreas (ex: desenvolvimento, QA, operações, negócio). |
| **Dependências** | REGRISK-001 (análise de riscos arquiteturais). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Identificamos 15 riscos: R-001 (perda de desenvolvedor sênior), R-002 (mudança de requisitos), R-003 (atraso na entrega de hardware), etc." |
| **Exemplo Negativo** | "Não temos riscos; o projeto é simples." |
| **Anti-pattern** | Identificar apenas riscos óbvios (ex: atraso) e ignorar riscos menos óbvios (ex: mudança de tecnologia). |
| **Métrica** | Número de riscos identificados por projeto (meta: ≥ 10). |
| **Critérios de Auditoria** | Verificar se há um registro de riscos documentado e atualizado. |

---

### REGPM-002 – Análise de Riscos com Matriz de Probabilidade x Impacto

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-002 |
| **Nome** | Análise de Riscos com Matriz de Probabilidade x Impacto |
| **Descrição** | Para cada risco identificado, o agente deve avaliar sua probabilidade e impacto utilizando uma escala de 1 a 5 (ou baixo-médio-alto) e posicioná-lo em uma matriz 5x5. A matriz deve classificar os riscos em quatro níveis: **(1)** Crítico (probabilidade alta e impacto alto) – requer ação imediata; **(2)** Alto (probabilidade média/alta e impacto médio/alto) – requer plano de mitigação; **(3)** Médio (probabilidade/impacto médio) – monitoramento; **(4)** Baixo – aceitação. O agente deve priorizar os riscos críticos e altos para mitigação. |
| **Objetivo** | Priorizar riscos com base em sua criticidade, alocando recursos de forma eficiente. |
| **Motivação** | Cap. 22.1.2 – a análise de riscos envolve avaliar probabilidade e impacto. |
| **Justificativa** | Sem priorização, todos os riscos parecem igualmente importantes, levando a alocação ineficiente de recursos. |
| **Critérios de Aplicação** | Após a identificação de riscos (REGPM-001). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Riscos identificados. |
| **Pós-condições** | Riscos priorizados e classificados. |
| **Restrições** | A matriz deve ser revisada periodicamente, pois probabilidade e impacto podem mudar. |
| **Dependências** | REGPM-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "R-001 (perda de desenvolvedor sênior): probabilidade 4, impacto 5 → crítico. R-002 (mudança de requisitos): probabilidade 3, impacto 4 → alto." |
| **Exemplo Negativo** | "Todos os riscos são 'médios', sem distinção." |
| **Anti-pattern** | Subestimar riscos para não assustar stakeholders. |
| **Métrica** | Percentual de riscos com análise de probabilidade/impacto. |
| **Critérios de Auditoria** | Revisar a matriz de riscos e a consistência das avaliações. |

---

### REGPM-003 – Plano de Mitigação e Contingência para Riscos Críticos e Altos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-003 |
| **Nome** | Plano de Mitigação e Contingência para Riscos Críticos e Altos |
| **Descrição** | Para cada risco classificado como **Crítico** ou **Alto**, o agente deve elaborar um plano de mitigação e um plano de contingência. O plano de mitigação deve incluir: **(1)** ações para reduzir a probabilidade e/ou o impacto; **(2)** responsável pela execução; **(3)** cronograma; **(4)** recursos necessários; **(5)** métricas de sucesso. O plano de contingência deve incluir: **(1)** ações a serem tomadas se o risco se materializar; **(2)** responsável; **(3)** gatilhos (ex: "se o atraso ultrapassar 10 dias"). |
| **Objetivo** | Garantir que riscos significativos sejam gerenciados proativamente, com planos claros de ação. |
| **Motivação** | Cap. 22.1.3 – o planejamento de riscos envolve estratégias de mitigação e contingência. |
| **Justificativa** | Riscos sem planos de ação tendem a se materializar e causar danos desnecessários. |
| **Critérios de Aplicação** | Riscos Críticos e Altos. |
| **Critérios de Não Aplicação** | Riscos Baixos (monitoramento apenas). |
| **Pré-condições** | Riscos priorizados (REGPM-002). |
| **Pós-condições** | Planos de mitigação e contingência aprovados. |
| **Restrições** | Os planos devem ser revisados e atualizados regularmente. |
| **Dependências** | REGPM-002. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "R-001 (perda de desenvolvedor sênior): mitigação – cross-training, documentação; contingência – contratação de consultor. Responsável: Gerente de Projetos." |
| **Exemplo Negativo** | "R-001: vamos torcer para que não aconteça." |
| **Anti-pattern** | Planos de mitigação vagos (ex: "monitorar o risco"). |
| **Métrica** | Percentual de riscos críticos/altos com plano de mitigação. |
| **Critérios de Auditoria** | Revisar se os planos de mitigação estão documentados e sendo executados. |

---

### REGPM-004 – Monitoramento Contínuo de Riscos com Indicadores (KRIs)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-004 |
| **Nome** | Monitoramento Contínuo de Riscos com Indicadores (KRIs) |
| **Descrição** | O agente deve garantir que os riscos sejam monitorados continuamente, utilizando Indicadores-Chave de Risco (Key Risk Indicators – KRIs). Para cada risco crítico ou alto, o agente deve definir pelo menos um KRI que possa ser medido objetivamente (ex: taxa de rotatividade da equipe, número de mudanças de requisitos, atraso em entregas). Os KRIs devem ter limites (thresholds) que, quando ultrapassados, disparam alertas e acionam os planos de contingência. |
| **Objetivo** | Detectar precocemente a materialização de riscos, permitindo ação corretiva antes que causem danos significativos. |
| **Motivação** | Cap. 22.1.4 – o monitoramento de riscos é uma atividade contínua. |
| **Justificativa** | Riscos não monitorados podem se materializar sem aviso, causando surpresas e danos. |
| **Critérios de Aplicação** | Riscos Críticos e Altos. |
| **Critérios de Não Aplicação** | Riscos Baixos (monitoramento simplificado). |
| **Pré-condições** | Riscos identificados e priorizados. |
| **Pós-condições** | KRIs definidos e sendo monitorados. |
| **Restrições** | Os KRIs devem ser revisados periodicamente para garantir que ainda são relevantes. |
| **Dependências** | REGPM-003. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-001 (perda de desenvolvedor): KRI = taxa de rotatividade > 15% ao ano. Se ultrapassar, acionar plano de contingência." |
| **Exemplo Negativo** | "Não temos indicadores; monitoramos riscos 'de ouvido'." |
| **Anti-pattern** | Definir KRIs que não podem ser medidos (ex: "moral da equipe"). |
| **Métrica** | Percentual de riscos com KRIs definidos. |
| **Critérios de Auditoria** | Verificar se há dashboards ou relatórios de monitoramento de riscos. |
