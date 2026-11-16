"""
ViralGenix - Unified Multi-Provider AI Client
Mendukung Google Gemini, OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet),
DeepSeek (V3 & R1), Qwen (Alibaba Cloud DashScope 2.5),
serta High-Fidelity Simulation Mode jika API key belum diisi.
"""

import os
import time
from typing import Optional, Dict, Any

class AIClient:
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or self._get_env_key(self.provider)
        self.model = model or self._get_default_model(self.provider)
        self.base_url = base_url

    def _get_env_key(self, provider: str) -> Optional[str]:
        from utils.env_manager import get_env_var
        if provider == "openai":
            return get_env_var("OPENAI_API_KEY")
        elif provider in ["gemini", "google"]:
            return get_env_var("GEMINI_API_KEY") or get_env_var("GOOGLE_API_KEY")
        elif provider == "anthropic":
            return get_env_var("ANTHROPIC_API_KEY")
        elif provider == "deepseek":
            return get_env_var("DEEPSEEK_API_KEY")
        elif provider in ["qwen", "dashscope"]:
            return get_env_var("DASHSCOPE_API_KEY") or get_env_var("QWEN_API_KEY")
        elif provider == "groq":
            return get_env_var("GROQ_API_KEY")
        elif provider == "ollama":
            return "ollama-local-key"
        elif provider == "openrouter":
            return get_env_var("OPENROUTER_API_KEY")
        return None

    def _get_default_model(self, provider: str) -> str:
        if provider == "openai":
            return "gpt-4o"
        elif provider in ["gemini", "google"]:
            return "gemini-2.0-flash"
        elif provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        elif provider == "deepseek":
            return "deepseek-chat"
        elif provider in ["qwen", "dashscope"]:
            return "qwen-plus"
        elif provider == "groq":
            return "llama-3.3-70b-versatile"
        elif provider == "ollama":
            return "qwen2.5:latest"
        elif provider == "openrouter":
            return "deepseek/deepseek-chat"
        return "demo"

    def is_configured(self) -> bool:
        if self.provider == "ollama":
            return True
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7) -> str:
        """
        Mengirim prompt ke provider LLM yang dipilih.
        Jika API key belum diisi, beralih secara cerdas ke High-Fidelity Simulation Mode.
        """
        if not self.is_configured():
            # Mode simulasi cerdas agar pengguna tetap bisa melihat demonstrasi aplikasi tanpa hambatan
            return self._generate_simulated_response(prompt, system_prompt)

        try:
            if self.provider == "openai":
                return self._call_openai(prompt, system_prompt, temperature)
            elif self.provider in ["gemini", "google"]:
                return self._call_gemini(prompt, system_prompt, temperature)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt, system_prompt, temperature)
            elif self.provider == "deepseek":
                return self._call_deepseek(prompt, system_prompt, temperature)
            elif self.provider in ["qwen", "dashscope"]:
                return self._call_qwen(prompt, system_prompt, temperature)
            elif self.provider == "groq":
                return self._call_groq(prompt, system_prompt, temperature)
            elif self.provider == "ollama":
                return self._call_ollama(prompt, system_prompt, temperature)
            elif self.provider == "openrouter":
                return self._call_openrouter(prompt, system_prompt, temperature)
            else:
                return self._generate_simulated_response(prompt, system_prompt)
        except Exception as e:
            # Jika API gagal (misal kuota habis atau koneksi terputus), beri pesan error informatif
            # dan berikan opsi fallback
            err_str = str(e)
            return (
                f"⚠️ **Peringatan Panggilan API ({self.provider.upper()})**: {err_str}\n\n"
                f"---\n"
                f"### [Mode Fallback Simulasi Diaktifkan Otomatis]\n\n"
                f"{self._generate_simulated_response(prompt, system_prompt)}"
            )

    def _call_openai(self, prompt: str, system_prompt: str, temperature: float) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model or "gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def _call_gemini(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Panggilan API Google Gemini dengan deteksi model teks dinamis dan timeout ketat 20 detik
        untuk mencegah terjadinya error 504 Deadline Exceeded dan error 400 response modalities (TTS).
        """
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)

        raw_model = (self.model or "gemini-2.0-flash").replace("models/", "").strip()

        # Pemetaan aman model eksperimental / invalid ke model teks resmi Google
        MODEL_ALIASES = {
            "gemini-3.8-flash": "gemini-2.0-flash",
            "gemini-3.5-flash": "gemini-2.0-flash",
            "gemini-2.5-flash": "gemini-2.0-flash",
            "gemini-2.5-flash-preview-tts": "gemini-2.0-flash",
            "gemini-2.5": "gemini-2.0-flash",
            "gemini-2.0": "gemini-2.0-flash",
            "gemini-1.5": "gemini-1.5-flash",
            "gemini-flash": "gemini-2.0-flash",
            "gemini-pro": "gemini-1.5-pro",
        }
        target_model = MODEL_ALIASES.get(raw_model.lower(), raw_model)

        # Kata kunci model non-teks yang WAJIB dibuang (model audio, suara, tts, gambar, embedding)
        NON_TEXT_KEYWORDS = ["tts", "audio", "image", "imagen", "embed", "embedding", "aqa", "vision-only", "robotics", "2.5"]

        # 1. Susun daftar kandidat model teks resmi Google secara eksplisit (UNCONDITIONAL)
        # Model ini dijamin 100% mendukung pembuatan teks (TEXT modality)
        candidates = []

        # Masukkan target model jika bukan model non-teks
        if target_model and not any(bad in target_model.lower() for bad in NON_TEXT_KEYWORDS):
            candidates.append(target_model)

        # Selalu tambahkan model teks standar Google yang aktif dan terbukti
        for std in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]:
            if std not in candidates:
                candidates.append(std)

        # 2. Coba deteksi model teks tambahan dari server Google jika ada
        try:
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    name_clean = m.name.replace("models/", "").strip()
                    # Filter KETAT: abaikan model TTS, audio, gambar, embedding
                    if any(bad in name_clean.lower() for bad in NON_TEXT_KEYWORDS):
                        continue
                    if name_clean not in candidates:
                        candidates.append(name_clean)
        except Exception:
            pass

        last_error = None

        # 3. Eksekusi cepat dengan timeout ketat 20 detik
        for cand in candidates:
            # Proteksi ganda: jangan pernah panggil model tts / audio
            if any(bad in cand.lower() for bad in NON_TEXT_KEYWORDS):
                continue
            try:
                model = genai.GenerativeModel(
                    model_name=cand,
                    system_instruction=system_prompt,
                    generation_config={"temperature": temperature}
                )
                response = model.generate_content(prompt, request_options={"timeout": 20.0})
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                # Jika error 400 (modalitas TTS) atau 404 (model tidak ada), langsung coba kandidat berikutnya
                continue

        # 4. Fallback ke OpenAI-compatible endpoint resmi Google
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=18.0
            )
            for cand in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                try:
                    response = client.chat.completions.create(
                        model=cand,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature
                    )
                    if response.choices and response.choices[0].message.content:
                        return response.choices[0].message.content
                except Exception:
                    continue
        except Exception:
            pass

        if last_error:
            err_msg = str(last_error)
            if "504" in err_msg or "Deadline Exceeded" in err_msg:
                raise TimeoutError("Server Google Gemini sedang padat trafik / timeout (504 Deadline Exceeded). Tip: Beralih ke provider Groq Cloud di sidebar (100% gratis & respon dalam 1 detik).")
            if "modalities" in err_msg or "tts" in err_msg.lower():
                raise ValueError("Kunci API yang dimasukkan tampaknya memiliki pembatasan Text-to-Speech (Audio) dari Google Cloud. Untuk membuat teks, pastikan membuat API Key gratis di https://aistudio.google.com (diawali AIzaSy...) atau gunakan Groq Cloud di sidebar.")
            raise last_error

        raise RuntimeError("Gagal terhubung ke Google Gemini. Silakan gunakan Groq Cloud di sidebar.")

    def _call_anthropic(self, prompt: str, system_prompt: str, temperature: float) -> str:
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model or "claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text or ""

    def _call_deepseek(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Integrasi DeepSeek API resmi (DeepSeek-V3 dan DeepSeek-R1).
        Menggunakan OpenAI-compatible protocol pada endpoint https://api.deepseek.com.
        """
        from openai import OpenAI
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url or "https://api.deepseek.com"
        )
        model_name = self.model or "deepseek-chat"
        # Untuk deepseek-reasoner (R1), beberapa konfigurasi menyarankan default temp
        kwargs = {}
        if model_name != "deepseek-reasoner":
            kwargs["temperature"] = temperature

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        return response.choices[0].message.content or ""

    def _call_qwen(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Integrasi Qwen (Tongyi Qianwen / Alibaba Cloud DashScope).
        Sangat unggul dalam pemahaman nuansa lokal dan multibahasa Asia.
        Menggunakan OpenAI-compatible protocol DashScope.
        """
        from openai import OpenAI
        base_url = self.base_url or os.getenv("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
        client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        response = client.chat.completions.create(
            model=self.model or "qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def _call_groq(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Integrasi Groq Cloud API (100% Gratis & Super Cepat via LPU).
        Menggunakan endpoint OpenAI-compatible https://api.groq.com/openai/v1.
        """
        from openai import OpenAI
        target_model = self.model or "llama-3.3-70b-versatile"
        # Auto-fallback jika ada model lama yang sudah di-decommission oleh Groq
        if any(bad in target_model.lower() for bad in ["mixtral", "llama-3.1-70b", "llama2", "gemma-7b"]):
            target_model = "llama-3.3-70b-versatile"

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def _call_ollama(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Integrasi Ollama Local LLM (100% Offline di komputer sendiri tanpa biaya internet / API).
        """
        from openai import OpenAI
        base_url = self.base_url or "http://localhost:11434/v1"
        client = OpenAI(
            api_key="ollama",
            base_url=base_url
        )
        response = client.chat.completions.create(
            model=self.model or "qwen2.5:latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def _call_openrouter(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Integrasi OpenRouter untuk akses universal model DeepSeek, Qwen, Llama, dll dengan 1 API key.
        """
        from openai import OpenAI
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        response = client.chat.completions.create(
            model=self.model or "deepseek/deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content or ""

    def _generate_simulated_response(self, prompt: str, system_prompt: str) -> str:
        """
        Menghasilkan output simulasi berkualitas tinggi berbasis masukan pengguna,
        sangat berguna untuk demo dan pengujian instan sebelum pengguna memasukkan API key.
        """
        p_lower = prompt.lower()

        # Deteksi modul berdasarkan isi prompt
        if "5 sudut pandang konten" in p_lower or "content gap" in p_lower or "trend radar" in p_lower:
            return self._mock_trend_radar(prompt)
        elif "reverse engineering" in p_lower or "transkrip" in p_lower or "steal like an artist" in p_lower:
            return self._mock_reverse_engineer(prompt)
        elif "10 variasi hook" in p_lower or "hook visual" in p_lower or "pilar psikologi" in p_lower:
            return self._mock_hook_generator(prompt)
        elif "tabel" in p_lower and ("skrip audio" in p_lower or "detik" in p_lower):
            return self._mock_storyboard(prompt)
        elif "monetization bridge" in p_lower or "closing bridge" in p_lower or "soft-selling" in p_lower:
            return self._mock_monetization_bridge(prompt)
        elif "caption" in p_lower or "hashtag" in p_lower:
            return self._mock_caption_hashtag(prompt)
        elif "7 hari" in p_lower or "sprint" in p_lower or "kalender" in p_lower:
            return self._mock_seven_day_sprint(prompt)
        else:
            return (
                "### Analisis ViralGenix AI Engine\n\n"
                "Sistem telah memproses parameter input Anda dengan formula retensi dan psikologi konversi.\n\n"
                "- **Status**: Berhasil dioptimasi dengan algoritma video pendek.\n"
                "- **Catatan**: Hubungkan API Key Anda di panel sidebar untuk hasil kustomisasi tanpa batas secara real-time."
            )

    def _mock_trend_radar(self, prompt: str) -> str:
        return """### 1. Ringkasan Sentimen & Gelombang Tren
- **Tren Mikro Meledak**: Pergeseran audiens dari konten teori dangkal ke format "No-BS Micro-Breakdown" & "Real Cost Transparency".
- **Trigger Kepanikan Audiens**: Ketakutan tertinggal teknologi baru dan kecemasan efisiensi di tengah tekanan persaingan tinggi.
- **Celah Kualitas Kompetitor**: Mayoritas kreator saat ini hanya membuat konten "lemas" yang kuat di hook sensasional namun tidak memberikan nama tools spesifik, tanpa angka empiris, dan tanpa langkah taktis nyata.
- **Tingkat Persaingan vs Potensi Viral**: Persaingan Rendah (3/10) | Potensi Viral Sangat Tinggi (9.4/10) untuk kreator yang berani menyajikan data empiris dan mekanisme konkret.

---

### 2. 5 Sudut Pandang Konten (Viral Content Angles) Unik & Berbobot Tinggi

#### 1. Angle Kontradiktif / Myth-Buster
- **Judul Konsep**: *"Berhenti Lakuin Cara Populer Ini: Data Menunjukkan Malah Bikin Boncos 42%"*
- **Trigger Emosi**: Rasa Takut Merugi (Loss Aversion) & Penasaran Logis.
- **Premis Cerita & Data Empiris**: Membongkar mitos umum di niche ini. Berdasarkan pengujian A/B test pada 100 sampel, metode konvensional justru membuang waktu 3.5 jam per hari dan menurunkan retensi audiens ke bawah 15%.
- **Estimasi Potensi Viral**: Sangat Tinggi (Memicu perdebatan sehat dan repost luas).

#### 2. Angle Rahasia Orang Dalam (Insider Secret)
- **Judul Konsep**: *"SOP Rahasia Praktisi Senior: Cukup Setting 2 Fitur Ini Buat Hasil 3x Lipat"*
- **Trigger Emosi**: Akses Eksklusif & Solusi Cerdas Efisiensi.
- **Premis Cerita & Data Empiris**: Mengungkap 1 tools/metode teknis gratisan yang biasa dirahasiakan agensi. Menjelaskan mekanisme kerja kausalitas mengapa settingan ini memangkas waktu kerja dari 4 jam menjadi 18 menit.
- **Estimasi Potensi Viral**: Tinggi (Bookmark & Save Rate di atas 20%).

#### 3. Angle Realita Pahit (Hard Truth)
- **Judul Konsep**: *"Alasan Jujur Kenapa 90% Orang Gagal di Sini (Bukan Salah Algoritma / Kurang Rajin)"*
- **Trigger Emosi**: Empati mendalam, Validasi Frustasi, lalu Pemahaman Sistemik.
- **Premis Cerita & Data Empiris**: Membedah anatomi akar masalah: kegagalan bukan karena kurang kerja keras, tapi karena rasio konversi yang bocor pada bottleneck pertama. Menyajikan perbandingan data sebelum vs sesudah perbaikan sistem.
- **Estimasi Potensi Viral**: Sangat Tinggi (Mendorong share ke komunitas senasib).

#### 4. Angle Hack Cepat (Low Effort High Result)
- **Judul Konsep**: *"Framework 3 Langkah Taktis yang Bisa Langsung Dipraktekkan Hari Ini (Hasil Terukur)"*
- **Trigger Emosi**: Keinginan Hasil Nyata Tanpa Penundaan.
- **Premis Cerita & Data Empiris**: Memberikan satu langkah taktis 'plug-and-play' tanpa perlu beli alat mahal. Formula ini terbukti menaikkan metrik performa sebesar 65% dalam 7 hari pengujian berturut-turut.
- **Estimasi Potensi Viral**: Sangat Tinggi (Komentar meminta template dan panduan).

#### 5. Angle Prediksi Masa Depan & Warning
- **Judul Konsep**: *"Tahun Ini Pola Lama Bakal Punah: 3 Antisipasi Wajib Berbasis Data Pasar"*
- **Trigger Emosi**: FOMO (Fear of Missing Out) & Urgensi Bertahan Hidup.
- **Premis Cerita & Data Empiris**: Mengungkap tren penurunan distribusi konten lemas/generik hingga 70% dan lonjakan 4x lipat pada konten bernilai tinggi (value-density) yang memiliki data empiris.
- **Estimasi Potensi Viral**: Tinggi.

---

### 3. Rekomendasi Format Video
- **Format Terbaik**: Talking head dinamis dengan b-roll split-screen data/metrik setiap 2.5 detik.
- **Sound / Audio Vibe**: Lo-fi investigatif atau tempo ritmis 115-125 BPM dengan ketukan tegas.
"""

    def _mock_reverse_engineer(self, prompt: str) -> str:
        return """### 1. Anatomi Pemicu Viralitas & Audit Kualitas Materi

- **Tipe Hook (0-3 Detik Pertama)**:
  * *Jenis Hook*: **High Stakes Warning + Data Anomaly**.
  * *Mekanisme*: Kreator langsung membuka dengan peringatan keras ("Jangan pernah lakukan X sebelum tahu angka ini") disertai gerakan memegang objek ke arah lensa. Refleks kejut (*startle response*) langsung menghentikan gerakan jempol penonton.

- **Pacing & Struktur Emosi**:
  * *Detik 0-08*: Panik & Penasaran (Membangun tensi bahwa ada ancaman tersembunyi).
  * *Detik 08-22*: Agitasi & Pembongkaran Akar Masalah (Mengapa cara lama gagal total).
  * *Detik 22-42*: The Mechanism (Menjelaskan kausalitas logis mengapa solusi alternatif ini bekerja).
  * *Detik 42-60*: Bukti Empiris & Call to Action halus yang memberikan solusi praktis.

- **Retention Trick (Jebakan Retensi)**:
  * Di detik ke-18 terdapat perpindahan angle kamera (*punch-in zoom*) disertai suara sfx *whoosh* dan penayangan screenshot grafik hasil uji coba yang membuat penonton fokus menyimak hingga tuntas.

- **Audit Kedalaman Materi (Substance Audit)**:
  * *Kelemahan Video Kompetitor*: Video aslinya sangat kuat di judul dan hook pembuka, namun pembahasannya di tengah agak "lemas" karena tidak menyebutkan nama tools secara spesifik dan tidak menyertakan langkah implementasi konkret bagi pemula.
  * *Celah Emas Anda*: Anda dapat mengungguli video ini 10x lipat dengan menyajikan data empiris riil dan 3 langkah checklist aksi langsung!

---

### 2. Formulasi "Steal Like an Artist" (3 Ide Konten Turunan 10x Lebih Berbobot & Empiris)

#### 💡 Ide 1: The Counter Angle (Bantahan Berbasis Data Empiris)
- **Headline / Hook**: *"Video viral kemarin ada yang keliru! Ini data uji coba asli kenapa cara itu bikin boncos 40%..."*
- **Kenapa Mengalahkan Aslinya**: Memanfaatkan audiens yang sudah menonton video kompetitor, lalu memberikan koreksi ilmiah/teknis berbasis data yang jauh lebih kredibel.
- **CTA**: *"Ketik 'DATA' di komentar, gue kirimkan file perbandingan lengkapnya gratis."*

#### 💡 Ide 2: The Deep-Dive Mechanism (Bongkar Mekanisme Solusi Asli)
- **Headline / Hook**: *"Ketinggalan penjelasan di video 2 juta views kemarin? Ini mekanisme rahasia yang gak sempat mereka jelasin!"*
- **Kenapa Mengalahkan Aslinya**: Menjelaskan MENGAPA trik itu berhasil dengan menyebutkan nama tools dan formula eksak tanpa istilah yang membingungkan.
- **CTA**: *"Save video ini biar lu gak lupa alur settingannya pas praktek nanti malam."*

#### 💡 Ide 3: The Step-by-Step Actionable Playbook
- **Headline / Hook**: *"Ini checklist 3 langkah persis yang langsung naikin hasilmu 3x lipat dalam waktu 24 jam!"*
- **Kenapa Mengalahkan Aslinya**: Langsung ke eksekusi taktis tanpa berputar-putar di teori.
- **CTA**: *"Template checklist praktisnya sudah gue taruh di link bio baris pertama."*
"""

    def _mock_hook_generator(self, prompt: str) -> str:
        return """### 10 Variasi Hook Berdaya Ledak Tinggi (3 Detik Pertama) & Berbobot Empiris

---

#### 🔴 Kategori 1: Ketakutan & Kerugian (Fear of Loss / FOMO)

**1. The Silent Bleed Hook (Kerugian Tersembunyi)**
- **Hook Verbal (Audio)**: *"Tiap bulan kamu boncos jutaan rupiah cuma karena langganan tools yang sebenarnya ada versi gratisnya!"*
- **Instruksi Visual**: Kamera zoom-in cepat ke wajah dengan ekspresi serius, tangan memegang dompet atau layar dashboard kosong.
- **Teks di Layar**: **STOP BONCOS JUTAAN! 💸**
- **Pijakan Fakta / Nilai Materi**: Membongkar pengeluaran rutin yang bisa dipangkas 100% menggunakan alternatif open-source atau metode manual.
- **Skor Retensi**: 96/100 (Otak manusia 2x lebih takut kehilangan daripada ingin mendapatkan sesuatu).

**2. The Impending Disaster Hook (Peringatan Tren Berbasis Data)**
- **Hook Verbal (Audio)**: *"Kalau format kontenmu masih teks rapat di 2024, retensinya bakal anjlok di bawah lima persen!"*
- **Instruksi Visual**: Tunjuk langsung ke arah lensa kamera dengan jarak dekat, latar belakang agak redup.
- **Teks di Layar**: **PERINGATAN KERAS! ⚠️**
- **Pijakan Fakta / Nilai Materi**: Algoritma media sosial terbaru mendowngrade konten dengan watch time rendah di bawah 3 detik.
- **Skor Retensi**: 93/100 (Memicu kecemasan status dan performa akun).

**3. The Cost of Inaction Hook (Anatomi Kesalahan Fatal)**
- **Hook Verbal (Audio)**: *"Ini kesalahan fatal yang bikin sembilan puluh persen pemula stuck dan churn rate-nya tembus enam puluh persen!"*
- **Instruksi Visual**: Gerakan kepala menggeleng pelan sambil menatap tajam ke kamera.
- **Teks di Layar**: **KENAPA KAMU MASIH STUCK? 📉**
- **Pijakan Fakta / Nilai Materi**: Menguak bottleneck konversi pertama yang sering diabaikan pemula.
- **Skor Retensi**: 91/100.

---

#### 🟡 Kategori 2: Keingintahuan Ekstrem (Curiosity Gap)

**4. The Hidden Loophole Hook (Celah Teknis Spesifik)**
- **Hook Verbal (Audio)**: *"Satu settingan rahasia di CapCut ini bikin ketajaman video naik dua kali lipat tanpa bikin bitrate bengkak."*
- **Instruksi Visual**: Kreator berbisik mendekat ke mikrofon clip-on dengan gestur misterius.
- **Teks di Layar**: **SETTINGAN RAHASIA 4K 🤫**
- **Pijakan Fakta / Nilai Materi**: Rasio kompresi bitrate vs codec H.264/HEVC untuk upload TikTok/Reels tanpa blur.
- **Skor Retensi**: 97/100 (Paling memicu klik dan retensi 10 detik pertama).

**5. The Weirdly Effective Trick Hook (Anomali Ilmiah / Praktis)**
- **Hook Verbal (Audio)**: *"Trik jeda enam puluh detik setelah cuci muka terbukti kunci kelembaban kulit dan cegah dehidrasi seharian."*
- **Instruksi Visual**: Tunjukkan benda sehari-hari atau layar smartphone dengan grafik melonjak tajam.
- **Teks di Layar**: **ANEH TAPI TERBUKTI! 💧**
- **Pijakan Fakta / Nilai Materi**: Mekanisme transepidermal water loss (TEWL) pada lapisan stratum corneum.
- **Skor Retensi**: 94/100 (Kombinasi paradoks & penjelasan kausalitas ilmiah).

**6. The Forbidden Knowledge Hook (Bocoran Standar Industri)**
- **Hook Verbal (Audio)**: *"Bocoran SOP agensi: ini alasan kenapa video durasi lima puluh detik punya retention rate tertinggi di algoritma!"*
- **Instruksi Visual**: Menoleh ke kanan dan kiri seolah-olah sedang mengawasi ruangan sekitar.
- **Teks di Layar**: **BOCORAN SOP AGENSI! 📑**
- **Pijakan Fakta / Nilai Materi**: Analisis data watch-through rate TikTok yang memprioritaskan completion rate video 45-60 detik.
- **Skor Retensi**: 95/100 (Sensasi urgensi dan konten eksklusif).

---

#### 🟢 Kategori 3: Keuntungan Maksimal & Kemudahan (High Gain / Greed)

**7. The Effortless Multiplier Hook (Efisiensi Waktu Terukur)**
- **Hook Verbal (Audio)**: *"Gimana cara pangkas waktu riset konten dari empat jam jadi lima belas menit pakai framework ini?"*
- **Instruksi Visual**: Tangan mengetik santai di keyboard atau menunjukkan stopwatch di smartphone.
- **Teks di Layar**: **DARI 4 JAM JADI 15 MENIT ⏱️**
- **Pijakan Fakta / Nilai Materi**: Penggunaan Content Matrix & AI Automation pipeline terstruktur.
- **Skor Retensi**: 92/100 (Sangat menarik untuk profesional & kreator yang sibuk).

**8. The Zero Capital Blueprint Hook (Formula Modal HP)**
- **Hook Verbal (Audio)**: *"Modal nol rupiah: cukup pakai microphone bawaan HP dan pencahayaan jendela jam sembilan pagi!"*
- **Instruksi Visual**: B-Roll suasana kamar rapi dan setup HP sederhana menghadap jendela alami.
- **Teks di Layar**: **MODAL 0 RUPIAH BISA! 🎙️**
- **Pijakan Fakta / Nilai Materi**: Pemanfaatan natural daylight 5500K dan setting gain audio tanpa beli lighting mahal.
- **Skor Retensi**: 91/100.

---

#### 🟣 Kategori 4: Validasi & Empati (Identity / Relatability)

**9. The Exhausted Strivers Hook (Empati Validasi Nyata)**
- **Hook Verbal (Audio)**: *"Capek bikin konten tiap hari tapi mentok di dua ratus views? Masalahnya bukan di algoritma lho."*
- **Instruksi Visual**: Menghembuskan nafas panjang, menyandarkan punggung di kursi sambil tersenyum hangat.
- **Teks di Layar**: **GUE TAU PERASAAN LO... ☕**
- **Pijakan Fakta / Nilai Materi**: Analisis data 200-view jail yang disebabkan oleh drop-off detik ke-2, bukan shadowban.
- **Skor Retensi**: 95/100 (Membangun ikatan emosional instan tanpa jarak).

**10. The Unfair Reality Hook (Bongkar Paradigma Usang)**
- **Hook Verbal (Audio)**: *"Bukan kamu yang gak bakat, tapi formula hook tiga detik pertama yang kamu pakai emang udah basi."*
- **Instruksi Visual**: Menatap kamera dengan tatapan pengertian dan gestur membuka telapak tangan.
- **Teks di Layar**: **BUKAN SALAH LO! 💡**
- **Pijakan Fakta / Nilai Materi**: Pergeseran psikologi audiens dari clickbait generik ke high-density value.
- **Skor Retensi**: 93/100 (Menghilangkan rasa bersalah dan memusatkan energi ke perbaikan strategi).
"""

    def _mock_storyboard(self, prompt: str) -> str:
        p_lower = prompt.lower()

        # Ekstraksi hook dan topik dari prompt jika ada
        import re
        hook_m = re.search(r'\[HOOK UTAMA\]:\s*([^\n]+)', prompt)
        topic_m = re.search(r'\[TOPIK KONTEN\]:\s*([^\n]+)', prompt)
        hook_val = hook_m.group(1).strip() if hook_m else "Stop lakuin cara ini kalau kamu gak mau rugi waktu dan duit sia-sia!"
        topic_val = topic_m.group(1).strip() if topic_m else "Tips & Trik Taktis Optimasi Konten"

        # Deteksi Target Jumlah Scene Berdasarkan Durasi Video atau Kedalaman Topik
        if any(k in p_lower for k in ["90 - 120", "8 - 12 scene", "8 - 10 scene", "deep-dive", "masterclass", "120 detik"]):
            target_scene_count = 10
        elif any(k in p_lower for k in ["75 - 90", "7 - 8 scene", "6 - 8 scene", "multi-poin", "90 detik"]):
            target_scene_count = 8
        elif any(k in p_lower for k in ["30 - 45", "3 - 4 scene", "fast paced", "fast-paced", "ringkas", "30 detik", "45 detik"]):
            target_scene_count = 4
        elif any(k in p_lower for k in ["60 detik", "5 - 6 scene", "standar"]):
            target_scene_count = 6
        else:
            # Mode Otomatis Fleksibel: Analisis kedalaman materi dari kata kunci topik & instruksi
            deep_kws = ["langkah", "cara", "tutorial", "panduan", "framework", "studi kasus", "deep", "metode", "lengkap", "tahap", "sistem", "strategi", "rahasia", "step", "guide", "mastery"]
            deep_score = sum(1 for kw in deep_kws if kw in p_lower)
            if deep_score >= 2:
                target_scene_count = 8
            elif any(kw in p_lower for kw in ["cepat", "singkat", "hack", "simple", "ringkas"]):
                target_scene_count = 4
            else:
                target_scene_count = 6

        # Indeks scene yang dipilih berdasarkan durasi (membentuk struktur narasi logis & utuh)
        if target_scene_count == 4:
            selected_indices = [0, 2, 7, 9]
        elif target_scene_count == 6:
            selected_indices = [0, 1, 2, 3, 7, 9]
        elif target_scene_count == 8:
            selected_indices = [0, 1, 2, 3, 4, 6, 7, 9]
        else:
            selected_indices = list(range(10))

        # Tentukan Niche, Dialogues Berbobot Empiris & Master Anchor Kontekstual (10-Scene Pool)
        if any(k in p_lower for k in ["masak", "resep", "kuliner", "makanan", "minuman", "dapur", "kue", "food"]):
            theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
            aud = "Pecinta kuliner, ibu rumah tangga, dan anak kost yang hobi masak simpel"
            slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
            emotion = "👀 Rasa Penasaran Ekstrem & Aha! Moment Kuliner"
            vis_style = "Live Action UGC 4K Food-Grade (Macro Close-Up)"
            char_anchor = "Wanita muda usia 24-28 tahun, rambut diikat rapi, celemek linen abu-abu, ekspresi ramah & hangat"
            env_anchor = "Dapur Rumah Minimalis Bersih & Estetik (Natural Morning Light & Marmer Putih)"
            color_anchor = "Warm Delicious Food Grade (Vibrant Saturation & Fresh Contrast)"
            voice_anchor = "Santai, bersahabat, tempo bicara riang 130 WPM, intonasi menggugah selera"
            all_dialogues = [
                "Stop buang tangkai daun bawang, ini rahasia kaldu gurih alami restoran bintang lima!",
                "Sebagian besar orang langsung buang bagian ini ke tong sampah karena dikira keras, akhirnya kaldu masakan lu hambar dan boros micin sintetis.",
                "Padahal asam amino glutamat alami tertinggi ngumpul di serat tangkai—cukup rebus bareng air dingin di suhu delapan puluh derajat Celsius.",
                "Uji rasa membuktikan intensitas gurihnya naik empat puluh persen, hemat micin sintetis sampai tujuh puluh persen.",
                "Teknik shock termal: celupkan tangkai ke air es sepuluh detik sebelum direbus untuk kunci klorofil aromatik.",
                "Gunakan rasio emas: seratus gram tangkai daun bawang untuk setiap satu liter air kaldu dasar.",
                "Kombinasikan dengan dua butir lada putih utuh yang digeprek kasar untuk memicu aroma gurih sedap.",
                "Simpan sisa potongan di wadah kedap udara dalam freezer, tahan tiga bulan dan siap cemplung kapan saja.",
                "Hindari merebus hingga mendidih bergolak keras di atas seratus derajat agar kaldu tidak terasa getir.",
                "Resep takaran lengkap sop bintang lima sudah aku rangkum di caption, langsung save video ini sekarang!"
            ]
            all_scene_labels = [
                ("The Hook (Scroll-Stopper Kuliner)", "Zoom-in cepat ke potongan tangkai daun bawang di talenan", "SFX: Rapid Whoosh + Crisp Knife Chop", "Pola Kejut & Relevansi Dapur"),
                ("The Curiosity Lock & Agitation (Jebakan Buang Tangkai)", "Cut ke B-Roll tempat sampah dan close-up kuah sup bening hambar", "SFX: Low Sub Swoosh + Dull Hit", "Validasi Frustrasi & Stakes"),
                ("The Mechanism (Ekstraksi Umami Suhu 80°C)", "Medium shot panci stainless steel kuah bening perlahan beruap di atas kompor", "SFX: Gentle Water Simmer / Bubble", "Aha! Moment Kausalitas Fisik"),
                ("Proof & Demonstration (Uji Rasa & Metrik 40%)", "Close-up sendok sup bening diseruput hangat, ekspresi puas tersenyum", "SFX: Satisfying Rich Chime", "Bukti Empiris & Kelezatan"),
                ("Step 1: Shock Termal Air Es", "POV tangan mencelupkan tangkai segar ke mangkuk kaca berisi air es batu", "SFX: Ice Clink & Splash", "Teknik Rahasia Chef"),
                ("Step 2: Rasio Emas 100g per 1 Liter", "Timbangan digital menakar 100 gram tangkai lalu dimasukkan ke panci 1 liter", "SFX: Digital Scale Beep", "Presisi Takaran Empiris"),
                ("Step 3: Lada Putih Geprek Aromatik", "Tangan menggeprek 2 butir lada putih dengan pisau koki di atas talenan kayu", "SFX: Solid Board Thud", "Penguat Aroma Alami"),
                ("Actionable Value Bomb (Freezer Storage Rule)", "POV tangan memasukkan wadah kedap udara berlabel ke dalam freezer", "SFX: Smooth Click / Riser", "Langkah Taktis Langsung Eksekusi"),
                ("Kesalahan Fatal Dihindari (Suhu > 100°C)", "B-Roll panci bergolak keras diberi tanda silang merah peringatan", "SFX: Warning Muted Buzzer", "Anti-Gagal Edukasi"),
                ("Organic Conversion (Resep Takaran Sop Lengkap)", "Talent menatap kamera tersenyum hangat, menunjuk ramah ke caption bawah", "SFX: Clean Bell Chime", "Organic Soft-CTA")
            ]
        elif any(k in p_lower for k in ["ai", "tech", "coding", "software", "gadget", "hp", "prompt", "komputer"]):
            theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
            aud = "Tech enthusiast, freelancer & content creator yang ingin efisiensi 10x"
            slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
            emotion = "🤯 Mind-Blown / Kaget (Membongkar Rahasia yang Tidak Disangka)"
            vis_style = "Live Action Tech Desk UGC 4K (Dinamis Punch-In)"
            char_anchor = "Pria/Wanita muda 22-29 tahun, kaos polos hitam oversized, kacamata anti-radiasi, tatapan percaya diri"
            env_anchor = "Desk Setup Gadget & Ambient Neon Light (Tech Minimalist Dark)"
            color_anchor = "Clean High-Key SaaS & Tech (Bright Natural, Cool Blue Accent)"
            voice_anchor = "Punchy, percaya diri, artikulasi renyah, tempo 135 WPM"
            all_dialogues = [
                "Stop bikin prompt panjang lebar, trik ini bikin respon AI sepuluh kali lebih cerdas!",
                "Lu pasti sering ngetik prompt tiga paragraf panjang, tapi responnya tetep ngaco dan halusinasi, bikin waktu lu kebuang dua jam sia-sia.",
                "Masalahnya bukan di AI-nya, tapi context window yang tercemar—solusinya pakai teknik Few-Shot Formatting dengan dua contoh konkret.",
                "Data akurasi melonjak dari enam puluh persen ke sembilan puluh lima persen, selesai dalam dua menit.",
                "Terapkan Negative Constraints: instruksikan AI melarang kata klise seperti 'menyelami', 'krusial', atau 'game-changer'.",
                "Pasang Role-Prompting Anchor dengan spesifikasi otoritas: posisikan AI sebagai Chief Editor berpengalaman sepuluh tahun.",
                "Paksa Chain-of-Thought: wajibkan AI menuliskan langkah penalaran logis sebelum memunculkan jawaban akhir.",
                "Cukup tambahkan kalimat ini di baris pertama: 'Gunakan kerangka berpikir step-by-step sebelum menyimpulkan jawaban'.",
                "Kunci output dengan format Markdown terstruktur lima kolom agar langsung siap diimpor ke spreadsheet.",
                "Template formula prompt Few-Shot siap copas sudah ada di link bio nomor satu, download sekarang juga!"
            ]
            all_scene_labels = [
                ("The Hook (Scroll-Stopper AI)", "Rapid punch-in 1.2x ke layar monitor berisi baris prompt dan ekspresi talent", "SFX: Fast Digital Glitch + Bass Hit", "Curiosity Gap & Efisiensi 10x"),
                ("The Curiosity Lock & Agitation (Halusinasi & Waktu Terbuang)", "Cut ke B-Roll monitor menyorot teks merah error dan ekspresi frustrasi talent", "SFX: Warning Drone + Vinyl Stop", "Validasi Frustrasi & Stakes"),
                ("The Mechanism (Few-Shot Formatting Framework)", "Split screen: jendela prompt terstruktur rapi dengan contoh input-output Markdown", "SFX: Clean Keyboard Clack + Ding", "The Mechanism & Solusi Logis"),
                ("Proof & Demonstration (Metrik Akurasi 95%)", "Layar monitor menampilkan grafik benchmarking dari 60% melonjak ke 95%", "SFX: High-Tech UI Sweep", "Bukti Data Empiris Terukur"),
                ("Step 1: Negative Constraints Anti-Klise", "Layar monitor menyorot baris instruksi larangan kata klise diblok highlight kuning", "SFX: Fast Typing Rhythm", "Eliminasi Halusinasi"),
                ("Step 2: Role-Prompting Anchor Otoritas", "Animasi UI badge 'Chief Editor 10+ Yrs Exp' disematkan ke avatar AI", "SFX: Digital Lock Click", "Otoritas & Kedalaman Output"),
                ("Step 3: Chain-of-Thought Reasoning", "Layar memperlihatkan AI menulis penalaran premis sebelum merangkum poin utama", "SFX: Smooth Synth Rise", "Logika Kausalitas Matang"),
                ("Actionable Value Bomb (Aturan Satu Kalimat Ajaib)", "Close-up wajah talent menatap lensa, gestur tangan mempertegas satu kalimat kunci", "SFX: Smooth UI Pop", "Free Taktis Value Bomb"),
                ("Step 4: Format Constraint 5 Kolom", "Layar monitor menampilkan tabel Markdown 5 kolom rapi yang terisi otomatis", "SFX: Crisp Table Snap", "Efisiensi Siap Pakai"),
                ("Organic Conversion (Template Siap Copas di Bio)", "Talent menunjuk santai ke arah pojok bio profil di layar HP", "SFX: Subtle Notification Ding", "Direct Action Organic Bridge")
            ]
        elif any(k in p_lower for k in ["skincare", "jerawat", "kulit", "glowing", "makeup", "beauty", "cantik"]):
            theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
            aud = "Wanita 18-32 tahun yang ingin kulit glowing sehat tanpa ketergantungan krim racikan"
            slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
            emotion = "👀 Rasa Penasaran Ekstrem & Kelegaan Solutif Kulit"
            vis_style = "Live Action Clean High-Key 4K (Macro Skin Texture)"
            char_anchor = "Wanita 20-27 tahun, kulit wajah bersih terawat, bando kain putih, ekspresi empati tulus"
            env_anchor = "Vanity Mirror Kamar Mandi Estetik Marmer Putih (Clean Bright Ring Light)"
            color_anchor = "Pastel Clean Skin-Tone Glow (Soft Warm White, Natural Rosy)"
            voice_anchor = "Empatik, ramah, artikulasi jelas, tempo mengalir luwes 128 WPM"
            all_dialogues = [
                "Stop pakai Niacinamide konsentrasi tinggi kalau kulitmu malah bruntusan dan makin memerah!",
                "Banyak orang kemakan tren mikir makin tinggi persentasenya makin cepet glowing, padahal kadar sepuluh persen justru memicu histamin yang merusak skin barrier lu sampai bruntusan parah.",
                "Jurnal dermatologi membuktikan kadar optimal itu cuma dua sampai empat persen—ini kunci turunin sebum empat puluh persen tanpa iritasi.",
                "Kadar empat persen terbukti klinis menurunkan sebum empat puluh persen dalam dua minggu tanpa iritasi sama sekali.",
                "Lapiskan dengan Hyaluronic Acid berkadar rendah untuk meningkatkan hidrasi transepidermal hingga enam puluh lima persen.",
                "Pastikan formula produk berada di rentang pH netral lima koma lima sampai enam koma lima agar tidak merusak asam alami kulit.",
                "Segel kelembaban dengan Ceramide tipe NP dan Phytosphingosine untuk memperkuat dinding pelindung kulit.",
                "Triknya: aplikasikan di kulit setengah lembab, tunggu enam puluh detik, baru kunci pakai moisturizer Ceramide.",
                "Hindari pemakaian berbarengan di telapak tangan dengan Vitamin C L-Ascorbic Acid berkadar asam tinggi.",
                "Daftar serum berkadar empat persen yang lulus uji lab ada di bio, cek sebelum belanja!"
            ]
            all_scene_labels = [
                ("The Hook (Scroll-Stopper Skincare)", "Macro zoom-in ke tekstur kulit wajah dan botol pipet serum", "SFX: Reverse Riser + Soft Drop", "Loss Aversion & Validasi Panik"),
                ("The Curiosity Lock & Agitation (Jebakan Persentase & Histamin)", "Cut ke B-Roll botol 10% dan makro kulit kemerahan meradang", "SFX: Warning Sub Resonance", "Bongkar Mitos & Validasi Kerusakan"),
                ("The Mechanism (Golden Ratio Dermatologi 2-4%)", "Visual animasi mikro 3D molekul aktif meresap seimbang di lapisan epidermis kulit", "SFX: Deep Clean Swoosh", "Aha! Moment Kausalitas Biologis"),
                ("Proof & Demonstration (Penurunan Sebum 40% Klinis)", "Split screen makro pori-pori hari ke-1 vs hari ke-14 tampak tenang dan halus", "SFX: Fresh Water Droplet Chime", "Bukti Klinis Terukur"),
                ("Step 1: Synergistic Hyaluronic Layering", "B-Roll tetesan bening Hyaluronic Acid meresap lembut di permukaan pipi", "SFX: Soft Liquid ASMR", "Sinergi Bahan Aktif"),
                ("Step 2: Cek pH Netral 5.5 - 6.5", "POV kertas uji pH menunjukkan warna hijau kekuningan netral 6.0 aman kulit", "SFX: Clean Paper Tap", "Validasi Laboratorium"),
                ("Step 3: Ceramide NP Barrier Seal", "Close-up tekstur krim moisturizer putih lembut diratakan tipis di punggung tangan", "SFX: Gentle Cream Swirl", "Proteksi Dinding Kulit"),
                ("Actionable Value Bomb (Golden Rule Jeda 60 Detik)", "Talent menepuk lembut pipi di depan cermin, mengoleskan pelembab ceramide", "SFX: Gentle ASMR Skincare Tap", "Free Tactical Step"),
                ("Kesalahan Fatal (Campur Asam Tinggi)", "B-Roll dua botol serum disilangkan tanda peringatan stop", "SFX: Warning Low Drone", "Anti-Iritasi Rule"),
                ("Organic Conversion (Kurasi Serum Lulus Lab Bio)", "Talent tersenyum ramah menunjuk ke arah bio profil dengan jemari rapi", "SFX: Sweet Harp Glissando", "Jembatan Konversi Halus")
            ]
        elif any(k in p_lower for k in ["otomotif", "motor", "mobil", "bengkel", "mesin", "modifikasi"]):
            theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
            aud = "Pria 20-45 tahun penghobi otomotif & pemilik kendaraan harian"
            slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
            emotion = "😱 FOMO & Ketakutan Rusak (Loss Aversion Mesin)"
            vis_style = "Cinematic Urban Garage 4K (Low Angle & Engine Macro)"
            char_anchor = "Pria 25-35 tahun, polo shirt gelap sporty, jam tangan outdoor, ekspresi tegas berwibawa"
            env_anchor = "Garasi Modern dengan Tool Rack Rapi & Pencahayaan Neon Cool White"
            color_anchor = "Industrial Urban Contrast (Deep Metallic Grey, Warm Orange Fill)"
            voice_anchor = "Tegas, maskulin, berwibawa, tempo tenang tapi berenergi 130 WPM"
            all_dialogues = [
                "Bunyi mendecit di ruang mesin pas starter pagi jangan disemprot minyak rem kalau gak mau putus!",
                "Banyak pemilik mobil nekat semprot pelumas atau minyak rem biar bunyi mendecitnya hilang instan, padahal cairan kimia itu bikin karet melar dan siap putus mendadak di jalan tol.",
                "Biang kerok aslinya bukan kurang licin, tapi tegangan belt kendor—lu cuma butuh ukur defleksi sepuluh milimeter dan setel baut adjuster-nya.",
                "Cukup ukur defleksi tali kipas: kalau ditekan jempol amblas lebih dari sepuluh milimeter, wajib kencangkan baut adjuster.",
                "Gunakan kunci ring dua belas untuk menyetel baut adjuster dengan torsi presisi dua puluh lima Newton meter.",
                "Periksa keselarasan alur pulley kruk as dan alternator menggunakan penggaris baja agar belt tidak aus sebelah.",
                "Dengarkan menggunakan stetoskop mekanik untuk memastikan suara bukan berasal dari lahar bearing alternator yang aus.",
                "Pertolongan pertama darurat: semprotkan silicon spray khusus karet, suaranya langsung hilang total tanpa merusak serat tali.",
                "Ganti fan belt baru setiap empat puluh ribu kilometer dan selalu pilih material berbahan karet sintetis EPDM tahan panas.",
                "Simpan video ini sekarang di bookmark ponselmu, biar gak panik pas mobil mendadak bunyi di jalan!"
            ]
            all_scene_labels = [
                ("The Hook (Scroll-Stopper Otomotif)", "Kamera low-angle menyorot kap mesin terbuka, lampu kerja menyorot fan belt", "SFX: High-Pitched Belt Squeak + Fast Cut", "Bahaya & Peringatan Darurat"),
                ("The Curiosity Lock & Agitation (Jebakan Semprot Pelumas)", "Cut ke B-Roll makro karet fan belt melar getas akibat cairan kimia", "SFX: Metallic Warning Swoosh", "Bongkar Kesalahan Fatal & Bahaya Tol"),
                ("The Mechanism (Defleksi 10mm & Baut Adjuster)", "POV tangan menekan belt dengan penggaris milimeter presisi", "SFX: Solid Mechanical Click", "The Mechanism & Standar Pabrik"),
                ("Proof & Demonstration (Metrik Defleksi 10mm Jempol)", "POV tangan menekan tali kipas dengan penggaris milimeter presisi", "SFX: Solid Mechanical Click", "Ukur Empiris Standar Pabrik"),
                ("Step 1: Setel Baut Adjuster Torsi 25 Nm", "POV mekanik memutar baut setelan alternator dengan kunci ring secara presisi", "SFX: Ratchet Click Sound", "Prosedur Bengkel Profesional"),
                ("Step 2: Cek Keselarasan Pulley Alignment", "Penggaris baja ditempelkan di bibir pulley untuk mengecek kelurusan bidang", "SFX: Metal Glide Clink", "Cegah Aus Asimetris"),
                ("Step 3: Diagnostik Bearing vs Belt", "Mekanik menempelkan ujung stetoskop ke rumah alternator sambil menyimak", "SFX: Muted Resonance Hum", "Deteksi Dini Kerusakan"),
                ("Actionable Value Bomb (Pertolongan Darurat Silicon Spray)", "Talent menyemprotkan silicon spray karet ke pulley dengan presisi", "SFX: Crisp Aerosol Spray Sound", "Trik Taktis Bebas Boncos"),
                ("Aturan Penggantian Berkala (EPDM 40.000 Km)", "B-Roll kemasan fan belt baru bertuliskan kode EPDM premium", "SFX: Solid Snap Tone", "Preventive Maintenance"),
                ("Organic Conversion (Bookmark Video di Ponsel)", "Talent menutup kap mesin mantap, tersenyum tegas ke kamera menunjuk bookmark", "SFX: Firm Hood Thud + Tone", "Save Rate Booster")
            ]
        else:
            # Default Business, Career, Creator, or General Niche
            theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
            aud = "Pekerja kantoran, pemula bisnis & kreator konten usia 22-35 tahun"
            slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
            emotion = "😱 FOMO & Dorongan Pertumbuhan Finansial Nyata"
            vis_style = "Live Action UGC Sinematik 4K (Dinamis Punch-In)"
            char_anchor = "Kreator muda usia 24-30 tahun, kemeja kasual rapi, tatapan mata fokus ke lensa, ekspresi meyakinkan"
            env_anchor = "Coworking Space Modern dengan Tanaman Indoor & Warm Ambient Fill Light"
            color_anchor = "Moody Teal & Warm Orange Sinematik (Hollywood Blockbuster Look)"
            voice_anchor = "Santai tapi tegas, penuh keyakinan, artikulasi padat 132 WPM"
            
            # Gunakan hook kustom jika ada dan panjangnya rasional, jika tidak gunakan hook default empiris
            hook_custom_clean = hook_val if (hook_val and len(hook_val.split()) <= 20) else "Stop bakar budget iklan kalau checkout conversion rate di landing page kamu masih di bawah satu persen!"
            all_dialogues = [
                hook_custom_clean,
                "Lu udah bakar budget jutaan buat iklan tapi nol penjualan karena penonton langsung kabur begitu lihat form checkout yang ruwet dan bikin ragu.",
                "Kuncinya bukan gonta-ganti materi iklan, tapi hilangkan gesekan pakai psikologi Risk-Reversal Offer dan ringkas formulir jadi dua kolom saja.",
                "Split-test membuktikan checkout rate melonjak dari satu koma dua persen menjadi tiga koma delapan persen dalam empat hari.",
                "Pasang tiga testimoni spesifik lengkap dengan foto profil asli tepat di bawah tombol utama checkout.",
                "Pecah formulir pembelian menjadi dua tahap micro-commitment: nama dan WhatsApp di langkah pertama, pembayaran di langkah kedua.",
                "Sematkan indikator stok terbatas riil untuk mengurangi penundaan pembeli tanpa manipulasi timer palsu.",
                "Cek sekarang juga: pangkas field alamat lengkap menjadi kode pos otomatis, tingkat drop-off langsung turun tiga puluh persen.",
                "Tawarkan satu produk pelengkap berdiskon khusus di halaman konfirmasi order untuk menaikkan Average Order Value dua puluh lima persen.",
                "Checklist lengkap optimasi landing page konversi tinggi sudah gue share di link profil, ambil sekarang selagi free!"
            ]
            all_scene_labels = [
                ("The Hook (Scroll-Stopper Bisnis)", "Punch-in cepat 1.2x ke layar dashboard analitik grafik merah menukik", "SFX: Warning Siren Beat + Bass Drop", "Loss Aversion & Financial Alert"),
                ("The Curiosity Lock & Agitation (Bakar Budget & Checkout Bounce)", "B-Roll layar formulir checkout ruwet dengan kursor ragu-ragu lalu keluar (bounce)", "SFX: Disappointed Low Tone + Warning Beat", "Validasi Frustrasi & Boncos Finansial"),
                ("The Mechanism (Risk-Reversal & Form 2 Kolom)", "Medium shot talent memegang tablet memperlihatkan rancangan landing page minimalis", "SFX: Clean Swipe UI Pop", "The Mechanism Penawaran Menang"),
                ("Proof & Demonstration (Split-Test 1.2% ke 3.8%)", "Layar monitor menyorot grafik split-test A/B warna hijau melesat tinggi", "SFX: Ascending Success Chime", "Bukti Metrik Empiris Nyata"),
                ("Step 1: Testimoni Otentik Bawah CTA", "Layar monitor memperlihatkan 3 kartu review pelanggan dengan bintang 5 dan foto", "SFX: Clean Pop Chime", "Social Proof Validation"),
                ("Step 2: 2-Step Micro-Commitment", "POV animasi checkout berpindah mulus dari Step 1 ke Step 2 tanpa reload", "SFX: Smooth Slide Transition", "Psikologi Komitmen Kecil"),
                ("Step 3: Real Scarcity Indicator", "Kursor menyorot badge 'Tersisa 4 Akses Hari Ini' dengan warna merah elegan", "SFX: Subtle Digital Tick", "Anti-Penundaan Keputusan"),
                ("Actionable Value Bomb (Pangkas Field Kode Pos Otomatis)", "POV layar HP menunjukkan checkout 10 detik dengan auto-fill kode pos", "SFX: Snappy Tock Click", "Aturan Taktis Langsung Eksekusi"),
                ("Step 4: Post-Purchase One-Click Upsell", "Layar konfirmasi menampilkan kotak centang add-on khusus hemat 30%", "SFX: Cash Register Ding", "Maksimalisasi Revenue"),
                ("Organic Conversion (Checklist Landing Page Free)", "Talent tersenyum mantap menatap lensa, menunjuk ke tautan di bio profil", "SFX: Gentle Success Bell", "Organic Soft-CTA")
            ]

        # Filter scenes sesuai target_scene_count
        dialogues = [all_dialogues[idx] for idx in selected_indices]
        scene_labels = [all_scene_labels[idx] for idx in selected_indices]

        # Hitung durasi dan timeline kumulatif berkesinambungan secara matematis
        timings = []
        cur_sec = 0
        for d in dialogues:
            wc = len(d.split())
            dur = max(4, min(14, round(wc / 1.9) + 1))
            timings.append((cur_sec, cur_sec + dur, dur, wc))
            cur_sec += dur

        table_rows = []
        for i, (start_s, end_s, dur_s, wc) in enumerate(timings):
            s_label, broll_dir, sfx_item, psych = scene_labels[i]
            # Format waktu: jika total durasi melebihi 60 detik, gunakan MM:SS - MM:SS yang elegan
            if cur_sec > 60:
                time_col = f"**{start_s // 60:02d}:{start_s % 60:02d} - {end_s // 60:02d}:{end_s % 60:02d}**"
            else:
                time_col = f"**{start_s:02d} - {end_s:02d}**"
            table_rows.append(
                f"| {time_col} | {broll_dir} | \"{dialogues[i]}\" | {sfx_item} | {psych} |"
            )
        table_md = "\n".join(table_rows)

        scene_blocks = []
        for i, (start_s, end_s, dur_s, wc) in enumerate(timings):
            s_num = i + 1
            s_title, broll_act, sfx_val, psych_val = scene_labels[i]
            est_speech = round(wc / 1.9, 1)
            from utils.export_helpers import build_pro_ai_video_prompt
            prompt_ai = build_pro_ai_video_prompt(
                base_prompt="",
                niche_or_topic=f"{theme} {env_anchor} {broll_act}",
                scene_num=s_num,
                visual_dir=f"{char_anchor}, {broll_act}",
                env=env_anchor,
                color=color_anchor
            )
            
            block = f"""### 🎬 SCENE {s_num} [{start_s // 60:02d}:{start_s % 60:02d} - {end_s // 60:02d}:{end_s % 60:02d}]: {s_title}
- **⏱️ Durasi**: {dur_s} Detik (Detik {start_s} s/d {end_s}, Sinkron Dialog ~{est_speech}s)
- **🎨 Tipe Visual**: {vis_style}
- **🏞️ Setting Lokasi**: {env_anchor}
- **🎨 Color Grading**: {color_anchor}
- **🗣️ Voice Style**: {voice_anchor}
- **🎭 Delivery & Level Energi Talent**: Energi {9 if s_num == 1 else 8.5}/10, tatapan mata mengunci penonton langsung ke lensa kamera, artikulasi tegas bernas
- **🎯 Relevansi Audiens & Diksi**: Pilihan kata kontekstual mengikat persona audiens dengan pembuktian empiris nyata
- **🎥 Visual & Kamera**: {broll_act}
- **🎙️ Dialog Audio (Word for Word)**: {dialogues[i]}
- **🎞️ B-Roll & Aset Visual**: Footage kontekstual pendukung materi scene
- **🔊 SFX & Transisi**: {sfx_val}
- **🎯 Catatan Editor & Pacing**: Potong jeda hening (zero dead-air), ketukan transisi sinkron dengan SFX beat
- **🔑 Prompt AI Video/Image (English)**: {prompt_ai}"""
            scene_blocks.append(block)

        scenes_md = "\n\n".join(scene_blocks)
        total_words = sum(wc for _, _, _, wc in timings)
        total_sec = timings[-1][1] if timings else 60

        return f"""### BAGIAN 0: MASTER PRODUCTION & AUDIENCE CONSISTENCY ANCHOR (KUNCI KONSISTENSI UTUH)
- **🎯 Pilar Tema Konten**: {theme}
- **👥 Target Audiens Persona**: {aud}
- **🗣️ Gaya Sapaan & Diksi**: {slang}
- **⚡ Trigger Emosi Dominan**: {emotion}
- **🧬 Master Visual Style Lock (English Prompt Prefix)**: {vis_style}, 9:16 vertical aspect ratio, shot on 35mm lens f/1.8, cinematic lighting, sharp focus, 8k uhd photorealistic
- **👤 Master Character / Subject Anchor**: {char_anchor}
- **🏞️ Master Environment Anchor**: {env_anchor}
- **🎨 Master Color Grading & Lighting Anchor**: {color_anchor}
- **🎙️ Master Voice Profile Anchor**: {voice_anchor}

### BAGIAN 1: TABEL STORYBOARD DETIK DEMI DETIK
| Detik | Visual / B-Roll Camera Direction | Skrip Audio (Word for Word - Sinkron Durasi) | Aset B-Roll & SFX | Pemicu Psikologis / Pacing |
|---|---|---|---|---|
{table_md}

### BAGIAN 2: LEMBAR KERJA PRODUKSI PER SCENE (SINKRON DURASI <= 15 DETIK & DIALOG MAKSIMAL 20-25 KATA)

{scenes_md}

### BAGIAN 3: REKOMENDASI TEKNIS & SOUND
- **Estimasi Jumlah Kata Audio Total**: ~{total_words} kata ({total_sec} Detik total, maksimal rata-rata 16-20 kata per scene, 100% aman anti-terpotong di klip AI 15s)
- **Rekomendasi Sound/Backsound**: Tempo 115-125 BPM, beat lo-fi modern atau ambient upbeat ritmis
- **Tips Eksekusi Kreator**: Lighting key-light 45 derajat, mic lavalier 15cm dari dada, tatap lensa kamera bukan layar HP
"""

    def _mock_monetization_bridge(self, prompt: str) -> str:
        return """### 4 Formula Jembatan Konversi (Monetization Bridge)

---

#### 🌉 Formula 1: The Natural Segue (Solusi Wajib Kelanjutan Masalah)
*Cocok untuk: Penjualan produk digital, tools, atau produk fisik solusi instan.*

- **Kalimat Transisi**: *"Punya ide brilian itu bagus, tapi kalau kamu harus ngerjain riset dan skripnya manual dari nol tiap hari, kamu bakal cepet burnout..."*
- **Skrip Audio CTA**: *"Makanya gue rangkum semua sistem ini ke dalam satu template otomatis yang tinggal kamu copas dalam 2 menit. Tinggal klik link di bio buat amankan aksesnya sekarang!"*
- **Instruksi Visual**: Tangan menunjukkan layar smartphone yang membuka produk atau mockup template yang rapi.
- **Teks Grafis di Layar**: **AMBIL TEMPLATE 2 MENIT DI BIO 🚀**

---

#### 🤝 Formula 2: The 'By Popular Demand' Bridge (Karena Banjir Permintaan)
*Cocok untuk: Layanan konsultasi, kelas bimbingan, atau jasa agensi/freelance.*

- **Kalimat Transisi**: *"Jujur, minggu ini DM gue jebol banget nanyain gimana langkah detailnya kalau mulai dari nol banget..."*
- **Skrip Audio CTA**: *"Karena gak sempat balesin satu per satu, gue buka sesi mentoring singkat buat 10 orang tercepat minggu ini. Detail dan link pendaftarannya udah gue pasang di bio ya."*
- **Instruksi Visual**: Tunjukkan screenshot tumpukan pesan DM (diberi efek blur privasi) lalu senyum ke kamera.
- **Teks Grafis di Layar**: **SLOT TERBATAS (CEK BIO SEKARANG) 📩**

---

#### 🎁 Formula 3: The Scarcity & High-Value Gift (Pancingan Lead Magnet Berharga)
*Cocok untuk: Pengumpulan leads, WhatsApp group, Telegram, email newsletter, atau afiliasi.*

- **Kalimat Transisi**: *"Gue gak mau kamu buang-buang jutaan rupiah buat coba-coba hal yang udah jelas gagal..."*
- **Skrip Audio CTA**: *"Khusus yang nonton video ini sampai habis, gue udah siapin checklist dan panduan PDF gratisnya. Tinggal tap foto profil gue, terus download di bio sebelum linknya gue archive!"*
- **Instruksi Visual**: Gerakan tangan menunjuk ke arah sudut kiri atas (foto profil) dengan ekspresi antusias.
- **Teks Grafis di Layar**: **DOWNLOAD PDF GRATIS (LINK DI PROFIL) 🎁**

---

#### 💾 Formula 4: The Save & Share Trigger (Algoritma Booster + Soft Sell)
*Cocok untuk: Menumbuhkan akun organik + penjualan pasif jangka panjang.*

- **Kalimat Transisi**: *"Informasi kayak gini biasanya cuma dibahas di kursus berbayar, jadi..."*
- **Skrip Audio CTA**: *"Save video ini sekarang biar gak hilang pas kamu butuh pas praktek besok. Buat yang mau alat yang persis gue pakai tadi, link rekomendasinya ada di bio nomor satu."*
- **Instruksi Visual**: Gestur menunjuk ke tombol simpan (bookmark) di sisi kanan layar aplikasi TikTok/Reels.
- **Teks Grafis di Layar**: **SAVE DULU SEBELUM LUPA 📌 (LINK DI BIO)**
"""

    def _mock_caption_hashtag(self, prompt: str) -> str:
        return """### Kit Publikasi Media Sosial (Caption, SEO & Jam Upload)

---

### 1. 📝 2 Variasi Caption Siap Copas (High CTR)

**Pilihan A (Storytelling & Emosional):**
Kebanyakan orang mikir mulai bisnis online atau bikin konten itu butuh modal puluhan juta & waktu 12 jam sehari. Padahal faktanya, yang bikin berhasil bukan kerja keras tanpa arah, tapi sistem otomatisasi yang tepat sejak hari pertama.

Kalo kamu sekarang posisinya lagi kerja kantoran tapi pengen punya penghasilan kedua, kamu wajib tonton video ini sampai selesai.

💬 *Pertanyaan diskusi:* Kamu lebih pilih punya 1 sumber income stabil atau 3 side-income kecil-kecil? Tulis di kolom komentar ya!
👉 Template dan panduan praktisnya udah aku rapikan di bio profil.

---

**Pilihan B (To-The-Point & Quick Agitation):**
Jangan mulai jualan online sebelum kamu tau trik 3 langkah ini. Hemat waktu riset 90% dan langsung bisa dipraktekkan hari ini juga modal HP!

Kira-kira apa kendala terberat kamu saat ini? Komen di bawah biar kita bahas bareng.
Amankan akses template gratisnya di link bio sekarang ⚡

---

### 2. 🏷️ Paket 10 Hashtag Terkurasi (Algoritma Booster)
#bisnisonline #sidehustleindonesia #tipsbisnispemula #cuanonline #belajarbisnis #toolsai #kontenkreator #produktifitas #foryoupage #trendingreels

---

### 3. ⏰ Rekomendasi Jam Tayang Terbaik (WIB)
- **Sesi Siang (12:00 - 13:00 WIB)**: Waktu istirahat kantor saat audiens membuka HP untuk hiburan & edukasi singkat.
- **Sesi Malam (19:30 - 21:00 WIB)**: *Peak Golden Time* dengan retensi tonton tertinggi di TikTok dan Instagram Reels.
"""

    def _mock_seven_day_sprint(self, prompt: str) -> str:
        return """# 📅 KALENDER KONTEN SPRINT 7 HARI (SENIN - MINGGU) - HIGH VALUE & EMPIRICAL DEPTH
*Disusun dengan formula retensi disiplin, kaya data empiris, dan bebas klaim kosong.*

---

### HARI 1: Senin - Mitos Terbesar: Modal Stok Barang vs Model Margin Bersih
- **Pilar Strategi**: The Myth-Buster (Membongkar Salah Kaprah Empiris)
- **Hook 3 Detik (Audio)**: *"Stop percaya kalau bisnis online harus stok barang jutaan rupiah kalau gak mau boncos!"*
- **Instruksi Visual**: Zoom-in cepat ke wajah ekspresi serius, tangan menyilangkan tanda X di depan tumpukan kardus kosong.
- **Teks di Layar**: **MITOS PALING BONCOS! 🛑**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Agitasi & Data Empiris)*: Data asosiasi UMKM menunjukkan 68% pemula gulung tikar dalam 90 hari karena dead-stock di gudang.
  - *Detik 15-40 (The Mechanism & Solusi)*: Bandingkan rasio perputaran kas model dropship afiliasi vs stok fisik. Margin bersih 20-30% tanpa modal awal dan tanpa risiko inventori.
  - *Detik 40-60 (Langkah Taktis & CTA)*: 3 kriteria memilih supplier dengan shipping success rate di atas 95%. Ambil panduan seleksi gratis di bio profil.
- **Jembatan Penutup (CTA)**: *"Panduan kurasi supplier dengan fulfillment rate 95% sudah aku taruh di bio profil ya."*
- **Caption Siap Copas**: Masih mikir bisnis itu harus punya ruko dan stok gudang? Data membuktikan modal stok tanpa uji pasar adalah penyebab nomor 1 kebangkrutan pemula. Apa ketakutan terbesar kamu saat mau mulai? Cek link bio buat checklist gratisnya!
- **Hashtag**: #bisnisonline #dataempiris #tipspemula #cuanonline #sidehustle #fyp

---

### HARI 2: Selasa - Tutorial 3 Langkah Riset Produk Laris (Validasi Metrik 5 Menit)
- **Pilar Strategi**: The 3-Step Practical Tutorial (Playbook Taktis)
- **Hook 3 Detik (Audio)**: *"Ini cara validasi produk viral yang pasti laku tanpa tebak-tebakan pakai data metrik!"*
- **Instruksi Visual**: Screen-record dinamis layar smartphone membuka tab marketplace dengan filter metrik.
- **Teks di Layar**: **RISET DATA 5 MENIT ⚡**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Akar Masalah)*: Jangan jual apa yang kamu suka, tapi jual apa yang conversion rate-nya di atas 3% dan sales velocity-nya tinggi.
  - *Detik 15-40 (Mekanisme Teknis)*: Terapkan rumus 300:10:3. Cari produk dengan minimal 300 ulasan positif dalam 30 hari terakhir dan komisi minimal 15%.
  - *Detik 40-60 (Golden Rule)*: Filter kata kunci komplain bintang 1 untuk menemukan kelemahan kompetitor yang bisa kamu jadikan hook konten.
- **Jembatan Penutup (CTA)**: *"Spreadsheet kalkulator rumus 300:10:3 ini bisa kamu download cuma-cuma di link bio."*
- **Caption Siap Copas**: Jangan buang waktu dan kuota promosiin produk yang gak ada peminatnya. Terapkan rumus 300:10:3 ini sebelum memilih katalog. Tag rekan tim bisnismu!
- **Hashtag**: #tutorialbisnis #risetproduk #affiliatemarketing #validasidata #keranjangkuning #fyp

---

### HARI 3: Rabu - Anatomi Kesalahan Pribadi: Terjebak 200 Views Selama 3 Bulan
- **Pilar Strategi**: The Emotional Relatability & Hard Truth (Refleksi Empiris)
- **Hook 3 Detik (Audio)**: *"Tiga bulan akun gue mandek di dua ratus views, dan ternyata ini penyebab sainsnya!"*
- **Instruksi Visual**: Talking head hangat, pencahayaan alami jendela 5500K, tatapan tulus dan bersahabat.
- **Teks di Layar**: **KENAPA MANDEK 200 VIEWS? 📉**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Validasi Masalah)*: Mengira terkena shadowban buatan, padahal analitik menunjukkan 70% penonton kabur di detik ke-1.8.
  - *Detik 15-40 (The Mechanism)*: Algoritma hanya mendistribusikan video yang memiliki 3-second completion rate di atas 60%. Basa-basi salam pembuka adalah racun retensi.
  - *Detik 40-60 (Solusi Nyata)*: Terapkan aturan 0.5 detik visual hook langsung ke inti masalah, watch time rata-rata seketika naik jadi 48%.
- **Jembatan Penutup (CTA)**: *"Coba cek analitik retention graph akunmu sekarang, drop di detik berapa? Komen di bawah biar kita bedah bareng."*
- **Caption Siap Copas**: Algoritma itu matematika, bukan takdir gaib. Kalau retensi detik ke-2 kamu di bawah 50%, video sebagus apapun gak bakal disebar. Siapa yang grafiknya sering anjlok di awal? Tulis di komen ya!
- **Hashtag**: #analisisakun #retensivideo #tipsngonten #algoritmatiktok #kontenkreator #fyp

---

### HARI 4: Kamis - 3 Blunder Fatal Audio-Visual yang Bikin Boncos Budget Iklan
- **Pilar Strategi**: The Costly Mistake (Peringatan & Metrik Biaya)
- **Hook 3 Detik (Audio)**: *"Stop pasang iklan kalau CTR video kreatif kamu masih di bawah satu koma lima persen!"*
- **Instruksi Visual**: Punch-in 1.2x ke layar dashboard iklan dengan angka Cost Per Click (CPC) tinggi.
- **Teks di Layar**: **STOP BONCOS ADS! ⚠️**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Akar Masalah Biaya)*: CPC membengkak bukan karena bidding salah, tapi karena hook visual tidak memicu pola interupsi di feed.
  - *Detik 15-40 (Audit Teknis)*: Blunder 1: Tidak pakai subtitle kontras tinggi. Blunder 2: Lighting remang di bawah 300 lux. Blunder 3: Tawaran tanpa garansi pembalik risiko.
  - *Detik 40-60 (Hasil A/B Test)*: Perbaikan teks layar dinamis berhasil memangkas CPC sebesar 45% dan melipatgandakan ROAS menjadi 3.8x.
- **Jembatan Penutup (CTA)**: *"Template checklist audit video iklan konversi tinggi sudah tersedia di bio."*
- **Caption Siap Copas**: Bikin ads itu bukan soal bakar uang, tapi soal efisiensi pesan. Evaluasi 3 elemen ini sebelum naikin budget iklan kamu malam ini. Share ke tim performance marketing kamu!
- **Hashtag**: #tiktokads #digitalmarketing #evaluasiiklan #roasbooster #bisnisdigital #fyp

---

### HARI 5: Jumat - Tools AI Otomatisasi: Pangkas Waktu Produksi dari 4 Jam Jadi 18 Menit
- **Pilar Strategi**: The Secret Tool / Insider Hack (Efisiensi Terukur)
- **Hook 3 Detik (Audio)**: *"Tools AI ini memangkas waktu produksi konten seminggu dari empat jam jadi delapan belas menit!"*
- **Instruksi Visual**: Tunjukkan layar monitor setup pipeline otomatis yang menghasilkan naskah dan aset dalam sekejap.
- **Teks di Layar**: **DARI 4 JAM JADI 18 MENIT 🤖**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Efisiensi Nyata)*: Hambatan terbesar kreator adalah burnout akibat ngetik skrip manual dan pusing nyari ide di depan layar kosong.
  - *Detik 15-40 (The Mechanism & Workflow)*: Gunakan ViralGenix Continuous Pipeline: 1 prompt riset otomatis terurai jadi 10 variasi hook berbasis psikologi dan tabel storyboard detik demi detik.
  - *Detik 40-60 (Pembuktian)*: Konsistensi upload 7 hari berturut-turut tanpa stres, menghasilkan peningkatan reach akun sebesar 300%.
- **Jembatan Penutup (CTA)**: *"Alur kerja pipeline otomatis ini bisa kamu pelajari langsung di link bio baris pertama."*
- **Caption Siap Copas**: Kerja cerdas dengan otomotif pipeline adalah rahasia top kreator konsisten upload tanpa burnout. Save video ini biar kamu gak lupa alurnya pas produksi akhir pekan nanti!
- **Hashtag**: #aitools #otomatisasikonten #produktivitaskreator #teknologibaru #workflowai #fyp

---

### HARI 6: Sabtu - Debat Analitis: Margin Afiliasi Fisik 5% vs Margin Produk Digital 80%
- **Pilar Strategi**: The Debate Trigger (Diskusi Berbasis Unit Economics)
- **Hook 3 Detik (Audio)**: *"Banyak yang debat: mending affiliate keranjang kuning atau bikin produk digital sendiri?"*
- **Instruksi Visual**: Tangan menunjukkan perbandingan dua model bisnis di papan tulis putih dengan spidol.
- **Teks di Layar**: **BEDAH MARGIN CUAN 🤔**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Bedah Angka)*: Affiliate fisik: volume besar tapi komisi rata-rata hanya 5-10%, dipotong risiko retur barang COD.
  - *Detik 15-40 (Perbandingan Empiris)*: Produk digital (ebook/template): margin bersih 85-90% tanpa ongkir, 1x produksi bisa dijual ribuan kali.
  - *Detik 40-60 (Strategi Hybrid)*: Formula pemenang: gunakan affiliate fisik untuk membangun basis audiens awal, lalu monetisasi dengan digital product sendiri.
- **Jembatan Penutup (CTA)**: *"Menurut kamu lebih cocok yang mana buat pemula modal nol? Tulis pendapatmu di kolom komentar!"*
- **Caption Siap Copas**: Jangan cuma lihat omset kotor, tapi hitung margin bersih yang masuk kantong! Dari hitungan unit economics tadi, kamu lebih tertarik fokus di mana tahun ini? Tulis A untuk Affiliate, B untuk Produk Digital!
- **Hashtag**: #debatbisnis #uniteconomics #produkkreator #bisnisdigital #cuanonline #fyp

---

### HARI 7: Minggu - Weekly Audit & Eksekusi Hari Senin (SOP 30 Menit)
- **Pilar Strategi**: The Weekly Mindset & Direct Action (Actionable Playbook)
- **Hook 3 Detik (Audio)**: *"Minggu depan mau cuma jadi penonton yang iri, atau mau mulai panen hasil sendiri?"*
- **Instruksi Visual**: Suasana santai kafe sore, tablet menampilkan checklist mingguan dan kopi hangat.
- **Teks di Layar**: **RESET AMUNISI MINGGUAN! 🎯**
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Mindset & Realita)*: Motivasi tanpa sistem cuma angan-angan. Yang membedakan kreator berhasil adalah persiapan 30 menit di hari Minggu malam.
  - *Detik 15-40 (3 Aksi Konkret)*: 1. Kunci 3 topik utama. 2. Rekam batch 3 video sekaligus dalam 45 menit. 3. Jadwalkan di jam prime time (19:30 WIB).
  - *Detik 40-60 (Golden Rule)*: 1 video yang tepat dengan bobot materi bernas bisa membuka pintu monetisasi pertama kamu dalam 30 hari ke depan.
- **Jembatan Penutup (CTA)**: *"Starter kit checklist mingguan sudah siap di bio profil, download sekarang dan eksekusi bareng aku besok pagi!"*
- **Caption Siap Copas**: Selamat berakhir pekan! Ambil waktu 30 menit malam ini buat siapkan amunisi konten minggu depan. Ketik 'KOMITMEN' di komen kalau kamu mau mulai eksekusi besok pagi!
- **Hashtag**: #resetmingguan #mindsetkreator #produktivitas #pejuangonline #disiplinkonten #fyp
"""


