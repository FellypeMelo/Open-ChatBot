# Seção 5 – Regras de Criptografia e Proteção de Dados (Layer 5 - Compliance, Segurança e Privacidade)

**ID:** ARCH-RULESET-L5-SEC-CRYPTO  
**Status:** Definitivo  
**Escopo:** Requisitos de cifragem em trânsito e em repouso de acordo com padrões internacionais de criptografia.

---

### REGSEC-005 – Criptografia em Trânsito Obrigatória (TLS 1.3+)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-005 |
| **Nome** | Criptografia em Trânsito Obrigatória (TLS 1.3+) |
| **Descrição** | Toda comunicação entre sistemas, serviços, ou entre cliente e servidor deve ser criptografada usando TLS (Transport Layer Security) na versão 1.3 ou superior. Protocolos obsoletos e inseguros (ex: TLS 1.0, SSL v3, HTTP sem TLS) são proibidos. A configuração do TLS deve usar conjuntos de cifras seguros (ex: excluir cipher suites vulneráveis como RC4, 3DES, e aquelas com chaves < 2048 bits para RSA) e verificação de certificados (não deve permitir certificados autoassinados em produção). |
| **Objetivo** | Garantir confidencialidade e integridade dos dados durante a transmissão, prevenindo ataques de interceptação (man-in-the-middle), sniffing e adulteração. |
| **Motivação** | Cap. 5.6.2 (comunicação como serviço de infraestrutura), OWASP (Transport Layer Protection). |
| **Justificativa** | Dados em trânsito são altamente vulneráveis a interceptação, especialmente em redes públicas ou ambientes de nuvem. TLS 1.3 é o padrão moderno e seguro. |
| **Critérios de Aplicação** | Toda comunicação em rede (HTTP, gRPC, WebSocket, SMTP, JDBC, Kafka, etc.). |
| **Critérios de Não Aplicação** | Comunicação dentro do mesmo processo (ex: chamada de método entre classes) e comunicação em redes totalmente isoladas e fisicamente seguras (ex: backplane de hardware, com justificativa aprovada). |
| **Pré-condições** | Certificados digitais válidos (ex: Let's Encrypt, CA corporativa). |
| **Pós-condições** | Nenhuma requisição não criptografada é aceita. |
| **Restrições** | O agente deve alertar sobre o uso de TLS 1.2 (que está em depreciação) e exigir um plano de migração para TLS 1.3. |
| **Dependências** | REGSEC-001. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Todos os endpoints da API utilizam HTTPS com TLS 1.3 e cipher suite `TLS_AES_256_GCM_SHA384`." |
| **Exemplo Negativo** | "Endpoint HTTP exposto para comunicação interna." |
| **Anti-pattern** | Desabilitar a verificação de certificados (ex: `-k` no curl) para "facilitar" testes em produção. |
| **Métrica** | Percentual de tráfego interno e externo criptografado com TLS 1.3 (meta: 100%). |
| **Critérios de Auditoria** | Scan de rede para detectar portas HTTP ou TLS < 1.3. |

---

### REGSEC-006 – Criptografia em Repouso Obrigatória (AES-256 ou Equivalente)

| Campo | Conteúdo |
| :--- | :--- |
| **ID** | REGSEC-006 |
| **Nome** | Criptografia em Repouso Obrigatória (AES-256 ou Equivalente) |
| **Descrição** | Todos os dados persistentes (bancos de dados, arquivos, backups, snapshots, logs) que contenham dados classificados como **CONFIDENCIAL ou RESTRITO** devem ser criptografados em repouso utilizando um algoritmo forte e aprovado, como AES-256 (GCM ou CBC com HMAC), ou equivalentes (ex: ChaCha20-Poly1305). As chaves de criptografia devem ser gerenciadas por um serviço centralizado de gerenciamento de chaves (ex: AWS KMS, HashiCorp Vault, Azure Key Vault) e não devem ser armazenadas junto com os dados. A rotação de chaves deve ser periódica (ex: anual). |
| **Objetivo** | Proteger dados em caso de roubo físico de dispositivos, comprometimento de snapshots ou acesso não autorizado a discos. |
| **Motivação** | Cap. 5.6.2 (armazenamento como serviço de infraestrutura), LGPD (Art. 46 – medidas técnicas para proteger dados). |
| **Justificativa** | Criptografia em repouso é a última linha de defesa. Se um invasor obtiver acesso ao disco ou backup, os dados permanecem ilegíveis sem as chaves. |
| **Critérios de Aplicação** | Bancos de dados (RDS, Postgres, MySQL), buckets S3, discos EBS, arquivos de configuração com credenciais, backups. |
| **Critérios de Não Aplicação** | Dados temporários em memória (desde que não persistam) e dados públicos que não requerem confidencialidade. |
| **Pré-condições** | Serviço de gerenciamento de chaves (KMS) configurado. |
| **Pós-condições** | Todos os dados persistentes classificados como CONFIDENCIAL/RESTRITO estão criptografados. |
| **Restrições** | O agente deve garantir que as chaves sejam rotacionadas automaticamente e que o acesso às chaves seja rigorosamente controlado e auditado. |
| **Dependências** | REGSEC-001, REGSEC-002. |
| **Prioridade** | **Crítica** |
| **Severidade** | **Bloqueante** |
| **Exemplo Positivo** | "Banco de dados `genomics-db` configurado com criptografia AES-256 usando AWS KMS (chave gerenciada pelo cliente). Snapshots criptografados." |
| **Exemplo Negativo** | "Bucket S3 com dados genômicos armazenados em texto puro." |
| **Anti-pattern** | Armazenar a chave de criptografia em um arquivo de configuração no mesmo bucket. |
| **Métrica** | Percentual de dados persistentes criptografados (meta: 100%). |
| **Critérios de Auditoria** | Revisar configurações de armazenamento para verificar criptografia ativa. |
