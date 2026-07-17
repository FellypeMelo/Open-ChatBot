import copy
import os
import re
import subprocess
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, List
from src.backend.core.config import settings

logger = logging.getLogger(__name__)


def get_oneapi_env() -> Dict[str, str]:
    """Build environment dict with Intel oneAPI variables merged in.

    Strategy:
    1. If oneAPI vars are ALREADY in os.environ (e.g. run.bat called setvars.bat),
       just return os.environ.copy() — no need to re-invoke setvars.bat.
    2. Otherwise, execute setvars.bat in a subprocess and parse the output.
    3. During pytest, skip entirely to avoid slow subprocess calls.
    """
    env = os.environ.copy()

    if settings.TESTING:
        logger.debug("[oneapi] Skipping env loading (pytest detected)")
        return env

    # Check if oneAPI vars are already inherited (e.g. from run.bat)
    if "ONEAPI_ROOT" in env or "SETVARS_COMPLETED" in env:
        logger.info(
            "[oneapi] oneAPI variables already present in environment (inherited from parent shell)."
        )
        return env

    setvars_path = Path("C:/Program Files (x86)/Intel/oneAPI/setvars.bat")
    if not setvars_path.exists():
        logger.warning(f"[oneapi] setvars.bat not found at {setvars_path}")
        return env

    logger.info(f"[oneapi] Loading variables from {setvars_path} ...")
    try:
        cmd = f'call "{setvars_path}" && set'
        proc = subprocess.run(
            cmd, capture_output=True, text=True, shell=True, timeout=60
        )
        if proc.returncode == 0:
            parsed = 0
            for line in proc.stdout.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v
                    parsed += 1
            logger.info(f"[oneapi] Successfully parsed {parsed} environment variables.")
        else:
            logger.warning(f"[oneapi] setvars.bat returned code {proc.returncode}")
            if proc.stderr:
                logger.warning(f"[oneapi] stderr: {proc.stderr[:500]}")
    except subprocess.TimeoutExpired:
        logger.error("[oneapi] setvars.bat timed out after 60 seconds!")
    except Exception as e:
        logger.warning(f"[oneapi] Error loading variables: {e}")
    return env


CONFIG_FILE = Path("models_config.json")

# llama-server spawn tunables (named instead of magic literals sprinkled across
# start_inference / start_embedding).
EMBEDDING_UBATCH_SIZE = 2048
EMBEDDING_POOLING = "cls"
CRASH_DETECT_SECONDS = 0.5

DEFAULT_CONFIG = {
    "inference": {
        "binary_path": "llama_bin/llama-server.exe",
        "model_path": "models/model.gguf",
        "port": 8080,
        "threads": 4,
        "gpu_layers": -1,
        "context_size": settings.CONTEXT_SIZE,
        "additional_args": "--cache-type-k q8_0 --cache-type-v turbo3 --flash-attn on --parallel 1",
    },
    "embedding": {
        "binary_path": "llama_bin/llama-server.exe",
        "model_path": "models/model.gguf",
        "port": 8080,
        "threads": 4,
        "gpu_layers": -1,
        "additional_args": "--flash-attn on",
    },
}


class LlamaServerRunner:
    def __init__(self):
        self.inference_proc = None
        self.embedding_proc = None
        # Resolve the project root once at init time so relative paths always work
        self._project_root = Path.cwd()
        logger.info(f"[runner] Initialized. Project root (CWD): {self._project_root}")
        self.load_config()

    def load_config(self):
        updated = False
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
                # Ensure all keys exist
                for key in ["inference", "embedding"]:
                    if key not in self.config:
                        self.config[key] = copy.deepcopy(DEFAULT_CONFIG[key])
                        updated = True
                    else:
                        for subkey, val in DEFAULT_CONFIG[key].items():
                            if subkey not in self.config[key]:
                                self.config[key][subkey] = val
                                updated = True

                # KV cache-type handling for the turboquant SYCL binary. Its
                # flash-attn vec kernel only accepts a *supported* K/V pair; an
                # invalid pair (e.g. q4_0 K + turbo3 V) makes llama-server abort
                # at boot ("fattn.cpp: Not match KV type in vec") and crash-loop
                # on 503. The recommended default is near-lossless K (q8_0) with
                # a compressed V (turbo3).
                #
                # Only INJECT a cache-type when the user set none. Never rewrite
                # an explicit choice: a previous migration force-replaced q8_0
                # with q4_0 on every startup, silently corrupting a valid config
                # and breaking inference. That behavior is intentionally removed.
                inf_args = self.config["inference"].get("additional_args", "")
                if "--cache-type-k" not in inf_args:
                    inf_args = (
                        inf_args + " --cache-type-k q8_0 --cache-type-v turbo3"
                    ).strip()
                    updated = True
                inf_args, changed = self._heal_flash_attn(inf_args)
                updated = updated or changed
                if "--parallel" not in inf_args and "-np" not in inf_args:
                    inf_args = (inf_args + " --parallel 1").strip()
                    updated = True
                self.config["inference"]["additional_args"] = inf_args

                # Migrate old embedding settings
                emb_args = self.config["embedding"].get("additional_args", "")
                emb_args, changed = self._heal_flash_attn(emb_args)
                updated = updated or changed
                self.config["embedding"]["additional_args"] = emb_args

                # Migrate embedding port to share port 8080 with inference if it's the old default (8081)
                # and no separate model path is defined (or they are identical)
                if (
                    self.config["embedding"]["port"] == 8081
                    and self.config["inference"]["port"] == 8080
                ):
                    emb_model = self.config["embedding"].get("model_path", "")
                    inf_model = self.config["inference"].get("model_path", "")
                    if not emb_model or emb_model == inf_model:
                        logger.info(
                            "Migrating embedding server to share port 8080 with inference server for consolidation."
                        )
                        self.config["embedding"]["port"] = 8080
                        updated = True

            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                logger.warning(
                    f"Could not load models_config.json, using defaults: {e}"
                )
                self.config = copy.deepcopy(DEFAULT_CONFIG)
                updated = True
            except Exception:
                logger.exception("Unexpected error loading models_config.json")
                self.config = copy.deepcopy(DEFAULT_CONFIG)
                updated = True
        else:
            self.config = copy.deepcopy(DEFAULT_CONFIG)
            models = self.get_available_models()
            if models:
                self.config["inference"]["model_path"] = f"models/{models[0]}"
                if len(models) > 1:
                    self.config["embedding"]["model_path"] = f"models/{models[1]}"
                else:
                    self.config["embedding"]["model_path"] = f"models/{models[0]}"
            updated = True

        if updated:
            self.save_config()

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            logger.exception("Failed to write to models_config.json")

    def get_available_models(self) -> List[str]:
        models_dir = Path("models")
        if not models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
        return [f.name for f in models_dir.glob("*.gguf")]

    def get_available_binaries(self) -> List[str]:
        bin_dir = Path("llama_bin")
        if not bin_dir.exists():
            return []

        binaries = []
        for f in bin_dir.iterdir():
            if f.is_file():
                name = f.name
                if "server" in name or "llama" in name:
                    if (
                        os.name == "nt"
                        and not name.endswith(".exe")
                        and not name.endswith(".dll")
                    ):
                        continue
                    if name.endswith(".dll"):
                        continue
                    binaries.append(name)
        return sorted(binaries)

    def get_status(self) -> Dict[str, Any]:
        inference_running = self._is_alive(self.inference_proc)
        embedding_running = self._is_alive(self.embedding_proc)

        # Consolidation check: if ports are identical, embedding running status matches inference
        if self._is_consolidated:
            embedding_running = inference_running

        return {
            "inference": {
                "running": inference_running,
                "config": self.config["inference"],
            },
            "embedding": {
                "running": embedding_running,
                "config": self.config["embedding"],
            },
            "available_models": self.get_available_models(),
            "available_binaries": self.get_available_binaries(),
        }

    @property
    def _is_consolidated(self) -> bool:
        """True when the embedding server shares the inference server's port."""
        return self.config["embedding"]["port"] == self.config["inference"]["port"]

    @staticmethod
    def _is_alive(proc) -> bool:
        """True if a spawned process exists and has not yet exited."""
        return proc is not None and proc.poll() is None

    @staticmethod
    def _ensure_embedding_args(extra_args: list) -> None:
        """Add the embedding-server flags in place, without clobbering an explicit
        user choice."""
        if "--embedding" not in extra_args and "-emb" not in extra_args:
            extra_args.append("--embedding")
        if "--ubatch-size" not in extra_args and "-ub" not in extra_args:
            extra_args.extend(["--ubatch-size", str(EMBEDDING_UBATCH_SIZE)])
        if "--pooling" not in extra_args:
            extra_args.extend(["--pooling", EMBEDDING_POOLING])

    @staticmethod
    def _heal_flash_attn(args: str) -> tuple:
        """llama-server's -fa now requires an explicit value: upgrade a bare
        --flash-attn to '--flash-attn on' and append it when absent. Returns
        (healed_args, changed)."""
        healed = re.sub(
            r"--flash-attn(?!\s+(?:on|off|auto)\b)", "--flash-attn on", args
        )
        changed = healed != args
        if "--flash-attn" not in healed:
            healed = (healed + " --flash-attn on").strip()
            changed = True
        return healed, changed

    def _resolve_path(self, rel_path: str) -> Path:
        """Resolve a relative path against the project root captured at init time."""
        p = Path(rel_path)
        if p.is_absolute():
            return p
        return (self._project_root / p).resolve()

    def _resolve_binary_and_model(self, cfg: dict, label: str):
        """Resolve (with llama_bin fallback) and validate the binary + model for
        a server config. Returns (binary, model, is_hf, model_str) or None on a
        fatal resolution error (missing binary/model). Shared by both starters."""
        binary = self._resolve_path(cfg["binary_path"])
        model_str = cfg["model_path"]

        # Detect Hugging Face model paths (owner/repo) BEFORE resolving to disk.
        is_hf = bool(
            model_str
            and "/" in model_str
            and not model_str.startswith("models/")
            and not Path(model_str).is_absolute()
        )
        model = self._resolve_path(model_str) if (model_str and not is_hf) else None

        logger.info(f"[{label}] Resolved binary: {binary} (exists={binary.exists()})")
        if not binary.exists():
            binary = self._resolve_path(f"llama_bin/{Path(cfg['binary_path']).name}")
            logger.info(
                f"[{label}] Fallback binary: {binary} (exists={binary.exists()})"
            )
            if not binary.exists():
                logger.error(f"[{label}] ABORT: binary not found at {binary}")
                return None

        if not is_hf and model and (not model.exists() or not model.is_file()):
            logger.error(f"[{label}] ABORT: model not found at {model}")
            return None

        return binary, model, is_hf, model_str

    def _base_args(self, cfg: dict, binary, model, is_hf, model_str, label: str):
        """Build the argv common to both servers: binary, model, port, threads,
        context (if configured) and GPU layers."""
        args = [str(binary)]
        if is_hf:
            args.extend(["-hf", model_str])
        else:
            args.extend(["-m", str(model)])

        threads = int(cfg["threads"])
        if threads <= 0:
            threads = max(1, (os.cpu_count() or 8) // 2)
            logger.info(f"[{label}] Auto-detected thread count: {threads}")

        args.extend(["--port", str(cfg["port"]), "-t", str(threads)])
        if cfg.get("context_size"):
            args.extend(["-c", str(cfg["context_size"])])

        gpu_layers = int(cfg["gpu_layers"])
        if gpu_layers >= 0:
            args.extend(["-ngl", str(gpu_layers)])
        return args

    def _spawn_process(
        self, args, log_name: str, proc_attr: str, log_attr: str, binary, label: str
    ) -> bool:
        """Launch a llama-server: open its log, build the oneAPI/SYCL/PATH env,
        Popen it, and detect an instant crash. Records the process/log-file on
        self via proc_attr/log_attr. Shared by both starters."""
        logger.info(f"[{label}] Full command: {' '.join(args)}")
        try:
            log_path = self._project_root / "logs"
            log_path.mkdir(exist_ok=True)
            out_log_path = log_path / log_name
            log_file = open(out_log_path, "w", encoding="utf-8")
            setattr(self, log_attr, log_file)

            spawn_env = get_oneapi_env()
            # Add the binary's dir to PATH so Windows finds its DLLs (ggml.dll).
            current_path = spawn_env.get("PATH", "")
            bin_dir = str(binary.parent.absolute())
            if bin_dir not in current_path:
                spawn_env["PATH"] = (
                    f"{bin_dir}{os.pathsep}{current_path}" if current_path else bin_dir
                )
            # SYCL JIT-compiles turbo kernels on first run; persist the cache so
            # later starts don't blow past the health-check warmup window.
            spawn_env.setdefault("SYCL_CACHE_PERSISTENT", "1")

            proc = subprocess.Popen(
                args,
                stdout=log_file,
                stderr=log_file,
                env=spawn_env,
                cwd=str(self._project_root),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            setattr(self, proc_attr, proc)
            logger.info(f"[{label}] Started (PID={proc.pid}).")

            # Wait briefly to catch instant crashes (e.g. missing DLL = 0xC0000135).
            time.sleep(CRASH_DETECT_SECONDS)
            exit_code = proc.poll()
            if exit_code is not None:
                log_file.flush()
                log_file.close()
                log_content = out_log_path.read_text(encoding="utf-8", errors="replace")
                try:
                    hex_code = f"0x{int(exit_code) & 0xFFFFFFFF:08X}"
                except (TypeError, ValueError):
                    hex_code = str(exit_code)
                logger.error(
                    f"[{label}] Process crashed immediately: exit_code={exit_code} "
                    f"(hex={hex_code})"
                )
                logger.error(
                    f"[{label}] Log output: {log_content[:2000] if log_content else '<empty>'}"
                )
                setattr(self, proc_attr, None)
                setattr(self, log_attr, None)
                return False

            logger.info(
                f"[{label}] Running after {CRASH_DETECT_SECONDS}s. Log: {out_log_path}"
            )
            return True
        except OSError as e:
            logger.exception(f"[{label}] OSError spawning process: {e}")
            self._close_log_file(log_attr)
            return False
        except Exception as e:
            logger.exception(f"[{label}] Unexpected error: {e}")
            self._close_log_file(log_attr)
            return False

    def start_inference(self) -> bool:
        self.stop_inference()
        cfg = self.config["inference"]
        logger.info(f"[start_inference] Starting with config: {json.dumps(cfg)}")

        resolved = self._resolve_binary_and_model(cfg, "start_inference")
        if resolved is None:
            return False
        binary, model, is_hf, model_str = resolved
        args = self._base_args(cfg, binary, model, is_hf, model_str, "start_inference")

        extra = cfg.get("additional_args", "").strip()
        extra_args = extra.split() if extra else []

        # Consolidation: if the embedding server shares this port, serve both.
        if self._is_consolidated:
            self._ensure_embedding_args(extra_args)

        # Enforce --parallel 1 unless set, to save slot-cache memory.
        if "--parallel" not in extra_args and "-np" not in extra_args:
            extra_args.extend(["--parallel", "1"])

        args.extend(extra_args)
        return self._spawn_process(
            args,
            "llama_inference.log",
            "inference_proc",
            "inf_log_file",
            binary,
            "start_inference",
        )

    def start_embedding(self) -> bool:
        cfg = self.config["embedding"]

        # Consolidation: if ports match, the inference server serves embeddings.
        if self._is_consolidated:
            logger.info(
                "[start_embedding] Consolidated server mode: using inference server for embeddings."
            )
            return (
                True if self._is_alive(self.inference_proc) else self.start_inference()
            )

        self.stop_embedding()
        logger.info("[start_embedding] Starting dedicated embedding server.")

        resolved = self._resolve_binary_and_model(cfg, "start_embedding")
        if resolved is None:
            return False
        binary, model, is_hf, model_str = resolved
        args = self._base_args(cfg, binary, model, is_hf, model_str, "start_embedding")

        extra = cfg.get("additional_args", "").strip()
        extra_args = extra.split() if extra else []
        self._ensure_embedding_args(extra_args)
        args.extend(extra_args)

        return self._spawn_process(
            args,
            "llama_embedding.log",
            "embedding_proc",
            "emb_log_file",
            binary,
            "start_embedding",
        )

    def _close_log_file(self, attr_name: str):
        f = getattr(self, attr_name, None)
        if f:
            try:
                f.close()
            except Exception:
                pass
        setattr(self, attr_name, None)

    @staticmethod
    def _terminate_and_reap(proc: subprocess.Popen, label: str):
        """terminate() -> wait(); on timeout kill() -> wait() again so the
        child is always reaped and the port/GPU memory it held is actually
        freed before the caller starts a replacement process."""
        try:
            proc.terminate()
            proc.wait(timeout=3)
            return
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            return
        try:
            proc.kill()
            proc.wait(timeout=3)
        except Exception:
            logger.warning(f"{label}: process did not reap after kill()")

    def stop_inference(self):
        if self.inference_proc is not None:
            logger.info("Stopping Llama Inference Server...")
            self._terminate_and_reap(self.inference_proc, "stop_inference")
            self.inference_proc = None

        self._close_log_file("inf_log_file")

    def stop_embedding(self):
        # Consolidation check: if sharing port, stop_embedding is a noop
        if self.config["embedding"]["port"] == self.config["inference"]["port"]:
            logger.info("Consolidated server mode: stop_embedding is a no-op.")
            return

        if self.embedding_proc is not None:
            logger.info("Stopping Llama Embedding Server...")
            self._terminate_and_reap(self.embedding_proc, "stop_embedding")
            self.embedding_proc = None

        self._close_log_file("emb_log_file")

    def stop_all(self):
        self.stop_inference()
        self.stop_embedding()


runner = LlamaServerRunner()
