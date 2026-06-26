# Seção 2 – Princípios Fundamentais da Arquitetura de Software (Layer 3)

**ID:** ARCH-RULESET-L3-ARCH-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Diretrizes conceituais de design para tradução de requisitos em código e infraestrutura.

### Princípio 01 – Separação Estrita entre Serviço e Realização (Service-Implementation Separation)
O contrato do serviço (interface pública) deve ser completamente independente de sua implementação. Mudanças na realização (ex: troca de banco, algoritmo) não podem impactar o contrato. Este é o princípio fundamental da Orientação a Serviços (Cap. 5.2).

### Princípio 02 – Isolamento do Domínio (Domain Isolation – DDD/Hexagonal)
A lógica de negócio (regras RN) deve residir em um núcleo de domínio isolado, sem dependências diretas de infraestrutura (bancos, APIs externas, frameworks). A infraestrutura deve depender do domínio, e não o contrário (Dependency Inversion).

### Princípio 03 – Baixo Acoplamento, Alta Coesão
Componentes devem ser fracamente acoplados (comunicação via interfaces/serviços) e fortemente coesos (funções relacionadas agrupadas). Isso maximiza a manutenibilidade e a testabilidade.

### Princípio 04 – Rastreabilidade Física Obrigatória
Todo componente lógico (ex: módulo, serviço) deve ser mapeado a um ou mais artefatos físicos (ex: arquivo JAR, container, tabela). A trilha de rastreabilidade deve atravessar os três mundos (Social → Simbólico → Físico), conforme Cap. 9.2.2.

### Princípio 05 – Evolução Controlada por Contratos
Mudanças em contratos (APIs públicas, eventos) devem seguir um processo de versionamento explícito (ex: Semantic Versioning) e nunca quebrar clientes existentes sem um período de depreciação documentado.

### Princípio 06 – Governança por Dependências Explícitas
Todas as dependências entre componentes devem ser explícitas (ex: arquivo de configuração, injeção de dependência, manifesto). Dependências implícitas (ex: acesso direto a tabelas de outro módulo) são proibidas.
