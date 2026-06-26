# Seção 6 – Regras de Gestão de Configuração (Layer 13 - EVOL-CM)

---

### REGEVOL-006 – Processo Formal de Gestão de Mudanças (Change Management)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-006 |
| **Nome** | Processo Formal de Gestão de Mudanças (Change Management) |
| **Descrição** | O agente deve garantir que toda mudança em um sistema em produção ou em desenvolvimento siga um processo formal de Change Management, composto por: **(1)** Submissão de Change Request (CR) com descrição, justificativa e impacto estimado; **(2)** Análise de Impacto (técnica e de negócio); **(3)** Avaliação e priorização (REGEVOL-002); **(4)** Aprovação pelo Change Control Board (CCB) ou autoridade delegada; **(5)** Implementação (desenvolvimento, testes, revisão); **(6)** Verificação pós-implementação; **(7)** Fechamento e documentação. O agente deve garantir que o processo seja rastreável e que cada CR tenha um identificador único. |
| **Objetivo** | Garantir que mudanças sejam controladas, avaliadas e implementadas de forma previsível e auditável. |
| **Motivação** | Cap. 25.1 – o processo de gestão de mudanças é essencial para controlar a evolução do sistema. |
| **Justificativa** | Mudanças não controladas são a principal causa de falhas em produção e degradação da qualidade. |
| **Critérios de Aplicação** | Toda mudança em sistemas em produção ou em versões estabilizadas. |
| **Critérios de Não Aplicação** | Mudanças em desenvolvimento inicial (pré-alpha) podem ter processo simplificado. |
| **Pré-condições** | Ferramenta de rastreamento de CRs configurada (ex: Jira, ServiceNow). |
| **Pós-condições** | CR aprovado e implementado com documentação. |
| **Restrições** | Em emergências (ex: incidente de segurança), o CR pode ser aprovado em caráter de urgência, mas deve ser formalizado posteriormente. |
| **Dependências** | REGEVOL-002 (priorização), REGGOV-006 (governança). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "CR-045: migração para Java 17. Análise de impacto concluída, aprovada pelo CCB, implementada em 3 sprints." |
| **Exemplo Negativo** | "Migramos para Java 17 sem processo formal." |
| **Anti-pattern** | CRs abertos, mas nunca aprovados ou implementados. |
| **Métrica** | Tempo médio de aprovação de CRs (meta: < 5 dias). |
| **Critérios de Auditoria** | Revisar se toda mudança significativa tem um CR associado. |

---

### REGEVOL-007 – Versionamento com Git e Estratégia de Branching

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-007 |
| **Nome** | Versionamento com Git e Estratégia de Branching |
| **Descrição** | O agente deve garantir que o sistema utilize um sistema de versionamento (preferencialmente Git) com uma estratégia de branching definida. A estratégia deve incluir, no mínimo: **(1)** Branch `main` (ou `master`) para código em produção; **(2)** Branch `develop` para integração de funcionalidades; **(3)** Branches de feature para cada nova funcionalidade (`feature/nome`); **(4)** Branches de hotfix para correções urgentes em produção (`hotfix/nome`); **(5)** Branches de release para preparação de novas versões (`release/vX.Y.Z`). O agente deve garantir que todas as alterações passem por PRs e revisões (REGTEST-008) antes de serem mescladas. |
| **Objetivo** | Garantir rastreabilidade, isolamento e controle de qualidade no desenvolvimento. |
| **Motivação** | Cap. 25.2 – versionamento é fundamental para gerenciar codelines e baselines. |
| **Justificativa** | Uma estratégia de branching bem definida evita conflitos, facilita releases e permite correções rápidas. |
| **Critérios de Aplicação** | Todo projeto com mais de 1 desenvolvedor ou com mais de 1 ambiente (dev, staging, produção). |
| **Critérios de Não Aplicação** | Projetos de um único desenvolvedor com fluxo simples (podem usar `main` diretamente). |
| **Pré-condições** | Repositório Git configurado. |
| **Pós-condições** | Estratégia de branching documentada e seguida. |
| **Restrições** | `main` deve estar sempre em estado deployável (todos os testes passando). |
| **Dependências** | REGTEST-008 (PRs e revisões), REGEVOL-006 (Change Management). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Estratégia GitFlow: `main` → `develop` → `feature/checkout` → PR → merge para `develop` → release `v1.2.0`." |
| **Exemplo Negativo** | "Todos committam diretamente em `main`." |
| **Anti-pattern** | Branches longos que nunca são mesclados, gerando conflitos enormes. |
| **Métrica** | Número de conflitos de merge por mês (meta: < 5). |
| **Critérios de Auditoria** | Revisar a estratégia de branching e o histórico de merges. |

---

### REGEVOL-008 – Build Automatizado e Integração Contínua (CI)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-008 |
| **Nome** | Build Automatizado e Integração Contínua (CI) |
| **Descrição** | O agente deve garantir que o sistema utilize um pipeline de build automatizado e integração contínua (CI), que deve: **(1)** ser acionado a cada commit; **(2)** compilar o código; **(3)** executar testes unitários, de integração e de regressão; **(4)** executar análise estática; **(5)** gerar relatórios de cobertura e qualidade; **(6)** notificar a equipe em caso de falhas. O agente deve garantir que o pipeline de CI seja parte obrigatória do processo de desenvolvimento e que nenhum código seja mesclado sem que o CI passe com sucesso. |
| **Objetivo** | Detectar defeitos precocemente, garantir a qualidade do código e automatizar tarefas repetitivas. |
| **Motivação** | Cap. 25.3 – a construção automatizada é essencial para sistemas complexos. |
| **Justificativa** | Builds manuais são propensos a erros e consomem tempo; CI automatiza e acelera o feedback. |
| **Critérios de Aplicação** | Todo projeto com mais de 1 desenvolvedor. |
| **Critérios de Não Aplicação** | Projetos de um único desenvolvedor com build manual (desaconselhável). |
| **Pré-condições** | Ferramenta de CI configurada (ex: GitHub Actions, Jenkins, GitLab CI). |
| **Pós-condições** | Pipeline de CI em execução e aprovado para cada PR. |
| **Restrições** | O pipeline não pode levar mais de 15 minutos para ser executado; se ultrapassar, deve ser otimizado ou paralelizado. |
| **Dependências** | REGTEST-001 (cobertura), REGEVOL-007 (versionamento). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Pipeline CI: build → testes unitários (92% cobertura) → testes integração → análise estática → relatório. Todos passaram." |
| **Exemplo Negativo** | "Fazemos build manual antes de cada release." |
| **Anti-pattern** | Pipeline de CI com muitos testes que demoram > 30 minutos, desmotivando a equipe a usá-lo. |
| **Métrica** | Percentual de commits que passam no CI na primeira tentativa (meta: > 90%). |
| **Critérios de Auditoria** | Verificar se o pipeline de CI está configurado e sendo usado. |

---

### REGEVOL-009 – Gestão de Releases com Versionamento Semântico

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-009 |
| **Nome** | Gestão de Releases com Versionamento Semântico |
| **Descrição** | O agente deve garantir que as releases sejam gerenciadas com versionamento semântico (SemVer): **(1)** MAJOR: mudanças incompatíveis na API; **(2)** MINOR: adição de funcionalidades compatíveis com versões anteriores; **(3)** PATCH: correções de bugs compatíveis com versões anteriores. O agente deve documentar cada release, incluindo: **(1)** número da versão; **(2)** data; **(3)** mudanças incluídas; **(4)** notas de release. O processo de release deve incluir: (1) branch de release; (2) validação final (testes de regressão, performance); (3) tag no repositório; (4) deploy para produção. |
| **Objetivo** | Garantir que as releases sejam previsíveis, rastreáveis e comunicadas adequadamente. |
| **Motivação** | Cap. 25.4 – o gerenciamento de releases é parte essencial da gestão de configuração. |
| **Justificativa** | Versionamento semântico facilita a comunicação de mudanças e a gestão de dependências. |
| **Critérios de Aplicação** | Todo projeto com múltiplas versões e dependências externas. |
| **Critérios de Não Aplicação** | Projetos com uma única versão (ex: scripts internos). |
| **Pré-condições** | Código em estado deployável. |
| **Pós-condições** | Release criada, tag aplicada e notas de release publicadas. |
| **Restrições** | A versão MAJOR não deve ser incrementada sem aviso prévio aos consumidores (depreciação). |
| **Dependências** | REGEVOL-008 (CI), REGEVOL-007 (versionamento). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Release v2.1.0: novas funcionalidades de relatórios (MINOR). Notas de release detalhadas." |
| **Exemplo Negativo** | "Versões sem sentido (v1, v2, v3) sem indicar compatibilidade." |
| **Anti-pattern** | Fazer breaking changes sem incrementar MAJOR. |
| **Métrica** | Percentual de releases com notas de release (meta: 100%). |
| **Critérios de Auditoria** | Revisar tags e notas de release. |
