"""Export CSV/Excel básico."""

from __future__ import annotations

from marketfinder.data.excel_io import export_ranking_csv, export_ranking_xlsx


def test_export_csv_and_xlsx(data_dir) -> None:
    rows = [
        {
            "rank": 1,
            "product": "FICTICIO Gadget A",
            "score": 85.0,
            "confidence": 60.0,
            "band": "alta",
            "qty": 10,
            "capital": 300.0,
            "notes": "FICTICIO",
        }
    ]
    csv_path = export_ranking_csv(rows, data_dir=data_dir)
    xlsx_path = export_ranking_xlsx(rows, data_dir=data_dir)
    assert csv_path.is_file()
    assert xlsx_path.is_file()
    text = csv_path.read_text(encoding="utf-8-sig")
    assert "FICTICIO Gadget A" in text
