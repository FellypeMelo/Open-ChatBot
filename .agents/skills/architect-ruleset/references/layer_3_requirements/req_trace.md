# Seção 6 – Regras de Rastreabilidade e Matrizes / Layer 3 (Layer 3 - Requisitos)

**ID:** ARCH-RULESET-L3-REQ-TRACE  
**Status:** Definitivo  
**Escopo:** Métodos e regras para manutenção da Matriz de Rastreabilidade bidirecional acíclica.

---

### REGREQ-011 – Matriz de Rastreabilidade Universal e Bidirecional

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-011 |
| **Nome** | Matriz de Rastreabilidade Universal e Bidirecional |
| **Descrição** | O agente deve manter e consultar uma Matriz de Rastreabilidade Universal que mapeie, no mínimo: **(1) Requisito (RN/PS/LGPD/RT) → Requisitos Derivados**; **(2) Requisito → RF (Requisito Funcional)** que o implementa; **(3) Requisito → Componente/Serviço** que o realiza; **(4) Requisito → Caso de Teste** que o valida; **(5) Requisito → Artefato Físico** (banco, fila, arquivo). A matriz deve ser bidirecional, permitindo navegar tanto "para frente" (origem → realização) quanto "para trás" (realização → origem). |
| **Objetivo** | Garantir que a arquitetura seja completamente rastreável, permitindo análise de impacto precisa e auditoria de conformidade. |
| **Motivação** | Cap. 8.3.1 (análise de impacto estático), Cap. 9.2.2 (três mundos). |
| **Justificativa** | Sem rastreabilidade, mudanças em um requisito são imprevisíveis, e a conformidade regulatória (LGPD) é impossível de comprovar. |
| **Critérios de Aplicação** | Todo o ciclo de vida do requisito. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisitos e elementos de realização identificados. |
| **Pós-condições** | A matriz é atualizada a cada mudança. |
| **Restrições** | A matriz deve ser mantida em um repositório acessível a todos os stakeholders. |
| **Dependências** | REGREQ-004, REGCORE-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Matriz: RN-042 → RF-101 (serviço de classificação) → Componente 'VariantClassifier' → Teste TC-042 → Artefato 'classifier.jar' no S3." |
| **Exemplo Negativo** | Nenhuma matriz documentada. |
| **Anti-pattern** | Manter a matriz em um diagrama desatualizado, sem versionamento. |
| **Métrica** | Percentual de requisitos com rastreabilidade completa (meta: 100%). |
| **Critérios de Auditoria** | Auditoria da matriz: cada requisito deve ter pelo menos um link em cada direção. |

---

### REGREQ-012 – Proibição de Rastreabilidade Circular

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-012 |
| **Nome** | Proibição de Rastreabilidade Circular |
| **Descrição** | O agente não pode criar ou manter uma relação de rastreabilidade onde A depende de B, B depende de C, e C depende de A (ciclo). Ciclos de rastreabilidade devem ser quebrados identificando uma origem externa ou uma relação de nível superior. |
| **Objetivo** | Garantir que a matriz de rastreabilidade seja acíclica e que exista sempre uma "âncora" (origem final). |
| **Motivação** | Cap. 3.3.2 (assinatura não pode ter ciclos) e Cap. 8.3.1 (análise de impacto não funciona com ciclos). |
| **Justificativa** | Ciclos de rastreabilidade impossibilitam a análise de impacto (qual é a origem?). |
| **Critérios de Aplicação** | Na criação ou atualização de relações de rastreabilidade. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Relação de rastreabilidade a ser criada. |
| **Pós-condições** | O grafo de rastreabilidade permanece acíclico. |
| **Restrições** | Se um ciclo for detectado, o agente deve quebrá-lo removendo a relação mais fraca ou adicionando um elemento externo. |
| **Dependências** | REGREQ-011. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RN-042 depende de RT-023. RT-023 depende de PS-012. PS-012 depende de LGPD-005. LGPD-005 depende da norma LGPD (origem externa). Ciclo quebrado." |
| **Exemplo Negativo** | "RN-042 depende de RT-023; RT-023 depende de RN-042." |
| **Anti-pattern** | Aceitar ciclos na matriz "porque são necessários" sem justificativa. |
| **Métrica** | Número de ciclos detectados e quebrados. |
| **Critérios de Auditoria** | Análise estática do grafo de rastreabilidade para detectar ciclos. |
