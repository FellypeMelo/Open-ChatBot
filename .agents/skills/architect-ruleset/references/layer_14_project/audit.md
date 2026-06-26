# Layer 14 — Auditoria, Exemplo Prático e Evolução

**Módulo:** ARCH-RULESET-MOD-15 | **Camada:** Layer 14 – Project Management & Planning

---

## Tabela de Auditoria — Critérios de Conformidade (REGPM-001 a REGPM-012)

| ID | Critério | Evidência Esperada | Status |
|----|---------|--------------------|--------|
| REGPM-001 | Risco identificado com técnica formal (brainstorming ou checklist) | Tabela de riscos presente no plano de projeto | [ ] |
| REGPM-002 | Riscos classificados em produto/projeto/negócio | Campo "tipo" na tabela de riscos | [ ] |
| REGPM-003 | Matriz probabilidade × impacto aplicada | Score quantificado por risco | [ ] |
| REGPM-004 | Plano de mitigação com dono e prazo definidos | Coluna "responsável" e "deadline" na tabela | [ ] |
| REGPM-005 | KRIs definidos para monitoramento contínuo | Seção de KRIs no plano ou dashboard | [ ] |
| REGPM-006 | Equipe composta com personalidades complementares | Mapeamento de papéis: tarefa / self / interação | [ ] |
| REGPM-007 | Estratégia motivacional baseada na pirâmide de Maslow | Registro de atividades de coesão / 1-on-1s | [ ] |
| REGPM-008 | Escopo, marcos e entregáveis documentados | Documento de plano formal ou backlog priorizado | [ ] |
| REGPM-009 | Estimativa realizada com COCOMO II ou story points | Planilha ou ferramenta de estimativa referenciada | [ ] |
| REGPM-010 | Velocity medida e atualizada a cada sprint | Gráfico de velocity ou tabela no board ágil | [ ] |
| REGPM-011 | Diagrama de Gantt criado e mantido dinamicamente | Arquivo de cronograma (Gantt) atualizado | [ ] |
| REGPM-012 | Caminho crítico determinado via PERT e monitorado | Diagrama PERT com caminho crítico destacado | [ ] |

---

## Exemplo Prático Integrado

### Cenário: Planejamento de Módulo de Autenticação JWT (VarSuS — Fase 2)

**Contexto:** Sprint 1 da Fase 2 (Autenticação & RBAC). Equipe de 3 desenvolvedores, 1 QA, 1 Scrum Master. Prazo: 2 semanas.

#### Passo 1 — Identificação de Riscos (REGPM-001 / REGPM-002)

| # | Risco | Tipo | Probabilidade | Impacto |
|---|-------|------|--------------|---------|
| R01 | Biblioteca JWT descontinuada | Produto | Baixa | Alto |
| R02 | Atraso na definição de RBAC com o cliente | Projeto | Média | Alto |
| R03 | Mudança de requisito de LGPD em produção | Negócio | Baixa | Crítico |

#### Passo 2 — Plano de Mitigação (REGPM-004)

| # | Estratégia | Responsável | Deadline |
|---|-----------|-------------|---------|
| R01 | Fixar versão major no `go.mod` + monitorar releases | Gabriel | Sprint 1, Dia 1 |
| R02 | Workshop de 2h com Product Owner antes do Sprint | Fellype | Pré-Sprint |
| R03 | Revisão do DPO antes do deploy em produção | Carlos (QA) | Pré-Release |

#### Passo 3 — Estimativa (REGPM-009 / REGPM-010)

- **Story Points por história:**
  - `[AUTH-01]` Endpoint de Login: **5 pts**
  - `[AUTH-02]` Middleware JWT: **3 pts**
  - `[AUTH-03]` RBAC de rotas: **8 pts**
  - `[AUTH-04]` Testes de integração: **5 pts**
- **Velocity histórica (Sprint 0):** 18 pts
- **Capacidade Sprint 1:** 21 pts → histórias selecionadas: 21 pts ✓

#### Passo 4 — Cronograma (REGPM-011)

```
Dia 1-2   : [AUTH-01] Endpoint de Login
Dia 3-4   : [AUTH-02] Middleware JWT
Dia 5-8   : [AUTH-03] RBAC de rotas  <-- Caminho Crítico
Dia 9-10  : [AUTH-04] Testes + Code Review
```

> **Caminho Crítico:** `AUTH-03` possui folga zero. Qualquer atraso impacta diretamente a entrega do Sprint.

---

## Direções de Evolução do Módulo

| Versão Futura | Adição Planejada |
|--------------|-----------------|
| 1.1 | Integração com ferramentas de rastreamento (Jira, Linear) via IDs em regras |
| 1.2 | Regras para EVM (Earned Value Management) e CPI/SPI |
| 1.3 | Templates de OKRs ligados aos marcos do plano de projeto |
| 2.0 | Extensão para gerenciamento multi-time (SAFe / LeSS) quando aprovado pelo Navegador |

---

*Gerado conforme Módulo 15 (ARCH-RULESET-MOD-15) — baseado em Sommerville, "Software Engineering", 9ª ed., Caps. 22-23.*
