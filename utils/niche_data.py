"""
ViralGenix - Centralized Niche & Product Category Taxonomy
Taksonomi kategori niche dan produk terlengkap untuk TikTok Shop, Shopee Affiliate,
Produk Digital, Jasa, dan Edukasi di Indonesia.
"""

import re

COMPREHENSIVE_NICHES = [
    "-- Pilih Kategori Niche Anda --",
    # Fashion, Kecantikan & Perawatan (Top E-Commerce)
    "👗 Fashion Wanita, Hijab, Gamis & Outfit OOTD",
    "👔 Fashion Pria, Sepatu Sneakers & Streetwear",
    "💄 Skincare, Sunscreen, Bodycare & Serum Viral",
    "✨ Make Up Tutorial, Cushion, Lipstik & Kosmetik",
    "💍 Aksesoris Fashion, Jam Tangan & Perhiasan",
    "👜 Tas, Dompet & Koper Travel",
    
    # Kebutuhan Rumah, Dapur & Keseharian
    "🏠 Perlengkapan Rumah Tangga, Dapur & CleanTok",
    "🍳 Alat Masak, Air Fryer, Blender & Peralatan Dapur",
    "🏡 Dekorasi Rumah, Rak Estetik & Kamar Minimalis",
    "🐾 Hewan Peliharaan (Kucing, Anjing & Aksesoris Pet)",
    "🌱 Tanaman Hias, Berkebun & Urban Farming",
    
    # Gadget, Elektronik & Otomotif
    "📱 Gadget, Aksesoris HP, Charger, TWS & Desk Setup",
    "💻 Laptop, Tablet, PC & Tools Kerja Remote",
    "🎮 Gaming, Aksesoris Konsol & Game Mobile",
    "🚗 Otomotif Mobil/Motor, Aksesoris Helm & Detailing",
    
    # Makanan & Minuman
    "🍲 Kuliner, Resep Masak Rumahan & Ide Bekal Hemat",
    "🍪 Snack Viral, Frozen Food, Sambal & Makanan Pedas",
    "☕ Kopi, Cafe Hopping, Minuman Kekinian & Home Barista",
    
    # Ibu, Bayi & Keluarga
    "👶 Perlengkapan Bayi, MPASI, Baju Anak & Stroller",
    "🧸 Mainan Edukasi Anak, Sensory Play & Parenting",
    
    # Bisnis, Finansial & Karir
    "💼 Bisnis Online, Affiliate TikTok/Shopee & Side Hustle",
    "💰 Keuangan Pribadi, Saham, Reksadana & Bebas Utang Pinjol",
    "👔 Karir, Lolos Interview Kerja, CV ATS & Freelancer",
    "📦 Dropship, Jualan Tanpa Modal & Reseller Produk",
    
    # Edukasi, AI, Desain & Konten
    "🤖 Teknologi, AI Tools, ChatGPT & Otomasi Digital",
    "🎨 Desain Canva, Video Editing CapCut & Konten Kreator",
    "🧠 Pengembangan Diri, Produktivitas & Mindset Juara",
    "🗣️ Belajar Bahasa Asing (Inggris, Mandarin, Korea, dll)",
    "📚 Buku Self-Improvement, Bisnis & Edukasi",
    
    # Kesehatan, Fitness & Hubungan
    "🥗 Diet Sehat, Defisit Kalori, Meal Prep & Nutrisi",
    "💪 Fitness, Workout Rumahan, Gym & Suplemen Otot",
    "🧘 Kesehatan Mental, Mengatasi Overthinking & Self-Care",
    "❤️ Hubungan Asmara, Pernikahan & Komunikasi Pasangan",
    
    # Custom
    "✍️ Custom Niche (Ketik Niche Sendiri)"
]

def get_clean_niche(selected_niche: str, custom_input: str = "") -> str:
    """Mengembalikan nama niche bersih tanpa emoji atau nilai custom."""
    if not selected_niche or selected_niche.startswith("--"):
        return ""
    if "Custom Niche" in selected_niche:
        return custom_input.strip()
    # Bersihkan simbol/emoji di awal teks
    cleaned = re.sub(r'^[^\w\s]+\s*', '', selected_niche).strip()
    return cleaned if cleaned else selected_niche.strip()
