# Market Prioritization UMKM untuk Klay (Skalar Solutions)

Milestone 1 + 2, Study Club Data Science Basic — KSM Veterantech UPNVJ 2026.
Unit analisis: 27 kabupaten/kota Jawa Barat (22 final setelah eliminasi).

## Struktur

- `Milestone1_ICP_Klay_Jabar.ipynb` — collection, cleaning, merging, EDA, rancangan bobot ICP
- `Milestone2_ICP_Klay_Jabar.ipynb` — skor prioritas, K-Means, baseline, sensitivity, Top 5, rekomendasi scraping
- `Tugas2_DS_Kelompok[NomorKelompok].docx` — laporan praktik (format akademik)
- `data/` — 5 CSV sumber + 2 PDF BPS + JSON mentah Open Data Jabar
- `assets/` — 10 gambar grafik (g1–g6 Milestone 1, g7–g10 Milestone 2)
- `scripts/` — `extract_bps_tables.py` (ekstraksi tabel PDF BPS) dan `build_*.py`
  (generator notebook/laporan)
- `docs-penugasan/` — brief studi kasus dan ICP dari mitra
- `SOURCES.md` — katalog sumber + log sumber yang gagal diakses
- CSV akar (`data_clean_merged.csv`, `data_scaled.csv`, `data_eliminated.csv`,
  `data_skor.csv`, `data_cluster.csv`, `top5_segmen.csv`) — output siap pakai

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
