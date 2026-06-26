# Seção 4 – Regras de Revisão Técnica / Layer 4 (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-REVIEW  
**Status:** Definitivo  
**Escopo:** Processos de revisão de arquitetura, fluxos de Pull Request e listas de checagem.

---

### REGQUAL-003 – Revisão Obrigatória de Arquitetura para Mudanças Estruturais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-003 |
| **Nome** | Revisão Obrigatória de Arquitetura para Mudanças Estruturais |
| **Descrição** | Qualquer mudança estrutural (ex: criação de novo módulo, alteração de interface pública, mudança de tecnologia, migração de banco, mudança de padrão de integração) deve passar por uma Revisão de Arquitetura formal, conduzida por um arquiteto que não participou da proposta. A revisão deve verificar: (1) conformidade com princípios arquiteturais (SOLID, Clean, DDD, orientação a serviços); (2) alinhamento com requisitos não-funcionais (RTs); (3) análise de impacto (REGARCH-SW-009); (4) segurança e compliance (PS/LGPD). |
| **Objetivo** | Garantir que a integridade conceitual da arquitetura seja preservada e que mudanças sejam avaliadas por um olhar independente. |
| **Motivação** | Cap. 7.4.5 (validação independente), Cap. 6.1 (conceptual integrity – Brooks), Cap. 8.3.1 (análise de impacto). |
| **Justificativa** | O autor da proposta tem vieses e pode não ver todas as implicações. Uma revisão independente reduz o risco de decisões equivocadas. |
| **Critérios de Aplicação** | Toda mudança com impacto arquitetural (conforme definido pela matriz de rastreabilidade). |
| **Critérios de Não Aplicação** | Mudanças internas a um módulo que não afetam interfaces públicas ou outras dependências. |
| **Pré-condições** | Proposta de mudança documentada com rationale (REGCON-009). |
| **Pós-condições** | Aprovação ou rejeição da mudança registrada com ata da reunião. |
| **Restrições** | A revisão deve ser síncrona (workshop) e não assíncrona (e-mail), conforme REGREQ-009. |
| **Dependências** | REGARCH-SW-009, REGCON-009. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Proposta de migrar de PostgreSQL para CockroachDB. Revisão de arquitetura: avaliou impacto, custo, performance e conformidade. Aprovada com ressalvas (plano de rollback)." |
| **Exemplo Negativo** | "Decidimos migrar para CockroachDB porque parece mais escalável." (sem revisão). |
| **Anti-pattern** | Realizar a revisão após a implementação (ex: "vamos fazer e depois revisamos"). |
| **Métrica** | Percentual de mudanças estruturais com revisão de arquitetura (meta: 100%). |
| **Critérios de Auditoria** | Revisar histórico de mudanças: se alguma não tiver revisão registrada, falha. |

---

### REGQUAL-004 – Revisão de Código Obrigatória (Pull Request com Aprovação Mínima)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-004 |
| **Nome** | Revisão de Código Obrigatória (Pull Request com Aprovação Mínima) |
| **Descrição** | Nenhuma alteração de código pode ser mesclada (merge) à branch principal sem passar por uma revisão de código formal (Pull Request). A PR deve ser aprovada por, no mínimo, **um revisor** que não seja o autor. O revisor deve verificar: (1) aderência a padrões de codificação; (2) clareza e legibilidade; (3) cobertura de testes adequada; (4) ausência de code smells; (5) segurança (ex: injeção de SQL, XSS); (6) conformidade com a arquitetura; (7) documentação atualizada. |
| **Objetivo** | Garantir que o código seja revisado por um par, detectando defeitos precocemente e disseminando conhecimento. |
| **Motivação** | Cap. 6.4 (legibilidade) e Cap. 10 (integração via CI). |
| **Justificativa** | Revisão de código é a prática mais eficaz para detectar defeitos e melhorar a qualidade do código, além de compartilhar conhecimento entre a equipe. |
| **Critérios de Aplicação** | Toda alteração de código, exceto emergências críticas (incidentes em produção) com justificativa documentada. |
| **Critérios de Não Aplicação** | Documentação, configurações (ex: YAML) podem ser revisadas de forma mais leve, mas ainda devem ser revisadas. |
| **Pré-condições** | Código submetido em PR, com CI passando. |
| **Pós-condições** | PR aprovado por revisor e mesclado. |
| **Restrições** | O revisor não pode ser o autor. O autor pode sugerir revisores, mas a aprovação final é do revisor designado. |
| **Dependências** | REGQUAL-002 (métricas verificadas no CI). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "PR #123: adiciona serviço de classificação. Aprovado por João (revisor). CI passou, cobertura 92%." |
| **Exemplo Negativo** | "Merge direto para master sem PR." |
| **Anti-pattern** | Aprovar PRs sem realmente revisar o código ("LGTM" sem análise). |
| **Métrica** | Percentual de PRs com revisão aprovada (meta: 100%). |
| **Critérios de Auditoria** | Revisar histórico de merges: se algum merge não tiver PR, falha. |

---

### REGQUAL-005 – Checklist de Revisão de Código Obrigatório

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-005 |
| **Nome** | Checklist de Revisão de Código Obrigatório |
| **Descrição** | O agente deve disponibilizar e exigir a aplicação de um checklist padronizado para revisão de código, contendo, no mínimo: **(1)** O código é legível e segue as convenções de nomenclatura? **(2)** Os testes unitários cobrem as novas funcionalidades e os casos de erro? **(3)** Há tratamento adequado de exceções e casos limite? **(4)** O código evita duplicação? **(5)** As dependências são injetadas (não são 'new' diretamente)? **(6)** A segurança básica (validação de entrada, escape de saída) é respeitada? **(7)** A documentação (ex: JavaDoc, README) foi atualizada? **(8)** O CI passou (incluindo análise estática)? |
| **Objetivo** | Padronizar o processo de revisão e garantir que nenhum aspecto crítico seja esquecido. |
| **Motivação** | Cap. 6.3.5 (breakdowns) e Cap. 7.4.4 (criação de visões com checklist). |
| **Justificativa** | Revisores, sem um checklist, tendem a focar em aspectos que lhes são familiares (ex: lógica) e ignorar outros (ex: segurança, tratamento de erros). |
| **Critérios de Aplicação** | Toda PR. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Checklist disponível no repositório. |
| **Pós-condições** | O revisor preencheu o checklist e anexou à PR. |
| **Restrições** | O checklist pode ser automatizado parcialmente (ex: ferramentas de linting), mas a validação final é humana. |
| **Dependências** | REGQUAL-004. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Checklist da PR #123: todos os itens verificados. OK." |
| **Exemplo Negativo** | "PR aprovada sem checklist." |
| **Anti-pattern** | Marcar todos os itens como "OK" sem realmente verificar. |
| **Métrica** | Percentual de PRs com checklist preenchido. |
| **Critérios de Auditoria** | Revisar PRs para verificar presença e qualidade do checklist. |
