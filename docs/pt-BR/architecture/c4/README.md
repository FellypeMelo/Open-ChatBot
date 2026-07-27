# Modelo C4

Diagramas de aprofundamento (Contexto, Container, Componente).

## Contexto
O Diagrama de Contexto representa as interações entre o Usuário, a UI, o Backend, o banco de dados local e o Motor de IA.

![Diagrama de Contexto](../../../en/architecture/c4/dp_local_openchatbot.puml)

## Container
O Diagrama de Container ilustra os componentes macro do Open-ChatBot.

- **Frontend React**: Interface principal.
- **Backend FastAPI**: Orquestração de lógica, transições de estado, exposição de API.
- **Banco de Dados SQLite**: Armazenamento relacional para chats, estados, perfis de usuário.
- **Subsistemas de LLM**: `llama-server.exe` servindo inferência & embeddings.

## Componente
As fronteiras de componente giram em torno dos routers (Chat, Characters, Tags, Settings, Users) e do motor central (LlamaClient, DB).
