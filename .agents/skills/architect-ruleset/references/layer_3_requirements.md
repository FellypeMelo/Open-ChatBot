# Layer 3 – Engenharia de Requisitos (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-03  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 3 – Engineering Rules (Requisitos)  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning) – obrigatórios  
**Autoridade:** Subordinado às Layers 0, 1 e 2. Nenhuma regra deste módulo pode violar os princípios constitucionais ou o motor de raciocínio.  
**Escopo:** Define o conjunto completo de regras para a engenharia de requisitos, abrangendo desde a elicitação (descoberta) até a especificação formal, validação com stakeholders, rastreabilidade bidirecional e gestão de mudanças.

---

## Estrutura do Módulo

Este módulo estabelece o **Motor de Engenharia de Requisitos** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_3_requirements/glossary.md)**  
   *Termos fundamentais específicos de requisitos como Elicitação, Validação de Conteúdo, Comprometimento, Derivação e Categorias (RN, PS, LGPD, RT) baseados na ISO/IEC 29148.*

2. **[Princípios Fundamentais de Requisitos](./layer_3_requirements/principles.md)**  
   *Os 6 princípios orientadores, incluindo Origem Obrigatória, Ambiguidade Zero, Separação por Categoria e Comprometimento como Fim.*

3. **[Regras de Elicitação e Scoping (REQ-ELICIT)](./layer_3_requirements/req_elicit.md)**  
   *Regras operacionais (REGREQ-001 a REGREQ-003) regulando a identificação do dono do requisito, uso das técnicas da Tabela 4.1 e a análise pelas 4 direções metafóricas.*

4. **[Regras de Especificação e Estruturação (REQ-SPEC)](./layer_3_requirements/req_spec.md)**  
   *Regras de estruturação padronizada (REGREQ-004 a REGREQ-007) definindo o template do requisito, critérios não-funcionais SMART, proibição de requisitos mistos e justificativa do porquê.*

5. **[Regras de Validação e Comprometimento (REQ-VALID)](./layer_3_requirements/req_valid.md)**  
   *Regras de aceitação (REGREQ-008 a REGREQ-010) definindo a separação entre validação técnica e comprometimento executivo, proibição de revisões assíncronas para requisitos complexos e fluxo de escalação formal de impasses.*

6. **[Regras de Rastreabilidade e Matrizes (REQ-TRACE)](./layer_3_requirements/req_trace.md)**  
   *Regras de controle de integridade (REGREQ-011 a REGREQ-012) exigindo matriz universal bidirecional e proibição estrita de rastreabilidade circular.*

7. **[Auditoria, Exemplo Prático e Evolução](./layer_3_requirements/audit.md)**  
   *Critérios detalhados de auditoria de conformidade da Layer 3, exemplo prático de refinação de entrada ambígua e mecanismos para evolução modular.*
