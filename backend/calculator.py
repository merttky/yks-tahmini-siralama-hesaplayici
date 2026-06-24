import json
from pathlib import Path


class ValidationError(ValueError):
    """Net veya OBP değerlerinin geçersiz olduğu durumlar için."""
    pass


def calculate_score(year, obp, tr, sos, mat, fen, mat2, fiz2, kimya2, biyo2):
    """
    Verilen yıl ve netlere göre YKS SAY puanı hesaplar.
    Geçersiz girdi durumunda ValidationError fırlatır.
    """

    # --- Validation ---
    if obp < 0:
        raise ValidationError("Ortaöğretim Başarı Puanı 0'dan küçük olamaz.")
    if obp > 100:
        raise ValidationError("Ortaöğretim Başarı Puanı 100'den büyük olamaz.")
    if tr > 40:
        raise ValidationError("Türkçe testinde 40 soru bulunmaktadır.")
    if sos > 20:
        raise ValidationError("Sosyal Bilimler testinde 20 soru bulunmaktadır.")
    if mat > 40:
        raise ValidationError("Matematik testinde 40 soru bulunmaktadır.")
    if fen > 20:
        raise ValidationError("Fen Bilimleri testinde 20 soru bulunmaktadır.")
    if mat2 > 40:
        raise ValidationError("Matematik 2 testinde 40 soru bulunmaktadır.")
    if fiz2 > 14:
        raise ValidationError("Fizik 2 testinde 14 soru bulunmaktadır.")
    if kimya2 > 13:
        raise ValidationError("Kimya 2 testinde 13 soru bulunmaktadır.")
    if biyo2 > 13:
        raise ValidationError("Biyoloji 2 testinde 13 soru bulunmaktadır.")

    # --- Weights ---
    current_dir = Path(__file__).resolve().parent
    json_path = current_dir.parent / "data" / "weights.json"

    with open(json_path, "r", encoding="utf-8") as f:
        weights = json.load(f)

    if str(year) not in weights:
        raise KeyError(f"{year} yılı için katsayı verisi bulunamadı.")

    w = weights[str(year)]["say"]

    return (
        w["taban"]
        + w["tr"]     * tr
        + w["sos"]    * sos
        + w["mat"]    * mat
        + w["fen"]    * fen
        + w["mat2"]   * mat2
        + w["fiz2"]   * fiz2
        + w["kimya2"] * kimya2
        + w["biyo2"]  * biyo2
        + obp * 0.6
    )
