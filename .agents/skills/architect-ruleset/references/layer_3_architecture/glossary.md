# Seção 1 – Glossário Formal (Layer 3 - Engenharia de Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Mapeamento semântico de termos estruturais e padrões de design.

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **Componente de Software** | Unidade estrutural autocontida que encapsula seu conteúdo e expõe sua funcionalidade por meio de interfaces. Pode ser um módulo, uma biblioteca, um microsserviço ou uma aplicação completa. | Cap. 5.5.1 |
| **Serviço** | Unidade de funcionalidade exposta ao ambiente por meio de uma interface bem definida. É a ponte entre o comportamento externo (contrato) e a realização interna (implementação). Deve ser independente de tecnologia. | Cap. 5.2 |
| **Interface** | Ponto de interação lógico (ou físico) onde os serviços de um componente podem ser acessados. Divide-se em **Provida** (oferecida ao ambiente) e **Requerida** (consumida do ambiente). | Cap. 5.3, Cap. 5.5.1 |
| **Camada (Layer)** | Mecanismo de estruturação que separa preocupações por nível de abstração e estabilidade. As camadas fundamentais são: **Apresentação**, **Aplicação/Negócio**, **Domínio**, **Infraestrutura**. | Cap. 5.2, Cap. 6.3.4 |
| **Domínio (DDD)** | Esfera de conhecimento ou atividade na qual o sistema opera. O Modelo de Domínio é a representação conceitual das regras de negócio, entidades, value objects, agregados e serviços de domínio. | Cap. 5.4 |
| **Agregado (DDD)** | Cluster de objetos de domínio tratados como uma única unidade para fins de consistência transacional. Possui uma raiz (Aggregate Root) que é a única porta de entrada. | Cap. 5.4 |
| **Entidade (DDD)** | Objeto de domínio que possui uma identidade contínua ao longo do tempo (ex: Paciente, Variante). | Cap. 5.4 |
| **Value Object (DDD)** | Objeto de domínio que é imutável e definido por seus atributos (ex: Endereço, Data de Nascimento). | Cap. 5.4 |
| **Bounded Context (DDD)** | Delimitação explícita do modelo de domínio. Cada contexto tem seu próprio modelo, linguagem e regras. Contextos se comunicam por meio de Context Maps (ex: parceria, anti-corruption layer). | Cap. 9 |
| **Artefato** | Representação física de um componente ou dado no mundo físico (ex: arquivo JAR, container Docker, tabela de banco, arquivo de configuração). | Cap. 5.6.1, Cap. 9.2.2 |
| **Dependência Estrutural** | Relação em que um componente requer a existência ou o comportamento de outro para funcionar. Dependências devem ser explícitas e, preferencialmente, direcionadas a abstrações (não a implementações concretas). | Cap. 5.7 |
| **Acoplamento** | Grau de dependência entre componentes. **Baixo acoplamento** (loose coupling) é desejável; **alto acoplamento** (tight coupling) é um anti-pattern. | Cap. 5.7, Cap. 9 |
| **Coesão** | Grau em que os elementos de um componente estão relacionados entre si. **Alta coesão** (single responsibility) é desejável. | Cap. 5.7 |
| **Portas e Adaptadores (Hexagonal Architecture)** | Padrão arquitetural onde a lógica de domínio (core) é isolada de tecnologias externas (bancos, APIs, filas) por meio de portas (interfaces) e adaptadores (implementações concretas). | Cap. 5.3, Cap. 6.3.4 |
| **Evento de Domínio** | Evento significativo que ocorre no domínio (ex: "VarianteClassificada", "LaudoGerado"). Utilizado para comunicação assíncrona entre Bounded Contexts. | Cap. 5.4.2 |
| **Contrato de API** | Especificação formal (ex: OpenAPI, gRPC) que define as operações, entradas, saídas, códigos de erro e protocolo de comunicação de um serviço. | Cap. 10.4.5 |
