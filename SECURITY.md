# Security Policy

## Supported Versions

Security updates are applied to the active release line.

| Version | Supported |
| :--- | :--- |
| 1.0.x | Yes |
| < 1.0 | No |

---

## Security Architecture

MarkItDown Studio is designed with an explicit local-first security model:

1. **Network Isolation**: The application contains no telemetry endpoints, analytics scripts, or remote server integrations. No document content, filenames, or metadata are ever transmitted off the host machine.
2. **Buffer Limits**: To prevent denial-of-service or memory exhaustion attacks from oversized payload drops, in-memory buffers in the JavaScript-to-Python bridge are constrained to 150 MB. Files exceeding this limit must be selected directly from disk via native dialogs.
3. **Path Traversal Protection**: Conversion targets and temporary file handlers sanitize file paths using `Path.name` and canonical `.resolve()` checks to prevent arbitrary path traversal or writes outside user-designated folders.
4. **Offline Sandboxing**: The embedded webview disables external navigation and runs strictly against local asset files bundled in the distribution.

---

## Reporting a Vulnerability

If you discover a security issue or vulnerability in MarkItDown Studio:

1. Do not open a public GitHub issue or pull request.
2. Submit a detailed report to the repository maintainers via private vulnerability reporting on GitHub (Security Advisories) or email the project maintainer directly.
3. Include:
   - Steps to reproduce or proof-of-concept payload.
   - Host environment details (Windows version, Python version).
   - Assessment of potential impact.

Maintainers will review the report within 48 hours and coordinate remediation before public disclosure.
