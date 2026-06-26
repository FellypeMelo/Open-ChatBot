# Seção 4 – Regras de Avaliação de Riscos (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-EVAL  
**Status:** Definitivo  
**Escopo:** Métodos qualitativos e quantitativos para a determinação de probabilidade, impacto e pontuação consolidada de risco (Risk Score).

---

### REGRISK-003 – Matriz de Risco Bidimensional (Probabilidade x Impacto)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-003 |
| **Nome** | Matriz de Risco Bidimensional (Probabilidade x Impacto) |
| **Descrição** | O agente deve avaliar cada risco com base em uma escala de 1 a 5 para probabilidade e 1 a 5 para impacto. A pontuação deve ser inserida em uma matriz de risco bidimensional para categorizar a severidade: **(1) Crítico** (pontuação 15-25): requer atenção imediata do Comitê de Arquitetura e mitigação obrigatória; **(2) Alto** (pontuação 10-14): requer plano de mitigação e monitoramento ativo; **(3) Médio** (pontuação 5-9): requer monitoramento periódico e planos simplificados; **(4) Baixo** (pontuação 1-4): pode ser aceito com justificativa. |
| **Objetivo** | Padronizar a severidade dos riscos para permitir a comparação e a priorização correta dos recursos. |
| **Motivação** | ISO 31000 / Cap. 9.4.2 (processos de governança baseados em risco). |
| **Justificativa** | Escalas arbitrárias ou ad-hoc impedem o ranking coeso de múltiplos riscos entre projetos distintos. |
| **Critérios de Aplicação** | Todo risco mapeado no Risk Register. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Identificação e descrição inicial do risco concluídas. |
| **Pós-condições** | O risco possui probabilidade, impacto e severidade final atribuídos. |
| **Restrições** | Se a probabilidade e o impacto mudarem significativamente na revisão periódica, a matriz correspondente deve ser recalculada. |
| **Dependências** | REGRISK-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-001: Probabilidade = 3, Impacto = 4. Risk Score = 12 (Alto)." |
| **Exemplo Negativo** | "R-001: probabilidade média, impacto severo." (sem escala numérica). |
| **Anti-pattern** | Atribuir valores de impacto baixos apenas para reduzir a severidade de um risco inconveniente no cronograma. |
| **Métrica** | Cobertura de avaliação numérica na planilha de riscos. |
| **Critérios de Auditoria** | Revisar o preenchimento de todas as pontuações do Risk Register. |

---

### REGRISK-004 – Análise Quantitativa para Riscos Críticos e de Alto Impacto

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-004 |
| **Nome** | Análise Quantitativa para Riscos Críticos e de Alto Impacto |
| **Descrição** | Para riscos categorizados como Crítico ou de Alto Impacto, o agente deve, quando aplicável, realizar ou requerer uma análise quantitativa utilizando métodos como FAIR (Factor Analysis of Information Risk) ou árvores de decisão baseadas em valor monetário esperado (EMV). A análise quantitativa deve estimar os intervalos monetários da perda potencial anual (Annualized Loss Expectancy - ALE) e da frequência de materialização, oferecendo dados para embasamento de trade-off de investimento em mitigação. |
| **Objetivo** | Mitigar a subjetividade de análises puramente qualitativas para decisões estratégicas que envolvam alto risco de capital ou conformidade. |
| **Motivação** | Cap. 8.2.4 (análise quantitativa de drivers) e padrões da indústria para riscos cibernéticos. |
| **Justificativa** | Análises qualitativas são úteis, mas insuficientes para riscos de alto impacto. A análise quantitativa permite decisões mais informadas. |
| **Critérios de Aplicação** | Riscos com impacto financeiro estimado > 5% do orçamento do projeto ou com potencial de multa regulatória > R$ 1M. |
| **Critérios de Não Aplicação** | Riscos com impacto puramente intangível (dificuldade extrema de coleta de métricas de perdas). |
| **Pré-condições** | Dados históricos ou estimativas parametrizadas de probabilidade e impacto. |
| **Pós-condições** | Relatório de análise quantitativa associado ao Risk Register. |
| **Restrições** | A modelagem deve ser validada por analista financeiro ou especialista de riscos designado. |
| **Dependências** | REGRISK-003. |
| **Prioridade** | **Média** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-001: Falha de compatibilidade com ORM. FAIR: Probabilidade = 25%, Impacto = R$ 500k. Expected Loss = R$ 125k. Intervalo de confiança (90%): R$ 50k – R$ 300k." |
| **Exemplo Negativo** | "R-001: Risco Alto (sem justificativa métrica para o trade-off de gastos com treinamento)." |
| **Anti-pattern** | Forçar estimativas numéricas de precisão arbitrária sobre premissas falsas ou sem base de amostragem mínima. |
| **Métrica** | Proporção de decisões críticas suportadas por análises EMV/FAIR. |
| **Critérios de Auditoria** | Revisar os anexos de modelagem quantitativa em ADRs de alto impacto. |

---

### REGRISK-005 – Priorização e Ranking de Riscos (Risk Score)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-005 |
| **Nome** | Priorização e Ranking de Riscos (Risk Score) |
| **Descrição** | O agente deve garantir que todos os riscos sejam ranqueados com base em seu Risk Score, calculado como: **Risk Score = Probabilidade × Impacto** (escala de 1 a 25). Riscos com maior Risk Score devem ser tratados com maior prioridade. O ranking deve ser revisado periodicamente (ex: trimestralmente) e atualizado conforme novos riscos surgem ou riscos existentes mudam. |
| **Objetivo** | Fornecer uma lista ordenada de riscos que orienta a alocação de recursos e a tomada de decisão. |
| **Motivação** | ISO 31000, Cap. 9.4.2. |
| **Justificativa** | Sem ranking, recursos são alocados de forma subjetiva, muitas vezes ignorando os riscos mais críticos. |
| **Critérios de Aplicação** | Todo risco identificado. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Probabilidade e impacto definidos (REGRISK-003). |
| **Pós-condições** | Riscos ordenados por Risk Score. |
| **Restrições** | O ranking deve ser visível e acessível a todos os stakeholders. |
| **Dependências** | REGRISK-003. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Ranking: R-001 (15 pontos), R-003 (12), R-002 (9), R-005 (6)." |
| **Exemplo Negativo** | "Lista de riscos em ordem aleatória." |
| **Anti-pattern** | Priorizar riscos com base na opinião de uma única pessoa. |
| **Métrica** | Número de riscos com ranking definido (meta: 100%). |
| **Critérios de Auditoria** | Revisar se todos os riscos têm Score. |
