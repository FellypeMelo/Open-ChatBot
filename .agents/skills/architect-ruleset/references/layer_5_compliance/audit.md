# Seção 10 – Auditoria, Exemplo Integrado e Evolução / Layer 5 (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-AUDIT-EXAMPLE  
**Status:** Definitivo  
**Escopo:** Métodos de validação de conformidade de segurança e privacidade, caso de uso clínico integrado e evolução da Layer 5.

---

## 1. Critérios de Auditoria de Segurança e Privacidade

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-SEC-01 | Todos os dados têm classificação definida (REGSEC-001). | Revisar dicionário de dados e schemas PostgreSQL. |
| AUD-SEC-02 | Inventário de ativos completo e atualizado (REGSEC-002). | Comparar recursos reais de infraestrutura contra a planilha de inventário. |
| AUD-SEC-03 | RBAC implementado com menor privilégio (REGSEC-003). | Validar perfis de usuários (`Geneticist`, `Admin`, `Auditor`) no banco. |
| AUD-SEC-04 | MFA ativo para dados restritos (REGSEC-004). | Verificar requisição de MFA em rotas de dados sensíveis e credenciais administrativas. |
| AUD-SEC-05 | TLS 1.3+ em todas as comunicações (REGSEC-005). | Rodar testes de handshake SSL/TLS nos endpoints e interconexões. |
| AUD-SEC-06 | Criptografia em repouso ativa (REGSEC-006). | Inspecionar configurações do RDS Postgres, buckets S3 e logs. |
| AUD-SEC-07 | Consentimento documentado para dados sensíveis (REGLGPD-001). | Buscar correspondência entre exames cadastrados e logs de aceite de termos. |
| AUD-SEC-08 | Suporte aos direitos do titular (REGLGPD-002). | Testar endpoints de exclusão lógica/expurgo e portabilidade. |
| AUD-SEC-09 | Política de retenção e expurgo ativa (REGLGPD-003). | Monitorar a execução e logs do cron/job diário de anonimização e expurgo. |
| AUD-SEC-10 | DPIA arquivado para projetos de alto risco (REGLGPD-004). | Validar existência do relatório de impacto assinado pelo DPO/CISO. |
| AUD-SEC-11 | Modelagem STRIDE para mudanças arquiteturais (REGSEC-007). | Revisar diagramas DFD e controles mitigadores documentados. |
| AUD-SEC-12 | Trilha de auditoria imutável (REGSEC-008). | Simular escrita de log e testar políticas de bloqueio de escrita (Object Lock/WORM). |
| AUD-SEC-13 | Monitoramento SIEM ativo (REGSEC-009). | Verificar triggers de alertas em tempo de execução para acessos anômalos. |
| AUD-SEC-14 | Plano de resposta a incidentes testado (REGSEC-010). | Revisar atas e relatórios de simulações periódicas (Red/Blue Team). |
| AUD-SEC-15 | Gestão de vulnerabilidades ativa (REGSEC-011). | Validar relatórios de CI/CD para SAST/DAST e patch management. |

---

## 2. Exemplo Integrado de Aplicação do Módulo 06

**Cenário:** O time de desenvolvimento do VarSuS-Web-System está implementando o serviço de processamento e classificação genômica das variantes (Módulo Científico) que recebe arquivos VCF carregados por clínicas parceiras.

**Aplicação das Regras Passo a Passo:**

1. **REGSEC-001 (Classificação de Dados):**
   - Dados brutos de genoma (`patient_genome`) e informações do paciente (nome, CPF) são classificados como **RESTRITO**.
   - Arquivos VCF pseudonimizados e suas coordenadas genômicas estruturadas são **CONFIDENCIAL**.
   - Listagens públicas de variantes genéticas de referência são **PÚBLICO**.

2. **REGSEC-002 (Inventário de Ativos):**
   - O novo bucket `varsus-vcf-uploads-prod` e o schema `tenant_1` são catalogados no inventário de ativos sob a propriedade do time de Genômica, associando as políticas de segurança adequadas.

3. **REGSEC-003 & REGSEC-004 (RBAC e MFA):**
   - O endpoint de upload e análise do VCF é protegido por RBAC. Usuários com a role `Geneticist` podem fazer upload e classificar variantes, mas apenas usuários com a role `DPO` ou `SecurityAdmin` podem visualizar trilhas de auditoria globais.
   - Qualquer login na plataforma exige autenticação por dois fatores (MFA) via Keycloak integrado com token TOTP.

4. **REGSEC-005 & REGSEC-006 (Criptografia):**
   - A comunicação entre a API Go e o Worker Python (Redis) é criptografada com TLS 1.3.
   - Os arquivos VCF em repouso no S3 são criptografados com chaves gerenciadas no AWS KMS (AES-256) com rotação anual automática. O banco de dados PostgreSQL utiliza criptografia a nível de disco (RDS KMS) e os dados pessoais sensíveis são criptografados no `identity_db` a nível de coluna (AES-256-GCM).

5. **REGLGPD-001 & REGLGPD-002 (Consentimento e Direitos):**
   - Antes do upload do VCF, o médico deve anexar ou confirmar o Termo de Consentimento Livre e Esclarecido (TCLE) assinado pelo paciente. O sistema guarda o timestamp, o hash do termo v1.1 e o IP no banco de consentimentos.
   - Se o paciente exercer o direito de exclusão, o endpoint `/api/v1/patients/{id}` agenda a deleção física do arquivo VCF e a anonimização irreversível dos dados estruturados no banco, respeitando eventuais deveres legais de guarda de prontuários.

6. **REGSEC-007 (STRIDE) & REGSEC-008 (Auditoria):**
   - Na modelagem de ameaças (STRIDE), mapeou-se o risco de *Information Disclosure* de variantes de pacientes na fila do Redis. Mitigou-se garantindo que a fila trafegue apenas o ID opaco da análise, forçando os Workers Python a buscarem os dados diretamente do Postgres por meio de conexões autenticadas e restritas.
   - Toda leitura e escrita em dados genéticos gera uma linha em `audit_logs` no Postgres e é replicada para um bucket S3 append-only em modo WORM (Write Once, Read Many).

7. **REGSEC-009, REGSEC-010 & REGSEC-011 (SIEM, Incidente e Vulnerabilidades):**
   - O SIEM dispara um alerta de severidade alta caso o mesmo usuário `dr.carlos` tente baixar mais de 5 laudos de pacientes diferentes em menos de 1 minuto.
   - Caso um vazamento seja suspeitado, entra em ação o plano de resposta: isolamento do tenant, rotação de chaves KMS, análise forense no log imutável de auditoria, e comunicação estruturada à ANPD em até 48 horas.
   - No pipeline do GitHub Actions, o Snyk/Trivy verifica as dependências do worker Python e bloqueia o build caso encontre vulnerabilidades críticas ou altas (como versões defasadas de `pysam` com buffers vulneráveis).

---

## 3. Evolução e Extensibilidade

Este módulo de segurança é projetado para expandir-se nos seguintes cenários:
* **Módulo 06-A (mTLS & Service Mesh):** Regras de provisionamento automático de certificados TLS para microserviços em ambientes de alta densidade (ex: Istio/Linkerd).
* **Módulo 06-B (Criptografia Homomórfica):** Análise estatística de variantes genéticas diretamente sobre dados criptografados, garantindo privacidade matemática ponta a ponta.
* **Módulo 06-C (Certificações de Saúde):** Requisitos regulatórios internacionais específicos, como HIPAA (Estados Unidos) e certificação ANVISA classe de risco II/III.
