import os
import sys
import time
import base64
import ctypes
import threading
import tempfile
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Optional, List, Dict, Any

import pyperclip
import webview

try:
    from .config import load_config, save_config, get_default_downloads_dir
    from .converter import MarkdownConverter
except ImportError:
    from config import load_config, save_config, get_default_downloads_dir
    from converter import MarkdownConverter

# Register unique AppID so Windows groups taskbar icon properly
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("markitdown.studio.app.v1")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent
UI_DIR = ROOT_DIR / "src" / "ui"

class AppAPI:
    """Secure Python API bridge exposed to JavaScript via PyWebView."""

    def __init__(self):
        self._converter = MarkdownConverter()

    def get_config(self) -> Dict[str, Any]:
        """Returns active user configuration."""
        return load_config()

    def update_config(self, key: str, value: Any) -> Dict[str, Any]:
        """Updates and persists a configuration entry."""
        return save_config({key: value})

    def select_files(self) -> List[str]:
        """Opens native Windows dialog to select one or more files to convert."""
        # Try PyWebView native window dialog first
        try:
            w = webview.active_window()
            if w:
                file_types = (
                    'Compatible Documents (*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.html;*.htm;*.csv;*.json;*.xml;*.txt;*.zip;*.ipynb)',
                    'PDF Files (*.pdf)',
                    'Word Documents (*.docx;*.doc)',
                    'Excel Sheets (*.xlsx;*.xls;*.csv)',
                    'PowerPoint Presentations (*.pptx;*.ppt)',
                    'All Files (*.*)'
                )
                res = w.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True, file_types=file_types)
                if res:
                    return list(res)
                return []
        except Exception:
            pass

        # Fallback to Tkinter native dialog
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            files = filedialog.askopenfilenames(
                title="Select files to convert to Markdown",
                filetypes=[
                    ("Compatible Documents", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.html;*.htm;*.csv;*.json;*.xml;*.txt;*.zip;*.ipynb"),
                    ("All Files", "*.*")
                ]
            )
            root.destroy()
            return list(files) if files else []
        except Exception:
            return []

    def select_directory(self) -> Optional[str]:
        """Opens native Windows directory chooser dialog."""
        initial_dir = load_config().get("default_output_dir") or get_default_downloads_dir()

        try:
            w = webview.active_window()
            if w:
                res = w.create_file_dialog(webview.FOLDER_DIALOG, directory=initial_dir)
                if res and len(res) > 0:
                    return res[0]
                return None
        except Exception:
            pass

        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            folder = filedialog.askdirectory(title="Select Destination Directory", initialdir=initial_dir)
            root.destroy()
            return folder if folder else None
        except Exception:
            return None

    def convert_file_path(self, file_path_str: str, destination_dir_str: Optional[str] = None) -> Dict[str, Any]:
        """Converts local file from path."""
        if not destination_dir_str:
            destination_dir_str = load_config().get("default_output_dir") or get_default_downloads_dir()

        return self._converter.convert_file(
            file_path_str=file_path_str,
            destination_dir_str=destination_dir_str
        )

    def convert_base64_file(self, filename: str, base64_data: str, destination_dir_str: Optional[str] = None) -> Dict[str, Any]:
        """Converts drag-and-dropped file buffer safely with size bounds checking."""
        if not destination_dir_str:
            destination_dir_str = load_config().get("default_output_dir") or get_default_downloads_dir()

        # Sanitize filename
        safe_name = Path(filename).name
        if not safe_name:
            safe_name = "document"

        # Security limit: 150 MB max for in-memory base64 conversion
        if len(base64_data) > 200 * 1024 * 1024:
            return {
                "success": False,
                "file_name": safe_name,
                "error": "File size exceeds memory threshold (150MB). Please click to select from disk."
            }

        temp_dir = Path(tempfile.gettempdir()) / "markitdown_temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file_path = temp_dir / safe_name

        try:
            file_bytes = base64.b64decode(base64_data)
            with open(temp_file_path, "wb") as f:
                f.write(file_bytes)

            result = self._converter.convert_file(
                file_path_str=str(temp_file_path),
                destination_dir_str=destination_dir_str
            )

            try:
                temp_file_path.unlink(missing_ok=True)
            except Exception:
                pass

            return result
        except Exception as e:
            return {
                "success": False,
                "file_name": safe_name,
                "error": f"Error decoding file buffer: {e}"
            }

    def open_folder(self, folder_path: str) -> bool:
        """Opens directory in Windows Explorer safely."""
        try:
            target = Path(folder_path).resolve()
            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)
            os.startfile(str(target))
            return True
        except Exception:
            return False

    def copy_text(self, text: str) -> bool:
        """Copies full text to Windows clipboard."""
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def read_full_content(self, file_path_str: str) -> str:
        """Reads and returns entire Markdown file from disk."""
        try:
            p = Path(file_path_str).resolve()
            if p.exists():
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()
            return ""
        except Exception as e:
            return f"Error reading file: {e}"

    def copy_file_content(self, file_path_str: str) -> bool:
        """Reads full Markdown file and copies entire text to Windows clipboard."""
        try:
            content = self.read_full_content(file_path_str)
            if content:
                pyperclip.copy(content)
                return True
            return False
        except Exception:
            return False


def _apply_windows_icon(title: str = "MarkItDown Studio"):
    """Binds application icon to titlebar, Alt+Tab and taskbar via Win32 API."""
    ico_path = (ROOT_DIR / "assets" / "app_logo.ico").resolve()
    if not ico_path.exists():
        ico_path = (ROOT_DIR / "assets" / "app.ico").resolve()
    if not ico_path.exists():
        return

    WM_SETICON = 0x0080
    ICON_SMALL = 0
    ICON_BIG = 1
    IMAGE_ICON = 1
    LR_LOADFROMFILE = 0x00000010

    for _ in range(25):
        time.sleep(0.1)
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        if hwnd:
            try:
                h_big = ctypes.windll.user32.LoadImageW(None, str(ico_path), IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
                h_small = ctypes.windll.user32.LoadImageW(None, str(ico_path), IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
                if h_big:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_big)
                if h_small:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small)
            except Exception:
                pass
            break


def main():
    api = AppAPI()
    index_file = UI_DIR / "index.html"

    if not index_file.exists():
        print(f"Error: UI not found at {index_file}")
        sys.exit(1)

    window_title = "MarkItDown Studio"
    window = webview.create_window(
        title=window_title,
        url=str(index_file),
        js_api=api,
        width=920,
        height=740,
        min_size=(780, 560),
        background_color="#08090b",
        text_select=True
    )

    threading.Thread(target=_apply_windows_icon, args=(window_title,), daemon=True).start()
    webview.start(debug=False)

if __name__ == "__main__":
    main()
