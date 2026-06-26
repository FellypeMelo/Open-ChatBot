# Seção 1 – Glossário Formal e Taxonomia (Layer 3 - Requisitos)

**ID:** ARCH-RULESET-L3-REQ-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Terminologia canônica baseada na ISO/IEC 29148 para Engenharia de Requisitos.

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **Requisito** | Declaração formal de uma capacidade, condição ou restrição que um sistema deve atender. Divide-se em quatro categorias obrigatórias: **RN** (Regra de Negócio), **PS** (Política de Segurança), **LGPD** (Requisito de Privacidade e Conformidade) e **RT** (Restrição Técnica/Arquitetural). | Cap. 5, 6, 9 |
| **Elicitação** | Processo ativo de descoberta de requisitos junto a stakeholders, utilizando técnicas como entrevistas, workshops, análise de documentos e observação. O agente nunca deve "inventar" requisitos. | Cap. 4.2.1, 4.2.2 |
| **Especificação** | Ato de documentar o requisito em linguagem formal ou semiforme, com estrutura padronizada, eliminando ambiguidades e definindo critérios de aceitação objetivos. | Cap. 6.3.2 |
| **Validação de Conteúdo** | Verificação de que o requisito especificado está **correto** do ponto de vista do domínio e do stakeholder, ou seja, representa fielmente a necessidade real. | Cap. 7.4.5 |
| **Comprometimento (Commitment)** | Estado em que o stakeholder não apenas concorda com o conteúdo do requisito, mas assume formalmente a responsabilidade por sua aprovação e pelas implicações (custos, riscos, mudanças). | Cap. 4.2.4, Cap. 7.4.6 |
| **Rastreabilidade** | Capacidade de rastrear um requisito bidirecionalmente: (1) **Forward** → para os componentes, serviços e artefatos que o implementam; (2) **Backward** → para a origem (stakeholder, norma, driver). | Cap. 8.3.1, Cap. 9.2.2 |
| **Matriz de Rastreabilidade** | Artefato formal que mapeia a relação entre requisitos e outros elements do sistema (RFs, componentes, testes). Deve ser mantida viva e atualizada a cada mudança. | Cap. 8.3.1 |
| **Critério de Aceitação (Acceptance Criteria)** | Conjunto de condições que devem ser satisfeitas para que um requisito seja considerado implementado corretamente. Devem ser objetivas, mensuráveis e testáveis. | Cap. 6.4, Cap. 7 |
| **Regra de Negócio (RN)** | Requisito que expressa uma política, condição ou restrição do domínio do negócio. É independente de tecnologia e deve permanecer estável ao longo do tempo. Ex: "Variantes classe 5 devem ser classificadas como patogênicas." | Cap. 5.4.3 |
| **Política de Segurança (PS)** | Requisito que expressa controles de acesso, criptografia, autenticação, autorização, proteção contra ataques e gestão de identidade. É derivada de normas como OWASP, NIST e políticas internas. | Cap. 1.4.2, Cap. 7.5.16 |
| **Requisito de Conformidade/Privacidade (LGPD)** | Requisito que expressa obrigações legais e regulatórias relacionadas à proteção de dados pessoais, privacidade, retenção, expurgo e consentimento. É derivado da LGPD, GDPR e normativos setoriais. | Cap. 1.4.2 |
| **Restrição Técnica (RT)** | Requisito não-funcional que impõe limites operacionais, arquiteturais ou tecnológicos ao sistema. Ex: tamanho máximo de arquivo, tempo de resposta máximo, throughput mínimo, tecnologia obrigatória. | Cap. 5.6, Cap. 8.2 |
| **Stakeholder** | Indivíduo, equipe ou organização com interesses ou preocupações relativas ao sistema. Na engenharia de requisitos, todo requisito deve ter pelo menos um stakeholder identificado como originário. | IEEE 1471 / Cap. 1 |
| **Premissa (Assumption)** | Fato considerado verdadeiro para fins de raciocínio, mas que ainda não foi validado com evidência. Toda premissa deve ser explicitamente rotulada como `[PREMISSA]` e associada a um plano de validação. | Cap. 4.2.3, Cap. 6.3.5 |
| **Derivação** | Relação entre requisitos onde um requisito é derivado de outro (ex: um RT derivado de uma RN). Deve ser documentada na matriz de rastreabilidade. | Cap. 5.7, Cap. 8.3.1 |
