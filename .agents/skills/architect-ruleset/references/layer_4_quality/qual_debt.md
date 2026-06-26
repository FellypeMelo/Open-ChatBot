# Seção 7 – Regras de Gestão de Dívida Técnica / Layer 4 (Layer 4 - Qualidade)

**ID:** ARCH-RULESET-L4-QUAL-DEBT  
**Status:** Definitivo  
**Escopo:** Mapeamento, orçamentação e mitigação contínua de juros de dívida técnica.

---

### REGQUAL-012 – Rastreamento e Priorização de Dívida Técnica

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGQUAL-012 |
| **Nome** | Rastreamento e Priorização de Dívida Técnica |
| **Descrição** | O agente deve manter um registro formal de dívida técnica, contendo: **(1)** descrição do problema (ex: "módulo X precisa de refatoração"), **(2)** impacto estimado (ex: custo de manutenção adicional), **(3)** esforço estimado para resolver (em pontos/horas), **(4)** prioridade (com base no impacto), **(5)** data de entrada, **(6)** plano de resolução. A dívida técnica deve ser priorizada juntamente com novas funcionalidades (ex: 20% do tempo do sprint dedicado à redução de dívida). |
| **Objetivo** | Gerenciar a dívida técnica de forma explícita, evitando que ela se acumule exponencialmente. |
| **Motivação** | Cap. 6.1 (conceptual integrity) e Cap. 9.4.2 (otimização global vs. local). |
| **Justificativa** | Dívida técnica não gerenciada leva a código frágil, difícil de modificar e alto custo de manutenção. |
| **Critérios de Aplicação** | Projetos com mais de 6 meses de desenvolvimento ou com mais de 3 desenvolvedores. |
| **Critérios de Não Aplicação** | Projetos de curta duração (ex: < 3 meses). |
| **Pré-condições** | Ferramenta de rastreamento (ex: Jira com tag "dívida técnica"). |
| **Pós-condições** | Itens de dívida técnica são revisados e priorizados a cada sprint. |
| **Restrições** | Nenhuma funcionalidade nova pode ser adicionada se a dívida técnica for classificada como "crítica" e não estiver em redução. |
| **Dependências** | REGQUAL-011. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Sprint atual: 80% novas funcionalidades, 20% redução de dívida técnica (refatoração do módulo de integração)." |
| **Exemplo Negativo** | "Nunca temos tempo para refatorar; sempre há novas funcionalidades." |
| **Anti-pattern** | Acumular dívida técnica por meses e depois tentar resolvê-la em uma "sprint de qualidade" única. |
| **Métrica** | Razão entre dívida técnica paga vs. acumulada. |
| **Critérios de Auditoria** | Revisar o backlog de dívida técnica e o tempo alocado a ela. |
