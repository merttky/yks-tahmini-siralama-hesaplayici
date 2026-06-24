import json
from pathlib import Path


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


# ── Test (sadece doğrudan çalıştırıldığında) ─────────────────────────────────
if __name__ == "__main__":
    from calculator import calculate_score

    test_score22 = calculate_score(2022, 833.42950, 36.5, 13, 24.5, 15.5, 34.5, 12.75, 11.75, 10.5)
    rank22 = int(calculate_rank(test_score22, 2022))
    print(f"{test_score22:.3f} Puan → 2022 Sıralama: {rank22}")

    test_score23 = calculate_score(2023, 83.42950, 36.5, 13, 24.5, 15.5, 34.5, 12.75, 11.75, 10.5)
    rank23 = int(calculate_rank(test_score23, 2023))
    print(f"{test_score23:.3f} Puan → 2023 Sıralama: {rank23}")

    test_score24 = calculate_score(2024, 83.42950, 36.5, 13, 24.5, 15.5, 34.5, 12.75, 11.75, 10.5)
    rank24 = int(calculate_rank(test_score24, 2024))
    print(f"{test_score24:.3f} Puan → 2024 Sıralama: {rank24}")

    test_score25 = calculate_score(2025, 83.42950, 36.5, 13, 24.5, 15.5, 34.5, 12.75, 11.75, 10.5)
    rank25 = int(calculate_rank(test_score25, 2025))
    print(f"{test_score25:.3f} Puan → 2025 Sıralama: {rank25}")

    w_22 = 0.3073
    w_23 = 0.1927
    w_24 = 0.1615
    w_25 = 0.3385

    # Ağırlıklı ortalama hesaplama algoritması
    r_2026 = (rank22 * w_22) + (rank23 * w_23) + (rank24 * w_24) + (rank25 * w_25)

    print("\n=============================================")
    print(f"Tahmini 2026 YKS Sıralamanız: {round(r_2026)}")
    print("=============================================")
