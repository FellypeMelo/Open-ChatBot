# Seção 4 – Regras de Controle de Acesso e IAM (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-ACCESS  
**Status:** Definitivo  
**Escopo:** Gestão de identidades, autorização por papéis (RBAC) e autenticação multifator.

---

### REGSEC-003 – Controle de Acesso Baseado em Função (RBAC) Obrigatório com Menor Privilégio

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-003 |
| **Nome** | Controle de Acesso Baseado em Função (RBAC) Obrigatório com Menor Privilégio |
| **Descrição** | O agente deve garantir que todo o controle de acesso seja gerenciado por um modelo RBAC (Role-Based Access Control) centralizado, onde permissões são atribuídas a funções (roles), e os usuários/atores assumem funções. O princípio do menor privilégio (least privilege) deve ser aplicado: uma função só deve ter as permissões estritamente necessárias para executar suas tarefas. Funções com permissões excessivas (ex: "admin" com acesso total) são proibidas, a menos que sejam justificadas por requisitos de operação crítica e aprovadas pelo CISO. |
| **Objetivo** | Minimizar a superfície de ataque e limitar danos em caso de comprometimento de credenciais. |
| **Motivação** | Cap. 5.4.1 (Business Role como conceito central) e Cap. 9.3.2 (infraestrutura de domínios). |
| **Justificativa** | O RBAC é o padrão da indústria para controle de acesso. O menor privilégio reduz drasticamente o impacto de credenciais comprometidas. |
| **Critérios de Aplicação** | Todo serviço, aplicação, API ou banco de dados que exija autenticação. |
| **Critérios de Não Aplicação** | Sistemas sem autenticação (ex: sites públicos estáticos). |
| **Pré-condições** | Funções (roles) definidas com base nas atividades dos stakeholders. |
| **Pós-condições** | Acesso concedido apenas com base nas funções atribuídas. |
| **Restrições** | A criação de novas funções deve passar por revisão de segurança. |
| **Dependências** | REGSEC-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Função `GenomicScientist`: permissão para LER dados da tabela `variants` e CRIAR laudos, mas NÃO DELETAR dados." |
| **Exemplo Negativo** | "Função `admin` com acesso total a todos os bancos." |
| **Anti-pattern** | Usar uma única conta de serviço para múltiplas aplicações, sem distinguir permissões. |
| **Métrica** | Número de funções com permissões excessivas (meta: zero). |
| **Critérios de Auditoria** | Revisar a matriz de permissões de cada função. |

---

### REGSEC-004 – Autenticação Multifator (MFA) Obrigatória para Dados Restritos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-004 |
| **Nome** | Autenticação Multifator (MFA) Obrigatória para Dados Restritos |
| **Descrição** | O agente deve exigir Autenticação Multifator (MFA) para qualquer acesso a systems, aplicações ou dados classificados como RESTRITO ou CONFIDENCIAL (criticidade alta). O MFA deve combinar pelo menos dois fatores de tipos diferentes: **(1)** algo que o usuário sabe (senha), **(2)** algo que o usuário possui (token TOTP, smart card), **(3)** algo que o usuário é (biometria). O uso de SMS como segundo fator é desencorajado devido a vulnerabilidades conhecidas (SIM swapping). |
| **Objetivo** | Reduzir drasticamente o risco de acessos não autorizados devido a credenciais comprometidas (ex: vazamento de senhas). |
| **Motivação** | OWASP, NIST, e práticas de segurança de mercado. A LGPD também exige medidas técnicas adequadas para proteger dados. |
| **Justificativa** | Senhas únicas são insuficientes. O MFA bloqueia mais de 99% dos ataques de comprometimento de contas. |
| **Critérios de Aplicação** | Acesso a dados Restritos, operações administrativas, alterações de configuração de segurança. |
| **Critérios de Não Aplicação** | Acesso a dados públicos ou internos de baixa criticidade (ex: documentos públicos). |
| **Pré-condições** | Provedor de identidade configurado (ex: Azure AD, Auth0, Keycloak). |
| **Pós-condições** | Acesso negado se MFA não for apresentado. |
| **Restrições** | O MFA deve ser exigido em todas as sessões, não apenas no login inicial (reauth para ações críticas). |
| **Dependências** | REGSEC-003. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Acesso ao banco de dados de genômica requer MFA (TOTP + senha)." |
| **Exemplo Negativo** | "Acesso ao banco de dados de genômica apenas com senha." |
| **Anti-pattern** | Usar MFA apenas no ambiente de produção, mas não no de desenvolvimento que contém dados anonimizados (ainda confidenciais). |
| **Métrica** | Percentual de acessos a dados restritos com MFA habilitado (meta: 100%). |
| **Critérios de Auditoria** | Revisar logs de autenticação para identificar acessos sem MFA a dados restritos. |
