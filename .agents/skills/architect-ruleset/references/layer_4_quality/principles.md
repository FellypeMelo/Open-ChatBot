# Seção 2 – Princípios Fundamentais da Qualidade (Layer 4)

**ID:** ARCH-RULESET-L4-QUAL-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Fundamentos atitudinais e conceituais da garantia de qualidade técnica.

### Princípio 01 – Qualidade como Requisito Não-Funcional (RT)
Qualidade não é um "extra"; é um requisito não-funcional obrigatório. Todo RT de qualidade deve ser SMART (mensurável) e ter critérios de aceitação explícitos.

### Princípio 02 – Prevenção em vez de Detecção
É mais barato e eficaz prevenir defeitos na fase de design/requisitos do que detectá-los em produção. Revisões de arquitetura e requisitos são tão importantes quanto testes.

### Princípio 03 – Revisão Independente (Quatro Olhos)
Todo artefato crítico (arquitetura, design, mudança estrutural, contrato de API) deve ser revisado por pelo menos uma pessoa que não participou de sua criação. A revisão pelo autor não é suficiente.

### Princípio 04 – Qualidade como Processo Contínuo
A qualidade não é uma fase (ex: "fase de testes"). Deve ser incorporada em cada etapa do pipeline de CI/CD (ex: linting, testes unitários, testes de integração, quality gates).

### Princípio 05 – Dívida Técnica como Dívida Financeira
Dívida técnica deve ser rastreada, priorizada e "paga" (refatorada) como qualquer dívida financeira. Se não for paga, os juros (custos de manutenção) crescem exponencialmente.

### Princípio 06 – Evidência de Qualidade
A qualidade não é uma percepção; é um estado demonstrável por evidências (relatórios de teste, métricas, registros de revisão). O agente deve sempre exigir e produzir evidências de qualidade.
