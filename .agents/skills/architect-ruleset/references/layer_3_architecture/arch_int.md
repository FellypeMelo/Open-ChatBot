# Seção 4 – Regras de Integração e Interoperabilidade / Layer 3 (Layer 3 - Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-INT  
**Status:** Definitivo  
**Escopo:** Regras para publicação de APIs, resiliência na comunicação e padrões de mensageria assíncrona.

---

### REGARCH-SW-006 – Especificação Obrigatória de Contratos (OpenAPI/Protocol Buffers)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-006 |
| **Nome** | Especificação Obrigatória de Contratos (OpenAPI/Protocol Buffers) |
| **Descrição** | Todo serviço exposto (síncrono ou assíncrono) deve ter sua interface especificada em um formato de contrato padronizado e legível por máquina: **(1)** Para APIs REST: OpenAPI 3.0+ (YAML/JSON); **(2)** Para gRPC: Protocol Buffers (.proto); **(3)** Para mensagens assíncronas (filas, eventos): Schema Registry (ex: Avro, JSON Schema) ou, no mínimo, um documento formal com todos os campos, tipos e regras de validação. |
| **Objetivo** | Garantir que a comunicação entre serviços seja inequívoca, versionada e passível de validação automatizada (ex: testes de contrato). |
| **Motivação** | Cap. 10.4.5 (formatos de troca XMI/XML com meta-linguagem) e Cap. 5.3 (interface como local de acesso). |
| **Justificativa** | Contratos informais (ex: "documentação no Confluence") são a fonte número 1 de incompatibilidades entre serviços. Contratos legíveis por máquina permitem validação, geração de código e testes automatizados. |
| **Critérios de Aplicação** | Toda interface pública entre serviços, microsserviços, ou módulos que se comuniquem via rede. |
| **Critérios de Não Aplicação** | Interfaces internas dentro do mesmo processo (ex: objetos Java) podem ser especificadas por interfaces de código (ex: Java Interface). |
| **Pré-condições** | Serviço definido (REGARCH-SW-001). |
| **Pós-condições** | Contrato versionado no repositório de código. |
| **Restrições** | Qualquer mudança no contrato deve ser versionada (ex: `/v2/classify`) e não quebrar versões anteriores sem depreciação. |
| **Dependências** | REGARCH-SW-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Arquivo `classifier-api.yaml` com OpenAPI 3.0, descrevendo endpoint `POST /v1/classify`, payload `VariantRequest`, resposta `ClassificationResponse`, códigos de erro 400, 404, 500." |
| **Exemplo Negativo** | "Endpoint `POST /classify` documentado apenas em texto livre no e-mail." |
| **Anti-pattern** | Especificar o contrato após a implementação ou não especificar contratos de erro. |
| **Métrica** | Percentual de serviços com contrato especificado (meta: 100%). |
| **Critérios de Auditoria** | Verificar se cada serviço exposto possui um arquivo de contrato atualizado. |

---

### REGARCH-SW-007 – Proibição de Chamadas Síncronas em Cadeia (Chatty Calls)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-007 |
| **Nome** | Proibição de Chamadas Síncronas em Cadeia (Chatty Calls) |
| **Descrição** | O agente deve proibir e detectar arquiteturas onde um serviço, para atender a uma única requisição, realiza múltiplas chamadas síncronas em cadeia para outros serviços (ex: Service A → Service B → Service C → Service D), especialmente se essas chamadas forem sequenciais e não paralelizáveis. Isso gera alta latência, falha em cascata e baixa resiliência. O agente deve recomendar: (1) agregação no cliente, (2) processamento assíncrono com eventos, (3) caching, ou (4) remodelação do serviço para ser mais coeso. |
| **Objetivo** | Garantir alta performance, resiliência e baixa latência. |
| **Motivação** | Cap. 8.2.3 (carga se propaga de cima para baixo – cascata) e Cap. 8.2.4 (acúmulo de tempos de resposta). |
| **Justificativa** | Cadeias síncronas são o principal gargalo de performance e o calcanhar de Aquiles da resiliência (falha de um serviço derruba todos os anteriores). |
| **Critérios de Aplicação** | Projetos de integração entre serviços. |
| **Critérios de Não Aplicação** | Pipelines internos de processamento de dados (batch). |
| **Pré-condições** | Dependências entre serviços mapeadas. |
| **Pós-condições** | Nenhum caminho síncrono com profundidade > 3. |
| **Restrições** | Se uma cadeia for inevitável, o agente deve impor circuit breakers, timeouts e retries com backoff. |
| **Dependências** | REGARCH-SW-006. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Service A recebe requisição, consulta dados em B (síncrono), e publica evento para C (assíncrono). C não bloqueia A." |
| **Exemplo Negativo** | "Service A chama B, B chama C, C chama D, todos síncronos, retornando para A." |
| **Anti-pattern** | "Orquestração centralizada" com um orquestrador síncrono que chama todos os microsserviços. |
| **Métrica** | Profundidade média da árvore de chamadas síncronas. |
| **Critérios de Auditoria** | Revisar tracing distribuído para detectar cadeias profundas. |

---

### REGARCH-SW-008 – Uso Obrigatório de Eventos de Domínio para Desacoplamento

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-008 |
| **Nome** | Uso Obrigatório de Eventos de Domínio para Desacoplamento |
| **Descrição** | Quando um Bounded Context precisa notificar outros sobre uma mudança de estado (ex: "variante classificada", "laudo aprovado"), o agente deve recomendar o uso de Eventos de Domínio publicados em um barramento de eventos (ex: Kafka, RabbitMQ, SNS/SQS) em vez de chamadas síncronas. Os eventos devem ser imutáveis, versionados e conter apenas os dados essenciais para os consumidores. |
| **Objetivo** | Promover comunicação assíncrona, reduzindo acoplamento temporal e aumentando resiliência. |
| **Motivação** | Cap. 5.4.2 (business events), Cap. 5.7 (triggering como relação temporal). |
| **Justificativa** | Eventos permitem que serviços evoluam independentemente, sem coordenação rígida. |
| **Critérios de Aplicação** | Comunicação entre Bounded Contexts ou entre módulos independentes. |
| **Critérios de Não Aplicação** | Comunicação dentro do mesmo Bounded Context (pode ser síncrona, se necessário). |
| **Pré-condições** | Bounded Contexts definidos (REGARCH-SW-005). |
| **Pós-condições** | Eventos publicados para transições de estado relevantes. |
| **Restrições** | Eventos devem ser projetados para serem idempotentes (consumidores podem receber duplicados). |
| **Dependências** | REGARCH-SW-005, REGARCH-SW-007. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Contexto Genômica publica o evento `VariantClassifiedEvent { variantId, classification, timestamp }`. Contexto Laudos consome este evento para gerar o laudo." |
| **Exemplo Negativo** | "Contexto Genômica chama síncronamente o serviço de Laudos para gerar o relatório após classificar." |
| **Anti-pattern** | Usar eventos para tudo, mesmo para requisições que exigem resposta síncrona (ex: consulta de saldo). |
| **Métrica** | Percentual de interações cross-context usando eventos vs. síncrono. |
| **Critérios de Auditoria** | Revisar diagramas de sequência para identificar chamadas síncronas entre contextos que poderiam ser eventos. |
