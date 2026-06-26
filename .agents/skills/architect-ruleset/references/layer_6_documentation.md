# Layer 6 – Documentação e Comunicação Técnica (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-07  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 6 – Documentation & Communication Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software), Módulo 05 (Qualidade), Módulo 06 (Segurança/Privacidade) – obrigatórios  
**Autoridade:** Subordinado às Layers 0 a 5. Nenhuma regra deste módulo pode violar os princípios constitucionais, o motor de raciocínio, os requisitos aprovados, as decisões arquiteturais, os critérios de qualidade ou as políticas de segurança.  
**Escopo:** Define o conjunto completo de regras para a documentação técnica e a comunicação arquitetural, abrangendo estrutura de artefatos (ARC42, ADRs, READMEs), Viewpoints vs Views, legibilidade (Grice, Miller, Gestalt), formatação de saída, rastreabilidade entre documentação e código, e boas práticas de comunicação com stakeholders.

---

## Estrutura do Módulo

Este módulo estabelece o **Sistema de Documentação e Comunicação** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_6_documentation/glossary.md)**  
   *Definições obrigatórias para documentação técnica, ARC42, ADRs, Viewpoints, Views, e métricas de legibilidade cognitiva.*

2. **[Princípios Fundamentais de Documentação](./layer_6_documentation/principles.md)**  
   *Princípios como Documentação como Ativo, Orientação a Público (Audience-First), Documentação Viva (Living Documentation), Clareza e Rastreabilidade.*

3. **[Regras de Estrutura de Artefatos (DOC-STRUCT)](./layer_6_documentation/doc_struct.md)**  
   *Regras (REGDOC-001 a REGDOC-003) regulando a estrutura de arquitetura sob o modelo ARC42, o registro imperativo de ADRs de design e READMEs de projeto.*

4. **[Regras de Legibilidade e Formato (DOC-READABILITY)](./layer_6_documentation/doc_readability.md)**  
   *Diretrizes de legibilidade (REGDOC-004 a REGDOC-006) aplicando as Máximas de Grice, a regra de Miller de 7 ± 2 itens para listas e os Princípios de Gestalt em diagramas.*

5. **[Regras de Viewpoints e Visualização (DOC-VIEW)](./layer_6_documentation/doc_view.md)**  
   *Regras (REGDOC-007 a REGDOC-008) sobre a separação formal de Viewpoints e Views e classificação de visualizações por propósitos (Designing, Deciding, Informing).*

6. **[Regras de Rastreabilidade da Documentação (DOC-TRACE)](./layer_6_documentation/doc_trace.md)**  
   *Regras (REGDOC-009 a REGDOC-010) sobre rastreabilidade bidirecional documento ↔ código e versionamento obrigatório em Git.*

7. **[Regras de Comunicação com Stakeholders (DOC-COMM)](./layer_6_documentation/doc_comm.md)**  
   *Diretrizes (REGDOC-011 a REGDOC-012) mapeando técnicas de conversação por propósito e o registro documentado de comprometimento (Aware, Agree, Commit).*

8. **[Auditoria, Exemplo Prático e Evolução](./layer_6_documentation/audit.md)**  
   *Tabela de auditoria para a Layer 6, exemplo prático de aprovação de Pull Request com ADRs e documentação de comprometimento no VarSuS, e direções de evolução.*
