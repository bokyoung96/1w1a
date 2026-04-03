from __future__ import annotations

import importlib
from pathlib import Path

__all__ = ("PdfRenderer",)


class PdfRenderer:
    def render(self, html_path: Path) -> Path | None:
        pdf_path, _ = self.render_with_status(html_path)
        return pdf_path

    def render_with_status(self, html_path: Path) -> tuple[Path | None, dict[str, object]]:
        html_path = Path(html_path)
        try:
            weasyprint = importlib.import_module("weasyprint")
        except ImportError as exc:
            return None, {"pdf_ok": False, "pdf_error": f"ImportError: {exc}"}

        pdf_path = html_path.with_suffix(".pdf")
        try:
            weasyprint.HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        except Exception as exc:
            return None, {"pdf_ok": False, "pdf_error": f"{type(exc).__name__}: {exc}"}
        return pdf_path, {"pdf_ok": True, "pdf_path": str(pdf_path)}
