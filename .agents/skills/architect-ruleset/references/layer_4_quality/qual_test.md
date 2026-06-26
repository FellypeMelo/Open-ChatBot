# Seção 5 – Regras de Testes e Validação / Layer 4 (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-TEST  
**Status:** Definitivo  
**Escopo:** Cobertura de código, testes de integração, testes de contrato e ensaios de performance.

---

### REGQUAL-006 – Cobertura Mínima de Testes Unitários (80%)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-006 |
| **Nome** | Cobertura Mínima de Testes Unitários (80%) |
| **Descrição** | O agente deve exigir que todo código novo ou modificado tenha cobertura de testes unitários de, no mínimo, **80%** (linhas e branches). A cobertura deve ser medida automaticamente no pipeline de CI. Se a cobertura cair abaixo de 80%, o merge é bloqueado (quality gate). Exceções podem ser concedidas para código legado, mas devem ser documentadas e acompanhadas de um plano de recuperação. |
| **Objetivo** | Garantir que o código seja testável e que a maioria dos caminhos seja validada automaticamente. |
| **Motivação** | Cap. 8.3.1 (análise de impacto) e Cap. 8.3.2 (simulação e teste). |
| **Justificativa** | Testes unitários são a primeira linha de defesa contra regressões. Baixa cobertura indica alto risco de defeitos. |
| **Critérios de Aplicação** | Todo código novo ou modificado. |
| **Critérios de Não Aplicação** | Código legado com cobertura < 80% não precisa ser bloqueado, mas deve ter um plano de melhoria documentado. |
| **Pré-condições** | Ferramenta de cobertura configurada (ex: JaCoCo, Istanbul). |
| **Pós-condições** | Cobertura ≥ 80% para que o merge seja aprovado. |
| **Restrições** | Cobertura de branches é tão importante quanto cobertura de linhas. |
| **Dependências** | REGQUAL-004. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Cobertura de 92% (linhas) e 88% (branches). Passou no quality gate." |
| **Exemplo Negativo** | "Cobertura de 45% – merge aprovado sem justificativa." |
| **Anti-pattern** | Testes que apenas "chamam" o código sem verificar asserts (cobertura falsa). |
| **Métrica** | Percentual de cobertura total do código-base. |
| **Critérios de Auditoria** | Revisar relatórios de cobertura para identificar áreas com baixa cobertura. |

---

### REGQUAL-007 – Testes de Integração Obrigatórios para Dependências Externas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-007 |
| **Nome** | Testes de Integração Obrigatórios para Dependências Externas |
| **Descrição** | Todo componente que depende de serviços externos (bancos, APIs, filas, sistemas legados) deve ter testes de integração automatizados que validem a comunicação com essas dependências. Os testes devem verificar: (1) contratos (REGARCH-SW-006), (2) comportamento esperado (respostas, erros), (3) timeouts e retries, (4) idempotência e (5) falhas simuladas (ex: serviço indisponível). Estes testes devem rodar em um ambiente de integração contínua (CI) e não podem ser ignorados. |
| **Objetivo** | Garantir que as integrações funcionem conforme o esperado em ambientes não controlados (produção). |
| **Motivação** | Cap. 8.3.2 (redes de fluxo de dados) e Cap. 10.4.5 (contratos). |
| **Justificativa** | Testes unitários com mocks não capturam problemas de integração real (ex: mudança de contrato, performance, timeouts). |
| **Critérios de Aplicação** | Todo componente com dependência externa. |
| **Critérios de Não Aplicação** | Componentes que não possuem dependências externas (apenas testes unitários). |
| **Pré-condições** | Dependências externas acessíveis em ambiente de CI (ex: containers Docker). |
| **Pós-condições** | Testes de integração passam antes do merge. |
| **Restrições** | Se a dependência externa não estiver disponível (ex: sistema de terceiros), use mocks com contrato validado (ex: WireMock). |
| **Dependências** | REGARCH-SW-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Teste de integração do `VariantService` com PostgreSQL: valida conexão, queries e transações. Passou no CI." |
| **Exemplo Negativo** | "Não temos testes de integração; confiamos que o banco funcionará." |
| **Anti-pattern** | Testes de integração que dependem de dados de produção (ex: banco real com dados sensíveis). |
| **Métrica** | Percentual de componentes com testes de integração. |
| **Critérios de Auditoria** | Revisar cobertura de testes de integração para módulos críticos. |

---

### REGQUAL-008 – Testes de Contrato (Consumer-Driven Contract Testing)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-008 |
| **Nome** | Testes de Contrato (Consumer-Driven Contract Testing) |
| **Descrição** | Para serviços com múltiplos consumidores (ex: API pública), o agente deve recomendar e exigir a prática de testes de contrato orientados a consumidor (ex: Pact). O provedor do serviço deve executar os testes de contrato de todos os consumidores para garantir que nenhuma mudança quebre um consumidor existente. A falha em um teste de contrato deve bloquear o deploy do provedor. |
| **Objetivo** | Garantir que mudanças no provedor não quebrem consumidores, especialmente em arquiteturas de microsserviços. |
| **Motivação** | Cap. 5.3 (interface como contrato), Cap. 10.4.5 (contratos). |
| **Justificativa** | Em microsserviços, a comunicação entre equipes é frágil. Testes de contrato reduzem drasticamente a necessidade de ambientes de integração compartilhados. |
| **Critérios de Aplicação** | Serviços com múltiplos consumidores, especialmente aqueles geridos por diferentes equipes. |
| **Critérios de Não Aplicação** | Serviços internos com um único consumidor (ex: módulo interno). |
| **Pré-condições** | Contrato especificado (OpenAPI/Proto). |
| **Pós-condições** | Pipeline do provedor inclui testes de contrato dos consumidores. |
| **Restrições** | Se um teste de contrato falhar, o provedor não pode ser implantado até que o problema seja resolvido (ou o consumidor seja notificado). |
| **Dependências** | REGARCH-SW-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Novo endpoint `/v2/classify` adicionado. Teste de contrato do consumidor 'Laudos' passou. Deploy permitido." |
| **Exemplo Negativo** | "Mudança na API quebrou o consumidor 'Laudos', mas ninguém percebeu porque não havia testes de contrato." |
| **Anti-pattern** | Testar contrato apenas no lado do consumidor, sem validação no provedor. |
| **Métrica** | Percentual de serviços com testes de contrato implementados. |
| **Critérios de Auditoria** | Verificar pipelines de serviços para presença de testes de contrato. |

---

### REGQUAL-009 – Testes de Performance Regulares (Carga, Estresse, Pico)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-009 |
| **Nome** | Testes de Performance Regulares (Carga, Estresse, Pico) |
| **Descrição** | O agente deve recomendar e, se possível, automatizar a execução de testes de performance regulares (ex: mensais ou a cada release importante). Os testes devem incluir: (1) **Teste de Carga**: validar desempenho sob carga normal; (2) **Teste de Estresse**: validar desempenho sob carga extrema (bottlenecks); (3) **Teste de Pico**: validar recuperação após pico de tráfego. Os resultados devem ser comparados com os critérios SMART definidos nos RTs (REGREQ-005). |
| **Objetivo** | Garantir que o sistema atenda aos requisitos de performance em produção e que a degradação seja detectada precocemente. |
| **Motivação** | Cap. 8.2.1 (visões de performance), Cap. 8.2.4 (análise quantitativa). |
| **Justificativa** | Requisitos de performance só podem ser validados com testes de carga reais. Testes unitários não capturam gargalos de produção. |
| **Critérios de Aplicação** | Sistemas com RTs de performance definidos. |
| **Critérios de Não Aplicação** | Aplicações de baixa criticidade sem requisitos de performance explícitos. |
| **Pré-condições** | Ambiente de staging semelhante ao de produção. |
| **Pós-condições** | Relatório de performance gerado e arquivado. |
| **Restrições** | Se os testes falharem (ex: tempo de resposta > RT), a release deve ser bloqueada e o problema deve ser investigado. |
| **Dependências** | REGREQ-005, REGQUAL-001. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Teste de carga: 600k requisições/mês, tempo de resposta médio 450ms (RT: 500ms). Aprovado." |
| **Exemplo Negativo** | "Não realizamos testes de performance; esperamos que funcione." |
| **Anti-pattern** | Realizar testes de performance em produção, sem plano de rollback. |
| **Métrica** | Percentual de releases com testes de performance executados. |
| **Critérios de Auditoria** | Revisar relatórios de performance para cada release major/minor. |
