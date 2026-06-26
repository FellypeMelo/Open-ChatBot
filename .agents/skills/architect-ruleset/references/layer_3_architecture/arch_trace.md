# Seção 6 – Regras de Rastreabilidade Física / Layer 3 (Layer 3 - Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-TRACE  
**Status:** Definitivo  
**Escopo:** Regras para mapeamento de componentes lógicos a artefatos físicos e versionamento semântico.

---

### REGARCH-SW-011 – Mapeamento Obrigatório para Artefatos Físicos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-011 |
| **Nome** | Mapeamento Obrigatório para Artefatos Físicos (Mundo Simbólico → Mundo Físico) |
| **Descrição** | Todo componente lógico (ex: módulo, serviço, data object) deve ser mapeado a um ou mais artefatos físicos (ex: arquivo JAR, container Docker, imagem AMI, tabela de banco, tópico Kafka, arquivo de configuração). Esse mapeamento deve ser documentado na matriz de rastreabilidade e validado no pipeline de deployment. |
| **Objetivo** | Garantir que a arquitetura seja completamente rastreável até o nível de infraestrutura, permitindo análise de impacto operacional e diagnóstico de incidentes (ex: "este serviço falhou, qual requisição de negócio ele afeta?"). |
| **Motivação** | Cap. 9.2.2 – três mundos: Social (requisitos), Simbólico (software), Físico (hardware/artefatos). |
| **Justificativa** | Sem rastreabilidade física, não é possível correlacionar incidentes de infraestrutura com requisitos de negócio, e auditorias de compliance (ex: LGPD) são inviáveis. |
| **Critérios de Aplicação** | Todo componente de software. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Componente lógico definido. |
| **Pós-condições** | Artefato físico associado ao componente. |
| **Restrições** | O artefato deve ter um identificador único (ex: SHA do container, versão do JAR). |
| **Dependências** | REGREQ-011. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Serviço `VariantClassifier` (lógico) → imagem Docker `variant-classifier:1.2.3` → implantado no cluster Kubernetes `genomics-prod`." |
| **Exemplo Negativo** | "Serviço `VariantClassifier` está em produção, mas não sei onde." |
| **Anti-pattern** | Mapear apenas o nome do serviço, sem versão ou local. |
| **Métrica** | Percentual de componentes com artefato físico mapeado (meta: 100%). |
| **Critérios de Auditoria** | Verificar se cada serviço no repositório de código tem um `Dockerfile` ou equivalente, e se sua imagem está registrada. |

---

### REGARCH-SW-012 – Obrigação de Versionamento Semântico para Artefatos e Contratos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-012 |
| **Nome** | Obrigação de Versionamento Semântico para Artefatos e Contratos |
| **Descrição** | Todo artefato (JAR, container) e todo contrato (API, evento) deve ser versionado seguindo o Semantic Versioning (MAJOR.MINOR.PATCH): **(1)** MAJOR: mudanças incompatíveis no contrato (breaking changes); **(2)** MINOR: adição de funcionalidade compatível com versões anteriores; **(3)** PATCH: correções de bug e melhorias internas que não afetam o contrato. |
| **Objetivo** | Permitir evolução controlada e previsível, sem quebrar consumidores. |
| **Motivação** | Cap. 1.3 (arquitetura acomoda mudanças), Cap. 9.2.3 (ciclo de vida e versões). |
| **Justificativa** | Sem versionamento semântico, não há como saber se uma atualização é segura ou quebrará o sistema. |
| **Critérios de Aplicação** | Todo artefato de software, toda API pública e todo evento de domínio. |
| **Critérios de Não Aplicação** | Artefatos internos (ex: bibliotecas de teste). |
| **Pré-condições** | Contrato ou artefato definido. |
| **Pós-condições** | Versionamento no `pom.xml`, `Dockerfile`, ou arquivo de contrato. |
| **Restrições** | O agente deve detectar breaking changes (ex: remoção de campo, mudança de tipo) e automaticamente recomendar um incremento de MAJOR. |
| **Dependências** | REGARCH-SW-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "API `v1.2.0` adiciona novo campo opcional. `v2.0.0` remove um campo obrigatório – breaking change." |
| **Exemplo Negativo** | "Todos os containers têm tag `latest`." |
| **Anti-pattern** | Mudar o comportamento da API sem mudar a versão. |
| **Métrica** | Percentual de artefatos com versionamento semântico (meta: 100%). |
| **Critérios de Auditoria** | Revisar tags de containers e versionamento de APIs. |
