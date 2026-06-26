# Seção 3 – Regras de Classificação e Inventário de Dados (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-CLASS  
**Status:** Definitivo  
**Escopo:** Definição de níveis de criticidade e rastreamento de ativos de informação.

---

### REGSEC-001 – Obrigação de Classificação de Dados por Níveis de Sensibilidade

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-001 |
| **Nome** | Obrigação de Classificação de Dados por Níveis de Sensibilidade |
| **Descrição** | O agente deve garantir que todos os dados manipulados pelo sistema sejam classificados em um dos quatro níveis obrigatórios: **(1) Público**: dados que podem ser divulgados livremente (ex: políticas de privacidade, contatos da empresa); **(2) Interno**: dados cuja divulgação não é desejada, mas não causa dano severo (ex: organograma, manuais internos); **(3) Confidencial**: dados cuja divulgação pode causar dano financeiro, reputacional ou operacional (ex: segredos comerciais, códigos-fonte, dados de clientes não sensíveis); **(4) Restrito (LGPD/Sensível)**: dados pessoais sensíveis (LGPD Art. 5, II) ou dados críticos cuja violação é inaceitável (ex: dados genômicos, diagnósticos, credenciais, chaves criptográficas). Esta classificação deve ser aplicada a cada campo, tabela, arquivo ou mensagem. |
| **Objetivo** | Garantir que cada dado receba o nível de proteção adequado, evitando superproteção (custos desnecessários) ou subproteção (riscos de violação). |
| **Motivação** | Cap. 5.4.1 (Objetos de Negócio e suas representações) e Cap. 9.2.2 (Mundo Simbólico e Físico). |
| **Justificativa** | A classificação de dados é a base para definir controles de acesso, criptografia, retenção e expurgo. Sem classificação, a segurança é aplicada de forma arbitrária. |
| **Critérios de Aplicação** | Todo atributo, tabela, arquivo, mensagem ou fluxo de dados. |
| **Critérios de Não Aplicação** | Dados temporários em memória (cache) que não são persistidos, desde que não contenham dados restritos. |
| **Pré-condições** | Inventário de dados iniciado. |
| **Pós-condições** | Cada elemento de dados possui uma classificação documentada (ex: metadado `classification: "RESTRITO"`). |
| **Restrições** | A classificação não pode ser alterada sem aprovação do DPO/CISO. Reclassificação deve ser registrada na auditoria. |
| **Dependências** | REGREQ-004, REGSEC-007 (inventário). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Campo `patient_genome`: classificação = RESTRITO (LGPD sensível). Campo `hospital_name`: classificação = CONFIDENCIAL." |
| **Exemplo Negativo** | "Todos os dados são tratados como internos, sem diferenciação." |
| **Anti-pattern** | Classificar tudo como "RESTRITO" para evitar o trabalho de classificar corretamente, gerando custos operacionais desnecessários. |
| **Métrica** | Percentual de atributos com classificação definida (meta: 100%). |
| **Critérios de Auditoria** | Revisar o dicionário de dados: se algum campo não tiver classificação, falha. |

---

### REGSEC-002 – Inventário de Ativos de Informação Obrigatório

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-002 |
| **Nome** | Inventário de Ativos de Informação Obrigatório |
| **Descrição** | O agente deve garantir a existência e a manutenção de um Inventário de Ativos de Informação, contendo: **(1)** identificação de cada ativo (banco de dados, tabela, bucket S3, fila, arquivo, API); **(2)** proprietário do ativo (time responsável); **(3)** classificação de dados (REGSEC-001); **(4)** localização física (região, nuvem, on-premise); **(5)** medidas de proteção aplicadas (criptografia, backups, MFA); **(6)** data de criação e de última revisão. O inventário deve ser atualizado a cada nova funcionalidade ou alteração arquitetural. |
| **Objetivo** | Garantir visibilidade total sobre onde os dados residem e quem é responsável por eles, permitindo análises de risco e respostas a incidentes. |
| **Motivação** | Cap. 9.2.2 (Mundo Físico – localização e infraestrutura) e Cap. 10.4.5 (formatos de troca). |
| **Justificativa** | Você não pode proteger o que não sabe que existe. A maioria das violações ocorre em dados "esquecidos" (shadow IT, buckets públicos). |
| **Critérios de Aplicação** | Todo novo ativo de informação criado (banco, bucket, fila). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Processo de criação de ativos integrado ao pipeline (ex: Terraform). |
| **Pós-condições** | Ativo registrado no inventário com todos os metadados. |
| **Restrições** | Ativos legados devem ser inventariados em até 90 dias da adoção desta regra. |
| **Dependências** | REGSEC-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Inventário: `genomics-db` (PostgreSQL, time Genômica, classificação RESTRITO, local: AWS us-east-1, criptografia: AES-256, backup: diário)." |
| **Exemplo Negativo** | "Não temos ideia de onde os dados genômicos estão armazenados." |
| **Anti-pattern** | Criar buckets S3 públicos para "testes" e depois esquecer deles. |
| **Métrica** | Percentual de ativos com registro no inventário (meta: 100%). |
| **Critérios de Auditoria** | Revisar o inventário contra a infraestrutura real (ex: scan de recursos na nuvem). |
