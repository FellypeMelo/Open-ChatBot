import os
import subprocess
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, List

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
    import sys

    if "pytest" in sys.modules:
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
DEFAULT_CONFIG = {
    "inference": {
        "binary_path": "llama_bin/llama-server.exe",
        "model_path": "",
        "port": 8080,
        "threads": 4,
        "gpu_layers": -1,
        "context_size": 4096,
        "additional_args": "--cache-type-k q4_0 --cache-type-v q4_0 --flash-attn --parallel 1",
    },
    "embedding": {
        "binary_path": "llama_bin/llama-server.exe",
        "model_path": "",
        "port": 8080,
        "threads": 4,
        "gpu_layers": -1,
        "additional_args": "--flash-attn",
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
                        self.config[key] = DEFAULT_CONFIG[key].copy()
                        updated = True
                    else:
                        for subkey, val in DEFAULT_CONFIG[key].items():
                            if subkey not in self.config[key]:
                                self.config[key][subkey] = val
                                updated = True

                # Migrate config files containing old q8_0 Cache parameters to q4_0 for inference
                inf_args = self.config["inference"].get("additional_args", "")
                if "q8_0" in inf_args:
                    inf_args = inf_args.replace("q8_0", "q4_0")
                    updated = True
                if "q4_0" not in inf_args:
                    inf_args = (
                        inf_args + " --cache-type-k q4_0 --cache-type-v q4_0"
                    ).strip()
                    updated = True
                if "--flash-attn" not in inf_args:
                    inf_args = (inf_args + " --flash-attn").strip()
                    updated = True
                if "--parallel" not in inf_args and "-np" not in inf_args:
                    inf_args = (inf_args + " --parallel 1").strip()
                    updated = True
                self.config["inference"]["additional_args"] = inf_args

                # Migrate old embedding settings
                emb_args = self.config["embedding"].get("additional_args", "")
                if "--flash-attn" not in emb_args:
                    emb_args = (emb_args + " --flash-attn").strip()
                    updated = True
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
                self.config = DEFAULT_CONFIG.copy()
                updated = True
            except Exception:
                logger.exception("Unexpected error loading models_config.json")
                self.config = DEFAULT_CONFIG.copy()
                updated = True
        else:
            self.config = DEFAULT_CONFIG.copy()
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
        inference_running = (
            self.inference_proc is not None and self.inference_proc.poll() is None
        )
        embedding_running = (
            self.embedding_proc is not None and self.embedding_proc.poll() is None
        )

        # Consolidation check: if ports are identical, embedding running status matches inference
        if self.config["embedding"]["port"] == self.config["inference"]["port"]:
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

    def _resolve_path(self, rel_path: str) -> Path:
        """Resolve a relative path against the project root captured at init time."""
        p = Path(rel_path)
        if p.is_absolute():
            return p
        return (self._project_root / p).resolve()

    def start_inference(self) -> bool:
        self.stop_inference()
        cfg = self.config["inference"]

        logger.info("[start_inference] ======= BEGIN =======")
        logger.info(f"[start_inference] Current CWD: {Path.cwd()}")
        logger.info(f"[start_inference] Project root: {self._project_root}")
        logger.info(f"[start_inference] Config: {json.dumps(cfg, indent=2)}")

        binary = self._resolve_path(cfg["binary_path"])
        model_str = cfg["model_path"]

        # Detect Hugging Face model paths BEFORE resolving to disk path
        is_hf = False
        if (
            model_str
            and "/" in model_str
            and not model_str.startswith("models/")
            and not Path(model_str).is_absolute()
        ):
            is_hf = True

        model = self._resolve_path(model_str) if (model_str and not is_hf) else None

        logger.info(
            f"[start_inference] Resolved binary: {binary} (exists={binary.exists()})"
        )

        if not binary.exists():
            # Try fallback
            binary = self._resolve_path(f"llama_bin/{Path(cfg['binary_path']).name}")
            logger.info(
                f"[start_inference] Fallback binary: {binary} (exists={binary.exists()})"
            )
            if not binary.exists():
                logger.error(f"[start_inference] ABORT: binary not found at {binary}")
                return False

        if model:
            logger.info(
                f"[start_inference] Resolved model: {model} (exists={model.exists()}, is_hf={is_hf})"
            )
        elif is_hf:
            logger.info(f"[start_inference] HF model path: {model_str}")

        if not is_hf and model and (not model.exists() or not model.is_file()):
            logger.error(f"[start_inference] ABORT: model not found at {model}")
            return False

        args = [str(binary)]
        if is_hf:
            args.extend(["-hf", model_str])
        else:
            args.extend(["-m", str(model)])

        threads = int(cfg["threads"])
        if threads <= 0:
            threads = max(1, (os.cpu_count() or 8) // 2)
            logger.info(f"[start_inference] Auto-detected thread count: {threads}")

        args.extend(
            [
                "--port",
                str(cfg["port"]),
                "-t",
                str(threads),
                "-c",
                str(cfg["context_size"]),
            ]
        )

        gpu_layers = int(cfg["gpu_layers"])
        if gpu_layers >= 0:
            args.extend(["-ngl", str(gpu_layers)])

        extra = cfg.get("additional_args", "").strip()
        extra_args = extra.split() if extra else []

        # Consolidation check: if embedding port matches inference, make sure --embedding is enabled
        emb_cfg = self.config.get("embedding", {})
        if emb_cfg.get("port") == cfg["port"]:
            if "--embedding" not in extra_args and "-emb" not in extra_args:
                extra_args.append("--embedding")
            if "--ubatch-size" not in extra_args and "-ub" not in extra_args:
                extra_args.extend(["--ubatch-size", "2048"])
            if "--pooling" not in extra_args:
                extra_args.extend(["--pooling", "cls"])

        # Enforce --parallel 1 if not defined to save memory allocations for slot caches
        if "--parallel" not in extra_args and "-np" not in extra_args:
            extra_args.extend(["--parallel", "1"])

        if extra_args:
            args.extend(extra_args)

        cmd_str = " ".join(args)
        logger.info(f"[start_inference] Full command: {cmd_str}")

        try:
            log_path = self._project_root / "logs"
            log_path.mkdir(exist_ok=True)
            inf_log_path = log_path / "llama_inference.log"
            self.inf_log_file = open(inf_log_path, "w", encoding="utf-8")

            spawn_env = get_oneapi_env()

            # Add binary parent directory to PATH so Windows finds DLLs like ggml.dll
            current_path = spawn_env.get("PATH", "")
            bin_dir = str(binary.parent.absolute())
            if bin_dir not in current_path:
                spawn_env["PATH"] = (
                    f"{bin_dir}{os.pathsep}{current_path}" if current_path else bin_dir
                )

            # Log critical env vars for diagnosis
            sycl_vars = {
                k: v
                for k, v in spawn_env.items()
                if "SYCL" in k.upper() or "ONEAPI" in k.upper() or k == "PATH"
            }
            logger.info(
                f"[start_inference] Key env vars: ONEAPI_ROOT={spawn_env.get('ONEAPI_ROOT', '<MISSING>')}, "
                f"SETVARS_COMPLETED={spawn_env.get('SETVARS_COMPLETED', '<MISSING>')}"
            )

            self.inference_proc = subprocess.Popen(
                args,
                stdout=self.inf_log_file,
                stderr=self.inf_log_file,
                env=spawn_env,
                cwd=str(self._project_root),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            logger.info(
                f"[start_inference] Popen succeeded. PID={self.inference_proc.pid}"
            )

            # Wait briefly to detect instant crashes (e.g. DLL not found = 0xC0000135)
            time.sleep(0.5)
            exit_code = self.inference_proc.poll()
            if exit_code is not None:
                # Process died immediately
                self.inf_log_file.flush()
                self.inf_log_file.close()
                # Read what the log captured
                log_content = inf_log_path.read_text(encoding="utf-8", errors="replace")
                try:
                    hex_code = f"0x{int(exit_code) & 0xFFFFFFFF:08X}"
                except (TypeError, ValueError):
                    hex_code = str(exit_code)
                logger.error(
                    f"[start_inference] PROCESS CRASHED IMMEDIATELY! exit_code={exit_code} (hex={hex_code})"
                )
                logger.error(
                    f"[start_inference] Log output: {log_content[:2000] if log_content else '<empty>'}"
                )
                self.inference_proc = None
                self.inf_log_file = None
                return False

            logger.info(
                f"[start_inference] Process still running after 0.5s. Log file: {inf_log_path}"
            )
            logger.info("[start_inference] ======= SUCCESS =======")
            return True
        except OSError as e:
            logger.exception(f"[start_inference] OSError spawning process: {e}")
            return False
        except Exception as e:
            logger.exception(f"[start_inference] Unexpected error: {e}")
            return False

    def start_embedding(self) -> bool:
        cfg = self.config["embedding"]
        inf_cfg = self.config["inference"]

        # Consolidation check: if ports match, we use inference server for both
        if cfg["port"] == inf_cfg["port"]:
            logger.info(
                "[start_embedding] Consolidated server mode: using inference server for embeddings."
            )
            inference_running = (
                self.inference_proc is not None and self.inference_proc.poll() is None
            )
            if not inference_running:
                return self.start_inference()
            return True

        self.stop_embedding()
        cfg = self.config["embedding"]

        logger.info("[start_embedding] ======= BEGIN =======")

        binary = self._resolve_path(cfg["binary_path"])
        model_str = cfg["model_path"]

        # Detect HF model paths BEFORE resolving
        is_hf = False
        if (
            model_str
            and "/" in model_str
            and not model_str.startswith("models/")
            and not Path(model_str).is_absolute()
        ):
            is_hf = True

        model = self._resolve_path(model_str) if (model_str and not is_hf) else None

        logger.info(
            f"[start_embedding] Resolved binary: {binary} (exists={binary.exists()})"
        )

        if not binary.exists():
            binary = self._resolve_path(f"llama_bin/{Path(cfg['binary_path']).name}")
            if not binary.exists():
                logger.error(f"[start_embedding] ABORT: binary not found at {binary}")
                return False

        if not is_hf and model and (not model.exists() or not model.is_file()):
            logger.error(f"[start_embedding] ABORT: model not found at {model}")
            return False

        args = [str(binary)]
        if is_hf:
            args.extend(["-hf", model_str])
        else:
            args.extend(["-m", str(model)])

        threads = int(cfg["threads"])
        if threads <= 0:
            threads = max(1, (os.cpu_count() or 8) // 2)

        args.extend(
            [
                "--port",
                str(cfg["port"]),
                "-t",
                str(threads),
                "--embedding",
                "--ubatch-size",
                "2048",
            ]
        )

        gpu_layers = int(cfg["gpu_layers"])
        if gpu_layers >= 0:
            args.extend(["-ngl", str(gpu_layers)])

        extra = cfg.get("additional_args", "").strip()
        extra_args = extra.split() if extra else []
        if "--pooling" not in extra_args:
            extra_args.extend(["--pooling", "cls"])
        if extra_args:
            args.extend(extra_args)

        logger.info(f"[start_embedding] Full command: {' '.join(args)}")
        try:
            log_path = self._project_root / "logs"
            log_path.mkdir(exist_ok=True)
            emb_log_path = log_path / "llama_embedding.log"
            self.emb_log_file = open(emb_log_path, "w", encoding="utf-8")

            spawn_env = get_oneapi_env()

            # Add binary parent directory to PATH so Windows finds DLLs like ggml.dll
            current_path = spawn_env.get("PATH", "")
            bin_dir = str(binary.parent.absolute())
            if bin_dir not in current_path:
                spawn_env["PATH"] = (
                    f"{bin_dir}{os.pathsep}{current_path}" if current_path else bin_dir
                )

            self.embedding_proc = subprocess.Popen(
                args,
                stdout=self.emb_log_file,
                stderr=self.emb_log_file,
                env=spawn_env,
                cwd=str(self._project_root),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            logger.info(
                f"[start_embedding] Popen succeeded. PID={self.embedding_proc.pid}"
            )

            # Wait briefly to detect instant crashes
            time.sleep(0.5)
            exit_code = self.embedding_proc.poll()
            if exit_code is not None:
                self.emb_log_file.flush()
                self.emb_log_file.close()
                log_content = emb_log_path.read_text(encoding="utf-8", errors="replace")
                try:
                    hex_code = f"0x{int(exit_code) & 0xFFFFFFFF:08X}"
                except (TypeError, ValueError):
                    hex_code = str(exit_code)
                logger.error(
                    f"[start_embedding] PROCESS CRASHED IMMEDIATELY! exit_code={exit_code} (hex={hex_code})"
                )
                logger.error(
                    f"[start_embedding] Log output: {log_content[:2000] if log_content else '<empty>'}"
                )
                self.embedding_proc = None
                self.emb_log_file = None
                return False

            logger.info("[start_embedding] ======= SUCCESS =======")
            return True
        except OSError as e:
            logger.exception(f"[start_embedding] OSError spawning process: {e}")
            return False
        except Exception as e:
            logger.exception(f"[start_embedding] Unexpected error: {e}")
            return False

    def stop_inference(self):
        if self.inference_proc is not None:
            logger.info("Stopping Llama Inference Server...")
            try:
                self.inference_proc.terminate()
                self.inference_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    self.inference_proc.kill()
                except Exception:
                    pass
            except Exception:
                pass
            self.inference_proc = None

        if hasattr(self, "inf_log_file") and self.inf_log_file:
            try:
                self.inf_log_file.close()
            except Exception:
                pass
            self.inf_log_file = None

    def stop_embedding(self):
        # Consolidation check: if sharing port, stop_embedding is a noop
        if self.config["embedding"]["port"] == self.config["inference"]["port"]:
            logger.info("Consolidated server mode: stop_embedding is a no-op.")
            return

        if self.embedding_proc is not None:
            logger.info("Stopping Llama Embedding Server...")
            try:
                self.embedding_proc.terminate()
                self.embedding_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    self.embedding_proc.kill()
                except Exception:
                    pass
            except Exception:
                pass
            self.embedding_proc = None

        if hasattr(self, "emb_log_file") and self.emb_log_file:
            try:
                self.emb_log_file.close()
            except Exception:
                pass
            self.emb_log_file = None

    def stop_all(self):
        self.stop_inference()
        self.stop_embedding()


runner = LlamaServerRunner()
