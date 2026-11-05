import os
from pathlib import Path
from typing import Dict, Any
from markitdown import MarkItDown

class MarkdownConverter:
    """Core document-to-markdown conversion engine powered by Microsoft MarkItDown."""

    def __init__(self):
        self.md = MarkItDown()

    def _get_unique_path(self, target_dir: Path, base_stem: str, ext: str = ".md") -> Path:
        """Finds a collision-free filename by appending incremental counters."""
        candidate = target_dir / f"{base_stem}{ext}"
        counter = 1
        while candidate.exists():
            candidate = target_dir / f"{base_stem} ({counter}){ext}"
            counter += 1
        return candidate

    def convert_file(self, file_path_str: str, destination_dir_str: str, overwrite: bool = False) -> Dict[str, Any]:
        """Converts any supported file to Markdown and saves it to destination directory."""
        input_path = Path(file_path_str).resolve()
        if not input_path.exists():
            return {
                "success": False,
                "file_name": input_path.name,
                "error": "Source file not found."
            }

        target_dir = Path(destination_dir_str).resolve()
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {
                "success": False,
                "file_name": input_path.name,
                "error": f"Cannot access target directory: {e}"
            }

        base_name = input_path.stem
        output_file = (target_dir / f"{base_name}.md") if overwrite else self._get_unique_path(target_dir, base_name)

        try:
            # Process conversion with MarkItDown
            result = self.md.convert(str(input_path))
            content = (result.text_content or "").strip()

            # Save full markdown file in UTF-8
            with open(output_file, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)

            return {
                "success": True,
                "file_name": input_path.name,
                "input_path": str(input_path),
                "output_path": str(output_file),
                "output_dir": str(target_dir),
                "chars_count": len(content),
                "lines_count": len(content.splitlines()),
                "content": content,  # Full markdown content for viewing and copying
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "file_name": input_path.name,
                "input_path": str(input_path),
                "error": str(e)
            }
