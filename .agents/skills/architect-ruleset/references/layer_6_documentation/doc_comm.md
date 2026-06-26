# Seção 7 – Regras de Comunicação com Stakeholders (Layer 6 - Documentação e Comunicação Técnica)

**ID:** ARCH-RULESET-L6-DOC-COMM  
**Status:** Definitivo  
**Escopo:** Métodos de comunicação baseados no alinhamento de intenções (Introducing, Agreeing, Committing) e na documentação formal de comprometimento.

---

### REGDOC-011 – Técnicas de Conversação por Propósito (Tabela 4.1)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-011 |
| **Nome** | Técnicas de Conversação por Propósito (Tabela 4.1) |
| **Descrição** | O agente deve recomendar e aplicar a técnica de conversação adequada ao propósito da comunicação arquitetural, conforme a Tabela 4.1 do Capítulo 4: **Introduzir** (Brown-paper, Elicitação), **Concordar** (Workshop, Validação), **Comprometer** (Committing Review). O agente não pode usar uma técnica inadequada (ex: validar por e-mail). A técnica deve ser documentada no plano de comunicação. |
| **Objetivo** | Garantir que a comunicação com stakeholders seja eficaz e atinja seu propósito. |
| **Motivação** | Cap. 4.4.2, Tabela 4.1. |
| **Justificativa** | A técnica errada gera feedback ineficaz ou comprometimento falso (ex: e-mail para decisão crítica). |
| **Critérios de Aplicação** | Toda comunicação com stakeholders sobre arquitetura. |
| **Critérios de Não Aplicação** | Comunicações internas da equipe de desenvolvimento (ex: daily stand-ups). |
| **Pré-condições** | Propósito da comunicação definido. |
| **Pós-condições** | Técnica recomendada e aplicada. |
| **Restrições** | Se o stakeholder insistir em uma técnica inadequada, o agente deve sinalizar o risco. |
| **Dependências** | REGREQ-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Para validar a nova arquitetura, recomendamos um workshop com os arquitetos (técnica de Concordar). Para informar os desenvolvedores, uma apresentação (técnica de Informar)." |
| **Exemplo Negativo** | "Vamos enviar a proposta de arquitetura por e-mail para todos aprovarem." |
| **Anti-pattern** | Usar a mesma técnica (ex: reunião semanal) para todos os propósitos. |
| **Métrica** | Número de comunicações com técnica adequada vs. total. |
| **Critérios de Auditoria** | Revisar plano de comunicação: se a técnica não estiver alinhada ao propósito, falha. |

---

### REGDOC-012 – Documentação de Comprometimento (Aware, Agree, Commit)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-012 |
| **Nome** | Documentação de Comprometimento (Aware, Agree, Commit) |
| **Descrição** | O agente deve garantir que para cada decisão arquitetural ou requisito crítico, o nível de comprometimento de cada stakeholder seja documentado, conforme os três estágios (Cap. 4.2.4): **Aware** (informado), **Agree** (concorda), **Commit** (assume responsabilidade). O registro deve incluir: data, stakeholder, nível de comprometimento e, se Commit, evidência (ex: assinatura, ata de reunião). |
| **Objetivo** | Garantir que não haja dúvidas sobre quem está comprometido com o quê, evitando surpresas em fases posteriores. |
| **Motivação** | Cap. 4.2.4 (níveis de comprometimento), Cap. 7.4.6 (comprometimento formal). |
| **Justificativa** | A falta de comprometimento formal é uma causa comum de retrabalho e desalinhamento. |
| **Critérios de Aplicação** | Decisões arquiteturais (ADRs), requisitos críticos (RN, PS, LGPD). |
| **Critérios de Não Aplicação** | Decisões triviais ou rotineiras. |
| **Pré-condições** | Decisão tomada. |
| **Pós-condições** | Nível de comprometimento registrado. |
| **Restrições** | O Commit só pode ser registrado após uma reunião formal (não por e-mail). |
| **Dependências** | REGDOC-002, REGREQ-008. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "ADR-012: Stakeholder Dr. Carlos (Commit, 10/01/2025, ata da reunião). Stakeholder Ana (Agree, 09/01/2025)." |
| **Exemplo Negativo** | "Todos concordam com a decisão." (sem documentar quem, quando, como). |
| **Anti-pattern** | Registrar Commit sem a participação efetiva do stakeholder na decisão. |
| **Métrica** | Percentual de decisões com comprometimento documentado. |
| **Critérios de Auditoria** | Revisar se há registro de comprometimento para cada ADR. |
