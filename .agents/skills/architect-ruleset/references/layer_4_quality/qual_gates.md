# Seção 6 – Regras de Quality Gates e Pipeline / Layer 4 (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-GATES  
**Status:** Definitivo  
**Escopo:** Definição de bloqueios automáticos no pipeline CI/CD e rastreamento de defeitos.

---

### REGQUAL-010 – Quality Gates Obrigatórios no Pipeline de CI/CD

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-010 |
| **Nome** | Quality Gates Obrigatórios no Pipeline de CI/CD |
| **Descrição** | O pipeline de CI/CD deve ter, no mínimo, os seguintes quality gates obrigatórios, que bloqueiam a progressão se não forem atendidos: **(1)** Análise estática sem violações críticas (vulnerabilidades, code smells), **(2)** Cobertura de testes unitários ≥ 80% (REGQUAL-006), **(3)** Testes de integração passando (REGQUAL-007), **(4)** Testes de contrato passando (REGQUAL-008), **(5)** Testes de performance dentro dos limites (REGQUAL-009), **(6)** Revisão de código aprovada (REGQUAL-004). |
| **Objetivo** | Automatizar a verificação de qualidade, garantindo que critérios objetivos sejam atendidos antes de qualquer deploy. |
| **Motivação** | Cap. 10 (integração de ferramentas e automação). |
| **Justificativa** | Gates manuais são ignorados ou aplicados de forma inconsistente. Gates automatizados garantem disciplina. |
| **Critérios de Aplicação** | Todo pipeline de CI/CD. |
| **Critérios de Não Aplicação** | Projetos em fase inicial (protótipos) podem ter gates flexíveis, mas devem evoluir para o padrão. |
| **Pré-condições** | Pipeline configurado com todos os gates. |
| **Pós-condições** | Deploy só ocorre se todos os gates passarem. |
| **Restrições** | Exceções (ex: hotfix de emergência) requerem aprovação de dois arquitetos. |
| **Dependências** | REGQUAL-004, REGQUAL-006, REGQUAL-007, REGQUAL-008, REGQUAL-009. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Pipeline: lint ✅, testes unitários 92% ✅, testes integração ✅, contrato ✅, performance ✅, PR aprovado ✅ → Deploy." |
| **Exemplo Negativo** | "Pipeline aprovou mesmo com cobertura de 40% e PR sem revisão." |
| **Anti-pattern** | Ter gates, mas permitir bypass sem auditoria. |
| **Métrica** | Percentual de deployments que passaram por todos os gates. |
| **Critérios de Auditoria** | Revisar logs do pipeline para identificar bypass de gates. |

---

### REGQUAL-011 – Registro e Rastreabilidade de Defeitos (Bug Tracking)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-011 |
| **Nome** | Registro e Rastreabilidade de Defeitos (Bug Tracking) |
| **Descrição** | Todo defeito identificado (em revisão, testes, produção) deve ser registrado em um sistema de rastreamento de defeitos (ex: Jira, GitHub Issues), com: **(1)** descrição clara, **(2)** passos para reproduzir, **(3)** gravidade (crítico, alto, médio, baixo), **(4)** prioridade, **(5)** versão afetada, **(6)** link para o requisito violado (RN/PS/LGPD/RT), **(7)** link para o commit/PR que corrigiu. A rastreabilidade de defeitos é obrigatória para auditoria de qualidade e análise de tendências. |
| **Objetivo** | Garantir que defeitos sejam gerenciados, priorizados e rastreados até sua resolução. |
| **Motivação** | Cap. 8.3.1 (rastreabilidade de defeitos) e Cap. 6.3.5 (breakdowns). |
| **Justificativa** | Defeitos não registrados são esquecidos. Defeitos sem rastreabilidade não podem ser auditados. |
| **Critérios de Aplicação** | Todo defeito, de qualquer fonte. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Emissor de tickets / ferramenta de gestão configurada. |
| **Pós-condições** | Defeito registrado com todos os campos obrigatórios. |
| **Restrições** | Defeitos críticos devem ser resolvidos antes de qualquer nova release. |
| **Dependências** | REGREQ-011 (rastreabilidade). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Issue #456: Variante classe 5 não está sendo classificada. Gravidade: crítica. Prioridade: alta. Link para RN-042. Corrigido no PR #789." |
| **Exemplo Negativo** | "O sistema está com um bug, mas ninguém abriu issue." |
| **Anti-pattern** | Abrir issues sem informações mínimas (ex: "está quebrado"). |
| **Métrica** | Número de defeitos resolvidos vs. abertos. |
| **Critérios de Auditoria** | Revisar o backlog de defeitos e verificar se todos têm campos obrigatórios. |
