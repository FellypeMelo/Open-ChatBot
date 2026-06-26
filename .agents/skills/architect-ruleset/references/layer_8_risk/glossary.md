# Seção 1 – Glossário Formal (Layer 8 - Análise de Riscos e Decisão Arquitetural)

**ID:** ARCH-RULESET-L8-RISK-GLOSSARY  
**Status:** Definitivo  
**Escopo:** Terminologia canônica de análise de riscos, modelagem financeira de incerteza (FAIR), e modos de falha estruturais (FMEA).

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **Risco** | Medida da possibilidade de um evento adverso ocorrer e seu impacto potencial. Risco = Probabilidade × Impacto (ou, em termos quantitativos, Expected Loss = Probability × Magnitude). | ISO 31000 / Cap. 8.2.1 |
| **Ameaça** | Agente, evento ou condição que pode causar dano a um sistema, dado ou processo. Ex: ataque cibernético, falha de hardware, erro humano. | NIST / Cap. 8.3.2 |
| **Vulnerabilidade** | Fraqueza em um sistema, processo ou controle que pode ser explorada por uma ameaça para causar danos. Ex: falta de criptografia, dependência de biblioteca desatualizada. | NIST / Cap. 8.3.2 |
| **Impacto** | Consequência negativa de um risco se materializar, expressa em termos financeiros, operacionais, reputacionais, regulatórios ou de segurança. | ISO 31000 / Cap. 8.2.1 |
| **Probabilidade** | Chance (0 a 1 ou 0% a 100%) de um risco se materializar dentro de um período definido (ex: anual). | ISO 31000 |
| **Matriz de Risco** | Ferramenta visual (geralmente 5x5 ou 3x3) que mapeia riscos com base em sua probabilidade e impacto, classificando-os em categorias: **Crítico**, **Alto**, **Médio**, **Baixo**. | ISO 31000 / Cap. 9.4.2 |
| **Mitigação** | Ação planejada para reduzir a probabilidade e/ou o impacto de um risco. Pode ser: **Evitar** (eliminar a causa), **Transferir** (ex: seguro, outsourcing), **Mitigar** (reduzir), **Aceitar** (reconhecer e conviver com o risco). | ISO 31000 / Cap. 9.4.2 |
| **FMEA (Failure Mode and Effects Analysis)** | Método estruturado para identificar modos de falha potenciais em um sistema, avaliar seu impacto e priorizar ações de mitigação com base no RPN (Risk Priority Number = Severidade × Ocorrência × Detecção). | Padrão da Indústria / Cap. 8.3.1 |
| **FAIR (Factor Analysis of Information Risk)** | Metodologia quantitativa para análise de risco cibernético, que modela riscos em termos de perda financeira esperada (Loss Magnitude) e frequência esperada (Threat Event Frequency). | Padrão da Indústria / Cap. 8.2.4 |
| **Tolerância a Risco** | Nível de risco que a organização está disposta a aceitar, com base em sua estratégia, apetite de risco e recursos disponíveis. | ISO 31000 / Cap. 1.4 |
| **Apetite de Risco** | Nível agregado de risco que a organização está disposta a assumir em busca de seus objetivos estratégicos. | ISO 31000 / Cap. 1.4 |
| **Decisão Baseada em Risco** | Processo de tomada de decisão que considera explicitamente os riscos associados a cada alternativa, comparando-os com os benefícios esperados e com a tolerância da organização. | Cap. 8.1, Cap. 9.4.2 |
| **Plano de Mitigação** | Documento formal que descreve as ações a serem tomadas para reduzir um risco, incluindo: responsável, cronograma, recursos necessários, métricas de sucesso e plano de contingência. | ISO 31000 / Cap. 9.4.2 |
| **Risk Owner** | Pessoa ou time responsável por gerenciar um risco específico, incluindo a implementação e monitoramento das ações de mitigação. | ISO 31000 / Cap. 9.4.2 |
| **Análise de Sensibilidade** | Técnica que avalia como a incerteza nos parâmetros de entrada (ex: probabilidade, impacto) afeta a decisão final, identificando quais premissas são mais críticas. | Cap. 8.2.4 |
| **Plano de Contingência** | Plano de ação a ser executado caso um risco se materialize, mesmo após as medidas de mitigação. É o "plano B". | ISO 31000 / Cap. 9.4.2 |
