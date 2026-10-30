# Sumber Data: Milestone 1 ICP Klay (Jawa Barat, 27 kab/kota)

Seluruh sumber diakses pada 30 Oktober 2026. Tahun data yang dipakai berkisar 2023 sampai 2025,
jadi semuanya masih dalam batas 5 tahun.

## S1: Open Data Jabar, Dinas Koperasi dan Usaha Kecil (Proyeksi UMKM per Kab/Kota x Kategori)
- URL dataset: https://opendata.jabarprov.go.id/id/dataset/proyeksi-jumlah-usaha-mikro-kecil-menengah-umkm-berdasarkan-kabupatenkota-dan-kategori-usaha-di-jawa-barat
- Endpoint API: https://data.jabarprov.go.id/api-backend/bigdata/diskuk/od_17371_proyeksi_jml_ush_mikro_kecil_menengah_umkm__kabupa_v2
- Tahun data yang dipakai: 2023 (rentang API 2017 sampai 2023). Level: kabupaten/kota (27 unit) x 10 kategori usaha.
- Kolom kunci: kode_kabupaten_kota, nama_kabupaten_kota, kategori_usaha, proyeksi_jumlah_umkm, tahun.
- Alasan: satu-satunya sumber terbuka yang memuat jumlah UMKM per kab/kota sekaligus rincian kategorinya, sehingga menjadi dasar Ukuran Pasar.
- Keterbatasan: angkanya berlabel "proyeksi"; komposisi kategori seragam di semua kab/kota (std share < 1e-5) sehingga tidak dipakai untuk komposisi sektor.

## S2: Open Data Jabar, Dinas Koperasi dan Usaha Kecil (UMKM Binaan per Kab/Kota x Jenis Usaha)
- URL dataset: https://opendata.jabarprov.go.id/id/dataset/jumlah-usaha-mikro-kecil-dan-menengah-umkm-binaan-berdasarkan-jenis-usaha-di-jawa-barat
- Endpoint API: https://data.jabarprov.go.id/api-backend/bigdata/diskuk/od_17367_jml_ush_mikro_kecil_menengah_umkm_binaan__jenis_us_v2
- Tahun data yang dipakai: 2023 (rentang 2019 sampai 2023). Level: kabupaten/kota (27 unit) x 15 jenis usaha. File lokal: data/umkm_binaan_2023.csv (405 baris).
- Alasan: komposisi jenis usahanya bervariasi antar kab/kota, sehingga menjadi dasar Kepadatan Sektor Target ICP.
- Keterbatasan: cakupannya hanya UMKM binaan (sekitar 3.861 unit pada 2023), bukan sensus; n per kab/kota 97 sampai 175 sehingga share-nya mengandung sampling noise sekitar 4-5 pp.

## S3: Open Data Jabar, Bapenda (Pembayaran PKB via e-Samsat per Kab/Kota)
- URL dataset: https://opendata.jabarprov.go.id/id/dataset/jumlah-pembayaran-pajak-kendaraan-bermotor-melalui-e-samsat-berdasarkan-bank-penerima-dan-cabang-pelayanan-di-jawa-barat
- Endpoint API: https://data.jabarprov.go.id/api-backend/bigdata/bapenda/od_15834_jml_pembayaran_pajak_kndrn_brmtr_melalui_e_samsat__v6
- Tahun data yang dipakai: 2024 (rentang 2014 sampai 2025). Level: kabupaten/kota (27 unit, hasil agregat cabang pelayanan x bank).
- Kolom yang dipakai: jumlah_pembayaran (satuannya RUPIAH, berarti nominal). File lokal: data/esamsat_2024.csv.
- Alasan: proksi Adopsi Pembayaran Digital, karena memuat nilai transaksi digital riil per wilayah (data QRIS per kab/kota tidak dipublikasikan).
- Keterbatasan: proksi ini tidak sempurna (pajak kendaraan berbeda dengan QRIS UMKM); sebagai konteks dipakai angka BI, yakni merchant QRIS Jabar 8,28 jt pada Q1-2025.

## S4: BPS ((a) PDRB per kapita kab/kota 2024 + (b) Internet per kab/kota 2025)
- (a) Publikasi "Provinsi Jawa Barat Dalam Angka 2025", No. Publikasi 32000.25001, rilis 28 Feb 2025 (revisi 30 Apr 2025). URL: https://jabar.bps.go.id/id/publication/2025/02/28/d906b36c4b300ab77908dfe2/provinsi-jawa-barat-dalam-angka-2025.html. Tabel 13.2.5 hlm. 799: PDRB per kapita ADHB per kab/kota 2020 sampai 2024 (ribu Rp). File lokal: data/pdrb_2024.csv. Ekstraksi: scripts/extract_bps_tables.py (pdfplumber, validasi 27 baris + nilai spot-check).
- (b) Publikasi "Statistik Kesejahteraan Rakyat Provinsi Jawa Barat 2025", No. Publikasi 32000.25059, rilis 28 Nov 2025 (Susenas Maret 2025). URL: https://jabar.bps.go.id/id/publication/2025/11/28/5c47dbf83e4123e9a4707950/statistik-kesejahteraan-rakyat-provinsi-jawa-barat-2025.html. Tabel 7.4 hlm. 118: % penduduk 5+ pengguna internet per kab/kota. File lokal: data/internet_2025.csv.
- Alasan: Aktivitas Ekonomi (PDRB) dan Kesiapan Digital (internet) tersedia di level kab/kota dan mutakhir.
- Keterbatasan: PDRB 2024 bertanda dua bintang (sangat sementara); Susenas memakai sampel (ada RSE, lihat publikasinya).

## Sumber yang dicoba tetapi TIDAK dipakai (dicatat sesuai aturan "Jika Terblokir")
1. SE2016 BPS / se2016.bps.go.id: terhalang CAPTCHA; datanya tahun 2016-2017 sehingga melanggar batas 5 tahun.
2. opendata.jabarprov.go.id via browser langsung: 502/WAF JabarCloud; datanya diakses lewat API backend dan arsip Wayback.
3. data.go.id: aplikasinya error saat diakses (30 Okt 2026).
4. Publikasi BPS "Potensi UMK SE2016" DKI dan Jabar: berhasil diunduh tetapi tahun datanya 2016-2017 (melewati 5 tahun), sehingga dibuang.
5. Dataset ODJ "desa internet 2025": hanya mencakup 19 unit (kota tidak tercakup), sehingga tidak dipakai.
6. Kaggle "UMKM Dataset" (zkyfauzi): dinyatakan sintetis oleh pemiliknya, sehingga ditolak.
