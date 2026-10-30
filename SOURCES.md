# Sumber Data — Milestone 1 ICP Klay (Jawa Barat, 27 kab/kota)

Tanggal akses semua sumber: 30 Oktober 2026. Tahun data yang dipakai: 2023–2025 (semua ≤ 5 tahun).

## S1 — Open Data Jabar, Dinas Koperasi dan Usaha Kecil: Proyeksi UMKM per Kab/Kota × Kategori
- URL dataset: https://opendata.jabarprov.go.id/id/dataset/proyeksi-jumlah-usaha-mikro-kecil-menengah-umkm-berdasarkan-kabupatenkota-dan-kategori-usaha-di-jawa-barat
- Endpoint API: https://data.jabarprov.go.id/api-backend/bigdata/diskuk/od_17371_proyeksi_jml_ush_mikro_kecil_menengah_umkm__kabupa_v2
- Tahun data dipakai: 2023 (rentang API 2017–2023). Level: kabupaten/kota (27 unit) × 10 kategori usaha.
- Kolom kunci: kode_kabupaten_kota, nama_kabupaten_kota, kategori_usaha, proyeksi_jumlah_umkm, tahun.
- Alasan: satu-satunya sumber terbuka dengan jumlah UMKM per kab/kota + rincian kategori (dasar Ukuran Pasar).
- Keterbatasan: angka berlabel "proyeksi"; komposisi kategori identik di semua kab/kota (std share < 1e-5) sehingga TIDAK dipakai untuk komposisi sektor.

## S2 — Open Data Jabar, Dinas Koperasi dan Usaha Kecil: UMKM Binaan per Kab/Kota × Jenis Usaha
- URL dataset: https://opendata.jabarprov.go.id/id/dataset/jumlah-usaha-mikro-kecil-dan-menengah-umkm-binaan-berdasarkan-jenis-usaha-di-jawa-barat
- Endpoint API: https://data.jabarprov.go.id/api-backend/bigdata/diskuk/od_17367_jml_ush_mikro_kecil_menengah_umkm_binaan__jenis_us_v2
- Tahun data dipakai: 2023 (rentang 2019–2023). Level: kabupaten/kota (27 unit) × 15 jenis usaha. File lokal: data/umkm_binaan_2023.csv (405 baris).
- Alasan: komposisi jenis usaha bervariasi antar kab/kota (dasar Kepadatan Sektor Target ICP).
- Keterbatasan: hanya UMKM binaan (±3.861 unit, 2023), bukan sensus; n per kab/kota 97–175 sehingga share punya sampling noise ±4–5 pp.

## S3 — Open Data Jabar, Bapenda: Pembayaran PKB via e-Samsat per Kab/Kota
- URL dataset: https://opendata.jabarprov.go.id/id/dataset/jumlah-pembayaran-pajak-kendaraan-bermotor-melalui-e-samsat-berdasarkan-bank-penerima-dan-cabang-pelayanan-di-jawa-barat
- Endpoint API: https://data.jabarprov.go.id/api-backend/bigdata/bapenda/od_15834_jml_pembayaran_pajak_kndrn_brmtr_melalui_e_samsat__v6
- Tahun data dipakai: 2024 (rentang 2014–2025). Level: kabupaten/kota (27 unit, agregat dari cabang pelayanan × bank).
- Kolom dipakai: jumlah_pembayaran (satuan RUPIAH = nominal). File lokal: data/esamsat_2024.csv.
- Alasan: proksi Adopsi Pembayaran Digital — nilai transaksi digital riil per wilayah (QRIS per kab/kota tidak dipublikasikan).
- Keterbatasan: proksi tidak sempurna (pajak kendaraan ≠ QRIS UMKM); didukung konteks BI: merchant QRIS Jabar 8,28 jt (Q1-2025, https://bi.go.id/id/publikasi/laporan/lpp/Pages/Laporan-Perekonomian-Provinsi-Jawa-Barat-Mei-2025.aspx).

## S4 — BPS: (a) PDRB per kapita kab/kota 2024 + (b) Internet per kab/kota 2025
- (a) Publikasi "Provinsi Jawa Barat Dalam Angka 2025", No. Publikasi 32000.25001, rilis 28 Feb 2025 (revisi 30 Apr 2025). URL: https://jabar.bps.go.id/id/publication/2025/02/28/d906b36c4b300ab77908dfe2/provinsi-jawa-barat-dalam-angka-2025.html. Tabel 13.2.5 hlm. 799: PDRB per kapita ADHB per kab/kota 2020–2024 (ribu Rp). File lokal: data/pdrb_2024.csv. Ekstraksi: scripts/extract_bps_tables.py (pdfplumber, validasi 27 baris + nilai spot-check).
- (b) Publikasi "Statistik Kesejahteraan Rakyat Provinsi Jawa Barat 2025", No. Publikasi 32000.25059, rilis 28 Nov 2025 (Susenas Maret 2025). URL: https://jabar.bps.go.id/id/publication/2025/11/28/5c47dbf83e4123e9a4707950/statistik-kesejahteraan-rakyat-provinsi-jawa-barat-2025.html. Tabel 7.4 hlm. 118: % penduduk 5+ pengguna internet per kab/kota. File lokal: data/internet_2025.csv.
- Alasan: Aktivitas Ekonomi (PDRB) dan Kesiapan Digital (internet) level kab/kota, mutakhir.
- Keterbatasan: PDRB 2024 bertanda ** (sangat sementara); Susenas memakai sampel (ada RSE, lihat publikasi).

## Sumber yang dicoba tetapi TIDAK dipakai (dicatat sesuai aturan "Jika Terblokir")
1. SE2016 BPS / se2016.bps.go.id — CAPTCHA; data 2016–2017 juga melanggar batas 5 tahun.
2. opendata.jabarprov.go.id via browser langsung — 502/JabarCloud WAF; diakses lewat API backend + arsip Wayback.
3. data.go.id — error aplikasi saat diakses (30 Okt 2026).
4. Publikasi BPS "Potensi UMK SE2016" DKI & Jabar — berhasil diunduh tetapi tahun data 2016–2017 (> 5 tahun), dibuang.
5. Dataset ODJ "desa internet 2025" — hanya mencakup 19 unit (kota tidak tercakup); tidak dipakai.
6. Kaggle "UMKM Dataset" (zkyfauzi) — dinyatakan sintetis oleh pemiliknya; ditolak.
