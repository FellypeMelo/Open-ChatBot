# Seção 1 – Glossário Formal (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Terminologia canônica de segurança da informação e privacidade de dados com base na LGPD, ISO 27001, NIST e OWASP.

| Termo | Definição Canônica (Obrigatória) | Fonte / Padrão |
| :--- | :--- | :--- |
| **Política de Segurança (PS)** | Requisito que expressa controles de acesso, criptografia, autenticação, autorização, proteção contra ataques e gestão de identidade. É derivada de normas como OWASP, NIST e políticas internas. | Cap. 1.4.2, Cap. 7.5.16 |
| **Requisito de Conformidade/Privacidade (LGPD)** | Requisito que expressa obrigações legais e regulatórias relacionadas à proteção de dados pessoais, privacidade, retenção, expurgo e consentimento. É derivado da Lei Geral de Proteção de Dados (Lei 13.709/2018) e normativos setoriais. | Cap. 1.4.2 |
| **Classificação de Dados** | Processo de categorização de dados com base em seu nível de sensibilidade e impacto potencial em caso de violação. Níveis obrigatórios: **Público, Interno, Confidencial, Restrito (LGPD/Sensível)**. | NIST SP 800-60 / Cap. 5.4.1 |
| **Tríade CIA** | Modelo de segurança da informação: **Confidencialidade** (acesso apenas por autorizados), **Integridade** (prevenção contra alterações não autorizadas), **Disponibilidade** (garantia de acesso quando necessário). | ISO 27001 / Cap. 8.2.1 |
| **RBAC (Role-Based Access Control)** | Modelo de controle de acesso onde permissões são atribuídas a funções (roles), e usuários/atores assumem funções. O princípio de **menor privilégio** (least privilege) deve ser sempre aplicado. | Cap. 5.4.1, Cap. 9.3.2 |
| **Autenticação Multifator (MFA)** | Método de autenticação que exige dois ou mais fatores de verificação (ex: senha + token TOTP, ou senha + biometria) para acessar sistemas críticos ou dados restritos. | OWASP / NIST |
| **Criptografia em Trânsito** | Proteção de dados durante a transmissão entre sistemas, utilizando protocolos como TLS 1.3+ (Transport Layer Security) para HTTPS, gRPC, ou VPNs. | NIST / Cap. 5.6.2 (comunicação) |
| **Criptografia em Repouso** | Proteção de dados armazenados em bancos de dados, arquivos ou backups, utilizando algoritmos como AES-256 ou equivalentes. | NIST / Cap. 5.6.2 (armazenamento) |
| **Threat Modeling (Modelagem de Ameaças)** | Processo estruturado para identificar, quantificar e mitigar ameaças à segurança. O método STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) é o padrão obrigatório. | OWASP / Cap. 8.3.1 |
| **DPIA (Data Protection Impact Assessment)** | Avaliação de Impacto à Proteção de Dados, exigida pela LGPD para operações que envolvam dados sensíveis ou de alto risco. Deve identificar riscos e medidas de mitigação. | LGPD (Art. 38) / GDPR (Art. 35) |
| **Anonimização / Pseudonimização** | Técnicas de processamento de dados que removem (anonimização) ou substituem (pseudonimização) identificadores diretos, reduzindo riscos à privacidade. | LGPD (Art. 13) |
| **Trilha de Auditoria (Audit Trail)** | Registro imutável (append-only) de todas as ações significativas realizadas em um sistema, especialmente aquelas que envolvem dados restritos ou sensíveis. Deve incluir: quem, o quê, quando, onde, como. | SOX / ISO 27001 / Cap. 9.2.2 |
| **Incidente de Segurança** | Qualquer evento adverso que comprometa a confidencialidade, integridade ou disponibilidade de um sistema ou dado. Inclui acessos não autorizados, vazamentos, ransomware, negação de serviço. | NIST / ISO 27001 |
| **Vulnerabilidade** | Fraqueza em um sistema, processo ou controle que pode ser explorada por uma ameaça para causar danos. | NIST / Cap. 8.3.2 |
| **Risco** | Medida do impacto potencial de uma ameaça explorar uma vulnerabilidade, considerando a probabilidade e as consequências. Risco = Probabilidade × Impacto. | ISO 27001 / Cap. 8.2.1 |
