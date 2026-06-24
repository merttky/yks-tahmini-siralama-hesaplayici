/**
 * YKS 2026 Tahmini Sıralama Hesaplayıcı — App JS
 * Net hesaplama (doğru - 0.25 × yanlış), API çağrısı, sonuç gösterimi
 */

(() => {
  'use strict';

  // ── Ders tanımları ───────────────────────────────
  const TYT_DERSLER = ['tr', 'sos', 'mat', 'fen'];
  const AYT_DERSLER = ['mat2', 'fiz2', 'kimya2', 'biyo2'];
  const DERSLER = [...TYT_DERSLER, ...AYT_DERSLER];

  // ── DOM referansları ─────────────────────────────
  const dom = {
    form: document.getElementById('yks-form'),
    obpInput: document.getElementById('obp-input'),
    obpYarila: document.getElementById('obp-yarila'),
    btnHesapla: document.getElementById('btn-hesapla'),
    resultsSection: document.getElementById('results-section'),
    tahmin2026: document.getElementById('tahmin-2026-value'),
    yilGrid: document.getElementById('yil-grid'),
    toast: document.getElementById('toast'),
    tytToplamNet: document.getElementById('tyt-toplam-net'),
    aytToplamNet: document.getElementById('ayt-toplam-net'),
  };

  // ── OBP Input ────────────────────────────────────
  function initOBP() {
    // OBP input alanı — ek bir listener gerekmiyor, değer form gönderilirken okunacak
  }

  // ── Net Hesaplama ────────────────────────────────
  function calculateNet(dogru, yanlis) {
    return dogru - 0.25 * yanlis;
  }

  function updateNet(ders) {
    const maxSoru = parseInt(document.querySelector(`[data-ders="${ders}"]`).dataset.max, 10);
    const dogruEl = document.getElementById(`${ders}-dogru`);
    const yanlisEl = document.getElementById(`${ders}-yanlis`);
    const netEl = document.getElementById(`${ders}-net`);
    const errorEl = document.getElementById(`${ders}-error`);
    const card = document.querySelector(`[data-ders="${ders}"]`);

    let dogru = parseInt(dogruEl.value, 10) || 0;
    let yanlis = parseInt(yanlisEl.value, 10) || 0;

    // Clamp değerleri
    dogru = Math.max(0, Math.min(maxSoru, dogru));
    yanlis = Math.max(0, Math.min(maxSoru, yanlis));

    // Validation: doğru + yanlış ≤ toplam soru
    let hasError = false;
    if (dogru + yanlis > maxSoru) {
      errorEl.textContent = `Doğru + Yanlış toplamı ${maxSoru} soruyu aşamaz`;
      errorEl.classList.add('visible');
      dogruEl.classList.add('has-error');
      yanlisEl.classList.add('has-error');
      card.classList.add('card-error');
      hasError = true;
    } else {
      errorEl.textContent = '';
      errorEl.classList.remove('visible');
      dogruEl.classList.remove('has-error');
      yanlisEl.classList.remove('has-error');
      card.classList.remove('card-error');
    }

    const net = calculateNet(dogru, yanlis);
    netEl.textContent = net.toFixed(2);

    // Renk sınıfları
    netEl.classList.remove('positive', 'negative', 'zero');
    if (net > 0) {
      netEl.classList.add('positive');
    } else if (net < 0) {
      netEl.classList.add('negative');
    } else {
      netEl.classList.add('zero');
    }

    // Toplam netleri güncelle
    updateTotalNets();

    return !hasError;
  }

  // ── Toplam Net Hesaplama ─────────────────────────
  function getTotalNet(dersListesi) {
    let total = 0;
    dersListesi.forEach((ders) => {
      const dogru = parseInt(document.getElementById(`${ders}-dogru`).value, 10) || 0;
      const yanlis = parseInt(document.getElementById(`${ders}-yanlis`).value, 10) || 0;
      total += calculateNet(dogru, yanlis);
    });
    return total;
  }

  function updateTotalNets() {
    const tytTotal = getTotalNet(TYT_DERSLER);
    const aytTotal = getTotalNet(AYT_DERSLER);

    dom.tytToplamNet.textContent = tytTotal.toFixed(2);
    dom.aytToplamNet.textContent = aytTotal.toFixed(2);

    // Renk ayarla
    [
      { el: dom.tytToplamNet, val: tytTotal },
      { el: dom.aytToplamNet, val: aytTotal },
    ].forEach(({ el, val }) => {
      el.classList.remove('positive', 'negative', 'zero');
      if (val > 0) el.classList.add('positive');
      else if (val < 0) el.classList.add('negative');
      else el.classList.add('zero');
    });
  }

  function initNetListeners() {
    DERSLER.forEach((ders) => {
      const dogruEl = document.getElementById(`${ders}-dogru`);
      const yanlisEl = document.getElementById(`${ders}-yanlis`);

      [dogruEl, yanlisEl].forEach((el) => {
        el.addEventListener('input', () => updateNet(ders));
        el.addEventListener('change', () => updateNet(ders));
      });
    });
  }

  // ── API Çağrısı ──────────────────────────────────
  function collectFormData() {
    let obp = parseFloat(dom.obpInput.value) || 80;

    // Geçen sene yerleşme durumu: OBP yarıya düşür
    if (dom.obpYarila.checked) {
      obp = obp / 2;
    }
    const nets = {};

    DERSLER.forEach((ders) => {
      const dogru = parseInt(document.getElementById(`${ders}-dogru`).value, 10) || 0;
      const yanlis = parseInt(document.getElementById(`${ders}-yanlis`).value, 10) || 0;
      nets[ders] = calculateNet(dogru, yanlis);
    });

    return {
      obp,
      tr: nets.tr,
      sos: nets.sos,
      mat: nets.mat,
      fen: nets.fen,
      mat2: nets.mat2,
      fiz2: nets.fiz2,
      kimya2: nets.kimya2,
      biyo2: nets.biyo2,
    };
  }

  function validateAll() {
    let allValid = true;
    let firstErrorDers = null;

    DERSLER.forEach((ders) => {
      if (!updateNet(ders)) {
        allValid = false;
        if (!firstErrorDers) firstErrorDers = ders;
      }
    });

    // OBP validasyonu
    const obpVal = parseFloat(dom.obpInput.value);
    if (isNaN(obpVal) || obpVal < 50 || obpVal > 100) {
      allValid = false;
      dom.obpInput.classList.add('has-error');
      if (!firstErrorDers) {
        dom.obpInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else {
      dom.obpInput.classList.remove('has-error');
    }

    // İlk hatalı alana scroll
    if (firstErrorDers) {
      const errorCard = document.querySelector(`[data-ders="${firstErrorDers}"]`);
      errorCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    return allValid;
  }

  async function submitForm() {
    if (!validateAll()) {
      showToast('Doğru ve yanlış toplamı soru sayısını aşamaz. Lütfen hatalı alanları düzeltin.');
      return;
    }

    const data = collectFormData();

    // Loading state
    dom.btnHesapla.classList.add('loading');

    try {
      const res = await fetch('/hesapla', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Sunucu hatası: ${res.status}`);
      }

      const result = await res.json();

      if (!result.success) {
        showToast(result.hatalar?.[0] || 'Hesaplama yapılamadı.');
        return;
      }

      renderResults(result);
    } catch (err) {
      console.error('Hesaplama hatası:', err);
      showToast(err.message || 'Bağlantı hatası. Lütfen tekrar deneyin.');
    } finally {
      dom.btnHesapla.classList.remove('loading');
    }
  }

  // ── Sonuç Gösterimi ──────────────────────────────
  function formatNumber(num) {
    return new Intl.NumberFormat('tr-TR').format(num);
  }

  function renderResults(result) {
    // 2026 Tahmini
    if (result.tahmin_2026 !== null && result.tahmin_2026 !== undefined) {
      animateCountUp(dom.tahmin2026, result.tahmin_2026);
    } else {
      dom.tahmin2026.textContent = '—';
    }

    // Yıl kartları
    dom.yilGrid.innerHTML = '';
    const years = [2022, 2023, 2024, 2025];

    years.forEach((year) => {
      const data = result.sonuclar?.[year];
      if (!data) return;

      const card = document.createElement('div');
      card.className = 'yil-card';
      card.innerHTML = `
        <div class="yil-year">${year} YKS</div>
        <div class="yil-puan">${data.puan.toFixed(2)}</div>
        <div class="yil-puan-label">Puan</div>
        <div class="divider"></div>
        <div class="yil-siralama">${formatNumber(data.siralama)}</div>
        <div class="yil-siralama-label">Sıralama</div>
      `;
      dom.yilGrid.appendChild(card);
    });

    // Sonuçları göster
    dom.resultsSection.classList.add('visible');
    dom.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Count-up Animasyonu ──────────────────────────
  function animateCountUp(el, target, duration = 1200) {
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + (target - start) * eased);

      el.textContent = formatNumber(current);

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  // ── Toast ────────────────────────────────────────
  let toastTimeout = null;

  function showToast(message, duration = 4000) {
    dom.toast.textContent = message;
    dom.toast.classList.add('show');

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      dom.toast.classList.remove('show');
    }, duration);
  }

  // ── Init ─────────────────────────────────────────
  function init() {
    initOBP();
    initNetListeners();

    dom.form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitForm();
    });
  }

  // DOM hazır olduğunda başlat
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
