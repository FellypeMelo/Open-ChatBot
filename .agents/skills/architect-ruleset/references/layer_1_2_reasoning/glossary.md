# Seção 1 – Glossário Formal (Layer 1 & 2)

**ID:** ARCH-RULESET-L12-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Definições conceituais canônicas para o motor de raciocínio da IA.

| Termo | Definição Canônica |
| :--- | :--- |
| **Raciocínio Lógico** | Processo de derivar conclusões a partir de premissas usando regras de inferência válidas (dedução, indução, abdução). O agente deve sempre explicitar o tipo de inferência utilizada. |
| **Alucinação** | Geração de conteúdo que não é fundamentado em fatos, regras ou evidências fornecidas, apresentado como se fosse verdadeiro. É o erro mais grave que o agente pode cometer. |
| **Incerteza** | Estado de conhecimento insuficiente para determinar com certeza o valor de verdade de uma proposição. Deve ser explicitamente modelada, nunca ignorada. |
| **Contradição** | Ocorrência de duas ou mais proposições que não podem ser simultaneamente verdadeiras no mesmo contexto. Deve ser detectada e resolvida. |
| **Premissa** | Proposição assumida como verdadeira para fins de raciocínio. Toda premissa deve ser explicitamente rotulada e, se não validada, marcada como suposição. |
| **Evidência** | Dado observado, documentado ou verificado que suporta ou refuta uma proposição. Evidência tem peso, que deve ser avaliado. |
| **Viés Cognitivo** | Padrão sistemático de desvio da racionalidade no julgamento. O agente é programado para detectar e mitigar vieses em seu próprio raciocínio e nas entradas do usuário. |
| **Método Socrático** | Técnica de questionamento contínuo para testar a consistência, a completude e a validade de proposições, premissas e conclusões. |
| **Trade-off** | Situação de decisão em que se ganha algo em uma dimensão e se perde em outra. Deve ser explicitamente quantificado e justificado. |
| **Contexto** | Conjunto de circunstâncias, restrições e informações que circundam uma decisão ou proposição. O agente não pode raciocinar fora do contexto definido. |
