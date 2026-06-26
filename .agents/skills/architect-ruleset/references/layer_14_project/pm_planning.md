# Seção 5 – Regras de Planejamento e Estimativa (Layer 14 - PM-PLANNING)

---

### REGPM-008 – Definição de Escopo, Marcos e Entregáveis no Plano de Projeto

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-008 |
| **Nome** | Definição de Escopo, Marcos e Entregáveis no Plano de Projeto |
| **Descrição** | O agente deve garantir que o plano de projeto inclua, no mínimo: **(1)** Escopo: descrição clara do que está incluído e excluído do projeto; **(2)** Atividades: lista de tarefas a serem realizadas; **(3)** Marcos (Milestones): pontos significativos no cronograma (ex: "entrega da arquitetura", "início dos testes"); **(4)** Entregáveis (Deliverables): produtos de trabalho tangíveis (ex: documento de requisitos, código, relatório de testes); **(5)** Cronograma: datas de início e término de cada atividade; **(6)** Alocação de Recursos: quem trabalhará em cada atividade. O agente deve garantir que cada marco tenha critérios de aceitação definidos. |
| **Objetivo** | Garantir que o plano de projeto seja completo, compreensível e forneça uma base para monitoramento. |
| **Motivação** | Cap. 23.2.1 – o plano de projeto é o documento central do gerenciamento de projetos. |
| **Justificativa** | Um plano incompleto ou vago leva a expectativas desalinhadas e dificuldade de monitoramento. |
| **Critérios de Aplicação** | Início de todo projeto. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisitos e restrições conhecidas. |
| **Pós-condições** | Plano de projeto aprovado pelos stakeholders. |
| **Restrições** | O plano deve ser revisado e atualizado periodicamente. |
| **Dependências** | REGPROC-004 (atividades fundamentais). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Plano de projeto com 15 atividades, 5 marcos, 8 entregáveis, cronograma de 6 meses." |
| **Exemplo Negativo** | "Plano de projeto: 'entregar software em 6 meses'." |
| **Anti-pattern** | Criar marcos sem critérios de aceitação (ex: "fase de desenvolvimento concluída"). |
| **Métrica** | Percentual de projetos com plano de projeto documentado. |
| **Critérios de Auditoria** | Revisar o plano de projeto e verificar se inclui todos os elementos obrigatórios. |

---

### REGPM-009 – Estimativa de Esforço com COCOMO II para Projetos Plan-Driven

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-009 |
| **Nome** | Estimativa de Esforço com COCOMO II para Projetos Plan-Driven |
| **Descrição** | Para projetos plan-driven com requisitos estáveis e arquitetura definida, o agente deve utilizar o modelo COCOMO II para estimar o esforço. O agente deve: **(1)** Estimar o tamanho do sistema em KSLOC (milhares de linhas de código) ou pontos de função; **(2)** Aplicar a fórmula: PM = A * Tamanho^B * M (onde A=2.94, B é calculado com base em fatores de escala, M é o multiplicador de custos); **(3)** Usar o submodelo apropriado (application-composition, early design, post-architecture) conforme a fase do projeto; **(4)** Documentar as premissas e a faixa de incerteza (ex: ±25%). |
| **Objetivo** | Fornecer uma estimativa objetiva e baseada em dados empíricos para projetos plan-driven. |
| **Motivação** | Cap. 23.5.2 – COCOMO II é um modelo de estimativa amplamente utilizado. |
| **Justificativa** | Estimativas baseadas em "achismo" são menos confiáveis; COCOMO II fornece uma base objetiva. |
| **Critérios de Aplicação** | Projetos plan-driven com > 10 mil linhas de código ou > 6 meses de duração. |
| **Critérios de Não Aplicação** | Projetos ágeis (usar story points/velocity – REGPM-010). |
| **Pré-condições** | Tamanho estimado e fatores de custo definidos. |
| **Pós-condições** | Estimativa de esforço documentada. |
| **Restrições** | O COCOMO II deve ser calibrado com dados históricos da organização, quando disponíveis. |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Estimativa COCOMO II: tamanho = 50 KSLOC, esforço = 120 pessoas-mês, faixa de incerteza ±20%." |
| **Exemplo Negativo** | "Estimativa baseada em 'feeling' do gerente." |
| **Anti-pattern** | Usar COCOMO II sem calibrar com dados históricos, resultando em estimativas imprecisas. |
| **Métrica** | Precisão da estimativa (esforço real vs. estimado) – meta: < 20% de desvio. |
| **Critérios de Auditoria** | Revisar as estimativas e comparar com o esforço real. |

---

### REGPM-010 – Estimativa Ágil com Story Points e Velocity

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-010 |
| **Nome** | Estimativa Ágil com Story Points e Velocity |
| **Descrição** | Para projetos ágeis, o agente deve utilizar story points e velocity para estimar esforço e planejar releases. O processo inclui: **(1)** Estimar cada user story em story points (ex: usando planning poker); **(2)** Calcular a velocity da equipe com base em sprints anteriores (pontos entregues por sprint); **(3)** Planejar o release com base no backlog priorizado e na velocity; **(4)** Ajustar o escopo (não a data) se a velocity for menor que o esperado. O agente deve documentar a velocity e revisá-la a cada sprint. |
| **Objetivo** | Fornecer estimativas realistas e adaptáveis para projetos ágeis. |
| **Motivação** | Cap. 23.4 – planejamento ágil baseado em velocity e story points. |
| **Justificativa** | A velocity é a métrica mais confiável para estimar capacidade em projetos ágeis. |
| **Critérios de Aplicação** | Projetos ágeis (Scrum, XP). |
| **Critérios de Não Aplicação** | Projetos plan-driven (usar REGPM-009). |
| **Pré-condições** | Backlog priorizado e estimado. |
| **Pós-condições** | Release plan e sprint backlog definidos. |
| **Restrições** | A velocity deve ser recalculada a cada sprint. |
| **Dependências** | REGPROC-009 (Scrum), REGPROC-010 (planning). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Velocity = 30 pontos/sprint. Backlog = 150 pontos → release em 5 sprints." |
| **Exemplo Negativo** | "Estimamos tudo em horas, sem calcular velocity." |
| **Anti-pattern** | Ignorar a velocity e prometer entregas irrealistas. |
| **Métrica** | Precisão da estimativa (story points entregues vs. planejados). |
| **Critérios de Auditoria** | Verificar se a velocity é usada no planejamento. |
