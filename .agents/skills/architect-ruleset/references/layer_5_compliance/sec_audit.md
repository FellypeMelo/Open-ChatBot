# Seção 8 – Regras de Auditoria, Logs e Monitoramento (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-AUDIT  
**Status:** Definitivo  
**Escopo:** Trilha de auditoria imutável (append-only), regras de SIEM e detecção contínua de anomalias operacionais.

---

### REGSEC-008 – Trilha de Auditoria Imutável (Append-Only) para Dados Restritos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-008 |
| **Nome** | Trilha de Auditoria Imutável (Append-Only) para Dados Restritos |
| **Descrição** | O agente deve garantir que todas as operações de criação, leitura, atualização e exclusão (CRUD) realizadas em dados classificados como **RESTRITO** sejam registradas em uma trilha de auditoria imutável (append-only). A trilha deve conter: **(1)** identidade do usuário/serviço que realizou a ação; **(2)** data/hora com alta resolução; **(3)** endereço IP ou identificador de origem; **(4)** ação executada (CREATE, READ, UPDATE, DELETE); **(5)** identificador do recurso afetado; **(6)** dados anteriores e posteriores (para updates); **(7)** justificativa (se aplicável). A trilha deve ser armazenada em um sistema que impeça alterações ou exclusões (ex: banco com WORM, AWS S3 Object Lock, ou sistema de log centralizado com hash chain). |
| **Objetivo** | Fornecer evidência forense em caso de incidentes, garantir não repúdio e atender a requisitos de auditoria (SOX, LGPD). |
| **Motivação** | Cap. 9.2.2 (rastreabilidade simbólica) e Cap. 10 (ferramentas de monitoramento). |
| **Justificativa** | Sem uma trilha imutável, é impossível investigar violações ou provar que os dados foram tratados corretamente. A LGPD exige transparência e rastreabilidade. |
| **Critérios de Aplicação** | Operações em dados RESTRITO (genômica, diagnósticos, dados bancários). |
| **Critérios de Não Aplicação** | Dados PÚBLICOS e INTERNOS (logs de sistema sem dados pessoais). |
| **Pré-condições** | Sistema de auditoria configurado. |
| **Pós-condições** | Cada ação é registrada na trilha antes do commit da transação. |
| **Restrições** | A trilha não pode ser desativada para usuários privilegiados (ex: administradores também são auditados). |
| **Dependências** | REGSEC-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Acesso à tabela `variants` para leitura do paciente X registrado: `{user: 'dr.carlos', timestamp: '2025-01-15T10:00:00Z', action: 'READ', resource: 'variant:123', ip: '10.0.1.5'}`." |
| **Exemplo Negativo** | "Logs de acesso não são mantidos ou são mantidos em arquivos de texto editáveis." |
| **Anti-pattern** | Registrar apenas ações de CREATE e DELETE, ignorando READ (acesso) que é o mais comum. |
| **Métrica** | Percentual de operações em dados restritos com registro na trilha (meta: 100%). |
| **Critérios de Auditoria** | Revisar a trilha para confirmar a imutabilidade (ex: tentativa de alteração de log antigo é bloqueada). |

---

### REGSEC-009 – Monitoramento Contínuo e Detecção de Anomalias

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-009 |
| **Nome** | Monitoramento Contínuo e Detecção de Anomalias |
| **Descrição** | O agente deve garantir que os logs de auditoria e os logs de sistema sejam monitorados continuamente por um sistema de SIEM (Security Information and Event Management) ou ferramenta equivalente, com regras de detecção de anomalias. Pelo menos as seguintes regras devem ser implementadas: **(1)** Múltiplas falhas de autenticação sucessivas (força bruta); **(2)** Acesso a dados restritos fora do horário comercial (anomalia de horário); **(3)** Acesso a dados restritos por usuários que não costumam acessá-los (anomalia de comportamento); **(4)** Pico de download de dados sensíveis; **(5)** Tentativas de exclusão de logs de auditoria. Alertas devem ser disparados para o time de segurança em tempo real. |
| **Objetivo** | Detectar e responder a incidentes de segurança rapidamente, reduzindo o tempo de exposição (MTTD - Mean Time to Detect). |
| **Motivação** | Cap. 8.2.1 (monitoramento de recursos) e NIST (incident response). |
| **Justificativa** | A detecção tardia de violações aumenta exponencialmente os danos e os custos de remediação. |
| **Critérios de Aplicação** | Sistemas que manipulam dados RESTRITO e CONFIDENCIAL. |
| **Critérios de Não Aplicação** | Sistemas de baixa criticidade. |
| **Pré-condições** | SIEM ou ferramenta de monitoramento configurada. |
| **Pós-condições** | Alertas gerados e investigados conforme procedimento. |
| **Restrições** | As regras de detecção devem ser revisadas e atualizadas trimestralmente. |
| **Dependências** | REGSEC-008. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Alerta disparado: 10 falhas de autenticação consecutivas para o usuário 'dr.carlos' às 03:00. Time de segurança investigou e bloqueou o IP." |
| **Exemplo Negativo** | "Ninguém notou que o bucket S3 foi acessado por um IP russo às 04:00 por 3 horas." |
| **Anti-pattern** | Gerar tantos alertas falsos que o time de segurança os ignora (alerta fadiga). |
| **Métrica** | Tempo médio de detecção (MTTD) e tempo médio de resposta (MTTR). |
| **Critérios de Auditoria** | Revisar relatórios de incidentes e o tempo de detecção. |
