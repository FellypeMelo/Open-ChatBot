# Layer 10 – Process & Lifecycle Rules (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-11  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 10 – Process & Lifecycle Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software), Módulo 05 (Qualidade), Módulo 06 (Segurança/Privacidade), Módulo 07 (Documentação), Módulo 08 (Governança), Módulo 09 (Riscos), Módulo 10 (Output) – obrigatórios  
**Autoridade:** Subordinado a todas as Layers 0 a 9. Nenhuma regra deste módulo pode violar qualquer princípio ou regra definida nas camadas superiores.  
**Escopo:** Define o conjunto completo de regras para a seleção, adaptação e execução de processos de software, abrangendo modelos tradicionais (cascata, incremental, espiral, RUP), métodos ágeis (XP, Scrum), atividades fundamentais de engenharia de software, gestão de mudanças, e critérios para escolha entre abordagens plan-driven e agile. Este módulo capacita o agente a recomendar o processo mais adequado para cada contexto de projeto, integrando boas práticas de gestão, qualidade e governança, com base nos Capítulos 2 (Processos de Software), 3 (Desenvolvimento Ágil de Software) e 2.4 (RUP) do livro-base "Software Engineering" (Sommerville, 9ª ed.).

---

## Estrutura do Módulo

Este módulo estabelece o **Sistema de Seleção e Execução de Processos** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_10_process/glossary.md)**  
   *Definições canônicas de processos de software, modelos em cascata, incremental, espiral, RUP, ágil, XP, Scrum e velocity baseadas no Sommerville.*

2. **[Princípios Fundamentais de Processos](./layer_10_process/principles.md)**  
   *Princípios como "Não Existe Processo Único", invariância das atividades fundamentais, acolhimento de mudanças e balanceamento de abordagens.*

3. **[Regras de Seleção de Modelos de Processo (PROC-SELECT)](./layer_10_process/proc_select.md)**  
   *Regras (REGPROC-001 a REGPROC-003) para análise de cinco dimensões de contexto e limites para uso de cascata vs. incremental.*

4. **[Regras de Atividades Fundamentais (PROC-ACTIVITIES)](./layer_10_process/proc_activities.md)**  
   *Regra (REGPROC-004) exigindo a cobertura e planejamento adequado de especificação, projeto/implementação, validação e evolução.*

5. **[Regras de Gestão de Mudanças e Prototipação (PROC-CHANGE)](./layer_10_process/proc_change.md)**  
   *Regras (REGPROC-005 a REGPROC-006) regulando o uso de protótipos descartáveis/evolutivos e o planejamento de entregas incrementais.*

6. **[Regras de Métodos Ágeis e Extreme Programming (PROC-AGILE-XP)](./layer_10_process/proc_agile_xp.md)**  
   *Regras (REGPROC-007 a REGPROC-008) sobre a aplicação de princípios do manifesto ágil e adoção de práticas XP (TDD, par, CI).*

7. **[Regras de Scrum e Gestão Ágil de Projetos (PROC-AGILE-SCRUM)](./layer_10_process/proc_agile_scrum.md)**  
   *Regras (REGPROC-009 a REGPROC-010) ditando a execução do Scrum com duração de sprint fixa e planejamento baseado em velocity.*

8. **[Regras de Escalabilidade e Adaptação de Métodos Ágeis (PROC-SCALING)](./layer_10_process/proc_scaling.md)**  
   *Regras (REGPROC-011) definindo a escalação de métodos ágeis em grandes equipes e sistemas críticos de segurança.*

9. **[Regras de Governança e Documentação de Processos (PROC-GOV)](./layer_10_process/proc_gov.md)**  
   *Regras (REGPROC-012) exigindo documentação leve, mas auditável, dos processos em três níveis distintos.*

10. **[Auditoria, Exemplo Prático e Evolução](./layer_10_process/audit.md)**  
    *Tabela de auditoria para a Layer 10 contendo 12 critérios, exemplo integrado de aplicação (startup de entrega de comida) e direções de extensão.*
