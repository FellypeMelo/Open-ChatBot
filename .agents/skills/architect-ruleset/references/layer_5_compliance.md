# Layer 5 – Compliance, Segurança e Privacidade (Índice de Módulo)

**ID do Módulo:** ARCH-RULESET-MOD-06  
**Versão:** 1.0  
**Status:** Definitivo  
**Camada:** Layer 5 – Compliance & Security Rules  
**Dependências:** Módulo 01 (Constituição), Módulo 02 (Core & Reasoning), Módulo 03 (Requisitos), Módulo 04 (Arquitetura de Software), Módulo 05 (Qualidade) – obrigatórios  
**Autoridade:** Subordinado às Layers 0, 1, 2, 3, 4. Nenhuma regra deste módulo pode violar os princípios constitucionais, o motor de raciocínio, os requisitos aprovados, as decisões arquiteturais ou os critérios de qualidade. **Este módulo possui status de "Supervisão Crítica"** – violações de segurança ou privacidade podem anular decisões de camadas inferiores em caso de conflito.  
**Escopo:** Define o conjunto completo de regras para segurança da informação, privacidade de dados (LGPD/GDPR) e gestão de riscos. Abrange desde a classificação de dados, controle de acesso (IAM/RBAC), criptografia, modelagem de ameaças (STRIDE), prevenção de vulnerabilidades (OWASP/NIST), até políticas de retenção, expurgo, consentimento, avaliação de impacto (DPIA) e auditoria contínua.

---

## Estrutura do Módulo

Este módulo estabelece o **Mecanismo de Segurança e Privacidade** do agente de IA. Ele está dividido nas seguintes seções granulares e auto-contidas:

1. **[Glossário Formal](./layer_5_compliance/glossary.md)**  
   *Definições obrigatórias e referências (NIST, OWASP, LGPD) para políticas de segurança, tráfego criptografado, STRIDE, DPIA e trilhas de auditoria.*

2. **[Princípios Fundamentais de Segurança e Privacidade](./layer_5_compliance/principles.md)**  
   *Princípios orientadores, como Privacy by Design (PbD), Defesa em Profundidade, Menor Privilégio, Confiança Zero e Auditoria Imutável.*

3. **[Regras de Classificação e Inventário de Dados (SEC-CLASS)](./layer_5_compliance/sec_class.md)**  
   *Regras (REGSEC-001 a REGSEC-002) para a classificação de dados em 4 níveis (Público, Interno, Confidencial, Restrito) e o Inventário de Ativos de Informação.*

4. **[Regras de Controle de Acesso e IAM (SEC-ACCESS)](./layer_5_compliance/sec_access.md)**  
   *Regras (REGSEC-003 a REGSEC-004) exigindo controle RBAC com princípio de menor privilégio e MFA obrigatório para acessos a dados restritos e confidenciais.*

5. **[Regras de Criptografia e Proteção de Dados (SEC-CRYPTO)](./layer_5_compliance/sec_crypto.md)**  
   *Regras (REGSEC-005 a REGSEC-006) regulando o uso imperativo de TLS 1.3+ para tráfego e cifragem AES-256 em repouso com chaves centralizadas (KMS/Vault).*

6. **[Regras de Privacidade e LGPD (SEC-PRIV)](./layer_5_compliance/lgpd_rules.md)**  
   *Diretrizes de conformidade (REGLGPD-001 a REGLGPD-004) regulando consentimento informado, atendimento aos direitos do titular, expurgo/anonimização automática e DPIA.*

7. **[Regras de Modelagem de Ameaças e Vulnerabilidades (SEC-THREAT)](./layer_5_compliance/sec_threat.md)**  
   *Regras (REGSEC-007 e REGSEC-011) exigindo modelagem STRIDE para mudanças arquiteturais e gestão dinâmica de patches/scans automáticos no CI.*

8. **[Regras de Auditoria, Logs e Monitoramento (SEC-AUDIT)](./layer_5_compliance/sec_audit.md)**  
   *Regras (REGSEC-008 a REGSEC-009) sobre trilhas de auditoria imutáveis (append-only/WORM) e alertas contínuos do SIEM contra acessos anômalos.*

9. **[Regras de Gestão de Incidentes (SEC-IR)](./layer_5_compliance/sec_ir.md)**  
   *Regras (REGSEC-010) definindo o plano de resposta e contenção de incidentes com prazo de notificação de 48h à ANPD.*

10. **[Auditoria, Exemplo Prático e Evolução](./layer_5_compliance/audit.md)**  
    *Tabela de auditoria para a Layer 5, exemplo prático de modelagem de ameaças e tratamento LGPD no processamento de VCF, e extensões para HIPAA/ANVISA.*
