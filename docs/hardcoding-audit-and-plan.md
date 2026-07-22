# Hardcoding Audit & Remediation Plan

> **⚠️ POINT-IN-TIME SNAPSHOT — not re-verified.** No known contradiction with current code, but this list has not been re-checked item by item since it was written. Confirm each finding against the live file:line before acting on it; some may already be fixed or have drifted further.

Deep sweep of the codebase for hardcoded values that should be config/env/constants. 44 findings, 13 actively broken/mismatched. Ordered broken-first, then severity. Each item has a config-driven fix and a TDD test.

## Summary table (broken-first)

| Broken | Sev | Eff | Location | Category | Issue |
|:------:|:---:|:---:|----------|----------|-------|
| YES | P0 | M | src/frontend/index.html:9 | url | The entire icon set is loaded from Google's CDN. In a local-first / offline app the font n... |
| YES | P0 | M | run.sh:24 | path | The Linux/mac launcher hardcodes '-m models/model.gguf', but the only model actually prese... |
| YES | P1 | S | src/frontend/playwright.demo.config.ts:28 | path | Hardcoded absolute machine-specific working directory. The demo E2E config only runs if th... |
| YES | P1 | S | run.sh:13 | path | A specific oneAPI version directory '2025.3' is hardcoded into LD_LIBRARY_PATH. Any machin... |
| YES | P1 | S | .env.example:3 | content | Three different placeholder model filenames exist across config surfaces that are supposed... |
| YES | P1 | S | models_config.example.json:6-9 | content | The committed example config has drifted hard from the real models_config.json: context_si... |
| YES | P1 | S | src/frontend/src/hooks/useSettings.ts:14 | url | The persisted LLM config defaults base_url to the hardcoded loopback port 8080 and is sent... |
| YES | P1 | S | src/backend/core/engine/runner.py:74 | magic-number | Two different context-size defaults disagree across the codebase. runner.DEFAULT_CONFIG se... |
| YES | P1 | M | src/backend/core/engine/llm.py:24 | ip | The host 127.0.0.1 is hardcoded in LlamaClient.url / embedding_url. config.py defines LLAM... |
| YES | P1 | S | src/backend/core/memory/vector_store.py:33 | url | Hardcoded embedding fallback URL points at port 8081, but the runner deliberately migrates... |
| YES | P1 | S | src/backend/core/config.py:6 | port | The default embedding URL is 8081, which contradicts the actual runtime layout where embed... |
| YES | P1 | M | src/backend/api/chat.py:468 | content | The default-state literal is duplicated here and has already drifted from the canonical Ag... |
| YES | P2 | S | src/backend/core/config.py:6 | url | The embedding URL default points at port 8081, but the runtime has consolidated embeddings... |
| - | P1 | M | src/frontend/index.html:8 | url | Remote Google Fonts <link> in a local-first app: fonts fail to load offline and fall back ... |
| - | P1 | M | src/frontend/src/index.css:1 | url | Second remote-CDN font dependency, this time the primary body font (Outfit, --font-sans us... |
| - | P1 | M | src/frontend/src/components/ChatView.tsx:11-23 | content | The action/gift id, label, icon AND the numeric stat deltas shown to the user are hardcode... |
| - | P1 | M | src/frontend/index.html:8-9 | url | A local-first / offline app hard-links two Google Fonts CDN stylesheets. Material Symbols ... |
| - | P1 | S | src/backend/core/engine/runner.py:37 | path | The Intel oneAPI setvars.bat location is a hardcoded absolute Windows path. Any machine wi... |
| - | P2 | S | src/frontend/vite.config.ts:17-25 | url | The dev-proxy backend origin is hardcoded nine times. It cannot be pointed at a different ... |
| - | P2 | S | src/frontend/playwright.config.ts:21 | port | Frontend port 5173, backend port 8000 and host 127.0.0.1 are hardcoded literals duplicated... |
| - | P2 | S | vector_store.py:33 | port | Embedding falls back to a hardcoded http://127.0.0.1:8081, duplicating config.py's EMBEDDI... |
| - | P2 | M | run.sh:24 | port | Ports are hardcoded as bare literals in every launcher and the CI smoke test: uvicorn 8000... |
| - | P2 | S | run.bat:5 | path | The Intel oneAPI install location is hardcoded to the default absolute path on both platfo... |
| - | P2 | M | src/frontend/src/components/SettingsModal.tsx:18-30,113-114,139,331,343,502,515 | port | Default inference port 8080, embedding port 8081, thread count 4, context 4096, and gpu_la... |
| - | P2 | S | src/frontend/src/components/SettingsModal.tsx:291-292,308-309,455,465-466,483-484 | path | The runner-binary directory prefix 'llama_bin/' and model directory prefix 'models/' are s... |
| - | P2 | S | src/frontend/src/components/ChatView.tsx:58 | magic-number | The typewriter reveal speed (20 ms/token) is a bare magic number at the call site, overrid... |
| - | P2 | M | src/frontend/src/components/ChatView.tsx:260,281,288,309,316,337,344 | magic-number | The manual HUD stat-adjustment deltas are hardcoded: the Feed button subtracts 30 hunger, ... |
| - | P2 | M | src/frontend/src/hooks/useAudio.ts:62,103-118 | content | The ambient-sound engine hardcodes the location taxonomy (which location keywords map to w... |
| - | P2 | S | src/backend/main.py:78 | timeout-retry | The LLM health-check warmup loop hardcodes 30 attempts, a literal '/30' in the log string,... |
| - | P2 | S | src/backend/core/engine/runner.py:349 | magic-number | The micro-batch size 2048 is a magic number baked into code in two places (consolidated in... |
| - | P2 | S | src/backend/core/engine/runner.py:351 | model-assumption | Embedding pooling is hardcoded to 'cls' in two places. 'cls' pooling is correct only for m... |
| - | P2 | S | src/backend/core/engine/runner.py:408 | magic-number | The 'wait briefly to detect instant crashes' window is a hardcoded 0.5s in both start_infe... |
| - | P2 | M | src/backend/core/context/budget.py:36 | magic-number | Every context layer's token cap is a hardcoded magic number. These caps directly govern ho... |
| - | P2 | S | src/backend/core/context/budget.py:64 | magic-number | The word-count->token fallback ratio 1.3 and the 5.0s tokenize timeout are hardcoded (the ... |
| - | P2 | S | src/backend/db/database.py:39 | content | Roleplay stat defaults ('Living Room', 'Neutral', 'Casual') are baked into migration ALTER... |
| - | P2 | S | src/backend/core/engine/llm.py:188 | model-assumption | The embedding dimension 2560 is hardcoded as a magic number in the pytest/E2E mock. 2560 i... |
| - | P2 | M | src/backend/api/chat.py:68 | magic-number | The narrative eating-action hunger reduction (-30) is a bare magic number, and it is incon... |
| - | P2 | M | src/backend/api/chat.py:139 | content | The entire quick-action catalog -- button messages and stat-delta magic numbers (happiness... |
| - | P2 | S | src/backend/api/chat.py:297 | magic-number | The reflection cadence '20' is hardcoded in five places (two %20 checks, the message-fetch... |
| - | P2 | M | src/backend/core/orchestration/bridge.py:108 | magic-number | History budgeting estimates tokens with a hardcoded '4 chars/token + 5' heuristic, while C... |
| - | P2 | M | src/backend/core/context/budget.py:36 | magic-number | All per-layer token allocation caps are hardcoded in the constructor. These directly shape... |
| - | P2 | M | src/backend/core/context/compressor.py:34 | magic-number | The physiological/relationship narrative thresholds that drive prompt modifiers are hardco... |
| - | P2 | S | src/backend/core/engine/llm.py:96 | timeout-retry | LLM request timeouts are scattered hardcoded floats (120.0 non-stream, 300.0 stream, 5.0 h... |
| - | P2 | S | src/backend/core/engine/engine.py:132 | magic-number | The rolling active-summary trim uses hardcoded 1500 (trigger) and 1000 (kept tail) charact... |

## Detailed findings

### 1. [P0] BROKEN src/frontend/index.html:9

- **What:** <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined..." rel="stylesheet"/>
- **Category:** url | **Effort:** M | **Slice:** Frontend build, assets & exter
- **Problem:** The entire icon set is loaded from Google's CDN. In a local-first / offline app the font never loads, and the 45 `<span class="material-symbols-outlined">...</span>` usages across 11 components (App.tsx:556 'menu', App.tsx:568 'person', ChatView.tsx 17 icons, Sidebar.tsx 5, CharactersView.tsx 6, etc.) render as literal ligature TEXT (the words 'menu', 'send', 'person'...) instead of glyphs. The UI is visibly broken with no network.
- **Fix:** Self-host the icon font: drop the Material Symbols woff2 into src/frontend/public/fonts/ and declare it with a local @font-face, OR replace the icon spans with the already-installed `lucide-react` dependency (package.json:18) or the existing public/icons.svg sprite. Remove the CDN <link>.
- **TDD test:** Playwright/vitest: block requests to fonts.gstatic.com/fonts.googleapis.com, render App, assert no visible text node equals 'menu'/'person' and that an icon element (svg or ::before glyph) is present.

### 2. [P0] BROKEN run.sh:24

- **What:** ./llama_bin/llama-server -m models/model.gguf --port 8080 ... -c 4096 --flash-attn auto
- **Category:** path | **Effort:** M | **Slice:** Launch scripts & infra (run.ba
- **Problem:** The Linux/mac launcher hardcodes '-m models/model.gguf', but the only model actually present is models/Qwen3-4B-Hivemind-Inst-Hrtic-Ablit-Uncensored-Q4_K_M-imat.gguf (and models_config.json points there). models/model.gguf does not exist, so run.sh's llama-server launch fails immediately and wait_for_server on 8080 exits 1 after 60s. run.sh also never reads models_config.json, so it is a second, diverging source of truth for the model path, port, and every llama flag (it uses --cache-type-k q8_0 -c 4096 --flash-attn auto while models_config.example.json uses --cache-type-k turbo3 -c 65536 --flash-attn on --ubatch-size 2048).
- **Fix:** Have run.sh read model_path/port/additional_args from models_config.json (e.g. via a small python -c json.load or jq) so it uses the same runtime config the Windows backend loads, instead of a baked-in 'models/model.gguf' and a hand-copied flag string. At minimum, sync the filename to the real model and drive it from an env var (MODEL_PATH already exists in config.py/.env).
- **TDD test:** Add a CI/shell test asserting the model file referenced by run.sh (or resolved from models_config.json) exists on disk, and a test asserting run.sh and models_config.example.json agree on model_path.

### 3. [P1] BROKEN src/frontend/playwright.demo.config.ts:28

- **What:** cwd: 'G:\\Programas\\Open-ChatBot'
- **Category:** path | **Effort:** S | **Slice:** Frontend build, assets & exter
- **Problem:** Hardcoded absolute machine-specific working directory. The demo E2E config only runs if the repo is checked out at exactly G:\Programas\Open-ChatBot. On any other developer's machine, CI, or a different drive/path it fails immediately to start the uvicorn webServer. (The sibling playwright.config.ts:38 correctly uses a relative `cd ../..` instead.)
- **Fix:** Derive the repo root relatively, e.g. cwd: path.resolve(__dirname, '../..') (import { fileURLToPath } for ESM), matching the relative approach in playwright.config.ts. Remove the drive-letter literal.
- **TDD test:** Copy the repo to a different path (or a CI temp dir) and run `pnpm exec playwright test -c playwright.demo.config.ts --list`; assert the webServer command resolves without a 'path not found' error.

### 4. [P1] BROKEN run.sh:13

- **What:** export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/llama_bin:/opt/intel/oneapi/2025.3/lib
- **Category:** path | **Effort:** S | **Slice:** Launch scripts & infra (run.ba
- **Problem:** A specific oneAPI version directory '2025.3' is hardcoded into LD_LIBRARY_PATH. Any machine with a different oneAPI release (2024.x, 2025.0, 2025.4, etc.) or the default-versioned 'latest' symlink layout gets a non-existent path silently appended, so the SYCL runtime libs are not found and llama-server fails to load its .so dependencies. The setvars.sh sourced on line 4 already exports the correct versioned lib paths, making this literal both fragile and redundant.
- **Fix:** Drop the hardcoded '/opt/intel/oneapi/2025.3/lib' and rely on setvars.sh, or derive it from an ONEAPI_ROOT / oneapi version env var (e.g. ${ONEAPI_ROOT:-/opt/intel/oneapi}/latest/lib).
- **TDD test:** Shell test: run.sh must not contain a literal oneAPI version segment; assert LD_LIBRARY_PATH additions resolve to existing directories on the runner.

### 5. [P1] BROKEN .env.example:3

- **What:** MODEL_PATH=models/your-model.gguf
- **Category:** content | **Effort:** S | **Slice:** Launch scripts & infra (run.ba
- **Problem:** Three different placeholder model filenames exist across config surfaces that are supposed to describe the same thing: .env.example says 'models/your-model.gguf', config.py default and models_config.example.json say 'models/model.gguf', and the real models_config.json says the actual Qwen3 file. None of the placeholders matches the real file, and they disagree with each other, so a config-less clone gets inconsistent guidance depending on which file it copies from. These will drift further with every edit.
- **Fix:** Pick one canonical placeholder (or, better, one canonical real default) and reference it from a single source. Sync .env.example MODEL_PATH, config.py MODEL_PATH default, and models_config.example.json model_path to the same string.
- **TDD test:** Test that MODEL_PATH in .env.example, config.py default, and models_config.example.json model_path are byte-identical.

### 6. [P1] BROKEN models_config.example.json:6-9

- **What:** context_size 65536, threads 0, gpu_layers 99, additional_args '--cache-type-k turbo3 --cache-type-v turbo3 --flash-attn on --parallel 1 --ubatch-size 2048'
- **Category:** content | **Effort:** S | **Slice:** Launch scripts & infra (run.ba
- **Problem:** The committed example config has drifted hard from the real models_config.json: context_size 65536 vs 4096, threads 0 vs 4, gpu_layers 99 vs -1, and cache-type-k turbo3 vs q8_0. A fresh clone copies the example and gets a 64k context on a 4B model plus a --cache-type-k turbo3 that directly contradicts the DEFAULT_CONFIG value just fixed this session (q8_0 for K). The example both misleads new users and re-introduces the exact K-cache setting that was corrected in code.
- **Fix:** Regenerate models_config.example.json from the same DEFAULT_CONFIG constant the backend uses (or a documented sane default), and set cache-type-k to q8_0 to match the fixed default. Keep context_size/gpu_layers/threads at conservative defaults documented as such.
- **TDD test:** Test asserting models_config.example.json's additional_args cache-type-k matches the backend DEFAULT_CONFIG, and that example values parse/validate against the same schema the runner uses.

### 7. [P1] BROKEN src/frontend/src/hooks/useSettings.ts:14

- **What:** return { base_url: 'http://localhost:8080', model_name: '' }
- **Category:** url | **Effort:** S | **Slice:** Frontend components & client l
- **Problem:** The persisted LLM config defaults base_url to the hardcoded loopback port 8080 and is sent to the backend as config.base_url (consumed at src/backend/api/chat.py:500 as the actual LLM target URL). The inference port is user-configurable in SettingsModal (default 8080 but editable). If a user runs inference on any other port, this stale localStorage 'http://localhost:8080' overrides it and chat requests hit the wrong port, breaking generation. The frontend has no single source of truth tying this value to the runner's real port.
- **Fix:** Do not hardcode a port here. Default base_url to undefined/'' (backend already falls back to its own runner config URL) OR derive it from fetchRunnerStatus().inference.config.port. Centralize the loopback host + default port as one exported constant shared by useSettings and SettingsModal.
- **TDD test:** Render useSettings with empty localStorage and assert base_url is undefined/'' (not a hardcoded port). Integration: set inference port to 9090 via saveRunnerConfig, then assert the config sent by sendMessageStream does not force :8080.

### 8. [P1] BROKEN src/backend/core/engine/runner.py:74

- **What:** DEFAULT_CONFIG inference "context_size": 4096
- **Category:** magic-number | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** Two different context-size defaults disagree across the codebase. runner.DEFAULT_CONFIG sets context_size=4096, but src/backend/core/config.py:18 sets CONTEXT_SIZE=8192. budget.py:_configured_context_size() reads the runner value first (4096) and only falls back to settings.CONTEXT_SIZE (8192) when the runner is unavailable, so the token budget silently computes with 8192 in unit tests / fallback but 4096 in production — a drift that mis-sizes the context window and can overflow or waste the prompt budget.
- **Fix:** Have a single source of truth: seed DEFAULT_CONFIG['inference']['context_size'] from settings.CONTEXT_SIZE (import config) instead of a separate literal, or make config.CONTEXT_SIZE default match 4096. Add a startup assertion that the two agree.
- **TDD test:** Assert runner.DEFAULT_CONFIG['inference']['context_size'] == settings.CONTEXT_SIZE, and that ContextBudgetCalculator with no runner config uses the same value the runner would launch with.

### 9. [P1] BROKEN src/backend/core/engine/llm.py:24

- **What:** return f"http://127.0.0.1:{runner.config['inference']['port']}" (and :36 for embedding)
- **Category:** ip | **Effort:** M | **Slice:** Backend configuration & runtim
- **Problem:** The host 127.0.0.1 is hardcoded in LlamaClient.url / embedding_url. config.py defines LLAMA_SERVER_URL/EMBEDDING_SERVER_URL (env-overridable) precisely so the host can be changed, but llm.py bypasses them and pins loopback, so setting LLAMA_SERVER_URL to a non-loopback host has no effect on the actual LLM/embedding calls. The env knob is effectively inert.
- **Fix:** Derive host from settings (parse LLAMA_SERVER_URL host, or add a LLAMA_HOST setting) and only substitute the runtime port; or drop the port-only override and use the full configured URL.
- **TDD test:** Set LLAMA_SERVER_URL to http://0.0.0.0:9999 (or a custom host) and assert LlamaClient.url reflects that host.

### 10. [P1] BROKEN src/backend/core/memory/vector_store.py:33

- **What:** target_url = getattr(self.llm_client, "embedding_url", None) or "http://127.0.0.1:8081"
- **Category:** url | **Effort:** S | **Slice:** Backend LLM + orchestration + 
- **Problem:** Hardcoded embedding fallback URL points at port 8081, but the runner deliberately migrates the embedding server to share port 8080 with inference (runner.py:160-163 'Migrate embedding port to share port 8080'). The real deployed config (models_config.json and models_config.example.json) has embedding.port == 8080. So whenever this fallback branch is taken (llm_client without a usable embedding_url), synchronous document embedding POSTs to 127.0.0.1:8081 where nothing is listening, and every embed silently returns [] -> memories are stored with empty vectors.
- **Fix:** Drop the hardcoded literal. Derive the fallback from the runner's embedding config the same way LlamaClient.embedding_url does (http://127.0.0.1:{runner.config['embedding']['port']}), or reuse settings.EMBEDDING_SERVER_URL after fixing that default. Never bake the port into two places that can drift.
- **TDD test:** Unit test: construct LlamaCppEmbeddings with a stub llm_client lacking embedding_url and assert the target URL used equals the runner-configured embedding port (mock runner.config['embedding']['port']=8080), not 8081.

### 11. [P1] BROKEN src/backend/core/config.py:6

- **What:** EMBEDDING_SERVER_URL: str = "http://127.0.0.1:8081"
- **Category:** port | **Effort:** S | **Slice:** Backend LLM + orchestration + 
- **Problem:** The default embedding URL is 8081, which contradicts the actual runtime layout where embedding shares inference port 8080 (runner.py migrates 8081->8080; models_config*.json both use 8080). The value is stale and only referenced by tests now; any code that trusts it (or a future reader) will hit a dead port. It duplicates the same wrong literal hardcoded in vector_store.py:33.
- **Fix:** Either set the default to the shared inference port (http://127.0.0.1:8080) or remove EMBEDDING_SERVER_URL entirely and always resolve the embedding endpoint from runner.config['embedding']['port'] at runtime so there is one source of truth.
- **TDD test:** Test that the resolved embedding endpoint matches runner.config['embedding']['port'] for a config-less clone (which uses the example config's 8080), asserting it is not the legacy 8081.

### 12. [P1] BROKEN src/backend/api/chat.py:468

- **What:** clear_chat_history resets state.location='Living Room', clothes='Casual', mood='Neutral', stats={energy:100,hunger:0,...,'relationship':{'score':50,'history':[],'nickname':None}}
- **Category:** content | **Effort:** M | **Slice:** Backend LLM + orchestration + 
- **Problem:** The default-state literal is duplicated here and has already drifted from the canonical AgentState defaults in models.py:135-158. models.py seeds relationship as {'score':50,'dynamic_preferences':['teasing','playful'],'user_sentiment':'Neutral'} and includes 'last_update', while clear_chat_history writes relationship {'score':50,'history':[],'nickname':None} and omits 'last_update'. After a chat clear, the state object has a different stats shape than a freshly created character, and the missing last_update disables time-based need decay (update_needs returns early when last_update is absent).
- **Fix:** Factor the default state into one factory (e.g. AgentState.default_stats() / classmethod reset) and call it from both models.py __init__ and clear_chat_history so the two can never diverge; ensure last_update is set on reset.
- **TDD test:** Test that after clear_chat_history the state.stats keys equal a freshly constructed AgentState's stats keys, and that update_needs still decays after a clear (last_update present).

### 13. [P2] BROKEN src/backend/core/config.py:6

- **What:** EMBEDDING_SERVER_URL: str = "http://127.0.0.1:8081"
- **Category:** url | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** The embedding URL default points at port 8081, but the runtime has consolidated embeddings onto port 8080: runner.load_config() migrates embedding port 8081->8080 (runner.py:160-173) and DEFAULT_CONFIG embedding port is 8080 (runner.py:81). Worse, llm.py builds the embedding URL from runner.config['embedding']['port'] (llm.py:36), never from this setting — so EMBEDDING_SERVER_URL is a dead, misleading config value that no longer reflects where the embedding server actually listens.
- **Fix:** Either remove EMBEDDING_SERVER_URL (and LLAMA_SERVER_URL host) as dead config, or derive it from the runner port; if kept, default it to 8080 to match consolidation and have llm.py honor it.
- **TDD test:** Assert the URL/port used by LlamaClient.embedding_url equals runner.config['embedding']['port'], proving the config default and the live client can't diverge.

### 14. [P1] src/frontend/index.html:8

- **What:** <link href="https://fonts.googleapis.com/css2?family=Playfair+Display...&family=Crimson+Text...&family=Inter...&family=JetBrains+Mono..." rel="stylesheet"/>
- **Category:** url | **Effort:** M | **Slice:** Frontend build, assets & exter
- **Problem:** Remote Google Fonts <link> in a local-first app: fonts fail to load offline and fall back to system fonts. Worse, it is mismatched with the actual theme: it loads Playfair Display and Inter which are NOT referenced anywhere in index.css @theme (index.css uses Outfit for sans, JetBrains Mono for mono, Crimson Text for serif). Inter is even explicitly discouraged by the project guidelines. Meanwhile the real primary sans font, Outfit, is NOT preloaded here at all (it is only pulled via a separate CSS @import).
- **Fix:** Self-host the four fonts actually used (Outfit, JetBrains Mono, Crimson Text; drop Playfair Display and Inter which are dead) as local @font-face pointing at src/frontend/public/fonts/. Remove the CDN <link>.
- **TDD test:** Build the SPA, serve it with network to fonts.googleapis.com blocked, assert getComputedStyle(body).fontFamily resolves to a bundled 'Outfit' face (document.fonts.check("1rem 'Outfit'") === true).

### 15. [P1] src/frontend/src/index.css:1

- **What:** @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
- **Category:** url | **Effort:** M | **Slice:** Frontend build, assets & exter
- **Problem:** Second remote-CDN font dependency, this time the primary body font (Outfit, --font-sans used by html/body and all headings/body text) plus JetBrains Mono. Offline this @import fails and the whole app falls back to system sans. This is a duplicate/parallel font-loading path to index.html:8 (JetBrains Mono is fetched twice), and it is the only place Outfit is loaded even though it is the app's main typeface. Also note Crimson Text (--font-serif, used by --font-body-lg) is referenced in index.css:23/51 but is only ever fetched from the index.html CDN link, so offline body-lg text silently drops to Georgia.
- **Fix:** Remove the remote @import; add local @font-face rules for Outfit / JetBrains Mono / Crimson Text served from public/fonts/. Keep a single source of truth for which weights are bundled.
- **TDD test:** Vitest/Playwright with gstatic/googleapis blocked: assert document.fonts contains 'Outfit' and 'Crimson Text' faces and that no stylesheet @import targets an https:// host.

### 16. [P1] src/frontend/src/components/ChatView.tsx:11-23

- **What:** ACTIONS/GIFTS arrays with baked stat-effect strings, e.g. { id: 'hug', ... effect: 'HAPPINESS +5 • SOCIAL +10 • RELATION +2' } and GIFTS 'HUNGER -35 • ENERGY +5 • RELATION +3'
- **Category:** content | **Effort:** M | **Slice:** Frontend components & client l
- **Problem:** The action/gift id, label, icon AND the numeric stat deltas shown to the user are hardcoded in the component, duplicating the authoritative backend ACTIONS_CONFIG in src/backend/api/chat.py:139-171 (hug={happiness:5,social:10,relationship_score:2}, croissant={hunger:-35,energy:5,relationship_score:3}, etc.). They match today, but the /chat/actions endpoint (chat.py:206-210) only returns the `message` string, not the stats, so the UI cannot derive these labels at runtime. Any tuning of the backend deltas silently makes the UI lie about what a gift/action does, and adding a new backend action never surfaces in the drawer.
- **Fix:** Extend the /chat/actions payload (or add /chat/actions/catalog) to return the full config per id: {id, name, icon, stats:{...}}. Have the frontend render ACTIONS/GIFTS from api.fetchActions() and format the effect string from the returned stat map (e.g. join `${KEY} ${v>0?'+':''}${v}`). Delete the hardcoded arrays; keep only an icon fallback map if icons stay client-side.
- **TDD test:** Backend: assert GET /chat/actions returns each id with a `stats` dict equal to ACTIONS_CONFIG. Frontend: mock fetchActions to return coffee with stats {hunger:-10,energy:15,relationship_score:2} and assert the rendered gift button shows 'HUNGER -10 • ENERGY +15 • RELATION +2'; change the mock deltas and assert the label changes (proves no hardcoded copy).

### 17. [P1] src/frontend/index.html:8-9

- **What:** <link href="https://fonts.googleapis.com/css2?family=Playfair+Display...&family=Inter...&family=JetBrains+Mono..."> and <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined...">
- **Category:** url | **Effort:** M | **Slice:** Frontend components & client l
- **Problem:** A local-first / offline app hard-links two Google Fonts CDN stylesheets. Material Symbols Outlined supplies EVERY icon in the UI (menu, close, delete, refresh, send arrow, chevrons, bolt, etc. via className 'material-symbols-outlined'). With no internet the icon font never loads and every icon renders as raw ligature text ('menu', 'close', 'arrow_upward'), and the serif/mono display fonts fall back. This contradicts the single-origin, offline-capable premise and is a remote runtime dependency baked into the shell.
- **Fix:** Self-host the fonts: add the woff2 files under src/frontend/public/fonts (or via @fontsource / a Vite font plugin) and reference them with @font-face + a local Material Symbols woff2, so no external host is contacted. Remove the two googleapis.com <link> tags.
- **TDD test:** Add a test/CI check that scans built index.html (and dist assets) for 'fonts.googleapis.com' / 'fonts.gstatic.com' and fails if any external font host is referenced; assert a local @font-face for 'Material Symbols Outlined' exists.

### 18. [P1] src/backend/core/engine/runner.py:37

- **What:** setvars_path = Path("C:/Program Files (x86)/Intel/oneAPI/setvars.bat")
- **Category:** path | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** The Intel oneAPI setvars.bat location is a hardcoded absolute Windows path. Any machine with oneAPI installed to a custom directory, a different drive, or a non-default install (or Linux via run.sh) will silently fail to load the SYCL/oneAPI environment (only a warning is logged), which can make the SYCL llama-server binary fail to find its runtime.
- **Fix:** Resolve from ONEAPI_ROOT env var first (os.environ.get('ONEAPI_ROOT')), then fall back to a configurable ONEAPI_SETVARS path/setting, and only then the default location.
- **TDD test:** With ONEAPI_ROOT pointing at a temp dir containing a stub setvars.bat, assert get_oneapi_env() targets that path rather than the hardcoded Program Files location.

### 19. [P2] src/frontend/vite.config.ts:17-25

- **What:** 'http://localhost:8000' repeated for /chat, /characters, /users, /tags, /stats, /settings, /lore, /presets, /history (9 identical route targets)
- **Category:** url | **Effort:** S | **Slice:** Frontend build, assets & exter
- **Problem:** The dev-proxy backend origin is hardcoded nine times. It cannot be pointed at a different host/port (e.g. backend on :8001, or a LAN IP) without editing every line, and the nine copies can drift out of sync. Every new backend route also requires remembering to add another proxy line.
- **Fix:** Define one constant from env, e.g. `const target = process.env.VITE_BACKEND_URL ?? 'http://localhost:8000'`, and either map the route array to that target or use a single regex key `'^/(chat|characters|users|tags|stats|settings|lore|presets|history)'`. Document VITE_BACKEND_URL in .env.example.
- **TDD test:** Set VITE_BACKEND_URL=http://127.0.0.1:9999, load the config, and assert every proxy entry's target === the env value.

### 20. [P2] src/frontend/playwright.config.ts:21

- **What:** baseURL: 'http://localhost:5173' and webServer ports 8000 / 5173 (also playwright.demo.config.ts:13,27,31/39)
- **Category:** port | **Effort:** S | **Slice:** Frontend build, assets & exter
- **Problem:** Frontend port 5173, backend port 8000 and host 127.0.0.1 are hardcoded literals duplicated across both playwright configs and the vite proxy. If the Vite dev server or backend is moved to another port the E2E suite silently targets the wrong address, and the two config files can drift from each other and from vite.config.ts.
- **Fix:** Read ports/host from env with defaults, e.g. `const FE=process.env.PLAYWRIGHT_FE_PORT ?? 5173; const BE=process.env.PLAYWRIGHT_BE_PORT ?? 8000;` and build baseURL/webServer.port from them; share a single ports module between the two playwright configs.
- **TDD test:** Set PLAYWRIGHT_FE_PORT=5200, import the config, assert use.baseURL ends with ':5200' and webServer[1].port === 5200.

### 21. [P2] vector_store.py:33

- **What:** target_url = getattr(self.llm_client, "embedding_url", None) or "http://127.0.0.1:8081"
- **Category:** port | **Effort:** S | **Slice:** Launch scripts & infra (run.ba
- **Problem:** Embedding falls back to a hardcoded http://127.0.0.1:8081, duplicating config.py's EMBEDDING_SERVER_URL default (:8081). But run.sh starts a single consolidated server on 8080 with --embedding and nothing ever listens on 8081; the Windows runner only reaches 8080 via a port-migration shim (runner.py:160). On the Linux/mac path (run.sh) where that shim doesn't run, if embedding_url isn't set the fallback hits 8081 and every embedding POST fails. The literal also can drift from config.py's default independently.
- **Fix:** Reference settings.EMBEDDING_SERVER_URL instead of a bare '8081' literal, and make the default point at the consolidated inference port (8080) or derive it from LLAMA_SERVER_URL so it matches what run.sh actually starts.
- **TDD test:** Test that vector_store's embedding fallback URL equals settings.EMBEDDING_SERVER_URL (no independent literal), and an integration test that embedding requests target the same port run.sh launches.

### 22. [P2] run.sh:24

- **What:** backend port 8000 (run.bat:44, run.sh:82), llama port 8080 (run.sh:24,46; config.py:5), 8010 (e2e.yml:70), 8.8.8.8 (run.bat:28)
- **Category:** port | **Effort:** M | **Slice:** Launch scripts & infra (run.ba
- **Problem:** Ports are hardcoded as bare literals in every launcher and the CI smoke test: uvicorn 8000 in both run scripts, llama 8080 repeated in run.sh (start + health check) and config.py, 8010 in e2e.yml, and Google DNS 8.8.8.8 baked into run.bat's LAN-IP route probe. There is no single PORT/HOST env var, so changing the API or inference port means editing 4+ files, and an environment where 8000/8080 is taken cannot be reconfigured without code edits.
- **Fix:** Introduce PORT (backend) and LLAMA_PORT env vars with the current values as defaults; have run.bat/run.sh/config.py/e2e.yml read them. Make the route-probe target IP a variable (default 8.8.8.8) so offline/air-gapped LAN detection can be pointed at a local gateway.
- **TDD test:** Test that setting PORT env var changes the uvicorn --port in the launch command, and that config.py LLAMA_SERVER_URL port and run.sh's llama port come from one source.

### 23. [P2] run.bat:5

- **What:** "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" / run.sh:4 "/opt/intel/oneapi/setvars.sh"
- **Category:** path | **Effort:** S | **Slice:** Launch scripts & infra (run.ba
- **Problem:** The Intel oneAPI install location is hardcoded to the default absolute path on both platforms. It's guarded by an exist-check so it fails soft, but a non-default oneAPI install (custom drive, user-local install, or the D:/E: relocations common on Windows dev boxes) is silently skipped, and llama-server then fails later with missing SYCL libraries and no hint why.
- **Fix:** Honor an ONEAPI_ROOT (or SETVARS path) env var, falling back to the current default: e.g. in run.bat use %ONEAPI_ROOT% if set else the Program Files path; in run.sh use ${ONEAPI_ROOT:-/opt/intel/oneapi}.
- **TDD test:** Shell/bat test: setting ONEAPI_ROOT redirects the setvars invocation to that path; when the resolved setvars is missing, the script emits a clear warning instead of silently continuing.

### 24. [P2] src/frontend/src/components/SettingsModal.tsx:18-30,113-114,139,331,343,502,515

- **What:** useState(8080)/useState(8081) default ports, threads 4, context 4096, gpu -1; setEmbPort(8081); context_size: 4096 // Fixed default; parseInt(...) || 8080 / || 8081 / || 4 / || 4096 fallbacks
- **Category:** port | **Effort:** M | **Slice:** Frontend components & client l
- **Problem:** Default inference port 8080, embedding port 8081, thread count 4, context 4096, and gpu_layers -1 are hardcoded in the component and repeated across initial state, the parse fallbacks, and the reset-on-toggle path. Line 139 also hardcodes embedding context_size:4096 as a 'Fixed default' regardless of what the user set. These duplicate the backend runner defaults (models_config / config.py) with no shared constant, so backend default changes silently diverge from the form and the several 8080/8081/4096 copies can drift from each other.
- **Fix:** Import defaults from a single config module (or seed the whole form purely from fetchRunnerStatus so no literal defaults live in the UI). Replace the repeated `parseInt(x) || 8080` literals with a shared DEFAULTS constant, and derive embedding context_size from the inference field instead of the fixed 4096.
- **TDD test:** Mock fetchRunnerStatus with non-default values (port 9000, context 8192) and assert every field reflects them. Assert saving with a custom embedding context does not silently emit 4096.

### 25. [P2] src/frontend/src/components/SettingsModal.tsx:291-292,308-309,455,465-466,483-484

- **What:** infBinary.replace('llama_bin/', '') / setInfBinary(`llama_bin/${...}`) and infModel.replace('models/', '') / `models/${...}` (repeated 6+ times)
- **Category:** path | **Effort:** S | **Slice:** Frontend components & client l
- **Problem:** The runner-binary directory prefix 'llama_bin/' and model directory prefix 'models/' are string-literal-baked into the component and duplicated across inference and embedding selects plus the consolidated-mode notice. If the backend ever relocates these directories, every one of these literals must be hand-edited and any missed copy produces a wrong path sent to saveRunnerConfig.
- **Fix:** Expose the binary/model directory names from the backend status payload (e.g. status.paths.binary_dir / model_dir) or define them as two exported frontend constants used everywhere, and build paths via a helper joinModelPath(name).
- **TDD test:** Set the model-dir constant/status field to a non-default value and assert the select's onChange emits that prefix; assert changing it in one place updates all binary/model path renders.

### 26. [P2] src/frontend/src/components/ChatView.tsx:58

- **What:** const { displayedContent, enqueue, reset, isDraining } = useTokenQueue(20, playTypewriterClick)
- **Category:** magic-number | **Effort:** S | **Slice:** Frontend components & client l
- **Problem:** The typewriter reveal speed (20 ms/token) is a bare magic number at the call site, overriding the hook's own default of 25 (useTokenQueue.ts:11). The two defaults already disagree, and the animation pace — a UX tuning knob — is buried in a component with no named constant or config.
- **Fix:** Define a named constant (e.g. TYPEWRITER_MS_PER_TOKEN) in one place (the hook or a ui-constants module) and use it both as the hook default and at the call site; optionally allow override via settings.
- **TDD test:** Render ChatView with fake timers, enqueue a known string, advance by N*constant ms, and assert exactly N characters are revealed — parameterized by the shared constant so a value change updates test and code together.

### 27. [P2] src/frontend/src/components/ChatView.tsx:260,281,288,309,316,337,344

- **What:** hunger: Math.max(0,(...)-30); happiness ±10; social ±10; relationship_score ±10 in the manual stat-adjust buttons
- **Category:** magic-number | **Effort:** M | **Slice:** Frontend components & client l
- **Problem:** The manual HUD stat-adjustment deltas are hardcoded: the Feed button subtracts 30 hunger, which duplicates the backend's eating logic in src/backend/api/chat.py:68 (new_hunger = max(0, old_hunger - 30)); the ±/- buttons use a bare 10 for happiness/social/relationship. These deltas (and the 0/100 clamps) are duplicated between UI and backend with no shared constant, so a backend rebalance leaves the UI applying stale amounts.
- **Fix:** Pull stat step sizes and clamp bounds from a shared constant/config (ideally the same source the backend uses, surfaced via API), rather than literal 30/10 in JSX. At minimum name them (FEED_HUNGER_DELTA, STAT_STEP, STAT_MIN=0, STAT_MAX=100).
- **TDD test:** Assert clicking Feed calls onUpdateState with hunger reduced by exactly the shared FEED_HUNGER_DELTA, and that it equals the backend eating delta constant (import/parity test) so the two cannot silently diverge.

### 28. [P2] src/frontend/src/hooks/useAudio.ts:62,103-118

- **What:** location default 'Living Room'; keyword lists ['garden','outdoor','park','forest'] / ['rain','storm','outside']; filter freqs 350/800/100 and gains 0.005/0.003/0.006
- **Category:** content | **Effort:** M | **Slice:** Frontend components & client l
- **Problem:** The ambient-sound engine hardcodes the location taxonomy (which location keywords map to wind vs rain vs room-tone) and all the synthesis magic numbers (filter frequencies, Q, gains, buffer length 4s, brown-noise coefficients) inline in the hook. The location keyword set is effectively product content that must stay in sync with whatever location strings the backend/character state produces; a new location name silently falls through to the default room tone with no single place to configure the mapping.
- **Fix:** Extract an AMBIENT_PROFILES config (keyword list -> {filterType, frequency, Q, gain}) as a named constant/data table, and drive playAmbient from it; keep the default location label as one named constant.
- **TDD test:** Given a location containing 'forest', assert the created BiquadFilter uses the wind profile (type 'bandpass', freq 350); add a profile entry and assert playAmbient selects it without editing the function body.

### 29. [P2] src/backend/main.py:78

- **What:** for attempt in range(1, 31): ... f"(attempt {attempt}/30)" ... await asyncio.sleep(1)
- **Category:** timeout-retry | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** The LLM health-check warmup loop hardcodes 30 attempts, a literal '/30' in the log string, and a 1-second sleep. On slower GPUs or larger models, model load can exceed 30s and the app declares the server 'unreachable' even though it comes up moments later; the loop count and the log literal can also drift apart. None of it is configurable.
- **Fix:** Introduce settings like LLM_HEALTH_TIMEOUT_SECONDS / LLM_HEALTH_POLL_INTERVAL and compute attempts = timeout/interval; interpolate the same variable into the log message instead of a literal 30.
- **TDD test:** Set LLM_HEALTH_TIMEOUT_SECONDS to a small value and assert the loop performs the expected number of iterations and the log uses that bound.

### 30. [P2] src/backend/core/engine/runner.py:349

- **What:** extra_args.extend(["--ubatch-size", "2048"]) (also embedding path at runner.py:511-513)
- **Category:** magic-number | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** The micro-batch size 2048 is a magic number baked into code in two places (consolidated inference embedding branch and start_embedding), so the two can drift and neither is user-tunable. 2048 is a memory/perf tradeoff that depends on the model and GPU VRAM and should be configurable.
- **Fix:** Add an embedding_ubatch_size (default 2048) to models_config.json / DEFAULT_CONFIG and reference it in both spots via a single constant.
- **TDD test:** Set a custom ubatch size in config and assert both start_inference (consolidated) and start_embedding emit --ubatch-size with that value.

### 31. [P2] src/backend/core/engine/runner.py:351

- **What:** extra_args.extend(["--pooling", "cls"]) (repeated at runner.py:522-523)
- **Category:** model-assumption | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** Embedding pooling is hardcoded to 'cls' in two places. 'cls' pooling is correct only for models trained with a CLS token; mean-pooled embedding models (very common) will produce wrong embeddings. It is baked in code with no config surface and duplicated so the two call sites can drift.
- **Fix:** Expose embedding pooling type as a config field (default 'cls') and apply it from one place for both inference-consolidated and standalone embedding launches.
- **TDD test:** Configure pooling='mean' and assert the spawned embedding args contain --pooling mean in both code paths.

### 32. [P2] src/backend/core/engine/runner.py:408

- **What:** time.sleep(0.5) crash-detection window (also runner.py:559)
- **Category:** magic-number | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** The 'wait briefly to detect instant crashes' window is a hardcoded 0.5s in both start_inference and start_embedding. A binary that crashes slightly later (e.g. DLL resolution or SYCL init after ~0.6s) will be reported as a successful start; the value is a named-constant candidate duplicated across two functions.
- **Fix:** Hoist to a module constant (e.g. CRASH_DETECT_WINDOW_S = 0.5) or a setting, referenced from both spots.
- **TDD test:** Patch the constant and assert both start_* methods sleep for the configured window before polling proc exit.

### 33. [P2] src/backend/core/context/budget.py:36

- **What:** self.allocations = {system_prompt:200, character_def:300, user_persona:100, lorebook_cap:500, chat_summary:200, post_history:200, dynamic_state:60}
- **Category:** magic-number | **Effort:** M | **Slice:** Backend configuration & runtim
- **Problem:** Every context layer's token cap is a hardcoded magic number. These caps directly govern how much of each prompt section survives truncation; they are model/context-size dependent (a 4096 vs 8192 window wants different caps) yet are fixed literals unreachable from config or the Settings UI. Combined with the 4096/8192 context mismatch above, the fixed caps plus response_slot/padding can consume a large fraction of a small window.
- **Fix:** Move the allocation table into config (or derive caps as fractions of usable_budget) so they scale with context_size and are overridable.
- **TDD test:** Instantiate ContextBudgetCalculator with a small context_size and assert allocations scale/clamp so history_budget stays >= 0 and layers don't exceed usable_budget.

### 34. [P2] src/backend/core/context/budget.py:64

- **What:** return int(len(text.split()) * 1.3) fallback ratio; timeout=5.0 on /tokenize
- **Category:** magic-number | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** The word-count->token fallback ratio 1.3 and the 5.0s tokenize timeout are hardcoded (the 1.3 literal appears twice, lines 64 and 69, so they can drift). 1.3 is a rough English heuristic and under-counts for many tokenizers, causing the budget to underestimate real token usage and overflow the context when /tokenize is unreachable.
- **Fix:** Hoist TOKENIZE_TIMEOUT_S and TOKENS_PER_WORD to named constants/settings and reference the ratio once.
- **TDD test:** Force the tokenize call to fail and assert count_tokens uses the configured ratio (change the constant, verify the returned estimate changes accordingly).

### 35. [P2] src/backend/db/database.py:39

- **What:** agent_states column defaults 'Living Room' (location), 'Neutral' (mood), 'Casual' (clothes)
- **Category:** content | **Effort:** S | **Slice:** Backend configuration & runtim
- **Problem:** Roleplay stat defaults ('Living Room', 'Neutral', 'Casual') are baked into migration ALTER TABLE SQL (and mirrored in models.py). These are user-facing narrative content/domain assumptions embedded in the schema layer; changing the app's default starting state requires editing raw SQL string literals in the migration, and they can silently diverge from the ORM model column defaults.
- **Fix:** Define these defaults once as named constants (or config) and reference them from both the models.py column server_default and any migration, rather than repeating literals.
- **TDD test:** Assert the agent_states model column defaults equal the migration DEFAULTs via a shared constant so schema and ORM cannot drift.

### 36. [P2] src/backend/core/engine/llm.py:188

- **What:** return [0.1] * 2560
- **Category:** model-assumption | **Effort:** S | **Slice:** Backend LLM + orchestration + 
- **Problem:** The embedding dimension 2560 is hardcoded as a magic number in the pytest/E2E mock. 2560 is the hidden size of the specific Qwen3-4B model currently in models_config.json. If the user swaps the embedding model (the whole point of models_config.json being runtime-configurable), the real embeddings will have a different dimension than the tests assume, so vector-store code/tests validated against 2560-dim vectors will silently diverge from production behavior.
- **Fix:** Define EMBEDDING_DIM as a named constant/setting (e.g. settings.EMBEDDING_DIM) and use it here and anywhere else that assumes a fixed vector width, or derive it once from a live /embedding probe cached at startup.
- **TDD test:** Test that the mock embedding length equals settings.EMBEDDING_DIM, and add a test that flips EMBEDDING_DIM to a different value and confirms the mock/vector-store paths honor it.

### 37. [P2] src/backend/api/chat.py:68

- **What:** new_hunger = max(0, old_hunger - 30)   # eating keyword action
- **Category:** magic-number | **Effort:** M | **Slice:** Backend LLM + orchestration + 
- **Problem:** The narrative eating-action hunger reduction (-30) is a bare magic number, and it is inconsistent with the curated food deltas in ACTIONS_CONFIG on the same file (croissant hunger -35, coffee hunger -10). Two different systems reduce hunger by three different hardcoded amounts with no shared constant, so tuning 'how much a meal satisfies' requires editing multiple literals and they will drift.
- **Fix:** Introduce named constants (e.g. HUNGER_PER_EAT_ACTION) or a small stat-effects config table, and source both the regex-action handler and ACTIONS_CONFIG food items from it.
- **TDD test:** TDD: given state hunger=50, feeding via an **eats ...** action reduces hunger by the configured constant; changing the constant changes the result, proving no hidden literal.

### 38. [P2] src/backend/api/chat.py:139

- **What:** ACTIONS_CONFIG = { 'hug': {..'stats': {'happiness':5,'social':10,'relationship_score':2}}, ... 'necklace': {...'relationship_score':8}}
- **Category:** content | **Effort:** M | **Slice:** Backend LLM + orchestration + 
- **Problem:** The entire quick-action catalog -- button messages and stat-delta magic numbers (happiness/social/hunger/energy/relationship_score) -- is hardcoded inside the chat API route module. These are gameplay-balance values and user-facing copy baked into code; tuning them or localizing the messages means editing the router, and there is no way to configure them per-deployment.
- **Fix:** Move ACTIONS_CONFIG to a JSON/config file (like models_config.json) or a DB table loaded at startup; keep the route thin. Stat deltas become data, message text becomes content that can be edited/localized without code changes.
- **TDD test:** Test that actions load from an injectable config source: patch the config with a custom action + deltas and assert /chat/actions returns it and _apply_action_stats applies the configured deltas.

### 39. [P2] src/backend/api/chat.py:297

- **What:** force_reflect = state.interaction_count % 20 == 0  (repeated at :312, plus .limit(20) at :118, window_size=20 at :125 and bridge.py:175)
- **Category:** magic-number | **Effort:** S | **Slice:** Backend LLM + orchestration + 
- **Problem:** The reflection cadence '20' is hardcoded in five places (two %20 checks, the message-fetch .limit(20), reflect(window_size=20), and bridge.Brain.reflect default). The reflection interval and the reflection window happen to share the literal 20 but are conceptually independent; changing how often the character reflects, or how many messages it reflects over, requires hunting down multiple literals that can silently disagree.
- **Fix:** Add settings/constants REFLECTION_INTERVAL and REFLECTION_WINDOW; use REFLECTION_INTERVAL for the %-checks and REFLECTION_WINDOW for the fetch limit + window_size default. Single source each.
- **TDD test:** Set REFLECTION_INTERVAL=3 and assert force_reflect becomes true exactly on the 3rd interaction; set REFLECTION_WINDOW=5 and assert reflect() only consumes the last 5 messages.

### 40. [P2] src/backend/core/orchestration/bridge.py:108

- **What:** est_tokens = len(line) // 4 + 5   (history token estimate)
- **Category:** magic-number | **Effort:** M | **Slice:** Backend LLM + orchestration + 
- **Problem:** History budgeting estimates tokens with a hardcoded '4 chars/token + 5' heuristic, while ContextBudgetCalculator.count_tokens falls back to a different hardcoded heuristic 'words * 1.3' (budget.py:64,68). Two divergent token estimators guard the same context window; they can under/over-count relative to each other and to the real tokenizer, risking prompt overflow or wasted budget. The '2048' history_budget fallback on bridge.py:101 is another bare magic number.
- **Fix:** Centralize token estimation in one helper (ideally calling the tokenize endpoint, else one shared CHARS_PER_TOKEN constant) and reuse it in both bridge.py and budget.py. Replace the 2048 literal with the calculator's computed history_budget or a named DEFAULT_HISTORY_BUDGET.
- **TDD test:** Test that bridge history trimming and budget.count_tokens fallback use the same estimator constant; feed a known string and assert both return the same estimate.

### 41. [P2] src/backend/core/context/budget.py:36

- **What:** self.allocations = {'system_prompt':200,'character_def':300,'user_persona':100,'lorebook_cap':500,'chat_summary':200,'post_history':200,'dynamic_state':60}
- **Category:** magic-number | **Effort:** M | **Slice:** Backend LLM + orchestration + 
- **Problem:** All per-layer token allocation caps are hardcoded in the constructor. These directly shape how much of each prompt layer survives under a given context size, yet they cannot be tuned without editing code and are not scaled to the configurable context_size (which ranges from 4096 in models_config.json to 65536 in the example). At 4096 context these fixed caps (sum 1560 + 1024 response + 128 pad) consume most of the window, leaving little history budget.
- **Fix:** Move allocations into settings/config (or express them as fractions of usable_budget) so they can be tuned per model/context size; validate they fit within usable_budget.
- **TDD test:** Test get_budget with context_size=4096 asserts history_budget stays >= a sane floor; test that overriding allocations via config changes history_budget accordingly.

### 42. [P2] src/backend/core/context/compressor.py:34

- **What:** energy<=10 / energy<=30 / hunger>=90 / hunger>=70 / score<=20 / score<=50 / score<=80 thresholds
- **Category:** magic-number | **Effort:** M | **Slice:** Backend LLM + orchestration + 
- **Problem:** The physiological/relationship narrative thresholds that drive prompt modifiers are hardcoded here, and they must stay consistent with the stat math elsewhere (engine.should_be_sleeping uses energy<20; engine drain rates ENERGY_DRAIN_RATE=5 etc.). E.g. compressor says 'CRITICAL EXHAUSTION' at energy<=10 while should_be_sleeping forces sleep at energy<20 -- overlapping, uncoordinated thresholds spread across files that can drift so the prompt state contradicts the simulated state.
- **Fix:** Extract stat thresholds (EXHAUSTION_CRITICAL, EXHAUSTION_LOW, HUNGER_STARVING, HUNGER_HUNGRY, REL_STRANGER/ACQUAINTANCE/FRIEND) into a shared constants/config module imported by both compressor.py and engine.py.
- **TDD test:** Test that compress_state emits 'CRITICAL EXHAUSTION' exactly at the shared EXHAUSTION_CRITICAL constant boundary, and that changing the constant moves the boundary.

### 43. [P2] src/backend/core/engine/llm.py:96

- **What:** timeout=120.0 (complete), timeout=300.0 (complete_stream:172), timeout=5.0 health/tokenize, httpx.AsyncClient(timeout=120.0) at :14
- **Category:** timeout-retry | **Effort:** S | **Slice:** Backend LLM + orchestration + 
- **Problem:** LLM request timeouts are scattered hardcoded floats (120.0 non-stream, 300.0 stream, 5.0 health, plus 60.0 in vector_store sync embed and 5.0 in budget.count_tokens). On a slow local model a long generation can exceed 120s and fail, and there is no single knob to raise it. The values also disagree between the non-streaming and streaming paths for the same model with no documented reason.
- **Fix:** Add settings.LLM_REQUEST_TIMEOUT / LLM_STREAM_TIMEOUT / LLM_HEALTH_TIMEOUT and reference them everywhere instead of literals.
- **TDD test:** Test that ChatOpenAI is constructed with timeout == settings.LLM_REQUEST_TIMEOUT (patch the setting and assert the client picks it up).

### 44. [P2] src/backend/core/engine/engine.py:132

- **What:** if len(new_active) > 1500: new_active = '...' + new_active[-1000:]
- **Category:** magic-number | **Effort:** S | **Slice:** Backend LLM + orchestration + 
- **Problem:** The rolling active-summary trim uses hardcoded 1500 (trigger) and 1000 (kept tail) character budgets. This is a context-budget concern expressed in raw chars, disconnected from budget.py's token allocations (chat_summary cap = 200 tokens). The summary can grow to ~1000 chars (~250+ tokens), potentially exceeding the 200-token chat_summary allocation the budgeter reserves, so the two subsystems disagree about how big the summary may be.
- **Fix:** Derive the summary char/token cap from the budgeter's chat_summary allocation (or a shared SUMMARY_MAX constant) rather than standalone 1500/1000 literals.
- **TDD test:** Test that evolve_character keeps active_summary within the configured summary cap and that the cap is a single named constant.
