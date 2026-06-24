import json
from pathlib import Path
from calculator import calculate_point

def hesapla_siralama_spline(score, year):
    
    current_dir = Path(__file__).resolve().parent
    json_path = current_dir.parent / "data" / "spline.json"

    with open(json_path, "r", encoding="utf-8") as f:
        spline = json.load(f)
        spline_data = spline[str(year)]

    if score >= 560:
        return 1
    if score <= 100:
        return 3500000

    interval = next((s for s in spline_data if s["x_min"] <= score <= s["x_max"]), None)

    if not interval:
        return -1 
    dx = score - interval["x_min"]
    
    siralama = (interval["a"] * (dx ** 3)) + \
               (interval["b"] * (dx ** 2)) + \
               (interval["c"] * dx) + \
               interval["d"]
    return max(1, round(siralama))

test_puani = calculate_point(2025, 100, 30, 10, 30, 6, 28, 10, 10, 0)
print(f"{test_puani} Puan Sıralaması:", hesapla_siralama_spline(test_puani, 2025))