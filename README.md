# ⚡ ViralGenix - Continuous AI Content Intelligence & Production Engine

> **Pabrik Produksi Konten Video Pendek Berkelanjutan untuk Kreator, Solo Builder, dan Pemasar Digital.**  
> Otomatisasi riset tren audiens, membedah video kompetitor, meracik skrip hook 3 detik, tabel storyboard 60s, jembatan monetisasi *soft-selling*, subtitle CapCut (.SRT), hingga kit copywriting siap posting dalam 1 alur terpadu.

---

## 🌟 Fitur Utama & Alur Kerja Terpadu (*Continuous Engine*)

### ⚡ 1. Fast-Track Pipeline (Jalur Cepat 5-Tahap untuk Pemula)
- **Fungsi:** Alur kerja terpadu tanpa putus yang mengalirkan data riset secara otomatis dari:
  `[1. Riset Celah] ➔ [2. Hook 3 Detik] ➔ [3. Storyboard 60s] ➔ [4. Monetisasi] ➔ [5. Siap Posting]`
- **Mode Sprint 7 Hari:** Opsi menghasilkan stok kalender konten 1 minggu penuh (Senin s/d Minggu) dalam satu kali klik, lengkap dengan hook, skrip, dan caption, lalu diimpor langsung ke papan produksi.

### 🗂️ 2. Studio Produksi & Papan Kanban (*Production Studio*)
- **Papan Kanban Visual:** Memantau status setiap video (`💡 Ide & Riset` ➔ `🎙️ Siap Syuting` ➔ `🎬 Editing CapCut` ➔ `🚀 Siap Upload` ➔ `✅ Sudah Tayang`).
- **Studio Teleprompter:** Mode latihan dan syuting di depan kamera HP dengan tampilan teks dialog besar, kontras tinggi, dan penghitung kecepatan bicara (*120-140 WPM*).
- **Paket Produksi All-in-One (.ZIP):** Unduh seluruh aset video sekaligus: berkas `.md` naskah, `.csv` tabel produksi, `.srt` subtitle CapCut, dan `.txt` copywriting caption & hashtag.

---

## 🔬 Modul Spesialisasi Terpisah (Modular Tools)

### 3. 📡 Trend Radar & Scraper (Pencari Celah Pasar)
- **Fungsi:** Memindai tren di TikTok, Instagram Reels, dan YouTube Shorts. Menghasilkan 5 sudut pandang unik (*Content Gap Analysis*) yang sedang dicari audiens tapi belum banyak dijawab tuntas oleh kreator lain.

### 4. 🔬 URL Reverse-Engineering (Pembedah Kompetitor)
- **Fungsi:** Mengambil transkrip video YouTube Shorts kompetitor dengan fallback otomatis ke metadata judul & deskripsi jika subtitle tidak tersedia.
- **Output:** Bedah pemicu viralitas dan 3 ide konten turunan (*Steal Like an Artist*).

### 5. 🪝 The 3-Second Hook Generator & Storyboard Table
- **Fungsi:** Menghasilkan 10 variasi hook berbasis 4 pilar psikologi audiens (FOMO, Curiosity, High Gain, Empathy) dan menyusun tabel sutradara 60 detik `[Detik] | [Visual] | [Audio] | [Teks Layar] | [Trigger]`.

### 6. 💰 Monetization Bridge (Jembatan Konversi Halus)
- **Fungsi:** 4 formula jembatan penutup (*The Natural Segue*, *By Popular Demand*, *Scarcity Gift*, *Save/Share Trigger*) untuk mengubah penonton menjadi pembeli tanpa merasa di-hard-sell.

---

## 🛠️ Tech Stack & Arsitektur

- **Antarmuka (Frontend):** [Streamlit](https://streamlit.io/) (Berbasis Python, responsif, Modern Light Mode berstandar SaaS).
- **Multi-LLM Engine:**
  - **Google Gemini API** (`gemini-3.8-flash`, `gemini-3.5-flash`, `gemini-2.5-flash`, `gemini-2.0-flash`) - *100% Gratis 1.500 request/hari, generasi terbaru latensi super rendah.*
  - **Groq Cloud API** (`llama-3.3-70b-versatile`, `deepseek-r1-distill-llama-70b`) - *100% Gratis, super kilat dengan chip LPU tanpa kartu kredit.*
  - **Ollama Local LLM** (`qwen2.5`, `deepseek-r1`) - *100% Offline di komputer sendiri tanpa biaya internet / API.*
  - **DeepSeek API** (`deepseek-chat` / V3, `deepseek-reasoner` / R1) - *Super hemat biaya (hingga 90% lebih murah), penalaran logika sangat tajam & luwes.*
  - **Qwen API / Alibaba DashScope** (`qwen-plus`, `qwen-max`, `qwen-2.5-72b-instruct`) - *Penguasaan nuansa bahasa & konteks kultural lokal Asia/Indonesia terbaik di dunia.*
  - **OpenAI API** (`gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`) - *Standar industri penulisan narasi emosional.*
  - **Anthropic Claude API** (`claude-3-5-sonnet-20241022`) - *Gaya bahasa paling natural dan persuasif.*
  - **OpenRouter Universal Gateway** - *Akses ratusan model AI hanya dengan 1 API key.*
  - **Built-in High-Fidelity Simulation Mode** - *Bisa langsung diuji coba seketika tanpa perlu API key.*
- **Data Extractor:** `youtube-transcript-api` untuk ekstraksi teks subtitle YouTube otomatis.
- **Data Export:** Pandas untuk konversi tabel storyboard ke CSV dan ekspor Markdown.

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### 1. Prasyarat
Pastikan komputer Anda sudah terinstal **Python 3.9+**.

### 2. Instalasi Dependensi
Buka terminal / Command Prompt di folder proyek ini:
```bash
# Jalankan setup otomatis di Windows:
setup.bat

# Atau instal manual via pip:
pip install -r requirements.txt
```

### 3. Konfigurasi API Key (Opsional)
Anda dapat memasukkan API Key langsung melalui antarmuka Web di sidebar, atau membuat file `.env`:
```bash
# Salin file template
copy .env.example .env
```
Isi kunci API yang Anda miliki di dalam file `.env`:
```env
DEEPSEEK_API_KEY=sk-...
DASHSCOPE_API_KEY=sk-...
GEMINI_API_KEY=AIzaSy...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-v1-...
```
> *Catatan: Jika Anda belum memiliki API key, aplikasi tetap dapat dijalankan penuh dengan **Mode Simulasi Berkualitas Tinggi** bawaan!*

### 4. Menjalankan Aplikasi
```bash
# Cara 1: Menggunakan file batch (Windows)
run.bat

# Cara 2: Menjalankan langsung perintah Streamlit
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser Anda pada alamat: `http://localhost:8501`.

---

## 📁 Struktur Direktori Proyek

```text
viral-genix/
├── app.py                     # Entry point & Navigasi Utama Streamlit
├── requirements.txt           # Daftar dependensi Python
├── .env.example               # Template environment variables
├── .env                       # File konfigurasi aktif (opsional)
├── run.bat                    # Script 1-klik untuk menjalankan aplikasi di Windows
├── setup.bat                  # Script 1-klik untuk instalasi dependensi
├── README.md                  # Dokumentasi teknis & panduan bisnis
├── assets/
│   └── style.css              # Custom styling UI (Dark Neon Creator Aesthetic)
├── modules/
│   ├── __init__.py
│   ├── trend_radar.py         # Modul 1: Radar tren & celah pasar
│   ├── video_analyzer.py      # Modul 2: Reverse-engineering & Steal Like an Artist
│   ├── hook_generator.py      # Modul 3: Hook matrix 3 detik & tabel storyboard
│   └── monetization_bridge.py # Modul 4: Jembatan konversi soft-selling
└── utils/
    ├── __init__.py
    ├── ai_client.py           # Multi-provider AI engine (Gemini, OpenAI, Claude, Demo)
    ├── transcript_extractor.py# Ekstraktor transkrip YouTube dengan fallback
    ├── prompts.py             # Kumpulan System Prompts rahasia teruji
    └── export_helpers.py      # Utilitas ekspor tabel ke CSV & Markdown
```

---

## 💼 Strategi Monetisasi (Ubah Aplikasi Menjadi Mesin Uang)

1. **Jalur 1: In-House Media Engine (Aset Audiens Organik)**
   - Gunakan ViralGenix untuk memproduksi 3-5 konten berpotensi viral setiap hari setara kualitas agensi.
   - Sambungkan dengan penawaran afiliasi (TikTok Shop / Shopee) atau produk digital (ebook, template Notion Rp 49rb - Rp 99rb).
2. **Jalur 2: SaaS Berbayar (Subscription Rp 99.000/bulan)**
   - Tambahkan sistem otentikasi login menggunakan Firebase Auth atau Supabase.
   - Sambungkan ke gateway pembayaran QRIS otomatis (Midtrans / Mayar).
   - Tawarkan layanan ini ke ribuan UMKM dan kreator pemula yang kesulitan membuat konten.

---
*Dibuat untuk Solo Builders & Content Creators Indonesia.*

