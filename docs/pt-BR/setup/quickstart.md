# Setup e Início Rápido

Este documento consolida os passos de setup/execução que, de outra forma, ficam espalhados entre o `README.md` da raiz, `CLAUDE.md`/`GEMINI.md`, `run.sh`/`run.bat`, `.env.example` e `models_config.example.json`. Se algum desses arquivos e esta página divergirem, os arquivos do repositório são a fonte da verdade — esta página só os organiza em um único lugar.

## O que você precisa fornecer

O Open-ChatBot **não** vem com um modelo nem um motor de inferência embutido. Antes de qualquer coisa rodar, você precisa de:

* Um binário `llama-server` — do [llama.cpp](https://github.com/ggml-org/llama.cpp), ou o fork [llama-cpp-turboquant-SYCL](https://github.com/FellypeMelo/llama-cpp-turboquant-SYCL) do próprio autor, se você quiser o modo opcional de quantização de KV-cache de 2-4 bits (`turbo3`) em hardware Intel Arc/SYCL.
* Um arquivo de modelo GGUF de sua escolha.
* Python >= 3.10 (o CI está fixado em 3.11) e Node.js com o [`pnpm`](https://pnpm.io/) instalado globalmente. Este projeto usa `pnpm` exclusivamente para o frontend — `npm`/`yarn` não são workflows suportados.
* Opcional: drivers de aceleração de GPU para o seu build do `llama-server` (ex.: Intel oneAPI, CUDA). Os dois scripts de execução tentam carregar um ambiente Intel oneAPI (`setvars.bat`/`setvars.sh`) se ele existir, mas seguem em frente sem ele caso não esteja instalado.

## 1. Ambiente do backend

```bash
python -m venv venv
# Windows: venv\Scripts\activate  |  Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## 2. Dependências do frontend

```bash
cd src/frontend && pnpm install && cd ../..
```

## 3. Aponte a aplicação para o seu próprio modelo

Copie os dois arquivos de exemplo e edite-os:

```bash
cp .env.example .env
cp models_config.example.json models_config.json
```

`.env.example` (config de runtime do backend):

```
LLAMA_SERVER_URL=http://localhost:8080
DATABASE_URL=sqlite:///./chatbot.db
MODEL_PATH=models/your-model.gguf
```

`models_config.example.json` (a config do launcher do processo `llama-server` — seções de inference e embedding, tipicamente apontadas para o mesmo servidor/porta consolidados):

```json
{
  "inference": {
    "binary_path": "llama_bin/llama-server.exe",
    "model_path": "models/model.gguf",
    "port": 8080,
    "threads": 0,
    "gpu_layers": 99,
    "context_size": 65536,
    "additional_args": "--cache-type-k turbo3 --cache-type-v turbo3 --flash-attn on --parallel 1 --ubatch-size 2048"
  },
  "embedding": {
    "binary_path": "llama_bin/llama-server.exe",
    "model_path": "models/model.gguf",
    "port": 8080,
    "threads": 0,
    "gpu_layers": 99,
    "context_size": 65536,
    "additional_args": "--cache-type-k turbo3 --cache-type-v turbo3 --flash-attn on --parallel 1 --ubatch-size 2048"
  }
}
```

Edite os dois arquivos para apontar `MODEL_PATH` / `binary_path` / `model_path` para o seu próprio binário `llama-server` e arquivo `.gguf`. As flags de cache-type `turbo3` em `additional_args` são específicas do fork turboquant-SYCL do autor — remova-as se você estiver rodando o `llama.cpp` padrão.

## 4. Execute

```bash
# Windows (PowerShell ou cmd)
run.bat

# Linux / macOS
chmod +x run.sh
./run.sh
```

Os dois scripts buildam o frontend (`pnpm build` em `src/frontend`) antes de iniciar a API. O `run.sh` adicionalmente inicia o próprio processo consolidado do `llama-server` e espera seu endpoint `/health` antes de continuar; no backend, `core/engine/runner.py` também sobe automaticamente e verifica a saúde de uma instância `llama-server` a partir de `models_config.json` na inicialização do FastAPI (veja [infrastructure/sre.md](../infrastructure/sre.md)) — verifique seu próprio setup se rodar os dois caminhos juntos, para evitar iniciar o servidor duas vezes.

Os dois scripts vinculam por padrão a `0.0.0.0` (alcançável pela LAN, para que um celular na mesma Wi-Fi consiga se conectar) e imprimem a URL da LAN na inicialização. Passe `local` (`run.bat local` / `./run.sh local`) para vincular apenas a `127.0.0.1`. **Não há login de nenhum tipo** — qualquer um que consiga alcançar o endereço vinculado pode usar o app, então só habilite o modo LAN em redes que você confia. O `run.sh` também aceita `--debug`, que define `DEBUG_LATENCY=True` e eleva o nível de log do `uvicorn` para diagnósticos de latência passo a passo.

Para rodar o backend sozinho, sem nenhum dos scripts de execução:

```bash
venv/Scripts/python.exe -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8000
```

## 5. Migrações de banco de dados

`init_db()` constrói/atualiza o schema na inicialização e o marca (`stamp`) na revisão Alembic atual, caso ainda não esteja rastreado. Mudanças de schema são versionadas via Alembic (`src/backend/db/migrations/`); depois de puxar mudanças que tocam no schema, rode a migração você mesmo — ela nunca é aplicada automaticamente:

```bash
venv/Scripts/python.exe -m alembic upgrade head
```

## Próximos passos

* [testing.md](../testing.md) — rodando as suítes de teste e adicionando uma feature com segurança.
* [card-authoring-epic.md](../card-authoring-epic.md) — escrevendo uma card de personagem.
* [mobile-lan-smoke-test.md](../mobile-lan-smoke-test.md) — o checklist manual para dispositivo móvel em modo LAN.
