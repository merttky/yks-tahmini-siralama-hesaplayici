import json
import math
from pathlib import Path


# ── 2026 tahmin ağırlıkları ve band sabiti ────────────────────────────────────
TAHMIN_AGIRLIKLARI = {2022: 0.3932, 2023: 0.2961, 2024: 0.1117, 2025: 0.1990}
BAND_Z = 0.8  # Güven aralığı çarpanı (log-sıra uzayında)


def calculate_rank(score: float, year: int) -> int:
    """
    Verilen puan ve yıl için tahmini sıralamayı döndürür.
    Spline verisi üzerinden kübik interpolasyon uygular.
    """
    current_dir = Path(__file__).resolve().parent
    spline_path = current_dir.parent / "data" / "spline.json"
    weights_path = current_dir.parent / "data" / "weights.json"

    with open(spline_path, "r", encoding="utf-8") as f:
        spline = json.load(f)

    with open(weights_path, "r", encoding="utf-8") as f:
        weights = json.load(f)

    if str(year) not in spline:
        raise KeyError(f"{year} yılı için spline verisi bulunamadı.")

    # Sayısal için ayarlandı, gelecekte güncelleme için diğer alanlar eklenebilir
    spline_data = spline[str(year)]["say"]
    score_int = int(score)

    # Sınır durumlar
    if score_int >= 560:
        return 1
    if score_int <= weights[str(year)]["base_score"]:
        return weights[str(year)]["tyt"]["lowest_rank"]

    interval = next(
        (s for s in spline_data if s["x_min"] <= score_int <= s["x_max"]),
        None,
    )

    if interval is None:
        return -1  # Veri aralığı dışında

    dx = score_int - interval["x_min"]
    rank = (
        interval["a"] * (dx**3)
        + interval["b"] * (dx**2)
        + interval["c"] * dx
        + interval["d"]
    )
    return max(1, round(rank))


def predict_2026(
    ranks: dict[int, int],
    scores: dict[int, float],
) -> dict:
    """
    Geometrik ortalama (sıra) + aritmetik ortalama (puan) + alt-üst band.

    Log-sıra uzayında ağırlıklı ortalama hesaplanır (geometrik ortalama).
    Band = sqrt(yıllar-arası varyans + yıl-içi puan belirsizliği) × BAND_Z

    ranks:  {2022: 5000, 2023: 8000, 2024: 6000, 2025: 4500}
    scores: {2022: 350.5, 2023: 345.2, 2024: 348.0, 2025: 352.0}

    Returns: {"sira": int, "puan": float, "alt": int, "ust": int}
    """
    w_sum = 0.0
    ln_sira = 0.0
    puan_sum = 0.0
    rows = []

    for year in sorted(TAHMIN_AGIRLIKLARI):
        w = TAHMIN_AGIRLIKLARI[year]
        rank = ranks[year]
        score = scores[year]

        if rank <= 0 or w <= 0:
            continue

        ln = math.log(rank)

        # Yıl-içi 1σ (log-sıra): ±1 puanlık bandın sıralamadaki etkisi
        rank_iyi = calculate_rank(score + 1, year)  # puan ↑ → sıra ↓ (daha iyi)
        rank_kotu = calculate_rank(score - 1, year)  # puan ↓ → sıra ↑ (daha kötü)
        rank_iyi = max(1, rank_iyi)
        rank_kotu = max(1, rank_kotu)
        h = max(0, (math.log(rank_kotu) - math.log(rank_iyi)) / 2)

        w_sum += w
        ln_sira += w * ln
        puan_sum += w * score
        rows.append({"w": w, "ln": ln, "h": h})

    if w_sum == 0:
        return None

    # Log-uzayda ağırlıklı ortalama (= geometrik ortalama)
    L = ln_sira / w_sum

    # Varyans bileşenleri
    v_year = sum(r["w"] * (r["ln"] - L) ** 2 for r in rows) / w_sum  # yıllar-arası
    v_puan = sum(r["w"] * r["h"] ** 2 for r in rows) / w_sum  # yıl-içi belirsizlik

    sig_log = math.sqrt(v_year + v_puan)

    return {
        "sira": max(1, round(math.exp(L))),
        "puan": round(puan_sum / w_sum, 3),
        "alt": max(1, round(math.exp(L - BAND_Z * sig_log))),  # iyi senaryo
        "ust": max(1, round(math.exp(L + BAND_Z * sig_log))),  # kötü senaryo
    }


# ── Test (sadece doğrudan çalıştırıldığında) ─────────────────────────────────
if __name__ == "__main__":
    from calculator import calculate_score

    test_years = [2022, 2023, 2024, 2025]
    test_ranks = {}
    test_scores = {}

    for y in test_years:
        obp_val = 83.42950
        s = calculate_score(y, [obp_val, False], 36.5, 13, 24.5, 15.5, 34.5, 12.75, 11.75, 10.5)
        r = int(calculate_rank(s, y))
        test_scores[y] = s
        test_ranks[y] = r
        print(f"{s:.3f} Puan → {y} Sıralama: {r}")

    tahmin = predict_2026(test_ranks, test_scores)

    print("\n=============================================")
    print(f"Tahmini 2026 YKS Sıralamanız: {tahmin['sira']}")
    print(f"Güven Aralığı: {tahmin['alt']} — {tahmin['ust']}")
    print(f"Ağırlıklı Ortalama Puan: {tahmin['puan']}")
    print("=============================================")
