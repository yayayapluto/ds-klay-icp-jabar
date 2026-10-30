# Market Prioritization UMKM untuk Klay (Skalar Solutions)

Milestone 1 + 2, Study Club Data Science Basic — KSM Veterantech UPNVJ 2026.
Unit analisis: 27 kabupaten/kota Jawa Barat (22 final setelah eliminasi).

## Struktur

- `notebooks/` — Milestone 1 (collection s.d. bobot) dan Milestone 2 (skor s.d. Top 5)
- `laporan/` — laporan praktik DOCX (format akademik)
- `output/` — CSV final (clean, scaled, eliminasi, skor, klaster, Top 5)
- `data/` — 5 CSV sumber + 2 PDF BPS + JSON mentah Open Data Jabar
- `assets/` — 10 gambar grafik (g1–g6 Milestone 1, g7–g10 Milestone 2)
- `scripts/` — `extract_bps_tables.py` (ekstraksi tabel PDF BPS) dan `build_*.py`
  (generator notebook/laporan)
- `docs-penugasan/` — brief studi kasus dan ICP dari mitra

## Reproduksi

```bash
pip install pandas numpy matplotlib seaborn scikit-learn pdfplumber python-docx jupyter
python scripts/extract_bps_tables.py   # butuh 2 PDF BPS di data/
python scripts/build_notebook.py       # bangun Milestone 1
python scripts/build_notebook2.py      # bangun Milestone 2
python scripts/build_report.py         # bangun laporan DOCX
```

Untuk Google Colab: upload `data/*.csv` (5 file) ke folder `data/`,
lalu Runtime > Run all.
