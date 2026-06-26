# Seção 2 – Princípios Fundamentais (Layer 12 - Testes e Garantia de Qualidade)

**ID:** ARCH-RULESET-L12-TEST-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Princípios conceituais permanentes regulando testes e controle de qualidade de software.

---

## Princípios de Qualidade

### Princípio 01 – Testes como Atividade Contínua, Não como Fase Final
Testes não são uma atividade que ocorre apenas no final do desenvolvimento. Devem ser incorporados em todas as fases, desde a especificação até a implantação. O desenvolvimento guiado por testes (TDD) é um exemplo de como testar antes mesmo de codificar.

### Princípio 02 – Validação vs. Verificação são Complementares
Validação responde à pergunta: *"Estamos construindo o produto certo?"* (atende às necessidades do cliente). Verificação responde à pergunta: *"Estamos construindo o produto corretamente?"* (em conformidade com a especificação). Ambas são necessárias e devem ser planejadas e executadas de maneira independente.

### Princípio 03 – Qualidade é um Requisito Não-Funcional (RT)
Qualidade não é opcional nem secundária. Requisitos de qualidade (ex: confiabilidade, performance, portabilidade, manutenibilidade e segurança) devem ser especificados, validados, testados e auditados com o mesmo rigor aplicado aos requisitos funcionais.

### Princípio 04 – Testes Automatizados são Essenciais para Regressão
Testes manuais repetitivos são caros, lentos e propensos a falhas humanas. Testes automatizados (especialmente testes unitários e de integração) permitem uma regressão rápida, confiável e barata, o que é essencial para o desenvolvimento ágil e iterativo.

### Princípio 05 – Revisões e Inspeções são Complementares aos Testes
Enquanto os testes automatizados encontram defeitos em tempo de execução (dinâmicos), as revisões e inspeções estáticas encontram problemas no design, código fonte, contratos e documentações antes de serem executados. A combinação das duas abordagens é exponencialmente mais eficiente.

### Princípio 06 – Métricas de Qualidade Orientam Melhorias
O que não é medido não pode ser gerenciado nem evoluído. Métricas objetivas como cobertura de código, complexidade ciclomática, densidade de defeitos e estimativa de dívida técnica devem ser acompanhadas de perto para orientar ações corretivas e refatorações.

### Princípio 07 – Qualidade é Responsabilidade de Todos
A qualidade do software não é responsabilidade exclusiva de uma equipe isolada de QA (Quality Assurance). Desenvolvedores, arquitetos de software, gerentes de produto (POs) e scrum masters compartilham coletivamente o dever de manter e zelar pela qualidade do produto.
