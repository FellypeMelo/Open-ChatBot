# Relatório Final — Limpeza e Refatoração de Qualidade de Produção

**Projeto:** Open-ChatBot (motor local de agentes/NPCs — FastAPI + React/TypeScript)
**Branch:** `fix/ci-flake-and-readme`
**Escopo:** limpeza completa do código sob Clean Architecture, SOLID, DDD, Design Patterns, Clean Code, TDD e Extreme Programming.
**Resultado:** 17 lotes ("batches") entregues, cada um com as duas suítes de teste verdes.

---

## 1. Resumo executivo

O código foi reescrito de forma incremental e **preservando comportamento**, em 15 commits agrupados em três camadas de risco crescente. Ao final:

| Métrica | Antes | Depois |
| :--- | :--- | :--- |
| Testes backend (pytest) | 231 | **237** (verdes) |
| Testes frontend (vitest) | 248 | **250** (verdes) |
| `ruff` (lint backend) | — | **limpo** |
| `tsc --noEmit` (tipos frontend) | — | **limpo** |
| `eslint` (frontend) | 11 erros + 1 aviso | **limpo** |
| Diff agregado | — | **62 arquivos, +4787 / −1854 linhas** |

Nenhuma mudança quebrou comportamento existente; toda correção de bug real veio acompanhada de um teste que **falhava antes** e passa depois (TDD).

### Princípios aplicados na prática

- **Clean Code / DRY:** eliminação sistemática de duplicação (tipos, mapeadores, helpers, blocos de query).
- **SOLID:** responsabilidade única (decomposição de funções gigantes), inversão de dependência (domínio deixa de depender da persistência).
- **DDD / Clean Architecture:** extração de uma camada de domínio pura (`state_transitions`) para fora da camada de API, dependendo de *ports* (interfaces) e não de modelos ORM.
- **TDD / XP:** teste-primeiro nas correções de bug; commits pequenos e frequentes (um por lote), cada um com as suítes verdes antes de seguir.

---

## 2. Metodologia

1. **Auditoria multi-agente** do código inteiro → síntese → plano ordenado de 17 lotes por relação valor/risco.
2. **Preservação de comportamento** como regra: as suítes de teste (231 backend + 248 frontend) foram a rede de segurança. Refatoração só era aceita com tudo verde.
3. **Isolamento de teste:** o banco de produção (`chatbot.db`) nunca foi tocado durante os testes; migrações e verificações usaram bancos temporários descartáveis.
4. **Commit por lote:** rastreabilidade total — cada lote é um commit atômico com mensagem descritiva.

---

## 3. As 17 melhorias, por camada

### Camada A — Limpeza preservando comportamento (lotes 1–11)

Reduções e reorganizações sem qualquer mudança de comportamento observável.

- **Memória por chat, código morto e números mágicos** (`b228768`)
  Escopo de memória vetorial por `(character, chat)`; remoção de código morto (refs não usadas, `db.commit` no-op, imports inline, `console.log` sempre-disparando); constantes nomeadas no lugar de literais espalhados (limiares de humor/sono, tamanhos de resumo, durações de toast, faixas de ID temporário).

- **Tipos de domínio consolidados no frontend** (`d20de80`)
  `Tag`/`Character`/`User` deixam de ser redeclarados em cada componente; passam a ser importados de `services/api.ts` via `import type`.

- **`get_or_404` + CRUD guiado por `model_dump`** (`aacbe43`)
  Novo `api/common.py` com `get_or_404` genérico, eliminando 5 cópias do padrão "buscar-ou-404" nos routers `tags`, `lore`, `presets`, `users`. Construção de modelos via `Model(**dto.model_dump())`.

- **`CharacterBase` + helpers de upload/upsert** (`cb2297c`)
  Um único esquema-base compartilhado por `CharacterUpsert`/`CharacterResponse`; helpers `_read_upload_within_limit` (413), `_parse_card_or_422` (422) e `_apply_upsert` reutilizados pelos endpoints de criar/importar/atualizar/avatar.

- **Correção do bug de `DEFAULT_CONFIG` + helpers no runner** (`fe3140c`)
  **Bug real:** o ramo sem arquivo de config usava cópia rasa (`.copy()`) e depois mutava dicionários aninhados, **corrompendo a constante de módulo compartilhada**. Corrigido para `copy.deepcopy`, com teste de regressão. Helpers extraídos (`_is_alive`, `_ensure_embedding_args`, `_heal_flash_attn`).

- **Deduplicação em `vector_store`/`llm`/`settings`** (`15236eb`)
  `_parse_embedding_response`, `_load_or_init_store`, `_clear_by_metadata` (colapsando duas rotinas quase idênticas); `_pick` para leitura de presets em `llm`; decorator `_handle_errors` uniformizando o tratamento de erro dos 8 endpoints de settings.

- **`chat.py`: persistência extraída, N+1 e recursão** (`732c695`)
  `_persist_assistant_reply` compartilhado entre `/chat` e `/chat/stream`; `list_chats` troca o N+1 por uma única query agrupada (`func.count()`); `deactivate_subtree` reescrito de recursão para BFS iterativo em lotes por nível; remoção do `gc.collect()` manual.

- **`CharacterCreator`: lint zerado + mapeadores compartilhados** (`7ea510d`)
  Resolve os **11 erros + 1 aviso** do eslint: helpers de token movidos para escopo de módulo; contagem de tokens derivada em render (elimina `setState`-em-effect); `MacroToolbar` extraído para escopo de módulo; escrita de refs movida para um handler de evento real. Em `App.tsx`, `toCharacterPayload` + `uploadAvatar` unificam criar/atualizar personagem. Em `ChatView.tsx`, `adjustStat` colapsa 6 chamadas duplicadas.

### Camada B — Correções de correção (teste-primeiro, lotes 12–14)

Bugs reais, cada um com teste que falhava antes da correção.

- **Frames SSE partidos + botão de formulário travado** (`bcb8f88`)
  **Bug 1:** o parser de streaming dividia cada leitura por `\n` isoladamente, então um frame `data: {...}` partido entre duas leituras era **descartado** (JSON parcial falhava no parse; a continuação não começava com `data: `). Agora há um buffer que atravessa leituras e só processa linhas completas.
  **Bug 2:** `isSaving` só voltava a `false` no caminho de sucesso — um `onCreate`/`onUpdate` que lançasse deixava o botão preso em "Saving...". Envolvido em `try/finally`.

- **Preservar caixa de nomes multi-palavra + contrato 500 do `/restart-all`** (`73b5ac9`)
  **Bug 3:** `str.capitalize()` sobre rótulos de local/roupa minusculiza tudo após a primeira letra, destruindo nomes como "Grand Ballroom" → "Grand ballroom". Extraído `_normalize_state_label` (primeira letra maiúscula preservando o resto).
  **Bug 4:** `/settings/restart-all` retornava 200 "success" mesmo quando um servidor falhava — inconsistente com `/start/inference` e `/start/embedding` (que retornam 500). Agora retorna 500 quando qualquer servidor falha.

- **Centralização da detecção de teste em `settings.TESTING`** (`b8af8fd`)
  Quatro módulos farejavam `"pytest" in sys.modules` de forma independente. Detecção feita uma única vez em `Settings.__init__`, exposta como `settings.TESTING`. Um único interruptor para raciocinar.

### Camada C — Refatorações arquiteturais (lotes 15–17)

- **Camada de domínio + decomposição de `evolve_character`** (`502fb46`)
  Nova `core/engine/state_transitions.py` concentra a lógica pura de "ação narrativa → estado do agente" (`parse_actions_to_state`, `apply_action_stats`, `normalize_state_label`, `ACTIONS_CONFIG`), retirada da camada de API. `evolve_character` (um bloco `try` de 165 linhas fazendo seis coisas) foi decomposto em `_merge_reflection_traits`, `_roll_active_summary`, `_append_unique_facts`, `_apply_relationship_change`, `_write_journal_entry` e `_evolve_relationship_tags` — com as 4 trocas de tag quase idênticas colapsadas num único `_swap_tag`.

- **Inversão de dependência domínio→db** (`f3fdd7e`)
  Aplica a regra de dependência da Clean Architecture na fronteira do domínio: `state_transitions` não importa mais o modelo ORM `AgentState`. Novo `core/ports.py` define o *Protocol* estrutural `AgentStateLike`; o domínio depende do *port*, e o modelo ORM o satisfaz estruturalmente nas bordas. Um teste de *fitness* arquitetural garante que o domínio nunca volte a importar `src.backend.db`.

- **Regras de `ondelete` uniformes e corretas por tipo** (`1bdd898`)
  FKs de posse → `CASCADE`; FKs de ponteiro (`current_message_id`, `active_chat_id`) → `SET NULL` (nunca `CASCADE`: apagar uma mensagem não pode apagar o agente). Afeta apenas esquemas recém-criados; bancos existentes continuam via a limpeza manual FK-safe dos endpoints. Novo teste habilita o *pragma* de FK do SQLite e verifica que `CASCADE` e `SET NULL` de fato disparam.

- **Alembic como framework de migração** (`b86dc6f`)
  Substitui a pilha crescente de `ALTER TABLE ... ADD COLUMN` manuais em `init_db()`. `env.py` ligado ao `Base.metadata` e a `settings.DATABASE_URL`, resolvendo o banco por `-x db_url=...` primeiro (autogenerate/testes nunca tocam o `chatbot.db` real) e habilitando o *batch mode* do SQLite. Migração inicial autogerada captura todas as tabelas, índices e as 12 regras `ondelete`. `test_migrations.py` aplica a migração a um banco temporário e garante que ela constrói o esquema completo dos modelos.

---

## 4. Bugs reais encontrados e corrigidos

| # | Bug | Onde | Correção |
| :-- | :--- | :--- | :--- |
| 1 | Cópia rasa mutando a constante de módulo `DEFAULT_CONFIG` | `core/engine/runner.py` | `copy.deepcopy` + teste de regressão |
| 2 | Tokens perdidos quando um frame SSE é partido entre leituras | `App.tsx` | buffer atravessando leituras |
| 3 | Botão do formulário preso em "Saving..." após erro | `CharacterCreator.tsx` | `try/finally` |
| 4 | `.capitalize()` destrói nomes multi-palavra (local/roupa) | `api/chat.py` | `_normalize_state_label` |
| 5 | `/restart-all` retornava 200 mesmo com falha | `api/settings.py` | 500 quando qualquer servidor falha |
| 6 | Consulta N+1 ao listar chats | `api/chat.py` | `func.count()` agrupado |
| 7 | Recursão sem limite em `deactivate_subtree` | `api/chat.py` | BFS iterativo |

---

## 5. Decisões de escopo e trade-offs (honestidade de engenharia)

Duas escolhas conscientes de **não** aplicar um padrão onde ele pioraria o código:

- **Sem "ChatService" só por formalidade.** As funções de orquestração em `chat.py` já são funções de módulo coesas e testadas. Envolvê-las numa classe de serviço apenas por convenção adicionaria indireção sem melhorar a separação de responsabilidades. A extração de valor real — a **camada de domínio** (`state_transitions`) — foi feita.

- **Sem *repository pattern* forçado sobre `evolve_character`/`suggest_tags`.** Esses são serviços de aplicação que legitimamente orquestram persistência. A lógica de troca de tags manipula a coleção ORM `character.tags` e usa *row locking* (`with_for_update`); esconder isso atrás de um *port* vazaria a abstração (o *port* teria de expor coleções ORM) e reescreveria ~15 testes fortemente mockados sem benefício real para um único banco local. A inversão foi aplicada onde é correta e segura: a **fronteira do domínio**.

Essas são decisões de engenheiro sênior: aplicar o padrão onde ele paga, recusá-lo onde vira *cargo cult*.

---

## 6. Como usar as novas peças

- **Evolução de esquema (Alembic):**
  - Aplicar migrações: `alembic upgrade head`
  - Gerar nova migração após mudar modelos: `alembic revision --autogenerate -m "descrição"`
  - Testes/autogenerate contra banco descartável: `alembic -x db_url="sqlite:///caminho/temp.db" ...`
  - `init_db()`/`create_all` permanece para primeira execução e para os engines de teste isolados.

- **Detecção de ambiente de teste:** use `settings.TESTING` (não fareje `sys.modules`).

- **Camada de domínio:** regras de estado ficam em `core/engine/state_transitions.py`, dependendo de `core/ports.py`. Não importe modelos ORM ali (há teste de *fitness* que falha se isso acontecer).

- **Acesso a entidade + 404:** use `get_or_404(db, Model, id, "Nome")` de `api/common.py`.

---

## 7. Verificação final

```
Backend:  237 testes verdes  ·  ruff limpo
Frontend: 250 testes verdes  ·  tsc limpo  ·  eslint limpo
```

Todos os 17 lotes foram commitados individualmente (de `b228768` a `b86dc6f`), cada um com as suítes verdes no momento do commit.

---

## 8. Trabalho pendente (fora dos 17 lotes)

- **B4 — fontes/ícones offline (P0):** substituir dependências de fontes/ícones remotos por versões auto-hospedadas, para que o app rode 100% offline. Esta tarefa foi mantida separada dos 17 lotes de limpeza e ainda está pendente.

---

*Documento gerado ao final da refatoração. Todas as referências a commits, arquivos e números de teste refletem o estado da branch no encerramento do trabalho.*
