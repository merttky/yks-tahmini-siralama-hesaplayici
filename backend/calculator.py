import json
from pathlib import Path

def calculate_score(year, obp, tr, sos, mat, fen, mat2, fiz2, kimya2, biyo2):

    if obp < 0:
        return "Ortaöğretim Başarı Puanı 50'den küçük olamaz."
    if obp > 100:
        return "Ortaöğretim Başarı Puanı 100'den büyük olamaz."
    if tr > 40:
        return "Türkçe testinde 40 soru bulunmaktadır."
    if sos > 20:
        return "Sosyal Bilimler testinde 20 soru bulunmaktadır."
    if mat > 40:
        return "Matematik testinde 40 soru bulunmaktadır."
    if fen > 20:
        return "Fen Bilimleri testinde 20 soru bulunmaktadır."
    if mat2 > 40:
        return "Matematik 2 testinde 40 soru bulunmaktadır."
    if fiz2 > 14:
        return "Fizik 2 testinde 14 soru bulunmaktadır."
    if kimya2 > 13:
        return "Kimya 2 testinde 13 soru bulunmaktadır."
    if biyo2 > 13:
        return "Biyoloji 2 testinde 13 soru bulunmaktadır."
    
    current_dir = Path(__file__).resolve().parent

    json_path = current_dir.parent / "data" / "weights.json"

    with open(json_path, "r", encoding="utf-8") as f:
        weights = json.load(f)
        current_year_weights = weights[str(year)]["say"]

    return (
        int(current_year_weights["taban"]
        + current_year_weights["tr"] * tr
        + current_year_weights["sos"] * sos
        + current_year_weights["mat"] * mat
        + current_year_weights["fen"] * fen
        + current_year_weights["mat2"] * mat2
        + current_year_weights["fiz2"] * fiz2
        + current_year_weights["kimya2"] * kimya2
        + current_year_weights["biyo2"] * biyo2
        + obp * 0.6)
    )

