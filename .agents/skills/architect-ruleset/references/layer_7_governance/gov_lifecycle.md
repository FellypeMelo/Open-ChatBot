# Seção 6 – Regras de Ciclo de Vida de Artefatos (Layer 7 - Governança, Alinhamento e Gestão de Mudanças)

**ID:** ARCH-RULESET-L7-GOV-LIFECYCLE  
**Status:** Definitivo  
**Escopo:** Controle de estados de maturidade de documentos e políticas de expiração/depreciação de especificações legadas.

---

### REGGOV-008 – Ciclo de Vida de Artefatos (Rascunho → Em Revisão → Aprovado → Arquivado)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-008 |
| **Nome** | Ciclo de Vida de Artefatos (Rascunho → Em Revisão → Aprovado → Arquivado) |
| **Descrição** | O agente deve garantir que todo artefato de arquitetura (requisito, ADR, documento ARC42, especificação de API) siga um ciclo de vida formal com estados: **(1) Rascunho**: em criação, ainda não revisado; **(2) Em Revisão**: submetido para revisão (por pares ou Comitê); **(3) Aprovado**: revisado e aprovado, pronto para uso; **(4) Arquivado** (ou Depreciado): substituído por uma versão mais recente ou não mais aplicável. Nenhum artefato em estado "Rascunho" ou "Em Revisão" pode ser utilizado como base para decisões de implementação. |
| **Objetivo** | Garantir que apenas artefatos aprovados sejam utilizados, evitando que documentação não validada seja usada como referência. |
| **Motivação** | Cap. 1.3 (ciclo de vida da descrição arquitetural). |
| **Justificativa** | Artefatos não aprovados podem conter erros ou informações desatualizadas, gerando decisões equivocadas. |
| **Critérios de Aplicação** | Requisitos (RN, PS, LGPD, RT), ADRs, documentos ARC42, especificações de API. |
| **Critérios de Não Aplicação** | Rascunhos pessoais ou anotações de reunião. |
| **Pré-condições** | Sistema de versionamento com metadados de status. |
| **Pós-condições** | Cada artefato tem um status claramente definido. |
| **Restrições** | A transição de "Em Revisão" para "Aprovado" exige aprovação formal (ex: Comitê, revisor designado). |
| **Dependências** | REGDOC-002 (ADRs), REGREQ-004 (requisitos). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "ADR-012: status = Aprovado (desde 10/01/2025). RN-042: status = Aprovado." |
| **Exemplo Negativo** | "Documentos de arquitetura sem status, misturando rascunhos e versões aprovadas." |
| **Anti-pattern** | Manter artefatos no estado "Rascunho" indefinidamente, sem nunca serem revisados. |
| **Métrica** | Percentual de artefatos com status definido (meta: 100%). |
| **Critérios de Auditoria** | Revisar cada artefato: se não tiver status, falha. |

---

### REGGOV-009 – Depreciação e Arquivamento de Artefatos (Sunset Policy)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-009 |
| **Nome** | Depreciação e Arquivamento de Artefatos (Sunset Policy) |
| **Descrição** | O agente deve garantir que artefatos obsoletos sejam formalmente depreciados e arquivados, e não apenas "esquecidos". O processo de depreciação deve incluir: **(1)** Notificação aos stakeholders (com prazo de transição); **(2)** Atualização de referências (ex: links para o novo artefato); **(3)** Arquivamento em um repositório de histórico; **(4)** Data de expiração (após a qual o artefato não pode mais ser usado). Artefatos arquivados não podem ser utilizados como base para novas decisões. |
| **Objetivo** | Evitar a confusão causada por múltiplas versões de artefatos e garantir que apenas artefatos atuais sejam utilizados. |
| **Motivação** | Cap. 1.3 (evolução da arquitetura) e Cap. 9.2.3 (ciclo de vida). |
| **Justificativa** | Artefatos obsoletos mantidos "por precaução" geram ambiguidade e decisões equivocadas. |
| **Critérios de Aplicação** | Artefatos substituídos por versões mais recentes ou que não são mais aplicáveis. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Artefato obsoleto identificado. |
| **Pós-condições** | Artefato depreciado e arquivado. |
| **Restrições** | O período de transição deve ser de no mínimo 30 dias para que os stakeholders possam se adaptar. |
| **Dependências** | REGGOV-008. |
| **Prioridade** | **Média** |
| **Severidade** | **Alerta** |
| **Exemplo Positivo** | "RN-042 (v1.0) depreciada em 01/12/2024, substituída por RN-042 (v2.0). Prazo de transição: 30 dias. Arquivada em 01/01/2025." |
| **Exemplo Negativo** | "Várias versões da mesma RN coexistindo sem indicação de qual é a atual." |
| **Anti-pattern** | Manter artefatos arquivados acessíveis para consulta, mas sem indicação clara de que estão obsoletos. |
| **Métrica** | Percentual de artefatos obsoletos com plano de depreciação. |
| **Critérios de Auditoria** | Revisar se há artefatos obsoletos sem depreciação formal. |
