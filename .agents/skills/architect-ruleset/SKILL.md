---
name: architect-ruleset
description: Permanent ruleset and decision engine enforcing senior software architecture, logical reasoning, and international engineering standards.
---
# Architect Ruleset — AI Agent Specification

This ruleset serves as the permanent decision engine ("Constitution" + "Rules Engine") for AI agents, establishing rigorous principles, reasoning paradigms, quality gates, and compliance protocols.

---

## 🧭 Semantic Task Router

When you are assigned a task, use this routing table to read only the most relevant sub-files immediately. Do not read the entire ruleset to conserve context.

| Task Concern | Key Layers to Read | Primary Sub-Files |
| :--- | :--- | :--- |
| **Requirements Validation** | Layer 0, Layer 3 | [regcon.md](./references/layer_0_constitution/regcon.md), [priorities.md](./references/layer_0_constitution/priorities.md), [req_spec.md](./references/layer_3_requirements/req_spec.md) |
| **Code Implementation** | Layer 3 (Architecture), Layer 4, Layer 5 | [arch_model.md](./references/layer_3_architecture/arch_model.md), [qual_std.md](./references/layer_4_quality/qual_std.md), [lgpd_rules.md](./references/layer_5_compliance/lgpd_rules.md) |
| **Testing & Quality Assurance** | Layer 4 | [qual_test.md](./references/layer_4_quality/qual_test.md), [qual_gates.md](./references/layer_4_quality/qual_gates.md) |
| **Security & Cryptography** | Layer 5 | [sec_access.md](./references/layer_5_compliance/sec_access.md), [sec_crypto.md](./references/layer_5_compliance/sec_crypto.md), [sec_threat.md](./references/layer_5_compliance/sec_threat.md) |
| **ADR & Documentation** | Layer 6 | [doc_struct.md](./references/layer_6_documentation/doc_struct.md), [doc_readability.md](./references/layer_6_documentation/doc_readability.md) |
| **Change Management & Design Choices** | Layer 7, Layer 8 | [gov_change.md](./references/layer_7_governance/gov_change.md), [risk_decision.md](./references/layer_8_risk/risk_decision.md) |
| **Response & Relatórios Formais** | Layer 9 | [out_strc.md](./references/layer_9_output/out_strc.md), [out_exec.md](./references/layer_9_output/out_exec.md) |
| **Software Process & Agile Methods** | Layer 10 | [principles.md](./references/layer_10_process/principles.md), [proc_select.md](./references/layer_10_process/proc_select.md), [proc_agile_scrum.md](./references/layer_10_process/proc_agile_scrum.md) |
| **System Modeling & OO Design** | Layer 11 | [principles.md](./references/layer_11_modeling/principles.md), [model_objects.md](./references/layer_11_modeling/model_objects.md), [model_structural.md](./references/layer_11_modeling/model_structural.md) |
| **Testing & Quality Assurance (Process)** | Layer 12 | [principles.md](./references/layer_12_testing/principles.md), [test_dev.md](./references/layer_12_testing/test_dev.md), [test_metrics.md](./references/layer_12_testing/test_metrics.md) |
| **Software Evolution & Configuration** | Layer 13 | [principles.md](./references/layer_13_evolution/principles.md), [evol_maint.md](./references/layer_13_evolution/evol_maint.md), [evol_cm.md](./references/layer_13_evolution/evol_cm.md) |
| **Project Management & Planning** | Layer 14 | [principles.md](./references/layer_14_project/principles.md), [pm_risk.md](./references/layer_14_project/pm_risk.md), [pm_planning.md](./references/layer_14_project/pm_planning.md) |

---

## 🗂️ Layer Hierarchy Index

- **Layer 0 – Constitution**: Detailed in [layer_0_constitution.md](./references/layer_0_constitution.md).
- **Layer 1 & 2 – Core Rules & Reasoning**: Detailed in [layer_1_2_reasoning.md](./references/layer_1_2_reasoning.md).
- **Layer 3 (Part 1) – Engineering Rules (Requirements)**: Detailed in [layer_3_requirements.md](./references/layer_3_requirements.md).
- **Layer 3 (Part 2) – Engineering Rules (Architecture)**: Detailed in [layer_3_architecture.md](./references/layer_3_architecture.md).
- **Layer 4 – Quality Rules**: Detailed in [layer_4_quality.md](./references/layer_4_quality.md).
- **Layer 5 – Compliance Rules**: Detailed in [layer_5_compliance.md](./references/layer_5_compliance.md).
- **Layer 6 – Documentation Rules**: Detailed in [layer_6_documentation.md](./references/layer_6_documentation.md).
- **Layer 7 – Governance Rules**: Detailed in [layer_7_governance.md](./references/layer_7_governance.md).
- **Layer 8 – Risk & Decision Rules**: Detailed in [layer_8_risk.md](./references/layer_8_risk.md).
- **Layer 9 – Output Rules**: Detailed in [layer_9_output.md](./references/layer_9_output.md).
- **Layer 10 – Process & Lifecycle Rules**: Detailed in [layer_10_process.md](./references/layer_10_process.md).
- **Layer 11 – Modeling & Design Rules**: Detailed in [layer_11_modeling.md](./references/layer_11_modeling.md).
- **Layer 12 – Testing & Quality Assurance Rules**: Detailed in [layer_12_testing.md](./references/layer_12_testing.md).
- **Layer 13 – Evolution & Configuration Management Rules**: Detailed in [layer_13_evolution.md](./references/layer_13_evolution.md).
- **Layer 14 – Project Management & Planning Rules**: Detailed in [layer_14_project.md](./references/layer_14_project.md).

---

## 🗺️ Ruleset Navigation Map

Directly locate any operational Rule ID within its granular source file:

### Layer 0 - Constitution
- `REGCON-001` to `REGCON-003` -> [regcon.md](./references/layer_0_constitution/regcon.md) (Philosophy & Rules Authority)
- `REGCON-004` to `REGCON-006` -> [priorities.md](./references/layer_0_constitution/priorities.md) (Hierarchy of Concerns)
- `REGCON-007` to `REGCON-009` -> [evolution.md](./references/layer_0_constitution/evolution.md) (Ruleset Evolution Model)
- `REGCON-010` to `REGCON-012` -> [ethics.md](./references/layer_0_constitution/ethics.md) (Engineering Ethics)

### Layers 1 & 2 - Core & Reasoning
- `REGCORE-001` to `REGCORE-003` -> [regcore.md](./references/layer_1_2_reasoning/regcore.md) (Operational Laws & Tool Execution)
- `REGRSN-001` to `REGRSN-003` -> [regrsn.md](./references/layer_1_2_reasoning/regrsn.md) (Deductive & Inductive Reasoning)
- `REGRSN-004` to `REGRSN-006` -> [metacognition.md](./references/layer_1_2_reasoning/metacognition.md) (Metacognitive Audit Controls)

### Layer 3 - Engineering (Requirements)
- `REGREQ-001` to `REGREQ-003` -> [req_elicit.md](./references/layer_3_requirements/req_elicit.md) (Requirements Elicitation)
- `REGREQ-004` to `REGREQ-006` -> [req_spec.md](./references/layer_3_requirements/req_spec.md) (Specification Standards)
- `REGREQ-007` to `REGREQ-008` -> [req_valid.md](./references/layer_3_requirements/req_valid.md) (Validation Protocols)
- `REGREQ-009` to `REGREQ-011` -> [req_trace.md](./references/layer_3_requirements/req_trace.md) (Bidirectional Traceability)

### Layer 3 - Engineering (Architecture)
- `REGARCH-SW-001` to `REGARCH-SW-003` -> [arch_model.md](./references/layer_3_architecture/arch_model.md) (Design Patterns, Clean & DDD)
- `REGARCH-SW-004` to `REGARCH-SW-006` -> [arch_int.md](./references/layer_3_architecture/arch_int.md) (Integration & Contracts)
- `REGARCH-SW-007` to `REGARCH-SW-009` -> [arch_impact.md](./references/layer_3_architecture/arch_impact.md) (Impact Analysis)
- `REGARCH-SW-010` to `REGARCH-SW-012` -> [arch_trace.md](./references/layer_3_architecture/arch_trace.md) (Code Mapping)
- `REGARCH-SW-013` to `REGARCH-SW-015` -> [arch_gov.md](./references/layer_3_architecture/arch_gov.md) (Architecture Governance)

### Layer 4 - Quality
- `REGQUAL-001` to `REGQUAL-002` -> [qual_std.md](./references/layer_4_quality/qual_std.md) (ISO 25010 & Metrics limits)
- `REGQUAL-003` to `REGQUAL-005` -> [qual_review.md](./references/layer_4_quality/qual_review.md) (Independent Reviews)
- `REGQUAL-006` to `REGQUAL-009` -> [qual_test.md](./references/layer_4_quality/qual_test.md) (Testing Suites)
- `REGQUAL-010` to `REGQUAL-011` -> [qual_gates.md](./references/layer_4_quality/qual_gates.md) (CI/CD Gates)
- `REGQUAL-012` -> [qual_debt.md](./references/layer_4_quality/qual_debt.md) (Technical Debt)

### Layer 5 - Compliance & Security
- `REGSEC-001` to `REGSEC-002` -> [sec_class.md](./references/layer_5_compliance/sec_class.md) (Classification & Inventory)
- `REGSEC-003` to `REGSEC-004` -> [sec_access.md](./references/layer_5_compliance/sec_access.md) (IAM & MFA)
- `REGSEC-005` to `REGSEC-006` -> [sec_crypto.md](./references/layer_5_compliance/sec_crypto.md) (Ciphers & KMS)
- `REGLGPD-001` to `REGLGPD-004` -> [lgpd_rules.md](./references/layer_5_compliance/lgpd_rules.md) (Brazilian Data Privacy)
- `REGSEC-007` & `REGSEC-011` -> [sec_threat.md](./references/layer_5_compliance/sec_threat.md) (STRIDE & Vulnerabilities)
- `REGSEC-008` to `REGSEC-009` -> [sec_audit.md](./references/layer_5_compliance/sec_audit.md) (Immutable logs & SIEM)
- `REGSEC-010` -> [sec_ir.md](./references/layer_5_compliance/sec_ir.md) (Incident Playbook)

### Layer 6 - Documentation
- `REGDOC-001` to `REGDOC-003` -> [doc_struct.md](./references/layer_6_documentation/doc_struct.md) (ARC42, ADR & README)
- `REGDOC-004` to `REGDOC-006` -> [doc_readability.md](./references/layer_6_documentation/doc_readability.md) (Grice, Miller & Gestalt)
- `REGDOC-007` to `REGDOC-008` -> [doc_view.md](./references/layer_6_documentation/doc_view.md) (Viewpoints & Views)
- `REGDOC-009` to `REGDOC-010` -> [doc_trace.md](./references/layer_6_documentation/doc_trace.md) (Docs Traceability)
- `REGDOC-011` to `REGDOC-012` -> [doc_comm.md](./references/layer_6_documentation/doc_comm.md) (Conversational alignment)

### Layer 7 - Governance
- `REGGOV-001` to `REGGOV-002` -> [gov_roles.md](./references/layer_7_governance/gov_roles.md) (Matriz RACI & Comitê)
- `REGGOV-003` to `REGGOV-005` -> [gov_align.md](./references/layer_7_governance/gov_align.md) (Conway's Law, FMO & Global)
- `REGGOV-006` to `REGGOV-007` -> [gov_change.md](./references/layer_7_governance/gov_change.md) (CR & Impact analysis)
- `REGGOV-008` to `REGGOV-009` -> [gov_lifecycle.md](./references/layer_7_governance/gov_lifecycle.md) (Lifecycle states & Sunset)
- `REGGOV-010` -> [gov_escalate.md](./references/layer_7_governance/gov_escalate.md) (Technical Escalations)

### Layer 8 - Risks
- `REGRISK-001` to `REGRISK-002` -> [risk_id.md](./references/layer_8_risk/risk_id.md) (Ameaças & Vulnerabilidades)
- `REGRISK-003` to `REGRISK-005` -> [risk_eval.md](./references/layer_8_risk/risk_eval.md) (Probabilidade, Impacto & FAIR)
- `REGRISK-006` to `REGRISK-008` -> [risk_mitigate.md](./references/layer_8_risk/risk_mitigate.md) (Plano de Mitigação & Owners)
- `REGRISK-009` to `REGRISK-010` -> [risk_monitor.md](./references/layer_8_risk/risk_monitor.md) (Revisões & KRIs)
- `REGRISK-011` to `REGRISK-012` -> [risk_decision.md](./references/layer_8_risk/risk_decision.md) (Risk trade-offs & ADR sections)

### Layer 9 - Output Formats
- `REGOUT-001` to `REGOUT-002` -> [out_strc.md](./references/layer_9_output/out_strc.md) (Structure & Detalhes)
- `REGOUT-003` to `REGOUT-005` -> [out_cont.md](./references/layer_9_output/out_cont.md) (Linguagem, Siglas & Termos)
- `REGOUT-006` to `REGOUT-008` -> [out_format.md](./references/layer_9_output/out_format.md) (Markdown, Tabelas & Diagramas)
- `REGOUT-009` to `REGOUT-010` -> [out_report.md](./references/layer_9_output/out_report.md) (Metadados & Relatórios)
- `REGOUT-011` -> [out_exec.md](./references/layer_9_output/out_exec.md) (CLARO recommendations)

### Layer 10 - Process & Lifecycle
- `REGPROC-001` to `REGPROC-003` -> [proc_select.md](./references/layer_10_process/proc_select.md) (Process Selection Rules)
- `REGPROC-004` -> [proc_activities.md](./references/layer_10_process/proc_activities.md) (Fundamental Activities)
- `REGPROC-005` to `REGPROC-006` -> [proc_change.md](./references/layer_10_process/proc_change.md) (Change Management & Prototyping)
- `REGPROC-007` to `REGPROC-008` -> [proc_agile_xp.md](./references/layer_10_process/proc_agile_xp.md) (Agile & XP Rules)
- `REGPROC-009` to `REGPROC-010` -> [proc_agile_scrum.md](./references/layer_10_process/proc_agile_scrum.md) (Scrum & Agile Management)
- `REGPROC-011` -> [proc_scaling.md](./references/layer_10_process/proc_scaling.md) (Scaling Agile)
- `REGPROC-012` -> [proc_gov.md](./references/layer_10_process/proc_gov.md) (Process Governance & Docs)

### Layer 11 - Modeling & Design
- `REGMODEL-001` to `REGMODEL-002` -> [model_objects.md](./references/layer_11_modeling/model_objects.md) (Object Identification & Responsibilities)
- `REGMODEL-003` to `REGMODEL-006` -> [model_structural.md](./references/layer_11_modeling/model_structural.md) (UML Diagrams: Class, Case Use, Sequence, State)
- `REGMODEL-007` to `REGMODEL-008` -> [model_patterns.md](./references/layer_11_modeling/model_patterns.md) (Design Patterns GoF & ADRs)
- `REGMODEL-009` to `REGMODEL-010` -> [model_validation.md](./references/layer_11_modeling/model_validation.md) (Consistency Validation & Traceability)
- `REGMODEL-011` to `REGMODEL-012` -> [model_implementation.md](./references/layer_11_modeling/model_implementation.md) (OO Coding Standards & Exceptions)

### Layer 12 - Testing & Quality Assurance
- `REGTEST-001` to `REGTEST-003` -> [test_dev.md](./references/layer_12_testing/test_dev.md) (Development Testing, Unit & Integration Tests & TDD)
- `REGTEST-004` to `REGTEST-005` -> [test_release.md](./references/layer_12_testing/test_release.md) (Release, Scenario & Performance Testing)
- `REGTEST-006` to `REGTEST-007` -> [test_user.md](./references/layer_12_testing/test_user.md) (User Testing, Alpha/Beta & Acceptance)
- `REGTEST-008` to `REGTEST-009` -> [test_review.md](./references/layer_12_testing/test_review.md) (Pull Request Reviews & Quality Checklist)
- `REGTEST-010` to `REGTEST-011` -> [test_metrics.md](./references/layer_12_testing/test_metrics.md) (Complexity Limits, Technical Debt & ISO 9001)

### Layer 13 - Evolution & Configuration Management
- `REGEVOL-001` -> [evol_dynamics.md](./references/layer_13_evolution/evol_dynamics.md) (Lehman's Laws of Evolution)
- `REGEVOL-002` to `REGEVOL-003` -> [evol_maint.md](./references/layer_13_evolution/evol_maint.md) (Maintenance Categorization & Refactoring)
- `REGEVOL-004` to `REGEVOL-005` -> [evol_legacy.md](./references/layer_13_evolution/evol_legacy.md) (Legacy System Evaluation Matrix & Action Plans)
- `REGEVOL-006` to `REGEVOL-009` -> [evol_cm.md](./references/layer_13_evolution/evol_cm.md) (Change Request SCM, Git Branching, CI Builds & SemVer)

### Layer 14 - Project Management & Planning
- `REGPM-001` to `REGPM-002` -> [principles.md](./references/layer_14_project/principles.md) (PM Principles & Responsibilities)
- `REGPM-003` to `REGPM-005` -> [pm_risk.md](./references/layer_14_project/pm_risk.md) (Risk Management: Identification, Mitigation & Monitoring)
- `REGPM-006` to `REGPM-007` -> [pm_people.md](./references/layer_14_project/pm_people.md) (People Management, Motivation & Team Building)
- `REGPM-008` to `REGPM-010` -> [pm_planning.md](./references/layer_14_project/pm_planning.md) (Project Planning, COCOMO II & Story Points)
- `REGPM-011` to `REGPM-012` -> [pm_scheduling.md](./references/layer_14_project/pm_scheduling.md) (Scheduling, Critical Path & Sprint Planning)
