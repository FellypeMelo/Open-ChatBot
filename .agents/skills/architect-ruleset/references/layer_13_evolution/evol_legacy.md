# Seção 5 – Regras de Gestão de Sistemas Legados (Layer 13 - EVOL-LEGACY)

---

### REGEVOL-004 – Avaliação de Sistemas Legados com Base em Valor de Negócio e Qualidade Técnica

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-004 |
| **Nome** | Avaliação de Sistemas Legados com Base em Valor de Negócio e Qualidade Técnica |
| **Descrição** | Para cada sistema legado, o agente deve realizar uma avaliação baseada em duas dimensões: **(1)** Valor de Negócio: contribuição do sistema para os objetivos da organização, uso, dependência, criticidade; **(2)** Qualidade Técnica: manutenibilidade, documentação, performance, segurança, tecnologia utilizada. A avaliação deve resultar em uma classificação do sistema em uma matriz 2x2: **Alto Valor / Alta Qualidade** → manter; **Alto Valor / Baixa Qualidade** → reengenharia; **Baixo Valor / Alta Qualidade** → manter com monitoramento; **Baixo Valor / Baixa Qualidade** → substituir ou descontinuar. |
| **Objetivo** | Orientar decisões estratégicas sobre o futuro de sistemas legados, maximizando o retorno sobre o investimento. |
| **Motivação** | Cap. 9.4 – a avaliação de sistemas legados deve considerar tanto o valor de negócio quanto a qualidade técnica. |
| **Justificativa** | Decisões baseadas apenas em idade ou tecnologia são inadequadas; sistemas antigos podem ainda ter alto valor de negócio. |
| **Critérios de Aplicação** | Sistemas com mais de 5 anos de uso ou com tecnologia obsoleta. |
| **Critérios de Não Aplicação** | Sistemas novos ou com planos de substituição já definidos. |
| **Pré-condições** | Dados sobre uso, custos, defeitos e arquitetura disponíveis. |
| **Pós-condições** | Classificação documentada e plano de ação definido. |
| **Restrições** | A avaliação deve ser revisada anualmente ou quando houver mudanças significativas. |
| **Dependências** | REGRISK-001 (riscos), REGEVOL-003 (refatoração). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Sistema de folha de pagamento: alto valor de negócio, baixa qualidade técnica (código COBOL, documentação inexistente). Decisão: reengenharia para Java." |
| **Exemplo Negativo** | "Sistema antigo, vamos substituir sem avaliar seu valor de negócio." |
| **Anti-pattern** | Manter sistemas legados "para sempre" sem avaliar custo-benefício. |
| **Métrica** | Percentual de sistemas legados com avaliação documentada (meta: 100%). |
| **Critérios de Auditoria** | Revisar a matriz de avaliação e os planos de ação. |

---

### REGEVOL-005 – Estratégias de Evolução para Sistemas Legados (Manter, Reengenharia, Substituir)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGEVOL-005 |
| **Nome** | Estratégias de Evolução para Sistemas Legados (Manter, Reengenharia, Substituir) |
| **Descrição** | Com base na avaliação do sistema legado (REGEVOL-004), o agente deve recomendar uma das seguintes estratégias: **(1)** Manter: continuar com manutenção regular, sem grandes investimentos. Aplicável a sistemas com baixo valor de negócio ou alta qualidade; **(2)** Reengenharia: modernizar o sistema (ex: refatoração, migração de tecnologia, documentação). Aplicável a sistemas com alto valor de negócio e baixa qualidade; **(3)** Substituir: desenvolver um novo sistema ou adquirir um COTS. Aplicável a sistemas com baixo valor e baixa qualidade. O agente deve documentar a justificativa, os custos estimados e o cronograma para cada estratégia. |
| **Objetivo** | Garantir que os sistemas legados sejam gerenciados de forma proativa e alinhada com os objetivos de negócio. |
| **Motivação** | Cap. 9.4 – as estratégias para sistemas legados incluem manter, reengenharia e substituição. |
| **Justificativa** | A estratégia errada pode desperdiçar recursos (ex: reengenharia de um sistema que deveria ser substituído). |
| **Critérios de Aplicação** | Sistemas legados classificados. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Avaliação concluída (REGEVOL-004). |
| **Pós-condições** | Estratégia escolhida e plano de ação definido. |
| **Restrições** | Para sistemas com alto valor de negócio, a substituição deve ser planejada com cuidado para evitar interrupções. |
| **Dependências** | REGEVOL-004. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Sistema de RH: alto valor, baixa qualidade → reengenharia (migração para plataforma web, refatoração). Estimativa: 12 meses, R$ 1M." |
| **Exemplo Negativo** | "Vamos reengenheirar todos os sistemas legados, independentemente do valor de negócio." |
| **Anti-pattern** | Substituir um sistema legado sem considerar a migração de dados e processos. |
| **Métrica** | Percentual de sistemas legados com estratégia definida. |
| **Critérios de Auditoria** | Revisar se cada sistema legado tem um plano de ação documentado. |
