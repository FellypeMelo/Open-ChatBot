# Seção 4 – Regras de Testes de Liberação e Validação (Layer 12 - TEST-RELEASE)

---

### REGTEST-004 – Testes de Liberação Baseados em Requisitos e Cenários

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-004 |
| **Nome** | Testes de Liberação Baseados em Requisitos e Cenários |
| **Descrição** | Antes de liberar uma nova versão do sistema, o agente deve garantir que testes de liberação sejam executados, utilizando duas abordagens complementares: **(1)** Testes Baseados em Requisitos: derivar casos de teste diretamente dos requisitos funcionais e não-funcionais; **(2)** Testes de Cenário: criar histórias realistas de uso do sistema e validar que o sistema se comporta conforme esperado em cada cenário. O agente deve documentar a rastreabilidade entre os testes e os requisitos. |
| **Objetivo** | Validar que o sistema atende aos requisitos e é adequado para uso externo. |
| **Motivação** | Cap. 8.3.1 e 8.3.2 – testes de liberação devem demonstrar que o sistema cumpre seus requisitos. |
| **Justificativa** | Testes baseados apenas em defeitos não garantem que o sistema atende às necessidades do cliente. |
| **Critérios de Aplicação** | Toda liberação de sistema (major, minor, patch). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisitos documentados e cenários definidos. |
| **Pós-condições** | Relatório de testes de liberação aprovado. |
| **Restrições** | Os testes de cenário devem envolver stakeholders, quando possível. |
| **Dependências** | REGREQ-004 (requisitos), REGMODEL-004 (casos de uso). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Testes de liberação: 120 casos de teste derivados de requisitos, 15 cenários de uso validados com PO. Todos aprovados." |
| **Exemplo Negativo** | "Liberamos o sistema sem testes formais; confiamos que a equipe testou." |
| **Anti-pattern** | Testar apenas o fluxo principal (happy path) e ignorar exceções. |
| **Métrica** | Percentual de requisitos cobertos por testes de liberação. |
| **Critérios de Auditoria** | Revisar a matriz de rastreabilidade requisito → teste. |

---

### REGTEST-005 – Testes de Performance e Estresse para Sistemas com RTs de Performance

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-005 |
| **Nome** | Testes de Performance e Estresse para Sistemas com RTs de Performance |
| **Descrição** | Se o sistema possui requisitos não-funcionais de performance (RTs com métricas de tempo de resposta, throughput, etc.), o agente deve garantir que testes de performance e estresse sejam executados antes de cada liberação. Os testes devem: **(1)** validar o desempenho sob carga normal (teste de carga); **(2)** validar o comportamento sob carga extrema (teste de estresse); **(3)** identificar gargalos e pontos de falha; **(4)** verificar a recuperação após pico de carga. Os resultados devem ser comparados com os RTs de performance e, se não forem atendidos, a liberação deve ser bloqueada. |
| **Objetivo** | Garantir que o sistema atenda aos requisitos de performance em produção. |
| **Motivação** | Cap. 8.3.3 – testes de performance são essenciais para sistemas com requisitos de desempenho. |
| **Justificativa** | Performance insatisfatória é uma das principais causas de rejeição de sistemas pelos usuários. |
| **Critérios de Aplicação** | Sistemas com RTs de performance definidos. |
| **Critérios de Não Aplicação** | Aplicações de baixa criticidade sem requisitos de performance explícitos. |
| **Pré-condições** | Ferramenta de teste de performance configurada (ex: JMeter, Gatling, k6). |
| **Pós-condições** | Relatório de performance aprovado. |
| **Restrições** | Os testes devem ser executados em ambiente que simule a produção. |
| **Dependências** | REGREQ-005 (SMART), REGQUAL-009. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Teste de carga: 600k requisições/mês, tempo de resposta médio 450ms (RT: 500ms). Aprovado." |
| **Exemplo Negativo** | "Não realizamos testes de performance; esperamos que funcione." |
| **Anti-pattern** | Testar performance apenas em ambiente de desenvolvimento, com dados irreais. |
| **Métrica** | Percentual de releases com testes de performance executados. |
| **Critérios de Auditoria** | Revisar relatórios de performance para cada release major/minor. |
