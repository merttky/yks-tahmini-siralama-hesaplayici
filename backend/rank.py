import json
from pathlib import Path
from calculator import calculate_score

def calculate_rank(score, year):
    
    current_dir = Path(__file__).resolve().parent
    json_path = current_dir.parent / "data" / "spline.json"

    with open(json_path, "r", encoding="utf-8") as f:
        spline = json.load(f)
        spline_data = spline[str(year)]

    if int(score) >= 560:
        return 1
    if int(score) <= 100:
        return 3500000

    interval = next((s for s in spline_data if s["x_min"] <= int(score) <= s["x_max"]), None)

    if not interval:
        return -1 
    dx = int(score) - interval["x_min"]
    
    rank = (interval["a"] * (dx ** 3)) + \
               (interval["b"] * (dx ** 2)) + \
               (interval["c"] * dx) + \
               interval["d"]
    return max(1, round(rank))

test_score = calculate_score(2025, 100, 41, 10, 30, 6, 28, 10, 10, 0)

print(f"{test_score} Puan Sıralaması:", calculate_rank(test_score, 2025))