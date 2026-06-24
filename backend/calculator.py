import json

def calculate_point(year, obp, tr, sos, mat, fen, mat2, fiz2, kimya2, biyo2):

    with open("../data/weights.json", "r") as f:
        weights = json.load(f)
        current_year_weights = weights[str(year)]["say"]

    return (
        current_year_weights["taban"]
        + current_year_weights["tr"] * tr
        + current_year_weights["sos"] * sos
        + current_year_weights["mat"] * mat
        + current_year_weights["fen"] * fen
        + current_year_weights["mat2"] * mat2
        + current_year_weights["fiz2"] * fiz2
        + current_year_weights["kimya2"] * kimya2
        + current_year_weights["biyo2"] * biyo2
        + obp * 0.6
    )

print(calculate_point(2025, 100, 30, 10, 30, 6, 28, 10, 10, 0))