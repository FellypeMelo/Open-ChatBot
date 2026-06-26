# Seção 8 – Auditoria, Exemplo Integrado e Evolução / Layer 8 (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-AUDIT-EXAMPLE  
**Status:** Definitivo  
**Escopo:** Métodos de auditoria para avaliação de riscos, caso prático de trade-off de persistência clínica e evolução metodológica.

---

## 1. Critérios de Auditoria de Riscos e Decisão

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-RISK-01 | Riscos mapeados e identificados para decisões de arquitetura (REGRISK-001). | Revisar ADRs de alto impacto e o Risk Register. |
| AUD-RISK-02 | Riscos classificados em categorias formais (REGRISK-002). | Validar metadados de categoria no Risk Register. |
| AUD-RISK-03 | Matriz de probabilidade x impacto (1-5) devidamente preenchida (REGRISK-003). | Validar pontuações de severidade. |
| AUD-RISK-04 | Análise quantitativa executada para riscos críticos (REGRISK-004). | Buscar relatórios FAIR ou cálculos de EMV anexados. |
| AUD-RISK-05 | Riscos ordenados sob ranking consolidado de prioridades (REGRISK-005). | Inspecionar a ordenação do portfólio de riscos. |
| AUD-RISK-06 | Planos de mitigação formais com ações de contingência (REGRISK-006). | Validar planos estruturados para riscos Críticos/Altos. |
| AUD-RISK-07 | Estratégia de mitigação explicitada e custo-benefício justificado (REGRISK-007). | Revisar rationale das estratégias (Mitigar, Evitar, Aceitar, Transferir). |
| AUD-RISK-08 | Risk Owner individualizado ou time responsável designado (REGRISK-008). | Confirmar proprietários atribuídos no registro de riscos. |
| AUD-RISK-09 | Revisão recorrente periódica trimestral dos riscos (REGRISK-009). | Verificar datas de atualização e logs de revisão do Risk Register. |
| AUD-RISK-10 | KRIs com limites alertas ativos no sistema de monitoramento (REGRISK-010). | Verificar triggers de KRIs em Prometheus/CloudWatch. |
| AUD-RISK-11 | Rationale documentado pesando trade-off risco x benefício (REGRISK-011). | Inspecionar a seção de alternativas em ADRs de alto impacto. |
| AUD-RISK-12 | Seção de riscos integrada e atualizada em documentos de decisões (REGRISK-012). | Confirmar a estrutura de riscos nos ADRs. |

---

## 2. Exemplo Integrado de Aplicação do Módulo 09

**Cenário:** O time propõe migrar a persistência dos Bounded Contexts de variantes e prontuários para CockroachDB para fins de alta escalabilidade. O agente avalia e gerencia os riscos técnicos e de negócio correspondentes.

**Aplicação das Regras Passo a Passo:**

1. **REGRISK-001 & REGRISK-002 (Identificação e Classificação):**
   - Mapeia-se os seguintes riscos principais:
     - `R-001 (Técnico):` Incompatibilidade de queries com o ORM Gorm.
     - `R-002 (Operacional):` Curva de aprendizado da equipe no tuning do CockroachDB.
     - `R-003 (Técnico/Operacional):` Degradação de performance em queries multi-tenant complexas.
     - `R-004 (Financeiro):` Aumento de custos de infraestrutura em nuvem.

2. **REGRISK-003 & REGRISK-004 (Matriz de Severidade e FAIR):**
   - Atribuição qualitativa:
     - `R-001:` Probabilidade = 3, Impacto = 4 → Risk Score = 12 (Alto).
     - `R-003:` Probabilidade = 3, Impacto = 3 → Risk Score = 9 (Médio).
   - Análise quantitativa FAIR executada para `R-001`: Estimou-se 25% de probabilidade de materialização anual, com impacto financeiro médio de R$ 500k em correção de código (Expected Loss de R$ 125k).

3. **REGRISK-005, REGRISK-006 & REGRISK-007 (Mitigação, Justificativa e Donos):**
   - R-001 (Alto) -> Estratégia: Mitigar. Ação: Escrever uma camada de testes automatizados de compatibilidade SQL no CI antes da liberação do deploy.
   - R-002 (Médio) -> Estratégia: Mitigar. Ação: Promover treinamento prático de 2 semanas sobre o CockroachDB. Custo de R$ 20k, justificado contra o risco de atraso em produção avaliado em R$ 100k.
   - Designa-se o time de Genômica (Gabriel) como Risk Owner para `R-001` e `R-003`.

4. **REGRISK-009 & REGRISK-010 (Revisão e Monitoramento):**
   - Define-se um KRI para `R-003` (Performance): `Latência de leitura P95 > 250ms`. Threshold disparará alerta no canal de emergência do Slack se mantido por > 2 minutos.
   - Agenda-se revisão automática dos scores de riscos para a próxima sprint de planejamento.

5. **REGRISK-011 & REGRISK-012 (Trade-off de Decisão e ADR):**
   - O agente documenta no `0002-use-postgresql-for-tenants.md` (ADR):
     - **Benefícios:** Suporte a transações ACID distribuídas, isolamento transparente de tenants, zero dependência de replicação lógica customizada.
     - **Riscos:** Compatibilidade do ORM e curva de aprendizado. Ambos mitigados conforme planos técnicos documentados.
     - **Trade-off:** Risco total aceitável frente ao ganho de conformidade multi-tenant exigido pela ANPD.

---

## 3. Evolução e Extensibilidade

Este módulo de riscos pode ser estendido com:
* **Módulo 09-A (Security Threat Score):** Modelagem com STRIDE/DREAD para atribuição matemática de criticidade de vulnerabilidades de infraestrutura.
* **Módulo 09-B (FinOps Architecture):** Cálculo automatizado de custo total de propriedade (TCO) integrado ao pipeline de infraestrutura como código (Terraform cost estimation).
* **Módulo 09-C (Audit Compliance):** Rastreamento de gaps regulatórios em auditorias de certificação médica.
