# 💡 Saran Fitur Tambahan KitchenOS-AI

> Disimpan: 10 Mei 2026

---

## 1. 📦 Inventory & Bahan Baku (Structured Database)

**Apa:** Tabel bahan baku yang bisa di-upload, di-update lewat chat, dan dipakai semua agent.

**Cara kerja:**
- Upload file CSV/Excel → auto jadi tabel
- Update via chat: "Harga ayam naik jadi 12.000"
- Finance agent otomatis pakai harga terbaru
- Alert kalau stok menipis

**Bukan RAG** — ini database terstruktur.

---

## 2. 📅 Menu Planner (Scheduling)

**Apa:** Rencana menu harian/mingguan yang otomatis hitung kebutuhan bahan.

**Cara kerja:**
- User: "Buat menu minggu ini untuk 50 porsi/hari"
- Sistem: Ambil resep dari RAG → hitung bahan dari tabel harga → generate jadwal
- Output: Tabel menu + shopping list + estimasi biaya

**Gabungan RAG + Structured Data + LLM.**

---

## 3. 📊 Dashboard Analytics

**Apa:** Halaman visual yang tampilkan trend food cost, waste, revenue.

**Cara kerja:**
- Grafik food cost % per minggu
- Top 5 bahan paling banyak di-waste
- Perbandingan target vs actual cost
- Alert kalau food cost > 35%

**Murni dari structured data** (waste tracker + finance).

---

## 4. 🧾 Auto Receipt Parser → Update Stok

**Apa:** Foto nota belanja → OCR → otomatis update harga & stok bahan baku.

**Cara kerja:**
- User foto nota dari supplier
- OCR extract: "Ayam 10kg × Rp 12.000 = Rp 120.000"
- Sistem otomatis update tabel bahan baku
- Kalau harga berubah dari sebelumnya → alert

**Gabungan Vision/OCR + Structured Database.**

---

## 5. 🔔 Smart Alerts (Proactive)

**Apa:** Bot yang proaktif kasih peringatan tanpa ditanya.

**Contoh:**
- "⚠️ Harga ayam naik 30% dari minggu lalu"
- "⚠️ Food cost bulan ini sudah 38%, di atas target"
- "⚠️ Stok bawang merah tinggal 2kg, biasanya habis 5kg/hari"
- "💡 Waste daging sapi tinggi minggu ini, pertimbangkan kurangi porsi"

**Dari analisis structured data + rules.**

---

## 6. 👨‍🍳 Staff Briefing Generator

**Apa:** Generate briefing harian untuk tim dapur.

**Cara kerja:**
- User: "Buat briefing hari ini"
- Sistem compile: menu hari ini + bahan yang perlu disiapkan + reminder SOP + info harga berubah
- Output: PDF atau teks yang bisa di-share ke grup

**Gabungan RAG (SOP) + Structured Data (menu, harga) + LLM.**

---

## 📋 Ringkasan Teknologi per Fitur

| Fitur | RAG | Structured DB | LLM | Vision |
|-------|-----|---------------|-----|--------|
| Resep & SOP | ✅ | | ✅ | |
| Finance Calculator | | ✅ | ✅ | |
| Bahan Baku & Harga | | ✅ | ✅ | |
| Menu Planner | ✅ | ✅ | ✅ | |
| Receipt Scanner | | ✅ | | ✅ |
| Waste Tracking | | ✅ | ✅ | |
| Smart Alerts | | ✅ | ✅ | |
| Staff Briefing | ✅ | ✅ | ✅ | |
| Web Search | | | ✅ | |
| Recommendation | ✅ | ✅ | ✅ | |

---

## Prioritas Rekomendasi

1. **📦 Inventory & Bahan Baku** — paling impactful, user sudah minta
2. **🧾 Auto Receipt Parser** — wow factor untuk presentasi
3. **📅 Menu Planner** — menunjukkan integrasi RAG + structured data
