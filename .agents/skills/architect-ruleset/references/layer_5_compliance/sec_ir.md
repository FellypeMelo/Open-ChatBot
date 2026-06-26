# Seção 9 – Regras de Gestão de Incidentes (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-IR  
**Status:** Definitivo  
**Escopo:** Gestão de incidentes de segurança e prazos legais de notificação segundo a LGPD (ANPD).

---

### REGSEC-010 – Plano de Resposta a Incidentes e Notificação à ANPD (prazo legal)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-010 |
| **Nome** | Plano de Resposta a Incidentes e Notificação à ANPD (prazo legal) |
| **Descrição** | O agente deve garantir que a organização possua um Plano de Resposta a Incidentes de Segurança documentado e testado (ex: simulações anuais). O plano deve incluir: **(1)** procedimentos de contenção, erradicação e recuperação; **(2)** comunicação interna (CISO, DPO, jurídico); **(3)** notificação à ANPD e aos titulares, conforme LGPD Art. 48 (comunicação em prazo razoável, definido como até 48 horas para incidentes críticos). O agente deve também garantir que os logs de auditoria (REGSEC-008) sejam preservados integralmente para investigação forense. |
| **Objetivo** | Garantir resposta rápida e organizada a incidentes, minimizando danos e cumprindo obrigações legais de notificação. |
| **Motivação** | LGPD Art. 48, NIST SP 800-61 (Incident Response). |
| **Justificativa** | A falta de plano de resposta agrava incidentes. A não notificação à ANPD dentro do prazo legal gera multas severas. |
| **Critérios de Aplicação** | Toda a organização, especialmente sistemas com dados RESTRITO. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Plano documentado e time de resposta treinado. |
| **Pós-condições** | Incidente contido, erradicado, e notificações enviadas. |
| **Restrições** | O agente deve garantir que o processo de notificação inclua a avaliação de danos aos titulares. |
| **Dependências** | REGSEC-008, REGSEC-009. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Incidente de vazamento de dados: detectado em 10min, contido em 1h, ANPD notificada em 24h, titulares notificados em 48h." |
| **Exemplo Negativo** | "Vazamento de dados descoberto 6 meses depois por um jornalista." |
| **Anti-pattern** | Ter um plano, mas nunca testá-lo (simulações). |
| **Métrica** | Tempo médio de contenção e notificação. |
| **Critérios de Auditoria** | Revisar se os tempos de resposta estão dentro dos SLAs definidos (ex: < 2h para contenção). |
