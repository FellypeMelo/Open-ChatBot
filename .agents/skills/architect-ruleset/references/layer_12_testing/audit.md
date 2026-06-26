# Seção 8 – Critérios de Auditoria, Exemplo e Evolução (Layer 12 - Testes e Garantia de Qualidade)

**ID:** ARCH-RULESET-L12-TEST-AUDIT  
**Status:** Definitivo  
**Escopo:** Métodos de verificação de qualidade de software, caso prático integrado de aplicação (e-commerce) e direções de evolução e extensibilidade.

---

## 1. Matriz de Auditoria de Testes e Garantia de Qualidade

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| **AUD-TEST-01** | Cobertura de testes ≥ 80% (REGTEST-001). | Revisar relatórios de cobertura do pipeline de CI (JaCoCo, Coverage.py, etc.) para assegurar cobertura mínima de 80% em linhas/branches. |
| **AUD-TEST-02** | Testes de integração para dependências externas (REGTEST-002). | Verificar a presença de suítes de testes de integração automatizados simulando falhas, timeouts e contratos de dependências reais (ex: banco de dados, APIs). |
| **AUD-TEST-03** | TDD aplicado em novas funcionalidades (REGTEST-003). | Validar o histórico de commits no Git para comprovar a gravação de arquivos de testes antes do código-fonte correspondente. |
| **AUD-TEST-04** | Testes de liberação baseados em requisitos (REGTEST-004). | Analisar a matriz de rastreabilidade para certificar que todos os requisitos funcionais e não-funcionais possuem casos de teste ou cenários validados. |
| **AUD-TEST-05** | Testes de performance executados (REGTEST-005). | Revisar relatórios das ferramentas de teste de carga (k6, JMeter) para releases contendo RTs de performance ativos. |
| **AUD-TEST-06** | Envolvimento do usuário em testes alfa/beta (REGTEST-006). | Verificar os registros de homologação, feedbacks recebidos de usuários reais e se as correções foram integradas na fila antes da release final. |
| **AUD-TEST-07** | Critérios objetivos para testes de aceitação (REGTEST-007). | Revisar o termo ou plano de aceitação assinado com o cliente, validando critérios mensuráveis predefinidos. |
| **AUD-TEST-08** | PRs com revisão aprovada (REGTEST-008). | Auditar o histórico do GitHub/GitLab para garantir que nenhum merge ocorreu na branch master/main sem aprovação de ao menos um par. |
| **AUD-TEST-09** | Checklist de revisão preenchido (REGTEST-009). | Verificar se os comentários da PR ou templates de revisão contêm o preenchimento formal dos itens do checklist de qualidade. |
| **AUD-TEST-10** | Métricas de qualidade monitoradas (REGTEST-010). | Acessar o dashboard de análise estática (SonarQube) e atestar que a complexidade ciclomática média e limite individual (< 10) estão em conformidade. |
| **AUD-TEST-11** | Conformidade com ISO 9001 (REGTEST-011). | Auditar os registros de processos de qualidade e a rastreabilidade geral no repositório de documentação do SGQ organizacional. |

---

## 2. Exemplo Integrado de Aplicação

**Cenário**: O time está desenvolvendo um sistema de e-commerce e precisa garantir a qualidade antes do lançamento.

**Aplicação das Regras**:

1. **REGTEST-001 (Cobertura)**: O agente executa ferramentas de cobertura estática no pipeline e verifica que a cobertura de testes unitários da nova API de carrinho está em 85% (≥ 80%). O build segue para a próxima fase.

2. **REGTEST-002 (Integração)**: O sistema de compras depende de um gateway de pagamento de terceiros. O agente verifica que há testes de integração usando *WireMock* para simular cenários de timeout, recusa de cartão de crédito e instabilidade do serviço externo.

3. **REGTEST-003 (TDD)**: No desenvolvimento da funcionalidade de cálculo de desconto progressivo, o agente garante que o desenvolvedor escreveu os testes que cobrem as condições de limite antes de criar a lógica da classe `DiscountCalculator`.

4. **REGTEST-004 (Liberação)**: O agente gera a matriz de rastreabilidade ligando os requisitos funcionais aos testes de liberação executados pela equipe de QA, cobrindo o fluxo completo de compra e cenários realistas de desistência.

5. **REGTEST-005 (Performance)**: Com o requisito de que o checkout não leve mais de 500ms sob carga, o agente roda uma simulação com a ferramenta `k6` injetando 500 usuários simultâneos (teste de estresse). A latência média permaneceu em 320ms, atendendo ao RT.

6. **REGTEST-006 (Alfa/Beta)**: Planeja e executa um teste alfa com 5 colaboradores de outras áreas da empresa. Em seguida, libera uma versão beta pública com 50 clientes preferenciais para validar a usabilidade do novo checkout em produção.

7. **REGTEST-007 (Aceitação)**: Assina um plano de aceitação formal com os gerentes de produto, estipulando que o produto só seria aprovado se não houvesse bugs impeditivos e a performance estivesse validada.

8. **REGTEST-008 & REGTEST-009 (Revisão)**: Toda a alteração de código da feature de e-commerce é bloqueada para commit direto. Uma PR é aberta e revisada por um engenheiro sênior, utilizando o checklist formal (segurança de dados do cartão de crédito, injeção de dependência, etc.) anexado nos comentários da PR.

9. **REGTEST-010 (Métricas)**: O agente avalia a complexidade ciclomática no SonarQube. Uma função de validação de cupons exibe complexidade de 14. O agente aponta o problema e força uma refatoração do código para quebrar a função em 3 sub-métodos de menor complexidade.

10. **REGTEST-011 (ISO 9001)**: O time gera logs de alteração e documenta todas as etapas do ciclo de testes em conformidade com as diretrizes do sistema de gestão da qualidade da empresa.

**Saída Final (resumida)**:
> "Estratégia de testes e qualidade definida para o sistema de e-commerce. Cobertura de 85% nos testes de unidade, testes de integração com gateway, TDD implementado para descontos, testes de liberação e performance executados com k6, testes alfa/beta planejados, critérios de aceitação definidos. Revisões de código com checklist e métricas monitoradas via SonarQube para manter complexidade < 10. Qualidade garantida para o lançamento."

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido com sub-módulos especializados:
- **Módulo 13-A**: Testes de Segurança Avançados (OWASP, DAST, SAST, pentest).
- **Módulo 13-B**: Testes em Sistemas Distribuídos e Microsserviços (testes de contrato, chaos engineering).
- **Módulo 13-C**: Qualidade de Dados (validação de esquemas, linhagem, integridade de dados analíticos).
- **Módulo 13-D**: Testes de Acessibilidade e Usabilidade (WCAG, testes heurísticos).

Todas as extensões devem respeitar as regras base e a Constituição.
