import json
import pytest
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from src.backend.core.engine.runner import LlamaServerRunner, DEFAULT_CONFIG

def test_runner_load_config_defaults():
    """Verify runner loads defaults if file does not exist."""
    mock_config_file = MagicMock(spec=Path)
    mock_config_file.exists.return_value = False
    
    with patch("src.backend.core.engine.runner.CONFIG_FILE", mock_config_file):
        with patch("src.backend.core.engine.runner.LlamaServerRunner.get_available_models", return_value=[]):
            with patch("src.backend.core.engine.runner.LlamaServerRunner.save_config") as mock_save:
                runner = LlamaServerRunner()
                assert runner.config["inference"]["port"] == 8080
                assert runner.config["embedding"]["port"] == 8080


def test_runner_load_config_non_existent_models_path(tmp_path):
    """Verify runner creates models directory if it doesn't exist."""
    mock_config_file = MagicMock(spec=Path)
    mock_config_file.exists.return_value = False
    
    with patch("src.backend.core.engine.runner.CONFIG_FILE", mock_config_file):
        with patch("src.backend.core.engine.runner.Path.exists", return_value=False):
            with patch("src.backend.core.engine.runner.Path.mkdir") as mock_mkdir:
                with patch("src.backend.core.engine.runner.Path.glob", return_value=[]):
                    with patch("src.backend.core.engine.runner.LlamaServerRunner.save_config"):
                        runner = LlamaServerRunner()
                        models = runner.get_available_models()
                        assert mock_mkdir.call_count == 2
                        assert models == []


def test_runner_load_config_defaults_with_models():
    """Verify default model assignments for single or multiple models."""
    mock_config_file = MagicMock(spec=Path)
    mock_config_file.exists.return_value = False
    
    with patch("src.backend.core.engine.runner.CONFIG_FILE", mock_config_file):
        with patch("src.backend.core.engine.runner.LlamaServerRunner.save_config"):
            # Case 1: Only 1 model found
            with patch("src.backend.core.engine.runner.LlamaServerRunner.get_available_models", return_value=["m1.gguf"]):
                runner = LlamaServerRunner()
                assert runner.config["inference"]["model_path"] == "models/m1.gguf"
                assert runner.config["embedding"]["model_path"] == "models/m1.gguf"

            # Case 2: Multiple models found
            with patch("src.backend.core.engine.runner.LlamaServerRunner.get_available_models", return_value=["m1.gguf", "m2.gguf"]):
                runner = LlamaServerRunner()
                assert runner.config["inference"]["model_path"] == "models/m1.gguf"
                assert runner.config["embedding"]["model_path"] == "models/m2.gguf"


def test_runner_load_config_exceptions():
    """Verify JSON errors, permissions, or general exceptions reload defaults."""
    mock_config_file = MagicMock(spec=Path)
    mock_config_file.exists.return_value = True
    
    with patch("src.backend.core.engine.runner.CONFIG_FILE", mock_config_file):
        with patch("src.backend.core.engine.runner.LlamaServerRunner.save_config") as mock_save:
            # 1. JSONDecodeError
            with patch("builtins.open", side_effect=json.JSONDecodeError("msg", "doc", 0)):
                runner = LlamaServerRunner()
                assert runner.config == DEFAULT_CONFIG

            # 2. General Exception
            with patch("builtins.open", side_effect=Exception("General")):
                runner = LlamaServerRunner()
                assert runner.config == DEFAULT_CONFIG


def test_runner_load_config_migrations():
    """Verify migrations for additional_args and port consolidation."""
    mock_config_file = MagicMock(spec=Path)
    mock_config_file.exists.return_value = True
    
    # Custom config containing old values to trigger all migration code paths
    old_cfg = {
        "inference": {
            "binary_path": "llama-server.exe",
            "model_path": "models/model.gguf",
            "port": 8080,
            "additional_args": "--extra --cache-type-k q8_0 --cache-type-v q8_0" # triggers replacement
        },
        "embedding": {
            "binary_path": "llama-server.exe",
            "model_path": "models/model.gguf",
            "port": 8081, # triggers port migration to 8080 since models are identical
            "additional_args": "--some-arg" # triggers flash-attn injection
        }
    }
    
    with patch("src.backend.core.engine.runner.CONFIG_FILE", mock_config_file):
        with patch("builtins.open", mock_open(read_data=json.dumps(old_cfg))):
            with patch("src.backend.core.engine.runner.LlamaServerRunner.save_config") as mock_save:
                runner = LlamaServerRunner()
                
                # Check inference migrations
                inf_args = runner.config["inference"]["additional_args"]
                assert "q8_0" not in inf_args
                assert "q4_0" in inf_args
                assert "--flash-attn" in inf_args
                assert "--parallel 1" in inf_args
                
                # Check embedding migrations
                emb_args = runner.config["embedding"]["additional_args"]
                assert "--flash-attn" in emb_args
                assert runner.config["embedding"]["port"] == 8080
                
                mock_save.assert_called()



def test_runner_save_config_success():
    """Verify saving configuration writes to CONFIG_FILE."""
    with patch("src.backend.core.engine.runner.LlamaServerRunner.get_available_models", return_value=[]):
        runner = LlamaServerRunner()
        
        m = mock_open()
        with patch("builtins.open", m):
            runner.save_config()
            m.assert_called_once_with(Path("models_config.json"), "w")


def test_runner_save_config_io_error():
    """Verify IOError inside save_config is caught and logged."""
    runner = LlamaServerRunner()
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        runner.save_config() # Should catch IOError internally


def test_runner_get_available_binaries_variations():
    """Verify iterdir outputs are correctly filtered on Windows and non-Windows."""
    runner = LlamaServerRunner()
    
    # 1. Directory does not exist
    with patch("src.backend.core.engine.runner.Path.exists", return_value=False):
        assert runner.get_available_binaries() == []

    # 2. Files with NT matching rules
    mock_bin_dir = MagicMock(spec=Path)
    mock_bin_dir.exists.return_value = True
    
    f1 = MagicMock(spec=Path)
    f1.is_file.return_value = True
    f1.name = "llama-server.exe"

    f2 = MagicMock(spec=Path)
    f2.is_file.return_value = True
    f2.name = "llama-server.dll"

    f3 = MagicMock(spec=Path)
    f3.is_file.return_value = True
    f3.name = "llama-server" # NT OS drops it (no exe/dll extension)

    f4 = MagicMock(spec=Path)
    f4.is_file.return_value = True
    f4.name = "unrelated.txt"

    with patch("src.backend.core.engine.runner.Path.exists", return_value=True):
        with patch("src.backend.core.engine.runner.Path.iterdir", return_value=[f1, f2, f3, f4]):
            with patch("os.name", "nt"):
                res = runner.get_available_binaries()
                assert res == ["llama-server.exe"]

            with patch("os.name", "posix"):
                res = runner.get_available_binaries()
                assert "llama-server" in res
                assert "llama-server.exe" in res
                assert "llama-server.dll" not in res


def test_runner_get_status():
    """Verify runner reports correct running status based on active processes."""
    runner = LlamaServerRunner()
    
    runner.inference_proc = MagicMock()
    runner.inference_proc.poll.return_value = None  # running
    
    runner.config["embedding"]["port"] = 8081
    runner.embedding_proc = MagicMock()
    runner.embedding_proc.poll.return_value = 1  # stopped
    
    status = runner.get_status()
    assert status["inference"]["running"] is True
    assert status["embedding"]["running"] is False

    # Consolidation check: if ports match, embedding running status matches inference
    runner.config["embedding"]["port"] = 8080
    runner.config["inference"]["port"] = 8080
    status = runner.get_status()
    assert status["embedding"]["running"] is True


@patch("src.backend.core.engine.runner.subprocess.Popen")
def test_runner_start_inference_edge_cases(mock_popen):
    """Verify various binary paths, HF models, NGL, and auto thread detection."""
    # Simulate a running process (poll() returns None = still alive)
    mock_popen.return_value.poll.return_value = None
    runner = LlamaServerRunner()
    
    # Config setup
    runner.config = {
        "inference": {
            "binary_path": "nonexistent.exe",
            "model_path": "models/model.gguf",
            "port": 8080,
            "threads": 0,  # triggers auto-detect threads
            "gpu_layers": 16, # triggers -ngl
            "context_size": 2048,
            "additional_args": ""
        },
        "embedding": {
            "port": 8080  # triggers consolidated embedding port enablement
        }
    }
    
    # 1. Binary path relative check fallback
    def mock_exists_side_effect(self):
        p_str = str(self).replace("\\", "/")
        if "llama_bin/nonexistent.exe" in p_str:
            return True
        if "nonexistent.exe" in p_str:
            return False
        return True
        
    with patch("src.backend.core.engine.runner.Path.exists", mock_exists_side_effect):
        with patch("src.backend.core.engine.runner.Path.is_file", return_value=True):
            with patch("os.cpu_count", return_value=8):
                success = runner.start_inference()
                assert success is True
                args, _ = mock_popen.call_args
                cmd = args[0]
                assert "llama_bin" in cmd[0].replace("\\", "/")
                assert "-t" in cmd
                assert "4" in cmd # 8 // 2
                assert "-ngl" in cmd
                assert "16" in cmd
                assert "--embedding" in cmd # due to identical ports
                assert "--parallel" in cmd
                assert "1" in cmd

    # Reset
    mock_popen.reset_mock()

    # 2. Binary not found entirely
    with patch("src.backend.core.engine.runner.Path.exists", return_value=False):
        success = runner.start_inference()
        assert success is False
        
    # 3. Model path invalid check
    # Let's say binary exists, but model does not exist
    def model_not_found_exists(self):
        if "model.gguf" in str(self):
            return False
        return True
    with patch("src.backend.core.engine.runner.Path.exists", model_not_found_exists):
        success = runner.start_inference()
        assert success is False

    # 4. Hugging Face path format model_str (e.g. username/model-repo)
    runner.config["inference"]["model_path"] = "MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF"
    def binary_exists_only(self):
        p_str = str(self).replace("\\", "/")
        if "nonexistent.exe" in p_str:
            return True
        if "MaziyarPanahi" in p_str:
            return False
        return True
    with patch("src.backend.core.engine.runner.Path.exists", binary_exists_only):
        success = runner.start_inference()
        assert success is True
        args, _ = mock_popen.call_args
        cmd = args[0]
        assert "-hf" in cmd
        assert "MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF" in cmd

    # Reset
    mock_popen.reset_mock()

    # 5. Subprocess OSError execution path
    runner.config["inference"]["model_path"] = "models/model.gguf"
    mock_popen.side_effect = OSError("Exec format error")
    with patch("src.backend.core.engine.runner.Path.exists", return_value=True):
        with patch("src.backend.core.engine.runner.Path.is_file", return_value=True):
            success = runner.start_inference()
            assert success is False


@patch("src.backend.core.engine.runner.subprocess.Popen")
def test_runner_start_embedding_edge_cases(mock_popen):
    """Verify embedding server launches, handles consolidation, relative paths, HF, and errors."""
    # Simulate a running process (poll() returns None = still alive)
    mock_popen.return_value.poll.return_value = None
    runner = LlamaServerRunner()
    
    # 1. Consolidation check (ports match)
    runner.config = {
        "inference": {
            "binary_path": "llama_bin/llama-server.exe",
            "model_path": "models/m1.gguf",
            "port": 8080,
            "threads": 4,
            "gpu_layers": -1,
            "context_size": 2048,
            "additional_args": ""
        },
        "embedding": {
            "port": 8080 # matches
        }
    }
    
    # If inference server is already running, starting embedding should just return True
    runner.inference_proc = MagicMock()
    runner.inference_proc.poll.return_value = None
    assert runner.start_embedding() is True
    mock_popen.assert_not_called()

    # Reset
    runner.inference_proc = None
    
    # If inference server is not running, starting embedding should launch inference server
    with patch("src.backend.core.engine.runner.Path.exists", return_value=True):
        with patch("src.backend.core.engine.runner.Path.is_file", return_value=True):
            assert runner.start_embedding() is True
            mock_popen.assert_called_once()
            
    # Reset
    mock_popen.reset_mock()

    # 2. Embedding ports differ (individual server)
    runner.config = {
        "inference": {"port": 8080},
        "embedding": {
            "binary_path": "nonexistent.exe",
            "model_path": "models/emb.gguf",
            "port": 8081,
            "threads": 0,
            "gpu_layers": 8,
            "additional_args": "--extra"
        }
    }

    # Binary check fallback relative, threads auto-detect, ngl, extra args
    def mock_exists_side_effect(self):
        p_str = str(self).replace("\\", "/")
        if "llama_bin/nonexistent.exe" in p_str:
            return True
        if "nonexistent.exe" in p_str:
            return False
        return True
        
    with patch("src.backend.core.engine.runner.Path.exists", mock_exists_side_effect):
        with patch("src.backend.core.engine.runner.Path.is_file", return_value=True):
            with patch("os.cpu_count", return_value=8):
                success = runner.start_embedding()
                assert success is True
                args, _ = mock_popen.call_args
                cmd = args[0]
                assert "--port" in cmd
                assert "8081" in cmd
                assert "-t" in cmd
                assert "4" in cmd
                assert "-ngl" in cmd
                assert "8" in cmd
                assert "--extra" in cmd

    # Reset
    mock_popen.reset_mock()

    # 3. Binary not found
    with patch("src.backend.core.engine.runner.Path.exists", return_value=False):
        assert runner.start_embedding() is False

    # 4. Model not found
    def model_not_found(self):
        if "emb.gguf" in str(self):
            return False
        return True
    with patch("src.backend.core.engine.runner.Path.exists", model_not_found):
        assert runner.start_embedding() is False

    # 5. HF model path
    runner.config["embedding"]["model_path"] = "huggingface/repo"
    def binary_exists_only(self):
        p_str = str(self).replace("\\", "/")
        if "nonexistent.exe" in p_str:
            return True
        if "huggingface" in p_str:
            return False
        return True
    with patch("src.backend.core.engine.runner.Path.exists", binary_exists_only):
        assert runner.start_embedding() is True
        args, _ = mock_popen.call_args
        cmd = args[0]
        assert "-hf" in cmd
        assert "huggingface/repo" in cmd

    # Reset
    mock_popen.reset_mock()

    # 6. OSError
    runner.config["embedding"]["model_path"] = "models/emb.gguf"
    mock_popen.side_effect = OSError("Launch failed")
    with patch("src.backend.core.engine.runner.Path.exists", return_value=True):
        with patch("src.backend.core.engine.runner.Path.is_file", return_value=True):
            assert runner.start_embedding() is False


def test_runner_stop_and_wait_timeouts():
    """Verify TimeoutExpired triggers process kill block for both servers, and handles exceptions."""
    runner = LlamaServerRunner()
    
    # 1. Inference timeout with kill success
    mock_inf = MagicMock()
    mock_inf.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)
    runner.inference_proc = mock_inf
    
    runner.stop_inference()
    mock_inf.terminate.assert_called_once()
    mock_inf.kill.assert_called_once()
    assert runner.inference_proc is None

    # 2. Inference timeout with kill exception and general exception
    mock_inf_exc = MagicMock()
    mock_inf_exc.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)
    mock_inf_exc.kill.side_effect = Exception("Kill failed")
    runner.inference_proc = mock_inf_exc
    runner.stop_inference()
    assert runner.inference_proc is None

    # 3. Embedding timeout (when ports differ)
    runner.config["embedding"]["port"] = 8081
    runner.config["inference"]["port"] = 8080
    
    mock_emb = MagicMock()
    mock_emb.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)
    runner.embedding_proc = mock_emb
    
    runner.stop_embedding()
    mock_emb.terminate.assert_called_once()
    mock_emb.kill.assert_called_once()
    assert runner.embedding_proc is None

    # 4. Embedding timeout with kill exception and general wait exception
    mock_emb_exc = MagicMock()
    mock_emb_exc.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)
    mock_emb_exc.kill.side_effect = Exception("Kill failed")
    runner.embedding_proc = mock_emb_exc
    runner.stop_embedding()
    assert runner.embedding_proc is None

    # 5. Embedding stop consolidation check (should be a no-op if ports are identical)
    runner.config["embedding"]["port"] = 8080
    runner.embedding_proc = MagicMock()
    runner.stop_embedding()
    runner.embedding_proc.terminate.assert_not_called()

    # 6. Stop all method check
    with patch("src.backend.core.engine.runner.LlamaServerRunner.stop_inference") as mock_stop_inf:
        with patch("src.backend.core.engine.runner.LlamaServerRunner.stop_embedding") as mock_stop_emb:
            runner.stop_all()
            mock_stop_inf.assert_called_once()
            mock_stop_emb.assert_called_once()
