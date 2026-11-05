# Contributing to MarkItDown Studio

Thank you for your interest in contributing to MarkItDown Studio. This document outlines the engineering guidelines, architecture principles, and contribution workflow for this repository.

---

## Architectural Principles

MarkItDown Studio is designed with three core constraints:

1. **Zero External Network Dependencies**: The application must never make outbound requests, load external CDN assets, or phone home. All dependencies must be vendored or bundled locally.
2. **Minimalist, Dependency-Light UI**: The user interface is implemented in standard HTML5, CSS3, and ES6 JavaScript. Do not introduce heavy frontend frameworks (e.g., React, Vue, Angular) or external stylesheet libraries.
3. **Robust Isolation**: The PyWebView JavaScript API bridge (`src/app.py`) must remain decoupled from native UI thread objects to prevent COM recursion issues on Windows.

---

## Development Workflow

### 1. Environment Setup

Ensure you have Python 3.12+ (64-bit) installed on Windows 10 or 11.

```powershell
# Clone your fork
git clone https://github.com/Jouless-dev/markitdown-studio.git
cd markitdown-studio

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Branching Strategy

Create a descriptive feature branch from `main`:

```powershell
git checkout -b feature/format-support-extension
# or
git checkout -b fix/dialog-cancel-behavior
```

### 3. Coding Standards

- **Python**: Adhere to PEP 8. Maintain explicit typing annotations (`typing.Dict`, `typing.Optional`, `Path`) across public methods.
- **Comments**: Keep comments short, factual, and strictly necessary. Avoid redundant commentary for self-describing code.
- **User Interface**: All UI text must remain in English. Ensure elements retain proper keyboard navigation and screen contrast.
- **Safety**: Always validate and sanitize file paths using `pathlib.Path.resolve()` and bounds-check memory allocations.

### 4. Verification Checklist

Before opening a pull request, verify:

1. The application launches cleanly via `python main.py` without terminal warnings.
2. Conversion tests pass for representative formats (PDF, DOCX, XLSX).
3. The standalone build completes successfully:
   ```powershell
   python scripts/build_portable.py
   ```
4. No temporary files (`__pycache__`, `.spec`, test outputs) are tracked in git.

### 5. Pull Request Submission

- Provide a concise description of the motivation and changes.
- Reference any related issues or discussions.
- Ensure all commits follow conventional commit messages (e.g., `feat: ...`, `fix: ...`, `refactor: ...`).

---

## Security Inquiries

Do not report security vulnerabilities via public pull requests or issues. Refer to [SECURITY.md](SECURITY.md) for disclosure instructions.
