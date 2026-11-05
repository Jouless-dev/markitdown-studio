import os
import sys
import argparse
import subprocess
from pathlib import Path
from PIL import Image

def generate_icons(source_path: Path):
    """Generates multi-resolution Windows ICO and PNG assets from a source image."""
    root = Path(__file__).resolve().parent.parent
    assets_dir = root / "assets"
    ui_dir = root / "src" / "ui"

    assets_dir.mkdir(parents=True, exist_ok=True)
    ui_dir.mkdir(parents=True, exist_ok=True)

    if not source_path.exists():
        print(f"Error: Source image not found at {source_path}")
        sys.exit(1)

    print(f"Processing source image: {source_path}")
    with Image.open(source_path) as img:
        img = img.convert("RGBA")

        # 1. Main PNG asset
        png_path = assets_dir / "app.png"
        img.save(png_path, format="PNG")
        print(f"Saved: {png_path}")

        # 2. UI Favicon
        favicon_path = ui_dir / "favicon.png"
        img.resize((64, 64), Image.Resampling.LANCZOS).save(favicon_path, format="PNG")
        print(f"Saved: {favicon_path}")

        # 3. Multi-resolution Windows ICO
        ico_sizes = [(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (96, 96), (128, 128), (256, 256)]
        for name in ("app.ico", "app_logo.ico"):
            target_ico = assets_dir / name
            img.save(target_ico, format="ICO", sizes=ico_sizes)
            print(f"Saved: {target_ico}")

    # 4. Optional C# launcher compilation if .NET Framework csc is available
    csc = Path(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe")
    if csc.exists():
        launcher_src = root / "launcher_temp.cs"
        launcher_src.write_text("""using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

class Program
{
    [STAThread]
    static void Main()
    {
        string dir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\\\');
        string pythonw = Path.Combine(dir, @".venv\\Scripts\\pythonw.exe");
        string mainPy = Path.Combine(dir, "main.py");

        if (!File.Exists(pythonw)) {
            DialogResult res = MessageBox.Show(
                "MarkItDown Studio (Source Code Edition)\\n\\n" +
                "The virtual environment (.venv) was not found in this folder.\\n\\n" +
                "• If you want to use the application without installing Python, please download the standalone portable version from GitHub Releases:\\n" +
                "  https://github.com/Jouless-dev/markitdown-studio/releases\\n\\n" +
                "• Would you like to open the GitHub Releases page now?",
                "MarkItDown Studio",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Information
            );
            if (res == DialogResult.Yes) {
                Process.Start("https://github.com/Jouless-dev/markitdown-studio/releases");
            }
            return;
        }

        try {
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = pythonw;
            psi.Arguments = "\\"" + mainPy + "\\"";
            psi.WorkingDirectory = dir;
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            Process.Start(psi);
        } catch (Exception ex) {
            MessageBox.Show("Error starting MarkItDown Studio:\\n\\n" + ex.Message, "MarkItDown Studio", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
""", encoding="utf-8")

        output_exe = root / "MarkItDown.exe"
        cmd = [
            str(csc),
            "/target:winexe",
            "/reference:System.Windows.Forms.dll",
            f"/win32icon:{assets_dir / 'app_logo.ico'}",
            f"/out:{output_exe}",
            str(launcher_src)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if launcher_src.exists():
            launcher_src.unlink()
        if res.returncode == 0:
            print(f"Recompiled native Windows launcher: {output_exe}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate icon assets for MarkItDown Studio.")
    parser.add_argument("source", nargs="?", default="assets/app.png", help="Path to source image.")
    args = parser.parse_args()
    generate_icons(Path(args.source))
