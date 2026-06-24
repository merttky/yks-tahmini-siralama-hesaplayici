"""
YKS SAY Hesaplayıcı — FastAPI Backend
Çalıştırmak için: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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


class HesaplaRequest(BaseModel):
    obp: float = Field(80.0, ge=0, le=100, description="Okul başarı puanı (100 üzerinden)")

    # TYT netler
    tr:  float = Field(0.0, ge=-10.0,  le=40.0, description="Türkçe neti")
    sos: float = Field(0.0, ge=-5.0,   le=20.0, description="Sosyal Bilimler neti")
    mat: float = Field(0.0, ge=-10.0,  le=40.0, description="Matematik neti")
    fen: float = Field(0.0, ge=-5.0,   le=20.0, description="Fen Bilimleri neti")

    # AYT SAY netler
    mat2:   float = Field(0.0, ge=-10.0, le=40.0, description="Matematik 2 neti")
    fiz2:   float = Field(0.0, ge=-3.5,  le=14.0, description="Fizik 2 neti")
    kimya2: float = Field(0.0, ge=-3.25, le=13.0, description="Kimya 2 neti")
    biyo2:  float = Field(0.0, ge=-3.25, le=13.0, description="Biyoloji 2 neti")


class YilSonucu(BaseModel):
    puan:     float
    siralama: int


class HesaplaResponse(BaseModel):
    success:  bool
    sonuclar: dict[int, YilSonucu] | None = None
    hatalar:  list[str] | None = None


@app.post("/hesapla", response_model=HesaplaResponse)
def hesapla(req: HesaplaRequest):
    """
    Girilen netlere göre 2022–2025 yıllarının her biri için
    ayrı katsayılarla puan ve sıralama hesaplar.
    """
    sonuclar: dict[int, dict] = {}
    hatalar: list[str] = []

    for year in TARGET_YEARS:
        try:
            puan = calculate_score(
                year, req.obp,
                req.tr, req.sos, req.mat, req.fen,
                req.mat2, req.fiz2, req.kimya2, req.biyo2,
            )
            siralama = calculate_rank(puan, year)
            sonuclar[year] = {
                "puan":     round(puan, 3),
                "siralama": siralama,
            }

        except ValidationError as e:
            # Validation hatası tüm yıllar için aynı → erken dön
            return HesaplaResponse(success=False, hatalar=[str(e)])

        except KeyError as e:
            hatalar.append(str(e))

        except Exception as e:
            hatalar.append(f"{year} yılı hesaplanamadı: {str(e)}")

    return HesaplaResponse(
        success=bool(sonuclar),
        sonuclar=sonuclar if sonuclar else None,
        hatalar=hatalar if hatalar else None,
    )


@app.get("/health")
def health():
    return {"status": "ok", "message": "API çalışıyor.", "yillar": TARGET_YEARS}
