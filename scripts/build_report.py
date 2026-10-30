"""Bangun laporan praktik Milestone 1 — format akademik TNR 12/14, margin 4-4-3-3, A4."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BLACK = RGBColor(0, 0, 0)
os.makedirs("laporan", exist_ok=True)
doc = Document()

sec = doc.sections[0]
sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
sec.top_margin = Cm(4); sec.left_margin = Cm(4)
sec.right_margin = Cm(3); sec.bottom_margin = Cm(3)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.font.size = Pt(12); normal.font.color.rgb = BLACK
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

for name, size, center in [("Heading 1", 14, True),
                           ("Heading 2", 12, False),
                           ("Heading 3", 12, False)]:
    s = doc.styles[name]
    s.font.name = "Times New Roman"
    s.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = BLACK
    s.paragraph_format.space_before = Pt(12); s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.line_spacing = 1.5
    if center:
        s.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if name == "Heading 1":
        s.font.all_caps = True

def bab(t):
    doc.add_page_break()
    doc.add_heading(t, level=1)

def sub(t):
    doc.add_heading(t, level=2)

def p(t, indent=True):
    q = doc.add_paragraph()
    if indent:
        q.paragraph_format.first_line_indent = Cm(1.0)
    q.add_run(t)
    return q

def center(t, size=12, bold=False):
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.first_line_indent = Cm(0)
    r = q.add_run(t); r.bold = bold; r.font.size = Pt(size)
    return q

def table(headers, rows):
    tb = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tb.style = "Table Grid"
    tb.alignment = 1
    for j, x in enumerate(headers):
        c = tb.cell(0, j); c.text = ""
        r = c.paragraphs[0].add_run(x)
        r.bold = True; r.font.size = Pt(11)
    for i, row in enumerate(rows, 1):
        for j, x in enumerate(row):
            c = tb.cell(i, j); c.text = ""
            r = c.paragraphs[0].add_run(str(x)); r.font.size = Pt(11)
    doc.add_paragraph()
    return tb

def gambar(path, caption):
    doc.add_picture(path, width=Cm(13))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    q = doc.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.first_line_indent = Cm(0)
    r = q.add_run(caption); r.font.size = Pt(11)

# ================= COVER =================
for _ in range(2):
    doc.add_paragraph()
center("LAPORAN PRAKTIK", 14, True)
center("STUDY CLUB DATA SCIENCE BASIC", 14, True)
center("MILESTONE 1: MARKET PRIORITIZATION UNTUK UMKM", 14, True)
center("Menentukan Segmen dan Wilayah Target Sourcing Leads B2B SaaS (Klay \u2014 Skalar Solutions)", 12, True)
for _ in range(2):
    doc.add_paragraph()
center("Disusun oleh Kelompok [Nomor Kelompok]", 12, False)
table(["Nama Anggota", "NIM", "Pembagian Tugas"],
      [["[ISI NAMA 1]", "[ISI NIM 1]", "Data collection dan cleaning ODJ"],
       ["[ISI NAMA 2]", "[ISI NIM 2]", "Ekstraksi BPS dan merging"],
       ["[ISI NAMA 3]", "[ISI NIM 3]", "EDA dan visualisasi"],
       ["[ISI NAMA 4]", "[ISI NIM 4]", "Bobot ICP dan laporan"]])
center("[NAMA PROGRAM STUDI]", 12, True)
center("[NAMA FAKULTAS / UNIVERSITAS]", 12, True)
center("2026", 12, True)

# ================= PENGESAHAN =================
doc.add_page_break()
center("LEMBAR PENGESAHAN", 14, True)
p("Laporan praktik Milestone 1 berjudul Market Prioritization untuk UMKM: Menentukan Segmen dan Wilayah "
  "Target Sourcing Leads B2B SaaS (Klay \u2014 Skalar Solutions) ini disusun oleh Kelompok [Nomor Kelompok] "
  "dan telah disahkan pada tanggal [ISI TANGGAL].", indent=False)
doc.add_paragraph()
table(["Pihak", "Nama", "Tanda Tangan"],
      [["Ketua Kelompok", "[ISI NAMA]", ""],
       ["Pembimbing / Mentor", "[ISI NAMA]", ""],
       ["Mitra (Skalar Solutions)", "[ISI NAMA]", ""]])

# ================= KATA PENGANTAR =================
doc.add_page_break()
center("KATA PENGANTAR", 14, True)
p("Puji syukur kami panjatkan atas terselesaikannya laporan praktik Milestone 1 Study Club Data Science Basic "
  "kerja sama KSM Veterantech UPNVJ 2026 dengan mitra Skalar Solutions.")
p("Laporan ini menyajikan fondasi berbasis data untuk menentukan sektor dan wilayah UMKM yang diprioritaskan "
  "dalam sourcing leads produk Klay. Ruang lingkup laporan ini hanya sampai perancangan matriks bobot Indeks "
  "Prioritas berbasis Ideal Customer Profile (ICP); pemodelan K-Means, skoring final, dan Top 5 segmen merupakan "
  "tahap berikutnya dan tidak dikerjakan di sini.")
p("Kami mengucapkan terima kasih kepada mentor, mitra Skalar Solutions, serta penyedia data publik (Badan Pusat "
  "Statistik, Open Data Jawa Barat, dan Bank Indonesia) yang datanya menjadi bahan analisis ini.")

# ================= DAFTAR ISI =================
doc.add_page_break()
center("DAFTAR ISI", 14, True)
for x in ["LEMBAR PENGESAHAN", "KATA PENGANTAR", "DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR",
          "BAB I PENDAHULUAN", "BAB II TINJAUAN PUSTAKA", "BAB III METODOLOGI",
          "BAB IV HASIL DAN PEMBAHASAN", "BAB V PENUTUP", "DAFTAR PUSTAKA", "LAMPIRAN"]:
    q = doc.add_paragraph(); q.paragraph_format.first_line_indent = Cm(0)
    q.add_run(x)
doc.add_paragraph()
center("DAFTAR TABEL", 14, True)
for x in ["Tabel 3.1 Sumber data publik yang digunakan",
          "Tabel 3.2 Pemetaan kategori usaha ke kelompok ICP",
          "Tabel 4.1 Wilayah tereliminasi beserta alasan",
          "Tabel 4.2 Rancangan bobot Indeks Prioritas"]:
    q = doc.add_paragraph(); q.paragraph_format.first_line_indent = Cm(0)
    q.add_run(x)
doc.add_paragraph()
center("DAFTAR GAMBAR", 14, True)
for x in ["Gambar 4.1 Distribusi ukuran pasar UMKM per wilayah",
          "Gambar 4.2 Kepadatan sektor target ICP per wilayah",
          "Gambar 4.3 Internet vs ukuran pasar",
          "Gambar 4.4 Daya beli vs adopsi pembayaran digital",
          "Gambar 4.5 Komposisi sektor 12 wilayah terbesar",
          "Gambar 4.6 Korelasi antar indikator ICP"]:
    q = doc.add_paragraph(); q.paragraph_format.first_line_indent = Cm(0)
    q.add_run(x)

# ================= BAB I =================
bab("BAB I PENDAHULUAN")
sub("1.1 Latar Belakang")
p("Tim sales Skalar Solutions melakukan sourcing leads calon klien UMKM secara manual dan belum terarah, "
  "sehingga volume kontak belum cukup berdampak pada pipeline. Produk Klay (POS berbasis cloud dan dashboard "
  "analitik AI untuk UMKM) memiliki profil klien ideal (ICP) yang jelas \u2014 ritel, food and beverage (F&B), "
  "dan jasa transaksi kecil berulang \u2014 tetapi belum ada dasar data untuk menentukan sektor dan wilayah mana "
  "yang dikejar lebih dulu. Praktik ini menyusun fondasi tersebut dari data publik yang sah.")
sub("1.2 Rumusan Masalah")
p("Bagaimana menentukan sektor dan wilayah UMKM yang paling layak diprioritaskan untuk sourcing leads Klay "
  "berdasarkan indikator publik yang terukur dan selaras dengan ICP?")
sub("1.3 Tujuan")
p("Tujuan praktik ini adalah: (1) mengumpulkan dan membersihkan data publik yang relevan; (2) melakukan EDA "
  "dan visualisasi potensi wilayah; serta (3) merancang matriks bobot Indeks Prioritas berbasis ICP. Unit "
  "analisis adalah kombinasi satu sektor dengan satu wilayah pada 27 kabupaten/kota Jawa Barat.")
sub("1.4 Manfaat")
p("Bagi Sales Development Representative (SDR) Skalar, hasil praktik ini memberi peta wilayah prospek yang "
  "terukur, indikator yang dapat dipantau, dan bobot prioritas yang terjustifikasi sebelum memperbesar volume "
  "sourcing melalui scraping atau otomasi.")
sub("1.5 Batasan Masalah")
p("Laporan ini hanya sampai perancangan bobot. K-Means/Elbow/Silhouette, skor indeks final, Top 5 segmen, "
  "sensitivity check, analisis legalitas scraping, dan slide presentasi tidak dikerjakan.")

# ================= BAB II =================
bab("BAB II TINJAUAN PUSTAKA")
sub("2.1 Produk Klay dan ICP Skalar")
p("Klay adalah platform kasir (POS) berbasis cloud yang terintegrasi dengan pembayaran digital (termasuk QRIS) "
  "dan dashboard analitik penjualan. ICP Klay mencakup sektor ritel, F&B (kafe, warung makan, katering), dan "
  "jasa transaksi kecil berulang (laundry, salon, bengkel); skala SMEs dengan transaksi hampir harian, "
  "pencatatan manual/spreadsheet, siap QRIS, multi-kasir/outlet, dan membutuhkan analitik (produk terlaris, "
  "jam ramai, performa cabang). Kriteria wilayah ICP meliputi ukuran pasar, kepadatan sektor target, kesiapan "
  "digital, adopsi pembayaran digital, dan aktivitas ekonomi.")
sub("2.2 Segmen dan Wilayah")
p("Segmen didefinisikan sebagai kombinasi satu sektor dengan satu wilayah (misalnya F&B di Kota Bandung). "
  "Wilayah yang jumlah UMKM-nya sangat kecil, yang data kuncinya kosong, atau yang sektornya tanpa transaksi "
  "harian rutin digugurkan dari ranking dan dicatat alasannya.")
sub("2.3 Data Publik yang Digunakan")
p("Data berasal dari Open Data Jawa Barat (Dinas Koperasi dan Usaha Kecil; Badan Pendapatan Daerah), Badan "
  "Pusat Statistik (publikasi Dalam Angka 2025 dan Statistik Kesejahteraan Rakyat 2025 berbasis Susenas Maret "
  "2025), serta publikasi Bank Indonesia sebagai konteks pembayaran digital. Seluruh angka tertelusur ke sumber "
  "dan tidak ada data sintetis.")

# ================= BAB III =================
bab("BAB III METODOLOGI")
sub("3.1 Sumber Data")
table(["Kode", "Sumber", "Tahun", "Level", "Kolom kunci", "Untuk indikator"],
      [["S1", "ODJ Diskuk: proyeksi UMKM per kab/kota x kategori", "2023", "kab/kota (27)",
        "kode_kabupaten_kota, kategori_usaha, proyeksi_jumlah_umkm", "Ukuran Pasar"],
       ["S2", "ODJ Diskuk: UMKM binaan per kab/kota x jenis usaha", "2023", "kab/kota (27)",
        "jenis_usaha, jumlah_umkm", "Kepadatan Sektor Target"],
       ["S3", "ODJ Bapenda: e-Samsat per cabang x bank", "2024", "kab/kota (agregat)",
        "jumlah_pembayaran (Rp)", "Adopsi Pembayaran Digital (proksi)"],
       ["S4a", "BPS Jabar Dalam Angka 2025, Tabel 13.2.5 hlm. 799", "2024**", "kab/kota (27)",
        "PDRB per kapita ADHB (ribu Rp)", "Aktivitas Ekonomi"],
       ["S4b", "BPS Kesra Jabar 2025, Tabel 7.4 hlm. 118 (Susenas)", "2025", "kab/kota (27)",
        "% penduduk 5+ pengguna internet", "Kesiapan Digital"]])
p("Tanggal akses seluruh sumber: 30 Oktober 2026. Seluruh indikator tersedia di level kab/kota sehingga tidak "
  "diperlukan penggabungan many-to-one provinsi ke kab/kota. QRIS level kab/kota tidak dipublikasikan "
  "(BI hanya merilis level provinsi: Jawa Barat 8,28 juta merchant pada triwulan I 2025), sehingga dipakai "
  "proksi e-Samsat (S3). Rincian URL dan sumber yang gagal diakses tercatat pada SOURCES.md.")
sub("3.2 Tahapan Analisis")
p("Tahapan yang dilaksanakan: (1) load dan pemeriksaan awal tiap dataset (shape, dtypes, head); (2) cleaning "
  "(missing, duplikat, anomali/outlier, standardisasi nama wilayah dengan kode BPS sebagai kunci, baris gagal "
  "match ditampilkan); (3) pemetaan kategori usaha ke tiga kelompok ICP; (4) merging dengan left join pada kode "
  "kabupaten/kota disertai validasi jumlah baris dan duplikasi; (5) filter penggugur; (6) normalisasi MinMax "
  "pada fitur numerik; (7) EDA dan visualisasi; (8) rancangan bobot. Pustaka: pandas, numpy, matplotlib, "
  "seaborn, scikit-learn (hanya MinMaxScaler).")
sub("3.3 Pemetaan Kategori ke Kelompok ICP")
table(["Kelompok ICP", "Kategori ODJ", "Alasan"],
      [["Ritel (G)", "FASHION, KONVEKSI", "Produk diperdagangkan eceran, transaksi harian"],
       ["F&B (I)", "KULINER, MAKANAN, MINUMAN", "Makanan/minuman siap saji dan kemasan"],
       ["Jasa rutin (S)", "JASA", "Jasa kecil berulang"],
       ["Di luar ICP", "AGRIBISNIS, AKSESORIS, BATIK, BORDIR, CRAFT, DEKORASI, INDUSTRI, MEBEL, OBAT-OBATAN",
        "Produksi/batch/musiman, bukan transaksi harian rutin"]])
p("Komposisi kategori pada S1 identik antar wilayah (simpangan baku < 1e-5), sehingga komposisi dihitung dari "
  "S2 yang bervariasi nyata. Pada binaan 2023 jenis kuliner/makanan/minuman tercatat nol (bias program yang "
  "didominasi fashion), dicatat sebagai keterbatasan.")
sub("3.4 Kriteria Penggugur dan Normalisasi")
p("Wilayah diurutkan menurut total UMKM menurun; yang secara kumulatif mencakup minimal 95 persen total UMKM "
  "Jawa Barat dipertahankan, sisanya tereliminasi karena kontribusi marjinal. Seluruh indikator berarah positif "
  "(makin tinggi makin baik) dan dinormalisasi MinMax ke rentang 0-1; versi unscaled disimpan terpisah.")

# ================= BAB IV =================
bab("BAB IV HASIL DAN PEMBAHASAN")
sub("4.1 Hasil Cleaning, Merging, dan Eliminasi")
p("Missing bernilai nol pada semua tabel dan tidak ada duplikat kunci. Kunci kode BPS 3201-3218 dan 3271-3279 "
  "selaras di lima tabel (27 unit). Uji outlier IQR pada total UMKM tidak menemukan pencilan yang harus "
  "dibuang. Merging 27 menjadi 27 baris tanpa kehilangan atau duplikasi. Artefak OCR pada ekstraksi PDF "
  "diselesaikan di scripts/extract_bps_tables.py dan divalidasi silang.")
table(["Wilayah", "Total UMKM 2023", "Alasan eliminasi"],
      [["KABUPATEN PANGANDARAN", "91.786", "Di luar 95% kumulatif total UMKM Jawa Barat"],
       ["KOTA CIMAHI", "86.636", "Di luar 95% kumulatif total UMKM Jawa Barat"],
       ["KOTA CIREBON", "61.234", "Di luar 95% kumulatif total UMKM Jawa Barat"],
       ["KOTA SUKABUMI", "60.866", "Di luar 95% kumulatif total UMKM Jawa Barat"],
       ["KOTA BANJAR", "39.422", "Di luar 95% kumulatif total UMKM Jawa Barat"]])
p("Lima wilayah tereliminasi hanya mencakup 4,8 persen total UMKM sehingga fokus analisis pada 22 wilayah "
  "final. Tidak dilakukan imputasi tebakan; tidak ada wilayah dengan data kunci kosong. Daftar lengkap "
  "tersimpan pada data_eliminated.csv; data final pada data_clean_merged.csv dan data_scaled.csv.")
sub("4.2 Hasil EDA dan Visualisasi")
gambar("assets/g1_distribusi_umkm.png", "Gambar 4.1 Distribusi ukuran pasar UMKM per wilayah")
p("Distribusi bersifat right-skew: tiga wilayah raksasa (Kabupaten Bogor 571 ribu, Kabupaten Bandung 538 ribu, "
  "Kota Bandung 524 ribu) jauh di atas median sekitar 150 ribu. Bagi SDR, pipeline prospek terkonsentrasi pada "
  "sebagian kecil wilayah, sehingga penjadwalan kunjungan dan akuisisi sebaiknya dibobot ke wilayah besar "
  "terlebih dahulu.")
gambar("assets/g2_kepadatan_icp.png", "Gambar 4.2 Kepadatan sektor target ICP per wilayah")
p("Kepadatan sektor ICP berkisar 57,5 persen (Kabupaten Bandung Barat) hingga 91,3 persen (Kabupaten "
  "Kuningan); Kabupaten Kuningan, Kota Tasikmalaya, dan Kabupaten Ciamis paling murni ritel/jasa harian. "
  "Angka ini mengukur porsi ritel dan jasa harian karena F&B tidak muncul pada data binaan (bias program). "
  "SDR dapat memakai peringkat ini untuk memilih wilayah dengan probabilitas product-fit tertinggi.")
gambar("assets/g3_internet_vs_pasar.png", "Gambar 4.3 Internet vs ukuran pasar (warna = PDRB/kapita)")
p("Korelasi Pearson sebesar -0,07 (praktis nol): kota-kota kecil justru paling digital (85-93 persen), "
  "sementara kabupaten besar berada pada 67-81 persen. Kesiapan digital tidak dapat menjadi proksi ukuran "
  "pasar sehingga keduanya dipertahankan sebagai komponen bobot yang terpisah.")
gambar("assets/g4_pdrb_vs_adopsi.png", "Gambar 4.4 Daya beli vs adopsi pembayaran digital")
p("Korelasi sebesar +0,42 (moderat): wilayah dengan PDRB per kapita tinggi (Kota Bandung, Karawang, Bekasi) "
  "membayar pajak kendaraan secara digital jauh lebih besar per UMKM-nya (tertinggi Kota Depok). Hasil ini "
  "memvalidasi proksi e-Samsat: kebiasaan transaksi digital bergerak searah dengan daya beli, dan kuadran "
  "kanan-atas adalah wilayah dengan friksi adopsi QRIS dan analitik Klay terendah.")
gambar("assets/g5_heatmap_sektor.png", "Gambar 4.5 Komposisi sektor 12 wilayah terbesar")
p("Ritel (terutama fashion) mendominasi UMKM binaan di semua wilayah terbesar (59-79 persen, tertinggi "
  "Kabupaten Bandung 79 persen). Kolom F&B bernilai nol di seluruh wilayah karena program binaan Diskuk 2023 "
  "tidak menyentuh kuliner, padahal pada populasi F&B besar. Daftar binaan bukan daftar prospek: untuk F&B, "
  "SDR merujuk pada data populasi S1.")
gambar("assets/g6_corr_matrix.png", "Gambar 4.6 Korelasi antar indikator ICP")
p("Tidak ada korelasi di atas 0,6 antar indikator: kelima indikator membawa sinyal yang berbeda tanpa duplikasi "
  "berlebih. Struktur bobot 30/25/20/15/10 dengan demikian mewakili lima dimensi keputusan yang independen.")
sub("4.3 Rancangan Bobot Indeks Prioritas")
table(["Komponen", "Indikator publik", "Arah", "Bobot", "Justifikasi (kaitan ICP Klay)"],
      [["Ukuran Pasar", "Total UMKM 2023 per kab/kota (S1)", "+", "30%",
        "Pipeline SDR: makin banyak UMKM makin banyak prospek yang dapat dihubungi."],
       ["Kepadatan Sektor Target", "Share UMKM binaan Ritel/F&B/Jasa (S2)", "+", "25%",
        "Product-fit: dagang eceran dan jasa rutin harian paling membutuhkan POS dan analitik."],
       ["Kesiapan Digital", "% penduduk pengguna internet 2025 (S4b)", "+", "20%",
        "Prasyarat POS cloud dan dashboard AI; wilayah offline butuh edukasi panjang."],
       ["Adopsi Pembayaran Digital", "Nominal e-Samsat per UMKM 2024, proksi (S3)", "+", "15%",
        "Bukti perilaku bayar digital (korelasi +0,42 dengan daya beli); QRIS kab/kota tidak dipublikasikan."],
       ["Aktivitas Ekonomi", "PDRB per kapita 2024 (S4a)", "+", "10%",
        "Daya beli menopang kemampuan langganan SaaS; bobot terkecil karena Klay menyasar volume UMKM."],
       ["Total", "", "", "100%", "Terverifikasi di kode: sum == 100."]])
p("Skor indeks final, pengelompokan K-Means, Top 5 segmen, dan uji sensitivitas merupakan Milestone 2 dan tidak "
  "dikerjakan dalam laporan ini.")

# ================= BAB V =================
bab("BAB V PENUTUP")
sub("5.1 Kesimpulan")
p("Pertama, fondasi data 27 kabupaten/kota Jawa Barat berhasil disusun dari empat sumber publik mutakhir "
  "dengan seluruh angka tertelusur. Kedua, lima wilayah marjinal tereliminasi secara berprinsip sehingga "
  "analisis berfokus pada 22 wilayah yang mencakup 95,2 persen UMKM. Ketiga, pasar terkonsentrasi pada tiga "
  "wilayah besar, kota menjadi kantong digital dan adopsi sedangkan kabupaten menjadi kantong volume. "
  "Keempat, rancangan bobot 30/25/20/15/10 ditetapkan dengan justifikasi ICP dan terverifikasi berjumlah 100.")
sub("5.2 Saran")
p("Bagi SDR Skalar: prioritaskan penjadwalan ke wilayah besar bervolume tinggi, gunakan peringkat kepadatan "
  "sektor untuk memilih angle pitch (ritel vs jasa), dan mulai dari kuadran kaya-digital untuk friksi adopsi "
  "terendah. Bagi tahap berikutnya: lengkapi data F&B populasi, kejar seri QRIS kab/kota bila tersedia, lalu "
  "lanjutkan ke K-Means, skoring, Top 5 segmen, dan sensitivity check.")
p("Keterbatasan utama: S1 berlabel proyeksi; S2 hanya UMKM binaan dengan n 97-175 per wilayah dan bias fashion; "
  "e-Samsat adalah proksi bukan QRIS; PDRB 2024 sangat sementara; Susenas memakai sampel.")

# ================= PUSTAKA =================
bab("DAFTAR PUSTAKA")
for x in ["Badan Pusat Statistik Provinsi Jawa Barat. 2025. Provinsi Jawa Barat Dalam Angka 2025. No. Publikasi "
          "32000.25001. Bandung: BPS Provinsi Jawa Barat.",
          "Badan Pusat Statistik Provinsi Jawa Barat. 2025. Statistik Kesejahteraan Rakyat Provinsi Jawa Barat "
          "2025. No. Publikasi 32000.25059. Bandung: BPS Provinsi Jawa Barat.",
          "Badan Pusat Statistik. 2024. Statistik Telekomunikasi Indonesia 2023. No. Publikasi 06300.24009. "
          "Jakarta: BPS.",
          "Bank Indonesia. 2025. Laporan Perekonomian Provinsi Jawa Barat Mei 2025. Jakarta: Bank Indonesia.",
          "Bank Indonesia. 2024. Laporan Perekonomian Provinsi Banten Mei 2024. Jakarta: Bank Indonesia.",
          "Dinas Koperasi dan Usaha Kecil Provinsi Jawa Barat. Proyeksi Jumlah UMKM Berdasarkan Kabupaten/Kota "
          "dan Kategori Usaha di Jawa Barat 2017-2023. Open Data Jawa Barat. Diakses 30 Oktober 2026.",
          "Dinas Koperasi dan Usaha Kecil Provinsi Jawa Barat. Jumlah UMKM Binaan Berdasarkan Jenis Usaha di "
          "Jawa Barat 2019-2023. Open Data Jawa Barat. Diakses 30 Oktober 2026.",
          "Badan Pendapatan Daerah Provinsi Jawa Barat. Jumlah Pembayaran PKB Melalui e-Samsat Berdasarkan Bank "
          "Penerima dan Cabang Pelayanan 2014-2025. Open Data Jawa Barat. Diakses 30 Oktober 2026.",
          "PT Skalar Solusi Digital. 2026. Case Study Brief: Market Prioritization untuk UMKM dan Brief ICP "
          "Klay. Jakarta: Skalar Solutions."]:
    q = doc.add_paragraph()
    q.paragraph_format.left_indent = Cm(1.0)
    q.paragraph_format.first_line_indent = Cm(-1.0)
    q.add_run(x)

# ================= LAMPIRAN =================
bab("LAMPIRAN")
sub("Lampiran 1. Akses Notebook dan Berkas")
p("Link Colab (atur akses Anyone with the link can view): [ISI LINK COLAB]", indent=False)
p("Berkas notebook: notebooks/Milestone1_ICP_Klay_Jabar.ipynb dan notebooks/Milestone2_ICP_Klay_Jabar.ipynb", indent=False)
p("Berkas data: output/ (CSV final), data/ (5 CSV sumber), "
  "assets/ (10 gambar), scripts/extract_bps_tables.py, SOURCES.md.", indent=False)

doc.save("laporan/Tugas2_DS_Kelompok[NomorKelompok].docx")
print("laporan tersimpan")
