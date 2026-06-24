# YKS 2026 Tahmini Sıralama Hesaplayıcı — Sayısal (SAY)

Bu proje, YKS (Yükseköğretim Kurumları Sınavı) Sayısal adaylarının geçmiş yılların (2022, 2023, 2024 ve 2025) verilerini kullanarak **2026 tahmini sıralamalarını** hesaplayan ve analiz eden modern bir web uygulamasıdır.

Uygulama, geçmiş yılların yığıntılı puan ve sıralama verileri üzerinde **kübik spline interpolasyonu** uygulayarak çalışır ve ağırlıklı analiz ile 2026 yılı sıralamasını tahmin eder.

---

## ✨ Özellikler

*   **Ağırlıklı 2026 Tahmini:** 2022 (%30.73), 2023 (%19.27), 2024 (%16.15) ve 2025 (%33.85) yıllarının sıralama verilerini ağırlıklandırarak 2026 tahmini sıralamasını oluşturur.
*   **Toplam Net Takibi:** TYT ve AYT toplam netleri sayfa üzerinde anlık olarak toplanır ve dinamik olarak renklenir.
*   **OBP Kırılması:** Geçen sene bir bölüme yerleşmiş adaylar için OBP'yi yarıya düşüren opsiyonel OBP katsayısı desteği mevcuttur.
*   **Modern Arayüz:** Gözü yormayan premium mavi-beyaz açık tema, modern SVG ikonları ve yumuşak geçiş efektleri.
*   **Gelişmiş Validasyon:** Soru sayısını aşan doğru/yanlış girişlerinde hata kartı vurgusu (`card-error`) ve ilk hatalı alana otomatik odaklanma/scroll desteği.

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
*   Python 3.10 veya üzeri
*   Modern bir web tarayıcısı

### Adımlar

1.  **Sanal Ortam Oluşturma ve Bağımlılıkların Kurulması:**
    ```bash
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Sunucuyu Başlatma:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```

3.  **Tarayıcıda Açma:**
    Sunucu başladıktan sonra `http://localhost:8000` adresine giderek uygulamayı kullanabilirsiniz.


---

## 📐 Hesaplama Algoritması

1.  **Ders Netleri:** `Net = Doğru - (Yanlış * 0.25)` formülüyle hesaplanır.
2.  **Yıl Puanı:** Taban Puan + (Ders Netleri × Katsayılar) + (OBP × 0.6) formülü uygulanır. Eğer checkbox işaretliyse OBP değeri yarıya bölünür.
3.  **Sıralama Hesaplama:** spline.json içerisindeki verilere göre kübik interpolasyon (`y = a·dx³ + b·dx² + c·dx + d`) uygulanarak sıralama bulunur.
4.  **2026 Sıralama Tahmini:**
    $$\text{Tahmin 2026} = \text{Sıralama}_{22} \cdot 0.3073 + \text{Sıralama}_{23} \cdot 0.1927 + \text{Sıralama}_{24} \cdot 0.1615 + \text{Sıralama}_{25} \cdot 0.3385$$