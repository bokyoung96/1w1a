# Tests Reporting Test_Pdf

> 12 nodes · cohesion 0.33

## Key Concepts

- **test_pdf.py** (18 connections) — `tests/reporting/test_pdf.py`
- **PdfRenderer** (13 connections) — `backtesting/reporting/pdf.py`
- **PdfRenderer.render_with_status()** (10 connections) — `backtesting/reporting/pdf.py`
- **test_pdf_renderer_writes_pdf_from_composed_report()** (6 connections) — `tests/reporting/test_pdf.py`
- **test_pdf_renderer_keeps_html_when_pdf_export_fails()** (5 connections) — `tests/reporting/test_pdf.py`
- **_FakeWeasyPrint** (4 connections) — `tests/reporting/test_pdf.py`
- **test_pdf_renderer_injects_print_layout_override_for_composed_reports()** (4 connections) — `tests/reporting/test_pdf.py`
- **test_pdf_renderer_writes_pdf_when_export_succeeds()** (4 connections) — `tests/reporting/test_pdf.py`
- **_FakeHtml** (3 connections) — `tests/reporting/test_pdf.py`
- **_FakeHtml.write_pdf()** (3 connections) — `tests/reporting/test_pdf.py`
- **_FakeHtml.__init__()** (1 connections) — `tests/reporting/test_pdf.py`
- **_raise_import_error()** (1 connections) — `tests/reporting/test_pdf.py`

## Relationships

- [[Docs Superpowers Reporting]] (12 shared connections)
- [[Raw Ksdq Csv]] (7 shared connections)
- [[Backtesting Reporting Frontend]] (5 shared connections)
- [[Backtesting Reporting Composers]] (1 shared connections)
- [[Docs Superpowers Backtest]] (1 shared connections)
- [[Docs Superpowers Performance]] (1 shared connections)
- [[Dashboard Frontend App]] (1 shared connections)

## Source Files

- `backtesting/reporting/pdf.py`
- `tests/reporting/test_pdf.py`

## Audit Trail

- EXTRACTED: 23 (32%)
- INFERRED: 49 (68%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*