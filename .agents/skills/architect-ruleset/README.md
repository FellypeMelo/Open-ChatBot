# 🧭 AI Architect Ruleset — Standalone Constitution & Decision Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![AI Standards: Strict](https://img.shields.io/badge/AI_Standards-Strict-red.svg)](#)
[![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-green.svg)](#)

A production-grade, highly structured multi-layered constitutional ruleset designed to govern AI coding agents (such as Google Antigravity, Claude Engineer, and others). It enforces strict software engineering standards, clean architecture, security protocols, LGPD compliance, testing guidelines, and semantic decision reasoning.

By standardizing agent behaviors through a multi-layered rulebook, this ruleset eliminates "vibe-coding" and aligns AI-driven software development with international engineering standards (ISO 25010, STRIDE, Conway's Law, etc.).

---

## 🌟 Key Capabilities

*   **🛡️ Layer 0 AI Constitution:** Establishes supreme guidelines that the AI agent cannot violate under any circumstances, prioritizing logical correctness, safety, and traceability.
*   **⚡ Zero-Bloat Semantic Router:** Integrates a semantic routing table allowing AI agents to load and read only the precise rule files relevant to their current task (e.g., loading only Layer 5 for Cryptography & LGPD concerns) instead of reading the entire ruleset. This saves thousands of context tokens and improves speed.
*   **🧪 TDD Quality Gates:** Mandates strict Red-Green-Refactor development cycles. The agent is structurally blocked from writing tests and implementations simultaneously, forcing test-driven development.
*   **🔒 Brazilian Privacy & Security Compliance (LGPD):** Dedicated layers covering STRIDE threat modeling, access control (IAM), encrypted data storage, and strict sanitization of Patient Identifiable Information (PII).
*   **📊 Structured ADR & Risk Models:** Standardizes Architectural Decision Records (ADRs) and quantitative risk assessments using FAIR (Factor Analysis of Information Risk) concepts.

---

## 📁 Repository Structure

The repository is modularized into isolated layers containing markdown specifications:

```text
architect-ruleset/
├── SKILL.md                 # Main entry point and Semantic Task Router
├── README.md                # General documentation
├── install.ps1              # Automation installer for Windows (PowerShell)
├── install.sh               # Automation installer for Unix/macOS (Bash)
├── .gitignore               # Ignored system files
├── examples/                # Real-world examples of correct implementations
├── resources/               # Templates and config structures
├── scripts/                 # Developer utility scripts
└── references/              # The 15 Layers of the Ruleset
    ├── layer_0_constitution.md         # Supreme directives, ethics, and priorities
    ├── layer_0_constitution/           # Detailed constitution rules
    ├── layer_1_2_reasoning.md          # Deduction, induction, and metacognitive audits
    ├── layer_1_2_reasoning/            # Logic & metacognition sub-rules
    ├── layer_3_requirements.md         # Elicitation, specification, validation
    ├── layer_3_requirements/           # Requirements sub-rules
    ├── layer_3_architecture.md         # Design patterns, clean architecture, DDD
    ├── layer_3_architecture/           # Architecture model rules
    ├── layer_4_quality.md              # ISO 25010 metrics limits, CI/CD gates, tech debt
    ├── layer_4_quality/                # Quality review & test sub-rules
    ├── layer_5_compliance.md           # IAM, Encryption, STRIDE, Brazilian LGPD
    ├── layer_5_compliance/             # Cryptography & security sub-rules
    ├── layer_6_documentation.md        # ARC42, ADR structure, readability rules
    ├── layer_6_documentation/          # Doc viewpoints & views
    ├── layer_7_governance.md           # Conway's law, CR impact, RACI matrix
    ├── layer_7_governance/             # Governance sub-rules
    ├── layer_8_risk.md                 # Quantitative threat assessments, FAIR, ADR risk
    ├── layer_8_risk/                   # Risk evaluation & monitor sub-rules
    ├── layer_9_output.md               # Markdown formatting, data tables, metrics
    ├── layer_9_output/                 # Output formats sub-rules
    ├── layer_10_process.md             # Software process selection & Agile/XP cycles
    ├── layer_10_process/               # Process rules
    ├── layer_11_modeling.md            # Structural UML (Class, Sequence, Use Case)
    ├── layer_11_modeling/              # Modeling & OO design rules
    ├── layer_12_testing.md             # TDD, QA metrics, unit/integration, PR checklists
    ├── layer_12_testing/               # Testing & QA rules
    ├── layer_13_evolution.md           # Lehman's laws, refactoring, SemVer, SCM git
    ├── layer_13_evolution/             # Evolution rules
    ├── layer_14_project.md             # Planning, COCOMO II estimation, critical path
    └── layer_14_project/               # PM rules
```

---

## 🚀 Easy Installation Guide

You can install this skill either **globally** (for use across all your projects) or **locally** (specific to a single project).

### Method 1: Automated Script (Fastest)

1. Clone this repository to your computer:
   ```bash
   git clone https://github.com/<your-username>/architect-ruleset.git
   cd architect-ruleset
   ```

2. Run the installer script matching your operating system:
   * **Windows (PowerShell):**
     ```powershell
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
     .\install.ps1
     ```
   * **macOS / Linux (Bash):**
     ```bash
     chmod +x install.sh
     ./install.sh
     ```
   
   The interactive installer will ask whether you want a **Global** or **Local** installation.

---

### Method 2: Manual Installation

#### A. Global Installation (Recommended for personal development)
Installing globally allows Gemini/Antigravity to access these rules on *any* project folder without committing rule files to individual project repositories.

* **Windows:** Copy the contents of this repository to:
  `C:\Users\<Your-Username>\.gemini\config\skills\architect-ruleset\`
* **macOS / Linux:** Copy the contents of this repository to:
  `~/.gemini/config/skills/architect-ruleset/`

#### B. Local Workspace Installation (Recommended for project teams)
Installing locally ensures the skill is versioned alongside the code. Copy the contents of this repository to:
`<your-project-root>/.agents/skills/architect-ruleset/`

---

## 🛠️ How to Activate in Your Projects

Once installed, you must tell the agent when and how to consult this ruleset.

1. Create or edit `.agents/AGENTS.md` in your project's root folder.
2. Append the operational mandate informing the agent about the Ruleset. Example:

```markdown
# Workspace Custom Agent Instructions

This workspace is strictly governed by the custom **Architect Ruleset** (Constitution + Rules Engine).

## ⚙️ AI Operational Mandate
Whenever you are assigned any task:
1. **Do not execute blind implementations.** Align with the corresponding Layer rules defined in the custom skill.
2. **Consult the Entry Point:** Go to [SKILL.md](file:///~/.gemini/config/skills/architect-ruleset/SKILL.md) (or relative local path).
3. **Use the Router:** Refer to the **Semantic Task Router** in `SKILL.md` to identify which Layer rules apply.
4. **Strict Hierarchy:** Layer 0 (Constitution) is supreme and overrides all decisions from lower layers.
```

---

## 🤝 Contribution Guidelines

Contributions are welcome! If you would like to submit amendments or new modules to the ruleset:
1. Refer to **Layer 0 Constitution (Evolution & Amendments)** in [evolution.md](./references/layer_0_constitution/evolution.md) for the rules engine update process.
2. Open a Pull Request detailing the changes and linking the relevant ADR/reasoning.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
