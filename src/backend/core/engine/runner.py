import os
import subprocess
import logging
import json
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

CONFIG_FILE = Path("models_config.json")
DEFAULT_CONFIG = {
    "inference": {
        "binary_path": "llama_bin/llama-server.exe",
        "model_path": "",
        "port": 8080,
        "threads": 4,
        "gpu_layers": -1,
        "context_size": 4096,
        "additional_args": "--cache-type-k q4_0 --cache-type-v q4_0 --flash-attn --parallel 1"
    },
    "embedding": {
        "binary_path": "llama_bin/llama-server.exe",
        "model_path": "",
        "port": 8080,
        "threads": 4,
        "gpu_layers": -1,
        "additional_args": "--flash-attn"
    }
}

class LlamaServerRunner:
    def __init__(self):
        self.inference_proc = None
        self.embedding_proc = None
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
                    inf_args = (inf_args + " --cache-type-k q4_0 --cache-type-v q4_0").strip()
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
                if self.config["embedding"]["port"] == 8081 and self.config["inference"]["port"] == 8080:
                    emb_model = self.config["embedding"].get("model_path", "")
                    inf_model = self.config["inference"].get("model_path", "")
                    if not emb_model or emb_model == inf_model:
                        logger.info("Migrating embedding server to share port 8080 with inference server for consolidation.")
                        self.config["embedding"]["port"] = 8080
                        updated = True

            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                logger.warning(f"Could not load models_config.json, using defaults: {e}")
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
                    if os.name == "nt" and not name.endswith(".exe") and not name.endswith(".dll"):
                        continue
                    if name.endswith(".dll"):
                        continue
                    binaries.append(name)
        return sorted(binaries)

    def get_status(self) -> Dict[str, Any]:
        inference_running = self.inference_proc is not None and self.inference_proc.poll() is None
        embedding_running = self.embedding_proc is not None and self.embedding_proc.poll() is None
        
        # Consolidation check: if ports are identical, embedding running status matches inference
        if self.config["embedding"]["port"] == self.config["inference"]["port"]:
            embedding_running = inference_running
            
        return {
            "inference": {
                "running": inference_running,
                "config": self.config["inference"]
            },
            "embedding": {
                "running": embedding_running,
                "config": self.config["embedding"]
            },
            "available_models": self.get_available_models(),
            "available_binaries": self.get_available_binaries()
        }

    def start_inference(self) -> bool:
        self.stop_inference()
        cfg = self.config["inference"]
        
        binary = Path(cfg["binary_path"])
        model_str = cfg["model_path"]
        model = Path(model_str)
        
        if not binary.exists():
            # Check if relative to workspace
            binary = Path("llama_bin") / binary.name
            if not binary.exists():
                logger.error(f"Inference binary not found: {cfg['binary_path']}")
                return False
            
        is_hf = False
        if model_str and not model.exists() and not model.is_absolute():
            if "/" in model_str and not model_str.startswith("models/"):
                is_hf = True

        if not is_hf and (not model.exists() or not model.is_file()):
            logger.error(f"Inference model not found or invalid: {cfg['model_path']}")
            return False
            
        args = [
            str(binary),
        ]
        if is_hf:
            args.extend(["-hf", model_str])
        else:
            args.extend(["-m", str(model)])

        threads = int(cfg["threads"])
        if threads <= 0:
            import os
            # Auto-detect physical cores (fallback to logical cores // 2)
            threads = max(1, (os.cpu_count() or 8) // 2)
            logger.info(f"Auto-detected optimal thread count: {threads}")

        args.extend([
            "--port", str(cfg["port"]),
            "-t", str(threads),
            "-c", str(cfg["context_size"])
        ])
        
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
                
        # Enforce --parallel 1 if not defined to save memory allocations for slot caches
        if "--parallel" not in extra_args and "-np" not in extra_args:
            extra_args.extend(["--parallel", "1"])
            
        if extra_args:
            args.extend(extra_args)
            
        logger.info(f"Starting Llama Inference Server: {' '.join(args)}")
        try:
            self.inference_proc = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except OSError:
            logger.exception("Failed to start Llama Inference Server subprocess")
            return False

    def start_embedding(self) -> bool:
        cfg = self.config["embedding"]
        inf_cfg = self.config["inference"]
        
        # Consolidation check: if ports match, we use inference server for both
        if cfg["port"] == inf_cfg["port"]:
            logger.info("Consolidated server mode: using inference server for embeddings.")
            inference_running = self.inference_proc is not None and self.inference_proc.poll() is None
            if not inference_running:
                return self.start_inference()
            return True
            
        self.stop_embedding()
        cfg = self.config["embedding"]
        
        binary = Path(cfg["binary_path"])
        model_str = cfg["model_path"]
        model = Path(model_str)
        
        if not binary.exists():
            binary = Path("llama_bin") / binary.name
            if not binary.exists():
                logger.error(f"Embedding binary not found: {cfg['binary_path']}")
                return False
            
        is_hf = False
        if model_str and not model.exists() and not model.is_absolute():
            if "/" in model_str and not model_str.startswith("models/"):
                is_hf = True

        if not is_hf and (not model.exists() or not model.is_file()):
            logger.error(f"Embedding model not found or invalid: {cfg['model_path']}")
            return False
            
        args = [
            str(binary),
        ]
        if is_hf:
            args.extend(["-hf", model_str])
        else:
            args.extend(["-m", str(model)])

        threads = int(cfg["threads"])
        if threads <= 0:
            import os
            threads = max(1, (os.cpu_count() or 8) // 2)
            logger.info(f"Auto-detected optimal embedding thread count: {threads}")

        args.extend([
            "--port", str(cfg["port"]),
            "-t", str(threads),
            "--embedding"
        ])
        
        gpu_layers = int(cfg["gpu_layers"])
        if gpu_layers >= 0:
            args.extend(["-ngl", str(gpu_layers)])
            
        extra = cfg.get("additional_args", "").strip()
        if extra:
            args.extend(extra.split())
            
        logger.info(f"Starting Llama Embedding Server: {' '.join(args)}")
        try:
            self.embedding_proc = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except OSError:
            logger.exception("Failed to start Llama Embedding Server subprocess")
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

    def stop_all(self):
        self.stop_inference()
        self.stop_embedding()

runner = LlamaServerRunner()
