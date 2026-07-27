# Testes e Contribuição

## Rodando os testes

Backend (a partir da raiz do repositório; use o venv do projeto, nunca um `python`
global):

```bash
venv/Scripts/python.exe -m pytest src/backend/__tests__ -q          # todos
venv/Scripts/python.exe -m pytest src/backend/__tests__/test_x.py::test_y -q   # um só
venv/Scripts/python.exe -m pytest src/backend/__tests__ -k "substring" -q      # por padrão
venv/Scripts/python.exe -m ruff check src/backend                   # lint
```

Frontend (a partir de `src/frontend`, apenas `pnpm` — nunca npm/yarn):

```bash
pnpm test            # vitest run
pnpm vitest run src/path/File.test.tsx -t "test name"   # um só
pnpm coverage        # coverage
pnpm lint            # eslint
pnpm exec playwright test   # E2E
```

## Isolamento de testes (obrigatório)

Os testes **nunca** devem tocar no banco de produção (`chatbot.db`) nem no vector
store real (`chroma_db`):

- `conftest.py` dá a cada teste um SQLite temporário isolado; `settings.CHROMA_PATH`
  é redirecionado para um diretório temporário sob os testes; o lifespan da
  aplicação pula o `init_db` e o boot do llama sob pytest.
- Nenhum teste pode acessar um llama-server real ou embeddings reais. Use fakes
  determinísticos (ex.: um embedding baseado em hash) ou mocks.
- A aplicação de FK está DESLIGADA no engine de teste padrão (ela vincula o
  listener `PRAGMA foreign_keys=ON` apenas ao engine da aplicação). Testes que
  precisam de comportamento de FK usam a fixture `fk_session` em
  `test_db_cascade.py`, que a habilita.

## Cobertura e padrões

- Mantenha **≥80%** de cobertura para backend e frontend, no geral e por módulo
  principal. Features novas são entregues com testes; prefira test-first para
  correções de bugs.
- O código segue Clean Architecture / SOLID / DDD (veja o README). A lógica de
  domínio em `core/` é agnóstica de transporte e persistência; a `Session` do
  banco e os clientes de LLM são injetados.

## Adicionando uma feature com segurança

1. Escreva primeiro o teste que falha (um cenário de falha concreto).
2. Implemente a mudança mínima; mantenha a suíte verde e o `ruff` limpo.
3. Para uma **mudança de schema**: atualize `models.py` **e** gere uma migração
   Alembic (`alembic revision -m "..."`); nunca rode migrações contra o banco real
   automaticamente — o usuário roda `alembic upgrade head`. Veja
   [data-model-er.md](./data-model-er.md) §"Gerenciamento de schema".
4. Para mudanças arriscadas no núcleo de chat/memória/estado, leia
   [architecture.md](./architecture.md) primeiro — o espelho Chat↔AgentState e o
   escopo por `(character, chat)` são as áreas mais propensas a bugs.
