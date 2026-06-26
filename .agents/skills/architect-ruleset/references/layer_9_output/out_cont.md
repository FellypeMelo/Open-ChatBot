# Seção 4 – Regras de Conteúdo e Linguagem (Layer 9 - Output Rules e Formatação de Resultados)

**ID:** ARCH-RULESET-L9-OUT-CONT  
**Status:** Definitivo  
**Escopo:** Diretrizes de clareza textual (Grice), padronização de acrônimos e proibição de adjetivos vagos ou premissas subjetivas.

---

### REGOUT-003 – Aplicação das Máximas de Grice ao Conteúdo

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-003 |
| **Nome** | Aplicação das Máximas de Grice ao Conteúdo |
| **Descrição** | O agente deve garantir que toda saída respeite as quatro máximas de Grice: **(1) Quantidade**: seja tão informativo quanto necessário, nem mais nem menos. Não inclua informações irrelevantes (ex: históricos, digressões). **(2) Qualidade**: não afirme o que é falso ou sem evidência; seja preciso. **(3) Relevância**: seja estritamente relevante ao tópico da consulta ou análise. **(4) Modo**: seja claro, breve, ordenado; evite ambiguidade, jargões desnecessários, e estrutura confusa. |
| **Objetivo** | Garantir comunicação eficaz, evitando retrabalho e mal-entendidos. |
| **Motivação** | Cap. 6.1 – Grice. |
| **Justificativa** | Comunicação ineficaz é uma das principais causas de retrabalho e desalinhamento. |
| **Critérios de Aplicação** | Toda saída. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Conteúdo definido. |
| **Pós-condições** | Saída revisada para cumprir as máximas. |
| **Restrições** | O agente pode sugerir reescrita de trechos que violem as máximas. |
| **Dependências** | REGOUT-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Resposta concisa, com informações relevantes e bem estruturada." |
| **Exemplo Negativo** | "Resposta com 50 linhas, incluindo longas digressões e informações irrelevantes." |
| **Anti-pattern** | Usar jargões desnecessários para parecer mais "técnico". |
| **Métrica** | Avaliação subjetiva de clareza por stakeholders. |
| **Critérios de Auditoria** | Revisar amostra de saídas para identificar violações das máximas. |

---

### REGOUT-004 – Uso Obrigatório de Glossário e Definição de Siglas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-004 |
| **Nome** | Uso Obrigatório de Glossário e Definição de Siglas |
| **Descrição** | O agente deve garantir que toda saída: **(1)** Utilize apenas termos definidos no Glossário do projeto (REGCON-003) ou defina novos termos na primeira ocorrência; **(2)** Defina siglas na primeira ocorrência (ex: "REST (Representational State Transfer)"); **(3)** Opcionalmente, inclua um glossário no final de relatórios extensos. O agente não pode usar siglas ou jargões sem definição clara, para evitar ambiguidade. |
| **Objetivo** | Garantir compreensão inequívoca e eliminar barreiras de entrada para leitores menos familiarizados com o domínio. |
| **Motivação** | Cap. 6.3.5 (breakdown por terminologia), Cap. 6.2.3 (registro de homônimos). |
| **Justificativa** | Siglas e jargões não definidos são a principal causa de mal-entendidos e barreiras de comunicação. |
| **Critérios de Aplicação** | Toda saída, especialmente relatórios formais e documentos. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Glossário disponível. |
| **Pós-condições** | Siglas definidas e termos consistentes com o glossário. |
| **Restrições** | Se um termo não estiver no glossário, o agente deve defini-lo e sugerir sua inclusão. |
| **Dependências** | REGCON-003. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "... utilizando um serviço de mensageria assíncrona (SQS – Simple Queue Service)..." |
| **Exemplo Negativo** | "... utilizando SQS..." (sem definição). |
| **Anti-pattern** | Usar múltiplos sinônimos para o mesmo conceito (ex: "componente", "módulo", "serviço" de forma intercambiável sem definição). |
| **Métrica** | Percentual de saídas com siglas definidas (meta: 100%). |
| **Critérios de Auditoria** | Revisar saídas para identificar siglas não definidas. |

---

### REGOUT-005 – Proibição de Linguagem Vaga e Subjetiva

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-005 |
| **Nome** | Proibição de Linguagem Vaga e Subjetiva |
| **Descrição** | O agente não pode utilizar termos vagos, subjetivos ou não mensuráveis, como "rápido", "seguro", "fácil", "adequado", "melhor", "suficiente", "ótimo", sem uma definição ou métrica objetiva associada (ex: "rápido" = "tempo de resposta < 500ms"). Quando um termo vago for utilizado pelo usuário, o agente deve solicitar esclarecimento ou propor uma definição objetiva. |
| **Objetivo** | Eliminar ambiguidades e garantir que as saídas sejam objetivas, mensuráveis e auditáveis. |
| **Motivação** | Cap. 6.3.5 (breakdown por modelo vago), Cap. 7.4.6 (critérios SMART). |
| **Justificativa** | Termos vagos geram interpretações divergentes e decisões equivocadas. |
| **Critérios de Aplicação** | Toda saída. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Conteúdo definido. |
| **Pós-condições** | Termos vagos substituídos por definições objetivas. |
| **Restrições** | Se o usuário insistir em um termo vago, o agente deve documentá-lo como uma premissa não validada. |
| **Dependências** | REGCORE-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "O sistema deve ter tempo de resposta < 500ms para 95% das requisições." |
| **Exemplo Negativo** | "O sistema deve ser rápido." |
| **Anti-pattern** | Usar termos como "melhor prática" sem especificar qual prática ou onde está documentada. |
| **Métrica** | Número de termos vagos identificados e corrigidos. |
| **Critérios de Auditoria** | Revisar saídas para identificar termos vagos não justificados. |
