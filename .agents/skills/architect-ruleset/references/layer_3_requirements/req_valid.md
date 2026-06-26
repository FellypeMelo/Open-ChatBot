# Seção 5 – Regras de Validação e Comprometimento / Layer 3 (Layer 3 - Requisitos)

**ID:** ARCH-RULESET-L3-REQ-VALID  
**Status:** Definitivo  
**Escopo:** Distinção de papéis de validação, métodos síncronos e escalações obrigatórias de impasses.

---

### REGREQ-008 – Validação de Conteúdo vs. Comprometimento (Separação de Papéis)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-008 |
| **Nome** | Validação de Conteúdo vs. Comprometimento (Separação de Papéis) |
| **Descrição** | O agente deve distinguir claramente entre dois tipos de validação: **(1) Validação de Conteúdo**: realizada por especialistas do domínio para verificar se o requisito está correto (ex: "a regra ACMG está correta?"); **(2) Comprometimento Formal**: realizado por tomadores de decisão (gerentes, patrocinadores) para assumir a responsabilidade pela implementação (ex: "aprovo o custo e o cronograma"). Ambos são obrigatórios, mas envolvem pessoas diferentes e ocorrem em momentos diferentes. O agente não pode tratar um como substituto do outro. |
| **Objetivo** | Evitar que a aprovação técnica seja confundida com aprovação executiva, e vice-versa. |
| **Motivação** | Cap. 7.4.5 e 7.4.6. |
| **Justificativa** | Um requisito pode estar tecnicamente correto (validação de conteúdo) mas ser inviável financeiramente (comprometimento). Ambos os aspectos precisam ser avaliados separadamente. |
| **Critérios de Aplicação** | Em todo processo de aprovação de requisitos. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Requisito especificado. |
| **Pós-condições** | O requisito tem dois campos: `Validado_Conteudo_por` e `Comprometido_por`. |
| **Restrições** | As mesmas pessoas não podem realizar ambos os papéis para o mesmo requisito (separaçao de poderes). |
| **Dependências** | REGREQ-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "RN-042: Validação de conteúdo por Dr. Carlos (especialista ACMG) em 10/10/2024. Comprometimento formal por Dra. Mariana (PO) em 15/10/2024, após análise de custo." |
| **Exemplo Negativo** | "RN-042 aprovada" (sem distinguir quem validou o quê). |
| **Anti-pattern** | Pedir aprovação executiva antes da validação técnica, gerando retrabalho. |
| **Métrica** | Percentual de requisitos com ambos os campos preenchidos. |
| **Critérios de Auditoria** | Verificar se ambos os campos estão preenchidos para cada requisito aprovado. |

---

### REGREQ-009 – Proibição de Validação Assíncrona para Requisitos Complexos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-009 |
| **Nome** | Proibição de Validação Assíncrona para Requisitos Complexos |
| **Descrição** | Requisitos complexos (definidos como aqueles com mais de 3 dependências, ou que afetam mais de 1 módulo, ou que envolvem segurança/compliance) NÃO podem ser validados por e-mail, documentos compartilhados assíncronos ou qualquer forma de comunicação não síncrona. Devem ser validados em workshops, reuniões ou entrevistas face-a-face (ou videoconferência síncrona). |
| **Objetivo** | Garantir que a validação de requisitos complexos envolva discussão, questionamento e resolução de conflitos em tempo real. |
| **Motivação** | Cap. 7.4.5 – "Feedback rounds via e-mail não funcionam. Encontre pessoas-chave e discuta face a face." |
| **Justificativa** | Requisitos complexos têm implicações cruzadas que não são capturadas em comunicações assíncronas. O e-mail gera mal-entendidos e decisões unilaterais. |
| **Critérios de Aplicação** | Requisitos com complexidade >= 3 (conforme métrica de complexidade). |
| **Critérios de Não Aplicação** | Requisitos simples (1 dependência, 1 módulo, sem impacto crítico). |
| **Pré-condições** | Complexidade do requisito avaliada. |
| **Pós-condições** | Validação registrada como "Síncrona" com data e participantes. |
| **Restrições** | Se a validação síncrona não for possível, o agente deve recomendar a simplificação do requisito ou a escalação para um comitê. |
| **Dependências** | REGREQ-008. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RT-023 (dimensionamento de infra) validada em workshop com arquitetos, PO e SRE em 20/10/2024." |
| **Exemplo Negativo** | "RT-023 enviada por e-mail para todos aprovarem." |
| **Anti-pattern** | Fazer uma reunião, mas sem pauta nem facilitação, tornando-a ineficaz. |
| **Métrica** | Percentual de requisitos complexos validados de forma síncrona. |
| **Critérios de Auditoria** | Revisar histórico de validação de requisitos complexos. |

---

### REGREQ-010 – Escalação Obrigatória de Requisitos com Conflito Irresolvível

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-010 |
| **Nome** | Escalação Obrigatória de Requisitos com Conflito Irresolvível |
| **Descrição** | Se o agente identificar um conflito entre dois ou mais requisitos que não possa ser resolvido pela hierarquia de decisão (REGCON-007) ou por um trade-off documentado, o agente deve imediatamente escalar o conflito para o comitê de arquitetura ou para o patrocinador executivo, documentando o impasse, as alternativas e as implicações de cada uma. |
| **Objetivo** | Garantir que conflitos de requisitos não sejam "varridos para debaixo do tapete", mas resolvidos no nível apropriado da organização. |
| **Motivação** | Cap. 9.4.2 (conflito entre otimização global e local) e Cap. 6.3.5 (breakdown por conflito). |
| **Justificativa** | Conflitos não resolvidos geram implementações inconsistentes e, eventualmente, falhas em produção. |
| **Critérios de Aplicação** | Quando a resolução automática (pela hierarquia) não for possível ou gerar uma solução inaceitável para um stakeholder. |
| **Critérios de Não Aplicação** | Conflitos resolvidos pela hierarquia de decisão. |
| **Pré-condições** | Conflito identificado e não resolvido. |
| **Pós-condições** | Conflito registrado e escalado. |
| **Restrições** | O agente deve fornecer um resumo executivo do conflito para a instância decisora. |
| **Dependências** | REGCON-007, REGRSN-003. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Conflito: RN-045 (processar todos os arquivos) vs. RT-023 (limite 10GB). Ambos na Layer 3. A hierarquia não resolve. Escalo para o Comitê de Arquitetura com as opções: (1) aumentar limite (custo alto), (2) processamento assíncrono (prazo maior), (3) dividir arquivos." |
| **Exemplo Negativo** | Ignorar o conflito e seguir com a análise. |
| **Anti-pattern** | Resolver o conflito com base em preferência pessoal do agente, sem consultar os stakeholders. |
| **Métrica** | Tempo médio para escalação vs. tempo de resolução. |
| **Critérios de Auditoria** | Revisar se todos os conflitos irresolvíveis foram escalados. |
