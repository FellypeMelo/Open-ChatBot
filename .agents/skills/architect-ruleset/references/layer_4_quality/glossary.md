# Seção 1 – Glossário Formal (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Terminologia canônica de qualidade com base na ISO/IEC 25010 e Engenharia de Software.

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **Qualidade de Software** | Grau em que um sistema atende às necessidades explíticas e implícitas de seus stakeholders, conforme definido pela ISO/IEC 25010. Compõe-se de oito características: **adequação funcional, eficiência de desempenho, compatibilidade, usabilidade, confiabilidade, segurança, manutenibilidade, portabilidade**. | ISO/IEC 25010 / Cap. 8 |
| **Manutenibilidade** | Capacidade do sistema de ser modificado com eficácia e eficiência. Inclui **modularidade, reusabilidade, analisabilidade, modificabilidade, testabilidade**. | ISO 25010 / Cap. 6 |
| **Dívida Técnica** | Custo implícito de retrabalho causado pela escolha de uma solução fácil (e rápida) em vez de uma abordagem melhor, mas que levaria mais tempo. É mensurável (ex: tempo estimado para refatoração). | Cap. 6, Cap. 9 |
| **Quality Gate** | Ponto de controle no pipeline de CI/CD onde um conjunto de critérios de qualidade (ex: cobertura de testes > 80%, zero vulnerabilidades críticas) deve ser atendido para que a entrega prossiga para o próximo estágio. | Cap. 10 |
| **Revisão de Código (Code Review)** | Processo sistemático de inspeção de código por um ou mais desenvolvedores (que não são os autores) para identificar defeitos, violações de estilo, problemas de segurança e oportunidades de melhoria. | Cap. 6.4, Cap. 10 |
| **Revisão de Arquitetura (Architecture Review)** | Processo formal de avaliação da arquitetura contra requisitos não-funcionais (RTs), padrões e princípios arquiteturais (ex: SOLID, Clean Architecture, DDD). Deve envolver arquitetos que não participaram do design original (validação independente). | Cap. 7.4.5, Cap. 8 |
| **Cobertura de Testes** | Métrica que indica a porcentagem de código (linhas, branches, condições) executada por testes automatizados. A meta mínima deve ser definida por projeto, mas, em geral, < 70% é considerado insuficiente. | Cap. 8.3.1 |
| **Teste Unitário** | Teste que verifica o comportamento de uma unidade isolada de código (ex: uma classe, um método). Deve ser rápido, determinístico e independente de infraestrutura (uso de mocks/stubs). | Cap. 8.3.2 |
| **Teste de Integração** | Teste que verifica a interação entre módulos, serviços ou componentes, incluindo bancos de dados, filas e APIs externas. | Cap. 8.3.2 |
| **Teste de Contrato** | Teste que valida se um serviço (provedor) atende ao contrato especificado (ex: OpenAPI) e se os consumidores (clientes) estão em conformidade com esse contrato. Essencial para microsserviços. | Cap. 10.4.5 |
| **Teste de Performance** | Teste que avalia a eficiência de desempenho do sistema, incluindo tempo de resposta, throughput, utilização de recursos e escalabilidade. | Cap. 8.2 |
| **Análise Estática** | Técnica de análise de código sem executá-lo, utilizada para detectar vulnerabilidades de segurança, violações de estilo, code smells e complexidade excessiva. | Cap. 8.3.1 |
| **Análise Dinâmica** | Técnica de análise de código durante sua execução, utilizada para detectar vazamentos de memória, condições de corrida e problemas de concorrência. | Cap. 8.3.2 |
| **Índice de Manutenibilidade (Maintainability Index)** | Métrica composta (varia de 0 a 100) que estima a facilidade de manutenção de um código. Valores > 80 são considerados "excelentes"; < 20 são "baixíssimos". | Cap. 6 |
| **Complexidade Ciclomática** | Métrica que mede o número de caminhos lineares independentes no código (ex: número de branches). Valores > 10 indicam complexidade excessiva e risco de defeitos. | Cap. 6 |
| **Métrica de Duplicação** | Percentual de código duplicado. Duplicação > 5% é considerada um indicador de baixa manutenibilidade. | Cap. 6.3.4 |
| **Defeito** | Qualquer desvio do comportamento esperado (requisito), que pode ser um bug, uma violação de segurança, uma degradação de performance ou uma não conformidade com padrões. | Cap. 8.3.1 |
