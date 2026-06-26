# Layer 13 – Evolution & Configuration Management Rules (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-14  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 13 – Evolution & Configuration Management Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software), Módulo 05 (Qualidade), Módulo 06 (Segurança/Privacidade), Módulo 07 (Documentação), Módulo 08 (Governança), Módulo 09 (Riscos), Módulo 10 (Output), Módulo 11 (Processos), Módulo 12 (Modelagem), Módulo 13 (Testes) – obrigatórios  
**Autoridade:** Subordinado a todas as Layers 0 a 12. Nenhuma regra deste módulo pode violar qualquer princípio ou regra definida nas camadas superiores.  
**Escopo:** Define o conjunto completo de regras para a evolução de software, manutenção e gestão de configuração, abrangendo desde os processos de evolução e dinâmica de mudanças (Leis de Lehman), passando pelos tipos de manutenção (corretiva, adaptativa, perfectiva), reengenharia e refatoração, gestão de sistemas legados, até o controle de versões, build, release e ferramentas de gestão de configuração (Git, Subversion, etc.), com base nos Capítulos 9 (Evolução de Software) e 25 (Gestão de Configuração) do livro-base "Software Engineering" (Sommerville, 9ª ed.).

---

## Estrutura do Módulo

Este módulo estabelece o **Sistema de Evolução e Gestão de Configuração** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_13_evolution/glossary.md)**  
   *Definições canônicas de evolução de software, manutenção corretiva/adaptativa/perfectiva, Leis de Lehman, reengenharia, refatoração, sistema legado, CM, versionamento, branch/merge, build, release, baseline e CR.*

2. **[Princípios Fundamentais](./layer_13_evolution/principles.md)**  
   *Princípios como "Mudança Inevitável", "Estrutura Degrada com o Tempo", "Manutenção além de Bugs", "Avaliação Baseada em Valor e Tecnologia", "Rastreabilidade e Aprovação".*

3. **[Regras de Evolução e Dinâmica de Mudanças (EVOL-DYNAMICS)](./layer_13_evolution/evol_dynamics.md)**  
   *Regras (REGEVOL-001) para a aplicação prática das Leis de Lehman na gerência de complexidade estrutural.*

4. **[Regras de Manutenção e Priorização (EVOL-MAINT)](./layer_13_evolution/evol_maint.md)**  
   *Regras (REGEVOL-002 a REGEVOL-003) ditando a classificação/priorização de manutenção e a alocação de tempo para refatoração contínua.*

5. **[Regras de Gestão de Sistemas Legados (EVOL-LEGACY)](./layer_13_evolution/evol_legacy.md)**  
   *Regras (REGEVOL-004 a REGEVOL-005) cobrindo a matriz de avaliação valor-qualidade e as estratégias correspondentes (manter, reengenharia, substituir).*

6. **[Regras de Gestão de Configuração (EVOL-CM)](./layer_13_evolution/evol_cm.md)**  
   *Regras (REGEVOL-006 a REGEVOL-009) regulando processos formais de change requests, versionamento com Git, builds automatizados de CI e SemVer.*

7. **[Auditoria, Exemplo Prático e Evolução](./layer_13_evolution/audit.md)**  
   *Tabela de auditoria contendo 9 critérios, exemplo integrado de aplicação (sistema de folha de pagamento em COBOL) e direções de evolução.*
