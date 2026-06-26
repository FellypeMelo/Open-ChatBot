# Quality Gate & UML Maturity Scorecard

## Quality Gates (QG-01 to QG-08)

| ID | Check | Criterion |
|----|-------|-----------|
| QG-01 | **Canonical Naming** | The same concept has the same name across all diagrams |
| QG-02 | **Requirement Traceability** | Every element has `{req: RF-XXX}` or a written justification |
| QG-03 | **Unique IDs** | No duplicate EID (Element Identifier) |
| QG-04 | **Versioning** | Diagram has version, date, and author in header |
| QG-05 | **Declared Purpose** | Diagram has a `<<purpose>>` note with audience and answered question |
| QG-06 | **Static-Dynamic Consistency** | Sequence messages exist as methods in class diagram |
| QG-07 | **Use Case Coverage** | Every use case has at least one sequence diagram |
| QG-08 | **Deployment Consistency** | Every component appears as an artifact in some deployment node |

---

## Acceptance Criteria by Diagram Type

| Diagram | Gold-Level Minimum Criteria |
|---------|----------------------------|
| Use Case | Correct name format; all actors mapped; ≥ 3 use cases; req traceability; attached specs |
| Sequence | Header with ID and scenario; sync/async messages; `alt`/`loop` fragments; ≤ 8 lifelines; method traceability |
| Activity | Initial node; decisions with guards; swimlanes when > 1 responsible; verb+object actions; no dead paths |
| Class | Attribute/method visibility; relationships with multiplicity; inheritance/realization; OCL invariants; arch stereotypes |
| Component | Provided/required interfaces; use case traceability; class diagram consistency |
| Deployment | Nodes with properties; artifacts mapped to components; connections with protocols; env separation |
| State | Initial/final states; event-guarded transitions; full event coverage; class link |

---

## Maturity Scorecard — Scoring Guide

### Scoring
For each of the 108 rules (UC1–11, SQ1–12, AC1–13, CL1–15, COMP1–10, DP1–10, ST1–11, QG1–8, MR1–4, plus header/naming/skinparam rules):

| Score | Meaning |
|-------|---------|
| 1.0 | Rule fully satisfied |
| 0.5 | Rule partially satisfied |
| 0.0 | Rule not satisfied |

**Maximum: 108 points**

### Interpretation

| Score | Level | Action |
|-------|-------|--------|
| 108 | **Platinum** | Deliver directly to dev team |
| 95–107 | **Gold** | Fix non-conformant items, then deliver |
| 80–94 | **Silver** | Review required before coding |
| < 80 | **Bronze** | Rework the model — significant inconsistency risk |

---

## Self-Audit Template

When completing a diagram, the agent must report:

```
## UML Scorecard – [Diagram Name]

| Rule Group | Score | Notes |
|------------|-------|-------|
| MR (Meta-Rules) 4/4 | 4.0 | All satisfied |
| UC (Use Case) 11/11 | 10.5 | UC6 partial: spec in note only |
| SQ (Sequence) 12/12 | 12.0 | All satisfied |
| CL (Class) 15/15 | 14.5 | CL12 partial: 1 method untraceable |
| QG (Quality Gates) 8/8 | 7.5 | QG-07 partial: UC-03 missing sequence |
| **TOTAL** | **94.5 / 108** | **Level: Silver** |

### Action Items
- [ ] UC6: Generate full specification document for UC-01.
- [ ] CL12: Add `validarEstoque()` to a sequence diagram.
- [ ] QG-07: Create `sq_UC03_consultar-cliente.puml`.
```
