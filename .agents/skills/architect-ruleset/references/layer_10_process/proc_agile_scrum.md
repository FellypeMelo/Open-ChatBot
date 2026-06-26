# Seção 7 – Regras de Scrum e Gestão Ágil de Projetos (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-AGILE-SCRUM  
**Status:** Definitivo  
**Escopo:** Gestão ágil de portfólio usando sprints e estimativas com velocity.

---

### REGPROC-009 – Uso do Scrum para Gerenciamento de Projetos Ágeis com Sprints Fixos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-009 |
| **Nome** | Uso do Scrum para Gerenciamento de Projetos Ágeis com Sprints Fixos |
| **Descrição** | Para projetos que adotam métodos ágeis, o agente deve recomendar o Scrum como framework de gerenciamento, com sprints de duração fixa (2 a 4 semanas), papéis definidos (Product Owner, Scrum Master, Time de Desenvolvimento), e artefatos (Product Backlog, Sprint Backlog, Incremento). O agente deve garantir que: **(1)** o Product Backlog seja priorizado pelo PO; **(2)** as reuniões diárias (Daily Scrum) sejam curtas (≤ 15 min) e focadas no progresso; **(3)** a Sprint Review e a Retrospectiva sejam realizadas ao final de cada sprint. |
| **Objetivo** | Estruturar o gerenciamento ágil com disciplina e transparência. |
| **Motivação** | Cap. 3.4 – Scrum é um framework ágil amplamente utilizado para gestão de projetos. |
| **Justificativa** | Scrum oferece visibilidade, adaptação e engajamento do cliente. |
| **Critérios de Aplicação** | Projetos ágeis com equipes de até 10 pessoas. |
| **Critérios de Não Aplicação** | Projetos onde o cliente não pode participar da priorização. |
| **Pré-condições** | PO definido, equipe treinada em Scrum. |
| **Pós-condições** | Processo Scrum implementado com artefatos e cerimônias. |
| **Restrições** | Os sprints não podem ser estendidos; se houver atraso, o escopo deve ser reduzido. |
| **Dependências** | REGPROC-007. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Projeto com PO dedicado, sprints de 2 semanas, retrospectivas e reviews regulares – equipe engajada." |
| **Exemplo Negativo** | "Scrum sem PO, sprints de 3 meses, sem retrospectiva." |
| **Anti-pattern** | Tratar Scrum como um ritual vazio, sem adaptação. |
| **Métrica** | Percentual de sprints entregues com sucesso. |
| **Critérios de Auditoria** | Verificar se as cerimônias Scrum são realizadas. |

---

### REGPROC-010 – Planejamento de Release e Sprint (Scrum/XP) com Estimativa por Velocity

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-010 |
| **Nome** | Planejamento de Release e Sprint (Scrum/XP) com Estimativa por Velocity |
| **Descrição** | Em projetos ágeis que usam Scrum ou XP, o agente deve garantir que o planejamento de release e sprint seja feito com base em estimativas de esforço (story points, horas ideais) e na velocity da equipe (pontos por sprint). O agente deve: **(1)** orientar a equipe a estimar as user stories de forma relativa (ex: planning poker); **(2)** calcular a velocity com base em sprints anteriores; **(3)** planejar o release com base no backlog priorizado e na velocity; **(4)** ajustar o escopo, não a data, em caso de desvios. |
| **Objetivo** | Garantir planejamento realista e previsível em projetos ágeis. |
| **Motivação** | Cap. 23.4 – planejamento ágil baseado em velocity e story points. |
| **Justificativa** | A velocity é a métrica mais confiável para estimar capacidade em projetos ágeis. |
| **Critérios de Aplicação** | Projetos que usam Scrum ou XP. |
| **Critérios de Não Aplicação** | Projetos plan-driven com estimativas tradicionais. |
| **Pré-condições** | Backlog priorizado e estimado. |
| **Pós-condições** | Release plan e sprint backlog definidos. |
| **Restrições** | A velocity deve ser recalculada a cada sprint. |
| **Dependências** | REGPROC-009. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Velocity de 30 pontos/sprint. Backlog de 150 pontos → release em 5 sprints." |
| **Exemplo Negativo** | "Estimamos tudo em horas e não calculamos velocity." |
| **Anti-pattern** | Ignorar a velocity e prometer entregas irrealistas. |
| **Métrica** | Precisão da estimativa vs. entregue. |
| **Critérios de Auditoria** | Verificar se a velocity é usada no planejamento. |
