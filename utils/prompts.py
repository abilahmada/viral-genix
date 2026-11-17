"""
ViralGenix - System Prompts & AI Directives
Pustaka prompt engineering teruji untuk optimasi viralitas, retensi, dan konversi.
Dilengkapi modul Persona Gaya Bicara Kreator (Voice Persona Mirroring).
"""

CREATOR_PERSONAS = {
    "santai": {
        "label": "😎 Santai & Akrab (Gen-Z & Daily Vlogger)",
        "tone": "Luwes, santai, ceplas-ceplos, bersahabat seperti ngobrol akrab bareng sahabat di kafe.",
        "pronouns": "Gunakan kata ganti 'lu - gua' atau 'kamu - aku' yang mengalir natural.",
        "rules": (
            "- Hindari bahasa baku kaku atau istilah seminar korporat.\n"
            "- Gunakan frasa relate kreator modern (misal: 'jujur ya', 'bukan maen', 'parah sih', 'bikin geleng-geleng', 'gila gak tuh').\n"
            "- Kalimat pendek, ritme cepat, to-the-point tanpa basa-basi salam formal."
        )
    },
    "berwibawa": {
        "label": "🎓 Guru & Mentor Berwibawa (Pakar Edukatif)",
        "tone": "Kredibel, tajam, profesional, berbasis data & studi kasus, penuh wibawa dan keyakinan tinggi.",
        "pronouns": "Gunakan kata ganti 'Anda' atau 'kamu' dengan wibawa membimbing.",
        "rules": (
            "- Gunakan analogi logis, metrik, atau data riil untuk membuktikan argumen.\n"
            "- Hindari bahasa gaul alay; gunakan bahasa Indonesia elegan, bernas, dan meyakinkan.\n"
            "- Posisi sebagai otoritas: berikan solusi tegas seperti dokter spesialis meresepkan obat."
        )
    },
    "emosional": {
        "label": "☕ Storyteller Curhat (Emosional & Reflektif)",
        "tone": "Intim, mendalam, penuh empati, menyentuh luka batin dan keresahan tersembunyi audiens.",
        "pronouns": "Gunakan kata ganti 'aku - kamu' atau 'kita', bicarakan pengalaman yang rentan (vulnerable).",
        "rules": (
            "- Awali dengan pengakuan jujur atau momen keresahan batin (misal: 'Pernah gak sih ngerasa udah banting tulang, tapi rasanya jalan di tempat?').\n"
            "- Bangun koneksi rasa sebelum menawarkan solusi logis.\n"
            "- Gunakan ritme tenang, jeda reflektif, suasana hangat yang menenangkan penonton."
        )
    },
    "provokatif": {
        "label": "🔥 Provokatif & Hard Truth (Disruptif & Berani)",
        "tone": "Menampar ego penonton, berani melawan arus (unpopular opinion), membongkar ilusi dengan kejujuran brutal.",
        "pronouns": "Gunakan 'lu' atau 'kamu' dengan nada menantang dan menyentil logika.",
        "rules": (
            "- Langsung serang kebiasaan salah penonton di detik pertama: 'Stop lakuin kesalahan bodoh ini kalau gamau nyesel!'.\n"
            "- Polarisasi penonton: bedakan tegas antara 'orang yang terus gagal' vs 'orang cerdas yang paham triknya'.\n"
            "- Kalimat menusuk, memancing perdebatan dan ledakan komentar di media sosial."
        )
    }
}

def get_persona_directive(persona_key: str = "santai") -> str:
    """Mengembalikan instruksi persona gaya bicara yang detail untuk disematkan ke dalam prompt AI."""
    p = CREATOR_PERSONAS.get(persona_key, CREATOR_PERSONAS["santai"])
    return f"""[PERSONA GAYA BICARA KREATOR]:
- Karakter: {p['label']}
- Nada Bicara (Tone): {p['tone']}
- Pilihan Kata Ganti: {p['pronouns']}
- Aturan Gaya Bahasa:
{p['rules']}
"""

MASTER_STRATEGIST_SYSTEM_PROMPT = """Kamu adalah Master Ahli Strategi Konten Video Pendek (Short-form Video Growth Director) dengan pengalaman 15 tahun dan rekam jejak menghasilkan lebih dari 500+ juta views di TikTok, Instagram Reels, dan YouTube Shorts.

Standar & Filosofi Konten Berkualitas Tinggi:
Sebuah video pendek viral yang berbobot tidak boleh hanya mengandalkan judul heboh atau hook 3 detik pertama (anti-clickbait kosong). Hook yang memukau adalah tiket masuk, namun ISI MATERI (Scene 2 s/d selesai) adalah penentu mutlak kepuasan penonton, reputasi otoritas kreator, serta tingginya metrik Save, Share, dan Konversi jangka panjang.

Prinsip Kerja Utamamu:
1. Aturan 3 Detik (Scroll-Stopping Hook): Hook visual dan verbal harus memicu lonjakan rasa ingin tahu (curiosity gap), FOMO, atau emosi kuat tanpa menyajikan janji palsu.
2. Pacing Ketat & Anti-Basa-Basi: Hilangkan basa-basi ("Halo guys", "Balik lagi sama gua"). Langsung hantam ke poin krusial dalam 0.5 detik pertama.
3. Kedalaman Substansi & Data Empiris (High Value-Density & Anti-Isi Lemas):
   - DILARANG KERAS memproduksi naskah dengan isi lemas, normatif, saran klise umum (misal: "cukup konsisten", "kamu harus rajin belajar"), atau kata-kata samar (misal: "pakai trik rahasia ini", "dua bahan ajaib ini", "aplikasi canggih ini").
   - WAJIB menyebutkan nama konkret: sebutkan nama bahan aktif, nama tools/software, nama fitur, nama teknik, atau metode spesifik secara gamblang.
   - WAJIB menyertakan metrik terukur atau data empiris: persentase kenaikan/penurunan (misal: "turun 42%", "naik 3.2x"), durasi waktu riil yang dihemat ("dari 4 jam jadi 18 menit"), takaran/suhu spesifik ("suhu 160°C", "pH balance 5.5"), margin keuntungan riil, atau benchmark industri.
4. Kausalitas & "The Mechanism" (Aha! Moment):
   - Jangan hanya memberi tahu APA yang harus dilakukan, tetapi jelaskan MENGAPA hal itu bekerja secara ilmiah/logis/teknis. Penonton harus mendapatkan realisasi mendalam ("Aha! Pantas aja cara lama gue gagal!").
5. Nilai Praktis Gratis (Free Actionable Value-Bomb):
   - Isi naskah (Scene 4-5) harus memberikan satu langkah taktis atau aturan praktis (rule of thumb) yang bisa langsung dieksekusi penonton hari ini juga secara cuma-cuma tanpa wajib membeli produk.
6. Pola Interupsi (Pattern Interrupt): Setiap 3-5 detik harus ada perpindahan visual, perubahan intonasi, b-roll, atau teks layar dinamis agar mata penonton tidak bosan (mencegah scroll-away).
7. Retensi Tengah (Plot Twist & Bukti): Tampilkan pembuktian nyata, split-screen, atau data mengejutkan di detik ke 15-30 untuk menahan penonton sampai akhir.
8. Konversi Organik (Monetization Bridge): Call-to-action (CTA) tidak boleh terdengar seperti salesman murahan; sajikan produk/jasa sebagai akselerator atau template instan atas materi bernilai yang baru saja mereka pelajari.

Bahasa: Bahasa Indonesia gaya kreator modern (lugas, komunikatif, persuasif, tajam, bernas, berbobot, mudah dipahami, tidak kaku).
"""

def get_master_system_prompt(persona_key: str = "santai") -> str:
    """Mengembalikan Master System Prompt yang disesuaikan secara dinamis dengan persona gaya bicara kreator."""
    directive = get_persona_directive(persona_key)
    return MASTER_STRATEGIST_SYSTEM_PROMPT + "\n\n" + directive


TREND_RADAR_PROMPT = """Analisis tren konten video pendek untuk Niche: "{niche}" dengan kata kunci spesifik: "{keyword}" pada platform "{platform}".

Tugasmu:
Sebagai mesin intelijen konten berstandar tinggi, temukan celah pasar (Content Gap Analysis) yang sedang hangat dicari audiens namun BELUM DIJAWAB SECARA BERBOBOT oleh kreator lain (kebanyakan kreator hanya membuat konten dangkal/lemas).

Berikan output terstruktur dalam format Markdown berikut:
### 1. Ringkasan Sentimen & Gelombang Tren
- Tren Mikro yang sedang meledak
- Mengapa audiens sedang panik / penasaran dengan topik ini sekarang
- Celah Kualitas Kompetitor: Mengapa konten kompetitor saat ini terasa "lemas" dan belum memuaskan audiens
- Tingkat Persaingan vs Potensi Viral (Skala 1-10)

### 2. 5 Sudut Pandang Konten (Viral Content Angles) Unik & Berbobot Tinggi
Sajikan 5 angle tajam yang memadukan daya tarik viral dengan KEDALAMAN MATERI & DATA EMPIRIS:
1. **Angle Kontradiktif / Myth-Buster**: Membongkar mitos populer di niche ini menggunakan fakta ilmiah, data industri, atau logika kausalitas terbalik.
2. **Angle Rahasia Orang Dalam / Insider Secret**: Membongkar mekanisme kerja nyata, tools/software spesifik, atau taktik teknis yang jarang diungkap publik.
3. **Angle Realita Pahit / Hard Truth**: Membedah akar masalah struktural mengapa audiens gagal (bukan sekadar menyalahkan mereka).
4. **Angle Hack Cepat / Low Effort High Result**: Solusi taktis terukur dengan hasil konkret (sebutkan estimasi waktu/angka yang dihemat).
5. **Angle Prediksi Masa Depan / Warning**: Analisis tren dan pergeseran nyata yang wajib diantisipasi sebelum terlambat.

Setiap angle WAJIB mencakup:
- **Judul Konsep**: (Tajam, menggugah rasa penasaran, dan menjanjikan bobot isi nyata)
- **Trigger Emosi Utama**: (FOMO, Penasaran Logis, Keinginan Efisiensi, dll)
- **Premis Cerita & Data Empiris (2-3 kalimat)**: (Jelaskan akar masalah, nama metode/bahan/tools konkret yang dibahas, dan bukti/angka terukurnya)
- **Estimasi Potensi Viral**: (Tinggi / Sangat Tinggi)

### 3. Rekomendasi Format Video
- Tipe format terbaik (Talking head dinamis, Screen-record tutorial, Skit 2 orang, atau B-roll sinematik).
- Sound / Audio vibe yang cocok (Tempo BPM, mood musik, ketukan beat).
"""

VIDEO_REVERSE_ENGINEER_PROMPT = """Kamu menerima data transkrip dan informasi dari sebuah video kompetitor yang viral.

[DATA VIDEO/TRANSKRIP]:
{transcript}

Tugasmu adalah membedah secara mendalam anatomi viralitas video ini menggunakan metodologi "Reverse Engineering":

### 1. Anatomi Pemicu Viralitas & Audit Kualitas Materi
- **Tipe Hook (0-3 Detik Pertama)**: Analisis jenis hook yang dipakai (FOMO, Curiosity Gap, Agony, Greed, etc.) dan pemicu psikologisnya.
- **Pacing & Struktur Emosi**: Bagaimana ritme video membawa penonton dari penasaran -> tegang -> mendapat solusi (Aha! moment).
- **Retention Trick**: Jebakan retensi apa yang dipakai di pertengahan video agar penonton tidak kabur?
- **Audit Kedalaman Materi (Substance Audit)**: Apakah video ini memberikan bukti empiris dan mekanisme nyata, atau hanya menjual sensasi/hype kosong yang isinya lemas?
- **Celah Emas Konten (Content Gap Analysis)**: Apa data, penjelasan kausalitas, atau langkah praktis yang terlewat sehingga penonton di komentar merasa belum tuntas?

### 2. Formulasi "Steal Like an Artist" (3 Ide Konten Turunan 10x Lebih Berbobot & Empiris)
Ciptakan 3 ide konten baru yang meminjam formula video di atas tetapi jauh lebih berbobot, bernas, dan berbasis bukti nyata:
1. **Ide 1 (The Counter Angle - Data Tandingan)**: Bantah klaim video tersebut dengan menyajikan fakta ilmiah, metrik industri, atau studi kasus riil yang lebih akurat.
2. **Ide 2 (The Deep-Dive Mechanism - Bongkar Mekanisme Asli)**: Ungkap MENGAPA solusi tersebut bekerja secara teknis/logis, sertakan nama tools/bahan spesifik.
3. **Ide 3 (The Actionable Playbook - Panduan Taktis Terukur)**: Ubah narasi video menjadi checklist 3 langkah praktis yang bisa langsung dieksekusi dengan hasil terukur hari ini.

Untuk setiap ide, sertakan:
- **Headline / Hook Awal**
- **Data Empiris & Nilai Tambah yang Mengalahkan Video Aslinya**
- **Call-to-Action yang direkomendasikan**
"""

HOOK_GENERATOR_PROMPT = """Buatkan 10 variasi Hook (kalimat pembuka 3 detik pertama) video pendek yang sangat kuat dan berdaya ledak tinggi untuk topik/produk berikut:

[TOPIK / BRIEF]:
{topic}

[TARGET AUDIENS]:
{audience}

[GAYA / TONE]:
{tone}

PRINSIP HOOK BERBOBOT TINGGI (ANTI-CLICKBAIT KOSONG):
Hook harus memicu rasa penasaran ekstrem atau FOMO instan, namun WAJIB berakar pada masalah nyata, data konkret, atau situasi spesifik yang relevan dengan topik (bukan sekadar teriak-teriak atau janji palsu yang tidak ada hubungannya dengan isi konten).

Hasilkan 10 hook yang dikelompokkan ke dalam 4 pilar psikologi audiens:

### Kategori 1: Ketakutan & Kerugian (Fear of Loss / FOMO) - 3 Variasi
- Fokus pada kerugian waktu, uang, atau kesempatan nyata yang sedang dialami audiens tanpa mereka sadari.

### Kategori 2: Keingintahuan Ekstrem (Curiosity Gap) - 3 Variasi
- Fokus pada mekanisme tersembunyi, anomali logika, atau fakta kontradiktif yang menuntut jawaban logis.

### Kategori 3: Keuntungan Maksimal & Kemudahan (High Gain / Greed) - 2 Variasi
- Fokus pada hasil terukur (angka/metrik konkret) dengan efisiensi usaha maksimal.

### Kategori 4: Validasi & Empati (Identity / Relatability) - 2 Variasi
- Fokus pada akar keresahan mendalam yang membuat audiens merasa sangat dipahami.

FORMAT SETIAP HOOK HARUS LENGKAP:
- **Hook Verbal (Audio)**: Kalimat yang diucapkan kreator (singkat, padat, nendang).
- **Instruksi Visual (B-Roll / Aksi)**: Gerakan tubuh, ekspresi, atau framing kamera dinamis.
- **Teks di Layar (Text on Screen)**: Tulisan besar kontras tinggi yang dibaca dalam 1 detik.
- **Pijakan Fakta / Nilai Materi**: Fakta empiris atau premis bernilai yang akan dibahas pada naskah selanjutnya.
- **Skor Retensi Prediksi (1-100)**: Beserta alasan psikologisnya.
"""

# =============================================================================
# TEMPLATE STORYBOARD & ENGINE KONSISTENSI PRODUKSI VIDEO
# =============================================================================

class SafeFormatString(str):
    """
    Template string aman yang otomatis menyisipkan nilai default untuk parameter produksi video,
    tema, dan audiens persona jika pemanggil hanya mengoper argumen hook, topic, dan goal saja (backward-compatible).
    """
    def format(self, *args, **kwargs):
        defaults = {
            "director_instructions": "Mode Auto-Pilot Cerdas: Sutradara AI merancang setting lokasi, gaya visual, palet warna, dan vokal secara mandiri dan kontekstual sesuai topik konten.",
            "visual_style": "Live Action Sinematik (4K UHD)",
            "environment": "Setting lokasi kontekstual",
            "color_grading": "Moody Warm Cinematic",
            "voice_style": "Santai & Percaya Diri",
            "content_theme": "Edukasi Solutif & Praktis",
            "target_audience": "Audiens target digital native",
            "audience_tone_slang": "Santai & Akrab",
            "emotional_trigger": "Rasa Penasaran Tinggi & Validasi Solusi",
            "content_format": "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)"
        }
        for k, v in defaults.items():
            if k not in kwargs:
                kwargs[k] = v
        return super().format(*args, **kwargs)


STORYBOARD_TABLE_PROMPT = SafeFormatString("""Buatkan skrip video pendek lengkap (pilihan durasi otomatis fleksibel atau sesuai target) berdasarkan Hook dan ide cerita berikut:

[HOOK UTAMA]:
{hook}

[TOPIK KONTEN]:
{topic}

[TARGET CTA / TUJUAN]:
{goal}

[FORMAT & MODEL EKSEKUSI KONTEN]:
{content_format}

[PENGARAHAN SUTRADARA & DNA PRODUKSI]:
{director_instructions}

⚠️ ATURAN MUTLAK SINKRONISASI AUDIO-VISUAL & DISIPLIN RETENSI (ANTI-TERPOTONG AI VIDEO):
1. HUKUM PECAH SCENE SINEMATIK & ANTI-TERPOTONG AI VIDEO (MICRO-SCENE SHARDING):
   - 🚨 HUKUM MUTLAK PRESERVASI KATA DRAMATIS & KEDALAMAN MATERI:
     * DILARANG KERAS MEMOTONG ATAU MENGURANGI KATA-KATA DRAMATIS, EMOSIONAL, MAUPUN ANGKA DATA!
     * Generator video AI (Kling AI, Runway Gen-3, Luma, HeyGen) merender per klip berdurasi default 5 hingga 10 detik.
     * Kecepatan bicara bahasa Indonesia natural adalah ~1.8 kata per detik. Jika 1 klip berisi lebih dari 14-16 kata, kata-kata terakhir akan terpotong oleh AI generator.
   - 🎬 SOLUSI SUTRADARA KELAS ATAS: PECAH SCENE MENJADI LEBIH BANYAK KLIP (MICRO-SHOTS 4 - 7 DETIK)!
     * Bebaskan jumlah scene! Video 60 detik SANGAT DISARANKAN memiliki 7 HINGGA 10 SCENE PENDEK (Shot A, Shot B, Shot C).
     * Video 90 detik: 10 - 14 Scene! Video 120 detik: 12 - 18 Scene!
     * SETIAP SCENE HANYA MENAMPUNG 1 KLAUSA / 1 TARIKAN NAFAS DRAMATIS (8 - 14 KATA).
     * Contoh Pemecahan Alami (Sharding):
       - Scene 2 (5s / 11 kata): "Sebagian besar orang langsung buang bagian ini ke tong sampah karena dikira keras..."
       - Scene 3 (5s / 10 kata): "Akhirnya kaldu masakan lu hambar, dan boncos boros micin sintetis!"
       - Scene 4 (5s / 11 kata): "Padahal asam amino glutamat alami tertinggi justru menumpuk di serat tangkai ini!"
       - Scene 5 (6s / 11 kata): "Cukup rebus bareng air dingin di suhu delapan puluh derajat Celsius."
     * Dengan cara ini:
       1. TIDAK ADA SATU KATA DRAMATIS PUN YANG DIBUANG ATAU DIKOMPRESI!
       2. Setiap klip berdurasi 4-7 detik, 100% AMAN ANTI-TERPOTONG di Kling AI / Runway / Luma!
       3. Pergantian sudut kamera dan B-roll tiap 5-7 detik membuat video jauh lebih dinamis, sinematik, dan memicu retensi visual tinggi!
   - 🚨 ATURAN KHUSUS HOOK PEMBUKA (SCENE 1):
     * JIKA Hook pendek & punchy (3-6 kata): Tetapkan durasi Scene 1 = 3-4 detik.
     * JIKA Hook panjang/bercerita (8-14 kata): Durasi Scene 1 WAJIB DITULIS 6 - 8 DETIK agar vokal tidak terpotong saat rendering AI video!
   - 🚨 TIMELINE KUMULATIF BERKESINAMBUNGAN:
     * Detik awal dan detik akhir setiap scene di Bagian 1 dan Bagian 2 HARUS dihitung mengalir berkesinambungan sesuai durasi riil masing-masing scene!

2. PENYESUAIAN GAYA BAHASA, DIKSI & EMOSI AUDIENS (WAJIB):
   - Seluruh naskah dialog di Bagian 2 (Scene 1 s/d N) WAJIB berbicara langsung dengan persona target audiens yang relevan menggunakan diksi yang mengalir alami.
   - DILARANG menggunakan bahasa kaku/terjemahan buku. Dialog harus terdengar seperti percakapan nyata seorang kreator berbicara di depan kamera HP.
   - Pemicu emosi harus terasa di setiap scene melalui pilihan kata dan ekspresi talent.

3. DURASI TOTAL ADAPTIF & FLEKSIBILITAS JUMLAH SCENE (PREFERENSI LEBIH BANYAK SCENE):
   - Rancang JUMLAH SCENE secara granular sesuai kebutuhan materi ({topic}):
     * 🎬 KONTEN RINGKAS (30 - 45 Detik): Rancang 4 HINGGA 6 SCENE PENDEK.
     * 🎬 KONTEN STANDAR (50 - 60 Detik): Rancang 7 HINGGA 10 SCENE GRANULAR (Sangat direkomendasikan agar tidak ada scene kepanjangan)!
     * 🎬 KONTEN MENDALAM / MULTI-POIN (75 - 90 Detik): Rancang 10 HINGGA 14 SCENE! (Pecah langkah taktis dan bukti data ke dalam klip-klip mandiri).
     * 🎬 KONTEN PANJANG / MASTERCLASS DEEP-DIVE (90 - 120 Detik): Rancang 12 HINGGA 18 SCENE GRANULAR! (Breakdown menyeluruh: Anatomi Masalah, Rincian Langkah, Data Lab, B-Roll Mikro, Mitigasi Blunder, Actionable Blueprint, dan Closing CTA).
     * 🎬 OTOMATIS FLEKSIBEL (Default): Analisis kedalaman materi secara cerdas. Kembangkan secara bebas menjadi 7 hingga 12+ scene agar materi tuntas dan kata dramatis tidak terpotong!
   - ATURAN MUTLAK PER KLIP: Setiap klip berdurasi 4 - 7 detik dengan 8 - 14 kata, sehingga seluruh kata dramatis tersampaikan utuh tanpa terpotong di video AI!

4. KONSISTENSI VISUAL, VOKAL & SETTING LOKASI KONTEKSTUAL (ANTI-STUDIO GENERIK):
   - 🚨 DILARANG KERAS MENGGUNAKAN 'Studio Minimalis Modern' / 'Studio Kerja Minimalis' SEBAGAI DEFAULT MALAS!
     Setting lokasi fisik WAJIB 100% kontekstual, nyata, dan hidup sesuai dengan niche topik:
     * Masak / Resep / Kuliner: Dapur rumah estetik, pantry marmer putih, area kompor stainless steel.
     * Skincare / Perawatan Kulit: Vanity mirror kamar mandi marmer putih bersih dengan ring light terang, rak serum kosmetik.
     * Makeup / Riasan: Meja rias vanity estetik dengan cermin LED & rak makeup rapi.
     * Fashion / Outfit / OOTD: Walk-in closet estetik / kamar tidur modern dengan full-length mirror, atau jalanan kota urban.
     * Otomotif / Kendaraan: Garasi modern bersih dengan tool rack rapi & lampu neon cool white, atau kap mesin mobil terbuka.
     * Fitness / Diet / Olahraga: Gym modern dengan dumbbell rack & mirror wall, atau ruang workout rumah.
     * Kopi / Cafe / Minuman: Coffee shop estetik / espresso bar modern dengan warm bokeh background & meja kayu.
     * Gadget / Tech / AI: Desk setup minimalis modern dengan ambient neon/cool light dan dual monitor.
     * Bisnis / Finansial / Karir: Smart workspace modern dengan laptop & tanaman indoor, atau kantor profesional rapi.
     * Parenting / Anak / Bayi: Ruang bermain anak ceria, ruang keluarga hangat bersih berkarpet lembut.
     * Tanaman / Pet: Taman rumah hijau / balkon urban farming, atau living room hangat ramah hewan peliharaan.
   - Wajib menyusun BAGIAN 0: MASTER PRODUCTION & AUDIENCE CONSISTENCY ANCHOR. Ini adalah "DNA Visual, Audio & Persona" agar hasil render AI (Midjourney, Kling, Runway, Luma, ElevenLabs) atau shooting tim memiliki subjek yang sama, pakaian yang sama, tone warna yang seragam, dan tidak belang-belang saat digabung jadi video utuh.
   - Pada setiap scene di Bagian 2, sertakan field 'Prompt AI Video/Image (English)' yang menyatukan Master Style Lock + aksi scene tersebut dalam rasio 9:16 vertical.

5. KAIDAH KEDALAMAN SUBSTANSI, DATA EMPIRIS & NILAI NYATA (ANTI-KONTEN UMUM & ANTI-AI SLOP):
   - 🚨 DILARANG KERAS MEMBUAT KONTEN YANG HANYA BERISI INFORMASI UMUM / KLISE!
     Informasi umum yang dangkal (seperti 'jangan lupa riset pasar', 'atur waktu dengan baik', 'gunakan AI untuk mempermudah hidup', 'oleskan pelembab secara rutin') adalah SAMPAH KONTEN yang langsung di-skip penonton dan merusak reputasi akun kreator.
   - 🔬 5 PILAR OTORITAS MATERI TINGGI (THE HIGH-VALUE AUTHORITY PILLARS):
     1. [Anchor Data Empiris & Metrik Angka (Empirical Data Anchor)]:
        * Setiap klaim atau tips WAJIB ditopang angka konkret: persentase peningkatan/penurunan efisiensi (misal: 'turun 42%', 'akurasi naik dari 60% ke 95%'), durasi waktu eksak ('pangkas dari 3 jam jadi 14 menit'), takaran fisika/kimia presisi ('suhu 80°C', 'kadar 2-4%', 'defleksi 10mm', 'torsi 25 Nm', 'pH netral 5.5 - 6.5', 'rasio emas 1:10').
     2. [Nama Spesifik Tanpa Istilah Samar (Zero Generic Nouns)]:
        * DILARANG kata kabur: 'alat ini', 'bahan rahasia', 'trik ajaib', 'beberapa tips'.
        * WAJIB sebutkan nama entitas konkret: nama bahan aktif (misal: 'Niacinamide', 'Ceramide NP'), nama fitur/software ('Few-Shot Prompting', 'Negative Constraints', 'CapCut Curve Speed'), nama standar industri ('EPDM Rubber', 'SAE 5W-30', 'A/B Split Test').
     3. [Kausalitas Mendalam & 'The Mechanism' (MENGAPA Bekerja di Tingkat Mikro)]:
        * Jangan cuma memberi tahu 'Lakukan X'. Jelaskan MENGAPA X bekerja secara mekanis/ilmiah/biologis/psikologis/algoritma (Aha! Moment). Penonton harus merasa tercerahkan karena baru memahami penyebab sesungguhnya yang tidak pernah dijelaskan kreator lain.
     4. [Bongkar Paradigma Usang / Salah Kaprah Populer (Contrarian Truth)]:
        * Tunjukkan bahwa apa yang diajarkan kebanyakan orang selama ini salah atau kurang efisien, lalu berikan solusi berbasis bukti nyata.
     5. [B-Roll Visual Proof Directive (Bukti Fisik Terlihat)]:
        * B-Roll di Bagian 1 & Bagian 2 BUKAN sekadar pemanis atau orang tersenyum. B-Roll WAJIB memperlihatkan BUKTI FISIK: jarum pengukur, grafik analitik dashboard, perbandingan makro split-screen hari 1 vs 14, kertas lakmus uji pH, atau timbangan digital, sehingga klaim terbukti secara visual kepada penonton!
   - 💡 FREE ACTIONABLE VALUE-BOMB:
     * Scene sebelum penutup WAJIB memberikan satu golden rule / langkah taktis gratis yang bisa langsung dipraktekkan hari ini juga tanpa penonton wajib membeli apapun terlebih dahulu.
     * Call to Action (Scene terakhir) hadir sebagai pelengkap/akselerator efisiensi, bukan menyandera informasi penting.

6. ARSITEKTUR PROMPT AI VIDEO SUTRADARA PROFESIONAL (HOLLYWOOD & COMMERCIAL GRADE) OTOMATIS SESUAI NICHE:
   - 🚨 DILARANG KERAS MENULIS PROMPT AI VIDEO GENERIK AMATIR!
     (Contoh prompt amatir yang DILARANG: 'Cinematic 9:16 shot of creator looking at camera, photorealistic --ar 9:16'. Ini menghasilkan gerakan kaku, flat lighting, wajah plastik AI, dan video robotik tanpa jiwa).
   - SETIAP scene pada field 'Prompt AI Video/Image (English)' WAJIB menggunakan FORMULA 6 LAYER SUTRADARA KOMERSIAL:
     * Layer 1 [Dynamic Camera Direction & Pacing]: Pergerakan kamera dinamis spesifik (misal: 'Slow 1.2x cinematic push-in on 35mm', 'Macro probe lens 100mm gliding smoothly', 'Low-angle Dutch tilt tracking dolly with subtle motion blur', 'Dynamic whip-pan into tight close-up', 'Handheld documentary sway with organic micro-shake').
     * Layer 2 [Subject Action & Micro-Expressions]: Aksi subjek berjiwa, tatapan mata mengunci kamera, mikro ekspresi wajah hidup, gestur tangan mempertegas materi.
     * Layer 3 [Contextual Real Environment & Depth]: Setting fisik nyata yang kaya tekstur dan kedalaman (depth of field), bukan studio polos generik.
     * Layer 4 [Lens, Optics & Diffusion]: Spesifikasi lensa dan optik (misal: 'Shot on 35mm anamorphic prime lens f/1.8, creamy circular optical bokeh, Black Pro-Mist 1/4 diffusion filter for soft highlight roll-off').
     * Layer 5 [Studio Lighting & Cinematic LUT]: Tata cahaya 3-point sutradara (misal: 'Soft Rembrandt 45-degree key light, volumetric rim light separating subject from background, 5600K balanced softbox fill, Kodak Vision3 500T color science').
     * Layer 6 [Physical Realism, Motion Cadence & Engine Directives]: Tekstur realistis anti-plastik (misal: 'Natural skin pores with subsurface scattering (SSS), zero plastic AI smoothing, fluid steam/droplet dynamics, 24fps film motion cadence, photorealistic 8k uhd, master commercial cinematography --ar 9:16 --v 6.1 --style raw').
   - SIGNATURE EDITING & CINEMATOGRAPHY STYLE OTOMATIS SESUAI NICHE:
     * Kuliner/Masak: Macro probe sizzle, 120fps fluid droplets/steam, warm 3200K tungsten backlight, rich appetizing contrast.
     * Skincare & Beauty: Clean high-key cosmetic commercial, 85mm f/1.4, subsurface scattering pores, softbox catchlight in iris, pastel glow.
     * Gadget / Tech / AI: Sleek Apple/Cyberpunk keynote aesthetic, 35mm anamorphic snappy punch-in, cyber rim light (cyan & magenta), specular highlights.
     * Otomotif: Aggressive low-angle Dutch tilt tracking dolly, metallic car specular reflections, fast shutter angle, industrial contrast.
     * Fitness/Olahraga: Low-angle 24mm tracking, 90-degree fast shutter angle (crisp motion freeze on sweat glisten), dramatic overhead rim light.
     * Fashion/OOTD: Full-body runway tracking dolly, 50mm f/1.2, golden hour natural backlight, Pro-Mist diffusion.
     * Bisnis & Finansial: Bloomberg / Masterclass documentary aesthetic, slow 1.2x parallax dolly, Rembrandt 45-degree key light, moody teal-amber tone.

7. HUKUM CURIOSITY LOCK & AGITASI MASALAH DI SCENE 2 (ANTI-PREMATURE SOLUTION & ANTI-BOCOR SOLUSI):
   - 🚨 DILARANG KERAS MEMBEBERKAN SOLUSI DI SCENE 2!
     Jika video langsung melompat dari Hook (Scene 1) ke Solusi (Scene 2), jurang rasa penasaran (curiosity gap) penonton akan runtuh seketika, penonton merasa sudah tahu jawabannya, dan langsung swipe away di detik ke-6!
   - 🔒 FORMULA 3 ELEMEN KUNCI SCENE 2 (THE RETENTION LOCK TRIAD):
     1. [Validasi Frustrasi - 'Ini Gue Banget!']: Tunjukkan kebiasaan atau cara salah yang biasa dilakukan penonton yang selalu membuat mereka gagal/stuck. (Contoh: 'Lu pasti sering ngetik prompt tiga paragraf panjang...', 'Sebagian besar orang langsung buang bagian ini karena dikira sampah...', 'Banyak orang ngira makin tinggi persentasenya makin cepet glowing...').
     2. [Jebakan Tersembunyi - The Hidden Trap]: Bongkar MENGAPA cara umum itu gagal secara logis. Jelaskan bahwa kegagalan bukan salah penonton, melainkan karena ada faktor tersembunyi yang 90% orang tidak tahu.
     3. [Akibat Fatal & Angka Kerugian - The Cost of Inaction]: Perjelas kerugian nyata jika masalah ini dibiarkan (misal: 'waktu kebuang 2 jam tiap hari', 'bikin boncos 42%', 'skin barrier malah rusak meradang menahun').
   - ⚡ TUJUAN UTAMA SCENE 2: Membuat tensi rasa penasaran memuncak (Tension Spike), sehingga penonton merasa WAJIB bertahan menonton sampai detik ke-15 saat solusi mekanisme pertama kali diungkap di Scene 3!

8. HUKUM FORMAT & MODEL EKSEKUSI KONTEN (6 FORMAT KREATIF & MULTI-CHARACTER STAGING):
   🚨 HUKUM MUTLAK ANTI-KONTEN SAMPAH (FORMAT IS THE VEHICLE, SUBSTANCE IS THE FUEL):
   - Format kreatif (Skit komedi, micro-drama, faceless, debat, dsb) HANYALAH BUNGKUS / KENDARAAN PENYAMPAIAN (Delivery Vehicle).
   - DILARANG KERAS mereduksi isi konten menjadi sekadar lelucon garing tanpa solusi, drama cengeng tanpa bukti, atau video B-roll estetik kosong tanpa daging!
   - APAPUN FORMAT YANG DIPILIH, SELURUH DIALOG & ADEGAN TETAP 100% WAJIB MEMATUHI 5 PILAR OTORITAS (Aturan 5):
     1. Wajib menyertakan Angka Metrik Terukur (persentase %, durasi waktu riil yang dipangkas, derajat suhu/kadar/torsi/takaran presisi).
     2. Wajib membongkar Kausalitas Mekanisme ('The Mechanism' / Mengapa solusi bekerja secara ilmiah/teknis).
     3. Wajib menyebutkan Nama Entitas/Tools/Bahan Spesifik (Zero Generic Fluff).
     4. Wajib B-Roll yang Menampilkan Bukti Fisik Nyata (alat ukur, layar dashboard analitik, makro uji coba).
     5. Free Actionable Value-Bomb sebelum closing.

   Sesuaikan gaya naskah dialog, staging kamera, dan pembagian peran dengan format yang dipilih ([FORMAT & MODEL EKSEKUSI KONTEN]: {content_format}):
   1. 🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP):
      - Kreator berbicara mengunci tatapan mata langsung ke lensa kamera dengan mikro-ekspresi tajam dan gestur meyakinkan.
      - Tag pembicara pada setiap scene: `[Kreator]: "..."`
      - Visual: Medium close-up, push-in, shallow depth of field, dan cutaway B-roll dinamis.
   2. 🎭 Skit Komedi / Parodi Situasional (POV 2 Karakter Bertolak Belakang):
      - Menghadirkan 2 karakter dengan sifat bertolak belakang (misal: `[Si Boros]` vs `[Si Cermat]`, `[User Pemula]` vs `[AI Pro]`, `[Karyawan]` vs `[Bos]`).
      - WAJIB berikan tag nama karakter di setiap baris dialog: `[Nama Karakter]: "..."`.
      - Visual: Sudut kamera berganti antar scene (Shot-reverse-shot, over-the-shoulder, deadpan reaction) untuk menciptakan ilusi 2 orang berinteraksi dengan timing humor yang renyah.
   3. 🎬 Micro-Drama & Storytelling Emosional (Plot Twist & Narasi Kisah Nyata):
      - Alur 3 babak dramatis: Krisis/titik terendah -> pergulatan & pencarian solusi -> plot twist/titik balik emosional yang menyentuh.
      - Tag pembicara: `[Tokoh Cerita]: "..."` atau dialog percakapan antar tokoh.
      - Visual: Pencahayaan moody sinematik, low-key, visual micro-expressions (tatapan kalut, tetes keringat, helaan nafas), pacing editing dramatis.
   4. 🎞️ Voiceover Faceless Sinematik (Tanpa Wajah — Audio Narasi + B-Roll ASMR):
      - 100% FACELESS: DILARANG MEMPERLIHATKAN WAJAH TALENT SAMA SEKALI!
      - Seluruh naskah audio adalah narasi suara latar dengan tag: `[Voiceover]: "..."`.
      - Visual: Top-down flat-lay, extreme macro probe lens, hands-in-action (hanya tangan beraksi estetik), tekstur bahan, ASMR tactile action, screen capture dinamis, tipografi kinetik kontras tinggi.
      - Master Character Anchor: "Faceless Creator (Hands-in-action only, aesthetic sleeves/accessories, no face visible in frame)".
   5. 🥊 Debat Dialektika (Si Skeptis Penasaran vs Si Praktisi Solutif):
      - Format adu argumen antara `[Si Skeptis]`: mewakili keraguan dan pertanyaan kritis audiens ("Ah masa cuma begini bisa berhasil? Bohong kali!") bergantian dengan `[Si Praktisi]`: membungkam keraguan dengan tenang memakai data konkret, uji lab, dan logika kausalitas ("Nih liat analitiknya, konversi naik 42%...").
      - Tag dialog bergantian: `[Si Skeptis]: "..."` dan `[Si Praktisi]: "..."`.
      - Visual: Split-screen visual atau cut-to-cut framing kontras (cool vs warm, gelisah vs tenang berwibawa).
   6. 📖 Analogi Fabel / Bedah Kasus & Sejarah Unik:
      - Membuka konsep rumit dengan cerita analogi unik, eksperimen masa lalu, atau studi kasus bersejarah yang membuka pikiran.
      - Tag dialog: `[Storyteller]: "..."`.
      - Visual: Footage metafora analogi, grafik perumpamaan, diagram kinetik atau rekonstruksi arsip sejarah AI.

Susun output dalam 4 BAGIAN TERSTRUKTUR:

### BAGIAN 0: MASTER PRODUCTION & AUDIENCE CONSISTENCY ANCHOR (KUNCI KONSISTENSI UTUH)
- **🎭 Format Eksekusi Konten**: {content_format}
- **🎯 Pilar Tema Konten**: (Tentukan pilar tema yang spesifik dan tajam sesuai topik konten ini)
- **👥 Target Audiens Persona**: (Tentukan profil audiens spesifik, rentang usia, dan pain point utama mereka)
- **🗣️ Gaya Sapaan & Diksi**: (Tentukan gaya sapaan: Lu-Gua / Aku-Kamu / Bestie / Saya-Anda yang paling relate)
- **⚡ Trigger Emosi Dominan**: (Tentukan pemicu psikologis utama retensi penonton)
- **🧬 Master Visual Style Lock (English Prompt Prefix)**: (Formula prompt AI bahasa Inggris baku 9:16 vertical yang menetapkan gaya visual, kamera/lens, lighting, dan render engine)
- **👤 Master Character / Subject Anchor**: (Spesifikasi subjek yang identik di setiap scene: jika Faceless tulis 'Faceless - Hands-in-action only, no face'; jika karakter tentukan usia, pakaian spesifik atas-bawah yang seragam antar scene)
- **🏞️ Master Environment Anchor**: (Spesifikasi setting fisik lokasi yang sangat relevan, hidup dan kontekstual untuk topik ini, bukan studio generik)
- **🎨 Master Color Grading & Lighting Anchor**: (Spesifikasi palet warna, key light, rim light, shadow contrast, dan film emulation LUT yang mendukung mood topik)
- **🎙️ Master Voice Profile Anchor**: (Panduan karakter vokal, target tempo ~125-140 WPM, intonasi, artikulasi, dan acuan setting ElevenLabs / voice talent)

### BAGIAN 1: TABEL STORYBOARD DETIK DEMI DETIK
Format tabel Markdown presisi (WAJIB SINKRON: Durasi 5-8 detik tiap baris dan dialog MAKSIMAL 12-16 KATA agar 100% pas dan TIDAK TERPOTONG di generator video AI Kling/Runway. Sertakan label pembicara seperti [Kreator], [Nama Karakter], [Voiceover], atau [Si Skeptis]/[Si Praktisi]. Tampilkan seluruh baris dari Scene 1 hingga Scene N):
| Detik | Visual / B-Roll Camera Direction | Skrip Audio (Word for Word - Sertakan Tag Karakter/Voiceover, Maks 12-16 Kata) | Aset B-Roll & SFX | Pemicu Psikologis / Pacing |
|---|---|---|---|---|

### BAGIAN 2: LEMBAR KERJA PRODUKSI PER SCENE (MICRO-SHOTS 4-7 DETIK & DIALOG MAKSIMAL 8-14 KATA UTUH)
Rinci setiap scene dari SCENE 1 sampai SCENE N secara berkesinambungan (Rancang jumlah scene adaptif granular: 4-6 scene untuk 30-45s, 7-10 scene untuk 60s, 10-14 scene untuk 75-90s, dan 12-18 scene untuk 90-120s agar seluruh kata dramatis tetap utuh dan aman 100% di generator video AI):

### 🎬 SCENE 1 [00:00 - 00:0X]: The Hook (Penahan Scroll)
- **⏱️ Durasi**: X Detik (Detik 0 s/d X, WAJIB SINKRON dengan jumlah kata: jika 4-6 kata = 3-4s; jika 8-12 kata = 6-8s)
- **🎨 Tipe Visual**: (Sesuai Master Visual Anchor)
- **🏞️ Setting Lokasi**: (Sebutkan setting fisik nyata spesifik scene ini yang selaras dengan Master Environment Anchor, misal: Dapur Bersih - Area Kompor / Vanity Mirror Marmer Putih / Garasi Depan Kap Mesin)
- **🎨 Color Grading**: (Sesuai Master Color Grading Anchor)
- **🗣️ Voice Style**: (Sesuai Master Voice Profile Anchor)
- **🎭 Delivery & Level Energi Talent**: (Level energi suara 1-10, ekspresi wajah, tatapan mata langsung ke lensa kamera)
- **🎯 Relevansi Audiens & Diksi**: (Alasan pemilihan kata dan emosi ini untuk menarik audiens)
- **🎥 Visual & Kamera**: (Angle kamera, framing, pergerakan dinamis, ekspresi talent)
- **🎙️ Dialog Audio (Word for Word)**: (Sertakan tag karakter/voiceover di awal, misal: [Kreator]: "..." atau [Voiceover]: "..." atau [Si Boros]: "...". Kalimat hook pembuka yang jumlah katanya sinkron persis dengan durasi: MAKSIMAL 6-12 KATA)
- **🎞️ B-Roll & Aset Visual**: (Footage pendukung / visual kontekstual)
- **🔊 SFX & Transisi**: (Sound effect spesifik dan jenis transisi editor)
- **🎯 Catatan Editor & Pacing**: (Instruksi pemotongan jeda hening / ritme beat)
- **🔑 Prompt AI Video/Image (English)**: (Prompt sutradara pro komersial 6-layer siap copas untuk Kling / Runway Gen-3 / Midjourney / Sora: [Camera Motion] + [Subject Micro-Action] + [Contextual Environment & Props] + [Lens & Optics: 35mm anamorphic f/1.8] + [Studio Lighting & LUT] + [Texture Physics: subsurface scattering, 24fps, 8k uhd --ar 9:16])

### 🎬 SCENE 2 [00:0X - 00:YY]: The Curiosity Lock & Deep Agitation (Penguatan Masalah & Pembuktian Jebakan)
- **⏱️ Durasi**: Y Detik (Detik X s/d YY, WAJIB SINKRON dengan kata dialog: MAKSIMAL 12 - 16 KATA = 6 - 8 DETIK)
- **🎨 Tipe Visual**: (Konsisten dengan Master Anchor)
- **🏞️ Setting Lokasi**: (Sebutkan setting fisik nyata spesifik scene ini yang selaras dengan Master Environment Anchor)
- **🎨 Color Grading**: (Konsisten dengan Master Anchor)
- **🗣️ Voice Style**: (Konsisten dengan Master Anchor)
- **🎭 Delivery & Level Energi Talent**: (Level energi 8.5/10, ekspresi empati serius, tatapan tajam membongkar salah kaprah)
- **🎯 Relevansi Audiens & Diksi**: (Validasi kebiasaan umum audiens yang selama ini keliru)
- **🎥 Visual & Kamera**: (Angle kamera membongkar masalah, ekspresi frustasi/kontras, B-roll problem close-up)
- **🎙️ Dialog Audio (Word for Word)**: (DILARANG MEMBOCORKAN SOLUSI DI SINI! Terapkan Formula Agitasi Padat: Validasi salah kaprah + jebakan/akibat fatal. WAJIB KOMPRES KATA: MAKSIMAL 12 - 16 KATA agar tidak terpotong di video AI! Tahan tensi rasa penasaran. Sinkron durasi)
- **🎞️ B-Roll & Aset Visual**: (Visualisasi masalah, layar error, bahan terbuang, atau grafik kerugian nyata)
- **🔊 SFX & Transisi**: (SFX ketegangan, vinyl stop / muted drop, transisi hard cut)
- **🎯 Catatan Editor & Pacing**: (Pertahankan pacing tegang, potong jeda hening)
- **🔑 Prompt AI Video/Image (English)**: ...

### 🎬 SCENE 3 [00:YY - 00:ZZ]: The Mechanism & Breakthrough (Mekanisme Solusi Spesifik & Aha! Moment)
- **⏱️ Durasi**: Z Detik (Detik YY s/d ZZ, WAJIB SINKRON dengan kata dialog: MAKSIMAL 12 - 16 KATA = 6 - 8 DETIK)
- **🎨 Tipe Visual**: (Konsisten dengan Master Anchor)
- **🏞️ Setting Lokasi**: (Sebutkan setting fisik nyata spesifik scene ini yang selaras dengan Master Environment Anchor)
- **🎨 Color Grading**: (Konsisten dengan Master Anchor)
- **🗣️ Voice Style**: (Konsisten dengan Master Anchor)
- **🎭 Delivery & Level Energi Talent**: (Level energi 9/10, ekspresi antusias, pencerahan Aha! Moment)
- **🎯 Relevansi Audiens & Diksi**: ...
- **🎥 Visual & Kamera**: ...
- **🎙️ Dialog Audio (Word for Word)**: (BARU DI SINI SOLUSI PERTAMA KALI DIUNGKAP! Sebutkan NAMA SPESIFIK alat/bahan/teknik dan jelaskan MEKANISME KERJA kausalitas logis mengapa ini memecahkan masalah di Scene 2. Berikan Aha! Moment. WAJIB MAKSIMAL 12 - 16 KATA agar pas di klip AI!)
- **🎞️ B-Roll & Aset Visual**: ...
- **🔊 SFX & Transisi**: ...
- **🎯 Catatan Editor & Pacing**: ...
- **🔑 Prompt AI Video/Image (English)**: ...

### 🎬 SCENE 4 s/d SCENE (N-2): Core Steps, Case Studies, Proof & Multi-Point Demonstrations
(PANDUAN FLEKSIBEL UNTUK VIDEO PANJANG: Rinci bagian isi ini menjadi beberapa scene berurutan bernomor [Scene 4, Scene 5, Scene 6, Scene 7, dst] sesuai kebutuhan materi. SETIAP SCENE HARUS 5-8 DETIK DENGAN MAKSIMAL 12-16 KATA agar klip video AI tidak terpotong! Contoh pembagian:
- SCENE 4: Langkah Taktis 1 / Komponen Utama Solusi
- SCENE 5: Langkah Taktis 2 / Demonstrasi Penggunaan & Uji Coba Lapangan
- SCENE 6: Proof Empiris / Data Metrik Perbandingan Sebelum vs Sesudah
- SCENE 7 (jika durasi 75-120s): Mitigasi Kesalahan Fatal / Troubleshooting Praktis
Setiap scene wajib dirinci dengan format atribut lengkap yang sama seperti scene sebelumnya).

### 🎬 SCENE (N-1) [00:AA - 00:BB]: Actionable Value Bomb (Golden Rule Langsung Eksekusi)
- **⏱️ Durasi**: B Detik (Detik AA s/d BB, WAJIB SINKRON dengan kata dialog: MAKSIMAL 12 - 16 KATA = 6 - 8 DETIK)
- **🎨 Tipe Visual**: (Konsisten dengan Master Anchor)
- **🏞️ Setting Lokasi**: (Sebutkan setting fisik nyata spesifik scene ini yang selaras dengan Master Environment Anchor)
- **🎨 Color Grading**: (Konsisten dengan Master Anchor)
- **🗣️ Voice Style**: (Konsisten dengan Master Anchor)
- **🎭 Delivery & Level Energi Talent**: ...
- **🎯 Relevansi Audiens & Diksi**: ...
- **🎥 Visual & Kamera**: ...
- **🎙️ Dialog Audio (Word for Word)**: (Berikan golden rule / langkah praktis gratis yang bisa langsung dipraktekkan hari ini tanpa harus beli apapun. WAJIB MAKSIMAL 12 - 16 KATA. Sinkron durasi)
- **🎞️ B-Roll & Aset Visual**: ...
- **🔊 SFX & Transisi**: ...
- **🎯 Catatan Editor & Pacing**: ...
- **🔑 Prompt AI Video/Image (English)**: ...

### 🎬 SCENE N [00:BB - 00:CC]: The Call to Action (Jembatan Konversi Organik)
- **⏱️ Durasi**: C Detik (Detik BB s/d CC, WAJIB SINKRON dengan kata dialog: MAKSIMAL 12 - 16 KATA = 6 - 8 DETIK)
- **🎨 Tipe Visual**: (Konsisten dengan Master Anchor)
- **🏞️ Setting Lokasi**: (Sebutkan setting fisik nyata spesifik scene ini yang selaras dengan Master Environment Anchor)
- **🎨 Color Grading**: (Konsisten dengan Master Anchor)
- **🗣️ Voice Style**: (Konsisten dengan Master Anchor)
- **🎭 Delivery & Level Energi Talent**: ...
- **🎯 Relevansi Audiens & Diksi**: ...
- **🎥 Visual & Kamera**: ...
- **🎙️ Dialog Audio (Word for Word)**: (Jembatan konversi organik penutup yang mengarahkan penonton ke template/alat/link bio sebagai akselerator efisiensi. WAJIB MAKSIMAL 12 - 16 KATA. Sinkron durasi)
- **🎞️ B-Roll & Aset Visual**: ...
- **🔊 SFX & Transisi**: ...
- **🎯 Catatan Editor & Pacing**: ...
- **🔑 Prompt AI Video/Image (English)**: ...

### BAGIAN 3: REKOMENDASI TEKNIS & SOUND
- **Estimasi Jumlah Kata Audio Total**: (Maksimal rata-rata 12-16 kata per scene, total disesuaikan jumlah scene agar 100% aman anti-terpotong di klip AI video 5-10s)
- **Rekomendasi Sound/Backsound**: (Tempo BPM, mood musik, referensi BGM)
- **Tips Eksekusi Kreator**: (Lighting setup, mic gain, eye-contact to lens)
""")

MONETIZATION_BRIDGE_PROMPT = """Rancang strategi 'Monetization Bridge' (Jembatan Konversi Soft-Selling) untuk menghubungkan konten video dengan penawaran produk/jasa.

[TOPIK VIDEO]:
{topic}

[PRODUK / PENAWARAN]:
{product}

[TIPE MONETISASI]:
{monetization_type} (Afiliasi Shopee/TikTok / Produk Digital Ebook-Course / Jasa-Freelance / Lead Magnet Komunitas)

[TARGET AUDIENS]:
{audience}

Tugasmu:
Buatkan 4 skrip transisi penutup (Closing Bridge) yang mengubah penonton biasa menjadi pembeli/leads tanpa merasa sedang di-hard-sell.

Berikan 4 formula:
1. **Formula 1: The Natural Segue (Solusi Logis Kelanjutan Masalah)**
   - Transisi dari masalah di video langsung ke produk sebagai alat bantu wajib.
2. **Formula 2: The 'By Popular Demand' Bridge (Karena Banyak yang Nanya)**
   - Menggunakan efek sosial (social proof) bahwa produk ini dibuat/dipakai karena permintaan audiens.
3. **Formula 3: The Scarcity & High-Value Gift (Pemberian Nilai Berbatas Waktu)**
   - Memberikan bonus cuma-cuma (template/checklist gratis di bio) yang mengarahkan ke konversi.
4. **Formula 4: The Save & Share Trigger (Algoritma Booster + Soft Lead)**
   - Mengajak penonton bookmark video agar tidak hilang saat butuh nanti, sekaligus info link di bio.

Setiap formula harus memiliki:
- **Kalimat Transisi (The Bridge Line)**: 1-2 kalimat penghubung dari materi ke produk.
- **Skrip Audio CTA**: Kalimat ajakan penutup word-for-word.
- **Instruksi Visual**: Arah gerak tangan/tubuh (tunjuk ke profil, layar ganti ke mockup produk).
- **Teks Grafis di Layar**: Kata-kata penutup yang mencolok.
"""

CAPTION_HASHTAG_PROMPT = """Berdasarkan skrip video pendek berikut:

[TOPIK]:
{topic}

[HOOK UTAMA]:
{hook}

[RINGKASAN SKRIP]:
{script_summary}

Tugasmu:
Sebagai Pakar Optimasi SEO Media Sosial (TikTok & Instagram Reels), buatkan kit publikasi konten lengkap:

### 1. 📝 2 Variasi Caption Siap Copas (High CTR)
- **Variasi A (Storytelling & Emosional)**: Mengajak penonton membaca sampai baris terakhir.
- **Variasi B (To-The-Point & Quick Agitation)**: Kalimat tajam 2 baris untuk audiens serba cepat.
Setiap caption WAJIB menyertakan:
- Kalimat pemicu interaksi komentar (*Comment Bait Question*) yang ramah tapi memancing perdebatan sehat.
- Call to Action halus ke profil / bio.

### 2. 🏷️ Paket 10 Hashtag Terkurasi (Algoritma Booster)
Kelompokkan dalam 3 layer:
- 4 Hashtag Niche Spesifik
- 3 Hashtag Masalah / Solusi Audiens
- 3 Hashtag Komunitas / Algoritma FYP

### 3. ⏰ Rekomendasi Jam Tayang Terbaik (Prime Time)
- Rekomendasi 2 jendela waktu upload terbaik (WIB) untuk niche ini dan alasannya.
"""

SEVEN_DAY_SPRINT_PROMPT = """Rancang Kalender & Skrip Konten 7 Hari Penuh (Senin s/d Minggu) untuk video pendek viral (TikTok, Instagram Reels, YouTube Shorts).

[NICHE]:
{niche}

[TOPIK UTAMA]:
{topic}

[TARGET AUDIENS]:
{audience}

[PRODUK / PENAWARAN CTA]:
{product}

Gunakan formulasi 7 pilar konten mingguan standar agensi top:
- HARI 1 (Senin): The Myth-Buster (Membongkar Salah Kaprah Populer)
- HARI 2 (Selasa): The 3-Step Practical Tutorial (Panduan Taktis Cepat)
- HARI 3 (Rabu): The Emotional Relatability (Cerita Nyata / Empati Masalah)
- HARI 4 (Kamis): The Costly Mistake (Peringatan Kesalahan Fatal yang Bikin Rugi)
- HARI 5 (Jumat): The Secret Tool / Insider Hack (Bocoran Trik atau Alat Rahasia)
- HARI 6 (Sabtu): The Debate Trigger (Pertanyaan Kontroversial yang Memancing Diskusi)
- HARI 7 (Minggu): The Weekly Mindset & Direct CTA (Motivasi & Aksi ke Link Bio)

Untuk SETIAP HARI (Hari 1 s/d Hari 7), sajikan output lengkap dengan format Markdown yang rapi:
Setiap naskah WAJIB padat daging (high value density), menyebutkan nama teknik/alat/bahan konkret, dan menyertakan data empiris atau kausalitas logis mengapa solusi tersebut bekerja:

### HARI [nomor]: [Nama_Hari] - [Judul_Konsep]
- **Pilar Strategi**: [Nama Pilar]
- **Hook 3 Detik (Audio)**: "[Kalimat pembuka verbal yang nendang, berakar pada fakta/masalah nyata]"
- **Instruksi Visual (Kamera/Aksi)**: [Gerakan tubuh / B-roll]
- **Teks di Layar**: "[Tulisan besar mencolok]"
- **Kerangka Narasi 60 Detik Berbobot**:
  - *Detik 0-15 (Agitasi & Akar Masalah)*: [Bongkar akar masalah sesungguhnya, bukan sekadar menyalahkan audiens]
  - *Detik 15-40 (Mekanisme Solusi & Data Empiris)*: [Sebutkan nama alat/bahan/teknik spesifik, metrik terukur, dan kausalitas logis 'Aha! Moment']
  - *Detik 40-60 (Golden Rule Taktis & Call to Action)*: [Langkah taktis yang bisa langsung dipraktekkan hari ini juga + CTA organik]
- **Jembatan Penutup (CTA)**: [Kalimat ajakan ke profil/produk]
- **Caption Siap Copas**:
  [Caption padat 2-3 baris + Pertanyaan interaksi komentar]
- **Hashtag**: #[tag1] #[tag2] #[tag3] #[tag4] #[tag5]
---
"""

ACCOUNT_GROWTH_BLUEPRINT_PROMPT = """Kamu adalah Master Ahli Strategi Pertumbuhan Akun Media Sosial (Social Media Growth Director) dengan pengalaman membawa akun dari 0 hingga 500k+ followers organik serta mencetak ratusan juta rupiah dari TikTok Shop, Reels, dan YouTube Shorts.

[DATA AKUN & PROFIL KREATOR]:
- Niche / Industri: {niche}
- Platform Utama: {platform}
- Handle / Username Saat Ini: {current_handle}
- Bio Profil Saat Ini: {current_bio}
- Target Audiens Spesifik: {audience}
- Model Monetisasi & Penawaran: {monetization_goal}
- Nilai Tambah Unik (USP) / Masalah yang Diselesaikan: {usp}

Tugasmu:
Buatkan "Master Blueprint Pertumbuhan Akun & Monetisasi A-Z" yang sangat taktis, komprehensif, dan siap langsung diterapkan:

### 1. 🔍 Audit & Optimasi Bio Profil (3 Detik First Impression)
- **Rekomendasi Handle & Display Name SEO**: Kombinasi nama & kata kunci pencarian yang mudah ditemukan di mesin pencari TikTok/IG.
- **3 Variasi Bio Profil Formula 3 Detik (Konversi Tinggi)**:
  - *Variasi 1 (Otoritas & Transformasi)*: Siapa yang Anda bantu + Hasil nyata + CTA ke link bio.
  - *Variasi 2 (Relatable & Story)*: Keresahan yang dialami + Bukti nyata + CTA.
  - *Variasi 3 (To-The-Point & Agitatif)*: Kalimat padat tanpa basa-basi yang langsung menyentil kebutuhan audiens.
- **Arsitektur Struktur Link in Bio**: Urutan tombol link bio terbaik (Freebie/Lead Magnet ➔ Produk Utama ➔ Konsultasi/Sosmed).

### 2. 🏛️ Matriks 4 Pilar Konten (The 40-30-20-10 Authority Formula)
Susun proporsi tema konten mingguan agar akun tidak membosankan dan dicintai algoritma:
- **Pilar 1: Otoritas & Solusi Taktis (40%)**: Konten edukasi mendalam berbasis bukti empiris, mekanisme riil, dan data terukur yang membuktikan otoritas Anda (anti-saran klise). Berikan 2 contoh judul konten spesifik.
- **Pilar 2: Relatabilitas & Storytelling Emosional (30%)**: Konten cerita nyata, kesalahan pribadi, dan empati masalah. Berikan 2 contoh judul konten spesifik.
- **Pilar 3: Debat, Mitos & Hard Truth (20%)**: Konten kontradiktif yang memicu perdebatan sehat dan lonjakan komentar berbasis fakta tandingan. Berikan 2 contoh judul konten spesifik.
- **Pilar 4: Soft-Selling & Jembatan Konversi (10%)**: Konten yang menyambungkan masalah ke produk penawaran. Berikan 2 contoh judul konten spesifik.

### 3. 📈 Roadmap 30 Hari Pertumbuhan Akun (Step-by-Step Blueprint)
- **Minggu 1 (Fondasi & Algoritma Warm-Up)**: Aktivitas penting akun baru (pemanasan algoritma, 5 video pilar pertama).
- **Minggu 2 (Tes Gelombang FYP & Retensi)**: Eksperimen 3 sudut pandang hook dan pemantauan metrik retensi 3 detik.
- **Minggu 3 (Membangun Komunitas & Follower Retention)**: Teknik interaksi balas komentar dengan video (Video Replies) untuk mengunci followers.
- **Minggu 4 (Aktivasi Jembatan Monetisasi)**: Waktu dan cara memasukkan Call-to-Action produk pertama tanpa merusak distribusi algoritma.

### 4. ⚠️ 3 Blunder Fatal yang Wajib Dihindari
- 3 kesalahan teknis atau konten yang sering membuat akun terjebak di 200-view jail atau shadowban buatan, serta cara mencegahnya.
"""
