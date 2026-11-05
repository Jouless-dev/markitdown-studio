# MarkItDown Studio

Desktop application for Microsoft Windows that converts documents, spreadsheets, presentations, and structured data into clean CommonMark Markdown using the Microsoft MarkItDown engine.

Designed with an offline-first architecture, zero external network dependencies, and a centered retro-cyber aesthetic.

---

## Overview

MarkItDown Studio provides a desktop interface for converting arbitrary document formats into structured Markdown. All processing occurs locally on the host machine without telemetry, tracking, or cloud reliance.

### Key Capabilities

- **Zero-Dependency Portable Release**: Precompiled standalone 64-bit Windows distribution executable without requiring a Python environment.
- **Offline Processing**: All document parsing is handled in-process via local libraries.
- **Automated Directory Discovery**: Automatically resolves the Windows Shell Downloads directory for outputs, with optional folder override and confirmation modes.
- **Full-Text In-App Viewer**: Renders full Markdown conversions with real-time character and line metrics, clipboard copy shortcuts, and file explorer integration.
- **Input Sanitization**: Path normalization and memory threshold enforcement to guard against malformed files and memory exhaustion.

---

## Supported Formats

| Category | File Extensions | Parser / Engine |
| :--- | :--- | :--- |
| **Documents** | `.pdf`, `.docx`, `.doc` | pdfminer.six, Mammoth, MarkItDown |
| **Spreadsheets** | `.xlsx`, `.xls`, `.csv` | OpenPyXL, Pandas / Standard CSV |
| **Presentations** | `.pptx`, `.ppt` | python-pptx |
| **Web & Data** | `.html`, `.json`, `.xml`, `.txt` | BeautifulSoup4, Standard Parsers |
| **Archives & Notebooks** | `.zip`, `.ipynb` | Zipfile, Nbformat |

---

## Installation & Distribution

### 1. Standalone Portable Package (Recommended)

1. Download `MarkItDown-Studio-v1.0.0-Windows-x64-Portable.zip` from the project Releases page.
2. Extract the archive to any local directory.
3. Execute `MarkItDown Studio.exe` to launch. No runtime dependencies or administrator privileges are required.

### 2. Running from Source

#### Prerequisites

- Windows 10 or Windows 11 (64-bit)
- Python 3.12 or later
- Microsoft Edge WebView2 Runtime (installed by default on Windows 10/11)

#### Setup

```powershell
# Clone the repository
git clone https://github.com/Jouless-dev/markitdown-studio.git
cd markitdown-studio

# Initialize virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

Alternatively, Windows users can run the precompiled native launcher `MarkItDown.exe` located at the root of the project.

---

## Project Structure

```text
MarkItDown/
├── assets/                     # High-resolution icons and application graphics
│   ├── app.ico
│   ├── app.png
│   └── app_logo.ico
├── dist/                       # Packaged distributions and release archives
├── outputs/                    # Default local scratch folder for conversions
├── scripts/                    # Automation and build tooling
│   ├── build_portable.py       # PyInstaller standalone packager
│   ├── create_shortcut.ps1     # Windows Desktop shortcut generator
│   └── generate_icons.py       # Multi-resolution icon compiler
├── src/                        # Core application source code
│   ├── ui/                     # Presentation layer (HTML5, CSS3, ES6)
│   │   ├── app.js              # UI controller and PyWebView bridge calls
│   │   ├── favicon.png         # Browser runtime icon
│   │   ├── index.html          # Centered workspace layout
│   │   ├── markitdown-wordmark.svg # Scalable pixel-art wordmark
│   │   └── style.css           # Design tokens, pixel borders, and layout
│   ├── app.py                  # PyWebView application bridge & Win32 hooks
│   ├── config.py               # User configuration & registry discovery
│   └── converter.py            # Microsoft MarkItDown engine wrapper
├── .gitignore                  # Git repository exclusion definitions
├── CONTRIBUTING.md             # Developer contribution guidelines
├── LICENSE                     # MIT License terms
├── main.py                     # Python runtime entry point
├── MarkItDown.exe              # Native compiled Windows launcher
├── README.md                   # Project documentation
├── requirements.txt            # Locked Python dependency manifest
└── SECURITY.md                 # Security architecture & vulnerability reporting
```

---

## Build Automation

To compile a standalone binary distribution using PyInstaller:

```powershell
python scripts/build_portable.py
```

The script compiles the application into `dist/MarkItDown Studio/` and produces a compressed release archive in `dist/MarkItDown-Studio-v1.0.0-Windows-x64-Portable.zip`.

---

## Security Model

- **Local Boundary**: The application executes zero outbound HTTP or WebSocket connections. All conversion logic is local.
- **Resource Constraints**: In-memory buffers for drag-and-drop operations are capped at 150 MB to prevent process memory exhaustion.
- **Path Traversal Mitigation**: File basenames are sanitized prior to disk writes, preventing directory escape attacks.
- See [SECURITY.md](SECURITY.md) for full policy details.

---

## Contributing

Review [CONTRIBUTING.md](CONTRIBUTING.md) for workflow details, code standards, and pull request procedures.

---

## License

This project is licensed under the [MIT License](LICENSE).

Document conversion engine powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).
