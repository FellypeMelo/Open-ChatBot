# Seção 5 – Regras de Viewpoints e Visualização (Layer 6 - Documentação e Comunicação Técnica)

**ID:** ARCH-RULESET-L6-DOC-VIEW  
**Status:** Definitivo  
**Escopo:** Distinção entre Viewpoints (parâmetros de modelagem) e Views (diagramas gerados) e categorização por propósitos comunicativos.

---

### REGDOC-007 – Separação entre Viewpoint e View (Onde vs. O que)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-007 |
| **Nome** | Separação entre Viewpoint e View (Onde vs. O que) |
| **Descrição** | O agente deve garantir que cada visão (view) seja construída a partir de um ponto de vista (viewpoint) formalmente definido. O viewpoint especifica: **(1)** stakeholders e preocupações atendidas; **(2)** meta-modelo (conceitos e relações permitidas); **(3)** critérios de seleção (quais elementos do modelo são incluídos); **(4)** formato de apresentação (diagrama, tabela, relatório). A view é o resultado da aplicação do viewpoint a um modelo. O agente não pode criar uma view sem um viewpoint definido (ex: "desenhar um diagrama aleatório"). |
| **Objetivo** | Garantir consistência, rastreabilidade e reutilização das visões arquiteturais. |
| **Motivação** | Cap. 3.2.4, Cap. 7.1 – definição formal de Viewpoint e View. |
| **Justificativa** | Views sem viewpoints definidos são arbitrárias, não reutilizáveis e difíceis de validar. |
| **Critérios de Aplicação** | Toda visualização de arquitetura (diagrama, tabela, relatório). |
| **Critérios de Não Aplicação** | Esboços rápidos (whiteboard) em reuniões, que devem ser formalizados posteriormente. |
| **Pré-condições** | Viewpoint definido (ex: "Visão de Componentes"). |
| **Pós-condições** | View criada a partir do viewpoint. |
| **Restrições** | Se o viewpoint não existir, o agente deve criá-lo antes da view. |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Viewpoint 'Visão de Segurança' define: stakeholders (CISO), preocupações (acesso, criptografia), meta-modelo (componentes, dados, PSs). View: diagrama mostrando fluxo de dados sensíveis." |
| **Exemplo Negativo** | "Desenhei um diagrama de fluxo de dados sem definir por que esses elementos foram escolhidos." |
| **Anti-pattern** | Ter muitos viewpoints, mas nenhum view real. |
| **Métrica** | Percentual de views com viewpoint associado. |
| **Critérios de Auditoria** | Revisar cada diagrama: se não tiver viewpoint documentado, falha. |

---

### REGDOC-008 – Três Propósitos de Viewpoints (Design, Decidir, Informar) – Classificação Obrigatória

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-008 |
| **Nome** | Três Propósitos de Viewpoints (Design, Decidir, Informar) – Classificação Obrigatória |
| **Descrição** | O agente deve classificar cada viewpoint em um dos três propósitos (Cap. 7.4.1): **(1) Designing**: para arquitetos e designers (ex: diagrama de componentes, fluxo de dados); **(2) Deciding**: para tomadores de decisão (ex: landscape maps, matrizes de trade-off, relatórios de custo); **(3) Informing**: para comunicação geral (ex: cartoon de processo, apresentação executiva). A classificação determina o nível de detalhe, o formato e a linguagem utilizados. |
| **Objetivo** | Adaptar a visualização ao público e ao propósito, maximizando a eficácia da comunicação. |
| **Motivação** | Cap. 7.4.1 – classificação de viewpoints por propósito. |
| **Justificativa** | Um diagrama técnico (Designing) é inadequado para uma apresentação executiva (Deciding), e vice-versa. |
| **Critérios de Aplicação** | Toda view criada. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Propósito da view definido. |
| **Pós-condições** | Viewpoint classificado. |
| **Restrições** | O mesmo modelo pode ter views de diferentes propósitos. |
| **Dependências** | REGDOC-007. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Viewpoint 'Visão de Deploy' – classificação: Designing (para engenheiros de infra). Viewpoint 'Landscape Map de Aplicações' – classificação: Deciding (para gestores)." |
| **Exemplo Negativo** | "Usar um diagrama de classes UML em uma apresentação para o CEO." |
| **Anti-pattern** | Ter apenas views do tipo Designing, ignorando Deciding e Informing. |
| **Métrica** | Distribuição dos tipos de views (ideal: equilíbrio entre os 3 tipos). |
| **Critérios de Auditoria** | Revisar se cada view tem propósito definido. |
