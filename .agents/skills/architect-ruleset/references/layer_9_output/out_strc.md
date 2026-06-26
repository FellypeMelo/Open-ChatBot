# Seção 3 – Regras de Estrutura de Saída (Layer 9 - Output Rules e Formatação de Resultados)

**ID:** ARCH-RULESET-L9-OUT-STRC  
**Status:** Definitivo  
**Escopo:** Definição da hierarquia e estrutura padrão para relatórios e ajuste de complexidade conforme stakeholders.

---

### REGOUT-001 – Estrutura Padrão para Respostas e Recomendações

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-001 |
| **Nome** | Estrutura Padrão para Respostas e Recomendações |
| **Descrição** | Toda resposta do agente que contenha uma análise, recomendação ou decisão deve seguir a estrutura padrão: **(1) Sumário Executivo**: 2-3 frases sintetizando o essencial (para leitores apressados); **(2) Contexto**: descrição do problem ou situação; **(3) Análise**: desenvolvimento detalhado, com evidências, raciocínio e alternativas; **(4) Conclusão ou Recomendação**: ação sugerida, com justificativa; **(5) Próximos Passos**: ações concretas sugeridas (se aplicável); **(6) Referências**: requisitos, ADRs, normas citadas. A estrutura pode ser ajustada para respostas simples (ex: informações factuais), mas o Sumário Executivo deve ser obrigatório para respostas com mais de 3 parágrafos. |
| **Objetivo** | Garantir que o leitor possa rapidamente captar a essência e, se quiser, aprofundar-se. |
| **Motivação** | Cap. 7.4.6 (comunicação executiva), Cap. 4 (comunicação eficaz). |
| **Justificativa** | Leitores têm tempo limitado; respostas não estruturadas dificultam a rápida compreensão. |
| **Critérios de Aplicação** | Respostas com análise, recomendação ou decisão. |
| **Critérios de Não Aplicação** | Respostas simples e factuais (ex: "qual é a definição de X?"). |
| **Pré-condições** | Análise concluída. |
| **Pós-condições** | Saída estruturada. |
| **Restrições** | O Sumário Executivo não pode ser mais longo que 4 linhas. |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "**Sumário Executivo**: A migração para CockroachDB é recomendada, pois oferece escalabilidade +30% com riscos controlados (compatibilidade mitigada com camada de abstração). **Contexto**: ... **Análise**: ... **Recomendação**: ... **Próximos Passos**: ... **Referências**: RN-042, ADR-012." |
| **Exemplo Negativo** | "Acho que CockroachDB é bom." (sem estrutura). |
| **Anti-pattern** | Sumário Executivo com detalhes técnicos ou muito longo. |
| **Métrica** | Percentual de respostas com estrutura padrão (meta: 100%). |
| **Critérios de Auditoria** | Revisar amostra de respostas: se não tiver Sumário Executivo para análises, falha. |

---

### REGOUT-002 – Níveis de Detalhe Ajustáveis ao Público (Detalhado, Moderado, Alto Nível)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-002 |
| **Nome** | Níveis de Detalhe Ajustáveis ao Público (Detalhado, Moderado, Alto Nível) |
| **Descrição** | O agente deve ajustar o nível de detalhe da saída ao público-alvo, utilizando três níveis padrão: **(1) Detalhado**: para arquitetos, engenheiros e especialistas – inclui todos os detalhes técnicos, evidências, alternativas, métricas, diagramas, códigos; **(2) Moderado**: para gerentes, POs e líderes técnicos – inclui a essência da análise, principais evidências e recomendações, mas omite detalhes de implementação; **(3) Alto Nível**: para executivos, patrocinadores e stakeholders não técnicos – inclui apenas o sumário executivo, decisões, impactos financeiros, riscos e próximos passos. O agente deve detectar ou perguntar qual nível de detalhe é desejado. |
| **Objetivo** | Evitar sobrecarga de informação para públicos não técnicos e garantir que públicos técnicos tenham todos os detalhes necessários. |
| **Motivação** | Cap. 7.4.1 (propósito de viewpoints), Cap. 4 (comunicação). |
| **Justificativa** | O mesmo conteúdo pode ser apresentado de forma diferente para diferentes públicos, maximizando a eficácia. |
| **Critérios de Aplicação** | Respostas que envolvam análises ou recomendações complexas. |
| **Critérios de Não Aplicação** | Respostas factuais simples. |
| **Pré-condições** | Público identificado. |
| **Pós-condições** | Saída com nível de detalhe adequado. |
| **Restrições** | Se o público não for especificado, o agente deve assumir "Moderado" e oferecer a opção de aprofundamento. |
| **Dependências** | REGOUT-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Fornecendo análise em nível Detalhado (para arquitetos): inclui diagrama de componentes, especificação de API, e métricas de performance. Fornecendo resumo em nível Alto Nível (para executivos): migração recomendada, ROI estimado, riscos mitigados." |
| **Exemplo Negativo** | "Enviar a mesma análise detalhada para todos os stakeholders." |
| **Anti-pattern** | Fornecer apenas nível Alto Nível para arquitetos, que não terão detalhes suficientes. |
| **Métrica** | Percentual de respostas com nível de detalhe ajustado (meta: 100%). |
| **Critérios de Auditoria** | Revisar se o nível de detalhe é consistente com o público. |
