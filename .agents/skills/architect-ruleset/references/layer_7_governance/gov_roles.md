# Seção 3 – Regras de Papéis e Responsabilidades (Layer 7 - Governança, Alinhamento e Gestão de Mudanças)

**ID:** ARCH-RULESET-L7-GOV-ROLES  
**Status:** Definitivo  
**Escopo:** Definição da matriz RACI e comitê técnico para supervisão de decisões arquiteturais.

---

### REGGOV-001 – Matriz RACI Obrigatória para Decisões Arquiteturais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-001 |
| **Nome** | Matriz RACI Obrigatória para Decisões Arquiteturais |
| **Descrição** | O agente deve garantir que para toda decisão arquitetural significativa (ex: escolha de tecnologia, mudança de padrão, alteração de interface) exista uma Matriz RACI definindo quem é: **Responsável** (executa a ação – ex: arquiteto de solução), **Accountável** (aprova e responde pela decisão – ex: arquiteto-chefe), **Consultado** (deve ser ouvido antes da decisão – ex: time de segurança, DPO), **Informado** (deve ser notificado após a decisão – ex: desenvolvedores). A matriz deve ser revisada a cada mudança de papéis. |
| **Objetivo** | Eliminar ambiguidades sobre quem decide, quem executa, quem consulta e quem é informado, acelerando o processo decisório. |
| **Motivação** | Cap. 9.4.2 (governança e coordenação) e práticas de gestão de projetos (PMBOK). |
| **Justificativa** | Decisões sem papéis definidos sofrem atrasos (ninguém sabe quem aprova) ou são tomadas unilateralmente (sem consulta adequada). |
| **Critérios de Aplicação** | Toda decisão arquitetural de alto impacto (conforme critérios do Comitê). |
| **Critérios de Não Aplicação** | Decisões rotineiras ou já padronizadas (ex: escolha de biblioteca de logging). |
| **Pré-condições** | Papéis organizacionais definidos. |
| **Pós-condições** | Matriz RACI aprovada e anexada ao ADR ou documento de decisão. |
| **Restrições** | A mesma pessoa não pode ser Responsável e Accountável para a mesma decisão (segurança de decisão). |
| **Dependências** | REGDOC-002 (ADRs). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Decisão: Uso de Kafka para eventos. RACI: R = Arquiteto de Solução (João), A = Arquiteto-Chefe (Maria), C = Time de Segurança, DPO, I = Times de Desenvolvimento." |
| **Exemplo Negativo** | "Decidimos usar Kafka." (sem papéis definidos). |
| **Anti-pattern** | Atribuir R e A à mesma pessoa para "simplificar". |
| **Métrica** | Percentual de decisões com RACI documentado (meta: 100%). |
| **Critérios de Auditoria** | Revisar ADRs: se não tiver RACI, falha. |

---

### REGGOV-002 – Comitê de Arquitetura Obrigatório para Decisões de Alto Impacto

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-002 |
| **Nome** | Comitê de Arquitetura Obrigatório para Decisões de Alto Impacto |
| **Descrição** | O agente deve garantir que exista um Comitê de Arquitetura formal, composto por arquitetos-chefes, representantes de segurança, DPO e, quando necessário, representantes de negócio. O Comitê deve se reunir periodicamente (ex: quinzenal ou mensal) para revisar e aprovar decisões arquiteturais de alto impacto. Decisões que envolvam: **(1)** mudança de tecnologia central, **(2)** mudança de padrão de integração, **(3)** alteração de interface pública, **(4)** impacto em mais de 3 módulos, **(5)** impacto em segurança/compliance – **devem ser submetidas ao Comitê**. A decisão do Comitê é vinculativa e não pode ser contestada por instâncias inferiores. |
| **Objetivo** | Garantir que decisões de alto impacto sejam avaliadas por um grupo diversificado de especialistas, minimizando riscos e vieses. |
| **Motivação** | Cap. 6.1 (conceptual integrity requer supervisão) e Cap. 9.4.2 (governança colegiada). |
| **Justificativa** | Decisões unilaterais de um arquiteto podem ter consequências não antecipadas. O Comitê oferece uma visão multidisciplinar. |
| **Critérios de Aplicação** | Decisões com impacto em > 3 módulos ou com impacto em segurança/compliance. |
| **Critérios de Não Aplicação** | Decisões locais a um módulo, que não afetam outros módulos ou interfaces. |
| **Pré-condições** | Comitê constituído e com regimento interno. |
| **Pós-condições** | Decisão aprovada ou rejeitada pelo Comitê, com ata registrada. |
| **Restrições** | O Comitê pode delegar decisões menores a subcomitês, mas mantém a supervisão. |
| **Dependências** | REGGOV-001 (RACI). |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Proposta de migração para Kafka submetida ao Comitê de Arquitetura. Aprovada com ressalvas (plano de rollback). Ata registrada." |
| **Exemplo Negativo** | "Decisão de migrar para Kafka tomada por um arquiteto, sem revisão do Comitê." |
| **Anti-pattern** | Comitê com membros que não têm tempo ou interesse, tornando as reuniões superficiais. |
| **Métrica** | Percentual de decisões de alto impacto submetidas ao Comitê (meta: 100%). |
| **Critérios de Auditoria** | Revisar se decisões de alto impacto têm ata do Comitê. |
