# Seção 8 – Auditoria, Exemplo Integrado e Evolução / Layer 4 (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-AUDIT-EXAMPLE  
**Status:** Definitivo  
**Escopo:** Métodos de validação de auditoria, caso de uso prático e evolução da Layer 4.

---

## 1. Critérios de Auditoria da Qualidade

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-QUAL-01 | RTs de qualidade classificados na ISO 25010 (REGQUAL-001). | Revisar todos os RTs. |
| AUD-QUAL-02 | Métricas de manutenibilidade verificadas no CI (REGQUAL-002). | Verificar relatórios da ferramenta de análise estática. |
| AUD-QUAL-03 | Revisão de arquitetura documentada para mudanças estruturais (REGQUAL-003). | Revisar atas do Comitê de Arquitetura. |
| AUD-QUAL-04 | PRs com aprovação mínima de 1 revisor (REGQUAL-004). | Revisar histórico do Git/PRs. |
| AUD-QUAL-05 | Checklist de revisão preenchido (REGQUAL-005). | Verificar documentação associada a cada Pull Request. |
| AUD-QUAL-06 | Cobertura de testes ≥ 80% (REGQUAL-006). | Relatórios de testes gerados na esteira do CI. |
| AUD-QUAL-07 | Testes de integração existentes para dependências externas (REGQUAL-007). | Revisar a suíte de testes de persistência/redes. |
| AUD-QUAL-08 | Testes de contrato para serviços com múltiplos consumidores (REGQUAL-008). | Verificar pipelines de publicação. |
| AUD-QUAL-09 | Testes de performance executados regularmente (REGQUAL-009). | Revisar relatórios históricos de testes de carga. |
| AUD-QUAL-10 | Quality gates no pipeline (REGQUAL-010). | Inspecionar configurações do runner do pipeline. |
| AUD-QUAL-11 | Defeitos registrados e rastreados (REGQUAL-011). | Auditar o board de issues (verificando links para commits e requisitos). |
| AUD-QUAL-12 | Dívida técnica rastreada e priorizada (REGQUAL-012). | Revisar o backlog de refatoração do produto. |

---

## 2. Exemplo Integrado de Aplicação do Módulo 05

**Cenário:** O agente está revisando uma PR que adiciona um novo microsserviço de classificação de variantes baseado em ACMG.

**Raciocínio Aplicado Passo a Passo:**
1. **REGQUAL-004 (Revisão de Código):** Bloqueia o merge pois a PR foi submetida pelo autor sem revisores assinalados.
2. **REGQUAL-005 (Checklist):** Ao inspecionar o código enviado:
   * Constata-se que o tratamento de exceção está vazio (violação da REGCON-004).
   * Não há documentação das chamadas de banco no README.
3. **REGQUAL-006 (Cobertura):** O agente constata que a cobertura de testes é de 62%. Bloqueia no Quality Gate.
4. **REGQUAL-007 (Testes de Integração):** O serviço utiliza Redis para filas e Postgres para histórico. O agente constata que há testes com mocks, mas não com integração real. Exige `testcontainers`.
5. **REGQUAL-010 (Quality Gates):** O CI/CD falha porque a análise estática detectou complexidade ciclomática = 14 em uma das rotas.
6. **REGQUAL-012 (Dívida Técnica):** O agente aprova a PR condicionalmente após a resolução da complexidade e dos testes de integração, mas cadastra uma dívida técnica com prioridade Média para atualizar o driver do banco em iteração futura.

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido com submódulos focados em:
* **Módulo 05-A (Data Quality):** Validação de integridade semântica de bases de dados clínicas (seeds).
* **Módulo 05-B (Security Quality Gates):** Inclusão de testes SAST/DAST integrados (OWASP ASVS, Gosec, Gitleaks).
* **Módulo 05-C (Observability Quality):** Verificação de cobertura de spans e instrumentação de telemetria.
