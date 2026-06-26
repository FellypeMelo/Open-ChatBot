# Seção 3 – Regras de Identificação de Objetos e Classes (Layer 11 - Modelagem e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-OBJECTS  
**Status:** Definitivo  
**Escopo:** Métodos e regras para identificação de entidades de domínio, classes e suas responsabilidades.

---

### REGMODEL-001 – Identificação de Objetos Usando Técnicas Múltiplas

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-001 |
| **Nome** | Identificação de Objetos Usando Técnicas Múltiplas |
| **Descrição** | O agente deve identificar objetos e classes utilizando, no mínimo, três técnicas complementares: **(1)** Análise Gramatical: identificar substantivos em descrições textuais do sistema (requisitos, histórias de usuário) como candidatos a classes, e verbos como operações; **(2)** Análise de Cenários: identificar objetos que participam de interações descritas em casos de uso; **(3)** Identificação de Entidades do Domínio: identificar entidades tangíveis do domínio do problema (ex: Cliente, Pedido, Produto), papéis (ex: Gerente, Usuário), eventos (ex: Solicitação, Pagamento), e locais (ex: Armazém, Filial). O agente deve documentar a origem de cada classe identificada (ex: "derivada do cenário de compra"). |
| **Objetivo** | Garantir cobertura completa de classes, minimizando omissões e garantindo rastreabilidade. |
| **Motivação** | Cap. 7.1.3 – a identificação de objetos pode ser feita por análise gramatical, cenários, e entidades do domínio. |
| **Justificativa** | Nenhuma técnica isolada é suficiente; a combinação de abordagens reduz o risco de classes ausentes ou irrelevantes. |
| **Critérios de Aplicação** | Fase inicial de design de qualquer sistema orientado a objetos. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisitos do sistema disponíveis (textuais ou em casos de uso). |
| **Pós-condições** | Lista inicial de classes candidatas com rastreabilidade documentada. |
| **Restrições** | As classes candidatas devem ser refinadas em iterações subsequentes. |
| **Dependências** | REGREQ-004 (requisitos estruturados), REGMODEL-004 (casos de uso). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Classe 'Pedido' identificada a partir de substantivos nos requisitos (RN-023). Classe 'ProcessadorPagamento' derivada de cenário de checkout. Classe 'Carrinho' derivada de entidade do domínio." |
| **Exemplo Negativo** | "Identificamos objetos apenas olhando o código de um sistema legado." |
| **Anti-pattern** | Criar classes baseadas apenas em implementação, sem considerar o domínio. |
| **Métrica** | Percentual de classes com origem documentada (meta: 100%). |
| **Critérios de Auditoria** | Revisar a lista de classes candidatas; se alguma não tiver origem documentada, falha. |

---

### REGMODEL-002 – Definição de Atributos e Operações com Base em Responsabilidades

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-002 |
| **Nome** | Definição de Atributos e Operações com Base em Responsabilidades |
| **Descrição** | Para cada classe identificada, o agente deve definir atributos e operações com base nas responsabilidades da classe (o que ela sabe e o que ela faz). O agente deve: **(1)** Listar as responsabilidades da classe (ex: "mantém informações do cliente", "calcula total do pedido"); **(2)** Derivar atributos a partir das informações que a classe mantém (ex: nome, endereço); **(3)** Derivar operações a partir das ações que a classe realiza (ex: calcularTotal(), adicionarItem()). O agente deve garantir que cada operação seja rastreável a uma ou mais responsabilidades e, idealmente, a requisitos. |
| **Objetivo** | Garantir que cada classe tenha um propósito claro e bem definido, evitando classes anêmicas ou inchadas. |
| **Motivação** | Cap. 7.1.3 – objetos têm estado (atributos) e comportamento (operações). |
| **Justificativa** | Classes sem responsabilidades claras levam a designs frágeis e difíceis de manter. |
| **Critérios de Aplicação** | Definição de cada classe candidata. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Classe identificada. |
| **Pós-condições** | Atributos e operações definidos e documentados. |
| **Restrições** | Cada operação deve ter um nome que reflita seu propósito (verbo no infinitivo em português ou inglês, conforme padrão da equipe). |
| **Dependências** | REGMODEL-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Classe 'Pedido': responsabilidades (manter itens, calcular total). Atributos (itens, data, status). Operações (adicionarItem, removerItem, calcularTotal)." |
| **Exemplo Negativo** | "Classe 'Pedido' com atributos (id, nome, descricao, data, valor, desconto, etc.) sem operações claras." |
| **Anti-pattern** | Criar classes apenas com getters e setters (anêmicas) ou com dezenas de operações não relacionadas (inchadas). |
| **Métrica** | Número médio de operações por classe (meta: 3-5 para classes de domínio). |
| **Critérios de Auditoria** | Verificar se cada classe tem responsabilidades documentadas. |
