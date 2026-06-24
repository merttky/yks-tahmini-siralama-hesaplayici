"""
YKS SAY Hesaplayıcı — FastAPI Backend
Çalıştırmak için: uvicorn main:app --reload
"""

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import BaseModel, Field # type: ignore 
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from calculator import calculate_score, ValidationError
from rank import calculate_rank

app = FastAPI(title="YKS SAY Hesaplayıcı API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Hesaplama yapılacak yıllar
TARGET_YEARS = [2022, 2023, 2024, 2025]

# 2026 tahmini sıralama için ağırlıklar
TAHMIN_AGIRLIKLARI = {
    2022: 0.3073,
    2023: 0.1927,
    2024: 0.1615,
    2025: 0.3385,
}


class HesaplaRequest(BaseModel):
    obp: float = Field(
        80.0, ge=25, le=100, description="Okul başarı puanı (100 üzerinden, yerleşme durumunda /2)"
    )

    # TYT netler
    tr: float = Field(0.0, ge=-10.0, le=40.0, description="TYT Türkçe neti")
    sos: float = Field(0.0, ge=-5.0, le=20.0, description="TYT Sosyal Bilimler neti")
    mat: float = Field(0.0, ge=-10.0, le=40.0, description="TYT Matematik neti")
    fen: float = Field(0.0, ge=-5.0, le=20.0, description="TYT Fen Bilimleri neti")

    # AYT SAY netler
    mat2: float = Field(0.0, ge=-10.0, le=40.0, description="AYT Matematik neti")
    fiz2: float = Field(0.0, ge=-3.5, le=14.0, description="AYT Fizik neti")
    kimya2: float = Field(0.0, ge=-3.25, le=13.0, description="AYT Kimya neti")
    biyo2: float = Field(0.0, ge=-3.25, le=13.0, description="AYT Biyoloji neti")


class YilSonucu(BaseModel):
    puan: float
    siralama: int


class HesaplaResponse(BaseModel):
    success: bool
    sonuclar: dict[int, YilSonucu] | None = None
    tahmin_2026: int | None = None
    hatalar: list[str] | None = None


@app.post("/hesapla", response_model=HesaplaResponse)
def hesapla(req: HesaplaRequest):
    """
    Girilen netlere göre 2022'den 2025'e kadar olan yılların her biri için puan ve sıralama hesaplar.
    Ardından ağırlıklı ortalama ile 2026 tahmini sıralamasını döndürür.
    """
    sonuclar: dict[int, YilSonucu] = {}
    hatalar: list[str] = []

    for year in TARGET_YEARS:
        try:
            puan = calculate_score(
                year,
                req.obp,
                req.tr,
                req.sos,
                req.mat,
                req.fen,
                req.mat2,
                req.fiz2,
                req.kimya2,
                req.biyo2,
            )
            siralama = calculate_rank(puan, year)
            sonuclar[year] = YilSonucu(puan=round(puan, 3), siralama=siralama)

        except ValidationError as e:
            # Validation hatası tüm yıllar için aynı → erken dön
            return HesaplaResponse(success=False, hatalar=[str(e)])

        except KeyError as e:
            hatalar.append(str(e))

        except Exception as e:
            hatalar.append(f"{year} yılı hesaplanamadı: {str(e)}")

    # 2026 tahmini sıralama hesabı (ağırlıklı ortalama)
    tahmin_2026 = None
    if len(sonuclar) == len(TARGET_YEARS):
        tahmin_2026 = round(
            sum(
                sonuclar[year].siralama * TAHMIN_AGIRLIKLARI[year]
                for year in TARGET_YEARS
            )
        )

    return HesaplaResponse(
        success=bool(sonuclar),
        sonuclar=sonuclar if sonuclar else None,
        tahmin_2026=tahmin_2026,
        hatalar=hatalar if hatalar else None,
    )


@app.get("/health")
def health():
    return {"status": "ok", "message": "API çalışıyor.", "yillar": TARGET_YEARS}


# Frontend statik dosya sunumu
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
