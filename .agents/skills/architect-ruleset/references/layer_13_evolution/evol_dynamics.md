# Seção 3 – Regras de Evolução e Dinâmica de Mudanças (Layer 13 - EVOL-DYNAMICS)

---

### REGEVOL-001 – Aplicação das Leis de Lehman para Planejamento de Evolução

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-001 |
| **Nome** | Aplicação das Leis de Lehman para Planejamento de Evolução |
| **Descrição** | O agente deve considerar as Leis de Lehman ao planejar a evolução de sistemas de longa duração. Em particular, deve: **(1)** reconhecer que a mudança é contínua e inevitável (Lei 1); **(2)** planejar investimentos em refatoração para combater o aumento da complexidade (Lei 2); **(3)** considerar que a evolução é auto-reguladora e que aumentar recursos pode não acelerar o processo (Lei 3); **(4)** entender que a estabilidade organizacional afeta a evolução (Lei 4); **(5)** planejar incrementos de mudança consistentes (Lei 5); **(6)** prever que a qualidade declina sem manutenção proativa (Lei 7). O agente deve usar essas leis como base para justificar investimentos em refatoração e melhoria contínua. |
| **Objetivo** | Garantir que as decisões de evolução sejam baseadas em princípios empíricos comprovados, evitando surpresas e custos inesperados. |
| **Motivação** | Cap. 9.2 – Leis de Lehman descrevem padrões observados em sistemas de grande porte. |
| **Justificativa** | Ignorar essas leis leva a sistemas que se tornam cada vez mais difíceis e caros de manter. |
| **Critérios de Aplicação** | Sistemas com mais de 3 anos de vida ou com mais de 100 mil linhas de código. |
| **Critérios de Não Aplicação** | Sistemas de curta duração ou protótipos descartáveis. |
| **Pré-condições** | Dados históricos de evolução do sistema disponíveis (tamanho, complexidade, defeitos). |
| **Pós-condições** | Plano de evolução inclui ações para combater degradação estrutural e gerenciar complexidade. |
| **Restrições** | O agente deve revisar periodicamente se as leis estão sendo respeitadas. |
| **Dependências** | REGEVOL-002 (tipos de manutenção), REGEVOL-003 (refatoração). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Baseado nas Leis de Lehman, alocamos 20% do orçamento de cada release para refatoração e redução de dívida técnica, para evitar degradação estrutural." |
| **Exemplo Negativo** | "Não investimos em refatoração; o código está cada vez mais complexo e difícil de modificar." |
| **Anti-pattern** | Ignorar a degradação estrutural até que o sistema se torne inmantível. |
| **Métrica** | Taxa de aumento da complexidade ciclomática por release (meta: < 2% ao ano). |
| **Critérios de Auditoria** | Verificar se há investimento em refatoração em cada release. |
