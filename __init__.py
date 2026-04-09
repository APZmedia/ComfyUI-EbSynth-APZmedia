import subprocess
import sys
from pathlib import Path

_here = Path(__file__).parent
_ezsynth = _here / "Ezsynth"
_REPO_URL = "https://github.com/FuouM/Ezsynth"

if not (_ezsynth / "ezsynth").exists():
    print("[comfyui-ebsynth] Ezsynth missing — attempting git submodule update --init --recursive")
    result = subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive"],
        cwd=str(_here),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not (_ezsynth / "ezsynth").exists():
        print("[comfyui-ebsynth] Submodule update failed or incomplete — falling back to git clone")
        if _ezsynth.exists():
            import shutil
            shutil.rmtree(_ezsynth)
        result = subprocess.run(
            ["git", "clone", _REPO_URL, str(_ezsynth)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[comfyui-ebsynth] ERROR: git clone failed:\n{result.stderr}")
            sys.exit(1)
    print("[comfyui-ebsynth] Ezsynth ready.")

# Ensure Ezsynth is importable as a Python package
_ezsynth_init = _ezsynth / "__init__.py"
if not _ezsynth_init.exists():
    _ezsynth_init.touch()

# ── Optional CuPy for GPU Poisson blending ───────────────────────────────────
def _check_cupy() -> bool:
    try:
        import cupy  # noqa: F401
        print(f"[comfyui-ebsynth] CuPy {cupy.__version__} detected — GPU Poisson blending available.")
        return True
    except ImportError:
        return False

def ensure_cupy() -> bool:
    """Install CuPy if missing. Called lazily when use_poisson_cupy=True is first used."""
    if _check_cupy():
        return True
    try:
        import torch
        major = int(torch.version.cuda.split(".")[0])
        pkg = f"cupy-cuda{major}x"
    except Exception:
        pkg = "cupy-cuda12x"
    print(f"[comfyui-ebsynth] CuPy not found. Installing {pkg} for GPU Poisson blending...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", pkg],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"[comfyui-ebsynth] {pkg} installed successfully.")
        return True
    print(f"[comfyui-ebsynth] Could not install {pkg}:\n{result.stderr.strip()}")
    print(f"[comfyui-ebsynth] To install manually:  pip install {pkg}")
    return False

CUPY_AVAILABLE = _check_cupy()
# ─────────────────────────────────────────────────────────────────────────────

from .run import (
    ES_Guides7,
    ES_Translate,
    ES_VideoTransfer,
    ES_VideoTransferExtra,
)

NODE_CLASS_MAPPINGS = {
    "ES_Guides7": ES_Guides7,
    "ES_Translate": ES_Translate,
    "ES_VideoTransfer": ES_VideoTransfer,
    "ES_VideoTransferExtra": ES_VideoTransferExtra,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ES_Guides7": "ES Guides 7",
    "ES_Translate": "ES Translate",
    "ES_VideoTransfer": "ES Video Transfer",
    "ES_VideoTransferExtra": "ES Video Transfer Extra",
}


__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
