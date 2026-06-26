# Seção 3 – Regras de Estrutura de Artefatos (Layer 6 - Documentação e Comunicação Técnica)

**ID:** ARCH-RULESET-L6-DOC-STRUCT  
**Status:** Definitivo  
**Escopo:** Diretrizes estruturais para documentos de arquitetura, decisões (ADR) e READMEs de repositório.

---

### REGDOC-001 – Estrutura Obrigatória para Documentação de Arquitetura (ARC42)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-001 |
| **Nome** | Estrutura Obrigatória para Documentação de Arquitetura (ARC42) |
| **Descrição** | O agente deve garantir que todo documento de arquitetura de solução siga a estrutura ARC42 (ou equivalente formal), contendo, no mínimo, as seguintes seções: **(1) Introdução e Metas**: propósito, escopo, stakeholders, metas; **(2) Restrições**: técnicas, organizacionais, regulatórias (RTs, PSs, LGPDs); **(3) Contexto**: diagrama de contexto, interfaces com sistemas externos; **(4) Estratégia de Solução**: visão geral da arquitetura, estilos e padrões adotados (Clean, DDD, SOA); **(5) Visão de Construção**: decomposição em módulos, componentes, pacotes; **(6) Visão de Execução**: comportamento em tempo de execução, fluxos, interações; **(7) Visões Transversais**: segurança, performance, deploy, data; **(8) Design e Decisões**: ADRs (REGDOC-002); **(9) Qualidade**: RTs de qualidade e como são atendidos; **(10) Riscos e Dívida Técnica**: riscos identificados e plano de mitigação. |
| **Objetivo** | Padronizar a documentação arquitetural, garantindo cobertura completa e facilitando a leitura por diferentes stakeholders. |
| **Motivação** | ARC42 é o padrão de fato para documentação de arquitetura, sendo recomendado pela indústria e pela academia. Cap. 7 (Viewpoints) complementa. |
| **Justificativa** | Sem uma estrutura padrão, cada arquiteto documenta de forma diferente, gerando confusão e dificultando a reutilização. |
| **Critérios de Aplicação** | Todo novo projeto ou módulo significativo. Projetos existentes devem ser migrados para ARC42 em até 90 dias. |
| **Critérios de Não Aplicação** | Documentação de APIs (OpenAPI) ou de código (READMEs), que seguem estruturas específicas. |
| **Pré-condições** | Template ARC42 disponível no repositório. |
| **Pós-condições** | Documento de arquitetura em conformidade com ARC42. |
| **Restrições** | Seções podem ser adaptadas, mas as 10 seções obrigatórias devem estar presentes. |
| **Dependências** | REGDOC-002 (ADRs), REGREQ-004 (requisitos). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Documento de arquitetura do `genomics-classifier` seguindo ARC42: 10 seções, cada uma preenchida com conteúdo relevante." |
| **Exemplo Negativo** | "Documento de arquitetura em formato livre, sem estrutura definida." |
| **Anti-pattern** | Preencher todas as seções com texto genérico ("a ser definido") apenas para cumprir o template. |
| **Métrica** | Percentual de projetos com documentação ARC42 (meta: 100%). |
| **Critérios de Auditoria** | Revisar a documentação de cada projeto: se não tiver ARC42, falha. |

---

### REGDOC-002 – Obrigação de Registrar Decisões Arquiteturais (ADRs)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-002 |
| **Nome** | Obrigação de Registrar Decisões Arquiteturais (ADRs) |
| **Descrição** | O agente deve garantir que toda decisão arquitetural significativa (ex: escolha de tecnologia, padrão de integração, estratégia de persistência, modelo de dados, política de segurança) seja registrada em um Architecture Decision Record (ADR). O ADR deve conter: **(1)** Título e identificador único; **(2)** Contexto (problema, restrições, premissas); **(3)** Decisão (o que foi decidido); **(4)** Rationale (por que essa decisão foi tomada, incluindo alternativas rejeitadas – REGCON-009); **(5)** Consequências (impactos positivos e negativos); **(6)** Status (proposto, aceito, depreciado, supersedido); **(7)** Data e autor; **(8)** Stakeholders envolvidos e nível de comprometimento (aware, agree, commit). Os ADRs devem ser versionados no mesmo repositório que o código. |
| **Objetivo** | Preservar o conhecimento do processo decisório, permitindo que futuros arquitetos entendam o contexto e as razões das decisões. |
| **Motivação** | Cap. 6.2.3 (documentação de ações) e Cap. 7.4.6 (rationale para comprometimento). |
| **Justificativa** | Decisões sem registro são esquecidas, repetidas ou contestadas. ADRs são a memória institucional da arquitetura. |
| **Critérios de Aplicação** | Toda decisão com impacto arquitetural (conforme REGARCH-SW-009). |
| **Critérios de Não Aplicação** | Decisões de implementação triviais (ex: qual biblioteca de logging usar, decisão já padronizada). |
| **Pré-condições** | Template de ADR disponível. |
| **Pós-condições** | ADR registrado e revisado. |
| **Restrições** | ADRs devem ser revisados por pares antes de serem aceitos. |
| **Dependências** | REGCON-009, REGARCH-SW-009. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "ADR-012: Uso de PostgreSQL vs. MongoDB para dados genômicos. Contexto: dados relacionais e transacionais. Decisão: PostgreSQL. Rationale: ACID e maturidade. Consequências: necessidade de particionamento. Alternativas rejeitadas: MongoDB (falta ACID). Status: Aceito." |
| **Exemplo Negativo** | "Decidimos usar PostgreSQL." (sem ADR). |
| **Anti-pattern** | Escrever ADRs longos demais que ninguém lê; ou tão vagos que não ajudam em nada. |
| **Métrica** | Número de decisões com ADR vs. total de decisões arquiteturais. |
| **Critérios de Auditoria** | Revisar se há um ADR para cada mudança significativa registrada no repositório. |

---

### REGDOC-003 – README Obrigatório e Estruturado para Todo Projeto/Módulo

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGDOC-003 |
| **Nome** | README Obrigatório e Estruturado para Todo Projeto/Módulo |
| **Descrição** | O agente deve garantir que todo projeto, módulo ou serviço possua um arquivo `README.md` no diretório raiz, contendo, no mínimo: **(1)** Nome e propósito (visão geral); **(2)** Instalação (pré-requisitos, dependências); **(3)** Configuração (variáveis de ambiente, arquivos de configuração); **(4)** Uso básico (exemplos de comandos ou chamadas de API); **(5)** Documentação adicional (links para arquitetura, ADRs, guias); **(6)** Testes (como executar); **(7)** Contribuição (como contribuir); **(8)** Licença e contato. |
| **Objetivo** | Garantir que qualquer desenvolvedor (novato ou experiente) possa entender rapidamente o que é o projeto, como instalá-lo e como usá-lo. |
| **Motivação** | Cap. 6.4 (usabilidade de modelos) e práticas de desenvolvimento de código aberto. |
| **Justificativa** | O README é a primeira impressão do projeto. Sem ele, os desenvolvedores perdem tempo procurando informações básicas. |
| **Critérios de Aplicação** | Todo repositório de código (projeto, módulo, serviço). |
| **Critérios de Não Aplicação** | Projetos internos que já possuem documentação centralizada (ex: portal de desenvolvedor), mas mesmo assim devem ter um README mínimo com links. |
| **Pré-condições** | Template de README disponível. |
| **Pós-condições** | README preenchido e atualizado a cada mudança significativa. |
| **Restrições** | O README não deve conter detalhes de implementação internos; deve ser orientado ao usuário do módulo. |
| **Dependências** | Nenhuma. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "README.md do `variant-classifier` com todas as 8 seções preenchidas, incluindo exemplos de uso da API." |
| **Exemplo Negativo** | "Repositório sem README ou com README vazio." |
| **Anti-pattern** | README desatualizado, com informações de instalação que não funcionam mais. |
| **Métrica** | Percentual de repositórios com README estruturado (meta: 100%). |
| **Critérios de Auditoria** | Revisar cada repositório: se não tiver README, falha. |
