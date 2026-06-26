# Deployment Diagram Rules (DP1–DP10)

## DP1 – Node Elements
- 3D box for hardware: `node "Servidor" as Servidor`.
- Execution environment: `node "JVM" <<executionEnvironment>>`.

## DP2 – Artifact
- `artifact "pedido-api.jar" as Artifact`.

## DP3 – Connections with Protocol
- `Servidor --> Banco : <<JDBC>>`.

## DP4 – Deploy Relationships
- `artifact ..> node : <<deploy>>`.

## DP5 – Faithful to Real Infrastructure
- Represent load balancers, clusters, firewalls accurately.

## DP6 – Hardware Properties
- Annotate nodes with `{cpu: 4, ram: 16GB}`.

## DP7 – Communication Constraints
- Annotate connections: `{latencia: < 10ms, banda: 100Mbps}`.

## DP8 – Component-to-Artifact Traceability
- Every artifact must correspond to a component from the component diagram.

## DP9 – Node Justification
- Link nodes to non-functional requirements.

## DP10 – Separate Environments
- Development, test, and production in separate diagrams.

---

## ✅ Complete Example

```plantuml
@startuml
title Diagrama de Implantação – Sistema de E-commerce (Produção)
header Versão 1.0 | Autor: Agente IA | {req: RNF-01, RNF-02, RNF-03}

node "Servidor Web (Nginx)" <<loadBalancer>> {
  node "Cluster de Aplicação" <<cluster>> {
    node "Pod 1" <<container>> {
      artifact "pedido-api.jar" as API1
    }
    node "Pod 2" <<container>> {
      artifact "pedido-api.jar" as API2
    }
    node "Pod 3" <<container>> {
      artifact "pagamento-api.jar" as API3
    }
  }
}

node "Banco de Dados" as Database {
  artifact "postgres:15" as Postgres
  note right : {cpu: 8, ram: 32GB}
}

node "Serviço Externo (Gateway)" as Gateway

API1 --> Database : <<JDBC>> {latencia: < 5ms}
API2 --> Database : <<JDBC>> {latencia: < 5ms}
API1 --> Gateway : <<HTTPS>> {timeout: 5s}
API2 --> Gateway : <<HTTPS>> {timeout: 5s}

note top of API1 : {realiza: COMP-01, COMP-02}
note top of API3 : {realiza: COMP-03}
@enduml
```
