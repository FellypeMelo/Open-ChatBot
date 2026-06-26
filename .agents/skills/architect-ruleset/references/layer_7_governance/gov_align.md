# Seção 4 – Regras de Alinhamento Estratégico (Layer 7 - Governança, Alinhamento e Gestão de Mudanças)

**ID:** ARCH-RULESET-L7-GOV-ALIGN  
**Status:** Definitivo  
**Escopo:** Métodos para garantir isomofismo organizacional (Lei de Conway), taxonomia de negócio (FMO) e prevalência de otimizações globais.

---

### REGGOV-003 – Aplicação da Lei de Conway (Estrutura Organizacional → Estrutura do Sistema)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-003 |
| **Nome** | Aplicação da Lei de Conway (Estrutura Organizacional → Estrutura do Sistema) |
| **Descrição** | O agente deve garantir que a estrutura dos módulos, serviços e Bounded Contexts esteja alinhada com a estrutura organizacional (squads, times, departamentos). Se a organização tem um time de "Genômica", deve haver um Bounded Context correspondente. Se dois times compartilham um módulo, isso gera conflitos de propriedade e deve ser evitado. O agente deve sinalizar desalinhamentos e recomendar a reestruturação do sistema ou da organização para alinhar. |
| **Objetivo** | Minimizar o "custo de comunicação" entre times, reduzir conflitos de propriedade e acelerar a tomada de decisão. |
| **Motivação** | Cap. 9.3.5 – Lei de Conway: "A estrutura do sistema projetado será isomórfica à estrutura de comunicação da equipe projetista." |
| **Justificativa** | Times que não têm autonomia sobre seus módulos geram dependências externas e atrasos. Módulos alinhados com times maximizam a produtividade. |
| **Critérios de Aplicação** | Estruturação inicial e evolução da arquitetura. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | Estrutura organizacional conhecida. |
| **Pós-condições** | Cada módulo possui um time proprietário identificado. |
| **Restrições** | Se a estrutura organizacional mudar (ex: reestruturação), a arquitetura deve ser revisada para refletir a mudança (evolução controlada). |
| **Dependências** | REGARCH-SW-005, REGARCH-SW-013. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Time de Genômica é dono do Bounded Context 'Genômica'. Time de Laudos é dono do Bounded Context 'Laudos'." |
| **Exemplo Negativo** | "Um único time (Backend) é dono de todos os contextos, gerando gargalo." |
| **Anti-pattern** | Forçar um time a manter um módulo que ele não entende (ex: time de frontend mantendo backend). |
| **Métrica** | Número de módulos por time (média saudável: 1-3 módulos por time). |
| **Critérios de Auditoria** | Revisar propriedade de módulos vs. estrutura de squads. |

---

### REGGOV-004 – Aplicação do Padrão FMO (Front/Mid/Back Office) para Estruturação de Negócio

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-004 |
| **Nome** | Aplicação do Padrão FMO (Front/Mid/Back Office) para Estruturação de Negócio |
| **Descrição** | O agente deve recomendar a aplicação do padrão FMO (Cap. 9.3.6) para estruturar as camadas do sistema e os times correspondentes: **(1) Front-office**: focado em experiência do cliente, canais, personalização (ex: interfaces de usuário, portais); **(2) Mid-office**: focado em orquestração de processos, regras de negócio, qualidade, workflow (ex: serviços de orquestração, motores de regras); **(3) Back-office**: focado em operações de commodity, processamento em lote, armazenamento, sistemas legados (ex: bancos de dados, processamento de arquivos). O alinhamento entre FMO e a estrutura organizacional deve ser mantido. |
| **Objetivo** | Isolar a instabilidade (Front-office muda mais rápido) da estabilidade (Back-office muda mais lentamente), reduzindo o impacto de mudanças. |
| **Motivação** | Cap. 9.3.6 – Padrão FMO para organizações. |
| **Justificativa** | O padrão FMO é um padrão de alinhamento testado em diversas indústrias, especialmente financeira e governamental. |
| **Critérios de Aplicação** | Estruturação de novos sistemas ou reestruturação de sistemas existentes. |
| **Critérios de Não Aplicação** | Sistemas muito pequenos (ex: < 3 módulos). |
| **Pré-condições** | Mapeamento funcional do sistema. |
| **Pós-condições** | Cada módulo classificado em F, M ou B. |
| **Restrições** | A comunicação entre F e B deve ser mediada pelo M (Mid-office), evitando dependências diretas. |
| **Dependências** | REGGOV-003 (Lei de Conway). |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Front: portal web e aplicativo mobile. Mid: serviço de orquestração de classificação e validação. Back: banco de dados genômico e processamento em lote." |
| **Exemplo Negativo** | "Todos os módulos misturados, sem separação clara entre Front, Mid e Back." |
| **Anti-pattern** | Front e Back se comunicando diretamente, ignorando o Mid, criando acoplamento desnecessário. |
| **Métrica** | Percentual de módulos classificados no padrão FMO. |
| **Critérios de Auditoria** | Revisar a classificação de cada módulo. |

---

### REGGOV-005 – Otimização Global Prevalece sobre Otimização Local (Proibição de Desalinhamento)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGGOV-005 |
| **Nome** | Otimização Global Prevalece sobre Otimização Local (Proibição de Desalinhamento) |
| **Descrição** | O agente deve sinalizar qualquer decisão de design ou implementação que otimize um componente localmente em detrimento da arquitetura global (ex: usar uma tecnologia que não está no portfólio aprovado para ganhar performance local, ou criar uma dependência direta para "facilitar" a implementação do time). Se uma otimização local é necessária, o agente deve documentar o trade-off e submeter ao Comitê de Arquitetura para aprovação formal. A otimização global tem precedência conforme REGCON-009. |
| **Objetivo** | Preservar a integridade conceitual e a governança arquitetural, evitando fragmentação. |
| **Motivação** | Cap. 9.4.2 – Conflito entre arquitetos (otimização global) e gerentes de projeto (otimização local). |
| **Justificativa** | Decisões locais não alinhadas geram dívida técnica e acabam aumentando o custo total de propriedade (TCO). |
| **Critérios de Aplicação** | Toda decisão de design que envolva escolha de tecnologia, padrão de integração ou arquitetura. |
| **Critérios de Não Aplicação** | Decisões puramente internas ao módulo, que não afetam outros módulos. |
| **Pré-condições** | Arquitetura de referência definida. |
| **Pós-condições** | Decisão documentada com rationale e, se aprovada, arquitetura atualizada. |
| **Restrições** | A otimização global tem precedência sobre a local, conforme REGCON-009. |
| **Dependências** | REGCON-009, REGGOV-002. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "O time propôs usar MongoDB para performance. A arquitetura global definiu PostgreSQL como padrão. Trade-off: performance +30% vs. custo de suporte +100%. Comitê aprovou após justificativa." |
| **Exemplo Negativo** | "O time usou MongoDB 'escondido' porque era mais rápido." |
| **Anti-pattern** | Adotar tecnologias "fashion" sem considerar o custo de longo prazo. |
| **Métrica** | Número de exceções à arquitetura aprovadas vs. rejeitadas. |
| **Critérios de Auditoria** | Revisar se cada tecnologia fora do padrão tem uma justificativa documentada. |
