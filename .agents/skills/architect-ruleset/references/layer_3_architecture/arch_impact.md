# Seção 5 – Regras de Análise de Impacto Estrutural / Layer 3 (Layer 3 - Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-IMPACT  
**Status:** Definitivo  
**Escopo:** Controle de mudanças técnicas, análise de propagação de carga e encapsulamento de dados.

---

### REGARCH-SW-009 – Análise de Impacto Obrigatória para Mudanças Estruturais

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-009 |
| **Nome** | Análise de Impacto Obrigatória para Mudanças Estruturais |
| **Descrição** | Antes de qualquer mudança estrutural (ex: alteração de interface, refatoração de módulo, substituição de biblioteca, migração de banco), o agente deve realizar uma análise de impacto formal, que deve incluir: (1) identificação de todos os componentes que dependem diretamente do elemento alterado; (2) identificação de dependências indiretas (via composição de relações, Cap. 5.7); (3) avaliação de risco (quebra de contratos, perda de dados, degradação de performance); (4) plano de mitigação (versionamento, feature flags, testes de regressão). |
| **Objetivo** | Garantir que nenhuma mudança quebre acidentalmente partes do sistema, seguindo a rastreabilidade estática do Cap. 8.3.1. |
| **Motivação** | Cap. 8.3.1 (análise de impacto estático via description logics) e Cap. 8.2 (propagação de workload). |
| **Justificativa** | Mudanças sem análise de impacto são a principal causa de incidentes em produção. |
| **Critérios de Aplicação** | Qualquer mudança que afete mais de um módulo, ou qualquer mudança em uma interface pública. |
| **Critérios de Não Aplicação** | Mudanças internas e isoladas (ex: refatoração dentro de uma classe que não altera comportamento público). |
| **Pré-condições** | Matriz de rastreabilidade atualizada (REGREQ-011). |
| **Pós-condições** | Um relatório de impacto formal foi gerado e revisado. |
| **Restrições** | Se o impacto for classificado como "Alto Risco", a mudança requer aprovação do comitê de arquitetura. |
| **Dependências** | REGREQ-011, REGRSN-003. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Antes de mudar o contrato do serviço `classify` de `V1` para `V2`, analisei o impacto: 3 serviços consomem V1. Estratégia: lançar V2, deprecar V1 com período de 6 meses, comunicar aos times." |
| **Exemplo Negativo** | "Mudar o contrato da API sem avisar ninguém." |
| **Anti-pattern** | Acreditar que "ninguém usa" esse endpoint sem verificar a matriz de rastreabilidade. |
| **Métrica** | Percentual de mudanças estruturais com análise de impacto documentada (meta: 100%). |
| **Critérios de Auditoria** | Revisar mudanças: se não houver análise de impacto registrada, falha. |

---

### REGARCH-SW-010 – Proibição de Acesso Direto a Dados de Outro Módulo (Data Encapsulation)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-010 |
| **Nome** | Proibição de Acesso Direto a Dados de Outro Módulo (Data Encapsulation) |
| **Descrição** | Um módulo não pode acessar diretamente as tabelas, arquivos ou armazenamentos de outro módulo. Todo acesso a dados deve ser feito por meio da interface (serviço) provida pelo módulo proprietário. A violação deste princípio (ex: Service A lendo a tabela `variants` que pertence ao Service B) é considerada uma dependência estrutural ilegal e deve ser imediatamente sinalizada e corrigida. |
| **Objetivo** | Preservar o encapsulamento dos dados e evitar acoplamento de esquema (schema coupling). |
| **Motivação** | Cap. 5.5.3 (data objects realizam business objects via serviços), Cap. 9.2.2 (encapsulamento é a base da agregação). |
| **Justificativa** | Acesso direto a dados de outro módulo cria dependências frágeis (ex: mudança no esquema do Service B quebra o Service A) e viola a propriedade dos dados. |
| **Critérios de Aplicação** | Toda interação com dados que residem em um módulo diferente. |
| **Critérios de Não Aplicação** | Acesso a bases de dados compartilhadas explicitamente como parte de um `Shared Kernel` (com regras estritas de governança). |
| **Pré-condições** | Dados categorizados por módulo. |
| **Pós-condições** | Acesso a dados ocorre exclusivamente via serviços. |
| **Restrições** | Relatórios e consultas analíticas (OLAP) podem ser exceções, mas devem usar réplicas (read replicas) dedicadas, nunca o banco transacional de origem. |
| **Dependências** | REGARCH-SW-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Service A chama o serviço `VariantService.getVariants()` para obter dados, em vez de executar `SELECT * FROM variants` diretamente." |
| **Exemplo Negativo** | "Service A tem uma string de conexão para o banco do Service B." |
| **Anti-pattern** | "Acesso direto justificado por performance" – usar cache de leitura em vez de acesso direto. |
| **Métrica** | Número de conexões de banco compartilhadas entre módulos (meta: zero). |
| **Critérios de Auditoria** | Auditoria de configurações de banco e conexões JDBC/ODBC. |
