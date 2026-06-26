# Seção 6 – Regras de Rastreabilidade da Documentação (Layer 6 - Documentação e Comunicação Técnica)

**ID:** ARCH-RULESET-L6-DOC-TRACE  
**Status:** Definitivo  
**Escopo:** Métodos de vinculação bidirecional (documentos ↔ código) e integridade de versionamento no Git.

---

### REGDOC-009 – Rastreabilidade Documento ↔ Código (Backward e Forward)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-009 |
| **Nome** | Rastreabilidade Documento ↔ Código (Backward e Forward) |
| **Descrição** | O agente deve garantir que cada artefato de documentação (requisito, ADR, especificação de API) seja rastreável ao código que o implementa (forward), e que cada componente de código seja rastreável à documentação que o descreve (backward). A rastreabilidade deve ser mantida por meio de: **(1)** comentários no código com referência a IDs (ex: `// Implements RN-042`); **(2)** metadados em documentos com referência a módulos ou pacotes; **(3)** ferramentas de integração (ex: Jira + GitHub). |
| **Objetivo** | Garantir que a documentação não seja um artefato isolado, mas esteja integrada ao ciclo de vida do desenvolvimento. |
| **Motivação** | Cap. 8.3.1 (rastreabilidade estática), Cap. 9.2.2 (três mundos). |
| **Justificativa** | Documentação sem rastreabilidade ao código é facilmente ignorada ou desatualizada. |
| **Critérios de Aplicação** | Requisitos, ADRs, especificações de API, READMEs. |
| **Critérios de Não Aplicação** | Documentação de usuário final (ex: manuais). |
| **Pré-condições** | IDs únicos atribuídos a requisitos e ADRs. |
| **Pós-condições** | Cada elemento de código tem referência à sua documentação; cada documento tem referência ao código. |
| **Restrições** | A rastreabilidade deve ser verificada automaticamente no CI (ex: script que verifica se cada RN tem um teste associado). |
| **Dependências** | REGREQ-011, REGDOC-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "No código: `// ADR-012: implementação da estratégia de persistência`. No ADR: `Implementado no módulo persistence`." |
| **Exemplo Negativo** | "Documentação arquivada em uma pasta, código em outra, sem referências cruzadas." |
| **Anti-pattern** | Usar comentários genéricos como `// TODO: link para documentação`. |
| **Métrica** | Percentual de código com referência à documentação (meta: 100% para código crítico). |
| **Critérios de Auditoria** | Revisar amostra de código: se um componente crítico não tiver referência à documentação, falha. |

---

### REGDOC-010 – Versionamento e Histórico de Documentação

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-010 |
| **Nome** | Versionamento e Histórico de Documentação |
| **Descrição** | O agente deve garantir que toda documentação seja versionada no mesmo sistema de controle de versão do código (ex: Git). Cada alteração significativa deve ser acompanhada por um commit com mensagem descritiva, referenciando a mudança (ex: issue, ADR). O histórico de alterações deve estar acessível para auditoria. |
| **Objetivo** | Garantir rastreabilidade de mudanças na documentação e permitir rollback se necessário. |
| **Motivação** | Cap. 1.3 (ciclo de vida da descrição arquitetural), Cap. 9.2.3 (ciclo de vida de sistemas). |
| **Justificativa** | Documentação não versionada é confiável? Não. Sem histórico, não se sabe por que uma decisão foi tomada ou quando foi alterada. |
| **Critérios de Aplicação** | Toda documentação técnica (requisitos, arquitetura, APIs, READMEs). |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Repositório Git configurado. |
| **Pós-condições** | Documento versionado com histórico de alterações. |
| **Restrições** | O commit deve referenciar o artefato correspondente (ex: issue, ADR). |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Commit: `docs: atualiza ADR-012 para refletir migração para CockroachDB (refs #456)`." |
| **Exemplo Negativo** | "Documento enviado por e-mail, sem controle de versão." |
| **Anti-pattern** | Versionar documentos em arquivos .docx ou PDF, que não permitem diff legível. |
| **Métrica** | Percentual de documentos com histórico de versão. |
| **Critérios de Auditoria** | Revisar se cada documento está no repositório com histórico. |
