"""Bước 1: tải light curve Kepler từ MAST và xuất CSV để mở bằng Google Sheets.

Cách chạy:
    .venv/Scripts/python scripts/01_download.py "Kepler-6"
    .venv/Scripts/python scripts/01_download.py "KIC 10874614" --quarters 1 2 3

Kết quả:
    data/raw/...                          file FITS gốc (mỗi quý 1 file)
    data/csv/<sao>_Q<n>_raw.csv            dữ liệu thô 1 quý, mở thẳng bằng Google Sheets
    data/csv/<sao>_all_flat.csv            tất cả các quý, đã ghép + làm phẳng (dùng cho bước 2)
    data/csv/<sao>_star_header.csv         thông tin ngôi sao đọc từ header FITS
"""

import argparse
import sys
import warnings
from pathlib import Path

import lightkurve as lk
import numpy as np
import requests

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định không in được tiếng Việt

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
CSV_DIR = ROOT / "data" / "csv"
ARCHIVE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
BKJD_OFFSET = 2454833.0  # BKJD = BJD − 2454833

# Các khóa header mô tả ngôi sao (xem docs/kien-thuc-exoplanet.md, mục 3.1)
STAR_KEYS = ["OBJECT", "KEPLERID", "RA_OBJ", "DEC_OBJ", "KEPMAG", "TEFF", "LOGG", "FEH", "RADIUS"]


def slug(name: str) -> str:
    return name.replace(" ", "").replace("-", "")


def known_transit_mask(host: str, time_bkjd: np.ndarray) -> np.ndarray:
    """True ở các điểm nằm trong transit (±T14, tức gấp đôi thời lượng) của hành tinh đã biết trên NASA.
    Bộ lọc làm phẳng bỏ qua các điểm này khi vẽ đường xu hướng, nên không "là phẳng" mất một phần transit."""
    query = f"select pl_name,pl_orbper,pl_tranmid,pl_trandur from pscomppars where hostname='{host}' and tran_flag=1"
    rows = requests.get(ARCHIVE_URL, params={"query": query, "format": "json"}, timeout=60).json()
    mask = np.zeros_like(time_bkjd, dtype=bool)
    for row in rows:
        if not (row["pl_orbper"] and row["pl_tranmid"] and row["pl_trandur"]):
            continue
        t0 = row["pl_tranmid"] - BKJD_OFFSET
        phase = (time_bkjd - t0 + row["pl_orbper"] / 2) % row["pl_orbper"] - row["pl_orbper"] / 2
        mask |= np.abs(phase) < row["pl_trandur"] / 24
        print(f"  Che transit {row['pl_name']} (P = {row['pl_orbper']:.4f} ngày, T14 = {row['pl_trandur']:.2f} giờ)")
    return mask


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help='Tên sao hoặc mã KIC, ví dụ "Kepler-6" hoặc "KIC 10874614"')
    parser.add_argument("--quarters", type=int, nargs="*", help="Chỉ tải một số quý (mặc định: tất cả)")
    parser.add_argument("--sheet-quarter", type=int, default=2, help="Quý xuất ra CSV cho Google Sheets (mặc định: Q2, đủ ~90 ngày)")
    parser.add_argument(
        "--flatten-window", type=int, default=901,
        help="Cửa sổ làm phẳng (số điểm, 49 điểm ≈ 1 ngày). Mặc định 901 ≈ 18 ngày; sao có vết đen quay nhanh "
             "(vd. sao lùn M Kepler-186) cần ngắn hơn, nhưng phải dài hơn ≥ 3 lần transit dài nhất",
    )
    parser.add_argument(
        "--mask-known", action="store_true",
        help="Che transit của các hành tinh đã biết (lấy P, T0, T14 từ NASA) khi làm phẳng, để không làm nông transit",
    )
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    name = slug(args.target)

    # author="Kepler": lấy sản phẩm chính thức của pipeline Kepler; long cadence ≈ 29.4 phút
    search = lk.search_lightcurve(args.target, author="Kepler", cadence="long", quarter=args.quarters)
    print(search)
    if len(search) == 0:
        raise SystemExit("Không tìm thấy dữ liệu. Kiểm tra lại tên sao.")

    collection = search.download_all(download_dir=str(RAW_DIR))
    print(f"\nĐã tải {len(collection)} file FITS vào {RAW_DIR}")

    # Thông tin ngôi sao từ header của file đầu tiên
    meta = collection[0].meta
    with open(CSV_DIR / f"{name}_star_header.csv", "w", encoding="utf-8") as f:
        f.write("key,value\n")
        for key in STAR_KEYS:
            f.write(f"{key},{meta.get(key)}\n")
            print(f"  {key:9s} = {meta.get(key)}")

    # 1 quý dữ liệu thô cho Google Sheets: chỉ giữ các dòng chất lượng tốt (QUALITY = 0, không NaN)
    # Q0 chỉ dài ~10 ngày nên mặc định lấy Q2; nếu không có thì lấy file đầu tiên
    by_quarter = {c.meta.get("QUARTER"): c for c in collection}
    first = by_quarter.get(args.sheet_quarter, collection[0])
    q = first.meta.get("QUARTER")
    good = (first.quality.value == 0) & np.isfinite(first.pdcsap_flux.value)
    raw = first[good]
    median = np.nanmedian(raw.pdcsap_flux.value)
    raw_path = CSV_DIR / f"{name}_Q{q}_raw.csv"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write("time_bkjd,sap_flux,pdcsap_flux,pdcsap_flux_err,flux_normalized\n")
        for t, sap, pdc, err in zip(raw.time.value, raw.sap_flux.value, raw.pdcsap_flux.value, raw.pdcsap_flux_err.value):
            f.write(f"{t:.6f},{sap:.3f},{pdc:.3f},{err:.3f},{pdc / median:.6f}\n")
    print(f"\nCSV 1 quý (Q{q}, {len(raw)} dòng) cho Google Sheets: {raw_path}")

    # Ghép tất cả các quý, chuẩn hóa về 1, làm phẳng để loại biến thiên chậm của sao, bỏ điểm ngoại lai.
    # remove_outliers chỉ cắt phía trên (sigma_upper) để không xóa nhầm chính các điểm transit.
    lc = collection.stitch().remove_nans()
    mask = known_transit_mask(args.target, lc.time.value) if args.mask_known else None
    lc = lc.flatten(window_length=args.flatten_window, mask=mask).remove_outliers(sigma_upper=4, sigma_lower=20)
    flat_path = CSV_DIR / f"{name}_all_flat.csv"
    with open(flat_path, "w", encoding="utf-8") as f:
        f.write("time_bkjd,flux,flux_err\n")
        for t, fl, err in zip(lc.time.value, lc.flux.value, lc.flux_err.value):
            f.write(f"{t:.6f},{fl:.6f},{err:.6f}\n")
    print(f"CSV tất cả các quý ({len(lc)} dòng, đã làm phẳng): {flat_path}")


if __name__ == "__main__":
    main()
