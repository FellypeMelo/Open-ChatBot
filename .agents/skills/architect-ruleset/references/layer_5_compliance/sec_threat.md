# Seção 7 – Regras de Modelagem de Ameaças e Vulnerabilidades (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-THREAT  
**Status:** Definitivo  
**Escopo:** Métodos de análise de riscos estruturais (STRIDE), varreduras estáticas/dinâmicas e ciclo de patch management.

---

### REGSEC-007 – Modelagem de Ameaças (STRIDE) Obrigatória para Mudanças Arquiteturais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-007 |
| **Nome** | Modelagem de Ameaças (STRIDE) Obrigatória para Mudanças Arquiteturais |
| **Descrição** | Para qualquer mudança arquitetural significativa (ex: nova API, novo fluxo de dados, nova integração com terceiros, nova camada de persistência), o agente deve exigir uma Modelagem de Ameaças utilizando o método STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege). A modelagem deve: **(1)** identificar ativos e fluxos de dados; **(2)** identificar ameaças potenciais para cada componente; **(3)** avaliar riscos; **(4)** propor controles mitigadores (os quais devem ser transformados em PSs ou LGPDs). A modelagem deve ser documentada e revisada pelo time de segurança. |
| **Objetivo** | Identificar proativamente vulnerabilidades e ameaças arquiteturais antes que elas se tornem incidentes. |
| **Motivação** | Cap. 8.3.1 (análise de impacto), Cap. 7.5.16 (deployment views para riscos), OWASP. |
| **Justificativa** | Sistemas seguros não são acidentais; eles são projetados com base em uma compreensão clara das ameaças. O STRIDE é um método padrão e eficaz para isso. |
| **Critérios de Aplicação** | Mudanças arquiteturais com impacto em dados ou fluxos. |
| **Critérios de Não Aplicação** | Mudanças de código internas sem impacto em fluxos ou dados. |
| **Pré-condições** | Diagrama de fluxo de dados (DFD) da arquitetura. |
| **Pós-condições** | Modelagem de ameaças aprovada e os controles implementados. |
| **Restrições** | O agente deve incluir a análise de ameaças à privacidade (ex: vazamento de dados sensíveis) junto com as ameaças técnicas. |
| **Dependências** | REGARCH-SW-009 (análise de impacto). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Modelagem STRIDE para a nova API de classificação: Spoofing (atacante finge ser um serviço legítimo) → mitigado com mTLS. Information Disclosure (logs contendo dados genômicos) → mitigado com sanitização de logs." |
| **Exemplo Negativo** | "Nova API implementada sem qualquer análise de ameaças." |
| **Anti-pattern** | Realizar a modelagem de ameaças apenas no papel, sem implementar os controles mitigadores. |
| **Métrica** | Percentual de mudanças arquiteturais com modelagem STRIDE (meta: 100%). |
| **Critérios de Auditoria** | Revisar projetos arquiteturais: se não houver modelagem de ameaças, falha. |

---

### REGSEC-011 – Gestão de Vulnerabilidades (Scans e Patch Management)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-011 |
| **Nome** | Gestão de Vulnerabilidades (Scans e Patch Management) |
| **Descrição** | O agente deve garantir que vulnerabilidades em código (SAST, DAST) e em infraestrutura (sistemas operacionais, bibliotecas, imagens de container) sejam identificadas e tratadas. Scans automatizados (ex: Snyk, Trivy, SonarQube, AWS Inspector) devem ser executados: **(1)** a cada build (para código e dependências); **(2)** diariamente (para infraestrutura). As vulnerabilidades devem ser classificadas por severidade (Crítica, Alta, Média, Baixa) e tratadas conforme os prazos: **Crítica**: 24h, **Alta**: 7 dias, **Média**: 30 dias, **Baixa**: 90 dias. Vulnerabilidades críticas bloqueiam o deploy. |
| **Objetivo** | Reduzir a superfície de ataque mantendo sistemas e dependências atualizados e corrigidos. |
| **Motivação** | OWASP, NIST, e práticas de DevSecOps. |
| **Justificativa** | A maioria dos ataques explora vulnerabilidades conhecidas e já corrigidas (ex: Log4Shell). |
| **Critérios de Aplicação** | Todo código e toda infraestrutura. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Scanners configurados no pipeline e na infraestrutura. |
| **Pós-condições** | Vulnerabilidades identificadas e tratadas. |
| **Restrições** | Se uma vulnerabilidade crítica não puder ser corrigida imediatamente, o agente deve recomendar a aplicação de controles compensatórios (ex: WAF). |
| **Dependências** | REGSEC-007, REGQUAL-010. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Scan identificou CVE-2024-XXXX (crítica) na biblioteca X. Pipeline bloqueado. Time atualizou para versão segura em 6h." |
| **Exemplo Negativo** | "Biblioteca X com vulnerabilidade crítica em produção há 6 meses." |
| **Anti-pattern** | Ignorar vulnerabilidades de baixa severidade, que se acumulam e permitem ataques em cadeia. |
| **Métrica** | Tempo médio de correção (MTTR) para vulnerabilidades críticas. |
| **Critérios de Auditoria** | Revisar relatório de vulnerabilidades e as datas de correção. |
