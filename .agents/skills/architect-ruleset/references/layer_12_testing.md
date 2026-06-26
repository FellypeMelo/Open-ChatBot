# Layer 12 – Testing & Quality Assurance Rules (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-13  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 12 – Testing & Quality Assurance Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software), Módulo 05 (Qualidade), Módulo 06 (Segurança/Privacidade), Módulo 07 (Documentação), Módulo 08 (Governança), Módulo 09 (Riscos), Módulo 10 (Output), Módulo 11 (Processos), Módulo 12 (Modelagem) – obrigatórios  
**Autoridade:** Subordinado a todas as Layers 0 a 11. Nenhuma regra deste módulo pode violar qualquer princípio ou regra definida nas camadas superiores.  
**Escopo:** Define o conjunto completo de regras para testes de software e garantia de qualidade, abrangendo testes de desenvolvimento (unitário, componente, sistema), TDD, testes de liberação, testes de usuário (alfa, beta, aceitação), revisões e inspeções, métricas e padrões de qualidade (ISO 9001), com base nos Capítulos 8 (Testes de Software) e 24 (Gestão da Qualidade) do livro-base "Software Engineering" (Sommerville, 9ª ed.).

---

## Estrutura do Módulo

Este módulo estabelece o **Sistema de Testes e Garantia de Qualidade** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_12_testing/glossary.md)**  
   *Definições canônicas de verificação, validação, teste unitário, teste de componente, teste de sistema, teste de liberação, aceitação, alfa, beta, TDD, revisão de código e métricas.*

2. **[Princípios Fundamentais](./layer_12_testing/principles.md)**  
   *Princípios como "Testes como Atividade Contínua", "Validação vs. Verificação", "Qualidade como RT", "Automação para Regressão" e "Revisões e Inspeções".*

3. **[Regras de Testes de Desenvolvimento (TEST-DEV)](./layer_12_testing/test_dev.md)**  
   *Regras (REGTEST-001 a REGTEST-003) regulando testes unitários (meta de 80%), testes de integração para dependências externas e prática de TDD.*

4. **[Regras de Testes de Liberação (TEST-RELEASE)](./layer_12_testing/test_release.md)**  
   *Regras (REGTEST-004 a REGTEST-005) sobre testes baseados em requisitos/cenários e testes de performance e estresse.*

5. **[Regras de Testes de Usuário (TEST-USER)](./layer_12_testing/test_user.md)**  
   *Regras (REGTEST-006 a REGTEST-007) exigindo envolvimento em testes alfa/beta e critérios objetivos para aceitação.*

6. **[Regras de Revisão e Inspeção de Código (TEST-REVIEW)](./layer_12_testing/test_review.md)**  
   *Regras (REGTEST-008 a REGTEST-009) sobre Pull Requests obrigatórios com aprovação e checklists formais de revisão.*

7. **[Regras de Métricas e Padrões de Qualidade (TEST-METRICS)](./layer_12_testing/test_metrics.md)**  
   *Regras (REGTEST-010 a REGTEST-011) sobre monitoramento de complexidade ciclomática, dívida técnica e padrões ISO 9001.*

8. **[Auditoria, Exemplo Prático e Evolução](./layer_12_testing/audit.md)**  
   *Tabela de auditoria contendo 11 critérios, exemplo integrado de aplicação (sistema de e-commerce) e direções de evolução e extensibilidade.*
