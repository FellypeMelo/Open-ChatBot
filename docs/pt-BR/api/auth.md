# Modelo de Autenticação e Segurança da API

## 1. Estado Atual: Single-Tenant / Execução Local
O Open-ChatBot é atualmente implementado como uma **aplicação local single-tenant**.

* **Sem Middleware de Autenticação:** Os endpoints da API (`/chat`, `/characters`, etc.) não aplicam atualmente verificação de JWT, OAuth2 ou cookie de sessão.
* **Provisionamento Automático de Usuário:** O backend registra/gerencia dinamicamente um único usuário ativo no banco SQLite (`chatbot.db`) através do endpoint `/users/me`. Veja [users.py](../../../src/backend/api/users.py) para detalhes de implementação.
* **Segurança por Isolamento de Rede:** A aplicação se vincula a `localhost` por padrão. Não há mecanismo de controle de acesso na camada de aplicação; o modelo de segurança depende inteiramente da fronteira do sistema da máquina local e do isolamento da interface de loopback.

## 2. Recomendações para Implantações Multi-Tenant / Produção
Para expandir esta plataforma para implantações externas ou em nuvem, os seguintes protocolos de autenticação precisam ser implementados:
1. **Tokens OAuth2 / JWT Bearer:** Envolver as rotas da API com escopos `Security` do FastAPI.
2. **Separação de Contexto de Usuário:** Atualizar o helper `get_me()` para extrair o contexto do usuário a partir do payload do JWT, em vez de consultar o primeiro usuário ativo padrão.
3. **Configuração de CORS:** Configurar políticas restritivas de CORS para permitir requisições apenas de origens autorizadas.
