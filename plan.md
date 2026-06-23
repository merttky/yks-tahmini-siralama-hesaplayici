

YAPI-
yks-hesaplayici/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/
│   ├── main.py (API'nin ana giriş noktası)
│   ├── calculator.py (Netleri puana çeviren fonksiyonlar)
│   └── rank_model.py (Puanı polinoma sokup sıralama veren fonksiyonlar)
└── data/
    ├── osym_weights.json (Ders katsayıları)
    └── polynomial_coefs.json (Polinom katsayıları)