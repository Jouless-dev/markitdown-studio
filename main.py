import sys
import os
import traceback
import ctypes
from pathlib import Path

# Native crash handler to guarantee errors are never silent
def _handle_exception(exc_type, exc_value, exc_tb):
    err_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        base_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
        with open(base_dir / "crash.log", "w", encoding="utf-8") as f:
            f.write(err_text)
    except Exception:
        pass
    ctypes.windll.user32.MessageBoxW(0, f"Application Error:\n\n{err_text}", "MarkItDown Studio Error", 0x10)

sys.excepthook = _handle_exception

# Automatically unblock Zone.Identifier from bundled DLLs on Windows
def _auto_unblock_self():
    if sys.platform != "win32":
        return
    try:
        base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
        kernel32 = ctypes.windll.kernel32
        for dll in base.rglob("*.dll"):
            try:
                kernel32.DeleteFileW(f"{dll}:Zone.Identifier")
            except Exception:
                pass
    except Exception:
        pass

_auto_unblock_self()

# Add paths to module search path
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
for p in (str(root_dir), str(src_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.app import main
except ImportError:
    from app import main

if __name__ == "__main__":
    main()
