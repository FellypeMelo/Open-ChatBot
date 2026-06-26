# Seção 3 – Regras de Elicitação e Scoping / Layer 3 (Layer 3 - Requisitos)

**ID:** ARCH-RULESET-L3-REQ-ELICIT  
**Status:** Definitivo  
**Escopo:** Métodos formais e restrições para descoberta e controle inicial de requisitos.

---

### REGREQ-001 – Obrigação de Identificação do Stakeholder Originário

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-001 |
| **Nome** | Obrigação de Identificação do Stakeholder Originário |
| **Descrição** | Todo requisito deve ser atribuído a pelo menos um stakeholder específico (pessoa, papel ou organização) que seja a fonte legítima daquele requisito. O agente não pode aceitar um requisito sem que o stakeholder seja identificado. Se o stakeholder não for conhecido, o agente deve perguntar explicitamente: "Quem é o dono/originador deste requisito?" |
| **Objetivo** | Garantir que todo requisito tenha um "dono" responsável por sua validação e comprometimento. |
| **Motivação** | Cap. 4.2.1 (atores na comunidade de desenvolvimento), Cap. 7.4.6 (seleção de stakeholders para comprometimento). |
| **Justificativa** | Requisitos sem dono viram "problema de todo mundo e de ninguém", ficam órfãos e nunca são validados corretamente. |
| **Critérios de Aplicação** | Na criação ou importação de qualquer requisito. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | O requisito deve estar sendo definido. |
| **Pós-condições** | O requisito possui o campo `Stakeholder_Originario` preenchido. |
| **Restrições** | Um stakeholder pode ser um grupo (ex: "Comitê de Segurança"), mas deve ser um grupo identificável e com um representante formal. |
| **Dependências** | REGCON-001, REGCORE-002. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "RN-012 (Classificar variante classe 5): Stakeholder Originário = Dr. João Silva (Coordenador de Genômica)." |
| **Exemplo Negativo** | "RN-012: O sistema deve classificar variantes." (sem stakeholder). |
| **Anti-pattern** | Atribuir o stakeholder como "Usuário" ou "Cliente" sem especificar qual pessoa ou papel. |
| **Métrica** | Percentual de requisitos com stakeholder preenchido (meta: 100%). |
| **Critérios de Auditoria** | Auditoria de todos os requisitos: se algum não tiver stakeholder, falha. |

---

### REGREQ-002 – Aplicação das Técnicas de Conversação por Objetivo

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-002 |
| **Nome** | Aplicação das Técnicas de Conversação por Objetivo (Tabela 4.1) |
| **Descrição** | O agente deve recomendar e aplicar a técnica de conversação adequada ao estágio do requisito, conforme a Tabela 4.1 do Capítulo 4: **Introduzir** (Brown-paper, Elicitação), **Concordar** (Workshop, Validação), **Comprometer** (Committing Review). O agente não pode usar uma técnica inadequada para o estágio (ex: validar um requisito complexo por e-mail). |
| **Objetivo** | Maximizar a eficácia da comunicação com stakeholders, usando a técnica certa para o momento certo. |
| **Motivação** | Cap. 4.4.2, Tabela 4.1. |
| **Justificativa** | Elicitação requer abertura (entrevista); validação requer estrutura (workshop); comprometimento requer formalidade (revisão com decisão). Usar a técnica errada gera feedback ineficaz ou comprometimento falso. |
| **Critérios de Aplicação** | Em todo processo de requisitos que envolva interação com stakeholders. |
| **Critérios de Não Aplicação** | Nenhum. |
| **Pré-condições** | O agente deve conhecer o estágio do requisito (novo, em revisão, em decisão). |
| **Pós-condições** | A técnica recomendada é documentada no plano de trabalho. |
| **Restrições** | Se o stakeholder insistir em uma técnica inadequada (ex: validar por e-mail), o agente deve sinalizar o risco de validação ineficaz. |
| **Dependências** | REGREQ-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "Para elicitar os novos requisitos de integração com o sistema legado, recomendo uma sessão de brown-paper com os arquitetos de ambos os sistemas. Para validar a consistência, um workshop. Para o comprometimento formal, uma committing review com os POs." |
| **Exemplo Negativo** | "Vamos enviar os requisitos de integração por e-mail para todos aprovarem." |
| **Anti-pattern** | Usar a mesma técnica (ex: reunião semanal) para todos os estágios, diluindo a eficácia. |
| **Métrica** | Número de requisitos validados com técnica adequada vs. total. |
| **Critérios de Auditoria** | Revisar o histórico de validação para verificar se a técnica foi apropriada ao estágio. |

---

### REGREQ-003 – Regra das 4 Direções Metafóricas para Descoberta de Requisitos

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGREQ-003 |
| **Nome** | Regra das 4 Direções Metafóricas para Descoberta de Requisitos |
| **Descrição** | Ao analisar um requisito ou funcionalidade, o agente deve sistematicamente explorar as quatro direções metafóricas para garantir a cobertura completa: **(1) Inwards**: o que compõe este requisito? (sub-requisitos, detalhes); **(2) Upwards**: o que este requisito suporta? (requisitos de nível superior, produtos, serviços); **(3) Downwards**: como este requisito é realizado? (componentes, serviços, dados, infraestrutura); **(4) Sideways**: com o que este requisito coopera? (requisitos relacionados, interfaces, fluxos de informação). |
| **Objetivo** | Garantir cobertura completa e evitar lacunas de requisitos em todas as direções da arquitetura. |
| **Motivação** | Cap. 6.3.2 e Cap. 7.5 – uso das direções metafóricas para identificar elementos relevantes. |
| **Justificativa** | A maioria dos requisitos perdidos está em relações "sideways" (cooperação) ou "downwards" (realização). Explorar as quatro direções sistematicamente reduz drasticamente as lacunas. |
| **Critérios de Aplicação** | Durante a elicitação e análise de qualquer requisito funcional (RN) ou restrição (RT). |
| **Critérios de Não Aplicação** | Requisitos de nível único e isolado (ex: "sistema deve ter relógio") – raros. |
| **Pré-condições** | Requisito central identificado. |
| **Pós-condições** | Pelo menos um requisito relacionado em cada direção foi identificado ou uma justificativa para a ausência foi documentada. |
| **Restrições** | A exploração deve ser documentada na matriz de rastreabilidade. |
| **Dependências** | REGREQ-001. |
| **Prioridade** | **Alta** |
| **Severidade** | **Crítica** |
| **Exemplo Positivo** | "RN-010 (Processar FASTQ): Inwards → validação de formato, extração de metadados. Upwards → suporta a RN-005 (Classificação ACMG). Downwards → utiliza serviço de armazenamento S3 (RT-023) e processamento assíncrono (RT-045). Sideways → coopera com o serviço de notificação (RN-099) e com o módulo de filas (RT-101)." |
| **Exemplo Negativo** | "RN-010: Processar FASTQ." (sem explorar relações). |
| **Anti-pattern** | Explorar apenas a direção "downwards" (implementação) e ignorar "upwards" (valor de negócio). |
| **Métrica** | Número de relacionamentos documentados por requisito vs. número esperado (mínimo 3). |
| **Critérios de Auditoria** | Revisar amostra de requisitos: se algum não tiver relacionamentos em pelo menos 3 direções, falha. |
