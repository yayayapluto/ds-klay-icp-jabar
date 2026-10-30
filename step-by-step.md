# Guidebook Manual: Milestone 1 dan 2 (Klay / Skalar Solutions)

Panduan langkah-demi-langkah mengerjakan ulang seluruh pipeline secara manual di notebook baru.
Setiap langkah berisi **tujuan**, **instruksi**, dan **cek hasil**. Kode disembunyikan di dalam
accordion. Klik untuk membuka, salin ke satu sel notebook, jalankan, lalu cocokkan dengan hasil yang diharapkan.

Struktur folder yang dipakai:

```text
├── notebooks/   <- notebook manual dibuat di sini
├── data/        <- 5 CSV sumber + 2 PDF BPS
├── output/      <- CSV hasil (dibuat otomatis)
└── assets/      <- PNG grafik (dibuat otomatis)
```

> Jalankan semua sel berurutan dari atas. Kernel boleh dimulai dengan working directory
> repo root ATAU folder `notebooks/`, karena blok Setup di Langkah 0 mendeteksi keduanya otomatis.

---

## Langkah 0: Setup dan path adaptif

**Tujuan:** impor pustaka dan buat helper path `P()` agar notebook jalan dari mana saja.

**Instruksi:**

1. Buat notebook baru, simpan sebagai `notebooks/manual.ipynb`.
2. Sel pertama: salin kode accordion, jalankan. Pastikan tidak error dan folder `output/` + `assets/` terbentuk.

<details>
<summary><b>Kode: Setup</b></summary>

```python
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

BASE = ".." if os.path.exists(os.path.join("..", "data")) else "."
def P(*parts):
    return os.path.join(BASE, *parts)

for d in ("data", "assets", "output"):
    os.makedirs(P(d), exist_ok=True)

NEED = {"esamsat_2024.csv", "internet_2025.csv", "pdrb_2024.csv",
        "umkm_binaan_2023.csv", "umkm_proyeksi_2023.csv"}
assert NEED.issubset(set(os.listdir(P("data")))), "Lengkapi 5 CSV di folder data/ dulu."
```

</details>

**Cek:** tidak ada `AssertionError`. Jika muncul, letakkan 5 CSV sumber ke `data/`.

---

## MILESTONE 1

### Langkah 1: Unduh data Open Data Jabar (3 dataset, via API)

**Tujuan:** ambil UMKM proyeksi, UMKM binaan, dan e-Samsat langsung dari API resmi. Portal web-nya
kadang 502/WAF, sedangkan API-nya terbuka.

**Instruksi:**

1. Dataset 1 (Diskuk, proyeksi per kab/kota x kategori 2017 sampai 2023): endpoint
   `od_17371_proyeksi_jml_ush_mikro_kecil_menengah_umkm__kabupa_v2`, paginasi `limit=1000`
   (`skip=0` lalu `skip=1000`) sampai total 1.890 baris.
2. Dataset 2 (Diskuk, binaan per kab/kota x jenis usaha 2019 sampai 2023): endpoint
   `od_17367_jml_ush_mikro_kecil_menengah_umkm_binaan__jenis_us_v2`, paginasi sampai 2.025 baris.
3. Dataset 3 (Bapenda, e-Samsat 2014 sampai 2025): endpoint
   `od_15834_jml_pembayaran_pajak_kndrn_brmtr_melalui_e_samsat__v6`, paginasi sampai 2.005 baris.
4. Simpan respons JSON, filter tahun yang dipakai (2023 / 2023 / 2024), tulis ke `data/*.csv`.

<details>
<summary><b>Kode: Unduh + tulis CSV ODJ</b></summary>

```python
import json, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
def fetch_all(base, total):
    recs, skip = [], 0
    while len(recs) < total:
        url = f"{base}?limit=1000&skip={skip}"
        req = urllib.request.Request(url, headers=UA)
        d = json.load(urllib.request.urlopen(req, timeout=90))
        recs += d["data"]; skip += 1000
    return recs[:total]

HOST = "https://data.jabarprov.go.id/api-backend/bigdata"
u = fetch_all(f"{HOST}/diskuk/od_17371_proyeksi_jml_ush_mikro_kecil_menengah_umkm__kabupa_v2", 1890)
b = fetch_all(f"{HOST}/diskuk/od_17367_jml_ush_mikro_kecil_menengah_umkm_binaan__jenis_us_v2", 2025)
e = fetch_all(f"{HOST}/bapenda/od_15834_jml_pembayaran_pajak_kndrn_brmtr_melalui_e_samsat__v6", 2005)

du = pd.DataFrame(u)
du[du.tahun == 2023].groupby(["kode_kabupaten_kota", "nama_kabupaten_kota"]
    )["proyeksi_jumlah_umkm"].sum().reset_index().rename(
    columns={"proyeksi_jumlah_umkm": "total_umkm_2023"}
    ).to_csv(P("data", "umkm_proyeksi_2023.csv"), index=False)

db = pd.DataFrame(b)
db[db.tahun == 2023].to_csv(P("data", "umkm_binaan_2023.csv"), index=False)

de = pd.DataFrame(e)
de[de.tahun == 2024].groupby(["kode_kabupaten_kota", "nama_kabupaten_kota"]
    )["jumlah_pembayaran"].sum().reset_index().rename(
    columns={"jumlah_pembayaran": "esamsat_nominal_2024_rp"}
    ).to_csv(P("data", "esamsat_2024.csv"), index=False)
print("OK:", len(du), len(db), len(de))
```

</details>

**Cek:** `umkm_proyeksi_2023.csv` 27 baris, `umkm_binaan_2023.csv` 405 baris, `esamsat_2024.csv` 27 baris.

### Langkah 2: Unduh 2 PDF BPS + ekstrak tabelnya

**Tujuan:** PDRB per kapita 2024 (Dalam Angka 2025, Tabel 13.2.5 hlm. 799) dan internet 2025
(Kesra 2025, Tabel 7.4 hlm. 118).

**Instruksi:**

1. Unduh dari halaman publikasi BPS (tombol *Unduh Publikasi*; token bertanda waktu,
   ambil baru tiap sesi).
2. Ekstrak dengan `pdfplumber` + tangani artefak OCR (huruf menempel angka, mis. `Bogort`,
   `25o.138`, `9/1.873`) via alias dan pembersih regex.
3. Wajib: `assert` 27 baris + spot-check (Kota Bandung sekitar 147.081; Depok internet sekitar 93,24).

<details>
<summary><b>Kode: Ekstrak PDF BPS</b></summary>

```python
import re, pdfplumber

KAB = {"Bogor": 3201, "Sukabumi": 3202, "Cianjur": 3203, "Bandung": 3204,
       "Garut": 3205, "Tasikmalaya": 3206, "Ciamis": 3207, "Kuningan": 3208,
       "Cirebon": 3209, "Majalengka": 3210, "Sumedang": 3211, "Indramayu": 3212,
       "Subang": 3213, "Purwakarta": 3214, "Karawang": 3215, "Bekasi": 3216,
       "Bandung Barat": 3217, "Pangandaran": 3218}
KOTA = {"Bogor": 3271, "Sukabumi": 3272, "Bandung": 3273, "Cirebon": 3274,
        "Bekasi": 3275, "Depok": 3276, "Cimahi": 3277, "Tasikmalaya": 3278, "Banjar": 3279}
num = lambda s: float(s.replace(".", "").replace(",", "."))

# --- PDRB (halaman PDF ke-869, indeks 868) ---
txt = pdfplumber.open(P("data", "BPS_Jabar_Dalam_Angka_2025.pdf")).pages[868].extract_text()
vals, alias = [], {"Bogort": "Bogor", "Sukabumih": "Sukabumi", "BandungBarat": "Bandung Barat"}
for ln in txt.split("\n"):
    ln = ln.replace("o.", ".").replace("/", "")
    ln = re.sub(r"[^A-Za-z0-9\.,\s]", "", ln).strip()
    ns = re.findall(r"\d{2,3}\.\d{3}", ln)
    nm = re.sub(r"\s*\d.*$", "", ln).strip().replace(" ", "")
    nm = alias.get(nm, nm)
    if len(ns) >= 5 and nm in list(KAB) + list(KOTA):
        vals.append((nm, num(ns[-1])))
assert len(vals) == 27, vals
rows = [(KAB[n] if i < 18 else KOTA[n],
         ("KABUPATEN " if i < 18 else "KOTA ") + n.upper(), v)
        for i, (n, v) in enumerate(vals)]
pd.DataFrame(rows, columns=["kode_kabupaten_kota", "nama_kabupaten_kota",
    "pdrb_per_kapita_2024_ribu_rp"]).to_csv(P("data", "pdrb_2024.csv"), index=False)

# --- Internet (halaman PDF ke-153, indeks 152) ---
txt = pdfplumber.open(P("data", "BPS_Kesra_Jabar_2025.pdf")).pages[152].extract_text()
rows = []
for ln in txt.split("\n"):
    m = re.match(r"^(?:\d+\.\s*)?(Kab\.\s*|Kota\s+)([A-Za-z ]+)", ln.strip())
    if not m:
        continue
    kind, nm = m.group(1).strip(), m.group(2).strip()
    hit = [k for k in list(KAB) + list(KOTA) if nm.startswith(k)]
    ns = re.findall(r"\d+,\d+", ln)
    if len(ns) < 3 or not hit:
        continue
    nm = max(hit, key=len)
    rows.append(((KAB if kind.startswith("Kab") else KOTA)[nm],
                 ("KABUPATEN " if kind.startswith("Kab") else "KOTA ") + nm.upper(),
                 num(ns[-1])))
inet = pd.DataFrame(rows, columns=["kode_kabupaten_kota", "nama_kabupaten_kota",
    "internet_pct_2025"]).drop_duplicates()
assert len(inet) == 27, len(inet)
inet.to_csv(P("data", "internet_2025.csv"), index=False)
print("PDF OK")
```

</details>

**Cek:** `pdrb_2024.csv` dan `internet_2025.csv` masing-masing 27 baris, tanpa missing.

### Langkah 3: Load + cleaning + validasi kunci

**Tujuan:** 0 missing, 0 duplikat, 27 kode BPS selaras di semua tabel.

**Instruksi:** muat 5 CSV lalu periksa shape, dtypes, dan head. Setelah itu cek missing,
duplikat, dan iris outlier IQR (catatan: tidak ada yang perlu dibuang, sebab skew adalah sifat data, bukan kesalahan).

<details>
<summary><b>Kode: Load dan cleaning</b></summary>

```python
umkm = pd.read_csv(P("data", "umkm_proyeksi_2023.csv"))
binaan = pd.read_csv(P("data", "umkm_binaan_2023.csv"))
esamsat = pd.read_csv(P("data", "esamsat_2024.csv"))
pdrb = pd.read_csv(P("data", "pdrb_2024.csv"))
inet = pd.read_csv(P("data", "internet_2025.csv"))

for d, n in [(umkm, "umkm"), (binaan, "binaan"), (esamsat, "esamsat"),
             (pdrb, "pdrb"), (inet, "internet")]:
    assert d.isna().sum().sum() == 0, f"missing di {n}"
assert binaan.duplicated().sum() == 0
codes = [set(d["kode_kabupaten_kota"]) for d in (umkm, pdrb, inet, esamsat)]
codes.append(set(binaan["kode_kabupaten_kota"].unique()))
assert len(set.intersection(*codes)) == 27

q1, q3 = umkm["total_umkm_2023"].quantile([0.25, 0.75])
print("outlier IQR:", umkm[umkm.total_umkm_2023 > q3 + 1.5 * (q3 - q1)]
      ["nama_kabupaten_kota"].tolist() or "tidak ada")
```

</details>

### Langkah 4: Pemetaan kategori ke 3 kelompok ICP

**Target langkah ini:** hitung share sektor target per wilayah dari data binaan. Komposisi proyeksi S1
seragam antar wilayah (std di bawah 1e-5), jadi tidak informatif.

**Aturan mapping:** Ritel = FASHION, KONVEKSI · F&B = KULINER, MAKANAN, MINUMAN ·
Jasa = JASA · sisanya (MEBEL, INDUSTRI, AGRIBISNIS, AKSESORIS, BATIK, BORDIR, CRAFT,
DEKORASI, OBAT-OBATAN) = Di luar ICP. Catat: pada binaan 2023 F&B = 0 (bias program).

<details>
<summary><b>Kode: Kepadatan ICP</b></summary>

```python
RITEL, FNB, JASA = ["FASHION", "KONVEKSI"], ["KULINER", "MAKANAN", "MINUMAN"], ["JASA"]
share = (binaan.assign(icp=binaan["jenis_usaha"].isin(RITEL + FNB + JASA))
         .groupby(["kode_kabupaten_kota", "nama_kabupaten_kota"])
         .apply(lambda g: g.loc[g["icp"], "jumlah_umkm"].sum() / g["jumlah_umkm"].sum(),
                include_groups=False)
         .reset_index(name="kepadatan_icp"))
assert share["kepadatan_icp"].between(0, 1).all()
print(share["kepadatan_icp"].describe().to_string())
```

</details>

**Cek:** rentang sekitar 0,575 sampai 0,913. Jika std mendekati nol, indikator tak layak skor (lihat jebakan di Langkah 8).

### Langkah 5: Merging

**Yang ingin dicapai:** satu tabel 27 baris, tanpa baris hilang/duplikat/missing.

**Instruksi:** gabungkan dengan left join berurutan memakai kunci `kode_kabupaten_kota`.
e-Samsat sudah diagregat di Langkah 1, lalu buat `esamsat_per_umkm = nominal / total_umkm`.

<details>
<summary><b>Kode: Merge</b></summary>

```python
df = (umkm.merge(share, on=["kode_kabupaten_kota", "nama_kabupaten_kota"])
            .merge(pdrb, on=["kode_kabupaten_kota", "nama_kabupaten_kota"])
            .merge(inet, on=["kode_kabupaten_kota", "nama_kabupaten_kota"])
            .merge(esamsat, on=["kode_kabupaten_kota", "nama_kabupaten_kota"]))
df["esamsat_per_umkm"] = df["esamsat_nominal_2024_rp"] / df["total_umkm_2023"]
assert len(df) == 27 and df["kode_kabupaten_kota"].nunique() == 27
assert df.isna().sum().sum() == 0
df.to_csv(P("output", "data_clean_27_unscaled.csv"), index=False)
```

</details>

### Langkah 6: Filter penggugur (eliminasi)

**Tujuan:** sisakan wilayah yang secara kumulatif mencakup minimal 95% total UMKM. Sisanya
catat di `data_eliminated.csv` beserta alasannya. Syaratnya: tersisa minimal 20 wilayah dan tanpa imputasi tebakan.

<details>
<summary><b>Kode: Eliminasi</b></summary>

```python
df = df.sort_values("total_umkm_2023", ascending=False).reset_index(drop=True)
df["cum_share"] = df["total_umkm_2023"].cumsum() / df["total_umkm_2023"].sum()
cut = (df["cum_share"] >= 0.95).idxmax()
final = df.loc[:cut].copy()
elim = df.loc[cut + 1:].copy()
elim["alasan"] = ("di luar 95% kumulatif total UMKM Jabar "
                  "(kontribusi marjinal, pasar sangat kecil)")
elim[["kode_kabupaten_kota", "nama_kabupaten_kota", "total_umkm_2023", "alasan"]].to_csv(
    P("output", "data_eliminated.csv"), index=False)
assert len(final) >= 20
final = final.drop(columns="cum_share").reset_index(drop=True)
final.to_csv(P("output", "data_clean_merged.csv"), index=False)
print(f"final {len(final)} | tereliminasi {len(elim)}")
```

</details>

**Cek:** final 22, tereliminasi 5 (Banjar, Sukabumi kota, Cirebon kota, Cimahi, Pangandaran, yang
bersama-sama hanya 4,8% total).

### Langkah 7: Normalisasi MinMax

**Tujuan:** 5 indikator ke rentang 0 sampai 1, semua arah positif. Hanya `MinMaxScaler` dari sklearn.

<details>
<summary><b>Kode: Scaling</b></summary>

```python
INDIKATOR = ["total_umkm_2023", "kepadatan_icp", "internet_pct_2025",
             "esamsat_per_umkm", "pdrb_per_kapita_2024_ribu_rp"]
scaled = pd.DataFrame(MinMaxScaler().fit_transform(final[INDIKATOR]),
                       columns=[c + "_scaled" for c in INDIKATOR])
assert ((scaled >= 0) & (scaled <= 1)).all().all()
pd.concat([final[["kode_kabupaten_kota", "nama_kabupaten_kota"]], scaled],
          axis=1).to_csv(P("output", "data_scaled.csv"), index=False)
```

</details>

### Langkah 8: EDA (6 grafik + insight SDR)

**Tujuan:** buat minimal 5 grafik (univariat, bivariat, multivariat). Tiap grafik diikuti 2-4 kalimat
insight bisnis. Pola acuan yang harus muncul: distribusi right-skew; kepadatan 57,5 sampai 91,3 persen;
korelasi internet-pasar sekitar -0,07; korelasi adopsi-PDRB sekitar +0,42; ritel fashion dominan di heatmap;
tidak ada korelasi antar-indikator di atas 0,6.

**Jebakan umum:** (a) indikator konstan (std mendekati nol) membuat MinMax gagal, jadi cek `describe()` dulu;
(b) heatmap F&B nol adalah fakta data (bias program), bukan bug kode.

<details>
<summary><b>Kode: 6 grafik</b></summary>

```python
# G1 univariat: histogram + boxplot total UMKM
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].hist(final["total_umkm_2023"] / 1000, bins=12, color="teal", edgecolor="white")
ax[0].set_xlabel("Total UMKM 2023 (ribu unit)"); ax[0].set_title("Distribusi ukuran pasar")
ax[1].boxplot(final["total_umkm_2023"] / 1000, vert=False)
ax[1].set_xlabel("Total UMKM 2023 (ribu unit)"); ax[1].set_title("Boxplot ukuran pasar")
plt.tight_layout(); plt.savefig(P("assets", "g1_distribusi_umkm.png")); plt.show()

# G2 univariat: bar horizontal kepadatan ICP
s = final.set_index("nama_kabupaten_kota")["kepadatan_icp"].sort_values() * 100
fig, ax = plt.subplots(figsize=(8, 7))
s.plot.barh(ax=ax, color=sns.color_palette("viridis", len(s)))
ax.set_xlabel("Share sektor ICP (%)"); ax.set_title("Kepadatan sektor target ICP")
plt.tight_layout(); plt.savefig(P("assets", "g2_kepadatan_icp.png")); plt.show()

# G3 bivariat: internet vs pasar (+trend, warna=PDRB)
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(final["internet_pct_2025"], final["total_umkm_2023"] / 1000, s=70, alpha=0.8,
           c=final["pdrb_per_kapita_2024_ribu_rp"], cmap="viridis")
z = np.polyfit(final["internet_pct_2025"], final["total_umkm_2023"] / 1000, 1)
xs = np.linspace(final["internet_pct_2025"].min(), final["internet_pct_2025"].max(), 50)
ax.plot(xs, np.polyval(z, xs), "r--", lw=1.5)
ax.set_xlabel("Internet 2025 (%)"); ax.set_ylabel("Total UMKM 2023 (ribu)")
ax.set_title("Internet vs ukuran pasar (warna = PDRB/kapita)")
plt.colorbar(ax.collections[0], ax=ax, label="PDRB/kapita (ribu Rp)")
plt.tight_layout(); plt.savefig(P("assets", "g3_internet_vs_pasar.png")); plt.show()
print("korelasi:", round(final["internet_pct_2025"].corr(final["total_umkm_2023"]), 2))

# G4 bivariat: PDRB vs adopsi (+trend, warna=internet)
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(final["pdrb_per_kapita_2024_ribu_rp"], final["esamsat_per_umkm"] / 1e6,
           s=70, alpha=0.8, c=final["internet_pct_2025"], cmap="viridis")
z = np.polyfit(final["pdrb_per_kapita_2024_ribu_rp"], final["esamsat_per_umkm"] / 1e6, 1)
xs = np.linspace(final["pdrb_per_kapita_2024_ribu_rp"].min(),
                 final["pdrb_per_kapita_2024_ribu_rp"].max(), 50)
ax.plot(xs, np.polyval(z, xs), "r--", lw=1.5)
ax.set_xlabel("PDRB/kapita 2024 (ribu Rp)"); ax.set_ylabel("e-Samsat/UMKM (juta Rp)")
ax.set_title("Daya beli vs adopsi digital (warna = internet %)")
plt.colorbar(ax.collections[0], ax=ax, label="Internet (%)")
plt.tight_layout(); plt.savefig(P("assets", "g4_pdrb_vs_adopsi.png")); plt.show()
print("korelasi:", round(final["pdrb_per_kapita_2024_ribu_rp"].corr(final["esamsat_per_umkm"]), 2))

# G5 multivariat: heatmap komposisi 12 wilayah terbesar
top12 = final.nlargest(12, "total_umkm_2023")
mat = (binaan[binaan["nama_kabupaten_kota"].isin(top12["nama_kabupaten_kota"])]
       .assign(grup=lambda d: np.select(
           [d["jenis_usaha"].isin(RITEL), d["jenis_usaha"].isin(FNB),
            d["jenis_usaha"].isin(JASA)], ["Ritel", "F&B", "Jasa"], "Luar"))
       .groupby(["nama_kabupaten_kota", "grup"])["jumlah_umkm"].sum().unstack(fill_value=0))
mat = mat.div(mat.sum(axis=1), axis=0)
fig, ax = plt.subplots(figsize=(9, 6))
sns.heatmap(mat * 100, annot=True, fmt=".0f", cmap="viridis", ax=ax,
            cbar_kws={"label": "%"})
ax.set_title("Komposisi sektor: 12 wilayah terbesar"); ax.set_ylabel(""); ax.set_xlabel("")
plt.tight_layout(); plt.savefig(P("assets", "g5_heatmap_sektor.png")); plt.show()

# G6 multivariat: matriks korelasi
num = final[INDIKATOR].rename(columns={"total_umkm_2023": "pasar",
    "kepadatan_icp": "sektor_icp", "internet_pct_2025": "internet",
    "esamsat_per_umkm": "adopsi_digital", "pdrb_per_kapita_2024_ribu_rp": "pdrb_kapita"})
fig, ax = plt.subplots(figsize=(6.5, 5.5))
sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="viridis", vmin=-1, vmax=1, ax=ax)
ax.set_title("Korelasi antar indikator ICP")
plt.tight_layout(); plt.savefig(P("assets", "g6_corr_matrix.png")); plt.show()
```

</details>

### Langkah 9: Tabel bobot ICP (akhir Milestone 1)

**Target langkah ini:** tetapkan 5 komponen dengan total tepat 100, tiap bobot beralasan ICP. Milestone 1
berhenti di sini, jadi JANGAN lanjut ke skor/K-Means/Top 5.

| Komponen | Indikator | Bobot | Justifikasi |
|---|---|---|---|
| Ukuran Pasar | Total UMKM 2023 | 30% | Pipeline SDR |
| Kepadatan Sektor Target | Share binaan Ritel/F&B/Jasa | 25% | Product-fit transaksi harian |
| Kesiapan Digital | % pengguna internet 2025 | 20% | Prasyarat POS cloud |
| Adopsi Pembayaran Digital | e-Samsat/UMKM 2024 (proksi) | 15% | Bukti perilaku digital |
| Aktivitas Ekonomi | PDRB/kapita 2024 | 10% | Daya beli langganan |

<details>
<summary><b>Kode: Verifikasi bobot</b></summary>

```python
BOBOT = {"pasar": 30, "sektor": 25, "digital": 20, "adopsi": 15, "ekonomi": 10}
assert sum(BOBOT.values()) == 100
print("Total bobot 100%: OK")
```

</details>

---

## MILESTONE 2

Prasyarat: `output/data_scaled.csv` dan `output/data_clean_merged.csv` dari Milestone 1.

### Langkah 10: Skor prioritas

**Tujuan:** hitung skor sebagai jumlah bobot dikali fitur scaled (0-1). Acuan peringkat 1: Kota Bandung sekitar 0,738.

<details>
<summary><b>Kode: Skor</b></summary>

```python
BOBOT = {"total_umkm_2023_scaled": 0.30, "kepadatan_icp_scaled": 0.25,
         "internet_pct_2025_scaled": 0.20, "esamsat_per_umkm_scaled": 0.15,
         "pdrb_per_kapita_2024_ribu_rp_scaled": 0.10}
X = scaled[FEAT].values
hasil = merged.copy()
hasil["skor_prioritas"] = X @ np.array([BOBOT[c] for c in FEAT])
hasil = hasil.sort_values("skor_prioritas", ascending=False).reset_index(drop=True)
hasil["ranking"] = hasil.index + 1
hasil.to_csv(P("output", "data_skor.csv"), index=False)
```

</details>

### Langkah 11: K-Means (k via silhouette) + nama tipe data-driven

**Tujuan:** k diambil dari argmax silhouette pada 2 sampai 6 (hasilnya k=3, sekitar 0,393). Nama klaster WAJIB turun dari
rata-rata profil, bukan dari nomor label (nomor label K-Means arbitrer dan bisa bertukar antar run).

**Aturan nama:** rata-rata internet+adopsi tertinggi → "Digital siap adopsi"; skor rerata
terendah → "Pengembangan lanjutan"; sisanya → "Pasar volume utama".

<details>
<summary><b>Kode: K-Means</b></summary>

```python
ks, inertia, sil = list(range(2, 7)), [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    inertia.append(km.inertia_); sil.append(silhouette_score(X, km.labels_))
K = ks[int(np.argmax(sil))]
assert K == 3
km = KMeans(n_clusters=K, n_init=10, random_state=42).fit(X)
hasil["cluster"] = km.labels_
prof = hasil.groupby("cluster")[INDIKATOR + ["skor_prioritas"]].mean()
id_digital = prof[["internet_pct_2025", "esamsat_per_umkm"]].mean(axis=1).idxmax()
id_belakang = prof["skor_prioritas"].idxmin()
NAMA = {c: ("Digital siap adopsi" if c == id_digital
            else "Pengembangan lanjutan" if c == id_belakang
            else "Pasar volume utama") for c in range(K)}
hasil["tipe_wilayah"] = hasil["cluster"].map(NAMA)
hasil[["kode_kabupaten_kota", "nama_kabupaten_kota", "cluster", "tipe_wilayah"]].to_csv(
    P("output", "data_cluster.csv"), index=False)
```

</details>

### Langkah 12: Baseline vs sensitivitas

**Yang ingin dicapai:** buktikan skor mengubah ranking secara material (Spearman sekitar 0,52; overlap Top 5 = 3/5:
Depok dan Bekasi kota masuk, Garut dan Sukabumi keluar) dan robust (overlap 5/5 di semua skenario +-5pp).

**Jebakan:** JANGAN pakai `hasil.iloc[argsort]` setelah `sort_values`, sebab posisi X (urutan final)
berbeda dengan posisi hasil terurut. Selalu index ke frame berurutan-final (`merged`).

<details>
<summary><b>Kode: Baseline dan sensitivity</b></summary>

```python
hasil["rank_umkm"] = hasil["total_umkm_2023"].rank(ascending=False).astype(int)
hasil["rank_skor"] = hasil["skor_prioritas"].rank(ascending=False).astype(int)
rho = hasil["rank_umkm"].corr(hasil["rank_skor"], method="spearman")
base_top = set(hasil.sort_values("skor_prioritas").tail(5)["nama_kabupaten_kota"])
print("Spearman:", round(rho, 2), "| overlap Top 5:",
      len(base_top & set(hasil.sort_values("total_umkm_2023").tail(5)["nama_kabupaten_kota"])), "/5")

W0 = {"pasar": 30, "sektor": 25, "digital": 20, "adopsi": 15, "ekonomi": 10}
SKEN = {"Basis": dict(W0),
        "Pasar +5/Adopsi -5": {**W0, "pasar": 35, "adopsi": 10},
        "Digital +5/Ekonomi -5": {**W0, "digital": 25, "ekonomi": 5},
        "Sektor +5/Pasar -5": {**W0, "sektor": 30, "pasar": 25}}
for nama, w in SKEN.items():
    assert sum(w.values()) == 100
    s = X @ np.array([w[k] / 100 for k in ["pasar", "sektor", "digital", "adopsi", "ekonomi"]])
    top = set(merged.iloc[np.argsort(s)[-5:]]["nama_kabupaten_kota"])  # merged = urutan final
    print(nama, "overlap:", len(top & base_top), "/5")
```

</details>

### Langkah 13: Top 5 segmen + cek scraping

**Tujuan:** tabel (Sektor dominan binaan × Wilayah × Skor × Estimasi UMKM × Alasan) dan tabel
rekomendasi scraping berbasis robots.txt aktual + ToS.

**Instruksi scraping:** fetch `https://<domain>/robots.txt` tiap kandidat (Google, Tokopedia,
Shopee, GoFood, Grab), catat status (Diizinkan/Dibatasi/Tidak ada), baca ToS, simpulkan:
scraping halaman dilarang → pakai API resmi (Places API, Seller API) atau jalur kemitraan.

<details>
<summary><b>Kode: Top 5 dan cek robots.txt</b></summary>

```python
grup = (binaan.assign(g=np.select(
    [binaan["jenis_usaha"].isin(RITEL), binaan["jenis_usaha"].isin(FNB),
     binaan["jenis_usaha"].isin(JASA)], ["Ritel", "F&B", "Jasa"], "Luar"))
    .groupby(["nama_kabupaten_kota", "g"])["jumlah_umkm"].sum().unstack(fill_value=0))
seg = []
for _, r in hasil.sort_values("skor_prioritas", ascending=False).head(5).iterrows():
    g = grup.loc[r["nama_kabupaten_kota"], ["Ritel", "F&B", "Jasa"]]
    est = int(r["total_umkm_2023"] * g.sum() / grup.loc[r["nama_kabupaten_kota"]].sum())
    seg.append({"Sektor": f"{g.idxmax()} (transaksi harian)", "Wilayah": r["nama_kabupaten_kota"],
                "Skor": round(r["skor_prioritas"], 3), "Estimasi jumlah UMKM": f"{est:,}",
                "Alasan": f"peringkat {int(r['ranking'])}; {r['tipe_wilayah']}"})
pd.DataFrame(seg, index=range(1, 6)).to_csv(P("output", "top5_segmen.csv"), index=False)

import urllib.request
for url in ["https://www.google.com/robots.txt", "https://www.tokopedia.com/robots.txt",
            "https://shopee.co.id/robots.txt", "https://gofood.link/robots.txt",
            "https://www.grab.com/robots.txt"]:
    try:
        txt = urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read().decode("utf-8", "ignore")
        print(f"[{url}]")
        print("\n".join(l for l in txt.splitlines()
                        if l.lower().startswith(("user-agent: *", "disallow:")))[:8], "\n")
    except Exception as e:
        print(f"[{url}] gagal: {e} (catat manual, jangan karang)")
```

</details>

---

## Lampiran A: Upload ke Google Colab

1. Di Colab: panel Files > New folder > `data`; upload 5 CSV sumber ke dalamnya.
2. Upload notebook via File > Upload notebook.
3. Runtime > Run all. Jika `AssertionError` folder data, perbaiki letak file lalu ulangi.
4. Share > Anyone with the link > salin link ke laporan.

## Lampiran B: Troubleshooting

| Gejala | Penyebab | Perbaikan |
|---|---|---|
| `AssertionError` 27 baris (PDRB/internet) | Artefak OCR / halaman PDF beda | Sesuaikan alias dan indeks halaman, cek manual 1-2 baris |
| `MinMaxScaler` error / kolom konstan | Indikator std ≈ 0 (template proyeksi) | Ganti sumber komposisi (pakai binaan), jangan pakai kolom itu |
| Label klaster "berubah" antar run | Nama hardcode per nomor label | Namai dari rata-rata profil tiap run |
| Overlap sensitivitas aneh (mis. basis ≠ 5/5) | `argsort` di frame terurut-skor | Index ke frame urutan-final (`merged`) |
| Portal ODJ 502 / data.go.id error | WAF / aplikasi rusak | Pakai API backend langsung; arsip Wayback; catat di SOURCES |
| Dataset Kaggle "UMKM" sintetis | Dinyatakan sintetis oleh pemilik | Tolak, sebab melanggar aturan anti-karangan |
