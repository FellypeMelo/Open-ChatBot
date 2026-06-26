# Seção 7 – Regras de Organização e Governança / Layer 3 (Layer 3 - Software & Arquitetura)

**ID:** ARCH-RULESET-L3-ARCH-GOV  
**Status:** Definitivo  
**Escopo:** Conway's Law (alinhamento organizacional) e priorização da arquitetura global.

---

### REGARCH-SW-013 – Alinhamento com a Lei de Conway (Estrutura Organizacional)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-013 |
| **Nome** | Alinhamento com a Lei de Conway (Estrutura Organizacional → Estrutura do Sistema) |
| **Descrição** | O agente deve garantir que a estrutura dos módulos, serviços e Bounded Contexts esteja alinhada com a estrutura organizacional (squads, times, departamentos). Se a organização tem um time de "Genômica", deve haver um Bounded Context correspondente. Se dois times compartilham um módulo, isso gera conflitos de propriedade e deve ser evitado. Essa regra é derivada da Lei de Conway (Cap. 9.3.5) e visa minimizar a complexidade de comunicação. |
| **Objetivo** | Minimizar o "custo de comunicação" entre times e evitar conflitos de propriedade. |
| **Motivação** | Cap. 9.3.5 – Lei de Conway: "A estrutura do sistema projetado será isomórfica à estrutura de comunicação da equipe projetista." |
| **Justificativa** | Times que não têm autonomia sobre seus módulos geram dependências externas e atrasos. Módulos alinhados com times maximizam a produtividade. |
| **Critérios de Aplicação** | Estruturação inicial e evolução da arquitetura. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Estrutura organizacional conhecida. |
| **Pós-condições** | Cada módulo possui um time proprietário identificado. |
| **Restrições** | Se a estrutura organizacional mudar (ex: reestruturação), a arquitetura deve ser revisada para refletir a mudança (evolução controlada). |
| **Dependências** | REGARCH-SW-005 (Bounded Contexts). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Time de Genômica é dono do Bounded Context 'Genômica'. Time de Laudos é dono do Bounded Context 'Laudos'." |
| **Exemplo Negativo** | "Um único time (Backend) é dono de todos os contextos, gerando gargalo." |
| **Anti-pattern** | Forçar um time a manter um módulo que ele não entende (ex: time de frontend mantendo backend). |
| **Métrica** | Número de módulos por time (média saudável: 1-3 módulos por time). |
| **Critérios de Auditoria** | Revisar propriedade de módulos vs. estrutura de squads. |

---

### REGARCH-SW-014 – Otimização Global (Arquitetura) vs. Otimização Local (Projeto)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGARCH-SW-014 |
| **Nome** | Otimização Global (Arquitetura) vs. Otimização Local (Projeto) – Proibição de Desalinhamento |
| **Descrição** | O agente deve sinalizar qualquer decisão de design ou implementação que otimize um componente localmente em detrimento da arquitetura global (ex: usar uma tecnologia que não está no portfólio aprovado para ganhar performance local, ou criar uma dependência direta para "facilitar" a implementação do time). Se uma otimização local é necessária, o agente deve documentar o trade-off e submeter ao comitê de arquitetura para aprovação formal. |
| **Objetivo** | Preservar a integridade conceitual e a governança arquitetural. |
| **Motivação** | Cap. 9.4.2 – Conflito entre arquitetos (otimização global) e gerentes de projeto (otimização local). |
| **Justificativa** | Decisões locais não alinhadas geram dívida técnica e acabam aumentando o custo total de propriedade (TCO). |
| **Critérios de Aplicação** | Toda decisão de design que envolva escolha de tecnologia, padrão de integração ou arquitetura. |
| **Critérios de Não Aplicação** | Decisões puramente internas ao módulo, que não afetam outros módulos. |
| **Pré-condições** | Arquitetura de referência definida. |
| **Pós-condições** | Decisão documentada com rationale e, se aprovada, arquitetura atualizada. |
| **Restrições** | A otimização global tem precedência sobre a local, conforme REGCON-009. |
| **Dependências** | REGCON-009. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "O time propôs usar MongoDB para performance. A arquitetura global definiu PostgreSQL como padrão. Trade-off: performance +30% vs. custo de suporte +100%. Comitê aprovou após justificativa." |
| **Exemplo Negativo** | "O time usou MongoDB 'escondido' porque era mais rápido." |
| **Anti-pattern** | Adotar tecnologias "fashion" sem considerar o custo de longo prazo. |
| **Métrica** | Número de exceções à arquitetura aprovadas vs. rejeitadas. |
| **Critérios de Auditoria** | Revisar se cada tecnologia fora do padrão tem uma justificativa documentada. |
