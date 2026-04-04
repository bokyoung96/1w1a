from __future__ import annotations

import importlib
from pathlib import Path

from backtesting.reporting.pdf import PdfRenderer


def test_pdf_renderer_keeps_html_when_pdf_export_fails(monkeypatch, tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    html_path.write_text("<html><body>hello</body></html>", encoding="utf-8")

    def _raise_import_error(name: str):
        raise ImportError("weasyprint missing")

    monkeypatch.setattr(importlib, "import_module", _raise_import_error)

    renderer = PdfRenderer()
    pdf_path = renderer.render(html_path)
    status_path, status = renderer.render_with_status(html_path)

    assert html_path.exists()
    assert pdf_path is None
    assert status_path is None
    assert status["pdf_ok"] is False
    assert str(status["pdf_error"]).startswith("ImportError:")


def test_pdf_renderer_writes_pdf_when_export_succeeds(monkeypatch, tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    html_path.write_text("<html><body>hello</body></html>", encoding="utf-8")

    class _FakeHtml:
        def __init__(self, *, filename: str) -> None:
            self.filename = filename

        def write_pdf(self, path: str) -> None:
            Path(path).write_bytes(b"%PDF-1.4")

    class _FakeWeasyPrint:
        HTML = _FakeHtml

    monkeypatch.setattr(importlib, "import_module", lambda name: _FakeWeasyPrint())

    pdf_path, status = PdfRenderer().render_with_status(html_path)

    assert pdf_path == html_path.with_suffix(".pdf")
    assert pdf_path.exists()
    assert status == {"pdf_ok": True, "pdf_path": str(pdf_path)}


def test_pdf_renderer_writes_pdf_from_composed_report(monkeypatch, tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    asset_path = tmp_path / "page.png"
    asset_path.write_bytes(b"png")
    html_path.write_text(
        f"""
        <html>
          <body>
            <main class="report-shell">
              <section class="report-cover cover">
                <div class="hero-main">
                  <h1>Momentum Tearsheet</h1>
                </div>
              </section>
              <section class="report-section executive-spread">
                <div class="metric-strip">
                  <article class="metric-card">
                    <p class="metric-card-label">CAGR</p>
                    <p class="metric-card-value">17.2%</p>
                  </article>
                </div>
                <section class="compact-table-block">
                  <div class="table-wrap">
                    <table>
                      <tr><td>1</td></tr>
                    </table>
                  </div>
                </section>
                <img src="{asset_path.name}" alt="equity">
              </section>
            </main>
          </body>
        </html>
        """,
        encoding="utf-8",
    )

    class _FakeHtml:
        def __init__(self, *, filename: str) -> None:
            self.filename = filename

        def write_pdf(self, path: str) -> None:
            Path(path).write_bytes(b"%PDF-1.4")

    class _FakeWeasyPrint:
        HTML = _FakeHtml

    monkeypatch.setattr(importlib, "import_module", lambda name: _FakeWeasyPrint())

    pdf_path, status = PdfRenderer().render_with_status(html_path)

    assert pdf_path == html_path.with_suffix(".pdf")
    assert pdf_path is not None
    assert pdf_path.exists()
    assert status["pdf_ok"] is True
