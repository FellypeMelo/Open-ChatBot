# Seção 5 – Regras de Padrões de Projeto e Reuso de Design (Layer 11 - Modelagem e Projeto OO)

**ID:** ARCH-RULESET-L11-MODEL-PATTERNS  
**Status:** Definitivo  
**Escopo:** Critérios para seleção, aplicação e documentação de padrões de projeto (GoF) em modelos de design.

---

### REGMODEL-007 – Reconhecimento e Aplicação de Padrões de Projeto

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-007 |
| **Nome** | Reconhecimento e Aplicação de Padrões de Projeto |
| **Descrição** | O agente deve reconhecer situações onde padrões de projeto podem ser aplicados e recomendar sua utilização, documentando no modelo. Exemplos de situações e padrões correspondentes: **(1)** Quando múltiplas visualizações de um mesmo estado são necessárias → **Observer**; **(2)** Quando é necessário simplificar uma interface complexa → **Façade**; **(3)** Quando é necessário acessar elementos de uma coleção sem expor sua estrutura → **Iterator**; **(4)** Quando é necessário adicionar comportamento a objetos dinamicamente → **Decorator**. O agente deve justificar a escolha do padrão com base no problema e nas alternativas rejeitadas. |
| **Objetivo** | Promover soluções de design comprovadas e reduzir a complexidade. |
| **Motivação** | Cap. 7.2 – padrões de projeto são soluções reutilizáveis para problemas recorrentes. |
| **Justificativa** | O uso de padrões acelera o design, melhora a comunicação e reduz riscos. |
| **Critérios de Aplicação** | Projetos orientados a objetos com complexidade moderada a alta. |
| **Critérios de Não Aplicação** | Projetos muito simples onde padrões adicionariam complexidade desnecessária. |
| **Pré-condições** | Problema de design identificado. |
| **Pós-condições** | Padrão documentado no modelo de design. |
| **Restrições** | O agente não deve forçar um padrão onde ele não se encaixa naturalmente. |
| **Dependências** | REGMODEL-003. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Utilizando padrão Observer para notificar a interface de usuário sobre mudanças no estado do pedido, garantindo que múltiplas telas sejam atualizadas automaticamente." |
| **Exemplo Negativo** | "Não usamos padrões; cada dev resolve do seu jeito." |
| **Anti-pattern** | Usar padrões de forma excessiva (over-engineering) ou sem necessidade. |
| **Métrica** | Número de padrões documentados / total de padrões aplicáveis identificados. |
| **Critérios de Auditoria** | Revisar se os padrões foram aplicados adequadamente e documentados. |

---

### REGMODEL-008 – Documentação de Padrões de Projeto nos Modelos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGMODEL-008 |
| **Nome** | Documentação de Padrões de Projeto nos Modelos |
| **Descrição** | Quando um padrão de projeto é aplicado, o agente deve documentá-lo no modelo de design, incluindo: **(1)** nome do padrão; **(2)** problema que resolve; **(3)** justificativa da escolha; **(4)** diagrama de classes específico mostrando participantes (ex: Subject, Observer no padrão Observer); **(5)** referência à literatura (ex: "Gamma et al., 1995"). A documentação do padrão deve ser integrada ao artefato de design (ex: seção separada no documento ARC42 ou ADR específico). |
| **Objetivo** | Garantir que o uso de padrões seja compreendido e mantido ao longo do tempo. |
| **Motivação** | Cap. 7.2 – padrões são melhor comunicados quando documentados. |
| **Justificativa** | Padrões não documentados podem ser mal compreendidos ou removidos em refatorações futuras. |
| **Critérios de Aplicação** | Todo padrão aplicado. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Padrão identificado e aplicado. |
| **Pós-condições** | Documentação do padrão incluída no artefato de design. |
| **Restrições** | A documentação deve ser concisa (ex: 1-2 páginas por padrão). |
| **Dependências** | REGMODEL-007. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "ADR-023: Uso do padrão Observer para notificação de eventos. Diagrama mostrando Pedido (Subject) e NotificacaoListener (Observer)." |
| **Exemplo Negativo** | "Usamos Observer aqui, mas não documentamos." |
| **Anti-pattern** | Documentar padrões de forma genérica, sem adaptar ao contexto do projeto. |
| **Métrica** | Percentual de padrões documentados. |
| **Critérios de Auditoria** | Verificar se cada padrão aplicado tem documentação associada. |
