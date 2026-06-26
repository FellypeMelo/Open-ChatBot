# Seção 3 – Regras de Identificação e Classificação de Riscos (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-ID  
**Status:** Definitivo  
**Escopo:** Mapeamento proativo de ameaças e vulnerabilidades categorizadas por natureza do risco.

---

### REGRISK-001 – Identificação Obrigatória de Riscos para Toda Decisão Arquitetural

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-001 |
| **Nome** | Identificação Obrigatória de Riscos para Toda Decisão Arquitetural |
| **Descrição** | O agente deve garantir que para toda decisão arquitetural significativa (ex: escolha de tecnologia, mudança de padrão, nova integração), seja realizada uma identificação formal de riscos. A identificação deve cobrir pelo menos as seguintes categorias: **(1) Riscos Técnicos**: falhas de performance, compatibilidade, obsolescência, complexidade; **(2) Riscos Operacionais**: falhas de deploy, indisponibilidade, perda de dados, capacidade; **(3) Riscos de Negócio**: impacto no valor entregue, desalinhamento estratégico, custos inesperados; **(4) Riscos de Compliance**: violações de LGPD, segurança, regulamentações; **(5) Riscos Financeiros**: custos de implementação, manutenção, multas. Cada risco deve ser registrado em um registro de riscos (Risk Register) com um identificador único. |
| **Objetivo** | Garantir que nenhum risco relevante seja esquecido ou ignorado durante o processo de decisão. |
| **Motivação** | Cap. 1.4 (drivers externos, riscos regulatórios), Cap. 8.3.1 (análise de impacto). |
| **Justificativa** | Riscos não identificados são os mais perigosos. Eles podem se materializar sem aviso, causando danos significativos. |
| **Critérios de Aplicação** | Toda decisão arquitetural de alto impacto (conforme REGGOV-002). |
| **Critérios de Não Aplicação** | Decisões rotineiras e de baixo impacto (ex: escolha de biblioteca de logging). |
| **Pré-condições** | Template de Risk Register disponível. |
| **Pós-condições** | Cada risco identificado registrado no Risk Register. |
| **Restrições** | Risco não identificado não pode ser posteriormente usado como "surpresa". |
| **Dependências** | REGGOV-002 (Comitê de Arquitetura), REGDOC-002 (ADRs). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Decisão: migrar para CockroachDB. Riscos identificados: (R-001) Falha de compatibilidade com ORM; (R-002) Curva de aprendizado da equipe; (R-003) Impacto em performance; (R-004) Custos adicionais de licenciamento." |
| **Exemplo Negativo** | "Migrar para CockroachDB (sem análise de riscos)." |
| **Anti-pattern** | Identificar apenas riscos óbvios (ex: performance) e ignorar riscos menos óbvios (ex: compliance). |
| **Métrica** | Número de riscos identificados por decisão (meta: mínimo 3). |
| **Critérios de Auditoria** | Revisar ADRs: se não houver identificação de riscos, falha. |

---

### REGRISK-002 – Classificação de Riscos por Categoria (Técnico, Operacional, Negócio, Compliance, Financeiro)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGRISK-002 |
| **Nome** | Classificação de Riscos por Categoria (Técnico, Operacional, Negócio, Compliance, Financeiro) |
| **Descrição** | O agente deve garantir que cada risco identificado seja classificado em uma ou mais categorias: **(1) Técnico**: falhas de sistema, tecnologia, arquitetura; **(2) Operacional**: falhas de processo, pessoas, infraestrutura, dependências; **(3) Negócio**: impacto em valor, receita, reputação, satisfação do cliente; **(4) Compliance**: violações legais, regulatórias, LGPD; **(5) Financeiro**: custos inesperados, multas, perda de investimento. A classificação ajuda a direcionar a responsabilidade (ex: Compliance para riscos LGPD) e a comunicação. |
| **Objetivo** | Direcionar a avaliação e a mitigação para os especialistas corretos, e facilitar a comunicação com stakeholders. |
| **Motivação** | Cap. 1.4 (drivers externos e compliance), Cap. 9.2.2 (diferentes mundos). |
| **Justificativa** | Riscos de diferentes categorias requerem diferentes abordagens e diferentes stakeholders. |
| **Critérios de Aplicação** | Todo risco identificado (REGRISK-001). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Risco identificado. |
| **Pós-condições** | Categoria registrada no Risk Register. |
| **Restrições** | Um risco pode ter mais de uma categoria, mas deve ter uma primária. |
| **Dependências** | REGRISK-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "R-001: categoria primária = Técnico, secundária = Operacional." |
| **Exemplo Negativo** | "R-001 sem categoria definida." |
| **Anti-pattern** | Classificar todos os riscos como "Técnico" por preguiça de avaliar outras dimensões. |
| **Métrica** | Percentual de riscos com classificação de categoria (meta: 100%). |
| **Critérios de Auditoria** | Revisar classificação no Risk Register. |
