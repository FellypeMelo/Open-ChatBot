# Seção 2 – Princípios Fundamentais da Engenharia de Requisitos (Layer 3)

**ID:** ARCH-RULESET-L3-REQ-PRINCIPLES  
**Status:** Definitivo  
**Escopo:** Diretrizes filosóficas de qualidade em elicitação e especificação.

### Princípio 01 – Origem Obrigatória (No Orphan Requirements)
Todo requisito deve ter uma origem documentada (stakeholder, norma, ou driver estratégico). Requisitos sem origem são "órfãos" e devem ser imediatamente questionados ou descartados.

### Princípio 02 – Ambiguidade Zero
Nenhum requisito pode conter termos vagos (ex: "rápido", "seguro", "fácil", "adequado") sem uma definição quantitativa ou qualitativa objetiva. Ambiguidade é o maior inimigo da engenharia de requisitos.

### Princípio 03 – Separação por Categoria (RN/PS/LGPD/RT)
Cada requisito deve pertencer a exatamente uma das quatro categorias canônicas. A mistura de categorias em uma única declaração é proibida e deve ser desmembrada. Ex: "O sistema deve ser seguro e processar arquivos FASTQ" → PS-001 (seguro) + RN-010 (processar FASTQ).

### Princípio 04 – Rastreabilidade como Ativo
A rastreabilidade não é uma atividade opcional ou "boa prática"; é um **ativo arquitetural obrigatório**. Sem rastreabilidade, a arquitetura é cega a mudanças e riscos.

### Princípio 05 – Validação Antes da Especificação Detalhada
Nunca especifique em detalhe um requisito antes de validar seu escopo e conteúdo com os stakeholders. Especificar o requisito errado em detalhes é pior do que não especificar nada.

### Princípio 06 – Comprometimento é a Linha de Chegada
Um requisito só está "pronto" quando o stakeholder se compromete formalmente com ele. O mero "entendimento" ou "concordância informal" não é suficiente para iniciar a implementação.
