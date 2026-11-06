import os
import shutil
import subprocess
from pathlib import Path

def build():
    root = Path(__file__).resolve().parent.parent
    icon_path = root / "assets" / "app_logo.ico"
    ui_dir = root / "src" / "ui"
    assets_dir = root / "assets"
    venv_pyinstaller = root / ".venv" / "Scripts" / "pyinstaller.exe"
    pyinstaller_bin = str(venv_pyinstaller) if venv_pyinstaller.exists() else "pyinstaller"

    print("Building standalone portable package with PyInstaller...")

    cmd = [
        pyinstaller_bin,
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "MarkItDown Studio",
        "--icon", str(icon_path),
        "--add-data", f"{ui_dir};src/ui",
        "--add-data", f"{assets_dir};assets",
        "--collect-all", "webview",
        "--collect-all", "pythonnet",
        "--collect-all", "clr_loader",
        "--collect-all", "markitdown",
        "--collect-all", "magika",
        "--collect-all", "mammoth",
        "--collect-all", "openpyxl",
        "--collect-all", "pdfminer",
        "--collect-all", "pptx",
        "--collect-all", "docx",
        "--collect-all", "bs4",
        "--collect-all", "markdownify",
        str(root / "main.py")
    ]

    subprocess.run(cmd, cwd=str(root), check=True)

    dist_dir = root / "dist" / "MarkItDown Studio"
    zip_output = root / "dist" / "MarkItDown-Studio-v1.0.0-Windows-x64-Portable"
    print("Compressing portable release into ZIP...")
    shutil.make_archive(str(zip_output), "zip", root / "dist", "MarkItDown Studio")
    print(f"Standalone portable package created at: {zip_output}.zip")

if __name__ == "__main__":
    build()
