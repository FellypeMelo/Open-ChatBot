# Seção 2 – Princípios Fundamentais de Segurança e Privacidade (Layer 5)

**ID:** ARCH-RULESET-L5-SEC-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Fundamentos atitudinais e conceituais de segurança da informação e privacidade de dados.

### Princípio 01 – Privacidade por Design (Privacy by Design – PbD)
A privacidade não pode ser uma camada adicional ou um "adendo" no final do desenvolvimento. Deve ser incorporada em todas as fases do ciclo de vida, desde a concepção da arquitetura até a implantação e desativação. Requisitos de privacidade (LGPD) têm a mesma prioridade que requisitos funcionais (RN).

### Princípio 02 – Defesa em Profundidade (Defense in Depth)
Nenhum único controle de segurança é suficiente. A arquitetura deve implementar múltiplas camadas de defesa (rede, aplicação, dados, identidade, monitoramento), de modo que, se uma camada for comprometida, outras ainda estejam ativas.

### Princípio 03 – Menor Privilégio (Least Privilege)
Nenhum usuário, sistema ou serviço deve ter permissões além do mínimo necessário para executar suas funções. Isso se aplica a acessos a dados, execução de comandos, permissões de rede e privilégios de sistema operacional.

### Princípio 04 – Confiança Zero (Zero Trust)
Nunca confie implicitamente em nenhuma entidade, mesmo dentro da rede interna. Toda requisição deve ser autenticada, autorizada e criptografada, independentemente de sua origem (interna ou externa).

### Princípio 05 – Dados como Ativo Crítico
Dados são o ativo mais valioso e mais visado. Eles devem ser classificados, inventariados e protegidos com base em sua criticidade. A segurança da infraestrutura serve aos dados, e não o contrário.

### Princípio 06 – Auditoria Imutável
Toda ação que crie, modifique, acesse ou exclua dados restritos ou sensíveis deve ser registrada em uma trilha de auditoria imutável (append-only). A trilha deve ser protegida contra alterações e ter integridade verificável.

### Princípio 07 – Conformidade como Requisito Não-Negociável
A conformidade com a LGPD e outras regulações não é negociável. Requisitos de conformidade (LGPD) devem ser tratados como bloqueantes (severidade crítica) e nunca postergados em prol de entregas funcionais.
