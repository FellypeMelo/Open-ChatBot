# Seção 8 – Regras de Escalabilidade e Adaptação de Métodos Ágeis (Layer 10 - Processos e Ciclo de Vida)

**ID:** ARCH-RULESET-L10-PROC-SCALING  
**Status:** Definitivo  
**Escopo:** Adaptação e escalonamento de práticas ágeis para grandes equipes e sistemas distribuídos ou críticos.

---

### REGPROC-011 – Adaptação de Métodos Ágeis para Grandes Equipes e Sistemas Críticos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGPROC-011 |
| **Nome** | Adaptação de Métodos Ágeis para Grandes Equipes e Sistemas Críticos |
| **Descrição** | Quando métodos ágeis são aplicados a grandes equipes (> 10 pessoas), sistemas distribuídos ou críticos, o agente deve recomendar adaptações, como: **(1)** divisão em squads com coordenação central; **(2)** uso de frameworks de escalonamento ágil (ex: SAFe, LeSS); **(3)** manutenção de documentação arquitetural mínima, mesmo em projetos ágeis; **(4)** integração contínua em múltiplos níveis; **(5)** governança reforçada com revisões de arquitetura e segurança. O agente deve alertar sobre os riscos de aplicar métodos ágeis "puros" em contextos que exigem mais estrutura. |
| **Objetivo** | Permitir que os benefícios dos métodos ágeis sejam colhidos em contextos complexos, sem comprometer a qualidade ou o controle. |
| **Motivação** | Cap. 3.5 – escalar métodos ágeis requer adaptações. |
| **Justificativa** | Métodos ágeis foram projetados para equipes pequenas; escalá-los exige cuidados. |
| **Critérios de Aplicação** | Projetos com > 10 pessoas, ou com requisitos críticos de segurança/compliance. |
| **Critérios de Não Aplicação** | Projetos com equipes pequenas e baixa criticidade. |
| **Pré-condições** | Avaliação do tamanho da equipe e criticidade. |
| **Pós-condições** | Plano de adaptação ágil documentado. |
| **Restrições** | Adaptações não podem violar os princípios ágeis fundamentais (ex: feedback contínuo, colaboração). |
| **Dependências** | REGPROC-001, REGGOV-003 (Conway). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Equipe de 40 pessoas dividida em 4 squads com um arquiteto coordenador; usamos SAFe com sprints de 3 semanas." |
| **Exemplo Negativo** | "Aplicar XP puro em um projeto de aviônicos com 50 engenheiros." |
| **Anti-pattern** | Ignorar a necessidade de coordenação e documentação em projetos grandes. |
| **Métrica** | Número de projetos ágeis escalados com sucesso. |
| **Critérios de Auditoria** | Verificar se adaptações foram documentadas e implementadas. |
