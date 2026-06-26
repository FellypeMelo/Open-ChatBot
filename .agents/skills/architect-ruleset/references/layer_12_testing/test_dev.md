# Seção 3 – Regras de Testes de Desenvolvimento (Layer 12 - TEST-DEV)

---

### REGTEST-001 – Obrigação de Testes Unitários com Cobertura Mínima (80%)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-001 |
| **Nome** | Obrigação de Testes Unitários com Cobertura Mínima (80%) |
| **Descrição** | O agente deve garantir que todo código novo ou modificado tenha testes unitários automatizados com cobertura mínima de **80%** (linhas e branches). A cobertura deve ser medida automaticamente no pipeline de CI. Se a cobertura cair abaixo de 80%, o merge é bloqueado (quality gate). Exceções podem ser concedidas para código legado, mas devem ser documentadas e acompanhadas de um plano de recuperação. |
| **Objetivo** | Garantir que o código seja testável e que a maioria dos caminhos seja validada automaticamente. |
| **Motivação** | Cap. 8.1.1 – testes unitários são a primeira linha de defesa contra regressões. |
| **Justificativa** | Baixa cobertura indica alto risco de defeitos. A meta de 80% é um padrão industrial amplamente aceito. |
| **Critérios de Aplicação** | Todo código novo ou modificado. |
| **Critérios de Não Aplicação** | Código legado com cobertura < 80% não precisa ser bloqueado, mas deve ter um plano de melhoria documentado. |
| **Pré-condições** | Ferramenta de cobertura configurada (ex: JaCoCo, Istanbul, Coverage.py). |
| **Pós-condições** | Cobertura ≥ 80% para que o merge seja aprovado. |
| **Restrições** | Cobertura de branches é tão importante quanto cobertura de linhas. |
| **Dependências** | REGQUAL-006 (quality gates), REGARCH-SW-009 (impacto). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Cobertura de 92% (linhas) e 88% (branches). Passou no quality gate." |
| **Exemplo Negativo** | "Cobertura de 45% – merge aprovado sem justificativa." |
| **Anti-pattern** | Testes que apenas "chamam" o código sem verificar asserts (cobertura falsa). |
| **Métrica** | Percentual de cobertura total do código-base. |
| **Critérios de Auditoria** | Revisar relatórios de cobertura para identificar áreas com baixa cobertura. |

---

### REGTEST-002 – Testes de Integração Obrigatórios para Dependências Externas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-002 |
| **Nome** | Testes de Integração Obrigatórios para Dependências Externas |
| **Descrição** | Todo componente que depende de serviços externos (bancos, APIs, filas, sistemas legados) deve ter testes de integração automatizados que validem a comunicação com essas dependências. Os testes devem verificar: (1) contratos, (2) comportamento esperado (respostas, erros), (3) timeouts e retries, (4) idempotência e (5) falhas simuladas (ex: serviço indisponível). Estes testes devem rodar em um ambiente de integração contínua (CI) e não podem ser ignorados. |
| **Objetivo** | Garantir que as integrações funcionem conforme o esperado em ambientes não controlados (produção). |
| **Motivação** | Cap. 8.1.3 – testes de componente/interface são essenciais para detectar problemas de integração. |
| **Justificativa** | Testes unitários com mocks não capturam problemas de integração real (ex: mudança de contrato, performance, timeouts). |
| **Critérios de Aplicação** | Todo componente com dependência externa. |
| **Critérios de Não Aplicação** | Componentes que não possuem dependências externas (apenas testes unitários). |
| **Pré-condições** | Dependências externas acessíveis em ambiente de CI (ex: containers Docker). |
| **Pós-condições** | Testes de integração passam antes do merge. |
| **Restrições** | Se a dependência externa não estiver disponível (ex: sistema de terceiros), use mocks com contrato validado (ex: WireMock). |
| **Dependências** | REGTEST-001, REGARCH-SW-006 (contratos). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Teste de integração do `VariantService` com PostgreSQL: valida conexão, queries e transações. Passou no CI." |
| **Exemplo Negativo** | "Não temos testes de integração; confiamos que o banco funcionará." |
| **Anti-pattern** | Testes de integração que dependem de dados de produção (ex: banco real com dados sensíveis). |
| **Métrica** | Percentual de componentes com testes de integração. |
| **Critérios de Auditoria** | Revisar cobertura de testes de integração para módulos críticos. |

---

### REGTEST-003 – TDD (Test-Driven Development) Obrigatório para Novas Funcionalidades

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-003 |
| **Nome** | TDD (Test-Driven Development) Obrigatório para Novas Funcionalidades |
| **Descrição** | Para novas funcionalidades ou mudanças significativas, o agente deve recomendar e, quando possível, exigir a prática de TDD (Test-Driven Development). O ciclo do TDD é: **(1)** Escrever um teste automatizado para a nova funcionalidade; **(2)** Executar o teste e verificar que ele falha (O código ainda não existe); **(3)** Escrever o código mínimo necessário para fazer o teste passar; **(4)** Executar todos os testes e verificar que todos passam; **(5)** Refatorar o código, melhorando sua estrutura sem alterar comportamento; **(6)** Repetir o ciclo para a próxima funcionalidade. |
| **Objetivo** | Garantir que o código seja escrito com qualidade desde o início, com testes que documentam o comportamento esperado. |
| **Motivação** | Cap. 8.2 – TDD melhora a qualidade do código e reduz defeitos. |
| **Justificativa** | TDD força o desenvolvedor a pensar nos requisitos antes de codificar, resultando em código mais testável e com menos defeitos. |
| **Critérios de Aplicação** | Novas funcionalidades ou mudanças significativas (> 10% do código do módulo). |
| **Critérios de Não Aplicação** | Correções de bugs simples (ex: ajuste de uma condição). |
| **Pré-condições** | Framework de testes automatizados configurado. |
| **Pós-condições** | Testes escritos e aprovados antes da entrega. |
| **Restrições** | O TDD não substitui testes de integração ou de sistema; é uma prática complementar. |
| **Dependências** | REGTEST-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Para a nova funcionalidade de cálculo de frete, escrevemos testes unitários primeiro, depois implementamos a lógica. Todos os testes passaram." |
| **Exemplo Negativo** | "Implementamos o cálculo de frete e depois escrevemos alguns testes para 'validar'." |
| **Anti-pattern** | Escrever testes apenas para "cumprir tabela", sem seguir o ciclo TDD (ex: testes escritos após o código, sem verificação de falha inicial). |
| **Métrica** | Percentual de novas funcionalidades desenvolvidas com TDD. |
| **Critérios de Auditoria** | Revisar histórico de commits: verificar se os testes foram escritos antes do código. |
