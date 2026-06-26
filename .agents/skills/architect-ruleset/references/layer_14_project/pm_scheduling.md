# Seção 6 – Regras de Agendamento e Alocação de Recursos (Layer 14 - PM-SCHEDULING)

---

### REGPM-011 – Criação de Diagrama de Gantt para Visualização do Cronograma

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-011 |
| **Nome** | Criação de Diagrama de Gantt para Visualização do Cronograma |
| **Descrição** | O agente deve criar um diagrama de Gantt para visualizar o cronograma do projeto, mostrando: **(1)** Atividades (listadas verticalmente); **(2)** Duração estimada (barras horizontais); **(3)** Datas de início e término; **(4)** Dependências entre atividades (setas); **(5)** Marcos; **(6)** Alocação de recursos (quem trabalha em cada atividade). O diagrama deve ser atualizado regularmente para refletir o progresso real. |
| **Objetivo** | Fornecer uma visão clara e de fácil compreensão do cronograma do projeto. |
| **Motivação** | Cap. 23.3.1 – diagramas de Gantt são a representação mais comum de cronogramas. |
| **Justificativa** | Uma representação visual facilita a comunicação com stakeholders e o monitoramento do progresso. |
| **Critérios de Aplicação** | Todo projeto com mais de 5 atividades. |
| **Critérios de Não Aplicação** | Projetos muito pequenos (≤ 5 atividades) onde uma lista simples é suficiente. |
| **Pré-condições** | Atividades, durações e dependências definidas. |
| **Pós-condições** | Diagrama de Gantt criado e atualizado. |
| **Restrições** | O diagrama deve ser legível (não ter mais de 30 atividades; agrupar se necessário). |
| **Dependências** | REGPM-008. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Diagrama de Gantt com 20 atividades, 5 marcos, dependências claras, atualizado semanalmente." |
| **Exemplo Negativo** | "Cronograma em uma planilha com atividades soltas, sem visualização." |
| **Anti-pattern** | Diagrama de Gantt desatualizado, com datas irreais. |
| **Métrica** | Percentual de projetos com diagrama de Gantt atualizado. |
| **Critérios de Auditoria** | Verificar se o diagrama de Gantt existe e está atualizado. |

---

### REGPM-012 – Identificação do Caminho Crítico e Gestão de Dependências

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPM-012 |
| **Nome** | Identificação do Caminho Crítico e Gestão de Dependências |
| **Descrição** | O agente deve identificar o caminho crítico do projeto – a sequência de tarefas dependentes que determina a duração total do projeto. O agente deve: **(1)** Criar um diagrama PERT (Activity Chart) mostrando as dependências; **(2)** Calcular a duração de cada caminho; **(3)** Identificar o caminho mais longo (crítico); **(4)** Monitorar de perto as tarefas no caminho crítico, pois qualquer atraso nelas atrasa todo o projeto; **(5)** Buscar formas de reduzir o caminho crítico (ex: paralelizar tarefas). |
| **Objetivo** | Garantir que as tarefas mais críticas sejam monitoradas de perto e que o projeto seja concluído no prazo. |
| **Motivação** | Cap. 23.3.1 – o caminho crítico determina a duração mínima do projeto. |
| **Justificativa** | Ignorar o caminho crítico leva a atrasos inesperados e surpresas no final do projeto. |
| **Critérios de Aplicação** | Projetos com mais de 10 tarefas e dependências significativas. |
| **Critérios de Não Aplicação** | Projetos com poucas dependências. |
| **Pré-condições** | Tarefas e dependências definidas. |
| **Pós-condições** | Caminho crítico identificado e monitorado. |
| **Restrições** | O caminho crítico deve ser revisado sempre que houver atrasos significativos. |
| **Dependências** | REGPM-011. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Caminho crítico: especificação → design → implementação → testes → deploy. Duração: 8 meses." |
| **Exemplo Negativo** | "Não sabemos qual é o caminho crítico; todas as tarefas são igualmente importantes." |
| **Anti-pattern** | Ignorar o caminho crítico e focar apenas em tarefas de baixa prioridade. |
| **Métrica** | Atraso no caminho crítico (meta: < 5% da duração total). |
| **Critérios de Auditoria** | Revisar se o caminho crítico está sendo monitorado. |
