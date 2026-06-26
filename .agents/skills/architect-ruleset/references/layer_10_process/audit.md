# Seção 10 – Critérios de Auditoria, Exemplo e Evolução (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-AUDIT  
**Status:** Definitivo  
**Escopo:** Métodos de verificação de processos, caso prático integrado de aplicação e extensões futuras.

---

## 1. Matriz de Auditoria de Processos

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| **AUD-PROC-01** | Análise contextual para escolha do processo (REGPROC-001). | Revisar se existe uma avaliação documentada considerando as cinco dimensões de contexto antes da seleção. |
| **AUD-PROC-02** | Cascata usado apenas com requisitos estáveis (REGPROC-002). | Verificar se projetos que usam modelo em cascata possuem histórico estável e sem grandes alterações de escopo. |
| **AUD-PROC-03** | Desenvolvimento incremental para requisitos voláteis (REGPROC-003). | Verificar se há planejamento de incrementos de curta duração e entregas funcionais intermediárias. |
| **AUD-PROC-04** | Quatro atividades fundamentais cobertas (REGPROC-004). | Confirmar se especificação, projeto/implementação, validação e evolução estão explicitadas nas fases planejadas. |
| **AUD-PROC-05** | Uso de prototipação para incertezas (REGPROC-005). | Revisar se foram criados protótipos em caso de tecnologias novas ou requisitos funcionais ambíguos. |
| **AUD-PROC-06** | Entregas incrementais planejadas (REGPROC-006). | Verificar a existência de datas e escopos de lançamentos frequentes ao cliente para obtenção de feedback. |
| **AUD-PROC-07** | Princípios do Manifesto Ágil aplicados (REGPROC-007). | Avaliar a dinâmica da equipe (reuniões diárias, retrospectivas e contato direto com o cliente). |
| **AUD-PROC-08** | Práticas XP adotadas quando apropriado (REGPROC-008). | Confirmar o uso de desenvolvimento orientado a testes (TDD), programação em pares e integração contínua (CI). |
| **AUD-PROC-09** | Scrum de sprints e cerimônias implementado (REGPROC-009). | Validar artefatos gerados (Backlog, Sprint Backlog) e a realização de reuniões de planejamento, revisão e retrospectiva. |
| **AUD-PROC-10** | Planejamento baseado em velocity (REGPROC-010). | Verificar se o esforço é estimado em story points e se o histórico de velocity é empregado para estimar datas. |
| **AUD-PROC-11** | Adaptações para escalar métodos ágeis (REGPROC-011). | Auditar a estrutura de squads, documentação arquitetural mínima e papéis de liderança em projetos > 10 pessoas. |
| **AUD-PROC-12** | Documentação do processo (REGPROC-012). | Confirmar se o fluxo e os papéis estão registrados e visíveis para a equipe no repositório ou wiki do projeto. |

---

## 2. Exemplo Integrado de Aplicação

**Cenário**: Uma startup de 8 desenvolvedores está criando um aplicativo de delivery de comida. Os requisitos mudam frequentemente baseados em feedback do mercado. O produto precisa ser lançado rapidamente, mas a qualidade é importante para evitar perda de clientes.

**Aplicação das Regras**:

1. **REGPROC-001 (Análise Contextual)**: O agente avalia: requisitos voláteis (alta), equipe pequena (8), criticidade média, maturidade baixa. Recomenda método ágil (Scrum + XP).
2. **REGPROC-007 (Manifesto Ágil)**: O agente enfatiza a colaboração com o PO (fundador) e entregas rápidas.
3. **REGPROC-008 (XP)**: Recomenda TDD e pair programming para garantir qualidade.
4. **REGPROC-009 (Scrum)**: Define sprints de 2 semanas, com Daily Scrums, Reviews e Retrospectivas.
5. **REGPROC-010 (Velocity)**: Estima histórias com planning poker, calcula velocity após 2 sprints.
6. **REGPROC-006 (Entregas Incrementais)**: Planeja entregas a cada sprint para obter feedback do mercado.
7. **REGPROC-012 (Documentação)**: Cria um wiki leve com o processo, papéis e decisões.
8. **REGPROC-011 (Escalabilidade)**: Como a equipe é pequena, não há necessidade de adaptações complexas.

**Saída Final (resumida)**:
> "Projeto de aplicativo de delivery: recomendo Scrum com sprints de 2 semanas, combinado com práticas XP (TDD, pair programming, CI). O PO deve priorizar o backlog semanalmente. Planejamento baseado em velocity. Entregas incrementais a cada sprint. Documentação leve em wiki. A equipe deve realizar retrospectivas para melhoria contínua."

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido com sub-módulos especializados:
- **Módulo 11-A**: Frameworks de Escalonamento Ágil (SAFe, LeSS, Nexus).
- **Módulo 11-B**: Processos para Sistemas Críticos e Regulados (DO-178C, IEC 61508).
- **Módulo 11-C**: Melhoria de Processos (CMMI, ISO 15504, GQM).
- **Módulo 11-D**: Processos para Desenvolvimento Distribuído e Open Source.

Todas as extensões devem respeitar as regras base e a Constituição.
