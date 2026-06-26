# Seção 6 – Regras de Métodos Ágeis e Extreme Programming (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-AGILE-XP  
**Status:** Definitivo  
**Escopo:** Regras e boas práticas técnicas para projetos ágeis baseados no manifesto ágil e XP.

---

### REGPROC-007 – Aplicação dos Princípios do Manifesto Ágil em Projetos com Equipes Pequenas e Co-localizadas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-007 |
| **Nome** | Aplicação dos Princípios do Manifesto Ágil em Projetos com Equipes Pequenas e Co-localizadas |
| **Descrição** | Para projetos com equipes pequenas (≤ 10 pessoas), co-localizadas, com requisitos voláteis e alto envolvimento do cliente, o agente deve recomendar a adoção de métodos ágeis baseados nos princípios do Manifesto Ágil: **(1)** indivíduos e interações sobre processos e ferramentas; **(2)** software funcional sobre documentação abrangente; **(3)** colaboração com o cliente sobre negociação de contratos; **(4)** responder a mudanças sobre seguir um plano. O agente deve enfatizar que isso não significa ausência de disciplina, mas sim uma abordagem adaptativa e centrada nas pessoas. |
| **Objetivo** | Aproveitar a agilidade para entregar valor rapidamente em ambientes dinâmicos. |
| **Motivação** | Cap. 3.1 – o manifesto ágil reflete a filosofia por trás dos métodos ágeis. |
| **Justificativa** | Equipes pequenas e co-localizadas se beneficiam da comunicação informal e da flexibilidade. |
| **Critérios de Aplicação** | Projetos com equipe ≤ 10, co-localizada, e com cliente disponível para colaboração. |
| **Critérios de Não Aplicação** | Projetos com equipes grandes (> 20), distribuídas, ou com regulações rigorosas que exigem documentação extensa. |
| **Pré-condições** | Análise de tamanho da equipe e disponibilidade do cliente. |
| **Pós-condições** | Adoção de práticas ágeis (ex: Scrum, XP) documentada no plano de projeto. |
| **Restrições** | Mesmo em projetos ágeis, a qualidade e a segurança não podem ser comprometidas. |
| **Dependências** | REGPROC-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Equipe de 7 desenvolvedores, cliente no mesmo andar, requisitos mudam semanalmente – adotar Scrum com sprints de 2 semanas." |
| **Exemplo Negativo** | "Adotar ágil em uma equipe de 50 pessoas distribuídas em 3 países, com cliente ausente." |
| **Anti-pattern** | Usar ágil como desculpa para ausência de planejamento ou documentação. |
| **Métrica** | Percentual de projetos ágeis com entregas no prazo. |
| **Critérios de Auditoria** | Verificar se os princípios ágeis são praticados (ex: stand-ups, retrospectivas, envolvimento do cliente). |

---

### REGPROC-008 – Adoção de Práticas do Extreme Programming (XP) para Alta Qualidade Técnica

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-008 |
| **Nome** | Adoção de Práticas do Extreme Programming (XP) para Alta Qualidade Técnica |
| **Descrição** | Em projetos onde a qualidade do código e a capacidade de evolução são críticas, o agente deve recomendar a adoção de práticas do XP, especialmente: **(1)** TDD (escrever testes antes do código); **(2)** Programação em Pares; **(3)** Integração Contínua; **(4)** Refatoração contínua; **(5)** Propriedade Coletiva do Código; **(6)** Ritmo Sustentável. O agente deve enfatizar que o XP não é apenas um conjunto de práticas, mas uma mudança cultural que exige disciplina e comprometimento da equipe. |
| **Objetivo** | Garantir alta qualidade técnica, baixa dívida técnica e capacidade de resposta a mudanças. |
| **Motivação** | Cap. 3.3 – XP integra boas práticas de programação para alcançar qualidade. |
| **Justificativa** | Práticas como TDD e refatoração reduzem defeitos e facilitam a evolução. |
| **Critérios de Aplicação** | Projetos onde a qualidade do código e a manutenibilidade são prioridades. |
| **Critérios de Não Aplicação** | Projetos onde a equipe não tem maturidade ou disciplina para adotar XP. |
| **Pré-condições** | Equipe treinada em TDD, pair programming, etc. |
| **Pós-condições** | Práticas XP documentadas no processo de desenvolvimento. |
| **Restrições** | O agente deve sinalizar que a adoção de XP requer adaptação gradual e suporte da gerência. |
| **Dependências** | REGQUAL-006 (cobertura de testes), REGARCH-SW-002 (clean code). |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Adotamos TDD, pair programming e CI em nosso projeto de microsserviços; a qualidade subiu 40%." |
| **Exemplo Negativo** | "Dizemos que usamos XP, mas não fazemos TDD nem refatoração." |
| **Anti-pattern** | Aplicar XP apenas no nome, sem as práticas essenciais. |
| **Métrica** | Percentual de código coberto por testes (meta: ≥ 80%). |
| **Critérios de Auditoria** | Verificar se TDD e pair programming são praticados. |
