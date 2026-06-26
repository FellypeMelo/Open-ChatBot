# Seção 4 – Regras de Tipos de Manutenção e Priorização (Layer 13 - EVOL-MAINT)

---

### REGEVOL-002 – Classificação e Priorização de Atividades de Manutenção

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-002 |
| **Nome** | Classificação e Priorização de Atividades de Manutenção |
| **Descrição** | O agente deve classificar cada atividade de manutenção em um dos três tipos e priorizá-los adequadamente: **(1)** Manutenção Corretiva: correção de defeitos. Prioridade baseada na gravidade (crítico: imediato, alto: próxima release, médio/baixo: backlog); **(2)** Manutenção Adaptativa: adaptação a mudanças no ambiente (ex: nova versão de SO, hardware). Prioridade baseada no impacto operacional; **(3)** Manutenção Perfectiva: adição de funcionalidades ou melhorias. Prioridade baseada no valor de negócio. O agente deve documentar a classificação e a justificativa da prioridade para cada mudança. |
| **Objetivo** | Garantir que os recursos de manutenção sejam alocados de forma eficiente e alinhada com as necessidades do negócio. |
| **Motivação** | Cap. 9.3 – a maior parte do esforço de manutenção é gasta em atividades perfectivas e adaptativas, não em correções. |
| **Justificativa** | A priorização correta evita que atividades de baixo valor consumam recursos que deveriam ser alocados a mudanças críticas. |
| **Critérios de Aplicação** | Toda solicitação de mudança em sistemas em produção. |
| **Critérios de Não Aplicação** | Mudanças em sistemas em desenvolvimento (pré-produção). |
| **Pré-condições** | Change Request (CR) submetido e analisado. |
| **Pós-condições** | CR classificado e priorizado. |
| **Restrições** | Mudanças corretivas críticas (ex: falha de segurança) têm prioridade máxima. |
| **Dependências** | REGEVOL-001 (Leis de Lehman), REGEVOL-006 (Change Management). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "CR-023: correção de vazamento de memória (corretiva, prioridade alta). CR-045: adaptação para nova versão do Java (adaptativa, prioridade média). CR-067: nova funcionalidade de relatórios (perfectiva, prioridade baixa)." |
| **Exemplo Negativo** | "Todas as mudanças têm a mesma prioridade." |
| **Anti-pattern** | Priorizar funcionalidades novas (perfectiva) em detrimento de correções críticas. |
| **Métrica** | Percentual de tempo gasto em cada tipo de manutenção (meta: 20% corretiva, 30% adaptativa, 50% perfectiva, conforme distribuição típica). |
| **Critérios de Auditoria** | Revisar o backlog de mudanças e verificar se a priorização está alinhada com a classificação. |

---

### REGEVOL-003 – Refatoração Contínua para Preservar Manutenibilidade

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-003 |
| **Nome** | Refatoração Contínua para Preservar Manutenibilidade |
| **Descrição** | O agente deve garantir que a refatoração seja uma prática contínua no ciclo de desenvolvimento, especialmente em sistemas de longa duração. A refatoração deve ser realizada sempre que: **(1)** código duplicado é identificado; **(2)** métodos ou classes estão muito longos; **(3)** há complexidade desnecessária; **(4)** há "bad smells" (ex: switch statements excessivos, data clumps). O agente deve alocar uma porcentagem mínima do tempo de cada sprint/iteração (ex: 10-20%) para refatoração, e deve documentar as refatorações realizadas. |
| **Objetivo** | Reduzir a dívida técnica e preservar a manutenibilidade do sistema ao longo do tempo. |
| **Motivação** | Cap. 9.3.3 – refatoração é uma forma de manutenção preventiva. |
| **Justificativa** | Refatoração contínua evita a degradação estrutural prevista pelas Leis de Lehman e reduz custos de manutenção futuros. |
| **Critérios de Aplicação** | Projetos com expectativa de vida > 1 ano ou com mais de 3 desenvolvedores. |
| **Critérios de Não Aplicação** | Projetos de curta duração ou protótipos descartáveis. |
| **Pré-condições** | Ferramentas de análise estática configuradas (ex: SonarQube) para identificar "bad smells". |
| **Pós-condições** | Refatorações realizadas e documentadas. |
| **Restrições** | Refatoração não deve alterar o comportamento externo do sistema; testes automatizados devem garantir isso. |
| **Dependências** | REGTEST-001 (cobertura de testes), REGEVOL-001 (Leis de Lehman). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "No sprint 12, dedicamos 15% do tempo para refatorar a classe `Pedido`, reduzindo sua complexidade ciclomática de 18 para 7." |
| **Exemplo Negativo** | "Nunca temos tempo para refatorar; sempre há novas funcionalidades." |
| **Anti-pattern** | Refatorar apenas quando o código está "quebrado", em vez de continuamente. |
| **Métrica** | Percentual de tempo de desenvolvimento dedicado à refatoração (meta: ≥ 10%). |
| **Critérios de Auditoria** | Revisar histórico de commits para verificar refatorações realizadas. |
