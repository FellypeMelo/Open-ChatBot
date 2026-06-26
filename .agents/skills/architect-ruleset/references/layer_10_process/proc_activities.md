# Seção 4 – Regras de Atividades Fundamentais (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-ACTIVITIES  
**Status:** Definitivo  
**Escopo:** Diretrizes para cobertura e planejamento das quatro atividades de engenharia de software.

---

### REGPROC-004 – Garantia de Cobertura das Quatro Atividades Fundamentais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-004 |
| **Nome** | Garantia de Cobertura das Quatro Atividades Fundamentais |
| **Descrição** | Independentemente do modelo de processo adotado, o agente deve garantir que as quatro atividades fundamentais estejam presentes e devidamente planejadas: **(1) Especificação** (o que o sistema deve fazer); **(2) Projeto e Implementação** (como o sistema será construído); **(3) Validação** (o sistema está correto e atende às necessidades); **(4) Evolução** (o sistema pode ser mantido e adaptado). O agente deve verificar se cada atividade tem recursos, papéis e critérios de conclusão definidos. |
| **Objetivo** | Garantir que nenhuma atividade essencial seja negligenciada, independentemente da abordagem escolhida. |
| **Motivação** | Cap. 2.2 – todas as atividades estão presentes em todos os processos. |
| **Justificativa** | A omissão de qualquer uma dessas atividades compromete a qualidade e a viabilidade do projeto. |
| **Critérios de Aplicação** | Todo projeto de desenvolvimento de software. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Modelo de processo definido. |
| **Pós-condições** | Plano de projeto com as quatro atividades mapeadas. |
| **Restrições** | Em métodos ágeis, as atividades são intercaladas, mas ainda devem estar presentes (ex: TDD cobre validação). |
| **Dependências** | REGPROC-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Projeto ágil: especificação (user stories), design (refatoração contínua), validação (testes automatizados), evolução (entregas incrementais) – todas cobertas." |
| **Exemplo Negativo** | "Não faremos especificação formal; o código é a especificação." (se não houver user stories ou testes, falha). |
| **Anti-pattern** | Acreditar que métodos ágeis dispensam qualquer tipo de especificação ou validação. |
| **Métrica** | Percentual de projetos com plano de atividades coberto. |
| **Critérios de Auditoria** | Verificar se o plano de projeto inclui as quatro atividades. |
