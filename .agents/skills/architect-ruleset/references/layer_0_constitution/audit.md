# Seção 6 – Critérios de Auditoria da Constituição (Layer 0)

**ID:** ARCH-RULESET-L0-AUDIT  
**Status:** Imutável  
**Escopo:** Métodos de auto-auditoria contínua para o agente.

A auditoria da Layer 0 deve ser realizada automaticamente pelo agente antes de qualquer entrega formal.

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-CON-01 | Todas as decisões referenciam uma regra explícita (REGCON-001). | Busca automática por referências a IDs de regras em toda saída. |
| AUD-CON-02 | Nenhum termo não definido no glossário foi utilizado (REGCON-003). | Scaneamento do texto contra o glossário oficial. |
| AUD-CON-03 | Requisitos possuem rastreabilidade bidirecional (REGCON-002). | Verificação da matriz de rastreabilidade. |
| AUD-CON-04 | Documentação contém alternativas rejeitadas (REGCON-009). | Inspeção da seção "Rationale" em cada artefato. |
| AUD-CON-05 | Nenhuma dependência direta de Negócio → Tecnologia (REGCON-010). | Análise estática do grafo de dependências. |
