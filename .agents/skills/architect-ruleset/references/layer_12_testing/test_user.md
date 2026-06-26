# Seção 5 – Regras de Testes de Usuário (Layer 12 - TEST-USER)

---

### REGTEST-006 – Envolvimento do Usuário em Testes Alfa e Beta

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-006 |
| **Nome** | Envolvimento do Usuário em Testes Alfa e Beta |
| **Descrição** | O agente deve recomendar e planejar a participação de usuários reais nos testes, utilizando duas abordagens: **(1)** Testes Alfa: usuários testam o sistema no ambiente do desenvolvedor, com feedback direto à equipe; **(2)** Testes Beta: uma versão quase final do sistema é disponibilizada para um grupo seleto de usuários em seu próprio ambiente, para que possam experimentá-lo e reportar problemas. O agente deve coletar e priorizar o feedback dos usuários, incorporando correções antes da liberação final. |
| **Objetivo** | Validar o sistema em condições reais de uso, identificando problemas que não foram detectados em testes internos. |
| **Motivação** | Cap. 8.4 – testes de usuário são essenciais para descobrir problemas de usabilidade, adequação e ambiente. |
| **Justificativa** | Desenvolvedores não conseguem replicar todas as condições de uso; usuários reais fornecem insights valiosos. |
| **Critérios de Aplicação** | Projetos com interação com usuários finais. |
| **Critérios de Não Aplicação** | Projetos sem usuários externos (ex: sistemas embarcados críticos). |
| **Pré-condições** | Sistema estável para testes. |
| **Pós-condições** | Feedback coletado e priorizado. |
| **Restrições** | O feedback deve ser documentado e rastreado até a correção. |
| **Dependências** | REGTEST-004. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Teste alfa com 5 usuários internos, feedback incorporado. Teste beta com 50 clientes piloto, bugs reportados e corrigidos antes do lançamento." |
| **Exemplo Negativo** | "Lançamos o sistema sem testes com usuários reais." |
| **Anti-pattern** | Ignorar o feedback dos testes alfa/beta por questões de cronograma. |
| **Métrica** | Número de issues reportadas em testes alfa/beta vs. pós-liberação. |
| **Critérios de Auditoria** | Verificar se há registros de testes alfa/beta e se o feedback foi tratado. |

---

### REGTEST-007 – Testes de Aceitação com Critérios Objetivos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-007 |
| **Nome** | Testes de Aceitação com Critérios Objetivos |
| **Descrição** | Para sistemas customizados ou produtos com contrato formal, o agente deve garantir que os testes de aceitação sejam realizados com critérios objetivos e previamente definidos. Os critérios de aceitação devem: **(1)** ser derivados dos requisitos do sistema; **(2)** ser mensuráveis (ex: "tempo de resposta < 500ms para 95% das requisições"); **(3)** ser aprovados pelo cliente antes dos testes; **(4)** ser documentados em um plano de aceitação. Se os testes de aceitação falharem, o agente deve documentar as falhas e negociar com o cliente as correções ou a aceitação condicional. |
| **Objetivo** | Garantir que a decisão de aceitação seja baseada em critérios objetivos e não em impressões subjetivas. |
| **Motivação** | Cap. 8.4 – testes de aceitação são a etapa final para decidir se o sistema é aceito. |
| **Justificativa** | Critérios subjetivos geram disputas; critérios objetivos facilitam a decisão e reduzem riscos. |
| **Critérios de Aplicação** | Projetos com contrato formal de desenvolvimento. |
| **Critérios de Não Aplicação** | Projetos ágeis com aceitação contínua (ex: cada sprint). |
| **Pré-condições** | Critérios de aceitação definidos e aprovados. |
| **Pós-condições** | Relatório de aceitação assinado pelo cliente. |
| **Restrições** | Se os critérios não forem atendidos, o sistema não pode ser aceito sem negociação formal. |
| **Dependências** | REGREQ-004, REGTEST-004. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Critérios de aceitação: 100% dos requisitos funcionais testados, performance < 500ms, segurança sem vulnerabilidades críticas. Todos atendidos. Sistema aceito." |
| **Exemplo Negativo** | "Aceitamos o sistema porque parece funcionar." |
| **Anti-pattern** | Critérios de aceitação vagos ou não testáveis (ex: "sistema deve ser rápido"). |
| **Métrica** | Percentual de projetos com critérios de aceitação objetivos. |
| **Critérios de Auditoria** | Revisar o plano de aceitação e os critérios. |
