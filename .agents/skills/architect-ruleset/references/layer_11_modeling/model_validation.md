# Seção 6 – Regras de Validação de Modelos e Rastreabilidade (Layer 11 - Modelagem e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-VALIDATION  
**Status:** Definitivo  
**Escopo:** Critérios para validação de consistência entre perspectivas UML e links de rastreabilidade a requisitos.

---

### REGMODEL-009 – Validação de Consistência entre Modelos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-009 |
| **Nome** | Validação de Consistência entre Modelos |
| **Descrição** | O agente deve garantir a consistência entre os diferentes modelos UML do sistema. Por exemplo: **(1)** As classes no diagrama de classes devem estar presentes nos diagramas de sequência e de estados; **(2)** As operações chamadas em diagramas de sequência devem estar definidas nas classes correspondentes; **(3)** Os estados definidos nos diagramas de estados devem ser compatíveis com as transições descritas nos diagramas de atividades. O agente deve usar ferramentas de validação (ex: plugins de modelagem) ou realizar revisões manuais para identificar inconsistências. |
| **Objetivo** | Garantir que os modelos sejam coerentes entre si e representem uma visão única do sistema. |
| **Motivação** | Cap. 5 – diferentes modelos apresentam perspectivas complementares, mas devem ser consistentes. |
| **Justificativa** | Inconsistências entre modelos levam a implementações defeituosas e retrabalho. |
| **Critérios de Aplicação** | Todo projeto com múltiplos modelos UML. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Modelos criados. |
| **Pós-condições** | Inconsistências identificadas e corrigidas. |
| **Restrições** | A validação deve ser feita em cada iteração do design. |
| **Dependências** | REGMODEL-003, REGMODEL-004, REGMODEL-005, REGMODEL-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Diagrama de classes tem a classe 'Pedido' com operação 'calcularTotal()'; diagrama de sequência usa 'calcularTotal()' de forma consistente." |
| **Exemplo Negativo** | "Diagrama de classes tem método 'calcularTotal()', mas o diagrama de sequência chama 'total()'." |
| **Anti-pattern** | Modelos criados por diferentes pessoas sem coordenação. |
| **Métrica** | Número de inconsistências detectadas / total de relações entre modelos. |
| **Critérios de Auditoria** | Revisar a consistência entre diagramas de classe e sequência. |

---

### REGMODEL-010 – Rastreabilidade entre Modelos e Requisitos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-010 |
| **Nome** | Rastreabilidade entre Modelos e Requisitos |
| **Descrição** | O agente deve garantir que cada elemento de modelo (classe, operação, caso de uso, estado) seja rastreável a um ou mais requisitos. A rastreabilidade pode ser documentada em: **(1)** anotações nos diagramas; **(2)** uma matriz de rastreabilidade; **(3)** ferramentas de modelagem que suportam rastreabilidade (ex: links para requisitos). O agente deve priorizar a rastreabilidade para requisitos críticos (segurança, compliance, performance). |
| **Objetivo** | Garantir que o design atenda aos requisitos e que mudanças possam ser avaliadas em termos de impacto. |
| **Motivação** | Cap. 8.3.1 – rastreabilidade é essencial para análise de impacto. |
| **Justificativa** | Sem rastreabilidade, não é possível saber se um requisito foi implementado ou qual o impacto de uma mudança. |
| **Critérios de Aplicação** | Projetos com requisitos formais (ex: plan-driven) ou críticos. |
| **Critérios de Não Aplicação** | Projetos ágeis onde a rastreabilidade pode ser mais informal, mas ainda desejável (ex: user stories → classes). |
| **Pré-condições** | Requisitos e modelos definidos. |
| **Pós-condições** | Matriz de rastreabilidade preenchida. |
| **Restrições** | Para cada requisito, deve haver pelo menos uma classe ou operação que o implemente. |
| **Dependências** | REGREQ-011 (rastreabilidade de requisitos). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RN-023 (calcular total do pedido) → classe Pedido → operação calcularTotal()." |
| **Exemplo Negativo** | "Não sabemos quais classes implementam quais requisitos." |
| **Anti-pattern** | Rastreabilidade documentada apenas em diagramas, sem link para requisitos. |
| **Métrica** | Percentual de requisitos com rastreabilidade para o design. |
| **Critérios de Auditoria** | Verificar se a matriz de rastreabilidade está atualizada. |
