# Seção 7 – Regras de Boas Práticas de Implementação (Layer 11 - Modelagem e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-IMPLEMENTATION  
**Status:** Definitivo  
**Escopo:** Diretrizes de implementação orientada a objetos (encapsulamento, validação e exceções).

---

### REGMODEL-011 – Aplicação de Princípios de Encapsulamento e Ocultação de Informação

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-011 |
| **Nome** | Aplicação de Princípios de Encapsulamento e Ocultação de Informação |
| **Descrição** | O agente deve garantir que as classes sigam os princípios de encapsulamento: **(1)** atributos devem ser privados (ou protegidos) e acessados via métodos públicos (getters/setters) apenas quando necessário; **(2)** detalhes internos de implementação devem ser ocultos das classes clientes; **(3)** a interface pública deve ser mínima e bem definida. O agente deve evitar classes com atributos públicos ou com acoplamento excessivo. |
| **Objetivo** | Promover baixo acoplamento e alta coesão, facilitando manutenção e evolução. |
| **Motivação** | Cap. 7.3.1 – encapsulamento é fundamental para reuso e manutenibilidade. |
| **Justificativa** | Ocultação de informação reduz o impacto de mudanças e facilita a substituição de implementações. |
| **Critérios de Aplicação** | Todo projeto orientado a objetos. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Classes definidas. |
| **Pós-condições** | Atributos privados e operações públicas documentadas. |
| **Restrições** | Getters e setters devem ser justificados (ex: necessidade de validação, ou acesso externo legítimo). |
| **Dependências** | REGMODEL-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Classe Pedido: atributo 'total' é privado; acesso via getTotal() apenas." |
| **Exemplo Negativo** | "Classe Pedido: atributo 'total' é público." |
| **Anti-pattern** | Criar getters e setters para todos os atributos, mesmo sem necessidade (excesso de encapsulamento). |
| **Métrica** | Percentual de atributos privados (meta: 100%). |
| **Critérios de Auditoria** | Revisar código para verificar visibilidade de atributos. |

---

### REGMODEL-012 – Tratamento de Exceções e Validação de Entradas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-012 |
| **Nome** | Tratamento de Exceções e Validação de Entradas |
| **Descrição** | O agente deve garantir que o design inclua tratamento adequado de exceções e validação de entradas: **(1)** toda operação deve validar seus parâmetros (ex: verificar se não são nulos, se estão dentro de intervalos válidos); **(2)** exceções devem ser capturadas e tratadas de forma consistente (ex: log + retorno de erro amigável); **(3)** exceções inesperadas (ex: RuntimeException) devem ser capturadas em um nível alto (ex: camada de controller) para evitar falhas não tratadas. O agente deve documentar as exceções que cada operação pode lançar. |
| **Objetivo** | Aumentar a robustez e a confiabilidade do sistema. |
| **Motivação** | Cap. 7.3 – validação de entradas e tratamento de exceções são práticas essenciais. |
| **Justificativa** | Entradas inválidas e exceções não tratadas são as principais causas de falhas em produção. |
| **Critérios de Aplicação** | Todo projeto. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Operações definidas. |
| **Pós-condições** | Validação e tratamento de exceções implementados. |
| **Restrições** | Exceções devem ser documentadas nas interfaces das operações. |
| **Dependências** | REGMODEL-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Operação 'calcularTotal()' valida se os itens não estão vazios e lança 'CarrinhoVazioException'." |
| **Exemplo Negativo** | "Operação 'calcularTotal()' assume que os itens sempre existem." |
| **Anti-pattern** | Capturar exceções genéricas (ex: Exception) sem tratamento específico. |
| **Métrica** | Percentual de operações com validação de entrada e tratamento de exceções. |
| **Critérios de Auditoria** | Revisar código para verificar validação e tratamento de exceções. |
