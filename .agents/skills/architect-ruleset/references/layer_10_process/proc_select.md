# Seção 3 – Regras de Seleção de Modelos de Processo (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-SELECT  
**Status:** Definitivo  
**Escopo:** Critérios formais para diagnóstico e escolha do ciclo de vida de desenvolvimento do projeto.

---

### REGPROC-001 – Análise Contextual para Escolha do Modelo de Processo

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-001 |
| **Nome** | Análise Contextual para Escolha do Modelo de Processo |
| **Descrição** | O agente deve, antes de recomendar um modelo de processo, analisar o contexto do projeto com base em, no mínimo, cinco dimensões: **(1) Estabilidade dos Requisitos**: mudam frequentemente? (2) **Criticidade do Sistema**: falhas podem causar danos severos? (3) **Tamanho da Equipe**: pequena (≤ 10) ou grande? (4) **Maturidade Organizacional**: processos existem e são seguidos? (5) **Cultura e Experiência da Equipe**: familiaridade com métodos ágeis ou plan-driven? Com base nessa análise, o agente deve recomendar um modelo (cascata, incremental, espiral, RUP, ágil) e justificar a escolha com evidências. |
| **Objetivo** | Evitar a aplicação de um modelo de processo inadequado ao contexto, que poderia gerar retrabalho, baixa qualidade ou insatisfação do cliente. |
| **Motivação** | Cap. 2.1 – diferentes modelos são adequados para diferentes tipos de sistemas. Cap. 3.2 – a escolha entre plan-driven e agile depende de questões técnicas, humanas e organizacionais. |
| **Justificativa** | Um modelo inadequado é uma das principais causas de fracasso em projetos de software. |
| **Critérios de Aplicação** | Sempre que o agente for consultado sobre qual processo adotar em um novo projeto ou na reavaliação de um projeto existente. |
| **Critérios de Não Aplicação** | Projetos com processo já definido e validado pela organização (a menos que haja solicitação de reavaliação). |
| **Pré-condições** | Informações sobre o projeto (requisitos, equipe, organização, etc.) disponíveis. |
| **Pós-condições** | Recomendação formal de modelo de processo, com justificativa baseada nas cinco dimensões. |
| **Restrições** | A recomendação deve ser revisada periodicamente (ex: a cada marco) para verificar se o contexto mudou. |
| **Dependências** | REGRISK-001 (identificação de riscos), REGGOV-003 (alinhamento organizacional). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Projeto de sistema de controle de aviônicos: requisitos estáveis (alta), criticidade muito alta, equipe grande (50+), organização com CMMI nível 3. Recomendo modelo em espiral com forte ênfase em análise de riscos e documentação formal." |
| **Exemplo Negativo** | "Vamos usar Scrum porque é moda." |
| **Anti-pattern** | Escolher um processo apenas com base na preferência pessoal do gerente, sem análise objetiva. |
| **Métrica** | Percentual de projetos com recomendação de processo baseada em análise formal (meta: 100%). |
| **Critérios de Auditoria** | Revisar recomendações de processo: se não houver análise documentada, falha. |

---

### REGPROC-002 – Uso do Modelo em Cascata Apenas para Requisitos Estáveis e Bem Compreendidos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-002 |
| **Nome** | Uso do Modelo em Cascata Apenas para Requisitos Estáveis e Bem Compreendidos |
| **Descrição** | O modelo em cascata só deve ser recomendado quando: **(1)** os requisitos são estáveis e bem compreendidos desde o início; **(2)** o projeto é de baixa complexidade ou é uma reimplementação de um sistema existente; **(3)** não há expectativa de mudanças significativas durante o desenvolvimento; **(4)** a equipe tem experiência com processos formais e documentação extensa. O agente deve alertar sobre os riscos de usar cascata em projetos com requisitos voláteis, pois o custo de retrabalho é alto. |
| **Objetivo** | Evitar o uso inadequado do cascata em projetos onde mudanças são frequentes, prevenindo atrasos e retrabalho. |
| **Motivação** | Cap. 2.1.1 – o cascata é inflexível e não lida bem com mudanças; deve ser usado apenas quando os requisitos são bem compreendidos. |
| **Justificativa** | O cascata ainda é útil em domínios com requisitos estáveis (ex: sistemas embarcados críticos), mas é desastroso em ambientes dinâmicos (ex: startups). |
| **Critérios de Aplicação** | Recomendação de modelo de processo quando os requisitos são conhecidos e estáveis. |
| **Critérios de Não Aplicação** | Projetos com requisitos incertos ou em domínios inovadores. |
| **Pré-condições** | Análise de estabilidade de requisitos concluída. |
| **Pós-condições** | Decisão documentada sobre o uso ou não do cascata. |
| **Restrições** | Se o cascata for escolhido, devem ser incluídas atividades formais de revisão e aprovação de cada fase. |
| **Dependências** | REGPROC-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Sistema de controle de trem: requisitos definidos por normas internacionais, estáveis. Uso do cascata é apropriado." |
| **Exemplo Negativo** | "Vamos usar cascata para desenvolver um aplicativo de entregas sob demanda, onde os requisitos mudam semanalmente." |
| **Anti-pattern** | Usar cascata porque "sempre foi assim na empresa". |
| **Métrica** | Número de projetos com cascata que sofreram mudanças significativas de requisitos (meta: baixo). |
| **Critérios de Auditoria** | Revisar projetos que usaram cascata e verificar se houve mudanças inesperadas. |

---

### REGPROC-003 – Preferência por Desenvolvimento Incremental para Sistemas com Requisitos Voláteis

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-003 |
| **Nome** | Preferência por Desenvolvimento Incremental para Sistemas com Requisitos Voláteis |
| **Descrição** | Para sistemas onde os requisitos são voláteis, incertos ou sujeitos a mudanças frequentes, o agente deve recomendar o desenvolvimento incremental (ou métodos ágeis). O desenvolvimento incremental deve ser planejado em incrementos curtos (2 a 4 semanas), com entregas frequentes ao cliente para feedback. O agente deve enfatizar os benefícios: redução do custo de mudanças, feedback precoce, e entrega de valor mais rápida. |
| **Objetivo** | Maximizar a capacidade de resposta a mudanças e reduzir o risco de entregar um sistema que não atende às necessidades reais do cliente. |
| **Motivação** | Cap. 2.1.2 – o desenvolvimento incremental tem benefícios claros para sistemas com requisitos instáveis. |
| **Justificativa** | Mudanças são mais baratas quando o sistema ainda não foi completamente especificado ou implementado. |
| **Critérios de Aplicação** | Projetos onde a estabilidade de requisitos é baixa ou incerta. |
| **Critérios de Não Aplicação** | Projetos onde os requisitos são fixos e bem compreendidos (ex: sistemas regulados). |
| **Pré-condições** | Análise de volatilidade de requisitos concluída. |
| **Pós-condições** | Definição do plano de incrementos (conteúdo, ordem, prazos). |
| **Restrições** | Cada incremento deve ser testado e validado com o cliente antes de prosseguir. |
| **Dependências** | REGPROC-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Sistema de e-commerce: requisitos mudam com frequência devido à concorrência. Recomendo desenvolvimento incremental com sprints de 2 semanas." |
| **Exemplo Negativo** | "Usar cascata para um sistema de marketplace porque o cliente diz que os requisitos estão 'quase prontos'." |
| **Anti-pattern** | Planejar incrementos longos demais (> 3 meses) que perdem o propósito de feedback rápido. |
| **Métrica** | Número de incrementos entregues vs. planejados (meta: 100%). |
| **Critérios de Auditoria** | Verificar se cada incremento foi validado pelo cliente. |
