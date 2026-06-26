# Seção 7 – Regras de Métricas e Padrões de Qualidade (Layer 12 - TEST-METRICS)

---

### REGTEST-010 – Monitoramento de Complexidade Ciclomática e Dívida Técnica

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-010 |
| **Nome** | Monitoramento de Complexidade Ciclomática e Dívida Técnica |
| **Descrição** | O agente deve monitorar e impor limites de complexidade ciclomática (máximo de **10** por função ou método) e gerenciar a dívida técnica acumulada. Qualquer função que exceda o limite de 10 deve ser refatorada ou receber uma justificativa técnica formal aprovada no processo de Code Review. O pipeline de CI deve executar ferramentas de análise estática de código (ex: SonarQube, golangci-lint, flake8) para calcular esses índices em cada commit. |
| **Objetivo** | Garantir que o código-base seja modular, legível, fácil de manter e testar, prevenindo o acúmulo de complexidade acidental e dívida técnica. |
| **Motivação** | Cap. 24.4 – métricas de código de produto medem a compreensibilidade e acoplamento estático do código. |
| **Justificativa** | Complexidade ciclomática elevada correlaciona-se fortemente com a taxa de defeitos introduzidos e com a dificuldade de obter alta cobertura de testes. |
| **Critérios de Aplicação** | Todo código-base em Go, Python e JavaScript. |
| **Critérios de Não Aplicação** | Código autogerado (ex: gRPC stubs, ORM models estruturados automaticamente). |
| **Pré-condições** | Linters e analisadores estáticos configurados e integrados no pipeline de CI. |
| **Pós-condições** | Relatório de lint limpo e sem violações de complexidade de nível "Bloqueante". |
| **Restrições** | Exceções de refatoração para legados devem ser catalogadas como Débitos Técnicos com prazo de resolução. |
| **Dependências** | REGQUAL-012 (dívida técnica), REGQUAL-010 (CI gates). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Análise do SonarQube detectou complexidade ciclomática média do projeto em 3.8. Nenhuma função excede complexidade 10. Merge liberado." |
| **Exemplo Negativo** | "Função de processamento VCF de 350 linhas com complexidade 28 é mesclada na main sem qualquer refatoração ou ADR." |
| **Anti-pattern** | Ignorar warnings de complexidade ou desligar regras de análise no CI para fazer o build passar rapidamente. |
| **Métrica** | Complexidade ciclomática média por arquivo e montante de dívida técnica (em dias de esforço). |
| **Critérios de Auditoria** | Revisar o dashboard do SonarQube ou relatórios de análise estática do projeto. |

---

### REGTEST-011 – Adoção de Padrões de Qualidade e Processos Coerentes (ISO 9001)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGTEST-011 |
| **Nome** | Adoção de Padrões de Qualidade e Processos Coerentes (ISO 9001) |
| **Descrição** | O agente deve garantir que o ciclo de desenvolvimento siga processos consistentes de garantia de qualidade (SGQ) alinhados a padrões internacionais (ISO 9001 / CMMI). Os processos devem contemplar: **(1)** definições formais das etapas do ciclo de vida; **(2)** documentação e versionamento de artefatos; **(3)** registro auditável de decisões e mudanças; **(4)** auditoria periódica de processos; **(5)** rastreabilidade imutável de requisitos. |
| **Objetivo** | Fornecer processos de engenharia de software previsíveis, auditáveis e consistentes, focados na melhoria contínua da qualidade do produto clínico. |
| **Motivação** | Cap. 24.2.1 – os padrões de qualidade organizacional, como ISO 9001, definem processos para estabelecer controle de qualidade. |
| **Justificativa** | O desenvolvimento de um software genético voltado para saúde pública exige processos estruturados para conformidade regulatória (ANVISA) e segurança. |
| **Critérios de Aplicação** | Gestão de ciclo de vida e engenharia de software de toda a organização. |
| **Critérios de Não Aplicação** | Scripts descartáveis ou testes exploratórios fora de ambientes compartilhados. |
| **Pré-condições** | Manual ou documentação do Sistema de Gestão de Qualidade (SGQ) disponível para o time. |
| **Pós-condições** | Evidências de auditoria de processo geradas a cada release. |
| **Restrições** | A burocracia dos processos não deve inviabilizar a agilidade (KISS e YAGNI aplicam-se à documentação). |
| **Dependências** | REGGOV-008 (ciclo de vida), REGREQ-011 (rastreabilidade). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Processos documentados e seguidos pelo time, com revisões e auditorias internas a cada trimestre. Certificação de qualidade ativa." |
| **Exemplo Negativo** | "Cada squad escolhe seu próprio processo de qualidade ad-hoc, sem padronização, auditoria de processos ou controle de registros." |
| **Anti-pattern** | Tratar os processos de qualidade como uma atividade burocrática de fachada, sem impacto no fluxo de desenvolvimento real. |
| **Métrica** | Percentual de conformidade de processos em auditorias de qualidade. |
| **Critérios de Auditoria** | Revisar relatórios de auditorias de qualidade do SGQ e rastreabilidade de artefatos de entrega. |
