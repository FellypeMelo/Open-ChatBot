#!/usr/bin/env python3
"""Auto-downloader and setup tool for llama.cpp binaries and models.
Supports CPU, NVIDIA CUDA, AMD ROCm/HIP, Intel SYCL, and Vulkan.

Usage: python scripts/setup_llama.py
Run from the project root directory.
"""

import os
import sys
import shutil
import zipfile
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import json

# Configuration
LLAMA_VERSION = "b4800"  # Stable pinned release tag
DEFAULT_MODEL_URL = "https://huggingface.co/DavidAU/Qwen3-4B-Hivemind-Instruct-Heretic-Abliterated-Uncensored-GGUF/resolve/main/Qwen3-4B-Hivemind-Inst-Hrtic-Ablit-Uncensored-Q4_K_M-imat.gguf"
DEFAULT_MODEL_NAME = "Qwen3-4B-Hivemind-Inst-Hrtic-Ablit-Uncensored-Q4_K_M-imat.gguf"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = PROJECT_ROOT / "llama_bin"
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_FILE = PROJECT_ROOT / "models_config.json"
TEMP_ZIP = PROJECT_ROOT / "llama_temp.zip"
TEMP_MODEL = MODELS_DIR / "model_temp.gguf"

# Pre-compiled Windows Binary URLs from official llama.cpp releases
PLATFORMS_WIN = {
    "cuda": f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-win-cuda-cu12.2.0-x64.zip",
    "vulkan": f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-win-vulkan-x64.zip",
    "sycl": f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-win-sycl-x64.zip",
    "hip": f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-win-hip-amd-x64.zip",
    "avx2": f"https://github.com/ggerganov/llama.cpp/releases/download/{LLAMA_VERSION}/llama-{LLAMA_VERSION}-bin-win-avx2-x64.zip",
}


def detect_hardware() -> str:
    print("Detecting system hardware...")
    
    # 1. Check NVIDIA / CUDA
    try:
        res = subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            print("  [+] NVIDIA GPU detected via nvidia-smi. CUDA option is recommended.")
            return "cuda"
    except FileNotFoundError:
        pass

    # 2. Check wmic for GPU brands (Intel / AMD)
    if sys.platform == "win32":
        try:
            res = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], capture_output=True, text=True)
            gpu_info = res.stdout.lower()
            if "intel" in gpu_info and ("arc" in gpu_info or "xe" in gpu_info):
                print("  [+] Intel Arc/Xe GPU detected. SYCL option is recommended.")
                return "sycl"
            if "amd" in gpu_info or "radeon" in gpu_info:
                print("  [+] AMD GPU detected. HIP/ROCm or Vulkan option is recommended.")
                return "hip"
        except Exception:
            pass
            
    print("  [-] No specialized GPU accelerator auto-detected (or driver CLI tools not in PATH).")
    print("  [!] Vulkan (Cross-vendor GPU) or AVX2 (CPU fallback) are the safest defaults.")
    return "vulkan"


def download_file(url: str, dest_path: Path) -> None:
    print(f"Downloading {url} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            block_size = 1024 * 1024  # 1 MB
            downloaded = 0
            
            with open(dest_path, "wb") as f:
                while True:
                    block = response.read(block_size)
                    if not block:
                        break
                    f.write(block)
                    downloaded += len(block)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="", flush=True)
                    else:
                        mb_downloaded = downloaded / (1024 * 1024)
                        print(f"\r  Progress: {mb_downloaded:.1f} MB downloaded", end="", flush=True)
            print("\n  [+] Download complete.")
    except Exception as e:
        print(f"\n  [-] Error downloading file: {e}")
        if dest_path.exists():
            dest_path.unlink()
        raise


def extract_and_clean_zip(zip_path: Path, dest_dir: Path) -> None:
    print(f"Extracting binaries to {dest_dir}...")
    temp_dir = dest_dir / "temp_extract"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # Locate the directory containing the server executable
        server_exe = None
        for p in temp_dir.rglob("llama-server.exe"):
            server_exe = p
            break
        for p in temp_dir.rglob("llama-server"):
            if not server_exe:
                server_exe = p
                break
                
        # Clean existing destination folder contents
        if dest_dir.exists():
            for item in dest_dir.iterdir():
                if item.name == "temp_extract":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                    
        # Move extracted files to target directory
        source_dir = server_exe.parent if server_exe else temp_dir
        for item in source_dir.iterdir():
            dest = dest_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
                
        print("  [+] Binaries extracted and placed in llama_bin/.")
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def update_config(model_name: str) -> None:
    config_data = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
        except Exception:
            pass
            
    # Load defaults if config is empty or corrupted
    if "inference" not in config_data:
        config_data["inference"] = {
            "binary_path": "llama_bin/llama-server.exe",
            "model_path": "",
            "port": 8080,
            "threads": 0,
            "gpu_layers": 99,
            "context_size": 4096,
            "additional_args": "--cache-type-k q4_0 --cache-type-v q4_0 --parallel 1 --pooling mean --cache-ram 2048 --kv-unified --flash-attn auto"
        }
    if "embedding" not in config_data:
        config_data["embedding"] = {
            "binary_path": "llama_bin/llama-server.exe",
            "model_path": "",
            "port": 8080,
            "threads": 0,
            "gpu_layers": 99,
            "additional_args": "--pooling mean --cache-ram 2048 --kv-unified --flash-attn auto"
        }
        
    config_data["inference"]["model_path"] = f"models/{model_name}"
    config_data["embedding"]["model_path"] = f"models/{model_name}"
    
    ext = ".exe" if sys.platform == "win32" else ""
    config_data["inference"]["binary_path"] = f"llama_bin/llama-server{ext}"
    config_data["embedding"]["binary_path"] = f"llama_bin/llama-server{ext}"
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"  [+] Updated models_config.json to point to models/{model_name}.")


def main() -> None:
    print("=" * 60)
    print(f"Open-ChatBot Llama Engine Setup (Release {LLAMA_VERSION})")
    print("=" * 60)

    if sys.platform != "win32":
        print("[-] This auto-setup currently targets Windows x64 pre-compiled builds.")
        print("[!] For Linux/macOS, please compile llama.cpp manually and place files in llama_bin/.")
        sys.exit(1)

    recommended = detect_hardware()
    print("\nAvailable precompiled platforms:")
    print("  1) NVIDIA CUDA 12  (Recommended for NVIDIA GPUs)")
    print("  2) Vulkan          (Recommended for modern GPUs of any brand - no SDK needed)")
    print("  3) Intel oneAPI    (Recommended for Intel Arc/Xe GPUs)")
    print("  4) AMD HIP / ROCm  (Recommended for AMD Radeon GPUs)")
    print("  5) CPU AVX2        (Fallback, works on all modern CPUs - slow)")
    
    choice_map = {
        "1": "cuda",
        "2": "vulkan",
        "3": "sycl",
        "4": "hip",
        "5": "avx2"
    }
    
    rec_num = "2"
    for k, v in choice_map.items():
        if v == recommended:
            rec_num = k
            break
            
    try:
        user_choice = input(f"\nSelect target platform [1-5] (default {rec_num} - {recommended}): ").strip()
        if not user_choice:
            user_choice = rec_num
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)

    platform_key = choice_map.get(user_choice, recommended)
    download_url = PLATFORMS_WIN.get(platform_key)
    
    if not download_url:
        print(f"[-] Invalid choice. Defaulting to Vulkan.")
        platform_key = "vulkan"
        download_url = PLATFORMS_WIN["vulkan"]

    print(f"\n[+] Selected target: {platform_key.upper()}")
    
    # 1. Setup llama_bin
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    try:
        download_file(download_url, TEMP_ZIP)
        extract_and_clean_zip(TEMP_ZIP, BIN_DIR)
    except Exception as e:
        print(f"[-] Failed to set up binaries: {e}")
        sys.exit(1)
    finally:
        if TEMP_ZIP.exists():
            TEMP_ZIP.unlink()

    # 2. Setup models
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    gguf_files = list(MODELS_DIR.glob("*.gguf"))
    
    model_name = DEFAULT_MODEL_NAME
    if gguf_files:
        model_name = gguf_files[0].name
        print(f"\n[+] GGUF Model found in models/: {model_name}. Skipping default model download.")
    else:
        print(f"\n[?] No GGUF model found in models/.")
        try:
            download_opt = input(f"Do you want to download the default 4B Abliterated model ({DEFAULT_MODEL_NAME})? [Y/n]: ").strip().lower()
            if not download_opt or download_opt == 'y':
                try:
                    download_file(DEFAULT_MODEL_URL, TEMP_MODEL)
                    final_path = MODELS_DIR / DEFAULT_MODEL_NAME
                    if final_path.exists():
                        final_path.unlink()
                    TEMP_MODEL.rename(final_path)
                    print(f"  [+] Saved model to models/{DEFAULT_MODEL_NAME}")
                    model_name = DEFAULT_MODEL_NAME
                except Exception as e:
                    print(f"  [-] Model download failed: {e}")
                    if TEMP_MODEL.exists():
                        TEMP_MODEL.unlink()
            else:
                print("  [*] Skipping model download. Please place a GGUF model file in the models/ directory manually.")
        except KeyboardInterrupt:
            print("\nModel download skipped.")

    # 3. Update configuration file
    update_config(model_name)
    
    print("\n" + "=" * 60)
    print("[+] Llama Engine Setup Completed Successfully!")
    print(f"  Platform target: {platform_key.upper()}")
    print(f"  Binaries folder: {BIN_DIR.relative_to(PROJECT_ROOT)}")
    print(f"  Active model   : models/{model_name}")
    print("=" * 60)
    print("You can now launch the application using .\\run.bat")


if __name__ == "__main__":
    main()
