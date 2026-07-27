# Visão Geral de Arquitetura

Design de sistema de alto nível para o Open-ChatBot.

## Drivers de Arquitetura
1. **Execução Local e Privacidade**: O sistema roda inteiramente local, sem dependências de modelos em nuvem, para garantir privacidade máxima. Usa um servidor `llama.cpp` consolidado local.
2. **Modularidade e Agentes com Estado**: Os personagens de IA têm estado dedicado (humor, energia, relacionamento, localização), habilitando role-play dinâmico e memórias persistentes.
3. **Responsividade e Estética**: Frontend React/Vite de alto padrão com Tailwind CSS garantindo uma interface elegante, anti-slop, rápida e responsiva para mobile.
4. **Testabilidade e Manutenibilidade**: Aplicação estrita de >80% de cobertura de código, arquitetura desacoplada usando FastAPI e SQLAlchemy.

## Arquitetura do Sistema
O Open-ChatBot opera como uma aplicação monolítica local com unidades funcionais desacopladas. Consiste em:
- **SPA Frontend**: React, TypeScript, Vite, Tailwind CSS. Servido estaticamente em produção ou via Vite em desenvolvimento.
- **API Backend**: Python FastAPI fornecendo rotas RESTful.
- **Banco de Dados**: SQLite (`chatbot.db`) gerenciado via ORM SQLAlchemy.
- **Núcleo de IA (Llama-Server Consolidado)**: Um único processo em background rodando `llama-server.exe` com a flag `--embedding` habilitada, servindo tanto completions quanto geração de embeddings (RAG) em uma única porta (padrão 8080), economizando uma quantidade significativa de RAM/VRAM.

## Componentes-Chave
- **LlamaClient**: Uma interface Python que orquestra requisições HTTP para o único servidor `llama.cpp` local, tanto para completion quanto para geração de embeddings.
- **Engine Runner**: O script central (`src/backend/core/engine/runner.py`) responsável por subir e derrubar o subprocesso único do servidor `llama.cpp` dinamicamente.
- **Árvore de Mensagens (Nodes)**: As mensagens são armazenadas como uma árvore (`MessageNode`), permitindo ramificação e caminhos alternativos de geração.
- **AgentState**: Um modelo altamente detalhado representando as condições ao vivo (ex.: felicidade, fome, roupas, localização) do Personagem.
