# Component Diagram Rules (COMP-1–COMP-10)

## COMP-1 – Component Element
- Rectangle with `<<component>>`.

```plantuml
component "PedidoModule" <<component>>
```

## COMP-2 – Interfaces
- Provided: `()--`. Required: `)--` (ball-and-socket notation).

```plantuml
interface "IPagamento" as IPagamento
PedidoModule ()-- IPagamento
PagamentoModule --() IPagamento
```

## COMP-3 – Ports
- Use when a component encapsulates multiple interfaces.

## COMP-4 – Dependencies
- Dashed arrows: `..>`.

```plantuml
PedidoModule ..> IPagamento
```

## COMP-5 – Use Case Realization
- Map explicitly with `<<realizes>>`.

```plantuml
component "PedidoModule" <<component>> {
  note : {realizes: UC-05, UC-06}
}
```

## COMP-6 – Independent Deployment Unit
- The component must be independently packageable and versionable.

## COMP-7 – Interfaces with Signatures
- Specify method signatures.

```plantuml
interface IPagamento {
  + processar(valor: Double) : Boolean
}
```

## COMP-8 – Class-to-Component Traceability
- Every component must map to internal classes.

## COMP-9 – Non-Functional Requirement Traceability
- Example: `{req: RNF-03 (performance)}`.

## COMP-10 – Reflects Real Architecture
- The diagram must mirror the actual code architecture.

---

## ✅ Complete Example

```plantuml
@startuml
title Diagrama de Componentes – Sistema de E-commerce
header Versão 1.0 | Autor: Agente IA | {req: RF-001 a RF-050}

package "Camada de Apresentação" {
  component "WebModule" <<component>> {
    note : {realizes: UC-01, UC-02, UC-03, UC-04, UC-05}
  }
}

package "Camada de Serviços" {
  component "PedidoModule" <<component>> {
    note : {realizes: UC-05, UC-06}\n{req: RNF-03 (performance)}
  }
  component "PagamentoModule" <<component>> {
    note : {realizes: UC-07}
  }
}

package "Camada de Infraestrutura" {
  component "EstoqueModule" <<component>>
  component "NotificacaoModule" <<component>>
}

interface "IPedido" as IPedido
interface "IPagamento" as IPagamento
interface "IEstoque" as IEstoque
interface "INotificacao" as INotificacao

WebModule ()-- IPedido
PedidoModule ()-- IPedido
PedidoModule ()-- IPagamento
PagamentoModule ()-- IPagamento
PedidoModule ..> IEstoque : usa
EstoqueModule ()-- IEstoque
PedidoModule ..> INotificacao : usa
NotificacaoModule ()-- INotificacao
@enduml
```
