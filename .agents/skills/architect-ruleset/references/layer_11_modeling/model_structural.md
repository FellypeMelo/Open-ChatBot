# Seção 4 – Regras de Diagramas UML e Modelagem Estrutural (Layer 11 - Modelagem e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-STRUCTURAL  
**Status:** Definitivo  
**Escopo:** Diretrizes de diagramas de classe, caso de uso, sequência e estados para modelagem estrutural e interações.

---

### REGMODEL-003 – Uso de Diagramas de Classes para Modelagem da Estrutura Estática

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-003 |
| **Nome** | Uso de Diagramas de Classes para Modelagem da Estrutura Estática |
| **Descrição** | O agente deve criar um diagrama de classes UML para representar a estrutura estática do sistema, incluindo: **(1)** classes com seus atributos e operações; **(2)** associações entre classes com multiplicidades (ex: 1, 0..*, 1..*); **(3)** generalizações (herança); **(4)** agregações e composições (todo-parte); **(5)** dependências. O diagrama deve ser mantido sincronizado com o código (ou gerado a partir dele, em abordagens de engenharia reversa). O agente deve evitar diagramas de classes excessivamente complexos; se necessário, dividir em visões por pacotes ou subsistemas. |
| **Objetivo** | Fornecer uma visão clara e concisa da estrutura do sistema para comunicação e design. |
| **Motivação** | Cap. 5.3.1 – diagramas de classes são a espinha dorsal da modelagem estrutural. |
| **Justificativa** | O diagrama de classes é o artefato mais importante para comunicação entre arquitetos e desenvolvedores. |
| **Critérios de Aplicação** | Todo projeto orientado a objetos. |
| **Critérios de Não Aplicação** | Projetos não orientados a objetos (ex: scripts funcionais). |
| **Pré-condições** | Classes identificadas e responsabilidades definidas. |
| **Pós-condições** | Diagrama de classes criado e revisado. |
| **Restrições** | O diagrama deve ser legível (evitar > 20 classes por diagrama; usar pacotes para agrupar). |
| **Dependências** | REGMODEL-001, REGMODEL-002. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Diagrama de classes do sistema de e-commerce: classes (Cliente, Pedido, Item, Produto, Pagamento), associações com multiplicidades, e herança (PagamentoCartao, PagamentoBoleto)." |
| **Exemplo Negativo** | "Não temos diagrama de classes; o código é o design." (a menos que seja um projeto trivial). |
| **Anti-pattern** | Diagrama de classes com centenas de classes sem organização por pacotes. |
| **Métrica** | Percentual de módulos com diagrama de classes atualizado. |
| **Critérios de Auditoria** | Verificar se o diagrama de classes existe e está sincronizado com o código. |

---

### REGMODEL-004 – Uso de Diagramas de Casos de Uso para Capturar Requisitos Funcionais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-004 |
| **Nome** | Uso de Diagramas de Casos de Uso para Capturar Requisitos Funcionais |
| **Descrição** | O agente deve criar diagramas de casos de uso para representar as interações entre atores (usuários ou sistemas externos) e o sistema. Cada caso de uso deve ser descrito com: **(1)** nome e descrição; **(2)** ator principal; **(3)** pré-condições; **(4)** fluxo principal (passos); **(5)** fluxos alternativos e de exceção; **(6)** pós-condições. O agente deve garantir que os casos de uso cubram todos os requisitos funcionais identificados. |
| **Objetivo** | Capturar e comunicar os requisitos funcionais de forma compreensível para stakeholders. |
| **Motivação** | Cap. 5.2.1 – casos de uso são amplamente usados para elicitar e documentar requisitos. |
| **Justificativa** | Casos de uso são a base para identificação de objetos e cenários de teste. |
| **Critérios de Aplicação** | Projetos com interações com usuários ou sistemas externos. |
| **Critérios de Não Aplicação** | Sistemas puramente de processamento em lote sem interação externa. |
| **Pré-condições** | Requisitos funcionais identificados. |
| **Pós-condições** | Modelo de casos de uso aprovado pelos stakeholders. |
| **Restrições** | Cada caso de uso deve ser rastreável a um ou mais requisitos. |
| **Dependências** | REGREQ-004 (requisitos estruturados). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Caso de uso 'Realizar Pedido': ator (Cliente), fluxo principal (selecionar produtos, finalizar, pagar), fluxo alternativo (pagamento recusado)." |
| **Exemplo Negativo** | "Caso de uso 'Realizar Pedido' descrito em uma linha." |
| **Anti-pattern** | Criar casos de uso para cada ação trivial (ex: "clicar no botão"). |
| **Métrica** | Percentual de requisitos cobertos por casos de uso. |
| **Critérios de Auditoria** | Verificar se todos os requisitos funcionais têm casos de uso associados. |

---

### REGMODEL-005 – Uso de Diagramas de Sequência para Modelar Interações Detalhadas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-005 |
| **Nome** | Uso de Diagramas de Sequência para Modelar Interações Detalhadas |
| **Descrição** | Para cada cenário relevante (ex: fluxo principal de um caso de uso), o agente deve criar um diagrama de sequência UML que mostre a ordem cronológica das mensagens entre objetos. O diagrama deve incluir: **(1)** objetos (instâncias de classes) participantes; **(2)** linhas de vida; **(3)** mensagens com setas indicando direção e tipo (síncrono, assíncrono); **(4)** ativações (barras de execução); **(5)** fragmentos de interação (alt, loop, opt) para representar alternativas e repetições. |
| **Objetivo** | Detalhar a dinâmica de interação entre objetos, útil para design fino e validação. |
| **Motivação** | Cap. 5.2.2 – diagramas de sequência mostram a ordem das interações. |
| **Justificativa** | Diagramas de sequência ajudam a validar se as interações estão alinhadas com os requisitos e a identificar potenciais problemas (ex: mensagens em falta). |
| **Critérios de Aplicação** | Cenários complexos ou críticos de interação. |
| **Critérios de Não Aplicação** | Interações triviais (ex: getter/setter). |
| **Pré-condições** | Casos de uso definidos. |
| **Pós-condições** | Diagrama de sequência aprovado. |
| **Restrições** | O agente deve garantir que os objetos no diagrama sejam instâncias das classes já identificadas. |
| **Dependências** | REGMODEL-004, REGMODEL-001. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Diagrama de sequência para 'Realizar Pedido': Cliente → SistemaPedido → ProcessadorPagamento → ServicoExterno." |
| **Exemplo Negativo** | "Não usamos diagramas de sequência; os devs entendem o fluxo." |
| **Anti-pattern** | Diagrama de sequência com muitas mensagens (complexidade excessiva). |
| **Métrica** | Percentual de casos de uso complexos com diagrama de sequência. |
| **Critérios de Auditoria** | Verificar se cenários críticos têm diagrama de sequência. |

---

### REGMODEL-006 – Uso de Diagramas de Estados para Objetos com Ciclo de Vida Complexo

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-006 |
| **Nome** | Uso de Diagramas de Estados para Objetos com Ciclo de Vida Complexo |
| **Descrição** | Para objetos que passam por diferentes estados ao longo de seu ciclo de vida (ex: Pedido, Processo, Entrega), o agente deve criar um diagrama de estados UML. O diagrama deve incluir: **(1)** estados (retângulos arredondados); **(2)** transições (setas com rótulos de eventos); **(3)** condições de guarda; **(4)** ações (atividades executadas em um estado). O agente deve garantir que todos os estados possíveis sejam mapeados e que as transições sejam consistentes. |
| **Objetivo** | Capturar o comportamento dependente de estado, essencial para sistemas transacionais e de workflow. |
| **Motivação** | Cap. 5.4.2 – diagramas de estados são úteis para objetos com comportamento dependente de estado. |
| **Justificativa** | Objetos com ciclos de vida complexos (ex: Pedido "criado → pago → enviado → entregue") são propensos a erros se o comportamento dependente de estado não for modelado. |
| **Critérios de Aplicação** | Objetos com ciclo de vida com > 3 estados. |
| **Critérios de Não Aplicação** | Objetos com comportamento simples (ex: utilitários). |
| **Pré-condições** | Classe identificada. |
| **Pós-condições** | Diagrama de estados criado e revisado. |
| **Restrições** | O diagrama deve ser validado com os stakeholders para garantir que captura todos os estados e transições esperados. |
| **Dependências** | REGMODEL-003. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Diagrama de estados do Pedido: estados (Novo, Pago, Enviado, Entregue, Cancelado); transições com eventos (pagamentoConfirmado, despachado, entregue)." |
| **Exemplo Negativo** | "O pedido pode ser cancelado em qualquer estado, mas não modelamos isso." |
| **Anti-pattern** | Diagrama de estados com transições impossíveis (ex: "Entregue" → "Novo"). |
| **Métrica** | Número de classes com diagrama de estados / total de classes com comportamento dependente de estado. |
| **Critérios de Auditoria** | Verificar se objetos com ciclo de vida crítico têm diagrama de estados. |
