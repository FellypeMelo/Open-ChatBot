# Seção 6 – Regras de Privacidade e LGPD (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-LGPD-RULES  
**Status:** Definitivo  
**Escopo:** Conformidade com a Lei Geral de Proteção de Dados (Lei 13.709/2018), cobrindo consentimento, direitos dos titulares, retenção e avaliações de impacto.

---

### REGLGPD-001 – Consentimento Explícito e Documentado para Dados Sensíveis

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGLGPD-001 |
| **Nome** | Consentimento Explícito e Documentado para Dados Sensíveis |
| **Descrição** | Para o tratamento de dados pessoais sensíveis (LGPD Art. 11 – origem racial, convicção religiosa, filiação sindical, dados genéticos, biométricos, relacionados à saúde ou vida sexual), o agente deve garantir que o consentimento do titular seja: **(1)** explícito (ação afirmativa clara, não por omissão ou pré-marcado); **(2)** informado (finalidade específica comunicada); **(3)** documentado (registro de data/hora, IP, versão do termo, meio de coleta). O consentimento deve ser revogável a qualquer momento, com a mesma facilidade com que foi dado. |
| **Objetivo** | Garantir conformidade com a LGPD, protegendo dados sensíveis e dando ao titular controle real sobre seus dados. |
| **Motivação** | LGPD Art. 5, 8, 11, 14. |
| **Justificativa** | Dados genômicos e de saúde são classificados como sensíveis pela LGPD. O tratamento inadequado pode gerar multas de até 2% do faturamento (limitado a R$ 50 milhões) e danos reputacionais. |
| **Critérios de Aplicação** | Qualquer operação que colete, armazene, processe ou compartilhe dados pessoais sensíveis. |
| **Critérios de Não Aplicação** | Dados anonimizados (irreversíveis) que não permitem identificação do titular. |
| **Pré-condições** | Política de privacidade e termos de consentimento aprovados juridicamente. |
| **Pós-condições** | Registro de consentimento armazenado com evidências. |
| **Restrições** | O consentimento deve ser registrado na trilha de auditoria (REGSEC-008). |
| **Dependências** | REGSEC-001 (classificação), REGSEC-008 (auditoria). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Termo de consentimento para análise genômica: checkbox explicitamente marcado, registro com timestamp, IP e versão do termo v1.0 armazenado em banco." |
| **Exemplo Negativo** | "Termo de consentimento genérico escondido em um link no rodapé, sem ação afirmativa." |
| **Anti-pattern** | Compartilhar dados sensíveis com terceiros sem consentimento específico para essa finalidade. |
| **Métrica** | Percentual de titulares com consentimento documentado para cada finalidade. |
| **Critérios de Auditoria** | Revisar logs de consentimento e comparar com as finalidades de processamento. |

---

### REGLGPD-002 – Direitos do Titular (Portabilidade, Retificação, Exclusão) – Implementação Obrigatória

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGLGPD-002 |
| **Nome** | Direitos do Titular (Portabilidade, Retificação, Exclusão) – Implementação Obrigatória |
| **Descrição** | O agente deve garantir que o sistema suporte operacionalmente os direitos dos titulares previstos na LGPD (Art. 18), incluindo: **(1)** Direito de acesso (fornecer uma cópia dos dados); **(2)** Direito de retificação (correção de dados incompletos/inexatos); **(3)** Direito de exclusão (eliminação de dados pessoais, exceto quando houver base legal para retenção); **(4)** Direito de portabilidade (fornecer dados em formato estruturado, interoperável e legível por máquina); **(5)** Direito de revogação de consentimento. O tempo de resposta para essas solicitações não pode exceder 15 dias (LGPD Art. 19). |
| **Objetivo** | Garantir que os titulares possam exercer seus direitos de forma efetiva e dentro dos prazos legais. |
| **Motivação** | LGPD Art. 18 e 19. |
| **Justificativa** | A falta de capacidade técnica para atender a esses direitos é uma das principais causas de multas e reclamações na ANPD. |
| **Critérios de Aplicação** | Dados pessoais (not anonimizados) armazenados no sistema. |
| **Critérios de Não Aplicação** | Dados anonimizados irreversíveis. |
| **Pré-condições** | Mecanismo de identificação do titular (ex: token, CPF, login). |
| **Pós-condições** | A solicitação é processada e o titular é notificado. |
| **Restrições** | A exclusão deve ser lógica (soft delete) ou física, mas deve ser registrada na auditoria. Se houver base legal para reter, o titular deve ser informado. |
| **Dependências** | REGLGPD-003 (retenção). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Endpoint `DELETE /api/v1/patients/{id}` que dispara um workflow de expurgo, notificando o titular por e-mail e registrando na auditoria. Tempo de resposta: 3 dias." |
| **Exemplo Negativo** | "Não há endpoint para exclusão; o titular precisa enviar um e-mail e esperar semanas." |
| **Anti-pattern** | Excluir os dados, mas manter backups com os dados por anos sem justificativa. |
| **Métrica** | Tempo médio de resposta a solicitações de titulares (meta: < 15 dias). |
| **Critérios de Auditoria** | Revisar logs de solicitações de titulares e tempo de resolução. |

---

### REGLGPD-003 – Política de Retenção e Expurgo Automático (Fim da Finalidade)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGLGPD-003 |
| **Nome** | Política de Retenção e Expurgo Automático (Fim da Finalidade) |
| **Descrição** | O agente deve garantir que todos os dados pessoais tenham um prazo de retenção definido com base na finalidade do tratamento. Após o término da finalidade ou do prazo legal, os dados devem ser automaticamente expurgados (eliminados) ou anonimizados de forma irreversível. A política de retenção deve ser documentada e justificada (ex: retenção por 5 anos para cumprir obrigação fiscal, ou retenção enquanto o contrato estiver ativo). A exclusão automática deve ser testada periodicamente. |
| **Objetivo** | Cumprir o princípio da minimização de dados (LGPD Art. 6) e evitar o armazenamento desnecessário de dados pessoais, reduzindo riscos. |
| **Motivação** | LGPD Art. 6, 15, 16 (hipóteses de conservação de dados). |
| **Justificativa** | Manter dados pessoais além do necessário aumenta a superfície de ataque, o custo de armazenamento e o risco de violações. A lei exige a eliminação quando a finalidade é cumprida ou o consentimento é revogado. |
| **Critérios de Aplicação** | Dados pessoais (sensíveis ou não). |
| **Critérios de Não Aplicação** | Dados mantidos por obrigação legal ou regulatória (ex: registros contábeis por 5 anos), desde que justificados. |
| **Pré-condições** | Regras de retenção definidas para cada categoria de dado. |
| **Pós-condições** | Dados expurgados ou anonimizados após o prazo. |
| **Restrições** | O expurgo deve ser registrado na trilha de auditoria (quem, o quê, quando). |
| **Dependências** | REGSEC-001, REGLGPD-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Dados genômicos retidos por 5 anos após o último contato do paciente. Após esse prazo, um job diário anonimiza irreversivelmente (remove identificadores)." |
| **Exemplo Negativo** | "Dados armazenados indefinidamente 'por precaução'." |
| **Anti-pattern** | Deletar dados, mas manter cópias de backup que nunca são expurgadas. |
| **Métrica** | Percentual de dados expurgados dentro do prazo estipulado. |
| **Critérios de Auditoria** | Revisar logs de expurgo e confirmar que os dados foram efetivamente removidos. |

---

### REGLGPD-004 – Avaliação de Impacto à Proteção de Dados (DPIA) para Alto Risco

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGLGPD-004 |
| **Nome** | Avaliação de Impacto à Proteção de Dados (DPIA) para Alto Risco |
| **Descrição** | O agente deve exigir a realização de uma Avaliação de Impacto à Proteção de Dados (DPIA) para qualquer novo processo, tecnologia ou mudança arquitetural que envolva o tratamento de dados pessoais sensíveis (LGPD Art. 38) ou que apresente alto risco aos direitos e liberdades dos titulares. A DPIA deve incluir: **(1)** descrição do tratamento e finalidade; **(2)** avaliação de riscos (confidencialidade, integridade, disponibilidade); **(3)** medidas de mitigação; **(4)** consulta ao DPO. O relatório da DPIA deve ser aprovado antes da implementação. |
| **Objetivo** | Identificar e mitigar riscos à privacidade antes da implementação, evitando violações e multas. |
| **Motivação** | LGPD Art. 38 e GDPR Art. 35. |
| **Justificativa** | A DPIA é um requisito legal para operações de alto risco. Além disso, é uma ferramenta de engenharia que ajuda a projetar sistemas mais seguros. |
| **Critérios de Aplicação** | Novas funcionalidades que envolvam dados sensíveis ou sistemas de pontuação, processamento em larga escala, ou vigilância. |
| **Critérios de Não Aplicação** | Processos de baixo risco (ex: atualização de dados de contato não sensíveis). |
| **Pré-condições** | Processo de DPIA definido (modelo de documento). |
| **Pós-condições** | DPIA aprovada e arquivada. |
| **Restrições** | A DPIA deve ser revisada a cada 2 anos ou quando houver mudanças significativas. |
| **Dependências** | REGSEC-001, REGLGPD-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "DPIA realizada antes da implementação do novo serviço de classificação genômica: riscos identificados (vazamento), mitigados (criptografia, MFA, auditoria). Aprovado pelo DPO." |
| **Exemplo Negativo** | "Implementamos o serviço de classificação genômica sem DPIA." |
| **Anti-pattern** | Realizar a DPIA após o sistema estar em produção (apenas para "cumprir tabela"). |
| **Métrica** | Percentual de projetos de alto risco com DPIA aprovada (meta: 100%). |
| **Critérios de Auditoria** | Revisar documentação do projeto: se não houver DPIA, falha. |
