# Seção 1 – Glossário Formal e Taxonomia (Layer 11 - Modelagem e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Terminologia canônica baseada nos Capítulos 5 e 7 do livro-base "Software Engineering" (Sommerville, 9ª ed.).

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **UML (Unified Modeling Language)** | Linguagem de modelagem visual padrão para especificar, visualizar, construir e documentar artefatos de sistemas de software. Possui 14 tipos de diagramas. | Cap. 5 |
| **Diagrama de Classes** | Diagrama UML que mostra as classes do sistema, seus atributos, operações e os relacionamentos (associações, generalizações, dependências) entre elas. | Cap. 5.3.1 |
| **Diagrama de Sequência** | Diagrama UML que mostra a interação entre objetos ao longo do tempo, enfatizando a ordem cronológica das mensagens trocadas. | Cap. 5.2.2 |
| **Diagrama de Estados (Statechart)** | Diagrama UML que mostra os estados possíveis de um objeto e as transições entre eles em resposta a eventos. | Cap. 5.4.2 |
| **Diagrama de Atividades** | Diagrama UML que mostra o fluxo de controle e dados de uma atividade para outra, representando processos de negócio ou fluxos de trabalho. | Cap. 5.4.1 |
| **Diagrama de Casos de Uso** | Diagrama UML que mostra os atores (usuários ou sistemas externos) e os casos de uso (funcionalidades) com que eles interagem. | Cap. 5.2.1 |
| **Diagrama de Componentes** | Diagrama UML que mostra a organização e dependências entre componentes de software. | Cap. 7.1.5 |
| **Diagrama de Implantação (Deployment)** | Diagrama UML que mostra a arquitetura física do sistema, incluindo nós (hardware) e a distribuição dos artefatos de software. | Cap. 7.3.3 |
| **Classe (OO)** | Abstração que define um conjunto de objetos com atributos (dados) e operações (comportamento) comuns. | Cap. 7.1.3 |
| **Objeto** | Instância de uma classe, com estado específico (valores de atributos) e comportamento. | Cap. 7.1.3 |
| **Associação** | Relacionamento estrutural entre classes, indicando que objetos de uma classe conhecem objetos de outra. | Cap. 5.3.1 |
| **Generalização (Herança)** | Relacionamento onde uma classe (subclasse) herda atributos e operações de outra classe (superclasse). | Cap. 5.3.2 |
| **Agregação/Composição** | Relacionamento "todo-parte" onde um objeto é composto por outros objetos. Composição é mais forte que agregação (ciclo de vida compartilhado). | Cap. 5.3.3 |
| **Padrão de Projeto (Design Pattern)** | Solução reutilizável para um problema recorrente em um contexto específico, capturando experiência e boas práticas. | Cap. 7.2 |
| **Gang of Four (GoF)** | Grupo de autores (Gamma, Helm, Johnson, Vlissides) que catalogaram 23 padrões de projeto em seu livro seminal. | Cap. 7.2 |
| **Padrão Observer** | Padrão de projeto que define uma dependência um-para-muitos entre objetos, de modo que quando um objeto muda de estado, todos os seus dependentes são notificados automaticamente. | Cap. 7.2 |
| **Padrão Façade** | Padrão de projeto que fornece uma interface unificada para um conjunto de interfaces em um subsistema, simplificando seu uso. | Cap. 7.2 |
| **Padrão Iterator** | Padrão de projeto que fornece uma maneira de acessar sequencialmente os elementos de um objeto agregado sem expor sua representação subjacente. | Cap. 7.2 |
| **Padrão Decorator** | Padrão de projeto que permite adicionar responsabilidades a um objeto dinamicamente, fornecendo uma alternativa flexível à herança. | Cap. 7.2 |
| **Injeção de Dependência (Dependency Injection)** | Técnica onde as dependências de um objeto são fornecidas externamente (ex: via construtor, setter, ou interface), em vez de serem criadas internamente. | Cap. 7.3 |
| **Host-Target Development** | Modelo de desenvolvimento onde o software é desenvolvido em uma máquina (host) e executado em outra (target), comum em sistemas embarcados. | Cap. 7.3.3 |
| **IDE (Integrated Development Environment)** | Ambiente de desenvolvimento integrado que fornece ferramentas para edição, compilação, depuração e teste de software. | Cap. 7.3.3 |
| **Reuso (Reuse)** | Uso de software existente (componentes, bibliotecas, frameworks, sistemas) para construir novos sistemas, reduzindo custo e tempo. | Cap. 7.3.1, Cap. 16 |
| **Open Source Development** | Abordagem de desenvolvimento onde o código-fonte é disponibilizado publicamente e contribuições externas são incentivadas. | Cap. 7.4 |
