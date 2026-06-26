# Seção 6 – Regras de Revisão e Inspeção de Código (Layer 12 - TEST-REVIEW)

---

### REGTEST-008 – Revisão de Código Obrigatória (Pull Request com Aprovação Mínima)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-008 |
| **Nome** | Revisão de Código Obrigatória (Pull Request com Aprovação Mínima) |
| **Descrição** | Nenhuma alteração de código pode ser mesclada (merge) à branch principal sem passar por uma revisão de código formal (Pull Request). A PR deve ser aprovada por, no mínimo, **um revisor** que não seja o autor. O revisor deve verificar: (1) aderência a padrões de codificação; (2) clareza e legibilidade; (3) cobertura de testes adequada; (4) ausência de code smells; (5) segurança (ex: injeção de SQL, XSS); (6) conformidade com a arquitetura; (7) documentação atualizada. O agente deve garantir que a revisão seja realizada de forma construtiva, focando no código e não na pessoa. |
| **Objetivo** | Garantir que o código seja revisado por um par, detectando defeitos precocemente e disseminando conhecimento. |
| **Motivação** | Cap. 24.3 – revisões são uma técnica eficaz de detecção de defeitos. |
| **Justificativa** | Revisão de código é a prática mais eficaz para detectar defeitos e melhorar a qualidade do código. |
| **Critérios de Aplicação** | Toda alteração de código, exceto emergências críticas (incidentes em produção) com justificativa documentada. |
| **Critérios de Não Aplicação** | Documentação, configurações (ex: YAML) podem ser revisadas de forma mais leve, mas ainda devem ser revisadas. |
| **Pré-condições** | Código submetido em PR, com CI passando. |
| **Pós-condições** | PR aprovado por revisor e mesclado. |
| **Restrições** | O revisor não pode ser o autor. O autor pode sugerir revisores, mas a aprovação final é do revisor designado. |
| **Dependências** | REGTEST-001 (cobertura), REGQUAL-010 (quality gates). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "PR #123: adiciona serviço de classificação. Aprovado por João (revisor). CI passou, cobertura 92%." |
| **Exemplo Negativo** | "Merge direto para master sem PR." |
| **Anti-pattern** | Aprovar PRs sem realmente revisar o código ("LGTM" sem análise). |
| **Métrica** | Percentual de PRs com revisão aprovada (meta: 100%). |
| **Critérios de Auditoria** | Revisar histórico de merges: se algum merge não tiver PR, falha. |

---

### REGTEST-009 – Checklist de Revisão de Código Obrigatório

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-009 |
| **Nome** | Checklist de Revisão de Código Obrigatório |
| **Descrição** | O agente deve disponibilizar e exigir a aplicação de um checklist padronizado para revisão de código, contendo, no mínimo: **(1)** O código é legível e segue as convenções de nomenclatura? **(2)** Os testes unitários cobrem as novas funcionalidades e os casos de erro? **(3)** Há tratamento adequado de exceções e casos limite? **(4)** O código evita duplicação? **(5)** As dependências são injetadas (não são 'new' diretamente)? **(6)** A segurança básica (validação de entrada, escape de saída) é respeitada? **(7)** A documentação (ex: JavaDoc, README) foi atualizada? **(8)** O CI passou (incluindo análise estática)? |
| **Objetivo** | Padronizar o processo de revisão e garantir que nenhum aspecto crítico seja esquecido. |
| **Motivação** | Cap. 24.3.2 – checklists de inspeção aumentam a eficácia da revisão. |
| **Justificativa** | Revisores sem checklist tendem a focar em aspectos familiares e ignorar outros (ex: segurança, tratamento de erros). |
| **Critérios de Aplicação** | Toda PR. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Checklist disponível no repositório. |
| **Pós-condições** | O revisor preencheu o checklist e anexou à PR. |
| **Restrições** | O checklist pode ser automatizado parcialmente (ex: ferramentas de linting), mas a validação final é humana. |
| **Dependências** | REGTEST-008. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Checklist da PR #123: todos os itens verificados. OK." |
| **Exemplo Negativo** | "PR aprovada sem checklist." |
| **Anti-pattern** | Marcar todos os itens como "OK" sem realmente verificar. |
| **Métrica** | Percentual de PRs com checklist preenchido. |
| **Critérios de Auditoria** | Revisar PRs para verificar presença e qualidade do checklist. |
