# Seção 6 – Regras de Monitoramento e Revisão (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-MONITOR  
**Status:** Definitivo  
**Escopo:** Ciclos de revisões recorrentes de risco e definição de limites de KRIs (Key Risk Indicators) vinculados à infraestrutura de monitoramento.

---

### REGRISK-009 – Revisão Periódica de Riscos (Trimestral ou a cada Marco)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-009 |
| **Nome** | Revisão Periódica de Riscos (Trimestral ou a cada Marco) |
| **Descrição** | O agente deve garantir que os riscos sejam revisados periodicamente (pelo menos trimestralmente ou a cada marco de projeto) para avaliar mudanças em probabilidade, impacto ou contexto. A revisão deve incluir: **(1)** Verificação se riscos antigos foram mitigados; **(2)** Identificação de novos riscos; **(3)** Reavaliação de probabilidade e impacto (REGRISK-003); **(4)** Atualização do ranking (REGRISK-005); **(5)** Status dos planos de mitigação (REGRISK-006). A revisão deve ser documentada e comunicada ao Comitê de Arquitetura. |
| **Objetivo** | Garantir que o registro de riscos reflita a realidade atual e que as ações de mitigação estejam progredindo. |
| **Motivação** | ISO 31000, Cap. 9.2.3 (ciclo de vida de sistemas). |
| **Justificativa** | Riscos dinâmicos requerem monitoramento contínuo. Um risco que era baixo pode se tornar crítico com o tempo. |
| **Critérios de Aplicação** | Todo o Risk Register. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Risk Register existente. |
| **Pós-condições** | Risk Register atualizado. |
| **Restrições** | A revisão deve ser conduzida por um facilitador independente (não o Risk Owner). |
| **Dependências** | REGRISK-001 a REGRISK-008. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Revisão trimestral: R-001 mitigado (80% concluído). R-002 probabilidade aumentou de 3 para 4. Novo risco identificado: R-010 (dependência de fornecedor)." |
| **Exemplo Negativo** | "Nunca revisamos os riscos." |
| **Anti-pattern** | Revisão superficial, apenas "carimbando" os mesmos riscos. |
| **Métrica** | Percentual de revisões realizadas vs. agendadas (meta: 100%). |
| **Critérios de Auditoria** | Verificar se há atas de revisão trimestral. |

---

### REGRISK-010 – Monitoramento Contínuo de Riscos com Indicadores (KRI – Key Risk Indicators)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-010 |
| **Nome** | Monitoramento Contínuo de Riscos com Indicadores (KRI – Key Risk Indicators) |
| **Descrição** | O agente deve garantir que para riscos **Críticos** e **Altos**, sejam definidos indicadores-chave de risco (KRIs) que possam ser monitorados continuamente (ex: tempo de resposta, taxa de erro, número de vulnerabilidades, disponibilidade, desvio de orçamento). Os KRIs devem ter limites (thresholds) que, quando ultrapassados, disparam alertas para o Risk Owner e para o Comitê de Arquitetura. Os KRIs devem ser revisados e ajustados periodicamente. |
| **Objetivo** | Permitir a detecção precoce de riscos se materializando, possibilitando ações corretivas antes do dano completo. |
| **Motivação** | Cap. 8.2.1 (monitoramento de recursos), Cap. 10 (ferramentas). |
| **Justificativa** | Risco não monitorado é risco não gerenciado. Indicadores objetivos permitem resposta rápida. |
| **Critérios de Aplicação** | Riscos Críticos e Altos. |
| **Critérios de Não Aplicação** | Riscos Baixos (monitoramento simplificado). |
| **Pré-condições** | Sistema de monitoramento (ex: Prometheus, CloudWatch, logs). |
| **Pós-condições** | KRIs definidos e sendo monitorados. |
| **Restrições** | Os KRIs devem ser acionáveis (ex: "aumentar capacidade" em vez de "observar"). |
| **Dependências** | REGRISK-006, REGSEC-009. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-003: Falha de performance. KRI: tempo de resposta > 500ms por 5 minutos consecutivos. Threshold: alerta para Risk Owner. Ação: escalar horizontalmente." |
| **Exemplo Negativo** | "R-003: monitoramento manual (ex: alguém pergunta de vez em quando)." |
| **Anti-pattern** | Definir KRIs que não podem ser medidos (ex: "qualidade do código"). |
| **Métrica** | Percentual de riscos críticos com KRIs definidos (meta: 100%). |
| **Critérios de Auditoria** | Verificar se há dashboards ou alertas configurados para riscos críticos. |
