# Layer 4 – Qualidade, Validação e Revisão Técnica (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-05  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 4 – Quality Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software) – obrigatórios  
**Autoridade:** Subordinado às Layers 0, 1, 2, 3. Nenhuma regra deste módulo pode violar os princípios constitucionais, o motor de raciocínio, os requisitos aprovados ou as decisões arquiteturais.  
**Escopo:** Define o conjunto completo de regras para garantir a qualidade do software e da arquitetura, abrangendo padrões de qualidade (ISO/IEC 25010), processos de revisão técnica (código, arquitetura, segurança), Quality Gates, métricas de dívida técnica, critérios de aceitação, cobertura de testes e práticas de validação contínua.

---

## Estrutura do Módulo

Este módulo estabelece o **Motor de Garantia de Qualidade** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_4_quality/glossary.md)**  
   *Termos específicos baseados na ISO/IEC 25010 e na Engenharia de Software, incluindo Dívida Técnica, Quality Gate, Complexidade Ciclomática e testes de contrato.*

2. **[Princípios Fundamentais da Qualidade](./layer_4_quality/principles.md)**  
   *Os 6 princípios orientadores de qualidade, incluindo Qualidade como RT, Prevenção, Revisão Independente e Qualidade como Processo Contínuo.*

3. **[Regras de Padrões de Qualidade (QUAL-STD)](./layer_4_quality/qual_std.md)**  
   *Regras operacionais (REGQUAL-001 a REGQUAL-002) para mapeamento ISO 25010 e aplicação de limites de duplicação, complexidade e índice de manutenibilidade.*

4. **[Regras de Revisão Técnica (QUAL-REVIEW)](./layer_4_quality/qual_review.md)**  
   *Políticas de inspeção (REGQUAL-003 a REGQUAL-005) regulando a revisão obrigatória independente de arquitetura para mudanças estruturais, fluxos de PR com aprovação mínima e uso do checklist de código.*

5. **[Regras de Testes e Validação (QUAL-TEST)](./layer_4_quality/qual_test.md)**  
   *Regras de testes automatizados (REGQUAL-006 a REGQUAL-009) exigindo cobertura unitária de 80%, testes de integração de persistência, testes de contrato em microsserviços e testes regulares de performance (carga/estresse).*

6. **[Regras de Quality Gates e Pipeline (QUAL-GATES)](./layer_4_quality/qual_gates.md)**  
   *Regras de controle de esteira (REGQUAL-010 a REGQUAL-011) detalhando bloqueios automáticos de CI/CD (Quality Gates) e rastreabilidade bidirecional de bugs.*

7. **[Regras de Gestão de Dívida Técnica (QUAL-DEBT)](./layer_4_quality/qual_debt.md)**  
   *Regras de gestão (REGQUAL-012) detalhando o rastreamento, priorização e orçamentação sprint-a-sprint de dívida técnica.*

8. **[Auditoria, Exemplo Prático e Evolução](./layer_4_quality/audit.md)**  
   *Tabela de auditoria interna da Layer 4, exemplo prático de aprovação condicional em PR genômico e submódulos de expansão do produto.*
