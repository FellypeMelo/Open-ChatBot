# Seção 3 – Regras de Padrões de Qualidade / Layer 4 (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-STD  
**Status:** Definitivo  
**Escopo:** Métodos e limites para métricas estáticas e ISO 25010.

---

### REGQUAL-001 – Aplicação da ISO/IEC 25010 para Requisitos de Qualidade

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-001 |
| **Nome** | Aplicação da ISO/IEC 25010 para Requisitos de Qualidade |
| **Descrição** | Todo requisito não-funcional (RT) relacionado à qualidade deve ser classificado em uma das oito características da ISO/IEC 25010: **adequação funcional, eficiência de desempenho, compatibilidade, usabilidade, confiabilidade, segurança, manutenibilidade, portabilidade**. O agente deve verificar se cada RT de qualidade está mapeado a pelo menos uma dessas características e, se necessário, desdobrar requisitos genéricos (ex: "deve ser seguro") em subcaracterísticas específicas (ex: "confidencialidade", "integridade", "disponibilidade"). |
| **Objetivo** | Garantir cobertura completa de todos os aspectos de qualidade, evitando lacunas (ex: focar apenas em performance e ignorar manutenibilidade). |
| **Motivação** | ISO/IEC 25010 (padrão internacional de qualidade) e Cap. 8.2.1 (diferentes visões de performance). |
| **Justificativa** | O modelo ISO 25010 é o padrão mais consolidado para qualidade de software. Usá-lo como referência garante que nenhum aspecto seja esquecido. |
| **Critérios de Aplicação** | Todo RT de qualidade e toda revisão de arquitetura. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | RT de qualidade definido. |
| **Pós-condições** | O RT está classificado com uma ou mais características ISO 25010. |
| **Restrições** | Um RT pode mapear para múltiplas características, mas todas devem ser documentadas. |
| **Dependências** | REGREQ-004, REGREQ-005. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RT-023 (performance): classificação = Eficiência de Desempenho (subcaracterísticas: tempo de resposta, throughput, utilização de recursos)." |
| **Exemplo Negativo** | "RT-023: de ser rápido." (sem classificação ISO). |
| **Anti-pattern** | Classificar tudo como "Confiabilidade" sem diferenciar os subaspectos. |
| **Métrica** | Percentual de RTs com classificação ISO 25010. |
| **Critérios de Auditoria** | Revisar todos os RTs: se algum não tiver classificação, falha. |

---

### REGQUAL-002 – Definição de Métricas de Manutenibilidade

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-002 |
| **Nome** | Definição de Métricas de Manutenibilidade (Índice de Manutenibilidade, Complexidade, Duplicação) |
| **Descrição** | O agente deve exigir que todo projeto defina métricas objetivas de manutenibilidade, incluindo, no mínimo: **(1)** Índice de Manutenibilidade (target: > 70 para novas implementações); **(2)** Complexidade Ciclomática máxima por método (target: < 10); **(3)** Percentual de duplicação de código (target: < 5%). Essas métricas devem ser verificadas automaticamente no pipeline de CI (análise estática) e, se violadas, devem bloquear o merge (quality gate). |
| **Objetivo** | Garantir que o código permaneça legível, testável e modificável ao longo do tempo. |
| **Motivação** | Cap. 6.1 (conceptual integrity, parsimony) e Cap. 6.3.4 (estruturação). |
| **Justificativa** | Código com alta complexidade e duplicação é caro de manter e propenso a defeitos. |
| **Critérios de Aplicação** | Todo código-fonte novo ou modificado. |
| **Critérios de Não Aplicação** | Código legado pode ter métricas diferentes, mas deve ter um plano de redução documentado. |
| **Pré-condições** | Ferramentas de análise estática configuradas (ex: SonarQube). |
| **Pós-condições** | As métricas são verificadas e os limites são respeitados. |
| **Restrições** | Se um limite for violado, a violação deve ser justificada e aprovada por um arquiteto. |
| **Dependências** | REGQUAL-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "SonarQube: maintainability index = 82, cyclomatic complexity = 6, duplication = 2%. Passou no quality gate." |
| **Exemplo Negativo** | "Código com maintainability index = 45, complexity = 18, duplication = 15% – merge aprovado sem justificativa." |
| **Anti-pattern** | Ignorar métricas de manutenibilidade, priorizando apenas velocidade de entrega. |
| **Métrica** | Média do índice de manutenibilidade do código-base (meta: > 70). |
| **Critérios de Auditoria** | Revisar relatórios de análise estática para verificar violações não justificadas. |
