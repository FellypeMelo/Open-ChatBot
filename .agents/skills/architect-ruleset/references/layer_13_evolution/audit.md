# Seção 7 – Critérios de Auditoria, Exemplo e Evolução (Layer 13 - Evolução e Gestão de Configuração)

**ID:** ARCH-RULESET-L13-EVOL-AUDIT  
**Status:** Definitivo  
**Escopo:** Métodos de verificação de processos de mudança, caso prático de sistema legado e extensões futuras.

---

## 1. Matriz de Auditoria de Evolução e Configuração

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| **AUD-EVOL-01** | Leis de Lehman consideradas no planejamento (REGEVOL-001). | Revisar se o planejamento de releases e roadmaps do produto inclui ações voltadas à prevenção de degradação estrutural e controle de complexidade ciclomática. |
| **AUD-EVOL-02** | Manutenção classificada e priorizada (REGEVOL-002). | Auditar o backlog de tarefas e change requests (Jira) para certificar a classificação tripartite (corretiva, adaptativa e perfectiva) e respectiva prioridade. |
| **AUD-EVOL-03** | Refatoração contínua com alocação de tempo (REGEVOL-003). | Validar o histórico de commits do Git e registros de sprint planning para atestar que ao menos 10-20% do esforço é dedicado à resolução de dívida técnica. |
| **AUD-EVOL-04** | Avaliação de sistemas legados documentada (REGEVOL-004). | Analisar se os sistemas antigos/legados foram classificados formalmente na matriz 2x2 baseada em valor de negócio e qualidade técnica. |
| **AUD-EVOL-05** | Estratégia de evolução definida (REGEVOL-005). | Confirmar se há um plano de ação detalhado (manter, modernizar/reengenharia, substituir) com justificativa de custo e cronograma para sistemas legados. |
| **AUD-EVOL-06** | Processo formal de change management (REGEVOL-006). | Auditar a trilha das solicitações de mudança (CR), avaliando se passaram por análise de impacto e aprovação prévia do CCB antes de ir a produção. |
| **AUD-EVOL-07** | Estratégia de branching definida e seguida (REGEVOL-007). | Analisar o repositório Git para verificar conformidade com o fluxo de branching estruturado (ex: GitFlow ou Trunk-Based) e bloqueio de pushes diretos. |
| **AUD-EVOL-08** | Pipeline de CI configurado e usado (REGEVOL-008). | Atarraxar e verificar as execuções automáticas de builds no CI, garantindo que testes unitários/integração e análise estática rodam a cada commit de PR. |
| **AUD-EVOL-09** | Versionamento semântico e notas de release (REGEVOL-009). | Verificar o histórico de tags do Git, garantindo a conformidade ao padrão SemVer e a existência de notas de release documentando as mudanças. |

---

## 2. Exemplo Integrado de Aplicação

**Cenário**: Uma empresa possui um sistema crítico de folha de pagamento em COBOL, com 15 anos de uso. A manutenção é muito cara, lenta e arriscada por falta de programadores especializados, mas o sistema suporta regras fiscais complexas essenciais para o negócio.

**Aplicação das Regras**:

1. **REGEVOL-001 (Leis de Lehman)**: O arquiteto avalia o histórico e percebe que as mudanças tornaram o código altamente fragilizado (Lei 2 - Complexidade Crescente) e as atualizações levam o triplo do tempo de antes (Lei 7 - Qualidade Declinante).

2. **REGEVOL-004 (Avaliação de Legado)**: O agente avalia o sistema em duas dimensões:
   - *Valor de Negócio*: Altíssimo (roda a folha sem erros e cumpre as obrigações sindicais).
   - *Qualidade Técnica*: Baixíssima (tecnologia obsoleta COBOL, sem documentação viva, sem testes de regressão).
   - *Classificação*: Matriz indica "Alto Valor / Baixa Qualidade".

3. **REGEVOL-005 (Estratégia)**: O agente recomenda a estratégia de **Reengenharia** (reescrever em Java mantendo as mesmas funcionalidades e migrando o banco de dados hierárquico para relacional). O plano é de 18 meses com cronograma e custo estimados.

4. **REGEVOL-002 (Priorização)**: As solicitações de mudança são catalogadas e a migração é tratada como perfectiva/adaptativa de prioridade alta, enquanto bugs em produção no COBOL continuam como corretiva de urgência.

5. **REGEVOL-003 (Refatoração)**: O novo código Java em construção é refatorado continuamente a cada sprint, usando o SonarQube para barrar o surgimento de bad smells e código duplicado.

6. **REGEVOL-006 (Change Management)**: É aberta a Change Request `CR-200` para iniciar o projeto de reengenharia, detalhando o plano de transição de dados de folha, riscos, rollback e impactos organizacionais, sendo aprovada pelo CCB.

7. **REGEVOL-007 (Versionamento)**: O novo repositório Java utiliza o GitFlow. Todo desenvolvimento ocorre em branches `feature/*` que requerem PR e 1 aprovação para integração em `develop`.

8. **REGEVOL-008 (CI)**: Configurado o pipeline em GitHub Actions. Qualquer alteração gera build, roda testes unitários e bloqueia o merge se a cobertura cair abaixo de 80% ou se houver vulnerabilidades de segurança.

9. **REGEVOL-009 (Release)**: O sistema migrado é empacotado e lançado incrementalmente, utilizando tags como `v1.0.0` (inicial), `v1.1.0` (módulos adicionais) e `v1.1.1` (correções), com release notes detalhados para o setor de RH.

**Saída Final (resumida)**:
> "Estratégia de evolução do legado de folha de pagamento: reengenharia (reescrita em Java) estimada em 18 meses. O sistema foi classificado como Alto Valor / Baixa Qualidade. Processo de mudanças gerenciado via CR-200 aprovado por CCB, com repositório no GitFlow, build de CI automatizado com cobertura > 80% e controle de releases orientado a SemVer."

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido com sub-módulos especializados:
- **Módulo 14-A**: Gestão de Dívida Técnica (ferramentas de medição, catalogação e estratégias de refatoração em grande escala).
- **Módulo 14-B**: Padrões de Modernização de Legados (padrões Strangler Fig, encapsulamento por API, migração de dados em fases).
- **Módulo 14-C**: CI/CD e GitOps Avançados (pipelines de entrega contínua, infraestrutura como código - IaC, ferramentas de deploy automatizado).
- **Módulo 14-D**: Gestão de Configuração Multi-Repositório (monorepo vs multirepo, dependências compartilhadas, versionamento de microserviços).

Todas as extensões devem respeitar as regras base e a Constituição.
