# Seção 6 – Regras de Relatórios e Documentos (Layer 9 - Output Rules e Formatação de Resultados)

**ID:** ARCH-RULESET-L9-OUT-REPORT  
**Status:** Definitivo  
**Escopo:** Estruturação formal de relatórios de engenharia e inclusão sistemática de cabeçalhos de metadados.

---

### REGOUT-009 – Estrutura Padrão para Relatórios de Análise

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-009 |
| **Nome** | Estrutura Padrão para Relatórios de Análise |
| **Descrição** | Relatórios formais de análise (ex: análise de arquitetura, parecer técnico, relatório de risco) devem seguir a estrutura: **(1) Página de Título**: título, autor, data, versão; **(2) Sumário Executivo**: síntese em linguagem não técnica; **(3) Índice**: para relatórios com mais de 10 páginas; **(4) Introdução**: contexto, objetivos, escopo, metodologia; **(5) Desenvolvimento**: análise detalhada, com evidências, alternativas, justificativas; **(6) Conclusões e Recomendações**: síntese das conclusões e ações sugeridas; **(7) Referências**: requisitos, normas, ADRs, dados; **(8) Anexos**: detalhes complementares (diagramas, dados brutos). |
| **Objetivo** | Padronizar a produção de relatórios, garantindo que todos os elementos essenciais estejam presentes. |
| **Motivação** | Cap. 7.4 (validação e comprometimento), Cap. 10 (ferramentas de relatório). |
| **Justificativa** | Relatórios sem estrutura padrão são difíceis de ler, revisar e arquivar. |
| **Critérios de Aplicação** | Relatórios formais (análise de arquitetura, parecer, relatório de risco). |
| **Critérios de Não Aplicação** | Respostas curtas, emails, notas rápidas. |
| **Pré-condições** | Análise concluída. |
| **Pós-condições** | Relatório estruturado. |
| **Restrições** | O Sumário Executivo não pode ter mais que 1 página. |
| **Dependências** | REGOUT-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Relatório de Análise de Migração – versão 1.0, com Sumário Executivo, Introdução, Análise (3 alternativas), Conclusão, Recomendação, Referências." |
| **Exemplo Negativo** | "Documento sem título, sem sumário, sem estrutura." |
| **Anti-pattern** | Sumário Executivo com jargões técnicos, que o executivo não entenderá. |
| **Métrica** | Percentual de relatórios com estrutura padrão. |
| **Critérios de Auditoria** | Revisar relatórios: se não tiver a estrutura, falha. |

---

### REGOUT-010 – Inclusão Obrigatória de Metadados (Data, Versão, Autor, Status)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGOUT-010 |
| **Nome** | Inclusão Obrigatória de Metadados (Data, Versão, Autor, Status) |
| **Descrição** | Toda saída formal (relatório, parecer, documento) deve conter metadados: **(1)** Data de criação/última atualização; **(2)** Versão (ex: 1.0, 1.1); **(3)** Autor(es); **(4)** Status (Rascunho, Em Revisão, Aprovado, Arquivado – REGGOV-008); **(5)** Destinatário (quem deve receber). Metadados facilitam o rastreamento e a governança. |
| **Objetivo** | Garantir rastreabilidade e controle de versão da documentação. |
| **Motivação** | Cap. 1.3 (ciclo de vida), Cap. 9.2.3 (versionamento). |
| **Justificativa** | Sem metadados, não se sabe se um documento está atualizado, se já foi revisado, ou quem o produziu. |
| **Critérios de Aplicação** | Relatórios, documentos de arquitetura, pareceres, atas. |
| **Critérios de Não Aplicação** | Respostas curtas e conversacionais. |
| **Pré-condições** | Documento criado. |
| **Pós-condições** | Metadados incluídos. |
| **Restrições** | O Status deve ser atualizado a cada alteração significativa. |
| **Dependências** | REGGOV-008, REGDOC-010. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "**Data:** 2025-01-15  \n**Versão:** 1.2  \n**Autor:** Agente Arquiteto  \n**Status:** Aprovado" |
| **Exemplo Negativo** | Documento sem data, versão ou autor. |
| **Anti-pattern** | Manter a versão "1.0" para sempre, mesmo após várias alterações. |
| **Métrica** | Percentual de documentos com metadados (meta: 100%). |
| **Critérios de Auditoria** | Revisar documentos: se não tiver metadados, falha. |
