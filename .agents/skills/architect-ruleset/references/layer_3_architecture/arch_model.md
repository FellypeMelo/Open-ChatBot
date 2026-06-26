# Seção 3 – Regras de Modelagem e Estruturação / Layer 3 (Layer 3 - Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-MODEL  
**Status:** Definitivo  
**Escopo:** Diretrizes para design orientado a serviços, Clean Architecture e Bounded Contexts.

---

### REGARCH-SW-001 – Obrigação de Modelagem Orientada a Serviços

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-001 |
| **Nome** | Obrigação de Modelagem Orientada a Serviços (Service-First Design) |
| **Descrição** | Todo componente de software deve expor sua funcionalidade por meio de serviços (interfaces providas). O design arquitetural deve sempre começar pela definição dos serviços que o componente oferece ao ambiente antes de detalhar sua implementação interna. A realização interna (processos, funções, dados) é secundária ao contrato público. |
| **Objetivo** | Garantir que a arquitetura seja orientada a contratos, promovendo baixo acoplamento e facilitando a substituição de implementações. |
| **Motivação** | Cap. 5.2 (Serviço como unidade de funcionalidade) e Cap. 5.3 (distinção entre comportamento externo e interno). |
| **Justificativa** | Projetar a partir dos serviços (outside-in) força a equipe a focar no valor entregue ao usuário final e reduz o acoplamento entre componentes. |
| **Critérios de Aplicação** | Todo novo componente, módulo ou microsserviço. |
| **Critérios de Não Aplicação** | Componentes puramente internos (ex: utilitários de logging) que não expõem serviços para outros componentes. |
| **Pré-condições** | Requisitos (RNs) que o componente deve atender foram identificados. |
| **Pós-condições** | O componente possui uma especificação de serviço (ex: OpenAPI, interface Java, proto) definida antes da implementação. |
| **Restrições** | A especificação do serviço deve ser versionada e revisada antes da implementação (Design Review). |
| **Dependências** | REGREQ-004, REGREQ-011. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Antes de codificar o 'VariantClassifier', especifiquei seu serviço: `classifyVariant(Variant variant)` retorna `Classification`. Esta interface é o contrato. A implementação concreta (usando ACMG) virá depois." |
| **Exemplo Negativo** | Codificar o classificador e depois "descobrir" sua interface. |
| **Anti-pattern** | Expor detalhes internos (ex: tabelas de banco) como parte do serviço. |
| **Métrica** | Percentual de componentes com especificação de serviço anterior à implementação (meta: 100%). |
| **Critérios de Auditoria** | Revisar histórico de desenvolvimento: se a interface foi criada após a implementação, falha. |

---

### REGARCH-SW-002 – Regra de Dependência Apontando para Abstrações (Dependency Inversion)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-002 |
| **Nome** | Regra de Dependência Apontando para Abstrações (Dependency Inversion Principle) |
| **Descrição** | Módulos de alto nível (domínio, negócio) não podem depender de módulos de baixo nível (infraestrutura, bibliotecas). Ambos devem depender de abstrações (interfaces). Além disso, abstrações não podem depender de detalhes; detalhes devem depender de abstrações. Consequentemente, o domínio define as interfaces (portas) que a infraestrutura implementa (adaptadores). |
| **Objetivo** | Isolar a lógica de negócio de mudanças tecnológicas (bancos, filas, bibliotecas externas). |
| **Motivação** | Cap. 5.2 (camadas) e Cap. 6.3.4 (separação de partes independentes). |
| **Justificativa** | Dependências concretas para infraestrutura tornam o domínio frágil e difícil de testar (ex: testes unitários exigem banco real). |
| **Critérios de Aplicação** | Toda relação de dependência entre módulos. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Módulos identificados. |
| **Pós-condições** | O grafo de dependências aponta de infraestrutura → domínio, nunca o contrário. |
| **Restrições** | Frameworks (ex: Spring, Django) são considerados infraestrutura e devem ser isolados por adaptadores. |
| **Dependências** | REGARCH-SW-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Domínio define a interface `VariantRepository`. A infraestrutura (módulo de banco) implementa `PostgresVariantRepository`. O domínio não sabe que é Postgres." |
| **Exemplo Negativo** | "O módulo de classificação importa diretamente `psycopg2` para acessar o banco." |
| **Anti-pattern** | Usar injeção de dependência apenas para "fingir" que está seguindo a regra, mas ainda usando implementações concretas em tempo de execução. |
| **Métrica** | Número de dependências diretas Domínio → Infraestrutura (meta: zero). |
| **Critérios de Auditoria** | Análise estática do grafo de dependências de código (ex: ferramentas como JDepend, ArchUnit). |

---

### REGARCH-SW-003 – Proibição de Dependências Circulares entre Módulos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-003 |
| **Nome** | Proibição de Dependências Circulares entre Módulos |
| **Descrição** | O grafo de dependências entre módulos, pacotes, serviços ou bounded contexts deve ser acíclico (DAG - Directed Acyclic Graph). Dependências circulares (A depende de B, B depende de A) são proibidas. Se um ciclo for detectado, o agente deve sugerir a quebra do ciclo por meio de: (1) extração de uma acoplagem comum (abstração), (2) introdução de um módulo de mediação (ex: orquestrador), ou (3) uso de eventos assíncronos para quebrar o acoplamento temporal. |
| **Objetivo** | Preservar a manutenibilidade, testabilidade e compreensão da arquitetura. |
| **Motivação** | Cap. 5.7 (relações não podem ser circulares), Cap. 6.4.2 (evitar linhas cruzadas) e Cap. 8.3.1 (análise de impacto em ciclos é impossível). |
| **Justificativa** | Ciclos geram acoplamento excessivo, dificultam testes (mock de ciclo) e tornam a análise de impacto imprecisa. |
| **Critérios de Aplicação** | Toda relação de dependência entre módulos/pacotes. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Relação de dependência definida. |
| **Pós-condições** | Grafo mantido como DAG. |
| **Restrições** | Se um ciclo for inevitável (ex: legacy), o agente deve documentá-lo como dívida técnica e priorizar sua eliminação. |
| **Dependências** | REGREQ-012 (rastreabilidade circular), REGARCH-SW-002. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Módulo A depende de B, B depende de C. C não depende de A (acíclico)." |
| **Exemplo Negativo** | "Módulo A depende de B; B depende de C; C depende de A." |
| **Anti-pattern** | Resolver ciclos com dependências bidirecionais implícitas (ex: callbacks) em vez de refatorar a estrutura. |
| **Métrica** | Número de ciclos no grafo de dependências (meta: zero). |
| **Critérios de Auditoria** | Análise estática com ferramenta de análise de dependências. |

---

### REGARCH-SW-004 – Estruturação por Camadas Obrigatória (Clean/Hexagonal Architecture)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-004 |
| **Nome** | Estruturação por Camadas Obrigatória (Clean/Hexagonal Architecture) |
| **Descrição** | Todo sistema deve ser estruturado em, no mínimo, três camadas lógicas: **(1) Camada de Domínio**: contém as entidades, value objects, agregados, regras de negócio e serviços de domínio. Não possui dependências externas. **(2) Camada de Aplicação (ou Casos de Uso)**: orquestra os serviços de domínio e gerencia os fluxos transacionais. Depende de interfaces (portas) definidas pelo domínio. **(3) Camada de Infraestrutura**: contém os adaptadores para bancos, APIs externas, filas, mensageria, e frameworks. Depende do domínio e da aplicação (implementa as portas). |
| **Objetivo** | Isolar as regras de negócio (camada mais estável) das tecnologias (camada mais volátil). |
| **Motivação** | Cap. 5.2 (camadas: negócio, aplicação, tecnologia) e Cap. 6.3.4 (layers como mecanismo de estabilidade). |
| **Justificativa** | Sistemas sem separação clara de camadas são difíceis de testar, evoluir e entender. A estrutura em camadas é o padrão arquitetural mais consolidado e eficaz. |
| **Critérios de Aplicação** | Toda nova aplicação, serviço ou módulo significativo. |
| **Critérios de Não Aplicação** | Scripts utilitários ou lambdas simples (ex: uma função de transformação). |
| **Pré-condições** | Requisitos analisados. |
| **Pós-condições** | A estrutura de diretórios/pacotes reflete as três camadas. |
| **Restrições** | A camada de Domínio não pode importar nada da Infraestrutura (incluindo anotações de framework, ORM, etc.). |
| **Dependências** | REGARCH-SW-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Estrutura de pacotes: `domain/` (entidades, agregados), `application/` (casos de uso), `infrastructure/` (repositórios Postgres, clientes HTTP)." |
| **Exemplo Negativo** | "Código de acesso a banco diretamente dentro da classe de domínio." |
| **Anti-pattern** | Criar uma "camada de serviço" anêmica que apenas delega para DAOs, sem conter lógica de negócio real. |
| **Métrica** | Percentual de módulos seguindo a estrutura de camadas (meta: 100% para novas implementações). |
| **Critérios de Auditoria** | Análise de estrutura de diretórios e imports entre camadas. |

---

### REGARCH-SW-005 – Uso Obrigatório de Bounded Contexts e Context Maps (DDD)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-005 |
| **Nome** | Uso Obrigatório de Bounded Contexts e Context Maps (DDD) |
| **Descrição** | Para sistemas com mais de três módulos ou equipes diferentes, o agente deve recomendar e aplicar a delimitação de Bounded Contexts. Cada Bounded Context deve ter seu próprio modelo de domínio, linguagem ubíqua e, preferencialmente, seu próprio armazenamento de dados. A comunicação entre contextos deve ser definida por um Context Map explícito, usando padrões como: (1) **Parceria** (cooperação estreita), (2) **Shared Kernel** (modelo compartilhado – com cautela), (3) **Customer-Supplier** (interface de provedor), (4) **Conformist** (segue o modelo do fornecedor), ou (5) **Anti-Corruption Layer** (tradutor para proteger o domínio). |
| **Objetivo** | Gerenciar a complexidade de sistemas grandes, permitindo que equipes diferentes evoluam seus modelos de forma independente. |
| **Motivação** | Cap. 9.3.2 (infraestrutura e domínios), Cap. 9.3.3 (áreas de aplicação e negócio). |
| **Justificativa** | Modelos de domínio grandes e monolíticos geram conflitos semânticos (ex: "Cliente" significa uma coisa para Vendas e outra para Cobrança). Contextos delimitados resolvem esse problema. |
| **Critérios de Aplicação** | Sistemas com > 3 módulos funcionais ou > 1 equipe de desenvolvimento. |
| **Critérios de Não Aplicação** | Aplicações simples, de equipe única, com < 3 módulos. |
| **Pré-condições** | Mapeamento funcional do sistema. |
| **Pós-condições** | Bounded Contexts definidos e Context Map documentado. |
| **Restrições** | Cada Bounded Context deve ter seu próprio artefato (ex: JAR, serviço, namespace). |
| **Dependências** | REGARCH-SW-004. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Contexto 'Genômica' (classificação) e Contexto 'Laudos' (geração de relatórios). Context Map: Anti-Corruption Layer para traduzir 'Classificação' para 'Patogenicidade' no contexto de Laudos." |
| **Exemplo Negativo** | "Um único modelo de domínio com 50 classes, usado por todas as áreas." |
| **Anti-pattern** | Criar Bounded Contexts idênticos (duplicação de modelo) sem justificativa clara. |
| **Métrica** | Número de Bounded Contexts / complexidade do sistema. |
| **Critérios de Auditoria** | Revisar se os Bounded Contexts estão alinhados com a estrutura organizacional (Lei de Conway – REGARCH-SW-013). |
