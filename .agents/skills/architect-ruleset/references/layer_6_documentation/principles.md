# Seção 2 – Princípios Fundamentais de Documentação (Layer 6)

**ID:** ARCH-RULESET-L6-DOC-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Fundamentos atitudinais e conceituais de documentação de software e arquitetura.

### Princípio 01 – Documentação como Ativo, não como Subproduto
A documentação é um ativo de primeira classe, com o mesmo valor que o código-fonte. Deve ser versionada, revisada, testada (ex: exemplos funcionais) e mantida com o mesmo rigor.

### Princípio 02 – Documentação Orientada a Público (Audience-First)
Documentação não é para o arquiteto; é para o leitor. Cada artefato deve ser escrito pensando em seu público-alvo (ex: desenvolvedores, operadores, usuários finais, gerentes). Use a linguagem, o nível de detalhe e o formato adequados para cada público.

### Princípio 03 – Documentação Viva (Living Documentation)
Documentação não é um artefato congelado que se escreve uma vez e se esquece. Deve evoluir junto com o código, ser atualizada a cada mudança significativa e ser automaticamente validada quando possível (ex: diagramas gerados a partir do código, contratos OpenAPI validados).

### Princípio 04 – Clareza e Simplicidade (Clarity over Completeness)
É melhor uma documentação clara e concisa (mesmo que incompleta em alguns aspectos) do que uma documentação completa, mas confusa e difícil de navegar. O leitor deve encontrar rapidamente o que precisa. Aplicar as Máximas de Grice (Cap. 6.1).

### Princípio 05 – Rastreabilidade como Pilar
Documentação não pode ser um "silêncio" ou uma "caixa preta". Cada artefato deve ser rastreável a suas origens (requisitos, decisões) e a seus destinatários (código, componentes). A rastreabilidade é a base da governança.

### Princípio 06 – Padronização e Consistência
Toda documentação deve seguir padrões e templates consistentes (ARC42, ADR, README). Isso reduz a carga cognitiva do leitor, pois ele sabe o que esperar em cada seção.
