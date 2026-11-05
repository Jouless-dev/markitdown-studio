import sys
import json
import winreg
from pathlib import Path

if getattr(sys, "frozen", False):
    CONFIG_FILE = Path(sys.executable).parent / "config.json"
else:
    CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.json"

def get_default_downloads_dir() -> str:
    """Detects the official Windows Downloads folder or falls back to ~/Downloads."""
    try:
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            return winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
    except Exception:
        return str(Path.home() / "Downloads")

DEFAULT_CONFIG = {
    "default_output_dir": get_default_downloads_dir(),
    "ask_destination": False,
    "overwrite_existing": False
}

def load_config() -> dict:
    """Loads configuration from disk, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception:
            pass
            
    # Fallback if saved dir was deleted or invalid
    if not config.get("default_output_dir") or not Path(config["default_output_dir"]).exists():
        config["default_output_dir"] = get_default_downloads_dir()

    return config

def save_config(updates: dict) -> dict:
    """Persists user configuration updates safely."""
    current = load_config()
    current.update(updates)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Config save error: {e}")
    return current
