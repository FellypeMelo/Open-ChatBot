# Seção 1 – Glossário Formal e Taxonomia (Layer 0)

**ID:** ARCH-RULESET-L0-GLOSSARY  
**Status:** Imutável  
**Escopo:** Definições conceituais canônicas para alinhamento semântico.

Todo termo técnico utilizado neste Ruleset obedece à seguinte definição canônica, extraída do IEEE 1471-2000 e do Capítulo 3 do livro-base.

| Termo | Definição Canônica (Obrigatória) | Fonte |
| :--- | :--- | :--- |
| **Arquitetura** | Organização fundamental de um sistema, incorporada em seus componentes, seus relacionamentos entre si e com o ambiente, e os princípios que orientam seu projeto e evolução. | IEEE 1471 / Cap. 1 |
| **Sistema** | Conjunto coerente de elementos cuja coerência produz valor agregado para seu ambiente. Pode ser social, simbólico (software) ou físico. | Cap. 9.2.1 |
| **Stakeholder** | Indivíduo, equipe ou organização (ou classes deles) com interesses ou preocupações relativas a um sistema. | IEEE 1471 / Cap. 1 |
| **Preocupação (Concern)** | Interesse de um stakeholder com relação à descrição da arquitetura, resultante de seus objetivos e do papel presente ou futuro do sistema em relação a esses objetivos. | Cap. 4.2.1 |
| **Modelo** | Concepção propositalmente abstraída e inequívoca de um domínio. Divide-se em **Modelo Simbólico** (sintaxe, signos, estrutura) e **Modelo Semântico** (interpretação formal, significado matemático). | Cap. 3.3.1 |
| **Visão (View)** | Representação de um sistema a partir da perspectiva de um conjunto relacionado de preocupações. É o que se vê. | IEEE 1471 / Cap. 3.2.4 |
| **Ponto de Vista (Viewpoint)** | Especificação das convenções para construir e usar uma visão: um padrão ou modelo a partir do qual desenvolver visões individuais, estabelecendo o propósito, o público e as técnicas para sua criação e análise. É de onde se olha. | IEEE 1471 / Cap. 3.2.4 |
| **Requisito** | Declaração formal de uma capacidade, condição ou restrição que um sistema deve atender. Divide-se em quatro categorias obrigatórias: **RN** (Regra de Negócio), **PS** (Política de Segurança), **LGPD** (Requisito de Privacidade e Conformidade) e **RT** (Restrição Técnica/Arquitetural). | Cap. 5, 6, 9 |
| **Assinatura (Signature)** | Núcleo de todo modelo simbólico. Categoriza as entidades em *sorts* (tipos) e declara relações e operações entre elas. É o glossário conceitual do sistema. | Cap. 3.3.2 |
| **Serviço** | Unidade de funcionalidade que uma entidade disponibiliza ao seu ambiente, possuindo valor para as entidades desse ambiente. É a ponte entre o comportamento externo (contrato) e a realização interna (implementação). | Cap. 5.2 |
| **Camada (Layer)** | Mecanismo de estruturação que separa preocupações por nível de abstração e estabilidade. As camadas fundamentais são: **Negócio** (estável), **Aplicação** (semiestável) e **Tecnologia** (mutável). | Cap. 5.2 |
