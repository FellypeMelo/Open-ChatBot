# Confiabilidade e Operações de Sistema (SRE)

O Open-ChatBot opera como um serviço local, com práticas específicas de confiabilidade, verificação de saúde e otimização implementadas diretamente dentro do ciclo de vida da aplicação.

## 1. Gerenciamento de Processos e Serviços Locais
A aplicação FastAPI atua como o gerenciador de processos para os motores de IA.
*   **Auto-Orquestração:** Ao iniciar, o backend lê a configuração de `models_config.json` e invoca o [LlamaServerRunner](../../../src/backend/core/engine/runner.py) para subir uma única instância unificada do `llama-server.exe`.
*   **Modo de Servidor Consolidado:** Por padrão, tanto a inferência quanto os embeddings usam o mesmo modelo e compartilham a porta `8080`. O runner detecta isso automaticamente e lança apenas um processo `llama-server.exe` com a flag `--embedding` habilitada para cobrir os dois papéis, economizando significativamente alocações de VRAM/RAM.
*   **Hook de Desligamento no Lifespan:** Quando a instância do FastAPI é parada, ela chama `runner.stop_all()` para encerrar a instância `llama-server.exe` rodando em background, evitando processos zumbis. Veja [main.py](../../../src/backend/main.py).

## 2. Monitoramento e Verificação de Saúde
*   **Verificação na Inicialização:** Durante a inicialização da aplicação, o servidor executa health checks de embedding e inferência via [LlamaClient](../../../src/backend/core/engine/llm.py).
*   **Contingência de Estado Degradado:** Se o servidor de embedding estiver inalcançável, o sistema grava um log `WARNING` e continua rodando em um estado degradado, com as features de recuperação de memória desabilitadas, prevenindo uma falha completa da aplicação.

## 3. Confiabilidade e Otimizações de Armazenamento
*   **Vacuuming do SQLite:** Na inicialização, o backend chama `vacuum_db()`, que executa o comando SQL `VACUUM` de forma assíncrona. Isso reduz a fragmentação em disco e recupera espaço não usado do banco de dados, garantindo a saúde do sistema de arquivos no longo prazo. Veja [database.py](../../../src/backend/db/database.py).
*   **Largura de Bits do Vector Database:** Para gerenciar as restrições de performance em hardware de consumo local, o índice do vector database TurboQuant usa uma **largura de quantização de 4 bits** (`bit_width=4`) para armazenar embeddings, reduzindo a utilização de RAM e acelerando as buscas por similaridade de cosseno. Veja [vector_store.py](../../../src/backend/core/memory/vector_store.py).

## 4. Logs de Troubleshooting
Os logs padrão da aplicação são capturados pelo módulo `logging` do Python. Os tempos de requisição em tempo real são opcionalmente medidos (se `settings.DEBUG_LATENCY` estiver habilitado) para logar gargalos de latência passo a passo.
