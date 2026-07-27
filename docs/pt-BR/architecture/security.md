# Arquitetura de Segurança

O Open-ChatBot implementa um modelo de arquitetura "Privacy-by-Design" otimizado para execução local e offline.

## 1. Modelagem de Ameaças (Análise STRIDE)
*   **Spoofing:** O risco é mitigado por rodar como um serviço local single-user.
*   **Tampering:** O arquivo de banco de dados SQLite local (`chatbot.db`) é protegido pelas permissões de controle de acesso do sistema de arquivos do usuário do sistema operacional.
*   **Repudiation:** Verificado via log de auditoria em nível de aplicação. Todas as requisições de inferência gravam rastros de auditoria contendo valores `request_id` UUID únicos.
*   **Information Disclosure:** O risco é extremamente baixo porque os dados nunca atravessam redes externas. Nenhuma API de LLM em nuvem é usada (toda a geração passa por uma instância local `llama-server.exe` em loopback).
*   **Denial of Service:** O loop de inferência bloqueia recursos de computação locais. Para prevenir esgotamento de recursos, os processos de execução são restritos às limitações de memória do dispositivo local.
*   **Elevation of Privilege:** O processo do backend executa sob o contexto de segurança do usuário que iniciou o script `run.bat`.

## 2. Autenticação e Autorização
Atualmente, não há autenticação de sessão (JWT/OAuth) na camada de API porque o sistema opera em um ambiente local single-tenant (vinculado ao loopback `127.0.0.1`). Se for necessária a implantação em redes externas, a autenticação deve ser adicionada à camada FastAPI. Consulte [auth.md](../api/auth.md) para diretrizes de recomendação.

## 3. Proteção de Dados
*   **Proteção via ORM:** As interações com o banco de dados são mediadas por schemas do ORM SQLAlchemy, prevenindo vulnerabilidades de SQL injection.
*   **Segurança do Vector Database:** Os vector databases locais residem dentro de `./chroma_db/` usando arquivos binários padrão, sem exposição de rede.
*   **Limites de Segurança:** Os limites de inferência são restringidos pelas alocações de parâmetros do `models_config.json` local.
*   **Sanitização:** Os diálogos são renderizados como texto bruto, mas as diretrizes de segurança determinam que os templates de prompt impedem que personagens produzam comandos de injeção de shell.
