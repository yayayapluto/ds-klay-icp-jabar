"""Ekstraksi tabel BPS dari PDF resmi -> CSV siap notebook.
Sumber: data/BPS_Jabar_Dalam_Angka_2025.pdf (Tabel 13.2.5, hlm. 799)
        data/BPS_Kesra_Jabar_2025.pdf (Tabel 7.4, hlm. 118)
Jalankan: python scripts/extract_bps_tables.py  (dari root repo)
"""
import re
import pandas as pd
import pdfplumber

KAB_KODE = {
    "Bogor": 3201, "Sukabumi": 3202, "Cianjur": 3203, "Bandung": 3204,
    "Garut": 3205, "Tasikmalaya": 3206, "Ciamis": 3207, "Kuningan": 3208,
    "Cirebon": 3209, "Majalengka": 3210, "Sumedang": 3211, "Indramayu": 3212,
    "Subang": 3213, "Purwakarta": 3214, "Karawang": 3215, "Bekasi": 3216,
    "Bandung Barat": 3217, "Pangandaran": 3218,
}

def parse_num(s):
    return float(s.replace(".", "").replace(",", "."))

def extract_pdrb(pdf_path, out_csv):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[868].extract_text()
    vals = []
    alias = {"Bogort": "Bogor", "Sukabumih": "Sukabumi",
             "BandungBarat": "Bandung Barat"}
    for line in text.split("\n"):
        line = line.replace("o.", ".").replace("/", "")
        line = re.sub(r"[^A-Za-z0-9\.,\s]", "", line).strip()
        nums = re.findall(r"\d{2,3}\.\d{3}", line)
        nama = re.sub(r"\s*\d.*$", "", line).strip().replace(" ", "")
        nama = alias.get(nama, nama)
        if len(nums) >= 5 and nama in list(KAB_KODE) + list(KOTA_KODE):
            vals.append((nama, parse_num(nums[-1])))
    assert len(vals) == 27, f"baris PDRB {len(vals)} != 27"
    rows = []
    for i, (nama, v) in enumerate(vals):
        if i < 18:
            rows.append((KAB_KODE[nama], "KABUPATEN " + nama.upper(), v))
        else:
            rows.append((KOTA_KODE[nama], "KOTA " + nama.upper(), v))
    df = pd.DataFrame(rows, columns=["kode_kabupaten_kota", "nama_kabupaten_kota",
                                     "pdrb_per_kapita_2024_ribu_rp"])
    assert df["kode_kabupaten_kota"].nunique() == 27
    df.to_csv(out_csv, index=False)
    print(f"PDRB tersimpan: {out_csv} ({len(df)} baris)")
    return df

KOTA_KODE = {"Bogor": 3271, "Sukabumi": 3272, "Bandung": 3273, "Cirebon": 3274,
             "Bekasi": 3275, "Depok": 3276, "Cimahi": 3277,
             "Tasikmalaya": 3278, "Banjar": 3279}

def extract_internet(pdf_path, out_csv):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[152].extract_text()
    rows = []
    for line in text.split("\n"):
        m = re.match(r"^(?:\d+\.\s*)?(Kab\.\s*|Kota\s+)([A-Za-z ]+)", line.strip())
        if not m:
            continue
        kind, nama = m.group(1).strip(), m.group(2).strip()
        nums = re.findall(r"\d+,\d+", line)
        cand = [k for k in list(KAB_KODE) + list(KOTA_KODE) if nama.startswith(k)]
        if len(nums) < 3 or not cand:
            continue
        nama = max(cand, key=len)
        total = parse_num(nums[-1])
        if kind.startswith("Kab"):
            rows.append((KAB_KODE[nama], "KABUPATEN " + nama.upper(), total))
        else:
            rows.append((KOTA_KODE[nama], "KOTA " + nama.upper(), total))
    df = pd.DataFrame(rows, columns=["kode_kabupaten_kota", "nama_kabupaten_kota",
                                     "internet_pct_2025"]).drop_duplicates()
    assert len(df) == 27, f"baris internet {len(df)} != 27"
    df.to_csv(out_csv, index=False)
    print(f"Internet tersimpan: {out_csv} ({len(df)} baris)")
    return df

if __name__ == "__main__":
    pdrb = extract_pdrb("data/BPS_Jabar_Dalam_Angka_2025.pdf", "data/pdrb_2024.csv")
    inet = extract_internet("data/BPS_Kesra_Jabar_2025.pdf", "data/internet_2025.csv")
    print(pdrb["pdrb_per_kapita_2024_ribu_rp"].describe().to_string())
    print(inet["internet_pct_2025"].describe().to_string())
