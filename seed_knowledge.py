"""
Seed script — Populates the RAG knowledge base with kitchen knowledge.
Run: python seed_knowledge.py
"""

from services.rag import add_documents_batch, get_doc_count

KITCHEN_KNOWLEDGE = [
    {
        "id": "recipe-nasi-goreng",
        "text": """Resep Nasi Goreng Spesial:
Bahan: 2 piring nasi dingin, 2 butir telur, 3 siung bawang putih (cincang), 5 siung bawang merah (iris), 2 sdm kecap manis, 1 sdm saus tiram, cabai rawit sesuai selera, garam dan merica, minyak goreng.
Cara masak: 1) Panaskan minyak, tumis bawang putih dan bawang merah hingga harum. 2) Masukkan telur, orak-arik. 3) Masukkan nasi, aduk rata dengan api besar. 4) Tambahkan kecap manis, saus tiram, garam, merica. 5) Aduk hingga rata dan nasi kering. 6) Sajikan dengan acar, kerupuk, dan irisan timun.
Food cost per porsi: Rp 8.000. Harga jual rekomendasi: Rp 25.000 (food cost 32%).""",
        "metadata": {"source": "recipe", "category": "main_course", "cuisine": "indonesian"},
    },
    {
        "id": "recipe-ayam-bakar",
        "text": """Resep Ayam Bakar Madu:
Bahan: 1 ekor ayam potong 8, 3 sdm madu, 2 sdm kecap manis, 1 sdm saus tiram, 5 siung bawang putih (haluskan), 1 sdt merica, 1 sdm air jeruk nipis, garam secukupnya.
Bumbu marinasi: Campur semua bumbu, lumuri ayam, diamkan minimal 2 jam di kulkas.
Cara masak: 1) Panggang ayam di suhu 180°C selama 25 menit. 2) Olesi sisa marinasi setiap 10 menit. 3) Balik ayam, panggang 15 menit lagi hingga kecoklatan. 4) Sajikan dengan sambal dan lalapan.
Food cost per porsi: Rp 15.000. Harga jual rekomendasi: Rp 45.000 (food cost 33%).""",
        "metadata": {"source": "recipe", "category": "main_course", "cuisine": "indonesian"},
    },
    {
        "id": "sop-food-safety",
        "text": """SOP Keamanan Pangan Dapur:
1. SUHU PENYIMPANAN: Daging segar: -18°C (freezer) atau 0-4°C (chiller, max 3 hari). Sayuran: 4-7°C. Bahan kering: suhu ruang, tempat tertutup.
2. DANGER ZONE: 5°C - 60°C adalah zona bahaya. Makanan tidak boleh berada di zona ini lebih dari 2 jam.
3. FIFO (First In First Out): Selalu gunakan bahan yang masuk lebih dulu. Label tanggal pada semua bahan.
4. CROSS CONTAMINATION: Pisahkan talenan untuk daging mentah (merah), sayuran (hijau), dan makanan matang (putih). Cuci tangan setelah memegang bahan mentah.
5. SUHU MASAK MINIMUM: Ayam: 74°C internal. Daging sapi: 63°C (medium). Ikan: 63°C. Telur: 71°C.
6. COOLING: Makanan panas harus didinginkan dari 60°C ke 21°C dalam 2 jam, lalu ke 5°C dalam 4 jam berikutnya.""",
        "metadata": {"source": "sop", "category": "food_safety"},
    },
    {
        "id": "sop-hygiene",
        "text": """SOP Kebersihan Personal & Dapur:
1. CUCI TANGAN: Wajib sebelum mulai kerja, setelah dari toilet, setelah memegang bahan mentah, setelah bersin/batuk. Gunakan sabun minimal 20 detik.
2. PAKAIAN KERJA: Apron bersih, topi chef/hairnet, sepatu tertutup anti-slip. Tidak boleh memakai perhiasan saat memasak.
3. SANITASI PERMUKAAN: Bersihkan meja kerja dengan sanitizer setiap 2 jam dan setelah berganti bahan. Konsentrasi chlorine: 200ppm.
4. PERALATAN: Cuci, bilas, sanitasi, keringkan. Suhu air pencuci minimal 77°C untuk sanitasi panas.
5. PEST CONTROL: Tutup semua tempat sampah. Bersihkan tumpahan segera. Inspeksi mingguan untuk tanda-tanda hama.""",
        "metadata": {"source": "sop", "category": "hygiene"},
    },
    {
        "id": "sop-inventory",
        "text": """SOP Manajemen Inventory Dapur:
1. PENERIMAAN BARANG: Periksa suhu, tanggal kadaluarsa, kondisi kemasan. Tolak jika: kemasan rusak, suhu tidak sesuai, bau tidak normal.
2. PENYIMPANAN: Rak atas: bahan kering/ringan. Rak tengah: dairy, telur. Rak bawah: daging mentah (untuk mencegah tetesan ke bahan lain).
3. STOCK OPNAME: Lakukan setiap hari untuk bahan segar, mingguan untuk bahan kering. Catat di sistem.
4. PAR LEVEL: Tentukan minimum stock untuk setiap item. Pesan ulang saat mencapai par level.
5. WASTE LOG: Catat semua bahan yang dibuang beserta alasan (expired, rusak, overproduction). Review mingguan untuk identifikasi pola.""",
        "metadata": {"source": "sop", "category": "inventory"},
    },
    {
        "id": "knowledge-food-cost",
        "text": """Panduan Food Cost Management:
FORMULA: Food Cost % = (Cost of Goods Sold / Total Revenue) × 100
TARGET IDEAL: 28-35% untuk restoran full service. 25-30% untuk fast casual.
STRATEGI MENURUNKAN FOOD COST:
1. Portion control — gunakan timbangan dan measuring tools
2. Menu engineering — identifikasi item high profit (stars) vs low profit (dogs)
3. Reduce waste — track waste harian, identifikasi pola
4. Supplier negotiation — bandingkan harga, beli bulk untuk item stabil
5. Cross-utilization — gunakan satu bahan untuk multiple menu items
6. Seasonal menu — gunakan bahan musiman yang lebih murah
MENU ENGINEERING MATRIX:
- Stars: High popularity + High profit → Promote
- Plowhorses: High popularity + Low profit → Re-engineer
- Puzzles: Low popularity + High profit → Reposition
- Dogs: Low popularity + Low profit → Remove""",
        "metadata": {"source": "knowledge", "category": "finance"},
    },
    {
        "id": "recipe-soto-ayam",
        "text": """Resep Soto Ayam:
Bahan: 500g ayam (rebus, suwir), 2L kaldu ayam, 3 lembar daun salam, 2 batang serai (geprek), 3cm lengkuas (geprek), 5 siung bawang putih, 8 siung bawang merah, 2cm kunyit, 1 sdt merica, garam.
Pelengkap: bihun, telur rebus, daun seledri, bawang goreng, jeruk nipis, sambal, kecap.
Cara masak: 1) Haluskan bumbu (bawang putih, bawang merah, kunyit, merica). 2) Tumis bumbu halus + daun salam + serai + lengkuas hingga harum. 3) Masukkan ke kaldu ayam, didihkan. 4) Masak 20 menit. 5) Sajikan dengan ayam suwir dan pelengkap.
Food cost per porsi: Rp 10.000. Harga jual rekomendasi: Rp 30.000 (food cost 33%).""",
        "metadata": {"source": "recipe", "category": "soup", "cuisine": "indonesian"},
    },
    {
        "id": "knowledge-kitchen-workflow",
        "text": """Alur Kerja Dapur Profesional (Brigade System):
MISE EN PLACE: Persiapan sebelum service dimulai. Semua bahan dipotong, bumbu disiapkan, station di-setup.
STATION SETUP:
- Grill station: protein, marinasi, suhu grill 200-250°C
- Sauté station: pan, minyak, bumbu, sayuran
- Cold station (garde manger): salad, appetizer dingin, plating garnish
- Pastry: dessert, roti, pastry
SERVICE FLOW:
1. Order masuk → Chef de partie terima ticket
2. Calling: Head chef announce order
3. Firing: Mulai masak sesuai timing
4. Plating: Tata di piring sesuai standard
5. Pass: Head chef quality check
6. Service: Waiter antar ke meja
TIMING: Appetizer 5-8 menit. Main course 12-18 menit. Dessert 5-10 menit.""",
        "metadata": {"source": "knowledge", "category": "operations"},
    },
]


def seed():
    """Seed the knowledge base with kitchen data."""
    current = get_doc_count()
    if current >= len(KITCHEN_KNOWLEDGE):
        print(f"Knowledge base already has {current} documents. Skipping seed.")
        return

    add_documents_batch(KITCHEN_KNOWLEDGE)
    print(f"✅ Seeded {len(KITCHEN_KNOWLEDGE)} documents into knowledge base.")
    print(f"   Total documents now: {get_doc_count()}")


if __name__ == "__main__":
    seed()
