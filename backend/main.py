"""
YKS SAY Hesaplayıcı — FastAPI Backend
Çalıştırmak için: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import sys

# Aynı klasördeki modülleri import et
sys.path.insert(0, str(Path(__file__).parent))

from calculator import calculate_score
from rank import calculate_rank

app = FastAPI(title="YKS SAY Hesaplayıcı API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class HesaplaRequest(BaseModel):
    year: int = Field(..., ge=2021, le=2025, description="Sınav yılı")
    obp: float = Field(80.0, ge=0, le=100, description="Okul başarı puanı (100 üzerinden)")

    # TYT netler
    tr: float = Field(0.0, ge=-10, le=40)
    sos: float = Field(0.0, ge=-5, le=20)
    mat: float = Field(0.0, ge=-10, le=40)
    fen: float = Field(0.0, ge=-5, le=20)

    # AYT SAY netler
    mat2: float = Field(0.0, ge=-7.5, le=30)
    fiz2: float = Field(0.0, ge=-3.5, le=14)
    kimya2: float = Field(0.0, ge=-3.25, le=13)
    biyo2: float = Field(0.0, ge=-3.25, le=13)


@app.post("/hesapla")
def hesapla(req: HesaplaRequest):
    try:
        puan = calculate_score(
            req.year, req.obp,
            req.tr, req.sos, req.mat, req.fen,
            req.mat2, req.fiz2, req.kimya2, req.biyo2
        )
        siralama = calculate_rank(puan, req.year)
        return {
            "success": True,
            "puan": round(puan, 3),
            "siralama": siralama,
        }
    except KeyError:
        return {
            "success": False,
            "error": f"{req.year} yılı için veri bulunamadı.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.get("/health")
def health():
    return {"status": "ok", "message": "API çalışıyor."}