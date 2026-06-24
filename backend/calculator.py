import json
from pathlib import Path


class ValidationError(ValueError):
    """Net veya OBP değerlerinin geçersiz olduğu durumlar için."""

    pass


def calculate_score(
    year,
    obp,
    tyt_turkce,
    tyt_sosyal_bilimler,
    tyt_matematik,
    tyt_fen_bilimleri,
    ayt_matematik,
    ayt_fizik,
    ayt_kimya,
    ayt_biyoloji,
):
    """
    Verilen yıl ve netlere göre YKS SAY puanı hesaplar.
    Geçersiz girdi durumunda ValidationError fırlatır.
    """

    # --- Validation ---
    validation_rules = {
        "TYT Türkçe": 0 <= tyt_turkce <= 40,
        "TYT Sosyal": 0 <= tyt_sosyal_bilimler <= 20,
        "TYT Matematik": 0 <= tyt_matematik <= 40,
        "TYT Fen": 0 <= tyt_fen_bilimleri <= 20,
        "AYT Matematik": 0 <= ayt_matematik <= 40,
        "AYT Fizik": 0 <= ayt_fizik <= 14,
        "AYT Kimya": 0 <= ayt_kimya <= 13,
        "AYT Biyoloji": 0 <= ayt_biyoloji <= 13,
    }

    validation_error = [alan for alan, durum in validation_rules.items() if not durum]

    if validation_error:
        raise ValidationError(
            f"Bu derslerin netlerinde bir hata var, lütfen düzenleyip tekrar deneyin: {', '.join(validation_error)}"
        )

    if not (25 <= obp <= 100):
        raise ValidationError(
            "Ortaöğretim Başarı Puanı (OBP) 25 ile 100 arasında olmalıdır."
        )

    # --- Weights ---
    current_dir = Path(__file__).resolve().parent
    json_path = current_dir.parent / "data" / "weights.json"

    with open(json_path, "r", encoding="utf-8") as f:
        weights = json.load(f)

    if str(year) not in weights:
        raise KeyError(f"{year} yılı için katsayı verisi bulunamadı.")

    w = weights[str(year)]
    w_tyt = weights[str(year)]["tyt"]
    w_ayt = weights[str(year)]["ayt"]

    return (
        w["base_score"]
        + w_tyt["turkce"] * tyt_turkce
        + w_tyt["sosyal_bilimler"] * tyt_sosyal_bilimler
        + w_tyt["matematik"] * tyt_matematik
        + w_tyt["fen_bilimleri"] * tyt_fen_bilimleri
        + w_ayt["matematik"] * ayt_matematik
        + w_ayt["fizik"] * ayt_fizik
        + w_ayt["kimya"] * ayt_kimya
        + w_ayt["biyoloji"] * ayt_biyoloji
        + obp * 0.6
    )
