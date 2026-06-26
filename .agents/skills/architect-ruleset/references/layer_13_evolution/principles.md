# Seção 2 – Princípios Fundamentais (Layer 13 - Evolução e Gestão de Configuração)

**ID:** ARCH-RULESET-L13-EVOL-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Princípios conceituais fundamentais regulando evolução, manutenção estruturada e controle de configuração.

---

## Princípios de Evolução e Configuração

### Princípio 01 – Mudança é Inevitável e Contínua (Lei de Lehman 1)
Sistemas de software que são utilizados em ambientes do mundo real precisam mudar continuamente para manterem-se úteis e alinhados às necessidades operacionais. A evolução não é uma exceção do ciclo de vida, mas sim a regra permanente.

### Princípio 02 – Estrutura Degrada com o Tempo (Lei de Lehman 2)
À medida que um sistema de software evolui, sua estrutura interna tende a tornar-se progressivamente mais complexa e desordenada. É obrigatório investir continuamente em refatoração e reengenharia para combater essa entropia e preservar a manutenibilidade.

### Princípio 03 – Manutenção é Mais que Correção de Bugs
A maior parte do orçamento e esforço de manutenção de um sistema está concentrada em adaptações a novos ambientes operacionais (manutenção adaptativa) e na adição de melhorias e novas funcionalidades demandadas (manutenção perfectiva), e não estritamente na correção de bugs e erros operacionais (manutenção corretiva).

### Princípio 04 – Decisões sobre Legados Baseadas em Valor e Qualidade
As decisões estratégicas de manter, realizar reengenharia ou descontinuar/substituir um sistema legado devem ser embasadas por uma análise equilibrada e quantitativa que considere tanto o seu valor real para o negócio quanto a sua qualidade técnica estrutural.

### Princípio 05 – Gestão de Configuração é Essencial para Rastreabilidade
Sem uma gestão de configuração de software (SCM) rigorosa, torna-se impossível garantir a reprodutibilidade dos builds, saber quais alterações foram integradas ao código por quais desenvolvedores, e realizar a reversão segura de código (rollback) em caso de incidentes.

### Princípio 06 – Cada Mudança Deve ser Rastreável e Aprovada
Nenhuma alteração de código ou infraestrutura pode ser introduzida em baselines estabilizadas de forma ad-hoc. Toda modificação deve ser documentada via solicitações formais de mudança (CR), analisada em termos de impacto técnico/risco, e aprovada pela respectiva alçada de governança.
