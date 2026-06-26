# PlantUML Syntax Reference, Skinparam & Glossary

## Recommended Skinparam Configuration

```plantuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

skinparam usecase {
  BackgroundColor #E1F5FE
  BorderColor #01579B
}
skinparam sequence {
  ArrowColor #000000
  LifeLineBorderColor #01579B
  LifeLineBackgroundColor #E1F5FE
}
skinparam class {
  BackgroundColor #FFF3E0
  BorderColor #E65100
}
skinparam component {
  BackgroundColor #F3E5F5
  BorderColor #4A148C
}
skinparam state {
  BackgroundColor #E8F5E9
  BorderColor #1B5E20
}
skinparam activity {
  BackgroundColor #FFF9C4
  BorderColor #F57F17
}
skinparam node {
  BackgroundColor #FCE4EC
  BorderColor #880E4F
}
```

---

## Architectural Stereotypes Reference

```
<<interface>>       <<abstract>>        <<component>>
<<system>>          <<entity>>          <<service>>
<<repository>>      <<controller>>      <<create>>
<<destroy>>         <<signal>>          <<include>>
<<extend>>          <<deploy>>          <<businessEvent>>
<<loadBalancer>>    <<cluster>>         <<container>>
<<executionEnvironment>>
```

---

## Sequence Diagram Fragments

```plantuml
alt opção1
  ' actions
else opção2
  ' actions
end

loop (1..n) condição
  ' actions
end

opt opcional
  ' actions
end

par em paralelo
  ' branch 1
and
  ' branch 2
end

break interrupção
  ' actions
end

ref over Participante1, Participante2
  Referência a outro diagrama
end
```

---

## Relationship Symbols Quick Reference

| UML Concept | PlantUML | Direction |
|-------------|---------|-----------|
| Association | `A -- B` | Undirected |
| Directed Association | `A --> B` | A → B |
| Aggregation | `A o-- B` | hollow diamond on A |
| Composition | `A *-- B` | filled diamond on A |
| Inheritance | `A --|> B` | A extends B |
| Realization | `A ..|> B` | A implements B |
| Dependency | `A ..> B` | A uses B |
| Include (UC) | `A --> B : <<include>>` | |
| Extend (UC) | `A ..> B : <<extend>>` | |

---

## Naming Conventions Table

| Element | Convention | Example |
|---------|-----------|---------|
| Use Case | Infinitive + Object | `Emitir Boleto` |
| Actor | Role or system name | `Cliente`, `Sistema de Pagamento` |
| Class | Singular noun | `Pedido`, `Cliente` |
| Attribute | Lowercase noun | `id`, `nome`, `data` |
| Method | Verb + object (camelCase) | `calcularTotal()`, `adicionarItem()` |
| Component | Noun + Module | `PedidoModule` |
| Artifact | Filename with extension | `pedido-api.jar` |
| Node | Type + identifier | `Servidor Web`, `Pod 1` |
| State | Adjective or past participle | `Criado`, `AguardandoPagamento` |
| Interface | Prefix `I` + noun | `IPagamento`, `IPedido` |

---

## Glossary

| Term | Definition |
|------|-----------|
| **Actor** | Role played by a user or external system that interacts with the system. |
| **Use Case** | Unit of functionality representing an actor's goal. |
| **Class** | Abstraction defining common attributes and methods for a set of objects. |
| **Component** | Independent software unit with well-defined interfaces. |
| **Interface** | Contract defining a set of operations without implementation. |
| **Node** | Physical element (hardware) or execution environment in deployment diagram. |
| **Artifact** | Software product (file, jar, image) deployed on a node. |
| **State** | Condition or situation an object is in at a given moment. |
| **Transition** | Change of state triggered by an event. |
| **Message** | Communication between objects — synchronous or asynchronous. |
| **Fragment** | Combined block in a sequence diagram (`alt`, `loop`, `opt`, `par`, `ref`). |
| **Stereotype** | Extension mechanism that classifies elements (`<<entity>>`, `<<service>>`). |
| **OCL** | Object Constraint Language — formal notation for invariants and guards. |
| **EID** | Element Identifier — unique ID for traceability across diagrams. |
| **Swimlane** | Partition in an activity diagram showing responsible actor/component. |
