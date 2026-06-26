# Seção 8 – Auditoria, Exemplo Integrado e Evolução / Layer 7 (Layer 7 - Governança, Alinhamento e Gestão de Mudanças)

**ID:** ARCH-RULESET-L7-GOV-AUDIT-EXAMPLE  
**Status:** Definitivo  
**Escopo:** Critérios de auditoria para governança arquitetural, caso de uso clínico integrado e direções de evolução.

---

## 1. Critérios de Auditoria de Governança

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-GOV-01 | Matriz RACI associada para decisões de arquitetura (REGGOV-001). | Revisar se as decisões em ADRs possuem preenchimento de matriz RACI. |
| AUD-GOV-02 | Comitê de Arquitetura ativo em decisões críticas (REGGOV-002). | Validar a presença de atas de comitê ou assinaturas de aprovação vinculadas a CRs de alto impacto. |
| AUD-GOV-03 | Alinhamento de módulos/Bounded Contexts com times (REGGOV-003). | Validar o mapeamento de propriedade técnica (squads vs. repositórios). |
| AUD-GOV-04 | Camadas organizadas de acordo com o padrão FMO (REGGOV-004). | Revisar arquitetura de interfaces, regras e banco de dados. |
| AUD-GOV-05 | Otimização global priorizada sobre interesses locais (REGGOV-005). | Inspecionar propostas de adoção de frameworks que saiam do padrão de portfólio. |
| AUD-GOV-06 | CRs abertos para alterações estruturais relevantes (REGGOV-006). | Auditar o sistema de tickets (Jira) buscando a correlação de commits com CRs. |
| AUD-GOV-07 | Análise de impacto documentada contendo plano de rollback (REGGOV-007). | Revisar o preenchimento de avaliações técnicas em CRs ativos. |
| AUD-GOV-08 | Ciclo de vida e status de maturidade documentados (REGGOV-008). | Confirmar metadados de status (Rascunho, Em Revisão, Aprovado) nos documentos. |
| AUD-GOV-09 | Artefatos e especificações legadas depreciados formalmente (REGGOV-009). | Inspecionar a presença de avisos e prazos de expiração em documentos obsoletos. |
| AUD-GOV-10 | Conflitos irresolvíveis escalados formalmente com opções de trade-off (REGGOV-010). | Verificar logs de escalação para o Comitê, DPO ou Patrocinador Executivo. |

---

## 2. Exemplo Integrado de Aplicação do Módulo 08

**Cenário:** O time de engenharia do Bounded Context de Genômica propõe a adoção do CockroachDB no VarSuS-Web-System para suportar alta escalabilidade distribuída multi-região (dados clínicos multi-tenant). O agente atua na aplicação das regras de governança para este caso.

**Aplicação das Regras Passo a Passo:**

1. **REGGOV-006 (Processo de Change Request - CR):**
   - O agente detecta que o time iniciou a codificação de adaptadores de banco em uma branch sem abrir um ticket formal. Ele bloqueia o pipeline e solicita a criação do CR `#789: Transição para CockroachDB`.

2. **REGGOV-007 (Análise de Impacto Detalhada):**
   - O agente exige o preenchimento da análise de impacto. Identifica que a mudança afeta 3 módulos diretamente (Classificação, Laudos e Relatórios) e impacta os requisitos de performance (`RT-023`) e privacidade (`REGLGPD-003`). O plano de rollback (restaurar backup PG) e riscos de suporte de queries específicas no CockroachDB são formalizados.

3. **REGGOV-002 (Comitê de Arquitetura):**
   - Como a mudança afeta mais de 3 módulos e envolve tecnologia central de banco, o CR é submetido ao Comitê de Arquitetura. O Comitê agenda uma revisão, faz apontamentos sobre custo extra e aprova o CR condicionalmente mediante a realização de testes de estresse em homologação.

4. **REGGOV-001 (RACI):**
   - Vincula-se a matriz RACI no ADR correspondente:
     - **Responsável (R):** Gabriel (Backend Architect) - que escreve e testa a migração.
     - **Accountável (A):** Marcos (Chief Architect) - que aprova o design final.
     - **Consultado (C):** Time de CyberSec, DBA e DPO (verificação de criptografia AES-256 e LGPD).
     - **Informado (I):** Time de Frontend (Davy) e desenvolvedores dos outros squads.

5. **REGGOV-003 & REGGOV-004 (Alinhamento Lei de Conway e FMO):**
   - O Bounded Context de Genômica pertence exclusivamente ao time de Genômica. A camada do banco (CockroachDB) é classificada como *Back-office* do padrão FMO. Ela receberá escritas mediadas pelas regras de negócio da API central (*Mid-office*).

6. **REGGOV-005 (Otimização Global vs Local):**
   - O time de Genômica argumentou que a performance local melhoraria. O agente validou que a escalabilidade global do VarSuS-Web-System justifica o custo extra de infraestrutura do CockroachDB. O trade-off global é aceito.

7. **REGGOV-008 & REGGOV-009 (Maturidade e Depreciação):**
   - O status do ADR muda de "Em Revisão" para "Aprovado".
   - As especificações antigas de conexão única do PostgreSQL são marcadas como `Depreciadas` com um prazo de transição de 30 dias para remoção definitiva das configs antigas das variáveis de ambiente de produção.

---

## 3. Evolução e Extensibilidade

Este módulo de governança técnica prevê as seguintes direções de expansão:
* **Módulo 08-A (Governança de Portfólio):** Alocação de recursos e priorização de arquitetura orientada a valor estratégico (TCO e ROI).
* **Módulo 08-B (Governança de Dados):** Políticas integradas de metadados, linhagem de dados e propriedade de tabelas e buckets.
* **Módulo 08-C (Governança Regulada):** Auditoria contínua de controles de processos (SOX, ANVISA, FDA).
