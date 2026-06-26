# Seção 8 – Auditoria, Exemplo Integrado e Evolução / Layer 3 (Layer 3 - Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-AUDIT-EXAMPLE  
**Status:** Definitivo  
**Escopo:** Métodos de validação de auditoria, caso de uso de aplicação prática e evolução.

---

## 1. Critérios de Auditoria da Arquitetura de Software

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-SW-01 | Todo componente tem serviço especificado antes da implementação (REGARCH-SW-001). | Revisar histórico de commits: especificação de API antes do código. |
| AUD-SW-02 | Grafo de dependências é acíclico (REGARCH-SW-003). | Análise estática com ferramentas (ex: ArchUnit, JDepend). |
| AUD-SW-03 | Estrutura de camadas respeita Clean/Hexagonal (REGARCH-SW-004). | Verificar imports entre camadas (domínio não importa infra). |
| AUD-SW-04 | Bounded Contexts definidos para sistemas com > 3 módulos (REGARCH-SW-005). | Revisar documentação de arquitetura. |
| AUD-SW-05 | Todo contrato de API está especificado em OpenAPI ou Proto (REGARCH-SW-006). | Verificar existência de arquivos de contrato. |
| AUD-SW-06 | Nenhuma cadeia de chamadas síncronas com profundidade > 3 (REGARCH-SW-007). | Análise de tracing distribuído. |
| AUD-SW-07 | Análise de impacto documentada para mudanças estruturais (REGARCH-SW-009). | Revisar processo de controle de mudanças. |
| AUD-SW-08 | Nenhum acesso direto a dados de outro módulo (REGARCH-SW-010). | Verificar conexões de banco e queries cruzadas. |
| AUD-SW-09 | Artefatos físicos mapeados para componentes lógicos (REGARCH-SW-011). | Verificar matriz de rastreabilidade física. |
| AUD-SW-10 | Versionamento semântico para todos os artefatos (REGARCH-SW-012). | Revisar tags de releases e containers. |
| AUD-SW-11 | Módulos alinhados com estrutura organizacional (REGARCH-SW-013). | Verificar squads proprietários de repositórios. |

---

## 2. Exemplo Integrado de Aplicação do Módulo 04

**Cenário:** O agente recebe os requisitos `RN-010` (processar FASTQ) e `RN-042` (classificar variantes ACMG) e deve desenhar a estrutura de software.

**Raciocínio Aplicado Passo a Passo:**
1. **REGARCH-SW-001 (Service-First):** Criação das portas abstratas:
   * `IngestionService` (recebe arquivo físico e emite evento).
   * `ClassificationService` (recebe variante e aplica lógica ACMG puramente em memória).
2. **REGARCH-SW-005 (Bounded Contexts):** Delimita-se o contexto de `Ingestão` (genômica primária) e o contexto de `Laudos` (relatórios finais de pacientes). Comunicação via eventos desacoplados.
3. **REGARCH-SW-002 (Dependency Inversion):** O domínio do classificador define a interface `ACMGClassifierRuleSet`. O adaptador na camada de infraestrutura implementa com uma engine baseada em pysam/estatísticas.
4. **REGARCH-SW-007 (Chatty Calls):** Em vez do `IngestionService` bloquear aguardando a classificação em cascata, ele publica o evento assíncrono `FASTQUploadedEvent` e termina a requisição.
5. **REGARCH-SW-011 (Rastreabilidade Física):** Mapeado: `ClassificationService` (lógico) → `classification-worker:1.2.0` (Docker image) → `docker-compose.yml` (Físico).
6. **REGARCH-SW-013 (Lei de Conway):** Squad "Genomics Processing" é dono exclusivo do contexto `Ingestão`. Squad "Clinical Decision Support" é dono do contexto `Laudos`.

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido com submódulos focados em:
* **Módulo 04-A (Modular Monoliths):** Diretrizes para migração gradual e estruturação de monólitos modulares.
* **Módulo 04-B (Data Architecture):** Modelagem física de banco de dados, particionamento e réplicas analíticas.
* **Módulo 04-C (Event Streams):** Governança de barramento de eventos (Apache Kafka, RabbitMQ) e políticas de retry de fila.
* **Módulo 04-D (Resiliency Patterns):** Implementação de Circuit Breaker, Timeout, Bulkhead e Retry com Backoff Exponencial.
