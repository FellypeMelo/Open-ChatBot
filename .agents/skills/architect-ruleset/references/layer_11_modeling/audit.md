# Seção 8 – Critérios de Auditoria, Exemplo e Evolução (Layer 11 - Modelagem de Sistemas e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-AUDIT  
**Status:** Definitivo  
**Escopo:** Métodos de verificação de modelagem de sistemas, caso prático integrado de aplicação (e-commerce) e direções de evolução e extensibilidade.

---

## 1. Matriz de Auditoria de Modelagem e Projeto OO

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| **AUD-MOD-01** | Identificação de objetos com técnicas múltiplas (REGMODEL-001). | Verificar se a origem de cada classe candidata está documentada a partir de análise gramatical, cenários ou entidades de domínio. |
| **AUD-MOD-02** | Definição de atributos e operações com base em responsabilidades (REGMODEL-002). | Revisar se cada classe tem suas responsabilidades listadas e se atributos/operações são derivados diretamente delas. |
| **AUD-MOD-03** | Diagrama de classes criado e atualizado (REGMODEL-003). | Verificar se existe um diagrama de classes UML cobrindo a estrutura estática do sistema e se está sincronizado com o código. |
| **AUD-MOD-04** | Casos de uso cobrindo requisitos (REGMODEL-004). | Confirmar se todos os requisitos funcionais mapeados estão representados por atores e fluxos estruturados em diagramas de casos de uso. |
| **AUD-MOD-05** | Diagramas de sequência para cenários complexos (REGMODEL-005). | Verificar se fluxos críticos ou não-triviais de interação de casos de uso possuem diagramas de sequência com objetos, mensagens e ativações. |
| **AUD-MOD-06** | Diagramas de estados para objetos com ciclo de vida complexo (REGMODEL-006). | Revisar se objetos transacionais ou com ciclo de vida dinâmico (> 3 estados) possuem diagramas de estados especificando transições e eventos. |
| **AUD-MOD-07** | Padrões de projeto reconhecidos e aplicados (REGMODEL-007). | Avaliar se problemas recorrentes de design (ex: Observer, Façade, Iterator, Decorator) foram resolvidos por meio de padrões GoF adequados. |
| **AUD-MOD-08** | Padrões de projeto documentados (REGMODEL-008). | Confirmar se as escolhas de padrões de projeto estão registradas em diagramas específicos de participantes e devidamente documentadas (ex: via ADRs). |
| **AUD-MOD-09** | Consistência entre modelos (REGMODEL-009). | Verificar a consistência cruzada entre modelos (ex: métodos chamados em sequências e estados devem existir nas respectivas classes no diagrama de classes). |
| **AUD-MOD-10** | Rastreabilidade entre modelos e requisitos (REGMODEL-010). | Auditar o mapeamento de classes, operações e casos de uso de volta para os requisitos de software correspondentes na matriz de rastreabilidade. |
| **AUD-MOD-11** | Encapsulamento aplicado (REGMODEL-011). | Auditar o código fonte para garantir que atributos sejam privados/protegidos, expondo interfaces mínimas e ocultando detalhes de implementação. |
| **AUD-MOD-12** | Tratamento de exceções e validação (REGMODEL-012). | Confirmar se as operações validam seus parâmetros de entrada e capturam exceções adequadamente de forma documentada e robusta. |

---

## 2. Exemplo Integrado de Aplicação

**Cenário**: A equipe está projetando um sistema de e-commerce. O agente deve orientar a modelagem e o design OO do zero.

**Aplicação das Regras**:

1. **REGMODEL-001 (Identificação de Objetos)**: O agente analisa as histórias de usuário e especificações funcionais e identifica classes candidatas:
   - *Análise Gramatical*: Substantivos como `Cliente`, `Pedido`, `Produto`, `Pagamento` viram classes; verbos como `realizarPedido`, `calcularTotal` e `processarPagamento` indicam operações.
   - *Análise de Cenários*: Identifica a necessidade de um `Carrinho` de compras a partir do cenário de checkout.
   - *Entidades do Domínio*: Mapeia `ItemPedido` e `Transacao`.

2. **REGMODEL-002 (Responsabilidades)**: O agente atribui responsabilidades:
   - Classe `Pedido`: Responsável por "manter itens", "calcular total com descontos" e "gerenciar status do pedido".
   - Derivação de Atributos: `itens` (lista de ItemPedido), `dataCriacao` (data), `status` (StatusPedido).
   - Derivação de Operações: `adicionarItem()`, `removerItem()`, `calcularTotal()`.

3. **REGMODEL-003 (Diagrama de Classes)**: Cria um diagrama de classes expressando as relações:
   - `Cliente` tem associação de `1` para `0..*` com `Pedido`.
   - `Pedido` é composto por `0..*` `ItemPedido` (composição).
   - `ItemPedido` tem associação `1` para `1` com `Produto`.
   - `Pedido` tem associação `1` para `0..1` com `Pagamento`.
   - `Pagamento` serve de superclasse para generalizações: `PagamentoCartao` e `PagamentoBoleto`.

4. **REGMODEL-004 (Casos de Uso)**: Cria o diagrama de casos de uso contendo o ator `Cliente` interagindo com o caso de uso `Realizar Checkout` e o ator `Administrador` interagindo com `Atualizar Estoque`. O fluxo principal de `Realizar Checkout` detalha a adição de itens, cálculo de frete e escolha de pagamento.

5. **REGMODEL-005 (Diagrama de Sequência)**: Detalha o fluxo dinâmico de `Realizar Checkout`:
   - `Cliente` envia mensagem `finalizarCompra()` para o `ControllerCheckout`.
   - `ControllerCheckout` chama `calcularTotal()` no `Pedido`.
   - `Pedido` itera e chama `calcularSubtotal()` em cada `ItemPedido`.
   - `ControllerCheckout` envia `processarPagamento(total)` para o `GatewayPagamento`.
   - O `GatewayPagamento` retorna a confirmação de forma síncrona.

6. **REGMODEL-006 (Diagrama de Estados)**: Modela o ciclo de vida da classe `Pedido`:
   - Estados: `AguardandoPagamento` -> `Pago` -> `Enviado` -> `Entregue` (e estado alternativo `Cancelado`).
   - Transições disparadas por eventos: `confirmarPagamento()` transiciona de `AguardandoPagamento` para `Pago`.

7. **REGMODEL-007 & REGMODEL-008 (Padrões de Projeto)**:
   - Identifica que o `Estoque` e a `Logística` precisam ser atualizados automaticamente quando um `Pedido` transicionar para o estado `Pago`.
   - Recomenda a aplicação do padrão **Observer**: o `Pedido` atua como *Subject* e registra *Observers* como `GerenciadorEstoque` e `GerenciadorLogistica`.
   - Documenta essa decisão através de uma ADR (Architecture Decision Record) contendo o diagrama de participantes do padrão.

8. **REGMODEL-009 (Consistência entre Modelos)**:
   - Garante que a operação `calcularTotal()` invocada na linha de vida do objeto `Pedido` no diagrama de sequência está declarada publicamente na classe `Pedido` do diagrama de classes.

9. **REGMODEL-010 (Rastreabilidade)**:
   - Mapeia o requisito funcional `RF-042 (Cálculo de Desconto Progressivo)` diretamente para o método `calcularTotal()` da classe `Pedido`.

10. **REGMODEL-011 (Encapsulamento)**:
    - No código fonte, o atributo `itens` da classe `Pedido` é declarado como privado. O acesso é feito por meio de um método público `getItensReadOnly()` que retorna uma lista imutável, ocultando a estrutura de dados interna (ex: array list vs linked list).

11. **REGMODEL-012 (Tratamento de Exceções e Validação)**:
    - A operação `adicionarItem(produto, quantidade)` valida se a `quantidade` é maior que zero (lançando `IllegalArgumentException` caso contrário) e verifica o estoque antes de inserir, lançando `EstoqueInsuficienteException` se necessário.

**Saída Final (resumida)**:
> "Modelagem orientada a objetos do e-commerce estruturada com classes Cliente, Pedido, ItemPedido, Produto e Pagamento. Relações de composição e generalização mapeadas. Diagramas de sequência e estados detalham a dinâmica de checkout e ciclo de vida do pedido. Padrão Observer aplicado para notificações pós-pagamento. Rastreabilidade com RF-042 assegurada. Atributos encapsulados e validação de entradas ativa."

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido com sub-módulos especializados:
- **Módulo 12-A**: Modelagem Avançada de Arquitetura Física e Componentes (Diagramas de Componentes, Implantação e Pacotes).
- **Módulo 12-B**: Catálogo Completo de Padrões de Projeto (Padrões de Criação, Estruturais e Comportamentais da GoF e padrões modernos como injeção de dependência avançada).
- **Módulo 12-C**: Modelagem Domain-Driven Design (DDD) e sua relação com a UML (Entities, Value Objects, Aggregates).
- **Módulo 12-D**: Modelagem Orientada a Serviços e Sistemas Distribuídos (diagramas de atividades para workflows assíncronos e orquestrações).

Todas as extensões devem respeitar as regras base e a Constituição.
