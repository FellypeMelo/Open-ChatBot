# Seção 4 – Sistema de Prioridades e Pesos (Layer 0)

**ID:** ARCH-RULESET-L0-PRIORITIES  
**Status:** Imutável  
**Escopo:** Tabela de criticidades e resolução de trade-offs.

Para garantir a consistência na tomada de decisão, o agente deve aplicar o seguinte sistema de prioridades a todas as regras e requisitos.

| Nível de Prioridade | Código | Descrição | Ação ao conflito |
| :--- | :--- | :--- | :--- |
| **Crítica** | P1 | Regras que afetam a segurança, conformidade legal (LGPD), integridade dos dados ou viabilidade do sistema. | Prevalece sobre qualquer outra. Não pode ser negociada. |
| **Alta** | P2 | Regras que afetam a arquitetura fundamental, padrões de integração, rastreabilidade ou manutenibilidade. | Prevalece sobre Média e Baixa; pode ser revista apenas por comitê. |
| **Média** | P3 | Regras que afetam a legibilidade, padronização de código, eficiência operacional ou usabilidade. | Prevalece sobre Baixa; pode ser ajustada por arquiteto sênior. |
| **Baixa** | P4 | Regras que afetam preferências estilísticas, convenções de nomenclatura secundárias ou otimizações marginais. | Pode ser quebrada se houver justificativa documentada. |
