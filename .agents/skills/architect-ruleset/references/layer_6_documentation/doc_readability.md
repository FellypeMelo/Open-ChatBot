# Seção 4 – Regras de Legibilidade e Formato (Layer 6 - Documentação e Comunicação Técnica)

**ID:** ARCH-RULESET-L6-DOC-READABILITY  
**Status:** Definitivo  
**Escopo:** Métricas cognitivas e regras visuais de Gestalt, Miller e Grice aplicadas a textos e diagramas.

---

### REGDOC-004 – Aplicação das Máximas de Grice à Documentação

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-004 |
| **Nome** | Aplicação das Máximas de Grice à Documentação |
| **Descrição** | O agente deve garantir que toda documentação técnica (texto, diagramas, tabelas) respeite as quatro máximas de Grice (Cap. 6.1): **(1) Quantidade**: seja tão informativo quanto necessário, nem mais nem menos; **(2) Qualidade**: não afirme o que é falso ou sem evidência; seja preciso; **(3) Relevância**: seja estritamente relevante ao tópico do documento; **(4) Modo**: seja claro, breve, ordenado; evite ambiguidade e jargões desnecessários. Se um documento violar uma máxima, o agente deve sugerir correção. |
| **Objetivo** | Garantir comunicação eficaz e evitar breakdowns de leitura (Cap. 6.3.5). |
| **Motivação** | Cap. 6.1 – Grice (1975) aplicado à comunicação técnica. |
| **Justificativa** | Documentação prolixa, irrelevante ou ambígua gera retrabalho e mal-entendidos. |
| **Critérios de Aplicação** | Toda documentação (requisitos, arquitetura, APIs, READMEs). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | O agente deve ter capacidade de avaliar a clareza do texto. |
| **Pós-condições** | Documento revisado para cumprir as máximas. |
| **Restrições** | O agente pode sugerir reescrita de trechos que violem as máximas. |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Documento conciso, com informações relevantes e bem estruturado." |
| **Exemplo Negativo** | "Documento com 50 páginas, incluindo longas digressões sobre história de tecnologias irrelevantes." |
| **Anti-pattern** | Usar jargões técnicos desnecessários para parecer mais "profissional". |
| **Métrica** | Avaliação subjetiva de clareza por stakeholders. |
| **Critérios de Auditoria** | Revisão de amostra de documentação: se houver violações recorrentes, o agente deve alertar. |

---

### REGDOC-005 – Regra dos 7 ± 2 (Miller) para Estruturação de Documentos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-005 |
| **Nome** | Regra dos 7 ± 2 (Miller) para Estruturação de Documentos |
| **Descrição** | O agente deve garantir que nenhum documento, seção ou lista (ex: lista de requisitos, lista de componentes, lista de decisões) contenha mais de 9 itens em um mesmo nível hierárquico. Listas com mais de 9 itens devem ser agrupadas em subcategorias ou sub-seções. Este princípio respeita a limitação da memória de trabalho humana (Miller, 1956). |
| **Objetivo** | Facilitar a compreensão e a retenção de informações, evitando sobrecarga cognitiva. |
| **Motivação** | Cap. 6.4 – Miller (1956): humanos processam bem 7±2 itens. |
| **Justificativa** | Listas longas são difíceis de processar; o leitor tende a esquecer os primeiros itens ao chegar ao final. |
| **Critérios de Aplicação** | Estrutura de documentos, listas, tabelas, índices. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Estrutura do documento definida. |
| **Pós-condições** | Nenhuma lista não categorizada excede 9 itens. |
| **Restrições** | Se uma lista tiver 10 itens, o agente deve sugerir agrupamento (ex: "Requisitos Funcionais", "Requisitos Não-Funcionais"). |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Média** |
| **Severidade** | **Alerta** |
| **Exemplo Positivo** | "Lista de requisitos dividida em 3 grupos de 6, 7 e 5 itens." |
| **Exemplo Negativo** | "Lista com 35 requisitos em uma única seção." |
| **Anti-pattern** | Criar subcategorias artificiais (ex: "Requisitos 1-9", "Requisitos 10-18") sem coesão semântica. |
| **Métrica** | Número de listas com > 9 itens. |
| **Critérios de Auditoria** | Revisar a estrutura de documentos. |

---

### REGDOC-006 – Aplicação dos Princípios de Gestalt em Diagramas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-006 |
| **Nome** | Aplicação dos Princípios de Gestalt em Diagramas |
| **Descrição** | O agente deve garantir que diagramas arquiteturais (componentes, fluxos, camadas) sejam organizados segundo os princípios de percepção visual de Gestalt (Cap. 6.4.1): **(1) Proximidade**: elementos relacionados devem estar próximos; **(2) Similaridade**: elementos similares devem ter cores/formas similares; **(3) Continuidade**: linhas e conexões devem ter direções previsíveis; **(4) Fechamento**: formas devem ser completas e simétricas quando possível; **(5) Destino Comum**: elementos que se movem ou funcionam juntos devem ser agrupados (ex: setas de fluxo com a mesma direção). |
| **Objetivo** | Melhorar a legibilidade e a interpretação correta de diagramas, reduzindo a carga cognitiva. |
| **Motivação** | Cap. 6.4.1 – Gestalt principles aplicados a modelos arquiteturais. |
| **Justificativa** | Diagramas mal organizados são confusos e geram interpretações equivocadas. |
| **Critérios de Aplicação** | Todo diagrama (C4, UML, BPMN, landscape maps). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Diagrama criado. |
| **Pós-condições** | Diagrama revisado para aplicar os princípios. |
| **Restrições** | O agente pode sugerir reposicionamento de elementos e ajuste de cores. |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Média** |
| **Severidade** | **Alerta** |
| **Exemplo Positivo** | "Diagrama com componentes relacionados agrupados, cores consistentes para tipos similares, setas com direção padronizada (esquerda → direita)." |
| **Exemplo Negativo** | "Diagrama com linhas cruzadas, cores aleatórias e elementos espalhados." |
| **Anti-pattern** | Usar muitas cores ou formas diferentes, distraindo o leitor do conteúdo. |
| **Métrica** | Avaliação de legibilidade por pares. |
| **Critérios de Auditoria** | Revisar diagramas para verificar violação dos princípios. |
