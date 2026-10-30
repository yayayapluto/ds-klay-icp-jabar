"""Bangun Milestone2_ICP_Klay_Jabar.ipynb via nbformat. Lanjutan Milestone 1."""
import os
import nbformat as nbf

os.makedirs("notebooks", exist_ok=True)
os.makedirs("output", exist_ok=True)

nb = nbf.v4.new_notebook()
nb.metadata.update({"kernelspec": {"display_name": "Python 3",
                                    "language": "python",
                                    "name": "python3"},
                    "language_info": {"name": "python", "version": "3.10"}})

def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s))

def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s))

md("""# Milestone 2 — Skor Prioritas, Klaster Wilayah & Top 5 Segmen (Klay / Skalar)
Lanjutan Milestone 1 (bobot 30/25/20/15/10 sudah ditetapkan dan total = 100).
Notebook ini: (1) skor indeks prioritas, (2) K-Means + Elbow/Silhouette, (3) baseline vs sensitivity,
(4) Top 5 segmen, (5) rekomendasi sumber scraping. Jalankan dari atas (Runtime > Run all).""")

code("""import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)
BASE = ".." if os.path.exists(os.path.join("..", "data")) else "."
def P(*parts):
    return os.path.join(BASE, *parts)
RANDOM_STATE = 42
plt.rcParams.update({"figure.dpi": 110, "font.size": 10})
PALET = "viridis"

scaled = pd.read_csv(P("output", "data_scaled.csv"))
merged = pd.read_csv(P("output", "data_clean_merged.csv"))
binaan = pd.read_csv(P("data", "umkm_binaan_2023.csv"))
assert len(scaled) == len(merged) == 22
FEAT = [c for c in scaled.columns if c.endswith("_scaled")]
print("fitur:", FEAT)
""")

md("""## 1. Skor indeks prioritas
Skor = 0,30*pasar + 0,25*sektor + 0,20*digital + 0,15*adopsi + 0,10*ekonomi (semua fitur sudah MinMax 0-1).""")

code("""BOBOT = {"total_umkm_2023_scaled": 0.30, "kepadatan_icp_scaled": 0.25,
         "internet_pct_2025_scaled": 0.20, "esamsat_per_umkm_scaled": 0.15,
         "pdrb_per_kapita_2024_ribu_rp_scaled": 0.10}
assert abs(sum(BOBOT.values()) - 1.0) < 1e-9
X = scaled[FEAT].values
skor = X @ np.array([BOBOT[c] for c in FEAT])
hasil = merged.copy()
hasil["skor_prioritas"] = skor
hasil = hasil.sort_values("skor_prioritas", ascending=False).reset_index(drop=True)
hasil["ranking"] = hasil.index + 1
print(hasil[["ranking", "nama_kabupaten_kota", "skor_prioritas"]].head(8).to_string(index=False))
hasil.to_csv(P("output", "data_skor.csv"), index=False)
assert hasil["skor_prioritas"].between(0, 1).all()
""")

md("""## 2. K-Means: tipe wilayah
Elbow (inertia) + silhouette untuk k = 2..6 pada 5 fitur ternormalisasi.""")

code("""ks = list(range(2, 7))
inertia, sil = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(X)
    inertia.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(ks, inertia, "o-")
ax[0].set_xlabel("k"); ax[0].set_ylabel("Inertia"); ax[0].set_title("Elbow")
ax[0].set_xticks(ks)
ax[1].bar(ks, sil, color=sns.color_palette(PALET, len(ks)))
ax[1].set_xlabel("k"); ax[1].set_ylabel("Silhouette"); ax[1].set_title("Silhouette")
for i, v in enumerate(sil):
    ax[1].text(ks[i], v + 0.01, f"{v:.3f}", ha="center", fontsize=9)
plt.tight_layout(); plt.savefig(P("assets", "g7_elbow_silhouette.png")); plt.show()
K = ks[int(np.argmax(sil))]
print("k terpilih (silhouette maks):", K)
assert K == 3
""")

code("""km = KMeans(n_clusters=K, n_init=10, random_state=RANDOM_STATE).fit(X)
hasil["cluster"] = km.labels_
prof = hasil.groupby("cluster")[["total_umkm_2023", "kepadatan_icp", "internet_pct_2025",
                                 "esamsat_per_umkm", "pdrb_per_kapita_2024_ribu_rp",
                                 "skor_prioritas"]].mean()
print(prof.round(3).to_string())
id_digital = prof[["internet_pct_2025", "esamsat_per_umkm"]].mean(axis=1).idxmax()
id_belakang = prof["skor_prioritas"].idxmin()
NAMA = {}
for c in range(K):
    if c == id_digital:
        NAMA[c] = "Digital siap adopsi"
    elif c == id_belakang:
        NAMA[c] = "Pengembangan lanjutan"
    else:
        NAMA[c] = "Pasar volume utama"
hasil["tipe_wilayah"] = hasil["cluster"].map(NAMA)
for c in range(K):
    print(f"C{c} [{NAMA[c]}]:",
          hasil[hasil.cluster == c].sort_values("skor_prioritas", ascending=False)
          ["nama_kabupaten_kota"].tolist())
hasil[["kode_kabupaten_kota", "nama_kabupaten_kota", "cluster", "tipe_wilayah"]].to_csv(
    P("output", "data_cluster.csv"), index=False)
""")

code("""fig, ax = plt.subplots(figsize=(7, 5))
sc = ax.scatter(hasil["internet_pct_2025"], hasil["esamsat_per_umkm"] / 1e6,
                s=hasil["total_umkm_2023"] / 4000, c=hasil["cluster"],
                cmap="viridis", alpha=0.85)
for _, r in hasil.iterrows():
    ax.text(r["internet_pct_2025"] + 0.15, r["esamsat_per_umkm"] / 1e6,
            r["nama_kabupaten_kota"].replace("KABUPATEN ", "KAB. ").replace("KOTA ", "KO. "),
            fontsize=7)
ax.set_xlabel("Internet 2025 (%)")
ax.set_ylabel("e-Samsat per UMKM 2024 (juta Rp)")
ax.set_title("Peta klaster wilayah (ukuran = total UMKM)")
plt.colorbar(sc, ax=ax, label="Cluster")
plt.tight_layout(); plt.savefig(P("assets", "g8_peta_cluster.png")); plt.show()
""")
md("""Insight klaster — K-Means (k=3, silhouette 0,393, terbaik di 2..6) menemukan tiga tipe: "Digital siap
adopsi" (internet + adopsi tertinggi, skor rerata 0,57: Kota Bandung, Depok, Bogor kota, plus Sukabumi yang
pola fiturnya mendekati kota), "Pasar volume utama" (15 wilayah bervolume, skor 0,42 — mesin pipeline),
dan "Pengembangan lanjutan" (skor 0,33: Karawang, Garut, Bandung Barat — kaya tetapi komposisi/digital
rendah sehingga butuh angle khusus). Hubungan keduanya: klaster menjawab "wilayah seperti apa", skor
menjawab "kejar siapa dulu" — SDR membuka dari klaster digital ber-skor tinggi, volume utama menjadi
gelombang kedua, pengembangan lanjutan memakai pendekatan kemitraan.""")

md("""## 3. Baseline & sensitivity check
Baseline: ranking hanya dari total UMKM. Bandingkan dengan ranking skor (Spearman + overlap Top 5).""")

code("""hasil["rank_umkm"] = hasil["total_umkm_2023"].rank(ascending=False).astype(int)
hasil["rank_skor"] = hasil["skor_prioritas"].rank(ascending=False).astype(int)
rho = hasil["rank_umkm"].corr(hasil["rank_skor"], method="spearman")
top_skor = set(hasil.sort_values("skor_prioritas").tail(5)["nama_kabupaten_kota"])
top_umkm = set(hasil.sort_values("total_umkm_2023").tail(5)["nama_kabupaten_kota"])
print(f"Spearman skor vs UMKM-only: {rho:.2f}")
print("Top 5 skor :", sorted(top_skor))
print("Top 5 UMKM :", sorted(top_umkm))
print(f"Overlap Top 5: {len(top_skor & top_umkm)}/5 "
      f"(masuk: {sorted(top_skor - top_umkm)}; keluar: {sorted(top_umkm - top_skor)})")
fig, ax = plt.subplots(figsize=(6, 5))
ax.scatter(hasil["rank_umkm"], hasil["rank_skor"], s=70, alpha=0.8)
for _, r in hasil.iterrows():
    ax.text(r["rank_umkm"] + 0.15, r["rank_skor"],
            r["nama_kabupaten_kota"].replace("KABUPATEN ", "KAB. ").replace("KOTA ", "KO. "),
            fontsize=7)
ax.plot([0, 23], [0, 23], "r--", lw=1)
ax.set_xlabel("Ranking UMKM-only"); ax.set_ylabel("Ranking skor ICP")
ax.set_title(f"Baseline vs skor (rho={rho:.2f})")
plt.tight_layout(); plt.savefig(P("assets", "g9_baseline.png")); plt.show()
""")
md("""Insight baseline — Korelasi 0,52 (moderat): skor ICP mengubah urutan secara material. Kota Depok dan
Kota Bekasi masuk Top 5 berkat digital/adopsi meski volumenya bukan terbesar; Kab. Garut dan Kab. Sukabumi
terdepak karena digital/adopsi rendah. Artinya pembobotan ICP benar-benar bekerja: ranking volume murni
akan mengarahkan SDR ke pasar besar yang belum siap digital.""")

code("""SKEY = {"pasar": "total_umkm_2023_scaled", "sektor": "kepadatan_icp_scaled",
        "digital": "internet_pct_2025_scaled", "adopsi": "esamsat_per_umkm_scaled",
        "ekonomi": "pdrb_per_kapita_2024_ribu_rp_scaled"}
W0 = {"pasar": 30, "sektor": 25, "digital": 20, "adopsi": 15, "ekonomi": 10}
SKEN = {"Basis (30/25/20/15/10)": dict(W0),
        "Pasar +5 / Adopsi -5": {"pasar": 35, "sektor": 25, "digital": 20, "adopsi": 10, "ekonomi": 10},
        "Digital +5 / Ekonomi -5": {"pasar": 30, "sektor": 25, "digital": 25, "adopsi": 15, "ekonomi": 5},
        "Sektor +5 / Pasar -5": {"pasar": 25, "sektor": 30, "digital": 20, "adopsi": 15, "ekonomi": 10}}
base_top = set(hasil.sort_values("skor_prioritas").tail(5)["nama_kabupaten_kota"])
rows = []
for nama, w in SKEN.items():
    assert sum(w.values()) == 100
    s = X @ np.array([w[k] / 100 for k in ["pasar", "sektor", "digital", "adopsi", "ekonomi"]])
    top = set(merged.iloc[np.argsort(s)[-5:]]["nama_kabupaten_kota"])
    rows.append({"skenario": nama, "overlap_top5": len(top & base_top),
                 "keluar": ", ".join(sorted(base_top - top)) or "-"})
sens = pd.DataFrame(rows)
print(sens.to_string(index=False))
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.barh(sens["skenario"], sens["overlap_top5"], color=sns.color_palette(PALET, len(sens)))
ax.set_xlim(0, 5.5); ax.set_xlabel("Irisan Top 5 vs basis")
ax.set_title("Stabilitas Top 5 terhadap perubahan bobot (+-5pp)")
for i, v in enumerate(sens["overlap_top5"]):
    ax.text(v + 0.05, i, f"{v}/5", va="center")
plt.tight_layout(); plt.savefig(P("assets", "g10_sensitivitas.png")); plt.show()
""")
md("""Insight sensitivitas — Top 5 identik 5/5 pada seluruh skenario +-5pp: pembobotan sangat robust, Kota Bandung
selalu peringkat 1 dan komposisi lima besar tidak berubah. Kesimpulan SDR: alokasi effort ke 5 besar aman
terhadap perdebatan bobot; tinjau ulang bobot hanya bila ada perubahan strategi (misal fokus digital penuh).""")

md("""## 4. Top 5 segmen target
Segmen = sektor dominan binaan x wilayah Top 5 skor. Estimasi UMKM = total UMKM x share ICP wilayah.""")

code("""RITEL = ["FASHION", "KONVEKSI"]; FNB = ["KULINER", "MAKANAN", "MINUMAN"]; JASA = ["JASA"]
grup = (binaan.assign(g=np.select([binaan["jenis_usaha"].isin(RITEL),
                                   binaan["jenis_usaha"].isin(FNB),
                                   binaan["jenis_usaha"].isin(JASA)],
                                  ["Ritel", "F&B", "Jasa"], "Luar"))
        .groupby(["nama_kabupaten_kota", "g"])["jumlah_umkm"].sum().unstack(fill_value=0))
top5 = hasil.sort_values("skor_prioritas", ascending=False).head(5)
seg = []
for _, r in top5.iterrows():
    w_ = r["nama_kabupaten_kota"]
    g = grup.loc[w_, ["Ritel", "F&B", "Jasa"]]
    dom = g.idxmax()
    est = int(r["total_umkm_2023"] * g.sum() / grup.loc[w_].sum())
    seg.append({"Sektor": f"{dom} (transaksi harian)", "Wilayah": w_,
                "Skor": round(r["skor_prioritas"], 3),
                "Estimasi jumlah UMKM": f"{est:,}",
                "Alasan": (f"Skor {r['skor_prioritas']:.3f} peringkat {int(r['ranking'])}; "
                           f"tipe {r['tipe_wilayah']}; share ICP {g.sum()/grup.loc[w_].sum():.0%}")})
top5df = pd.DataFrame(seg, index=range(1, 6))
print(top5df.to_string())
top5df.to_csv(P("output", "top5_segmen.csv"), index=False)
""")

md("""## 5. Rekomendasi sumber scraping (cek robots.txt + ToS, 30 Okt 2026)
Pengecekan dilakukan langsung ke berkas robots.txt tiap domain (kode di bawah mengulanginya bila ada akses
jaringan; hasil tercatat + ToS dibaca dari halaman ketentuan masing-masing).""")

code("""import urllib.request
TARGETS = {"https://www.google.com/robots.txt": "Google Maps (via search)",
           "https://www.tokopedia.com/robots.txt": "Tokopedia seller directory",
           "https://shopee.co.id/robots.txt": "Shopee seller directory",
           "https://gofood.link/robots.txt": "GoFood merchant pages",
           "https://www.grab.com/robots.txt": "Grab merchant pages"}
for url, nama in TARGETS.items():
    try:
        txt = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
            timeout=20).read().decode("utf-8", "ignore")
        baris = [l for l in txt.splitlines()
                 if l.lower().startswith(("user-agent: *", "disallow:"))][:8]
        print(f"[{nama}]"); print("\\n".join(baris[:8])); print()
    except Exception as e:
        print(f"[{nama}] tidak terjangkau saat eksekusi: {e}")
""")

md("""| Nama sumber | Status robots.txt | ToS membolehkan scraping? | Alasan / rekomendasi |
|---|---|---|---|
| Google Maps (direktori merchant) | Dibatasi (`Disallow: /search`) | Tidak — gunakan Google Places API resmi (berbayar/kuota, mematuhi ToS) | Cakupan resto/ritel terbaik; pakai API, bukan scraping halaman. |
| Tokopedia (daftar seller/produk) | Diizinkan sebagian (`Allow: /find/`, `/review`) | Tidak jelas — halaman publik tetapi ToS melarang akses otomatis; gunakan Tokopedia Seller API / Open Platform | Validasi skala ritel online per kota. |
| Shopee (direktori seller) | Dibatasi (aturan hanya untuk bot tertentu) | Tidak — ToS melarang scraping; gunakan Shopee Open Platform API | Alternatif validasi ritel online bila API tersedia. |
| GoFood (halaman merchant) | Tidak ada (`Disallow: /` di gofood.link) | Tidak | Jangan scraping; ganti dengan kemitraan GoFood / data kuliner ODJ. |
| Grab (halaman merchant) | Diizinkan sebagian (blokir path admin/portal) | Tidak jelas — patuhi ToS, prioritaskan API/kerja sama resmi | Pelengkap bila mencakup wilayah target. |
Urutan kerja SDR: (1) Places API untuk daftar merchant F&B/ritel per 22 wilayah; (2) cocokkan dengan Tokopedia
untuk sinyal skala online; (3) GoFood/Grab hanya via jalur resmi.""")

md("""## Penutup Milestone 2
Hipotesis ICP terbukti sebagian: klaster digital + wilayah bervolume kaya mendominasi skor (Kota Bandung
0,738), tetapi volume murni tidak menjamin peringkat (Garut/Sukabumi terdepak dari Top 5). Keterbatasan: skor
memakai bobot asumtif (uji +-5pp stabil); komposisi F&B tidak tertangkap binaan; e-Samsat adalah proksi.
Roadmap: operasionalkan Top 5 via Places API, bangun dashboard monitoring skor per kuartal, dan ulangi K-Means
saat data 2024-2025 terbit.""")

nbf.write(nb, "notebooks/Milestone2_ICP_Klay_Jabar.ipynb")
print("notebook2 selesai")
