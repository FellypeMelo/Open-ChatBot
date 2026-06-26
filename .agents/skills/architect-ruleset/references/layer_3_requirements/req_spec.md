# Seção 4 – Regras de Especificação e Estruturação / Layer 3 (Layer 3 - Requisitos)

**ID:** ARCH-RULESET-L3-REQ-SPEC  
**Status:** Definitivo  
**Escopo:** Formatos estruturais, critérios de aceitação SMART e rationales obrigatórios.

---

### REGREQ-004 – Estrutura Obrigatória do Requisito (RN/PS/LGPD/RT)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-004 |
| **Nome** | Estrutura Obrigatória do Requisito (RN/PS/LGPD/RT) |
| **Descrição** | Todo requisito deve ser escrito em uma estrutura padronizada contendo, no mínimo, os seguintes campos: **ID** (prefixo RN/PS/LGPD/RT), **Nome**, **Descrição** (texto claro e objetivo), **Categoria** (RN, PS, LGPD, RT), **Stakeholder Originário**, **Prioridade** (Crítica, Alta, Média, Baixa), **Critérios de Aceitação** (condições mensuráveis para considerar o requisito atendido), **Premissas** (se houver), **Dependências** (IDs de outros requisitos), **Rationale** (justificativa), **Status** (Rascunho, Em Revisão, Aprovado, Arquivado), **Data de Criação**, **Data de Última Alteração**, **Versão**. |
| **Objetivo** | Padronizar a especificação para eliminar ambiguidades e garantir que todos os requisitos sejam completos e auditáveis. |
| **Motivação** | Cap. 6.3.2 (o que capturar em um modelo), Cap. 5 (estrutura de conceitos). |
| **Justificativa** | Requisitos sem estrutura padronizada são interpretados de forma diferente por diferentes stakeholders, gerando conflitos de implementação. |
| **Critérios de Aplicação** | Toda criação ou atualização de requisito. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | O agente deve ter o template disponível. |
| **Pós-condições** | O requisito está em conformidade com o template. |
| **Restrições** | Os campos `Critérios de Aceitação` e `Dependências` não podem estar vazios (mínimo: "A definir" com justificativa). |
| **Dependências** | REGREQ-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "ID: RN-042. Nome: Classificação de Variantes Classe 5. Descrição: Variantes genômicas classificadas como Classe 5 (patogênicas) pela ACMG devem ser automaticamente associadas ao laudo como 'Patogênica'. Categoria: RN. Stakeholder: Dr. Carlos. Prioridade: Crítica. Critérios de Aceitação: (1) Ao processar VCF, toda variante com tag 'pathogenic' é rotulada como 'Patogênica'; (2) O campo de classificação no laudo é preenchido com 'Patogênica'. Dependências: RT-010 (processamento de VCF), PS-005 (controle de acesso ao laudo)." |
| **Exemplo Negativo** | "O sistema deve classificar variantes como patogênicas." (sem estrutura). |
| **Anti-pattern** | Usar campos opcionais apenas quando forçado, deixando-os vazios sem justificativa. |
| **Métrica** | Percentual de requisitos em conformidade com o template (meta: 100%). |
| **Critérios de Auditoria** | Auditoria de todos os requisitos: qualquer campo obrigatório vazio é uma falha. |

---

### REGREQ-005 – Critérios SMART para Requisitos Não-Funcionais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-005 |
| **Nome** | Critérios SMART para Requisitos Não-Funcionais (RT, PS, LGPD) |
| **Descrição** | Todo requisito não-funcional (RT, PS, LGPD) deve ter seus critérios de aceitação definidos no formato SMART: **Specific** (específico), **Measurable** (mensurável), **Achievable** (atingível), **Relevant** (relevante), **Time-bound** (temporal). Se um critério não puder ser SMART, o agente deve sinalizar o risco de não verificabilidade. |
| **Objetivo** | Eliminar requisitos vagos ("rápido", "seguro") e garantir que possam ser objetivamente testados e auditados. |
| **Motivação** | Cap. 7.4.6 – "faça custos e benefícios tão SMART quanto possível". |
| **Justificativa** | Requisitos não mensuráveis geram disputas intermináveis sobre se foram atendidos ou não. |
| **Critérios de Aplicação** | RTs, PSs e LGPDs. |
| **Critérios de Não Aplicação** | RNs podem ser qualitativos, desde que tenham critérios de aceitação objetivos (ex: "deve calcular" → critério: "o cálculo está correto para 10 casos de teste"). |
| **Pré-condições** | Requisito não-funcional em especificação. |
| **Pós-condições** | Critérios de aceitação estão no formato SMART. |
| **Restrições** | Se o stakeholder não souber definir a métrica, o agente deve sugerir métricas comuns (ex: tempo de resposta em ms, throughput em req/s). |
| **Dependências** | REGREQ-004. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RT-023: O sistema deve suportar o processamento de arquivos FASTQ de até 10 GB. Critério: 95% dos arquivos de 10 GB são processados em menos de 5 minutos em ambiente de produção com 4 workers." |
| **Exemplo Negativo** | "RT-023: O sistema deve processar arquivos grandes rapidamente." |
| **Anti-pattern** | Definir métricas que não podem ser medidas em produção (ex: "deve ser rápido" sem definir o que é rápido). |
| **Métrica** | Percentual de RTs com critérios SMART (meta: 100%). |
| **Critérios de Auditoria** | Revisar RTs: se algum não tiver métrica objetiva, falha. |

---

### REGREQ-006 – Separação Obrigatória por Categoria (Proibição de Requisitos Mistos)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-006 |
| **Nome** | Separação Obrigatória por Categoria (Proibição de Requisitos Mistos) |
| **Descrição** | Um requisito não pode conter declarações que pertençam a mais de uma categoria (RN, PS, LGPD, RT). Se um requisito misturar categorias, o agente deve imediatamente dividi-lo em múltiplos requisitos, cada um com sua categoria adequada. |
| **Objetivo** | Garantir que cada categoria de requisito seja gerenciada, priorizada e auditada por seu próprio processo (ex: PS tem revisão de segurança, RT tem revisão de arquitetura). |
| **Motivação** | Cap. 5 (separação de camadas) e Cap. 9 (alinhamento). |
| **Justificativa** | Requisitos mistos geram confusão de responsabilidades e dificultam a governança (ex: quem revisa um requisito que é 50% segurança e 50% negócio?). |
| **Critérios de Aplicação** | Na criação ou revisão de qualquer requisito. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisito em especificação. |
| **Pós-condições** | O requisito é dividido em sub-requisitos, cada um com uma única categoria. |
| **Restrições** | O agente deve manter a rastreabilidade entre o requisito original e os sub-requisitos. |
| **Dependências** | REGREQ-004. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Requisito original: 'O sistema deve ser seguro e processar FASTQ.' → Dividir em: PS-001 (segurança: autenticação e criptografia) e RN-010 (processar FASTQ)." |
| **Exemplo Negativo** | Manter o requisito misto. |
| **Anti-pattern** | Criar uma categoria "híbrida" (ex: RNT - Regra de Negócio Técnica) em vez de dividir. |
| **Métrica** | Número de requisitos com categoria única vs. total. |
| **Critérios de Auditoria** | Revisar todos os requisitos: se algum tiver conteúdo de mais de uma categoria, falha. |

---

### REGREQ-007 – Obrigação de Especificar o "Porquê" (Rationale)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-007 |
| **Nome** | Obrigação de Especificar o "Porquê" (Rationale) |
| **Descrição** | Todo requisito deve ser apresentado com o campo `Rationale` que explique a justificativa para sua existência. O rationale deve responder: (1) Por que este requisito é necessário? (2) Qual problema ele resolve? (3) Qual é a consequência de não o implementar? (4) Quais alternativas foram consideradas e rejeitadas (REGCON-009)? |
| **Objetivo** | Preservar o conhecimento do processo decisório e permitir que futuros arquitetos entendam o contexto da decisão. |
| **Motivação** | Cap. 6.2.3 (documentação de ações) e Cap. 7.4.6 (rationale para comprometimento). |
| **Justificativa** | Requisitos sem rationale são frágeis; quando o contexto muda, não há base para decidir se o requisito ainda é válido. |
| **Critérios de Aplicação** | Todo requisito. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisito definido. |
| **Pós-condições** | Campo `Rationale` preenchido. |
| **Restrições** | O rationale não pode ser circular (ex: "precisamos de X porque Y, e Y porque X"). |
| **Dependências** | REGCON-009, REGREQ-004. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RN-042: Classificação ACMG. Rationale: A diretriz ACMG 2024 exige que variantes classe 5 sejam automaticamente reportadas como patogênicas. A não implementação gera risco de laudos incorretos e exposição jurídica." |
| **Exemplo Negativo** | "RN-042: Classificar variantes." (sem rationale). |
| **Anti-pattern** | Copiar o texto da descrição no rationale, sem adicionar valor. |
| **Métrica** | Percentual de requisitos com rationale preenchido (meta: 100%). |
| **Critérios de Auditoria** | Revisar se o rationale responde às 4 perguntas obrigatórias. |
