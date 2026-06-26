# Layer 14 – Project Management & Planning Rules (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-15  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 14 – Project Management & Planning Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software), Módulo 05 (Qualidade), Módulo 06 (Segurança/Privacidade), Módulo 07 (Documentação), Módulo 08 (Governança), Módulo 09 (Riscos), Módulo 10 (Output), Módulo 11 (Processos), Módulo 12 (Modelagem), Módulo 13 (Testes), Módulo 14 (Evolução) – obrigatórios  
**Autoridade:** Subordinado a todas as Layers 0 a 13. Nenhuma regra deste módulo pode violar qualquer princípio ou regra definida nas camadas superiores.  
**Escopo:** Define o conjunto completo de regras para o gerenciamento de projetos de software e planejamento, abrangendo desde a gestão de riscos (identificação, análise, mitigação, monitoramento), passando pela gestão de pessoas e equipes (motivação, composição, comunicação), até o planejamento de projeto (escopo, atividades, marcos, entregáveis), técnicas de estimativa (COCOMO, pontos de função, análise de pontos, story points), agendamento (diagramas de Gantt, PERT, alocação de recursos), e planejamento ágil (release planning, sprint planning, velocity), com base nos Capítulos 22 (Gerenciamento de Projetos) e 23 (Planejamento de Projetos) do livro-base "Software Engineering" (Sommerville, 9ª ed.).

---

## Estrutura do Módulo

Este módulo estabelece o **Sistema de Gerenciamento e Planejamento de Projetos** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_14_project/glossary.md)**  
   *Definições canônicas de gerenciamento de projetos, risco (projeto/produto/negócio), mitigação, plano de contingência, motivação, coesão de grupo, estimativa, COCOMO II, pontos de função, story points, velocity, diagramas de Gantt/PERT, caminho crítico, marcos e entregáveis.*

2. **[Princípios Fundamentais](./layer_14_project/principles.md)**  
   *Princípios como "GP além de Ferramentas", "Risco como atividade contínua", "Pessoas como ativo mais importante", "Incerteza das estimativas", "Planejamento iterativo/adaptativo" e "Comunicação como chave".*

3. **[Regras de Gestão de Riscos (PM-RISK)](./layer_14_project/pm_risk.md)**  
   *Regras (REGPM-001 a REGPM-004) regulando a identificação de riscos via brainstorming/checklists, análise com matriz de probabilidade x impacto, planos de mitigação/contingência e KRIs.*

4. **[Regras de Gestão de Pessoas e Equipes (PM-PEOPLE)](./layer_14_project/pm_people.md)**  
   *Regras (REGPM-005 a REGPM-007) ditando a composição de equipe com personalidades complementares (tarefa, self, interação), engajamento via pirâmide de Maslow e reuniões de coesão.*

5. **[Regras de Planejamento e Estimativa (PM-PLANNING)](./layer_14_project/pm_planning.md)**  
   *Regras (REGPM-008 a REGPM-010) sobre a definição de escopo, marcos/entregáveis em planos formais, estimativa com COCOMO II e estimativas ágeis via story points e velocity.*

6. **[Regras de Agendamento e Alocação de Recursos (PM-SCHEDULING)](./layer_14_project/pm_scheduling.md)**  
   *Regras (REGPM-011 a REGPM-012) exigindo a criação de diagramas de Gantt dinâmicos e determinação/monitoramento de caminho crítico por diagramas PERT.*

7. **[Auditoria, Exemplo Prático e Evolução](./layer_14_project/audit.md)**  
   *Tabela de auditoria contendo 12 critérios, exemplo integrado de aplicação (planejamento de marketplace em startup) e direções de evolução.*
