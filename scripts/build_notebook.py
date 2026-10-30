"""Bangun Milestone1_ICP_Klay_Jabar.ipynb via nbformat."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata.update({"kernelspec": {"display_name": "Python 3",
                                    "language": "python",
                                    "name": "python3"},
                    "language_info": {"name": "python", "version": "3.10"}})

def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s))

def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s))

md("""# Milestone 1 — Prioritisasi Segmen UMKM untuk Klay (Skalar Solutions)
Wilayah: 27 kabupaten/kota Jawa Barat. Lingkup notebook ini HANYA sampai perancangan matriks bobot ICP
(tanpa K-Means, tanpa skor final/Top 5, tanpa sensitivity check — itu Milestone 2).
Jalankan berurutan dari atas (Runtime > Run all). Di Colab: upload folder `data/` berisi 5 CSV + jalankan.""")

code("""import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

os.makedirs("data", exist_ok=True)
os.makedirs("assets", exist_ok=True)
NEED = {"esamsat_2024.csv", "internet_2025.csv", "pdrb_2024.csv",
        "umkm_binaan_2023.csv", "umkm_proyeksi_2023.csv"}
assert NEED.issubset(set(os.listdir("data"))), (
    "Folder data/ belum lengkap: upload 5 file CSV (%s) ke folder data/ dulu, "
    "lalu Runtime > Run all ulang." % ", ".join(sorted(NEED)))

RANDOM_STATE = 42
plt.rcParams.update({"figure.dpi": 110, "font.size": 10})
PALET = "viridis"
print("pandas", pd.__version__)
""")

md("""## Bagian 1 — Data Collection & Understanding
| # | Sumber | Akses | Tahun | Level | Kolom kunci | Untuk indikator |
|---|---|---|---|---|---|---|
| S1 | Open Data Jabar — Diskuk, Proyeksi UMKM per kab/kota × kategori (API `od_17371...v2`) | https://opendata.jabarprov.go.id/id/dataset/proyeksi-jumlah-usaha-mikro-kecil-menengah-umkm-berdasarkan-kabupatenkota-dan-kategori-usaha-di-jawa-barat — diakses 30 Okt 2026 | 2023 | kab/kota | kode_kabupaten_kota, kategori_usaha, proyeksi_jumlah_umkm | Ukuran Pasar |
| S2 | Open Data Jabar — Diskuk, UMKM Binaan per kab/kota × jenis usaha (API `od_17367...v2`) | https://opendata.jabarprov.go.id/id/dataset/jumlah-usaha-mikro-kecil-dan-menengah-umkm-binaan-berdasarkan-jenis-usaha-di-jawa-barat — diakses 30 Okt 2026 | 2023 | kab/kota | jenis_usaha, jumlah_umkm | Kepadatan Sektor Target |
| S3 | Open Data Jabar — Bapenda, e-Samsat per cabang × bank (API `od_15834...v6`) | https://opendata.jabarprov.go.id/id/dataset/jumlah-pembayaran-pajak-kendaraan-bermotor-melalui-e-samsat-berdasarkan-bank-penerima-dan-cabang-pelayanan-di-jawa-barat — diakses 30 Okt 2026 | 2024 | kab/kota (agregat) | jumlah_pembayaran (Rp) | Adopsi Pembayaran Digital (proksi) |
| S4a | BPS, Jabar Dalam Angka 2025, Tabel 13.2.5 hlm. 799 | https://jabar.bps.go.id/id/publication/2025/02/28/d906b36c4b300ab77908dfe2/provinsi-jawa-barat-dalam-angka-2025.html — diakses 30 Okt 2026 | 2024** | kab/kota | PDRB per kapita ADHB (ribu Rp) | Aktivitas Ekonomi |
| S4b | BPS, Kesra Jabar 2025 (Susenas Mar 2025), Tabel 7.4 hlm. 118 | https://jabar.bps.go.id/id/publication/2025/11/28/5c47dbf83e4123e9a4707950/statistik-kesejahteraan-rakyat-provinsi-jawa-barat-2025.html — diakses 30 Okt 2026 | 2025 | kab/kota | % penduduk 5+ pengguna internet | Kesiapan Digital |
Rincian + sumber yang gagal diakses tercatat di `SOURCES.md`. QRIS per kab/kota tidak dipublikasikan (BI hanya merilis level provinsi: Jabar 8,28 jt merchant Q1-2025), sehingga dipakai proksi e-Samsat (S3).""")

code("""umkm = pd.read_csv("data/umkm_proyeksi_2023.csv")
binaan = pd.read_csv("data/umkm_binaan_2023.csv")
esamsat = pd.read_csv("data/esamsat_2024.csv")
pdrb = pd.read_csv("data/pdrb_2024.csv")
inet = pd.read_csv("data/internet_2025.csv")
for d, n in [(umkm, "umkm"), (binaan, "binaan"), (esamsat, "esamsat"),
             (pdrb, "pdrb"), (inet, "internet")]:
    print(f"{n}: shape={d.shape}")
print(umkm.dtypes.to_string())
print("--- head umkm ---"); print(umkm.head(3).to_string())
print("--- head binaan ---"); print(binaan.head(3).to_string())
assert {len(umkm), len(pdrb), len(inet), len(esamsat)} == {27}
assert len(binaan) == 27 * 15
""")

md("""## Bagian 2 — Data Preparation & Kriteria Penggugur
### 2.1 Cleaning""")
code("""for d, n in [(umkm, "umkm"), (binaan, "binaan"), (esamsat, "esamsat"),
             (pdrb, "pdrb"), (inet, "internet")]:
    assert d.isna().sum().sum() == 0, f"missing di {n}"
print("missing: 0 di semua tabel")
for d, n in [(umkm, "umkm"), (esamsat, "esamsat"), (pdrb, "pdrb"),
             (inet, "internet")]:
    assert d.duplicated(subset="kode_kabupaten_kota").sum() == 0, n
assert binaan.duplicated().sum() == 0
print("duplikat: 0")
codes = [set(d["kode_kabupaten_kota"]) for d in (umkm, pdrb, inet, esamsat)]
codes.append(set(binaan["kode_kabupaten_kota"].unique()))
assert len(set.intersection(*codes)) == 27, "kode tidak selaras"
print("27 kode BPS selaras di semua tabel")
q1, q3 = umkm["total_umkm_2023"].quantile([0.25, 0.75])
iqr = q3 - q1
out = umkm[umkm["total_umkm_2023"] > q3 + 1.5 * iqr]
print("outlier IQR total_umkm:", out["nama_kabupaten_kota"].tolist() or "tidak ada")
""")

md("""### 2.2 Pemetaan kategori ke 3 kelompok ICP
| Kelompok ICP | Kategori ODJ | Alasan |
|---|---|---|
| Ritel (G) | FASHION, KONVEKSI | produk diperdagangkan eceran, transaksi harian |
| F&B (I) | KULINER, MAKANAN, MINUMAN | makanan/minuman siap saji & kemasan |
| Jasa rutin (S) | JASA | jasa kecil berulang (laundry/salon/bengkel sejenis) |
| Di luar ICP | AGRIBISNIS, AKSESORIS, BATIK, BORDIR, CRAFT, DEKORASI, INDUSTRI, MEBEL, OBAT-OBATAN | produksi/batch/musiman, bukan transaksi harian rutin |
Kategori proyeksi S1 komposisinya identik antar wilayah (std < 1e-5) sehingga komposisi dihitung dari S2 (binaan, komposisi riil bervariasi).
Catatan penting: pada binaan 2023, jenis KULINER/MAKANAN/MINUMAN tercatat nol (program binaan didominasi
FASHION) — ini bias program, bukan cerminan populasi (di populasi, F&B besar). Dicatat sebagai keterbatasan.""")

code("""RITEL = ["FASHION", "KONVEKSI"]
FNB = ["KULINER", "MAKANAN", "MINUMAN"]
JASA = ["JASA"]
ICP_JENIS = RITEL + FNB + JASA
share = (binaan.assign(icp=binaan["jenis_usaha"].isin(ICP_JENIS))
         .groupby(["kode_kabupaten_kota", "nama_kabupaten_kota"])
         .apply(lambda g: g.loc[g["icp"], "jumlah_umkm"].sum() / g["jumlah_umkm"].sum(),
                include_groups=False)
         .reset_index(name="kepadatan_icp"))
print(share["kepadatan_icp"].describe().to_string())
assert share["kepadatan_icp"].between(0, 1).all()
""")

md("""### 2.3 Merging (left join dengan kunci kode BPS)""")
code("""df = (umkm.merge(share, on=["kode_kabupaten_kota", "nama_kabupaten_kota"])
            .merge(pdrb, on=["kode_kabupaten_kota", "nama_kabupaten_kota"])
            .merge(inet, on=["kode_kabupaten_kota", "nama_kabupaten_kota"])
            .merge(esamsat, on=["kode_kabupaten_kota", "nama_kabupaten_kota"]))
df["esamsat_per_umkm"] = df["esamsat_nominal_2024_rp"] / df["total_umkm_2023"]
assert len(df) == 27 and df["kode_kabupaten_kota"].nunique() == 27
assert df.isna().sum().sum() == 0
print("merge OK:", df.shape)
df.to_csv("data_clean_27_unscaled.csv", index=False)
""")

md("""### 2.4 Disqualification filter
Aturan: urutkan total_umkm_2023 menurun, pertahankan wilayah yang secara kumulatif mencakup >=95% total UMKM Jabar;
sisanya tereliminasi (kontribusi marjinal, pipeline SDR tidak ekonomis). Kriteria (b) data kunci kosong dan
(c) sektor non-rutin ditangani: (b) tidak ada missing; (c) via indikator kepadatan, bukan eliminasi baris.""")
code("""df = df.sort_values("total_umkm_2023", ascending=False).reset_index(drop=True)
df["cum_share"] = df["total_umkm_2023"].cumsum() / df["total_umkm_2023"].sum()
cut = (df["cum_share"] >= 0.95).idxmax()
keep = df.loc[:cut].copy()
elim = df.loc[cut + 1:].copy()
elim["alasan"] = ("di luar 95% kumulatif total UMKM Jabar "
                  "(kontribusi marjinal, pasar sangat kecil)")
print(f"final: {len(keep)} wilayah, tereliminasi: {len(elim)}")
print(elim[["nama_kabupaten_kota", "total_umkm_2023", "alasan"]].to_string(index=False))
elim_out = elim[["kode_kabupaten_kota", "nama_kabupaten_kota",
                 "total_umkm_2023", "alasan"]]
elim_out.to_csv("data_eliminated.csv", index=False)
assert len(keep) >= 20, "unit final < 20"
final = keep.drop(columns="cum_share").reset_index(drop=True)
final.to_csv("data_clean_merged.csv", index=False)
""")

md("""### 2.5 Normalisasi MinMax (arah: semua makin tinggi makin baik)""")
code("""INDIKATOR = ["total_umkm_2023", "kepadatan_icp", "internet_pct_2025",
             "esamsat_per_umkm", "pdrb_per_kapita_2024_ribu_rp"]
scaler = MinMaxScaler()
scaled = pd.DataFrame(scaler.fit_transform(final[INDIKATOR]),
                      columns=[c + "_scaled" for c in INDIKATOR])
assert ((scaled >= 0) & (scaled <= 1)).all().all()
out = pd.concat([final[["kode_kabupaten_kota", "nama_kabupaten_kota"]],
                 scaled], axis=1)
out.to_csv("data_scaled.csv", index=False)
print(out.describe().to_string())
""")

md("""## Bagian 3 — EDA & Visualisasi""")

code("""fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(final["total_umkm_2023"] / 1000, bins=12, color="teal", edgecolor="white")
ax[0].set_xlabel("Total UMKM 2023 (ribu unit)")
ax[0].set_ylabel("Jumlah wilayah")
ax[0].set_title("Distribusi ukuran pasar per wilayah")
ax[1].boxplot(final["total_umkm_2023"] / 1000, vert=False)
ax[1].set_xlabel("Total UMKM 2023 (ribu unit)")
ax[1].set_title("Boxplot ukuran pasar")
plt.tight_layout(); plt.savefig("assets/g1_distribusi_umkm.png"); plt.show()
print("median:", int(final['total_umkm_2023'].median()),
      "| min:", final.sort_values('total_umkm_2023').iloc[0]['nama_kabupaten_kota'],
      "| max:", final.sort_values('total_umkm_2023').iloc[-1]['nama_kabupaten_kota'])
""")
md("""Insight G1 — Distribusi right-skew: tiga raksasa (Kab. Bogor 571 rb, Kab. Bandung 538 rb, Kota Bandung 524 rb)
jauh di atas median (±150 rb). Bagi SDR ini berarti pipeline terkonsentrasi: sebagian kecil wilayah menyimpan
sebagian besar prospek, sehingga penjadwalan kunjungan/akuisisi sebaiknya dibobot ke wilayah besar lebih dulu.""")

code("""s = final.set_index("nama_kabupaten_kota")["kepadatan_icp"].sort_values() * 100
fig, ax = plt.subplots(figsize=(8, 7))
s.plot.barh(ax=ax, color=sns.color_palette(PALET, len(s)))
ax.set_xlabel("Share UMKM binaan pada sektor ICP Ritel/F&B/Jasa (%)")
ax.set_title("Kepadatan sektor target ICP per wilayah")
plt.tight_layout(); plt.savefig("assets/g2_kepadatan_icp.png"); plt.show()
""")
md("""Insight G2 — Kepadatan ICP bervariasi nyata (57,5% Kab. Bandung Barat s.d. 91,3% Kab. Kuningan).
Kuningan, Kota Tasikmalaya, dan Ciamis paling "murni" ritel/jasa harian, sementara Bandung Barat paling
banyak porsi kerajinan/industri (mebel/industri). Catatan: F&B tidak muncul di data binaan (bias program),
jadi angka ini mengukur porsi ritel+jasa harian. SDR memakai daftar ini untuk wilayah dengan probabilitas
product-fit tertinggi per kunjungan.""")

code("""fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(final["internet_pct_2025"], final["total_umkm_2023"] / 1000,
           s=70, alpha=0.8, c=final["pdrb_per_kapita_2024_ribu_rp"], cmap=PALET)
z = np.polyfit(final["internet_pct_2025"], final["total_umkm_2023"] / 1000, 1)
xs = np.linspace(final["internet_pct_2025"].min(), final["internet_pct_2025"].max(), 50)
ax.plot(xs, np.polyval(z, xs), "r--", lw=1.5)
ax.set_xlabel("Penduduk 5+ pengguna internet 2025 (%)")
ax.set_ylabel("Total UMKM 2023 (ribu unit)")
ax.set_title("Internet vs ukuran pasar (warna = PDRB/kapita)")
plt.colorbar(ax.collections[0], ax=ax, label="PDRB/kapita (ribu Rp)")
plt.tight_layout(); plt.savefig("assets/g3_internet_vs_pasar.png"); plt.show()
r = final["internet_pct_2025"].corr(final["total_umkm_2023"])
print(f"korelasi Pearson: {r:.2f}")
""")
md("""Insight G3 — Korelasi internet vs jumlah UMKM ≈ -0,07 (praktis nol): wilayah digital (kota, 85–93%)
cenderung ber-UMKM sedikit, kabupaten besar ber-UMKM banyak tetapi internet 67–81%. Artinya kesiapan digital
tidak boleh dipakai sebagai proksi ukuran pasar — keduanya mengukur hal berbeda dan layak jadi komponen
bobot terpisah. Kota-kota adalah kantong kesiapan digital di tengah pasar kabupaten yang besar.""")

code("""fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(final["pdrb_per_kapita_2024_ribu_rp"], final["esamsat_per_umkm"] / 1e6,
           s=70, alpha=0.8, c=final["internet_pct_2025"], cmap=PALET)
z = np.polyfit(final["pdrb_per_kapita_2024_ribu_rp"],
               final["esamsat_per_umkm"] / 1e6, 1)
xs = np.linspace(final["pdrb_per_kapita_2024_ribu_rp"].min(),
                 final["pdrb_per_kapita_2024_ribu_rp"].max(), 50)
ax.plot(xs, np.polyval(z, xs), "r--", lw=1.5)
ax.set_xlabel("PDRB per kapita 2024 (ribu Rp)")
ax.set_ylabel("Nominal e-Samsat per UMKM 2024 (juta Rp)")
ax.set_title("Daya beli vs adopsi pembayaran digital (warna = internet %)")
plt.colorbar(ax.collections[0], ax=ax, label="Internet (%)")
plt.tight_layout(); plt.savefig("assets/g4_pdrb_vs_adopsi.png"); plt.show()
r = final["pdrb_per_kapita_2024_ribu_rp"].corr(final["esamsat_per_umkm"])
print(f"korelasi Pearson: {r:.2f}")
""")
md("""Insight G4 — Korelasi +0,42 (moderat): wilayah kaya (Kota Bandung, Karawang, Bekasi) membayar pajak
kendaraan secara digital jauh lebih besar per UMKM-nya (Depok tertinggi). Ini validasi proksi e-Samsat:
kebiasaan transaksi digital bergerak searah dengan daya beli. Bagi SDR, kuadran kanan-atas (kaya + digital)
adalah wilayah dengan friksi adopsi QRIS/analitik Klay terendah.""")

code("""top12 = final.nlargest(12, "total_umkm_2023")
mat = (binaan[binaan["nama_kabupaten_kota"].isin(top12["nama_kabupaten_kota"])]
       .assign(grup=lambda d: np.select(
           [d["jenis_usaha"].isin(RITEL), d["jenis_usaha"].isin(FNB),
            d["jenis_usaha"].isin(JASA)], ["Ritel", "F&B", "Jasa"], "Di luar ICP"))
       .groupby(["nama_kabupaten_kota", "grup"])["jumlah_umkm"].sum()
       .unstack(fill_value=0))
mat = mat.div(mat.sum(axis=1), axis=0).reindex(
    top12.sort_values("total_umkm_2023", ascending=False)["nama_kabupaten_kota"])
fig, ax = plt.subplots(figsize=(9, 6))
sns.heatmap(mat * 100, annot=True, fmt=".0f", cmap=PALET, ax=ax, cbar_kws={"label": "%"})
ax.set_title("Komposisi sektor: 12 wilayah terbesar")
ax.set_ylabel(""); ax.set_xlabel("")
plt.tight_layout(); plt.savefig("assets/g5_heatmap_sektor.png"); plt.show()
""")
md("""Insight G5 — Ritel (terutama FASHION) mendominasi UMKM binaan di semua 12 wilayah terbesar (59–79%),
tertinggi di Kab. Bandung 79%. Kolom F&B nol di seluruh wilayah: program binaan Diskuk 2023 tidak menyentuh
kuliner — padahal di populasi F&B besar (SE2016 Jabar: kategori I ±19%). Ini bias program yang wajib
diingat SDR: daftar binaan bukan daftar prospek. Implikasi pitch: angle ritel (stok, varian, kasir multi-outlet)
terbukti relevan; untuk F&B gunakan data populasi/S1 sebagai dasar prospek, bukan data binaan.""")

code("""num = final[INDIKATOR].rename(columns={
    "total_umkm_2023": "pasar", "kepadatan_icp": "sektor_icp",
    "internet_pct_2025": "internet", "esamsat_per_umkm": "adopsi_digital",
    "pdrb_per_kapita_2024_ribu_rp": "pdrb_kapita"})
fig, ax = plt.subplots(figsize=(6.5, 5.5))
sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap=PALET, vmin=-1, vmax=1, ax=ax)
ax.set_title("Korelasi antar indikator ICP")
plt.tight_layout(); plt.savefig("assets/g6_corr_matrix.png"); plt.show()
""")
md("""Insight G6 — Tidak ada korelasi > 0,6 antar indikator: kelima indikator membawa sinyal berbeda
(pasar vs daya beli vs digital vs komposisi sektor). Ini kabar baik untuk pembobotan: tidak ada duplikasi
berlebih, sehingga bobot 30/25/20/15/10 benar-benar mewakili lima dimensi keputusan yang independen bagi SDR.""")

md("""## Bagian 4 — Rancangan Bobot Indeks Prioritas
| Komponen | Indikator publik dipakai | Arah | Bobot | Justifikasi bisnis (kaitan ICP Klay) |
|---|---|---|---|---|
| Ukuran Pasar | Total UMKM 2023 per kab/kota (S1) | + | 30% | Pipeline SDR: makin banyak UMKM makin banyak prospek yang bisa dihubungi. |
| Kepadatan Sektor Target | Share UMKM binaan pada Ritel/F&B/Jasa (S2; pada 2023 terisi ritel+jasa) | + | 25% | Product-fit: porsi usaha dagang eceran dan jasa rutin harian paling butuh POS + analitik. |
| Kesiapan Digital | % penduduk 5+ pengguna internet 2025 (S4b) | + | 20% | Prasyarat POS cloud & dashboard AI; wilayah offline tinggi butuh edukasi panjang. |
| Adopsi Pembayaran Digital | Nominal e-Samsat per UMKM 2024 (S3, proksi) | + | 15% | Bukti perilaku bayar digital; korelasi +0,42 dengan daya beli. QRIS per kab/kota tidak dipublikasikan (BI hanya level provinsi). |
| Aktivitas Ekonomi | PDRB per kapita 2024 (S4a) | + | 10% | Daya beli menopang kemampuan bayar langganan SaaS; bobot terkecil karena Klay menyasar volume UMKM, bukan segmen premium. |
| Total | | | 100% | |""")

code("""BOBOT = {"pasar": 30, "sektor": 25, "digital": 20, "adopsi": 15, "ekonomi": 10}
assert sum(BOBOT.values()) == 100, "total bobot harus 100"
print("Total bobot:", sum(BOBOT.values()), "% — OK")
""")

md("""## Penutup
Temuan awal: (1) pasar terkonsentrasi di 3 wilayah >500 rb UMKM; (2) kepadatan ICP tertinggi di
Kuningan/Tasikmalaya/Ciamis; (3) kota = kantong digital dan adopsi, kabupaten = kantong volume;
(4) 5 wilayah kecil tereliminasi (4,8% pasar) sehingga fokus pada 22 wilayah.
Keterbatasan utama: proyeksi S1 (bukan sensus); S2 hanya UMKM binaan (n 100-175/wilayah);
proksi e-Samsat bukan QRIS; PDRB 2024 sangat sementara; Susenas memakai sampel.
Langkah berikut (Milestone 2, tidak dikerjakan di sini): K-Means dan Elbow/Silhouette,
skor indeks final, Top 5 segmen, sensitivity check, rekomendasi scraping.""")

nbf.write(nb, "Milestone1_ICP_Klay_Jabar.ipynb")
print("notebook selesai")
