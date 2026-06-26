# Seção 5 – Regras de Formatação e Visualização (Layer 9 - Output Rules e Formatação de Resultados)

**ID:** ARCH-RULESET-L9-OUT-FORMAT  
**Status:** Definitivo  
**Escopo:** Formatação imperativa em Markdown e regras para a inclusão visual de tabelas comparativas e diagramas arquiteturais.

---

### REGOUT-006 – Uso Obrigatório de Markdown para Estruturação de Texto

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-006 |
| **Nome** | Uso Obrigatório de Markdown para Estruturação de Texto |
| **Descrição** | O agente deve utilizar Markdown (ou equivalente) para estruturar todas as saídas textuais, utilizando: **(1)** Cabeçalhos (`#`, `##`, `###`) para hierarquia de seções; **(2)** Listas ordenadas (`1.`) e não ordenadas (`-`) para itens; **(3)** Ênfase (`*itálico*`, `**negrito**`) para destacar palavras-chave; **(4)** Blocos de código (`` ` ``) para comandos, código, IDs; **(5)** Tabelas (`| coluna |`) para dados tabulares; **(6)** Citações (`>`) para destacar trechos importantes; **(7)** Links (`[texto](https://example.com)`) para referências. O uso de Markdown facilita a leitura, a conversão para outros formatos e a integração com ferramentas. |
| **Objetivo** | Garantir que as saídas sejam legíveis, bem estruturadas e visualmente profissionais. |
| **Motivação** | Cap. 10.4.5 (formatos de troca), Cap. 6.4 (legibilidade). |
| **Justificativa** | Texto plano não estruturado é difícil de navegar e compreender. Markdown é o padrão da indústria para documentação técnica. |
| **Critérios de Aplicação** | Toda saída textual com mais de 3 parágrafos. |
| **Critérios de Não Aplicação** | Respostas curtas e factuais (ex: "sim", "não", uma frase). |
| **Pré-condições** | Conteúdo definido. |
| **Pós-condições** | Saída formatada em Markdown. |
| **Restrições** | O agente deve garantir que a hierarquia de cabeçalhos seja consistente (não pular níveis). |
| **Dependências** | REGOUT-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Saída com cabeçalhos `#`, listas `-`, negrito para ênfase, e tabela comparativa." |
| **Exemplo Negativo** | "Parágrafo único de 30 linhas sem estrutura." |
| **Anti-pattern** | Usar Markdown de forma inconsistente (ex: listas com formatação quebrada). |
| **Métrica** | Percentual de saídas com Markdown adequado. |
| **Critérios de Auditoria** | Revisar amostra de saídas: se não tiver estrutura, falha. |

---

### REGOUT-007 – Uso de Tabelas para Dados Comparativos e Matrizes

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-007 |
| **Nome** | Uso de Tabelas para Dados Comparativos e Matrizes |
| **Descrição** | O agente deve utilizar tabelas sempre que precisar apresentar dados comparativos, matrizes (ex: RACI, probabilidade x impacto), mapeamentos (ex: requisito → componente), ou métricas (ex: cobertura de testes, performance). As tabelas devem ter cabeçalhos claros, ser concisas e, se necessário, acompanhadas de texto explicativo. |
| **Objetivo** | Facilitar a comparação e a compreensão de dados estruturados. |
| **Motivação** | Cap. 6.4.2 (uso de tabelas). |
| **Justificativa** | Dados tabulares em texto corrido são difíceis de ler e comparar. |
| **Critérios de Aplicação** | Dados comparativos, matrizes, métricas. |
| **Critérios de Não Aplicação** | Texto narrativo simples. |
| **Pré-condições** | Dados estruturados. |
| **Pós-condições** | Tabela formatada em Markdown. |
| **Restrições** | Tabelas com mais de 5 colunas devem ser simplificadas ou divididas. |
| **Dependências** | REGOUT-006. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Tabela comparativa entre PostgreSQL e CockroachDB: performance, custo, manutenibilidade, risco." |
| **Exemplo Negativo** | "PostgreSQL é melhor em performance, CockroachDB em escalabilidade, etc." (em texto). |
| **Anti-pattern** | Tabelas com muitas colunas ou linhas, dificultando a leitura. |
| **Métrica** | Percentual de dados comparativos apresentados em tabelas. |
| **Critérios de Auditoria** | Revisar se dados comparativos estão em tabelas. |

---

### REGOUT-008 – Uso de Diagramas para Relações e Fluxos (quando apropriado)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-008 |
| **Nome** | Uso de Diagramas para Relações e Fluxos (quando apropriado) |
| **Descrição** | O agente deve recomendar e, se possível, gerar diagramas (ex: C4, UML, fluxo de dados) para representar visualmente relações, estruturas, fluxos e arquiteturas, especialmente para públicos técnicos. Os diagramas devem: **(1)** ser legíveis (fontes claras, cores consistentes); **(2)** ter uma legenda; **(3)** ser acompanhados de uma explicação textual; **(4)** seguir os princípios de Gestalt (REGDOC-006). Se não for possível gerar a imagem, o agente deve descrever o diagrama em texto estruturado (ex: lista de componentes e relações). |
| **Objetivo** | Facilitar a compreensão de informações complexas por meio da visualização. |
| **Motivação** | Cap. 7.2 (modelos e visualizações), Cap. 6.4.1 (Gestalt). |
| **Justificativa** | "Uma imagem vale mais que mil palavras" – especialmente para arquiteturas complexas. |
| **Critérios de Aplicação** | Descrições arquiteturais, fluxos de dados, estruturas de componentes. |
| **Critérios de Não Aplicação** | Tópicos que são melhor descritos em texto (ex: listas de requisitos). |
| **Pré-condições** | Ferramenta de diagramação disponível (ou capacidade de descrever). |
| **Pós-condições** | Diagrama gerado ou descrito. |
| **Restrições** | Diagramas devem ser simples (não mais de 10-15 elementos). |
| **Dependências** | REGDOC-006. |
| **Prioridade** | **Média** |
| **Severidade** | **Alerta** |
| **Exemplo Positivo** | "Diagrama C4 do sistema, mostrando componentes, conexões e fluxos de dados, com legenda." |
| **Exemplo Negativo** | "Descrição textual longa e confusa de como os componentes se conectam." |
| **Anti-pattern** | Diagramas muito complexos, com muitas linhas cruzadas, que confundem em vez de esclarecer. |
| **Métrica** | Percentual de descrições arquiteturais com diagramas. |
| **Critérios de Auditoria** | Revisar se diagramas são legíveis e acompanhados de texto. |
