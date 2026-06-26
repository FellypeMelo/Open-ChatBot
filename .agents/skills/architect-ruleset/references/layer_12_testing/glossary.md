# Seção 1 – Glossário Formal (Layer 12 - Testes e Garantia de Qualidade)

**ID:** ARCH-RULESET-L12-TEST-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Definições canônicas obrigatórias de terminologias de teste de software e garantia de qualidade segundo Sommerville.

---

## Termos Canônicos

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **Teste de Software** | Execução de um programa com dados artificiais para verificar se ele se comporta conforme esperado e para descobrir defeitos. | Cap. 8 |
| **Validação (Validation)** | Processo de verificar se o sistema atende às necessidades e expectativas do cliente ("estamos construindo o produto certo?"). | Cap. 8 |
| **Verificação (Verification)** | Processo de verificar se o sistema está em conformidade com sua especificação ("estamos construindo o produto corretamente?"). | Cap. 8 |
| **Teste Unitário** | Teste de uma unidade isolada de código (ex: método, classe). Deve ser rápido, determinístico e independente de infraestrutura (uso de mocks/stubs). | Cap. 8.1.1 |
| **Teste de Componente** | Teste de um grupo de unidades integradas, focando em interfaces e interações entre componentes. | Cap. 8.1.3 |
| **Teste de Sistema** | Teste do sistema integrado como um todo, verificando funcionalidades, performance e segurança. | Cap. 8.1.4 |
| **Teste de Liberação (Release Testing)** | Teste de uma versão do sistema antes de ser liberada para usuários, geralmente realizado por uma equipe independente. | Cap. 8.3 |
| **Teste de Aceitação (Acceptance Testing)** | Teste realizado pelo cliente para decidir se o sistema deve ser aceito e colocado em produção. | Cap. 8.4 |
| **Teste Alfa (Alpha Testing)** | Teste realizado com usuários no ambiente do desenvolvedor, com feedback direto à equipe. | Cap. 8.4 |
| **Teste Beta (Beta Testing)** | Teste realizado com usuários em seu próprio ambiente, com uma versão quase final do sistema. | Cap. 8.4 |
| **TDD (Test-Driven Development)** | Prática onde os testes automatizados são escritos antes do código, seguindo o ciclo: escrever teste → verificar falha → escrever código → verificar sucesso → refatorar. | Cap. 8.2 |
| **Teste Baseado em Requisitos** | Abordagem de teste onde os casos de teste são derivados diretamente dos requisitos do sistema. | Cap. 8.3.1 |
| **Teste de Cenário (Scenario Testing)** | Abordagem de teste onde os casos de teste são baseados em histórias de uso realistas (cenários). | Cap. 8.3.2 |
| **Teste de Performance** | Teste que avalia o desempenho do sistema sob carga, incluindo tempo de resposta e throughput. | Cap. 8.3.3 |
| **Teste de Estresse (Stress Testing)** | Teste que submete o sistema a cargas extremas para avaliar seu comportamento em condições de pico e sua capacidade de recuperação. | Cap. 8.3.3 |
| **Teste de Segurança** | Teste que avalia a capacidade do sistema de resistir a ataques maliciosos, incluindo testes de invasão e análise de vulnerabilidades. | Cap. 15.3 |
| **Revisão de Código (Code Review)** | Processo sistemático de inspeção de código por pares para identificar defeitos, violações de estilo e oportunidades de melhoria. | Cap. 24.3 |
| **Inspeção de Código (Code Inspection)** | Tipo formal de revisão de código, com papéis definidos (moderador, leitor, escriba) e checklist de erros comuns. | Cap. 24.3.2 |
| **Cobertura de Testes** | Métrica que indica a porcentagem de código (linhas, branches, condições) executada por testes automatizados. | Cap. 8.1.2 |
| **Dívida Técnica** | Custo implícito de retrabalho causado pela escolha de soluções rápidas em vez de abordagens melhores. | Cap. 9.3.3 |
| **Métrica de Qualidade** | Medida objetiva de um atributo do software ou processo, usada para avaliar e melhorar a qualidade. Exemplos: complexidade ciclomática, cobertura de testes, índice de manutenibilidade. | Cap. 24.4 |
| **ISO 9001** | Norma internacional para sistemas de gestão da qualidade, aplicável ao desenvolvimento de software. | Cap. 24.2.1 |
| **CMMI** | Modelo de maturidade de processos que define níveis de capacidade e boas práticas para desenvolvimento de software. | Cap. 26.5 |
