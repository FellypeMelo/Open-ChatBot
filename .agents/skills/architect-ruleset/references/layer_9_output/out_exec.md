# Seção 7 – Regras de Resultados Executivos (Layer 9 - Output Rules e Formatação de Resultados)

**ID:** ARCH-RULESET-L9-OUT-EXEC  
**Status:** Definitivo  
**Escopo:** Métodos de apresentação simplificada (CLARO) orientada a tomadores de decisão executivos.

---

### REGOUT-011 – Formatação de Recomendações para Decisão Executiva (CLARO)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-011 |
| **Nome** | Formatação de Recomendações para Decisão Executiva (CLARO) |
| **Descrição** | Para recomendações destinadas a executivos e tomadores de decisão, o agente deve utilizar o formato CLARO: **(C) Contexto**: 1 parágrafo com a situação atual; **(L) Lacuna**: o problema ou oportunidade; **(A) Alternativas**: 2-3 opções viáveis; **(R) Recomendação**: a opção sugerida, com justificativa; **(O) Objetivo**: o resultado esperado e próximos passos. A recomendação deve ser autoexplicativa e não exigir conhecimento técnico profundo. |
| **Objetivo** | Facilitar a tomada de decisão executiva, apresentando a informação de forma clara, direta e acionável. |
| **Motivação** | Cap. 7.4.6 (comprometimento executivo). |
| **Justificativa** | Executivos precisam de informações claras e concisas para decidir rapidamente. |
| **Critérios de Aplicação** | Recomendações para tomadores de decisão. |
| **Critérios de Não Aplicação** | Recomendações técnicas para engenheiros (que podem ser mais detalhadas). |
| **Pré-condições** | Análise concluída. |
| **Pós-condições** | Recomendação formatada. |
| **Restrições** | A seção de Alternativas deve destacar os trade-offs de risco, custo e benefício. |
| **Dependências** | REGOUT-002. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "**C**: Sistema atual com gargalos de performance. **L**: Necessidade de escalabilidade. **A**: (1) Migrar para CockroachDB (custo médio, performance alta), (2) Particionar PostgreSQL (custo baixo, performance média). **R**: Opção 1 – CockroachDB. **O**: Implantar em 6 meses, reduzir latência em 30%." |
| **Exemplo Negativo** | "Recomendo migrar para CockroachDB." (sem contexto, alternativas, ou justificativa). |
| **Anti-pattern** | Incluir detalhes técnicos irrelevantes (ex: "usaremos a versão 23.1.2 com o driver JDBC..." – o executivo não precisa disso). |
| **Métrica** | Percentual de recomendações com formato CLARO (meta: 100%). |
| **Critérios de Auditoria** | Revisar recomendações executivas: se não tiverem estrutura CLARO, falha. |
