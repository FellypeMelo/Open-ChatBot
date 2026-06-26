# Seção 7 – Auditoria, Exemplo Integrado e Evolução / Layer 3 (Layer 3 - Requisitos)

**ID:** ARCH-RULESET-L3-REQ-AUDIT-EXAMPLE  
**Status:** Definitivo  
**Escopo:** Métodos de validação de auditoria, caso de uso prático e regras de evolução de Engenharia de Requisitos.

---

## 1. Critérios de Auditoria da Engenharia de Requisitos

| ID | Critério de Auditoria | Método de Verificação |
| :--- | :--- | :--- |
| AUD-REQ-01 | Todo requisito tem stakeholder originário (REGREQ-001). | Verificar campo `Stakeholder_Originario`. |
| AUD-REQ-02 | Requisitos não-funcionais têm critérios SMART (REGREQ-005). | Confirmar a presença de métricas e limites testáveis. |
| AUD-REQ-03 | Nenhum requisito mistura categorias (REGREQ-006). | Validar se o requisito foi desmembrado caso houvesse múltiplas categorias. |
| AUD-REQ-04 | Todo requisito tem Rationale (REGREQ-007). | Garantir o preenchimento do campo com justificação do porquê. |
| AUD-REQ-05 | Requisitos complexos foram validados de forma síncrona (REGREQ-009). | Verificar o histórico/atas de workshops e reuniões ativas. |
| AUD-REQ-06 | Matriz de rastreabilidade está atualizada (REGREQ-011). | Checagem de links bidirecionais (Origem ↔ Componente ↔ Teste). |
| AUD-REQ-07 | Não há ciclos na matriz de rastreabilidade (REGREQ-012). | Análise de grafo acíclico. |
| AUD-REQ-08 | Comprometimento formal registrado para requisitos aprovados (REGREQ-008). | Validar a presença da assinatura do PO no campo comprometimento. |
| AUD-REQ-09 | Técnica de conversação adequada usada em cada estágio (REGREQ-002). | Validar adequação com a Tabela 4.1. |
| AUD-REQ-10 | Conflitos irresolvíveis foram escalados (REGREQ-010). | Verificar atas do Comitê de Arquitetura. |

---

## 2. Exemplo Integrado de Aplicação do Módulo 03

**Cenário:** O agente recebe a seguinte entrada do usuário: *"Precisamos de um sistema que processe arquivos FASTQ de forma segura e rápida, e que classifique as variantes conforme ACMG."*

**Raciocínio Aplicado Passo a Passo:**
1. **REGRSN-001 (Socrático):** Identifica termos vagos ("segura", "rápida") e uma mistura de objetivos na mesma frase.
2. **REGREQ-006 (Proibição de Requisitos Mistos):** Desmembra o requisito bruto em 4 partes bem definidas:
   * **RN-010:** Processar arquivos FASTQ (Regra de Negócio).
   * **PS-001:** Criptografar tráfego e impor RBAC (Política de Segurança).
   * **RT-023:** SLA de processamento de arquivos FASTQ de 10GB em até 5min (Restrição Técnica).
   * **RN-042:** Classificar variantes em lote conforme ACMG (Regra de Negócio).
3. **REGREQ-001 (Identificação de Stakeholders):**
   * RN-010 e RN-042 → Originados pelo Dr. Carlos (Chefe de Genética).
   * RT-023 → SRE (João).
   * PS-001 → Security Officer (Ana).
4. **REGREQ-005 (Métricas SMART para RT-023):** "O processamento de 95% dos arquivos FASTQ de até 10GB deve ocorrer em menos de 5 minutos utilizando infraestrutura com 4 workers paralelos em ambiente produtivo."
5. **REGREQ-003 (As 4 Direções Metafóricas):**
   * *Inwards (Interno):* RN-010 requer validação e extração de checksum.
   * *Upwards (Negócio):* RN-042 suporta a emissão de laudo genético.
   * *Downwards (Tecnologia):* Utiliza infraestrutura de filas (RT-045).
   * *Sideways (Interface):* Cooperação direta com o barramento de eventos (RT-101) e notificações (RN-099).
6. **REGREQ-011 (Matriz de Rastreabilidade):**
   Mapeado: `RN-042` → `RF-10` (Automação ACMG) → `VariantClassifier` (Código Go) → `Test_ACMG_Classifier_L5` (Teste unitário Go).

---

## 3. Evolução e Extensibilidade

Este módulo pode ser estendido através de sub-módulos focados em:
* **Módulo 03-A (Change Control):** Governança para mudanças de requisitos.
* **Módulo 03-B (Safety Critical):** Engenharia de requisitos específicos para normas clínicas rigorosas (ANVISA, FDA).
* **Módulo 03-C (Legacy Integration):** Mapeamento de interfaces com sistemas legados Hospitalares (HL7/FHIR).
