# Seção 5 – Regras de Gestão de Mudanças (Layer 7 - Governança, Alinhamento e Gestão de Mudanças)

**ID:** ARCH-RULESET-L7-GOV-CHANGE  
**Status:** Definitivo  
**Escopo:** Fluxo formal de solicitações de mudanças (Change Request - CR) e análise de impactos em dependências dinâmicas.

---

### REGGOV-006 – Processo Formal de Gestão de Mudanças (CR – Change Request)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-006 |
| **Nome** | Processo Formal de Gestão de Mudanças (CR – Change Request) |
| **Descrição** | O agente deve garantir que toda mudança arquitetural significativa siga um processo formal de Change Request (CR), composto pelas seguintes etapas: **(1)** Submissão (proponente descreve a mudança, justificativa e impacto estimado); **(2)** Triagem (avaliação de impacto preliminar); **(3)** Análise de Impacto detalhada (REGGOV-007); **(4)** Revisão e Aprovação (pelo Comitê de Arquitetura ou autoridade delegada); **(5)** Implementação (com plano de rollback); **(6)** Revisão Pós-Implementação (validação dos resultados esperados). O CR deve ser rastreado em um sistema de ticketing (ex: Jira) e cada etapa deve ter um responsável claro (RACI). |
| **Objetivo** | Garantir que mudanças sejam planejadas, avaliadas e implementadas de forma controlada, minimizando riscos. |
| **Motivação** | Cap. 1.3 (processo de arquitetura), Cap. 9.2.3 (ciclo de vida de sistemas). |
| **Justificativa** | Mudanças não planejadas são a principal causa de incidentes em produção e dívida técnica. |
| **Critérios de Aplicação** | Mudanças com impacto arquitetural (conforme REGARCH-SW-009) ou que afetem mais de um módulo. |
| **Critérios de Não Aplicação** | Mudanças internas a um módulo que não afetam interfaces públicas. |
| **Pré-condições** | Sistema de ticketing configurado. |
| **Pós-condições** | CR aprovado e implementado com documentação. |
| **Restrições** | Em emergências (ex: incidente de segurança), o CR pode ser aprovado em caráter de urgência, mas deve ser formalizado posteriormente. |
| **Dependências** | REGGOV-002, REGARCH-SW-009. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "CR #456: Migração de PostgreSQL para CockroachDB. Submetido, análise de impacto concluída, aprovado pelo Comitê, implementado com rollback. Revisão pós-implantação: performance melhorou 20%." |
| **Exemplo Negativo** | "Migramos para CockroachDB sem processo formal." |
| **Anti-pattern** | CRs abertos, mas nunca aprovados ou implementados, criando um backlog de "mudanças fantasmas". |
| **Métrica** | Tempo médio de aprovação de CRs (meta: < 5 dias). |
| **Critérios de Auditoria** | Revisar se toda mudança significativa tem um CR associado. |

---

### REGGOV-007 – Análise de Impacto Detalhada Obrigatória para CRs

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-007 |
| **Nome** | Análise de Impacto Detalhada Obrigatória para CRs |
| **Descrição** | Antes da aprovação de um CR, o agente deve garantir que uma Análise de Impacto detalhada seja realizada, abrangendo: **(1)** Componentes afetados (diretos e indiretos – REGARCH-SW-009); **(2)** Requisitos afetados (RN, PS, LGPD, RT); **(3)** Cronograma estimado; **(4)** Recursos necessários (pessoas, infraestrutura); **(5)** Riscos identificados (segurança, performance, conformidade); **(6)** Plano de rollback (como reverter a mudança). A análise deve ser revisada pelo Comitê de Arquitetura antes da aprovação. |
| **Objetivo** | Garantir que as consequências de uma mudança sejam totalmente compreendidas antes da implementação. |
| **Motivação** | Cap. 8.3.1 (análise de impacto estático), Cap. 9.4.2 (governança). |
| **Justificativa** | Mudanças sem análise de impacto são a principal causa de incidentes em produção. |
| **Critérios de Aplicação** | Todo CR (REGGOV-006). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Matriz de rastreabilidade atualizada (REGREQ-011). |
| **Pós-condições** | Análise de impacto aprovada e anexada ao CR. |
| **Restrições** | Se o impacto for classificado como "Alto", a aprovação deve ser do Comitê de Arquitetura. |
| **Dependências** | REGARCH-SW-009, REGREQ-011, REGGOV-006. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "CR #456: Análise de impacto: afeta 3 módulos (A, B, C), requisitos RN-042, RT-023. Risco: médio. Plano de rollback: reverter para versão anterior. Aprovado." |
| **Exemplo Negativo** | "CR #456 aprovado sem análise de impacto." |
| **Anti-pattern** | Análise de impacto superficial, sem considerar dependências indiretas. |
| **Métrica** | Percentual de CRs com análise de impacto documentada (meta: 100%). |
| **Critérios de Auditoria** | Revisar CRs: se não tiver análise de impacto, falha. |
