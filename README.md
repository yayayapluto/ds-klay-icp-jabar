# Market Prioritization UMKM untuk Klay (Skalar Solutions)

Repositori ini menyimpan pengerjaan Milestone 1 dan 2, Study Club Data Science Basic,
KSM Veterantech UPNVJ 2026. Unit analisisnya 27 kabupaten/kota Jawa Barat.
Setelah tahap eliminasi, 22 wilayah masuk analisis final.

## Struktur

- `notebooks/`: Milestone 1 (pengumpulan data sampai rancangan bobot) dan Milestone 2 (skor sampai Top 5)
- `laporan/`: laporan praktik DOCX dengan format akademik
- `output/`: CSV final (data bersih, hasil scaling, daftar eliminasi, skor, klaster, Top 5)
- `data/`: 5 CSV sumber, 2 PDF BPS, dan JSON mentah Open Data Jabar
- `assets/`: 10 gambar grafik (g1 sampai g6 untuk Milestone 1, g7 sampai g10 untuk Milestone 2)
- `scripts/`: `extract_bps_tables.py` (mengekstrak tabel dari PDF BPS) dan `build_*.py`
  (membangkitkan notebook dan laporan)
- `penugasan/`: brief studi kasus dan ICP dari mitra

## Reproduksi

```bash
pip install pandas numpy matplotlib seaborn scikit-learn pdfplumber python-docx jupyter
python scripts/extract_bps_tables.py   # butuh 2 PDF BPS di data/
python scripts/build_notebook.py       # bangun Milestone 1
python scripts/build_notebook2.py      # bangun Milestone 2
python scripts/build_report.py         # bangun laporan DOCX
```

Untuk Google Colab: unggah lima file `data/*.csv` ke folder `data/`,
lalu jalankan Runtime > Run all.
