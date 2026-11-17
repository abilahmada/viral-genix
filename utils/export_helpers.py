"""
ViralGenix - Export & Formatting Helpers
Membantu mengekspor hasil skrip, storyboard, dan analisis ke file Markdown dan CSV.
"""

import io
import re
import pandas as pd
from typing import Optional

def markdown_table_to_dataframe(md_text: str) -> Optional[pd.DataFrame]:
    """
    Mengonversi tabel markdown atau outline narasi di dalam teks menjadi pandas DataFrame.
    Mendukung format tabel pipa (| col |) dan format kerangka narasi berbutir (Sprint 7 Hari).
    """
    if not md_text or not md_text.strip():
        return None

    lines = md_text.strip().split("\n")
    table_lines = [l for l in lines if l.strip().startswith("|") and l.strip().endswith("|")]
    
    if len(table_lines) >= 3:
        try:
            # Header
            headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]
            
            # Rows (lewati baris divider index 1)
            rows = []
            for line in table_lines[2:]:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) == len(headers):
                    rows.append(cells)
                elif len(cells) > len(headers):
                    rows.append(cells[:len(headers)])
                else:
                    cells += [""] * (len(headers) - len(cells))
                    rows.append(cells)

            if rows:
                return pd.DataFrame(rows, columns=headers)
        except Exception:
            pass

    # Fallback: Ekstraksi dari format outline / kerangka narasi (misal hasil Sprint 7 Hari)
    return outline_to_dataframe(md_text)


def outline_to_dataframe(md_text: str) -> Optional[pd.DataFrame]:
    """Mengonversi outline narasi berbutir (Detik 0-15, 15-40, 40-60) menjadi DataFrame produksi."""
    headers = [
        "Detik",
        "Visual / B-Roll Camera Direction",
        "Skrip Audio (Word for Word)",
        "Teks di Layar (On-Screen Text)",
        "Pemicu Psikologis"
    ]
    rows = []

    # 1. Ekstrak Hook 3 Detik
    hook_m = re.search(r'Hook 3 Detik.*?:\s*(?:_|\*|")?([^"\*\_\n]+)', md_text, re.IGNORECASE)
    hook_val = hook_m.group(1).strip() if hook_m else ""

    vis_m = re.search(r'Instruksi Visual.*?:\s*(?:_|\*|")?([^\n\*\"]+)', md_text, re.IGNORECASE)
    vis_val = vis_m.group(1).strip() if vis_m else "Close-up wajah kreator, tatapan tajam ke arah lensa kamera"

    screen_m = re.search(r'Teks di Layar.*?:\s*(?:_|\*|")?([^\n\*\"]+)', md_text, re.IGNORECASE)
    screen_val = screen_m.group(1).strip() if screen_m else "PERHATIKAN INI! ⚠️"

    pilar_m = re.search(r'Pilar Strategi.*?:\s*(?:_|\*|")?([^\n\*\"]+)', md_text, re.IGNORECASE)
    pilar_val = pilar_m.group(1).strip() if pilar_m else "Pattern Interrupt & Dopamin Spike"

    if hook_val:
        rows.append(["00-03", vis_val, hook_val, screen_val, pilar_val])

    # 2. Ekstrak fase narasi detik demi detik
    beats = re.findall(
        r'[\*\-]\s*\*?Detik\s*(\d+\s*[\-\–]\s*\d+)\s*(?:\((.*?)\))?\*?:\s*(.*?)(?=\n\s*[\*\-]\s*\*?Detik|\n\s*[\*\-]\s*\*?Jembatan|\n\s*[\*\-]\s*\*?Caption|\Z)',
        md_text,
        re.DOTALL | re.IGNORECASE
    )

    for time_span, phase_name, audio_desc in beats:
        clean_time = time_span.replace(" ", "")
        clean_audio = audio_desc.strip().strip('"').strip('*').strip()
        phase = phase_name.strip() if phase_name else "Retensi Konten"
        vis_dir = "B-Roll cepat sesuai masalah" if "agitasi" in phase.lower() or "masalah" in phase.lower() else "Demonstrasi solusi / B-Roll pendukung"
        text_screen = "MASALAH UTAMA ❌" if "agitasi" in phase.lower() else ("SOLUSI NYATA 🔥" if "solusi" in phase.lower() else "INFO PENTING 💡")
        rows.append([clean_time, vis_dir, clean_audio, text_screen, f"{phase} (Retensi Tinggi)"])

    # 3. Ekstrak CTA / Jembatan Penutup jika belum ada di beat
    cta_m = re.search(r'Jembatan Penutup.*?:?\s*(?:_|\*|")?([^"\*\_\n]+)', md_text, re.IGNORECASE)
    if cta_m:
        cta_val = cta_m.group(1).strip()
        has_cta_row = any("60" in r[0] for r in rows)
        if not has_cta_row:
            rows.append(["50-60", "Close-up ke kamera, tunjuk ke arah bio", cta_val, "KLIK LINK DI BIO 🔗", "Call to Action (Konversi)"])

    if rows:
        return pd.DataFrame(rows, columns=headers)

    # 4. Fallback jika hanya teks narasi bebas (split per kalimat/paragraf)
    paragraphs = [p.strip() for p in md_text.split("\n") if len(p.strip()) > 20 and not p.strip().startswith("#")]
    if paragraphs:
        step_len = max(5, 60 // len(paragraphs[:5]))
        for idx, p in enumerate(paragraphs[:5]):
            start = idx * step_len
            end = min(60, (idx + 1) * step_len)
            rows.append([f"{start:02d}-{end:02d}", "Arahan B-roll visual sesuai narasi", p, "POIN PENTING 📌", "Retensi Narasi"])
        return pd.DataFrame(rows, columns=headers)

    return None

def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Mengonversi DataFrame ke bytes CSV UTF-8 dengan BOM agar terbaca sempurna di Excel."""
    return df.to_csv(index=False).encode('utf-8-sig')

def prepare_markdown_download(content: str, title: str = "viralgenix_output") -> bytes:
    """Mempersiapkan teks markdown untuk diunduh."""
    header = f"# {title.replace('_', ' ').title()}\n*Dihasilkan oleh ViralGenix AI Content Intelligence*\n\n---\n\n"
    full_doc = header + content
    return full_doc.encode('utf-8')

def markdown_table_to_srt(md_text: str) -> Optional[bytes]:
    """
    Mengonversi tabel storyboard detik demi detik menjadi file Subtitle (.srt)
    yang dapat diimpor langsung ke CapCut, Premiere Pro, atau DaVinci Resolve.
    """
    df = markdown_table_to_dataframe(md_text)
    if df is None:
        return None

    # Cari kolom detik dan kolom skrip audio/teks layar
    col_sec = None
    col_text = None
    for c in df.columns:
        c_l = c.lower()
        if "detik" in c_l or "sec" in c_l or "time" in c_l:
            col_sec = c
        elif "audio" in c_l or "skrip" in c_l or "dialog" in c_l:
            col_text = c

    if not col_sec:
        col_sec = df.columns[0]
    if not col_text and len(df.columns) > 2:
        col_text = df.columns[2]

    srt_entries = []
    counter = 1
    current_sec = 0

    for _, row in df.iterrows():
        time_raw = str(row[col_sec])
        text_raw = str(row[col_text]).strip().strip('"').strip('*')
        if not text_raw:
            continue

        # Ekstrak angka detik (misal: "00 - 03" atau "3-15")
        numbers = re.findall(r'\d+', time_raw)
        if len(numbers) >= 2:
            start_s = int(numbers[0])
            end_s = int(numbers[1])
        elif len(numbers) == 1:
            start_s = int(numbers[0])
            end_s = start_s + 4
        else:
            start_s = current_sec
            end_s = start_s + 4

        current_sec = end_s

        start_time_str = f"00:{start_s//60:02d}:{start_s%60:02d},000"
        end_time_str = f"00:{end_s//60:02d}:{end_s%60:02d},000"

        srt_entries.append(f"{counter}\n{start_time_str} --> {end_time_str}\n{text_raw}\n")
        counter += 1

    if srt_entries:
        full_srt = "\n".join(srt_entries)
        return full_srt.encode('utf-8')
    return None


def parse_master_consistency_anchor(storyboard_text: str) -> dict:
    """
    Mengekstraksi Bagian 0: Master Production Consistency Anchor dari teks storyboard.
    Mencakup Style Lock Prompt AI, Character Anchor, Setting Lokasi, Color Grading, dan Voice Profile.
    """
    if not storyboard_text or not storyboard_text.strip():
        return {}

    anchor = {
        "content_theme": "",
        "target_audience": "",
        "audience_tone_slang": "",
        "emotional_trigger": "",
        "visual_style_lock": "",
        "character_anchor": "",
        "environment_anchor": "",
        "color_grading_anchor": "",
        "voice_profile_anchor": ""
    }

    def _get_val(patterns):
        for p in patterns:
            m = re.search(p, storyboard_text, re.IGNORECASE)
            if m:
                return m.group(1).strip().strip('*').strip('_').strip('"')
        return ""

    anchor["content_theme"] = _get_val([
        r'[\*\-]\s*(?:\🎯\s*)?Pilar\s*Tema\s*Konten[^\:]*:\s*([^\n]+)',
        r'Tema\s*Konten[^\:]*:\s*([^\n]+)'
    ])
    anchor["target_audience"] = _get_val([
        r'[\*\-]\s*(?:\👥\s*)?Target\s*Audiens\s*Persona[^\:]*:\s*([^\n]+)',
        r'Target\s*Audiens[^\:]*:\s*([^\n]+)'
    ])
    anchor["audience_tone_slang"] = _get_val([
        r'[\*\-]\s*(?:\🗣️\s*)?Gaya\s*Sapaan\s*(?:&|dan)?\s*Diksi[^\:]*:\s*([^\n]+)',
        r'Sapaan\s*&\s*Diksi[^\:]*:\s*([^\n]+)',
        r'Gaya\s*Bahasa[^\:]*:\s*([^\n]+)'
    ])
    anchor["emotional_trigger"] = _get_val([
        r'[\*\-]\s*(?:\⚡\s*)?Trigger\s*Emosi\s*Dominan[^\:]*:\s*([^\n]+)',
        r'Trigger\s*Emosi[^\:]*:\s*([^\n]+)',
        r'Pemicu\s*Emosi[^\:]*:\s*([^\n]+)'
    ])

    anchor["visual_style_lock"] = _get_val([
        r'[\*\-]\s*(?:\🧬\s*)?Master\s*Visual\s*Style\s*Lock[^\:]*:\s*([^\n]+)',
        r'Visual\s*Style\s*Lock[^\:]*:\s*([^\n]+)',
        r'Style\s*Lock[^\:]*:\s*([^\n]+)'
    ])
    anchor["character_anchor"] = _get_val([
        r'[\*\-]\s*(?:\👤\s*)?Master\s*Character[^\:]*:\s*([^\n]+)',
        r'Character\s*(?:/|dan)?\s*Subject\s*Anchor[^\:]*:\s*([^\n]+)',
        r'Subjek\s*Karakter[^\:]*:\s*([^\n]+)'
    ])
    anchor["environment_anchor"] = _get_val([
        r'[\*\-]\s*(?:\🏞️\s*)?Master\s*Environment[^\:]*:\s*([^\n]+)',
        r'Environment\s*Anchor[^\:]*:\s*([^\n]+)',
        r'Setting\s*Lokasi\s*Master[^\:]*:\s*([^\n]+)'
    ])
    anchor["color_grading_anchor"] = _get_val([
        r'[\*\-]\s*(?:\🎨\s*)?Master\s*Color\s*Grading[^\:]*:\s*([^\n]+)',
        r'Color\s*Grading\s*Anchor[^\:]*:\s*([^\n]+)',
        r'Palet\s*Warna\s*Master[^\:]*:\s*([^\n]+)'
    ])
    anchor["voice_profile_anchor"] = _get_val([
        r'[\*\-]\s*(?:\🎙️\s*)?Master\s*Voice\s*Profile[^\:]*:\s*([^\n]+)',
        r'Voice\s*Profile\s*Anchor[^\:]*:\s*([^\n]+)',
        r'Karakter\s*Vokal\s*Master[^\:]*:\s*([^\n]+)'
    ])

    return anchor


def parse_content_angles(text: str, fallback_topic: str = "") -> list:
    """
    Mengekstraksi 5 Sudut Pandang Konten (Content Angles) dari hasil riset celah pasar (Tahap 1).
    Menghasilkan list dictionary yang siap ditampilkan sebagai kartu / radio button interaktif di UI
    tanpa ada teks yang terpotong.
    """
    if not text or not text.strip():
        return []

    angles = []
    
    # Ambil teks setelah bagian "### 2." jika ada untuk mempersempit pencarian
    sec2_m = re.search(r'###\s*2\.[^\n]*\n(.*?)(?=\n###\s*3\.|\Z)', text, re.DOTALL | re.IGNORECASE)
    search_text = sec2_m.group(1) if sec2_m else text

    # Split berdasarkan penomoran 1 s/d 5 (misal: "1. **Angle...", "2. **Angle...")
    raw_blocks = re.split(r'(?:\n|\A)(?=[1-5]\.\s+)', search_text)
    candidate_blocks = [b.strip() for b in raw_blocks if re.match(r'^[1-5]\.\s+', b.strip())]

    # Jika pemisahan [1-5]. tidak menemukan blok, coba pemisahan alternatif dengan header "Angle"
    if not candidate_blocks:
        raw_blocks_alt = re.split(r'(?:\n|\A)(?=(?:\#\#\#|\*\*)\s*(?:Angle|\d+))', search_text, flags=re.IGNORECASE)
        candidate_blocks = [b.strip() for b in raw_blocks_alt if "judul" in b.lower() or "premis" in b.lower() or "angle" in b.lower()]

    for idx, block in enumerate(candidate_blocks[:5]):
        lines = block.split("\n")
        first_line = lines[0].strip()

        # Ekstrak nama angle (misal: "Angle Kontradiktif / Myth-Buster")
        angle_name_m = re.search(r'^[1-5]\.\s*\*{0,2}(.*?)(?:\*{0,2}\:|\Z)', first_line)
        if angle_name_m:
            angle_name = angle_name_m.group(1).strip().strip('*').strip('_')
        else:
            angle_name = f"Sudut Pandang #{idx+1}"

        def _get_field_val(header_names, stop_headers):
            h_pattern = r'(?:' + '|'.join(header_names) + r')'
            s_pattern = r'(?:' + '|'.join(stop_headers) + r'|\d+\.|\Z)'
            
            # 1. Coba pencarian multiline hingga stop_header berikutnya
            m = re.search(
                r'[\*\-]?\s*\*{0,2}' + h_pattern + r'[^\:\n]*\*{0,2}\s*:\s*([\s\S]+?)(?=\n\s*[\*\-]?\s*\*{0,2}' + s_pattern + r')',
                block,
                re.IGNORECASE
            )
            if m:
                val = m.group(1).strip()
                val = re.sub(r'^[\s\*\_\'\"\>]+|[\s\*\_\'\"\>]+$', '', val)
                return ' '.join(val.split())
            
            # 2. Fallback pencarian 1 baris
            m_line = re.search(
                r'[\*\-]?\s*\*{0,2}' + h_pattern + r'[^\:\n]*\*{0,2}\s*:\s*([^\n]+)',
                block,
                re.IGNORECASE
            )
            if m_line:
                val = m_line.group(1).strip()
                val = re.sub(r'^[\s\*\_\'\"\>]+|[\s\*\_\'\"\>]+$', '', val)
                return ' '.join(val.split())
            return ""

        title = _get_field_val(
            ['Judul Konsep', 'Judul'],
            ['Trigger Emosi', 'Premis', 'Estimasi Potensi', 'Potensi Viral']
        )

        premise = _get_field_val(
            ['Premis Cerita & Data Empiris', 'Premis Cerita', 'Premis'],
            ['Estimasi Potensi', 'Trigger Emosi', 'Potensi Viral', 'Judul']
        )

        trigger = _get_field_val(
            ['Trigger Emosi Utama', 'Trigger Emosi', 'Trigger'],
            ['Estimasi Potensi', 'Premis', 'Judul', 'Potensi Viral']
        )

        viral_pot = _get_field_val(
            ['Estimasi Potensi Viral', 'Potensi Viral'],
            ['Trigger', 'Premis', 'Judul']
        )

        # Jika title belum ada, ambil dari deskripsi pada first_line jika ada pemisah titik dua
        if not title and ":" in first_line:
            parts = first_line.split(":", 1)
            if len(parts) > 1 and len(parts[1].strip()) > 3:
                title = parts[1].strip().strip('*').strip('_').strip('"')

        if not title:
            title = f"{angle_name}"

        if not premise:
            other_lines = [l.strip().lstrip('*-').strip() for l in lines[1:] if len(l.strip()) > 10 and not l.strip().startswith("#")]
            premise = other_lines[0] if other_lines else title

        if premise and premise.lower() not in title.lower():
            full_concept = f"{title}. {premise}"
        else:
            full_concept = title

        angles.append({
            "id": idx + 1,
            "angle_name": angle_name,
            "title": title,
            "premise": premise,
            "trigger": trigger or "Penasaran tinggi & validasi solusi",
            "viral_pot": viral_pot or "Sangat Tinggi 🔥",
            "full_concept": full_concept,
            "display_label": f"#{idx+1} [{angle_name}]: {title}"
        })

    # Jika parsing menghasilkan < 2 angles, gunakan smart fallback berbasis keyword
    if len(angles) < 2 and fallback_topic:
        smart_angles = [
            ("Angle Kontradiktif / Myth-Buster", f"Bongkar mitos terbesar tentang {fallback_topic} yang bikin banyak orang gagal", "Membongkar cara lama yang salah dan menyajikan solusi cepat berbasis data."),
            ("Angle Rahasia Orang Dalam / Insider Secret", f"Rahasia tersembunyi {fallback_topic} yang cuma diketahui top 1%", "Mengungkap teknik rahasia dan tools spesifik tanpa modal besar."),
            ("Angle Realita Pahit / Hard Truth", f"Fakta pahit kenapa 90% orang gagal di {fallback_topic}", "Kejujuran brutal yang membuka mata penonton agar sadar akar masalah struktural."),
            ("Angle Hack Cepat / Low Effort High Result", f"Cara tercepat kuasai {fallback_topic} dalam hitungan hari", "Langkah taktis 1-2-3 yang langsung bisa dipraktekkan hari ini dengan hasil terukur."),
            ("Angle Peringatan Masa Depan / Warning", f"Apa yang bakal terjadi kalau lu gak mulai {fallback_topic} sekarang", "Urgensi dan ketakutan tertinggal pergeseran tren terbaru (FOMO).")
        ]
        angles = []
        for idx, (ang, tit, prem) in enumerate(smart_angles):
            angles.append({
                "id": idx + 1,
                "angle_name": ang,
                "title": tit,
                "premise": prem,
                "trigger": "FOMO & Solusi Instan",
                "viral_pot": "Sangat Tinggi 🔥",
                "full_concept": f"{tit}. {prem}",
                "display_label": f"#{idx+1} [{ang}]: {tit}"
            })

    return angles


def parse_hook_variations(text: str, fallback_topic: str = "") -> list:
    """
    Mengekstraksi 10 Variasi Hook dari hasil perumusan hook (Tahap 2).
    Mendukung pengelompokan 4 pilar psikologi (FOMO, Curiosity, Gain, Empathy)
    dan mengekstraksi Hook Verbal, Visual, Teks Layar, dan Skor Retensi secara utuh tanpa terpotong.
    """
    if not text or not text.strip():
        return []

    hooks = []

    # Pisahkan berdasarkan kategori atau pilar
    cat_blocks = re.split(r'(?:\n|\A)(?=\#\#\#\s*(?:Kategori|Pilar)\s*\d+)', text, flags=re.IGNORECASE)

    hook_counter = 1

    for c_block in cat_blocks:
        c_lines = c_block.strip().split("\n")
        first_c_line = c_lines[0].strip() if c_lines else ""

        # Deteksi nama pilar psikologi
        c_lower = c_block.lower()
        if "fomo" in c_lower or "kerugian" in c_lower or "ketakutan" in c_lower:
            cat_pillar = "😱 FOMO & Kerugian (Fear of Loss)"
        elif "curiosity" in c_lower or "keingintahuan" in c_lower or "misteri" in c_lower:
            cat_pillar = "👀 Keingintahuan Ekstrem (Curiosity Gap)"
        elif "gain" in c_lower or "keuntungan" in c_lower or "kemudahan" in c_lower or "greed" in c_lower:
            cat_pillar = "💰 Keuntungan Maksimal & Kemudahan (High Gain)"
        elif "empati" in c_lower or "validasi" in c_lower or "identity" in c_lower or "relatab" in c_lower:
            cat_pillar = "🤝 Validasi & Empati (Identity / Relatability)"
        else:
            cat_pillar = "🔥 Rekomendasi Hook Pilihan"

        # Pisahkan variasi di dalam blok kategori
        var_chunks = re.split(
            r'(?:\n|\A)(?=(?:[\*\-]\s*)?(?:Variasi\s*\d+|[1-9]\d?\.\s*(?:\*\*)?Hook|\*{0,2}Hook\s*(?:Verbal)?\s*\d*|\#{3,4}\s*Variasi))',
            c_block,
            flags=re.IGNORECASE
        )

        for chunk in var_chunks:
            if not chunk.strip():
                continue

            def _get_hook_field(header_names, stop_headers):
                h_pattern = r'(?:' + '|'.join(header_names) + r')'
                s_pattern = r'(?:' + '|'.join(stop_headers) + r'|\d+\.|\Z)'
                
                # 1. Coba pencarian multiline hingga stop_header berikutnya
                m = re.search(
                    r'[\*\-]?\s*\*{0,2}' + h_pattern + r'[^\:\n]*\*{0,2}\s*:\s*([\s\S]+?)(?=\n\s*[\*\-]?\s*\*{0,2}' + s_pattern + r')',
                    chunk,
                    re.IGNORECASE
                )
                if m:
                    val = m.group(1).strip()
                    val = re.sub(r'^[\s\*\_\'\"\>]+|[\s\*\_\'\"\>]+$', '', val)
                    return ' '.join(val.split())
                
                # 2. Fallback pencarian 1 baris
                m_line = re.search(
                    r'[\*\-]?\s*\*{0,2}' + h_pattern + r'[^\:\n]*\*{0,2}\s*:\s*([^\n]+)',
                    chunk,
                    re.IGNORECASE
                )
                if m_line:
                    val = m_line.group(1).strip()
                    val = re.sub(r'^[\s\*\_\'\"\>]+|[\s\*\_\'\"\>]+$', '', val)
                    return ' '.join(val.split())
                return ""

            verbal = _get_hook_field(
                ['Hook Verbal', 'Audio', 'Hook Audio', 'Hook'],
                ['Instruksi Visual', 'Visual', 'Teks di Layar', 'Text on Screen', 'Pijakan Fakta', 'Skor Retensi', 'Skor']
            )

            if not verbal or len(verbal) < 8:
                continue

            visual = _get_hook_field(
                ['Instruksi Visual', 'Visual', 'B-Roll'],
                ['Teks di Layar', 'Text on Screen', 'Pijakan Fakta', 'Skor Retensi', 'Skor', 'Hook Verbal']
            )

            screen = _get_hook_field(
                ['Teks di Layar', 'Text on Screen', 'Teks Layar'],
                ['Pijakan Fakta', 'Skor Retensi', 'Skor', 'Instruksi Visual', 'Hook Verbal']
            )

            fact_anchor = _get_hook_field(
                ['Pijakan Fakta', 'Nilai Materi', 'Fakta Empiris'],
                ['Skor Retensi', 'Skor', 'Teks di Layar', 'Instruksi Visual']
            )

            score = _get_hook_field(
                ['Skor Retensi', 'Skor'],
                ['Variasi', 'Kategori', 'Pilar', 'Hook']
            )
            score_num = re.search(r'\d+', score).group(0) if re.search(r'\d+', score) else "94"

            # Cegah duplikasi
            if any(h["verbal"] == verbal for h in hooks):
                continue

            cat_short = cat_pillar.split()[0] + " " + cat_pillar.split()[1] if len(cat_pillar.split()) > 1 else cat_pillar
            hooks.append({
                "id": hook_counter,
                "category": cat_pillar,
                "verbal": verbal,
                "visual": visual or "Close-up kreator bicara tegas ke lensa kamera HP",
                "screen_text": screen or "PERHATIKAN INI! ⚠️",
                "fact_anchor": fact_anchor or "Materi edukasi taktis terukur",
                "score": f"{score_num}/100",
                "display_label": f"#{hook_counter} [{cat_short}] \"{verbal}\" (Skor: {score_num})"
            })
            hook_counter += 1

    # Fallback jika parsing blok hanya menghasilkan < 3 hooks
    if len(hooks) < 3:
        all_verbals = re.findall(
            r'[\*\-]?\s*\*{0,2}(?:Hook\s*Verbal(?:\s*\(Audio\))?|Hook\s*Audio|Hook\s*Verbal)[^\:\n]*\*{0,2}\s*:\s*([^\n]+)',
            text,
            re.IGNORECASE
        )
        for cl_v in all_verbals:
            clean = cl_v.strip()
            clean = re.sub(r'^[\s\*\_\'\"\>]+|[\s\*\_\'\"\>]+$', '', clean)
            if len(clean) > 8 and not any(h["verbal"] == clean for h in hooks):
                hooks.append({
                    "id": len(hooks) + 1,
                    "category": "🔥 Hook Pilihan",
                    "verbal": clean,
                    "visual": "Kreator menatap langsung ke arah lensa kamera",
                    "screen_text": "INFO PENTING 💡",
                    "fact_anchor": "Fakta penting terukur",
                    "score": "95/100",
                    "display_label": f"#{len(hooks)+1} [🔥 Hook Pilihan] \"{clean}\" (Skor: 95)"
                })

    # Fallback terakhir jika text masih belum menghasilkan hook sama sekali
    if not hooks and fallback_topic:
        default_templates = [
            ("😱 FOMO & Kerugian", f"Stop scroll kalau lu gak mau rugi waktu dan duit cuma gara-gara salah paham soal {fallback_topic}!", "97"),
            ("😱 FOMO & Kerugian", f"90% orang yang nyoba {fallback_topic} bakal gagal total kalau mereka gak tahu satu hal krusial ini.", "95"),
            ("👀 Keingintahuan Ekstrem", f"Ada satu trik rahasia tentang {fallback_topic} yang sengaja disembunyiin dari lu selama ini.", "96"),
            ("👀 Keingintahuan Ekstrem", f"Jangan pernah lakuin {fallback_topic} sebelum lu nonton video 60 detik ini sampai habis!", "94"),
            ("💰 Keuntungan Maksimal", f"Ternyata cuma butuh 1 trik simpel ini buat hasilin lompatan besar di {fallback_topic}!", "93"),
            ("💰 Keuntungan Maksimal", f"Cara termudah kuasai {fallback_topic} modal HP tanpa ribet dan tanpa modal gede.", "92"),
            ("🤝 Validasi & Empati", f"Lu juga ngerasa capek gak sih, udah berusaha maksimal di {fallback_topic} tapi hasilnya masih nihil?", "95"),
            ("🤝 Validasi & Empati", f"Gua tahu lu udah hampir nyerah soal {fallback_topic}, tapi dengerin gua sebentar aja.", "94")
        ]
        for idx, (cat, vb, sc) in enumerate(default_templates):
            cat_short = cat.split()[0] + " " + cat.split()[1] if len(cat.split()) > 1 else cat
            hooks.append({
                "id": idx + 1,
                "category": cat,
                "verbal": vb,
                "visual": "Kreator tatapan fokus ke lensa kamera, ekspresi serius",
                "screen_text": "RAHASIA TERBONGKAR 🔥",
                "fact_anchor": f"Nilai praktis {fallback_topic}",
                "score": f"{sc}/100",
                "display_label": f"#{idx+1} [{cat_short}] \"{vb}\" (Skor: {sc})"
            })

    return hooks


def extract_duration_seconds(dur_text: str = "", timing_text: str = "") -> int:
    """
    Mengekstrak durasi detik secara presisi dari berbagai variasi penulisan:
    - '12 Detik (Detik 26-38)' -> 12
    - '00:26 - 00:38' -> 12
    - '00:03 - 00:14' -> 11
    - '00 - 03' -> 3
    - '26 - 38' -> 12
    - '3 Detik' -> 3
    """
    combined = f"{dur_text} {timing_text}".strip()
    if not combined:
        return 10

    # 1. Prioritaskan jika tertulis angka eksplisit diikuti 'detik'/'sec'/'s'
    m_explicit = re.search(r'(\d+)\s*(?:detik|second|sec|s\b)', combined, re.IGNORECASE)
    if m_explicit:
        val = int(m_explicit.group(1))
        if 1 <= val <= 180:
            return val

    # 2. Cek format range waktu MM:SS - MM:SS (contoh: 00:26 - 00:38)
    m_range_colon = re.search(r'(\d+):(\d+)\s*[-–—]\s*(\d+):(\d+)', combined)
    if m_range_colon:
        start_sec = int(m_range_colon.group(1)) * 60 + int(m_range_colon.group(2))
        end_sec = int(m_range_colon.group(3)) * 60 + int(m_range_colon.group(4))
        diff = end_sec - start_sec
        if 1 <= diff <= 120:
            return diff

    # 3. Cek format range angka biasa (contoh: Detik 26-38 atau 00 - 03)
    m_range_simple = re.search(r'(\d+)\s*[-–—]\s*(\d+)', combined)
    if m_range_simple:
        start_sec = int(m_range_simple.group(1))
        end_sec = int(m_range_simple.group(2))
        diff = abs(end_sec - start_sec)
        if 1 <= diff <= 120:
            return diff

    # 4. Fallback angka integer pertama
    nums = re.findall(r'\d+', combined)
    if nums:
        val = int(nums[0])
        if 1 <= val <= 120:
            return val

    return 10


def parse_storyboard_scenes(storyboard_text: str) -> list:
    """
    Mengekstraksi scene demi scene dari storyboard untuk kebutuhan produksi video.
    Mendukung format '### 🎬 SCENE X' yang kaya informasi maupun tabel markdown pipa (| col |).
    Menghasilkan list dictionary per scene yang siap di-copas atau dirender di UI.
    """
    if not storyboard_text or not storyboard_text.strip():
        return []

    # Ekstrak Master Production & Audience Consistency Anchor terlebih dahulu
    master_anchor = parse_master_consistency_anchor(storyboard_text)
    master_env = master_anchor.get("environment_anchor", "").strip()
    master_vis = master_anchor.get("visual_style_lock", "").strip()
    master_color = master_anchor.get("color_grading_anchor", "").strip()
    master_voice = master_anchor.get("voice_profile_anchor", "").strip()

    scenes = []

    # Metode 1: Coba deteksi blok '### 🎬 SCENE' atau '### SCENE'
    scene_blocks = re.split(r'###\s*(?:🎬\s*)?SCENE\s*(\d+)', storyboard_text, flags=re.IGNORECASE)
    if len(scene_blocks) > 1:
        for i in range(1, len(scene_blocks), 2):
            s_num = scene_blocks[i].strip()
            s_body = scene_blocks[i+1] if i+1 < len(scene_blocks) else ""

            lines = s_body.strip().split("\n")
            first_line = lines[0].strip().strip(":").strip() if lines else ""

            time_m = re.search(r'\[([^\]]+)\]|\(([^)]+)\)', first_line)
            timing_val = time_m.group(1) or time_m.group(2) if time_m else ""
            title_clean = re.sub(r'\[[^\]]+\]|\([^)]+\)', '', first_line).strip().strip(":").strip()
            if not title_clean:
                title_clean = f"Scene {s_num}"

            def _extract_field(patterns):
                for p in patterns:
                    m = re.search(p, s_body, re.IGNORECASE)
                    if m:
                        return m.group(1).strip().strip('*').strip('_').strip('"')
                return ""

            dur_val = _extract_field([
                r'[\*\-]\s*(?:\⏱️\s*)?Durasi\s*:\s*([^\n]+)',
                r'Durasi\s*:\s*([^\n]+)'
            ])
            if not timing_val and dur_val:
                timing_val = dur_val

            # Hitung estimasi durasi visual klip secara presisi
            duration_sec = extract_duration_seconds(dur_val, timing_val)

            vis_style_val = _extract_field([
                r'[\*\-]\s*(?:\🎨\s*)?Tipe\s*Visual\s*:\s*([^\n]+)',
                r'[\*\-]\s*Gaya\s*Visual\s*:\s*([^\n]+)',
                r'Tipe\s*Visual\s*:\s*([^\n]+)'
            ])

            env_val = _extract_field([
                r'[\*\-]\s*(?:\🏞️\s*)?(?:Setting\s*)?(?:Lokasi|Environment)\s*:\s*([^\n]+)',
                r'[\*\-]\s*Environment\s*:\s*([^\n]+)',
                r'Setting\s*Lokasi\s*:\s*([^\n]+)'
            ])

            color_val = _extract_field([
                r'[\*\-]\s*(?:\🎨\s*)?Color\s*Grading\s*:\s*([^\n]+)',
                r'[\*\-]\s*Palet\s*Warna\s*:\s*([^\n]+)',
                r'Color\s*Grading\s*:\s*([^\n]+)'
            ])

            voice_val = _extract_field([
                r'[\*\-]\s*(?:\🗣️\s*)?Voice\s*Style[^\:]*:\s*([^\n]+)',
                r'[\*\-]\s*Gaya\s*Vokal\s*:\s*([^\n]+)',
                r'Voice\s*Style\s*:\s*([^\n]+)'
            ])

            vis_val = _extract_field([
                r'[\*\-]\s*(?:\🎥\s*)?Visual\s*(?:&|dan)?\s*Kamera\s*:\s*([^\n]+)',
                r'[\*\-]\s*Visual\s*:\s*([^\n]+)',
                r'Visual\s*Camera\s*Direction\s*:\s*([^\n]+)'
            ])

            audio_raw = _extract_field([
                r'[\*\-]\s*(?:\🎙️\s*)?(?:Dialog|Skrip)\s*Audio[^\:]*:\s*([^\n]+)',
                r'Dialog\s*Audio[^\:]*:\s*([^\n]+)',
                r'Skrip\s*Audio[^\:]*:\s*([^\n]+)'
            ])
            # Bersihkan kutipan luar saja secara bersih tanpa memotong tanda kutip/tanda baca di dalam kalimat
            audio_val = audio_raw.strip().strip('*').strip('_').strip()
            if (audio_val.startswith('"') and audio_val.endswith('"')) or (audio_val.startswith("'") and audio_val.endswith("'")):
                audio_val = audio_val[1:-1].strip()

            broll_val = _extract_field([
                r'[\*\-]\s*(?:\🎞️\s*)?B-Roll[^\:]*:\s*([^\n]+)',
                r'[\*\-]\s*Aset\s*Visual[^\:]*:\s*([^\n]+)',
                r'B-Roll\s*&\s*Aset\s*Visual\s*:\s*([^\n]+)'
            ])

            sfx_val = _extract_field([
                r'[\*\-]\s*(?:\🔊\s*)?SFX\s*(?:&|dan)?\s*Transisi\s*:\s*([^\n]+)',
                r'[\*\-]\s*SFX[^\:]*:\s*([^\n]+)',
                r'Transisi\s*:\s*([^\n]+)'
            ])

            note_val = _extract_field([
                r'[\*\-]\s*(?:\🎯\s*)?Catatan\s*Editor[^\:]*:\s*([^\n]+)',
                r'[\*\-]\s*Pemicu\s*Psikologis\s*:\s*([^\n]+)',
                r'Catatan\s*:\s*([^\n]+)'
            ])

            ai_prompt_val = _extract_field([
                r'[\*\-]\s*(?:\🔑\s*)?Prompt\s*AI\s*(?:Video|Image)[^\:]*:\s*([^\n]+)',
                r'[\*\-]\s*AI\s*Video\s*Prompt[^\:]*:\s*([^\n]+)',
                r'AI\s*Prompt[^\:]*:\s*([^\n]+)'
            ])

            acting_val = _extract_field([
                r'[\*\-]\s*(?:\🎭\s*)?(?:Delivery|Panduan\s*Akting)[^\:]*:\s*([^\n]+)',
                r'[\*\-]\s*Level\s*Energi[^\:]*:\s*([^\n]+)',
                r'Delivery\s*(?:&|dan)?\s*Level\s*Energi[^\:]*:\s*([^\n]+)'
            ])

            relevance_val = _extract_field([
                r'[\*\-]\s*(?:\🎯\s*)?Relevansi\s*Audiens[^\:]*:\s*([^\n]+)',
                r'[\*\-]\s*Diksi\s*Audiens[^\:]*:\s*([^\n]+)',
                r'Relevansi\s*:\s*([^\n]+)'
            ])

            clean_audio_txt = audio_val or "(Baca naskah dialog)"
            words_in_scene = len(clean_audio_txt.split())
            est_audio_dur = max(2, round(words_in_scene / 1.9))
            ideal_scene_dur = max(3, min(15, round(words_in_scene / 1.85) + (1 if words_in_scene > 5 else 0)))
            diff = est_audio_dur - duration_sec

            # Evaluasi Presisi Sinkronisasi Audio vs Visual untuk Generator AI (Kling, Runway, Luma)
            # Batas aman per klip AI video 5-10 detik: dialog ideal 10 - 15 kata (maks 16 kata)
            if words_in_scene > 16:
                sync_status = "overflow"
                sync_badge = f"🚨 Rawan Terpotong AI ({words_in_scene} kata > 16)"
                sync_badge_color = "#dc2626"
                sync_badge_bg = "#fef2f2"
                sync_badge_border = "#fecaca"
                sync_note = f"Dialog ini memiliki {words_in_scene} kata (~{est_audio_dur}s). Di generator AI video (Kling/Runway klip 5-10s), dialog di atas 16 kata rawan terpotong di akhir. Disarankan kompres ke <= 15 kata!"
                is_synced = False
            elif diff >= 2:
                sync_status = "overflow"
                sync_badge = f"🚨 Dialog Kepanjangan (+{diff}s)"
                sync_badge_color = "#dc2626"
                sync_badge_bg = "#fef2f2"
                sync_badge_border = "#fecaca"
                sync_note = f"Dialog butuh ~{est_audio_dur}s ({words_in_scene} kata), sedangkan durasi klip visual tertulis {duration_sec}s. Vokal berisiko terpotong {diff} detik di generator AI video!"
                is_synced = False
            elif diff <= -4 and duration_sec >= 8:
                sync_status = "underflow"
                sync_badge = f"⚠️ Hening Visual (+{abs(diff)}s)"
                sync_badge_color = "#d97706"
                sync_badge_bg = "#fffbeb"
                sync_badge_border = "#fde68a"
                sync_note = f"Dialog selesai di detik ke-{est_audio_dur} ({words_in_scene} kata), menyisakan jeda hening {abs(diff)}s pada klip {duration_sec}s."
                is_synced = False
            else:
                sync_status = "synced"
                sync_badge = f"✅ Pas di AI Video ({words_in_scene} kata ~{est_audio_dur}s)"
                sync_badge_color = "#10b981"
                sync_badge_bg = "#ecfdf5"
                sync_badge_border = "#a7f3d0"
                sync_note = f"Panjang dialog ({words_in_scene} kata) sangat ideal dan aman untuk klip video AI 5-10 detik."
                is_synced = True

            # Keamanan klip: Durasi <= 12s, dialog <= 16 kata, dan audio tidak overflow klip
            is_clip_safe = (duration_sec <= 12) and (words_in_scene <= 16) and (diff < 2)
            if is_clip_safe:
                clip_status = "safe"
                clip_status_text = "✅ Aman AI Video (<= 16 kata)"
            elif words_in_scene > 20 or duration_sec > 15:
                clip_status = "danger"
                clip_status_text = "🚨 Rawan Terpotong (> 20 kata / > 15s)"
            else:
                clip_status = "warning"
                clip_status_text = "⚠️ Perhatian Durasi (> 16 kata)"

            # Resolusi Cerdas Setting Lokasi (Anti-Monoton & Anti-Studio Generik)
            # Jika scene bertuliskan "(Sesuai Master Anchor)" atau kosong, gunakan master_env
            clean_env = env_val.strip().strip('()').strip() if env_val else ""
            if not clean_env or any(ph in clean_env.lower() for ph in ["sesuai", "konsisten", "master", "anchor", "environment anchor"]):
                clean_env = master_env or clean_env

            # Jika masih kosong atau terjebak generic studio, lakukan inferensi kontekstual dari naskah
            if not clean_env or clean_env.lower() in ["studio minimalis", "studio minimalis modern", "studio kerja minimalis", "studio"]:
                if master_env and master_env.lower() not in ["studio minimalis", "studio minimalis modern", "studio kerja minimalis", "studio"]:
                    clean_env = master_env
                else:
                    text_for_env = f"{title_clean} {vis_val} {clean_audio_txt} {storyboard_text[:400]}".lower()
                    if any(k in text_for_env for k in ["masak", "resep", "kuliner", "makanan", "panci", "bumbu", "dapur", "kuah", "bawang", "kompor"]):
                        clean_env = "Dapur Rumah Minimalis Bersih & Estetik (Natural Morning Light & Marmer Putih)"
                    elif any(k in text_for_env for k in ["skincare", "serum", "kulit", "jerawat", "glowing", "toner", "wajah", "niacinamide", "pelembab"]):
                        clean_env = "Vanity Mirror Kamar Mandi Marmer Putih Bersih (Clean Bright Ring Light)"
                    elif any(k in text_for_env for k in ["makeup", "lipstik", "cushion", "bedak", "riasan", "kosmetik"]):
                        clean_env = "Meja Rias Vanity Estetik dengan Cermin LED & Rak Kosmetik Rapi"
                    elif any(k in text_for_env for k in ["outfit", "baju", "celana", "gamis", "fashion", "hijab", "sepatu", "sneaker"]):
                        clean_env = "Walk-in Closet Estetik / Kamar Tidur Modern dengan Full-Length Mirror"
                    elif any(k in text_for_env for k in ["motor", "mobil", "bengkel", "mesin", "oli", "ban", "belt", "pulley"]):
                        clean_env = "Garasi Modern Bersih dengan Tool Rack Rapi & Pencahayaan Neon Cool White"
                    elif any(k in text_for_env for k in ["gym", "fitness", "otot", "kalori", "diet", "workout", "dumbel", "latihan"]):
                        clean_env = "Gym Modern / Ruang Latihan Fitness dengan Mirror Wall & Dumbbell Rack"
                    elif any(k in text_for_env for k in ["kopi", "cafe", "kafe", "barista", "espresso"]):
                        clean_env = "Coffee Shop Estetik / Espresso Bar Modern (Warm Bokeh Background)"
                    elif any(k in text_for_env for k in ["ai", "tech", "coding", "software", "prompt", "laptop", "komputer", "chatgpt"]):
                        clean_env = "Desk Setup Gadget & Ambient Neon Light (Tech Minimalist Dark)"
                    elif any(k in text_for_env for k in ["anak", "bayi", "parenting", "ibu", "mainan"]):
                        clean_env = "Ruang Bermain Anak Ceria & Ruang Keluarga Hangat Bersih (Natural Daylight)"
                    elif any(k in text_for_env for k in ["tanaman", "kebun", "taman", "bunga", "farming"]):
                        clean_env = "Taman Rumah Minimalis / Balkon Urban Farming Hijau (Natural Daylight)"
                    else:
                        clean_env = "Smart Workspace Modern dengan Meja Kayu & Tanaman Indoor (Warm Daylight)"

            clean_vis_style = vis_style_val or (master_vis if master_vis and "live action" in master_vis.lower() else "Realistis Sinematik / Live Action")
            clean_color = color_val or (master_color or "Moody Warm Cinematic")
            clean_voice = voice_val or (master_voice or "Santai & Empatik")

            # Resolusi Sinematografi & Prompt AI Video Kelas Sutradara Pro (Hollywood/Commercial-Grade)
            scene_num_int = int(s_num) if s_num.isdigit() else len(scenes) + 1
            cine_context = f"{title_clean} {vis_val} {clean_audio_txt} {clean_env} {storyboard_text[:350]}"
            pro_cine = get_contextual_pro_cinematography(cine_context, scene_num=scene_num_int, scene_type=title_clean)
            final_ai_prompt = build_pro_ai_video_prompt(
                base_prompt=ai_prompt_val,
                niche_or_topic=cine_context,
                scene_num=scene_num_int,
                visual_dir=vis_val,
                env=clean_env,
                color=clean_color
            )

            scene_entry = {
                "scene_num": scene_num_int,
                "title": title_clean or f"Scene {s_num}",
                "timing": timing_val or f"Detik {s_num}",
                "duration_sec": duration_sec,
                "ideal_duration_sec": ideal_scene_dur,
                "word_count": words_in_scene,
                "est_audio_dur": est_audio_dur,
                "duration_diff": diff,
                "duration_compliant": duration_sec <= 15,
                "is_clip_safe": is_clip_safe,
                "clip_status": clip_status,
                "clip_status_text": clip_status_text,
                "sync_status": sync_status,
                "sync_badge": sync_badge,
                "sync_badge_color": sync_badge_color,
                "sync_badge_bg": sync_badge_bg,
                "sync_badge_border": sync_badge_border,
                "sync_note": sync_note,
                "is_synced": is_synced,
                "visual_style": clean_vis_style,
                "environment": clean_env,
                "color_grading": clean_color,
                "voice_style": clean_voice,
                "acting_delivery": acting_val or "Energi 7/10, ekspresi antusias, tatapan fokus ke lensa",
                "audience_relevance": relevance_val or "Relatable dengan masalah sehari-hari audiens",
                "visual": vis_val or "Kreator di depan kamera, tatapan fokus ke lensa",
                "audio": clean_audio_txt,
                "b_roll": broll_val or "Footage pendukung / B-Roll kontekstual",
                "sfx_transition": sfx_val or "SFX: Whoosh / Glitch | Transisi: Jump Cut",
                "notes": note_val or "Pertahankan pacing cepat dan retensi tinggi",
                "ai_prompt": final_ai_prompt,
                "camera_motion": pro_cine["camera_motion"],
                "lens_optics": pro_cine["lens_optics"],
                "lighting_setup": pro_cine["lighting_setup"],
                "editing_style": pro_cine["editing_style"],
                "cine_badge": pro_cine["display_badge"]
            }
            scenes.append(scene_entry)

    # Metode 2: Jika belum ada format SCENE eksplisit, ekstrak dari tabel markdown pipa
    if not scenes:
        df = markdown_table_to_dataframe(storyboard_text)
        if df is not None and not df.empty:
            col_sec = df.columns[0]
            col_vis = df.columns[1] if len(df.columns) > 1 else ""
            col_aud = df.columns[2] if len(df.columns) > 2 else ""
            col_ost = df.columns[3] if len(df.columns) > 3 else ""
            col_note = df.columns[4] if len(df.columns) > 4 else ""

            default_titles = [
                "The Hook (Penahan Scroll 3 Detik)",
                "The Agitation (Memperdalam Masalah)",
                "The Solution & Pattern Interrupt (Solusi Unik)",
                "Proof & Demonstration (Aplikasi Nyata)",
                "Value Escalation (Poin Kunci)",
                "The Call to Action (Jembatan Konversi)"
            ]
            default_sfx = [
                "SFX: Glitch / Bass Drop | Transisi: Hard Cut Zoom-In",
                "SFX: Vinyl Scratch / Whoosh | Transisi: Jump Cut",
                "SFX: Ding / Chime | Transisi: Whip Pan",
                "SFX: Pop Sound | Transisi: Zoom Out",
                "SFX: Rising Whoosh | Transisi: Fast Pan",
                "SFX: Click / Riser | Transisi: Smooth Fade"
            ]

            for idx, row in df.iterrows():
                sec_val = str(row[col_sec]).strip()
                vis_val = str(row[col_vis]).strip() if col_vis else "Kamera fokus ke subjek"
                aud_val = str(row[col_aud]).strip().strip('"').strip('*') if col_aud else ""
                note_val = str(row[col_note]).strip().strip('"').strip('*') if col_note else "Retensi tinggi"

                t_idx = min(idx, len(default_titles) - 1)
                
                # Hitung durasi detik visual klip secara presisi
                dur_sec = extract_duration_seconds(sec_val, "")

                clean_audio_txt = aud_val or ""
                words_in_scene = len(clean_audio_txt.split())
                est_audio_dur = max(2, round(words_in_scene / 1.9))
                ideal_scene_dur = max(3, min(15, round(words_in_scene / 1.85) + (1 if words_in_scene > 5 else 0)))
                diff = est_audio_dur - dur_sec

                if words_in_scene > 16:
                    sync_status = "overflow"
                    sync_badge = f"🚨 Rawan Terpotong AI ({words_in_scene} kata > 16)"
                    sync_badge_color = "#dc2626"
                    sync_badge_bg = "#fef2f2"
                    sync_badge_border = "#fecaca"
                    sync_note = f"Dialog ini memiliki {words_in_scene} kata (~{est_audio_dur}s). Di generator AI video klip 5-10s, dialog di atas 16 kata rawan terpotong di akhir. Disarankan kompres ke <= 15 kata!"
                    is_synced = False
                elif diff >= 2:
                    sync_status = "overflow"
                    sync_badge = f"🚨 Dialog Kepanjangan (+{diff}s)"
                    sync_badge_color = "#dc2626"
                    sync_badge_bg = "#fef2f2"
                    sync_badge_border = "#fecaca"
                    sync_note = f"Dialog butuh ~{est_audio_dur}s ({words_in_scene} kata), sedangkan klip hanya {dur_sec}s. Audio berisiko terpotong {diff} detik di generator video AI!"
                    is_synced = False
                elif diff <= -4 and dur_sec >= 8:
                    sync_status = "underflow"
                    sync_badge = f"⚠️ Hening Visual (+{abs(diff)}s)"
                    sync_badge_color = "#d97706"
                    sync_badge_bg = "#fffbeb"
                    sync_badge_border = "#fde68a"
                    sync_note = f"Dialog selesai di detik ke-{est_audio_dur} ({words_in_scene} kata), klip {dur_sec}s memiliki {abs(diff)}s jeda hening tanpa suara."
                    is_synced = False
                else:
                    sync_status = "synced"
                    sync_badge = f"✅ Pas di AI Video ({words_in_scene} kata ~{est_audio_dur}s)"
                    sync_badge_color = "#10b981"
                    sync_badge_bg = "#ecfdf5"
                    sync_badge_border = "#a7f3d0"
                    sync_note = f"Panjang dialog ({words_in_scene} kata) sangat ideal dan aman untuk klip video AI 5-10 detik."
                    is_synced = True

                is_clip_safe = (dur_sec <= 12) and (words_in_scene <= 16) and (diff < 2)
                if is_clip_safe:
                    clip_status = "safe"
                    clip_status_text = "✅ Aman AI Video (<= 16 kata)"
                elif words_in_scene > 20 or dur_sec > 15:
                    clip_status = "danger"
                    clip_status_text = "🚨 Rawan Terpotong (> 20 kata / > 15s)"
                else:
                    clip_status = "warning"
                    clip_status_text = "⚠️ Perhatian Durasi (> 16 kata)"

                clean_env_tbl = master_env or "Smart Workspace Modern dengan Tanaman Indoor (Warm Daylight)"
                cine_context_tbl = f"{default_titles[t_idx]} {vis_val} {aud_val} {clean_env_tbl} {storyboard_text[:350]}"
                pro_cine_tbl = get_contextual_pro_cinematography(cine_context_tbl, scene_num=idx + 1, scene_type=default_titles[t_idx])
                final_ai_prompt_tbl = build_pro_ai_video_prompt(
                    base_prompt="",
                    niche_or_topic=cine_context_tbl,
                    scene_num=idx + 1,
                    visual_dir=vis_val,
                    env=clean_env_tbl,
                    color=master_color or "Moody Warm Cinematic"
                )

                scenes.append({
                    "scene_num": idx + 1,
                    "title": default_titles[t_idx],
                    "timing": f"Detik {sec_val}",
                    "duration_sec": dur_sec,
                    "ideal_duration_sec": ideal_scene_dur,
                    "word_count": words_in_scene,
                    "est_audio_dur": est_audio_dur,
                    "duration_diff": diff,
                    "duration_compliant": dur_sec <= 15,
                    "is_clip_safe": is_clip_safe,
                    "clip_status": clip_status,
                    "clip_status_text": clip_status_text,
                    "sync_status": sync_status,
                    "sync_badge": sync_badge,
                    "sync_badge_color": sync_badge_color,
                    "sync_badge_bg": sync_badge_bg,
                    "sync_badge_border": sync_badge_border,
                    "sync_note": sync_note,
                    "is_synced": is_synced,
                    "visual_style": master_vis or "Live Action Sinematik",
                    "environment": clean_env_tbl,
                    "color_grading": master_color or "Moody Warm Cinematic",
                    "voice_style": master_voice or "Santai & Percaya Diri",
                    "visual": vis_val,
                    "audio": aud_val,
                    "b_roll": "B-Roll kontekstual / Footage pendukung",
                    "sfx_transition": default_sfx[t_idx],
                    "notes": note_val,
                    "ai_prompt": final_ai_prompt_tbl,
                    "camera_motion": pro_cine_tbl["camera_motion"],
                    "lens_optics": pro_cine_tbl["lens_optics"],
                    "lighting_setup": pro_cine_tbl["lighting_setup"],
                    "editing_style": pro_cine_tbl["editing_style"],
                    "cine_badge": pro_cine_tbl["display_badge"]
                })

    # Format text siap copas per scene
    for s in scenes:
        act_line = f"• 🎭 Delivery Talent: {s['acting_delivery']}\n" if s.get('acting_delivery') else ""
        rel_line = f"• 🎯 Relevansi Audiens: {s['audience_relevance']}\n" if s.get('audience_relevance') else ""
        cine_line = f"• 🎬 Arahan Kamera & Optik: {s['cine_badge']}\n" if s.get('cine_badge') else ""
        w_cnt = s.get('word_count', len(s.get('audio', '').split()))
        est_d = s.get('est_audio_dur', round(w_cnt / 1.9))
        safe_str = s.get('clip_status_text', '✅ Aman AI Video <= 15s')
        sync_str = s.get('sync_badge', safe_str)
        s["copy_text"] = (
            f"🎬 SCENE {s['scene_num']}: {s['title']} [{s['timing']}]\n"
            f"• ⏱️ Durasi Klip: {s['timing']} ({w_cnt} kata | vokal ~{est_d}s)\n"
            f"• 🎨 Tipe Visual: {s['visual_style']}\n"
            f"• 🏞️ Setting Lokasi: {s['environment']}\n"
            f"• 🎨 Color Grading: {s['color_grading']}\n"
            f"• 🗣️ Voice Style: {s['voice_style']}\n"
            f"{act_line}"
            f"{rel_line}"
            f"{cine_line}"
            f"• 🎥 Visual & Kamera: {s['visual']}\n"
            f"• 🎙️ Dialog Audio (Word for Word): \"{s['audio']}\"\n"
            f"• 🎞️ B-Roll / Aset: {s['b_roll']}\n"
            f"• 🔊 SFX & Transisi: {s['sfx_transition']}\n"
            f"• 🎯 Catatan Editor: {s['notes']}\n"
            f"• 🔑 Prompt AI Video/Image: {s['ai_prompt']}"
        )

    return scenes


def sync_storyboard_scenes_timeline(scenes: list) -> list:
    """
    Menghitung ulang timeline detik kumulatif dan durasi tiap scene secara presisi
    berdasarkan jumlah kata dialog aktual (1.85 kata/detik + 1 detik buffer visual/SFX)
    sehingga durasi klip visual dan audio terjamin 100% sinkron (anti-terpotong & anti-dead air).
    """
    if not scenes:
        return []

    synced_scenes = []
    current_sec = 0
    for idx, sc in enumerate(scenes):
        sc_copy = dict(sc)
        w_cnt = sc_copy.get("word_count", len(sc_copy.get("audio", "").split()))
        
        # Hitung durasi ideal: waktu bicara (~1.85 kata/detik) + 1 detik buffer visual/editing
        ideal_dur = max(3, min(15, round(w_cnt / 1.85) + (1 if w_cnt > 4 else 0)))
        start_sec = current_sec
        end_sec = current_sec + ideal_dur
        current_sec = end_sec

        sc_copy["duration_sec"] = ideal_dur
        sc_copy["timing"] = f"Detik {start_sec:02d} - {end_sec:02d} ({ideal_dur} Detik)"
        sc_copy["duration_diff"] = 0
        sc_copy["is_synced"] = True
        sc_copy["is_clip_safe"] = (ideal_dur <= 15) and (w_cnt <= 25)
        sc_copy["clip_status"] = "safe" if sc_copy["is_clip_safe"] else "warning"
        sc_copy["clip_status_text"] = "✅ Aman AI Video (<= 15s)" if sc_copy["is_clip_safe"] else "⚠️ Perhatian Durasi"
        sc_copy["sync_status"] = "synced"
        sc_copy["sync_badge"] = f"✅ Sinkron Sempurna ({w_cnt} kata ~{sc_copy.get('est_audio_dur', round(w_cnt/1.9))}s / klip {ideal_dur}s)"
        sc_copy["sync_badge_color"] = "#10b981"
        sc_copy["sync_badge_bg"] = "#ecfdf5"
        sc_copy["sync_badge_border"] = "#a7f3d0"
        sc_copy["sync_note"] = f"Durasi visual telah diselaraskan persis dengan tempo bicara dialog ({ideal_dur} detik)."

        # Perbarui copy_text
        act_line = f"• 🎭 Delivery Talent: {sc_copy['acting_delivery']}\n" if sc_copy.get('acting_delivery') else ""
        rel_line = f"• 🎯 Relevansi Audiens: {sc_copy['audience_relevance']}\n" if sc_copy.get('audience_relevance') else ""
        cine_line = f"• 🎬 Arahan Kamera & Optik: {sc_copy['cine_badge']}\n" if sc_copy.get('cine_badge') else ""
        sc_copy["copy_text"] = (
            f"🎬 SCENE {sc_copy['scene_num']}: {sc_copy['title']} [{sc_copy['timing']}]\n"
            f"• ⏱️ Durasi Klip: {sc_copy['timing']} ({w_cnt} kata | vokal ~{sc_copy.get('est_audio_dur', round(w_cnt/1.9))}s)\n"
            f"• 🎨 Tipe Visual: {sc_copy['visual_style']}\n"
            f"• 🏞️ Setting Lokasi: {sc_copy['environment']}\n"
            f"• 🎨 Color Grading: {sc_copy['color_grading']}\n"
            f"• 🗣️ Voice Style: {sc_copy['voice_style']}\n"
            f"{act_line}"
            f"{rel_line}"
            f"{cine_line}"
            f"• 🎥 Visual & Kamera: {sc_copy['visual']}\n"
            f"• 🎙️ Dialog Audio (Word for Word): \"{sc_copy['audio']}\"\n"
            f"• 🎞️ B-Roll / Aset: {sc_copy['b_roll']}\n"
            f"• 🔊 SFX & Transisi: {sc_copy['sfx_transition']}\n"
            f"• 🎯 Catatan Editor: {sc_copy['notes']}\n"
            f"• 🔑 Prompt AI Video/Image: {sc_copy['ai_prompt']}"
        )
        synced_scenes.append(sc_copy)

    return synced_scenes


def apply_synced_timeline_to_markdown(storyboard_text: str, synced_scenes: list) -> str:
    """
    Memperbarui timestamp durasi pada naskah Markdown storyboard asli (Bagian 1 & Bagian 2)
    agar sinkron dengan timeline yang baru dihitung.
    """
    if not storyboard_text or not synced_scenes:
        return storyboard_text

    updated_text = storyboard_text

    for sc in synced_scenes:
        s_num = sc["scene_num"]
        timing = sc["timing"]
        dur_sec = sc["duration_sec"]
        
        # Ekstrak rentang detik misal "00:00 - 00:07"
        dur_range_m = re.search(r'Detik\s*(\d+)\s*[-–—]\s*(\d+)', timing)
        if dur_range_m:
            p1, p2 = int(dur_range_m.group(1)), int(dur_range_m.group(2))
            formatted_range = f"00:{p1:02d} - 00:{p2:02d}"
            
            # Ganti di header scene: ### 🎬 SCENE X [...]
            pat_header = re.compile(
                rf'(###\s*(?:🎬\s*)?SCENE\s*{s_num}\s*\[)([^\]]+)(\])',
                re.IGNORECASE
            )
            updated_text = pat_header.sub(rf'\g<1>{formatted_range}\g<3>', updated_text)

        # Ganti di baris durasi: - **⏱️ Durasi**: ...
        # Cari blok scene spesifik
        sec_block_pat = re.compile(
            rf'(###\s*(?:🎬\s*)?SCENE\s*{s_num}\b.*?(?=(?:###\s*(?:🎬\s*)?SCENE\b|###\s*BAGIAN|\Z)))',
            re.DOTALL | re.IGNORECASE
        )
        sec_m = sec_block_pat.search(updated_text)
        if sec_m:
            sec_body = sec_m.group(1)
            new_sec_body = re.sub(
                r'([\*\-]\s*(?:⏱️\s*)?Durasi\s*:\s*)([^\n]+)',
                rf'\g<1>{dur_sec} Detik ({timing})',
                sec_body,
                count=1,
                flags=re.IGNORECASE
            )
            updated_text = updated_text[:sec_m.start()] + new_sec_body + updated_text[sec_m.end():]

    # Perbarui baris tabel di Bagian 1 jika ada
    b1_idx = updated_text.find("### BAGIAN 1")
    b2_idx = updated_text.find("### BAGIAN 2")
    if b1_idx != -1 and b2_idx != -1 and b2_idx > b1_idx:
        table_part = updated_text[b1_idx:b2_idx]
        table_lines = table_part.split("\n")
        data_row_count = 0
        new_table_lines = []
        for line in table_lines:
            stripped = line.strip()
            if stripped.startswith("|") and not stripped.startswith("|---") and not "Detik" in stripped:
                if data_row_count < len(synced_scenes):
                    sc = synced_scenes[data_row_count]
                    dur_range_m = re.search(r'Detik\s*(\d+)\s*[-–—]\s*(\d+)', sc["timing"])
                    if dur_range_m:
                        p1, p2 = int(dur_range_m.group(1)), int(dur_range_m.group(2))
                        new_col0 = f"**{p1:02d} - {p2:02d}**"
                        cells = line.split("|")
                        if len(cells) >= 3:
                            cells[1] = f" {new_col0} "
                            line = "|".join(cells)
                    data_row_count += 1
            new_table_lines.append(line)
        updated_text = updated_text[:b1_idx] + "\n".join(new_table_lines) + updated_text[b2_idx:]

    return updated_text


def compress_storyboard_dialogues_to_safe_words(storyboard_text: str, max_words: int = 15) -> str:
    """
    Mengompresi seluruh kalimat dialog per scene pada storyboard agar memiliki maksimal 12-15 kata,
    sehingga pas dengan durasi render AI video (5-10 detik) dan 100% bebas dari risiko terpotong di akhir.
    Tetap mempertahankan angka metrik (%, °C, dll) dan esensi kausalitas pesan.
    """
    if not storyboard_text:
        return storyboard_text

    def _trim_sentence(txt: str, limit: int = 15) -> str:
        clean_in = txt.strip().strip('"').strip()
        words = clean_in.split()
        if len(words) <= limit:
            return clean_in

        # 1. Hilangkan basa-basi / filler phrases umum yang memboroskan kata
        cleaned = clean_in
        substitutions = [
            (r'\bSebagian besar orang langsung buang\b', 'Banyak orang buang'),
            (r'\bSebagian besar orang langsung\b', 'Banyak orang'),
            (r'\bBanyak orang kemakan tren mikir bahwa\b', 'Mitos umum:'),
            (r'\bBanyak orang kemakan tren mikir\b', 'Mitos umum:'),
            (r'\bBanyak pemilik mobil nekat semprot\b', 'Jangan nekat semprot'),
            (r'\bBanyak pemilik mobil nekat\b', 'Jangan nekat'),
            (r'\bLu pasti sering ngetik prompt tiga paragraf panjang, tapi responnya tetep ngaco\b', 'Sering ngetik prompt panjang tapi AI tetep ngaco'),
            (r'\bLu pasti sering ngetik\b', 'Sering ngetik'),
            (r'\bPada kenyataannya hal ini\b', 'Faktanya,'),
            (r'\bPadahal sebenarnya\b', 'Padahal'),
            (r'\bJurnal dermatologi membuktikan bahwa\b', 'Riset lab membuktikan'),
            (r'\bJurnal dermatologi membuktikan\b', 'Riset membuktikan'),
            (r'\bUntuk memastikan bahwa\b', 'Agar'),
            (r'\bCukup tambahkan kalimat ini di baris pertama:\s*', 'Tambahkan kalimat: '),
            (r'\bSplit-test membuktikan bahwa\b', 'Split-test membuktikan'),
            (r'\bdi tong sampah karena dikira keras,\s*', ''),
            (r'\bsehingga putaran alternator dan pompa radiator drop drastis\b', 'bikin putaran alternator drop'),
            (r'\bsecara presisi\b', ''),
            (r'\bdengan sangat cepat\b', 'cepat'),
            (r'\bhanya dalam waktu\b', 'dalam'),
            (r'\byang ada di dalam\b', 'di')
        ]
        for pat, repl in substitutions:
            cleaned = re.sub(pat, repl, cleaned, flags=re.IGNORECASE).strip()

        words_after = cleaned.split()
        if len(words_after) <= limit:
            return cleaned

        # 2. Jika masih > limit, potong kalimat majemuk sekunder sambil menjaga angka/metrik
        clauses = re.split(r'[,;—]\s*', cleaned)
        if len(clauses) >= 2:
            candidate = clauses[0].strip()
            for cl in clauses[1:]:
                test_str = f"{candidate}, {cl.strip()}"
                if len(test_str.split()) <= limit:
                    candidate = test_str
                else:
                    break
            if len(candidate.split()) >= 7 and len(candidate.split()) <= limit:
                if not candidate.endswith(('.', '!', '?')):
                    candidate += "!"
                return candidate

        # 3. Fallback: potong kata ke limit dan jaga tanda baca akhir
        trimmed = " ".join(words_after[:limit])
        if not trimmed.endswith(('.', '!', '?')):
            trimmed += "!"
        return trimmed

    # Terapkan kompresi pada baris dialog: - **🎙️ Dialog Audio (Word for Word)**: "..."
    def _replace_dialogue(match):
        prefix = match.group(1)
        raw_dlg = match.group(2).strip().strip('"')
        new_dlg = _trim_sentence(raw_dlg, limit=max_words)
        return f'{prefix}"{new_dlg}"'

    pat_dlg = re.compile(
        r'([\*\-]\s*(?:🎙️\s*)?Dialog\s*Audio[^\:]*:\s*)([^\n]+)',
        re.IGNORECASE
    )
    res_text = pat_dlg.sub(_replace_dialogue, storyboard_text)

    # Sinkronkan juga pada tabel Markdown di Bagian 1 jika ada
    lines = res_text.split("\n")
    new_lines = []
    for line in lines:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = line.split("|")
            if len(cells) >= 4 and not "---" in line and not "Skrip Audio" in line and not "Detik" in line:
                raw_aud = cells[2].strip().strip('"')
                if len(raw_aud.split()) > max_words:
                    new_aud = _trim_sentence(raw_aud, limit=max_words)
                    cells[2] = f' "{new_aud}" '
                    line = "|".join(cells)
            new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def shard_storyboard_scenes_by_clauses(storyboard_text: str, max_words_per_shot: int = 15) -> str:
    """
    Memecah (sharding) scene yang memiliki dialog panjang menjadi 2 klip/scene terpisah berkesinambungan
    TANPA memotong atau mengurangi satu kata pun dari dialog dramatisnya!
    Setiap potongan klausa mendapatkan angle kamera, B-Roll, SFX, dan durasi klip mandiri (4-7 detik),
    sehingga 100% aman anti-terpotong di generator video AI (Kling, Runway, Luma) sekaligus membuat
    pergantian shot visual lebih sinematik dan dinamis.
    """
    import re

    scenes = parse_storyboard_scenes(storyboard_text)
    if not scenes:
        return storyboard_text

    master_anchor = parse_master_consistency_anchor(storyboard_text)

    sharded_scenes = []
    for sc in scenes:
        dlg = sc.get("audio", "").strip().strip('"').strip()
        words = dlg.split()

        if len(words) <= max_words_per_shot:
            sharded_scenes.append(sc)
            continue

        # Pecah dialog panjang menjadi 2 bagian secara alami (berdasarkan tanda baca atau kata hubung)
        mid_idx = len(words) // 2
        split_point = -1

        # Cek tanda baca dalam kalimat: '.', '!', '?', ';', ':', '—', '-'
        best_punc_dist = 999
        for i, w in enumerate(words):
            if any(w.endswith(p) for p in ['.', '!', '?', ';', ':', '—', '-']):
                dist = abs(i - mid_idx)
                if dist < best_punc_dist and i >= 3 and (len(words) - i - 1) >= 3:
                    best_punc_dist = dist
                    split_point = i + 1
            elif w.endswith(','):
                dist = abs(i - mid_idx)
                if dist < best_punc_dist and i >= 3 and (len(words) - i - 1) >= 3:
                    best_punc_dist = dist
                    split_point = i + 1

        # Jika tidak ada tanda baca yang pas, cari kata hubung alami
        if split_point == -1:
            conjunctions = ["padahal", "karena", "sehingga", "akhirnya", "tapi", "namun", "justru", "dan", "untuk", "biar", "agar", "yaitu", "cukup"]
            best_conj_dist = 999
            for i, w in enumerate(words):
                w_clean = w.lower().strip(',.!?')
                if w_clean in conjunctions:
                    dist = abs(i - mid_idx)
                    if dist < best_conj_dist and i >= 3 and (len(words) - i) >= 3:
                        best_conj_dist = dist
                        split_point = i

        # Fallback jika tidak ada titik temu: bagi dua tepat di tengah
        if split_point == -1:
            split_point = mid_idx

        part1_words = words[:split_point]
        part2_words = words[split_point:]

        part1_text = " ".join(part1_words).strip()
        part2_text = " ".join(part2_words).strip()

        # Format tanda baca penutup agar vokal mengalir mulus antar scene
        if not part1_text.endswith(('.', '!', '?', ',', '—', '...')):
            part1_text += "..."
        if not part2_text.endswith(('.', '!', '?')):
            part2_text += "!"

        # Shot A (Premis / Setup)
        shot_a = dict(sc)
        base_title = sc.get('title', 'Scene')
        shot_a["title"] = f"{base_title} (Shot A: Setup)"
        shot_a["audio"] = part1_text
        shot_a["word_count"] = len(part1_words)
        shot_a["duration_sec"] = max(4, round(len(part1_words) / 1.85) + 1)
        shot_a["visual"] = f"{sc.get('visual', 'Talent di depan kamera')} — Framing Medium Close-Up fokus ke ekspresi emosional"
        shot_a["b_roll"] = sc.get("b_roll", "Footage pembuka setup materi")
        shot_a["sfx_transition"] = "SFX: Subtle Whoosh | Transisi: Jump Cut Pacing Cepat"

        # Shot B (Punchline / Payoff / Konsekuensi)
        shot_b = dict(sc)
        shot_b["title"] = f"{base_title} (Shot B: Payoff)"
        shot_b["audio"] = part2_text
        shot_b["word_count"] = len(part2_words)
        shot_b["duration_sec"] = max(4, round(len(part2_words) / 1.85) + 1)
        shot_b["visual"] = f"Cut ke Macro Close-Up / B-Roll reaksi dinamis mempertegas poin materi"
        shot_b["b_roll"] = sc.get("b_roll", "B-Roll detail pendukung materi")
        shot_b["sfx_transition"] = "SFX: Accent Impact / Bass Drop | Transisi: Whip Pan"

        sharded_scenes.append(shot_a)
        sharded_scenes.append(shot_b)

    # Re-number and calculate cumulative timeline
    current_sec = 0
    table_rows = []
    scene_blocks = []

    for i, s in enumerate(sharded_scenes):
        s_num = i + 1
        w_cnt = len(s["audio"].split())
        dur = max(4, min(10, round(w_cnt / 1.85) + 1))
        start_s = current_sec
        end_s = current_sec + dur
        current_sec = end_s

        time_str = f"Detik {start_s:02d} - {end_s:02d} ({dur} Detik)"
        est_speech = round(w_cnt / 1.9, 1)

        # Build table row
        col_sec = f"**{start_s:02d} - {end_s:02d}**"
        col_vis = s.get("visual", "Visual dinamis")
        col_aud = s["audio"].strip('"')
        col_sfx = s.get("sfx_transition", "SFX: Whoosh")
        col_note = s.get("notes", "Pacing cepat & sinematik")
        table_rows.append(f"| {col_sec} | {col_vis} | \"{col_aud}\" | {col_sfx} | {col_note} |")

        # Re-build pro AI video prompt for this specific shot
        cine_ctx = f"{s.get('title', '')} {col_vis} {col_aud} {s.get('environment', '')}"
        ai_prompt = build_pro_ai_video_prompt(
            base_prompt="",
            niche_or_topic=cine_ctx,
            scene_num=s_num,
            visual_dir=col_vis,
            env=s.get("environment", ""),
            color=s.get("color_grading", "")
        )

        block = f"""### 🎬 SCENE {s_num} [{start_s // 60:02d}:{start_s % 60:02d} - {end_s // 60:02d}:{end_s % 60:02d}]: {s.get('title', f'Scene {s_num}')}
- **⏱️ Durasi**: {dur} Detik (Detik {start_s} s/d {end_s}, Sinkron Dialog ~{est_speech}s | 100% Aman AI Video)
- **🎨 Tipe Visual**: {s.get('visual_style', 'Live Action Sinematik')}
- **🏞️ Setting Lokasi**: {s.get('environment', '-')}
- **🎨 Color Grading**: {s.get('color_grading', '-')}
- **🗣️ Voice Style**: {s.get('voice_style', '-')}
- **🎭 Delivery & Level Energi Talent**: {s.get('acting_delivery', 'Energi 8.5/10, tatapan fokus ke kamera')}
- **🎯 Relevansi Audiens & Diksi**: {s.get('audience_relevance', 'Relatable dengan masalah audiens')}
- **🎥 Visual & Kamera**: {col_vis}
- **🎙️ Dialog Audio (Word for Word)**: "{col_aud}"
- **🎞️ B-Roll & Aset Visual**: {s.get('b_roll', '-')}
- **🔊 SFX & Transisi**: {s.get('sfx_transition', '-')}
- **🎯 Catatan Editor & Pacing**: {s.get('notes', 'Potong jeda hening')}
- **🔑 Prompt AI Video/Image (English)**: {ai_prompt}"""
        scene_blocks.append(block)

    table_md = "\n".join(table_rows)
    scenes_md = "\n\n".join(scene_blocks)
    total_words = sum(len(s["audio"].split()) for s in sharded_scenes)

    # Reconstruct whole markdown preserving Bagian 0
    b0_match = re.search(r'(###\s*BAGIAN\s*0:.*?(?=###\s*BAGIAN\s*1|\Z))', storyboard_text, re.DOTALL | re.IGNORECASE)
    b0_text = b0_match.group(1).strip() if b0_match else ""

    if not b0_text and master_anchor and any(master_anchor.values()):
        b0_text = f"""### BAGIAN 0: MASTER PRODUCTION & AUDIENCE CONSISTENCY ANCHOR (KUNCI KONSISTENSI UTUH)
- **🎯 Pilar Tema Konten**: {master_anchor.get('content_theme', '-')}
- **👥 Target Audiens Persona**: {master_anchor.get('target_audience', '-')}
- **🗣️ Gaya Sapaan & Diksi**: {master_anchor.get('audience_tone_slang', '-')}
- **⚡ Trigger Emosi Dominan**: {master_anchor.get('emotional_trigger', '-')}
- **🧬 Master Visual Style Lock (English Prompt Prefix)**: {master_anchor.get('visual_style_lock', '-')}
- **👤 Master Character / Subject Anchor**: {master_anchor.get('character_anchor', '-')}
- **🏞️ Master Environment Anchor**: {master_anchor.get('environment_anchor', '-')}
- **🎨 Master Color Grading & Lighting Anchor**: {master_anchor.get('color_grading_anchor', '-')}
- **🎙️ Master Voice Profile Anchor**: {master_anchor.get('voice_profile_anchor', '-')}"""

    full_sharded_md = f"""{b0_text}

### BAGIAN 1: TABEL STORYBOARD DETIK DEMI DETIK (MICRO-SCENE SHARDING)
| Detik | Visual / B-Roll Camera Direction | Skrip Audio (Word for Word - Sinkron Klip 4-7s) | Aset B-Roll & SFX | Pemicu Psikologis / Pacing |
|---|---|---|---|---|
{table_md}

### BAGIAN 2: LEMBAR KERJA PRODUKSI PER SCENE (MICRO-SHOTS 4-7 DETIK — 100% AMAN AI VIDEO)

{scenes_md}

### BAGIAN 3: REKOMENDASI TEKNIS & SOUND
- **Total Scene Pasca-Sharding**: {len(sharded_scenes)} Micro-Scenes (Total ~{current_sec} Detik, rata-rata {round(total_words/len(sharded_scenes), 1)} kata per klip)
- **Status Kompatibilitas AI Video**: 100% Aman untuk Kling AI, Runway Gen-3, Luma & HeyGen (Zero Word Clipping).
- **Rekomendasi Sound/Backsound**: Tempo 115-125 BPM, beat lo-fi modern atau ambient upbeat ritmis.
"""
    return full_sharded_md


def format_scenes_for_production_sheet(scenes: list, title: str = "Video Konten", platform: str = "TikTok / Reels", master_anchor: dict = None) -> str:
    """
    Menyusun lembar kerja naskah storyboard per scene lengkap dalam bentuk teks siap copas
    untuk dikirimkan langsung ke tim editor, videografer, generator AI, atau grup WhatsApp/Notion.
    """
    if not scenes:
        return ""

    out = [
        "==================================================",
        "🎬 LEMBAR KERJA PRODUKSI VIDEO (SCENE-BY-SCENE PRODUCTION SHEET)",
        f"Judul Konten   : {title}",
        f"Target Platform: {platform} | Format: 9:16 Vertical Video",
        "Disiplin Scene : Maksimal durasi per scene <= 15 detik (Anti-Drop Retensi)",
        "=================================================="
    ]

    if master_anchor and any(master_anchor.values()):
        if master_anchor.get("content_theme") or master_anchor.get("target_audience"):
            out.append("\n🎯 BAGIAN 0.1: DNA BRIEF & TARGET AUDIENCE PERSONA (LANDASAN KONTEN)")
            if master_anchor.get("content_theme"):
                out.append(f"• 💡 Pilar Tema    : {master_anchor['content_theme']}")
            if master_anchor.get("target_audience"):
                out.append(f"• 👥 Target Persona: {master_anchor['target_audience']}")
            if master_anchor.get("audience_tone_slang"):
                out.append(f"• 🗣️ Diksi & Sapaan: {master_anchor['audience_tone_slang']}")
            if master_anchor.get("emotional_trigger"):
                out.append(f"• ⚡ Trigger Emosi : {master_anchor['emotional_trigger']}")
            out.append("--------------------------------------------------")

        out.append("\n🛡️ BAGIAN 0.2: MASTER PRODUCTION CONSISTENCY ANCHOR (KUNCI KONSISTENSI UTUH)")
        out.append("Gunakan parameter ini pada seluruh prompt generator AI & arahan shooting agar video kohesif 100%:")
        if master_anchor.get("visual_style_lock"):
            out.append(f"• 🧬 Style Lock AI : {master_anchor['visual_style_lock']}")
        if master_anchor.get("character_anchor"):
            out.append(f"• 👤 Karakter Subjek: {master_anchor['character_anchor']}")
        if master_anchor.get("environment_anchor"):
            out.append(f"• 🏞️ Setting Lokasi: {master_anchor['environment_anchor']}")
        if master_anchor.get("color_grading_anchor"):
            out.append(f"• 🎨 Color Grading : {master_anchor['color_grading_anchor']}")
        if master_anchor.get("voice_profile_anchor"):
            out.append(f"• 🎙️ Voice Profile : {master_anchor['voice_profile_anchor']}")
        out.append("==================================================\n")
    else:
        out.append("")

    for s in scenes:
        out.append(f"🎬 SCENE {s['scene_num']} [{s['timing']}]: {s['title']}")
        out.append("--------------------------------------------------")
        w_cnt = s.get('word_count', len(s.get('audio', '').split()))
        safe_str = "Aman AI Video <= 15s" if s.get('is_clip_safe', True) else "Perhatian Durasi"
        sync_str = s.get('sync_badge', safe_str)
        out.append(f"⏱️ Durasi Klip   : {s['timing']} ({w_cnt} kata ~{s.get('est_audio_dur', round(w_cnt/1.9))}s vokal)")
        out.append(f"🎨 Tipe & Lokasi: {s.get('visual_style', '-')} | {s.get('environment', '-')}")
        out.append(f"🎨 Color Grading: {s.get('color_grading', '-')}")
        out.append(f"🗣️ Voice Style  : {s.get('voice_style', '-')}")
        if s.get("cine_badge"):
            out.append(f"🎬 Kamera/Optik : {s['cine_badge']}")
        if s.get("acting_delivery"):
            out.append(f"🎭 Delivery Vokal: {s['acting_delivery']}")
        if s.get("audience_relevance"):
            out.append(f"🎯 Target Audiens: {s['audience_relevance']}")
        out.append(f"🎥 Visual/Kamera: {s['visual']}")
        out.append(f"🎙️ Dialog Audio : \"{s['audio']}\"")
        out.append(f"🎞️ Aset B-Roll  : {s['b_roll']}")
        out.append(f"🔊 SFX/Transisi : {s['sfx_transition']}")
        out.append(f"🎯 Pemicu/Pacing: {s['notes']}")
        if s.get("ai_prompt"):
            out.append(f"🔑 Prompt AI Gen: {s['ai_prompt']}")
        out.append("")

    out.append("==================================================")
    out.append("📌 PANDUAN EKSEKUSI PRODUKSI & KONSISTENSI:")
    out.append("1. DISIPLIN DURASI: Setiap scene <= 15 detik untuk mencegah audience drop-off.")
    out.append("2. TEMPO BICARA: Talent membaca dialog dengan kecepatan terukur (~1.9 kata/detik).")
    out.append("3. JUMP-CUT PACING: Editor memotong setiap jeda nafas/hening tanpa ampun.")
    out.append("4. KONSISTENSI AI: Salin 'Prompt AI Gen' ke Kling / Runway / Midjourney untuk hasil visual seragam.")
    out.append("==================================================")

    return "\n".join(out)


def calculate_retention_curve(scenes: list) -> dict:
    """
    Menghitung simulasi kurva retensi audiens (detik 0 s/d total durasi video) berdasarkan disiplin pacing,
    frekuensi pergantian scene, dan durasi tiap shot.
    Mendukung video pendek 30s hingga video panjang 120s secara dinamis.
    Menghasilkan DataFrame titik detik vs estimasi retensi (%), skor potensi viral (1-100),
    serta analisis risiko drop-off.
    """
    import pandas as pd

    if not scenes:
        sec_points = list(range(0, 61, 5))
        pct_points = [100.0, 88.0, 82.0, 78.0, 75.0, 72.0, 70.0, 68.0, 67.0, 65.0, 64.0, 63.0, 62.0]
        df_chart = pd.DataFrame({"Detik": sec_points, "Estimasi Retensi (%)": pct_points}).set_index("Detik")
        return {
            "df_chart": df_chart,
            "virality_score": 85,
            "retention_tier": "🚀 FYP Tier 1 (Potensi Viral Tinggi)",
            "final_retention": 62.0,
            "avg_scene_duration": 10.0,
            "max_scene_duration": 12,
            "total_duration": 60,
            "is_all_compliant": True,
            "risk_points": ["Pacing teratur, tidak ada scene membosankan."]
        }

    durations = [s.get("duration_sec", 10) for s in scenes]
    avg_dur = sum(durations) / max(1, len(durations))
    max_dur = max(durations) if durations else 10
    total_dur = sum(durations) if durations else 60
    max_chart_sec = max(30, total_dur)
    all_compliant = all(d <= 15 for d in durations)

    current_pct = 100.0
    sec_points = [0]
    pct_points = [100.0]
    risk_points = []

    elapsed = 0
    for idx, s in enumerate(scenes):
        s_dur = s.get("duration_sec", 10)
        s_num = s.get("scene_num", idx + 1)

        if idx == 0:
            if s_dur <= 7:
                current_pct -= 9.0
            else:
                current_pct -= 18.0
                risk_points.append(f"Scene 1 ({s_dur}s): Hook pembuka agak panjang ({s_dur}s). Untuk retensi maksimal, usahakan 3-6 detik.")
        else:
            if s_dur > 15:
                penalty = 12.0 + (s_dur - 15) * 1.5
                current_pct -= penalty
                risk_points.append(f"Scene {s_num} ({s_dur}s): Melebihi batas 15 detik! Berisiko audiens swipe-away.")
            elif s_dur <= 8:
                current_pct -= 3.5
            else:
                current_pct -= 5.5

        current_pct = max(25.0, min(100.0, current_pct))
        elapsed += s_dur
        sec_points.append(min(max_chart_sec, elapsed))
        pct_points.append(round(current_pct, 1))

        if elapsed >= max_chart_sec:
            break

    if sec_points[-1] < max_chart_sec:
        sec_points.append(max_chart_sec)
        pct_points.append(round(max(20.0, current_pct - 2.0), 1))

    final_retention = pct_points[-1]
    score = int(final_retention * 0.7 + (30 if all_compliant else 10))
    score = max(45, min(98, score))

    if score >= 85:
        tier = "🚀 FYP Tier 1 (Potensi Viral Sangat Tinggi)"
    elif score >= 70:
        tier = "⚡ FYP Tier 2 (Distribusi Algoritma Kuat)"
    else:
        tier = "⚠️ Perlu Peningkatan Pacing (Risiko Drop Cepat)"

    if not risk_points:
        risk_points.append("✅ Seluruh scene memenuhi batas maksimal <= 15 detik. Pacing visual sangat dinamis!")

    df_chart = pd.DataFrame({
        "Detik": sec_points,
        "Estimasi Retensi (%)": pct_points
    }).set_index("Detik")

    return {
        "df_chart": df_chart,
        "virality_score": score,
        "retention_tier": tier,
        "final_retention": final_retention,
        "avg_scene_duration": round(avg_dur, 1),
        "max_scene_duration": max_dur,
        "total_duration": max_chart_sec,
        "is_all_compliant": all_compliant,
        "risk_points": risk_points
    }


def evaluate_content_authority(scenes: list, full_text: str = "") -> dict:
    """
    Mengevaluasi tingkat kedalaman materi, otoritas praktisi, dan bukti data pendukung (Anti-AI Slop).
    Menganalisis:
    1. Metrik angka terukur (%, durasi hemat, derajat suhu, takaran eksak, ratio)
    2. Kausalitas ilmiah/teknis ('The Mechanism' & pembongkaran salah kaprah)
    3. Nama entitas spesifik (zero ambiguous generic words)
    4. B-Roll visual proof directing (grafik analitik, alat ukur fisik, makro uji coba)
    """
    import re

    all_audio = " ".join(s.get("audio", "") for s in scenes)
    all_visual = " ".join(f"{s.get('visual', '')} {s.get('b_roll', '')}" for s in scenes)
    combined = f"{all_audio} {all_visual} {full_text}".lower()

    # 1. Deteksi Metrik Angka Terukur (Percentages, Units, Precision Measurements)
    metric_patterns = [
        r'\b\d+[\.,]?\d*\s*%',                   # 40%, 1.2%
        r'\b\d+\s*(?:detik|menit|jam|hari|minggu|bulan|tahun)\b', # 2 jam, 15 menit
        r'\b\d+[\.,]?\d*\s*(?:derajat|celsius|°c|celcius)\b',    # 80 derajat
        r'\b\d+[\.,]?\d*\s*(?:gram|kg|liter|ml|mililiter|meter|cm|mm)\b', # 100 gram
        r'\b\d+[\.,]?\d*\s*(?:nm|newton|psi|bar|volt|watt|wpm|fps)\b',    # 25 Nm, 130 WPM
        r'\b\d+[\.,]?\d*\s*x\s*(?:lipat)?\b',    # 10x, 3.2x lipat
        r'\b\d+[\.,]?\d*\s*(?:koma|titik)\s*\d+\b' # satu koma dua
    ]

    detected_metrics = []
    for pat in metric_patterns:
        matches = re.findall(pat, combined, re.IGNORECASE)
        for m in matches:
            if m not in detected_metrics and len(detected_metrics) < 8:
                detected_metrics.append(m.strip())

    # 2. Deteksi Kausalitas "The Mechanism" & Pembongkaran Mitos
    causality_kws = [
        "karena", "memicu", "akibat", "mekanisme", "sehingga", "penyebab", 
        "dermatologi", "biologis", "mekanis", "reaksi", "asam amino", "enzim",
        "barrier", "defleksi", "adjuster", "konversi", "jurnal", "uji lab",
        "split-test", "few-shot", "context window", "algoritma", "tekanan"
    ]
    causality_hits = [kw for kw in causality_kws if kw in combined]

    # 3. Deteksi Visual Proof Directing (B-Roll yang Menampilkan Bukti Fisik)
    proof_visual_kws = [
        "grafik", "layar", "monitor", "dashboard", "makro", "probe", "timbangan", 
        "penggaris", "split screen", "kertas uji", "termometer", "stetoskop",
        "analitik", "before", "after", "tekstur", "close-up", "alat"
    ]
    visual_proof_hits = [kw for kw in proof_visual_kws if kw in all_visual.lower()]

    # 4. Deteksi Kata Samar yang DILARANG (Anti-Generik Check)
    fluff_kws = ["trik rahasia ini", "dua bahan ajaib", "aplikasi canggih ini", "beberapa tips", "cara ajaib"]
    detected_fluff = [kw for kw in fluff_kws if kw in combined]

    # Hitung Skor Otoritas (0 - 100)
    score = 65
    score += min(20, len(detected_metrics) * 5)
    score += min(15, len(causality_hits) * 3)
    score += min(10, len(visual_proof_hits) * 2.5)
    if detected_fluff:
        score -= 15
    score = max(50, min(99, int(score)))

    if score >= 90:
        tier = "💎 Subject Matter Expert (Tingkat Otoritas & Data Sangat Tinggi)"
        status = "Bebas Info Umum & AI Slop"
        badge_color = "#10b981"
    elif score >= 75:
        tier = "🔬 Praktisi Berbasis Data (Berbobot & Terukur)"
        status = "Kualitas Teruji"
        badge_color = "#4f46e5"
    else:
        tier = "⚠️ Konten Standar / Cenderung Umum"
        status = "Perlu Penguatan Data"
        badge_color = "#f59e0b"

    return {
        "authority_score": score,
        "authority_tier": tier,
        "status": status,
        "badge_color": badge_color,
        "metrics_found": detected_metrics,
        "causality_signals": causality_hits[:6],
        "visual_proof_signals": visual_proof_hits[:6],
        "fluff_detected": detected_fluff
    }


def get_smart_autopilot_presets(niche: str = "", hook: str = "", topic: str = "", existing_audience: str = "") -> dict:
    """
    Menghasilkan preset rekomendasi cerdas (Auto-Pilot) untuk Tahap 3 Storyboard
    berdasarkan Niche, Hook, dan Topik Konten secara 100% kontekstual dan hidup (Anti-Studio Monoton).
    """
    niche_lower = (niche or "").lower()
    topic_lower = (topic or "").lower()
    hook_lower = (hook or "").lower()
    combined = f"{niche_lower} {topic_lower} {hook_lower}"

    # Default preset (Creative Workspace Nyata & Segar, Bukan Studio Kosong)
    theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
    slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
    emotion = "👀 Rasa Penasaran Ekstrem (Curiosity Gap - Wajib Nonton Sampai Akhir)"
    visual = "🎥 Realistis Sinematik / Live Action (Talent Manusia / UGC 4K)"
    env = "Smart Workspace Modern dengan Meja Kayu & Tanaman Indoor (Warm Daylight)"
    color = "Moody Teal & Warm Orange Sinematik (Hollywood Blockbuster Look)"
    voice = "Santai & Empatik (Bestie Vibe, Akrab, Mengalir Luwes)"
    aud = existing_audience.strip() if existing_audience and existing_audience.strip() else "Penonton usia 20-35 tahun (Digital Native)"

    # 1. KULINER, RESEP, MAKANAN & DAPUR
    if any(k in combined for k in ["masak", "resep", "kuliner", "makanan", "panci", "bumbu", "dapur", "kuah", "bawang", "snack", "bento", "kue", "food", "air fryer"]):
        theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
        if not existing_audience.strip():
            aud = "Pecinta kuliner, ibu rumah tangga, dan anak kost yang hobi masak simpel"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "👀 Rasa Penasaran Ekstrem & Aha! Moment Kuliner"
        visual = "🎥 Realistis Sinematik / Live Action (Talent Manusia / UGC 4K)"
        env = "Dapur Rumah Minimalis Bersih & Estetik (Natural Morning Light & Marmer Putih)"
        color = "Warm Delicious Food Grade (Vibrant Saturation & Fresh Contrast)"
        voice = "Santai, bersahabat, tempo bicara riang 130 WPM, intonasi menggugah selera"

    # 2. SKINCARE, BODYCARE, PERAWATAN KULIT & SERUM
    elif any(k in combined for k in ["skincare", "serum", "kulit", "jerawat", "glowing", "toner", "sunscreen", "bodycare", "niacinamide", "pelembab", "retinol", "barrier"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Wanita & pria muda 18-32 tahun yang ingin kulit sehat glowing bebas jerawat"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "👀 Rasa Penasaran Ekstrem & Kelegaan Solutif Kulit"
        visual = "🎥 Live Action Clean High-Key 4K (Macro Skin Texture Focus)"
        env = "Vanity Mirror Kamar Mandi Marmer Putih Bersih (Clean Bright Ring Light & Rak Serum)"
        color = "Pastel Clean Skin-Tone Glow (Soft Warm White, Natural Rosy)"
        voice = "Empatik, ramah, artikulasi jelas, tempo mengalir luwes 128 WPM"

    # 3. MAKEUP, KOSMETIK & RIASAN
    elif any(k in combined for k in ["makeup", "make up", "lipstik", "cushion", "bedak", "riasan", "kosmetik", "eyeliner", "mascara", "foundation"]):
        theme = "🛍️ Review Jujur & Soft-Selling (Solusi Masalah)"
        if not existing_audience.strip():
            aud = "Wanita muda 18-30 tahun pecinta tutorial makeup harian & look praktis"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "👀 Rasa Penasaran Ekstrem (Curiosity Gap - Wajib Nonton Sampai Akhir)"
        visual = "🎥 Realistis Sinematik / Live Action (Macro Beauty Close-Up)"
        env = "Meja Rias Vanity Estetik dengan Cermin LED & Rak Kosmetik Rapi"
        color = "Vibrant Soft Glow (Warm Golden Highlight & Crisp Clean Focus)"
        voice = "Santai, ceria, tempo bicara hangat dan bersahabat 130 WPM"

    # 4. FASHION, OUTFIT, HIJAB, GAMIS & STREETWEAR
    elif any(k in combined for k in ["fashion", "outfit", "ootd", "hijab", "gamis", "baju", "celana", "sepatu", "sneaker", "dress", "streetwear"]):
        theme = "🛍️ Review Jujur & Soft-Selling (Solusi Masalah)"
        if not existing_audience.strip():
            aud = "Pria & wanita muda 18-35 tahun pencari inspirasi mix & match outfit stylish"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "💪 Semangat & Termotivasi (Percaya Diri & Upgrade Penampilan)"
        visual = "🎥 Realistis Sinematik / Live Action (Full-Body Dynamic Panning)"
        env = "Walk-in Closet Estetik / Kamar Tidur Modern dengan Full-Length Mirror & Natural Daylight"
        color = "Warm Fashion Editorial (Natural Daylight & Soft Contrast)"
        voice = "Santai, percaya diri, intonasi energik dan ekspresif 130 WPM"

    # 5. OTOMOTIF, MOTOR, MOBIL & BENGKEL
    elif any(k in combined for k in ["otomotif", "motor", "mobil", "bengkel", "mesin", "modifikasi", "oli", "ban", "belt", "pulley", "rem"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Pria 20-45 tahun penghobi otomotif & pemilik kendaraan harian"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "😱 FOMO & Ketakutan Rusak (Loss Aversion Mesin)"
        visual = "🎥 Cinematic Urban Garage 4K (Low Angle & Engine Macro)"
        env = "Garasi Modern Bersih dengan Tool Rack Rapi & Pencahayaan Neon Cool White"
        color = "Industrial Urban Contrast (Deep Metallic Grey, Warm Orange Fill)"
        voice = "Tegas, maskulin, berwibawa, tempo tenang tapi berenergi 130 WPM"

    # 6. FITNESS, GYM, DIET, KALORI & OLAHRAGA
    elif any(k in combined for k in ["fitness", "gym", "diet", "kalori", "nutrisi", "workout", "otot", "dumbel", "olahraga", "fat loss", "defisit"]):
        theme = "🥊 Bongkar Mitos & Realita Pahit (Hard Truth / Kontras)"
        if not existing_audience.strip():
            aud = "Pria & wanita 20-40 tahun yang ingin badan ideal & sehat tanpa tersiksa"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "💪 Semangat & Termotivasi (Dorongan Aksi Cepat Tanpa Nanti)"
        visual = "🎥 High-Energy Athletic UGC 4K (Crisp Motion & Muscle Tension)"
        env = "Gym Modern / Ruang Latihan Fitness dengan Mirror Wall & Dumbbell Rack"
        color = "Clean High-Key Athletic (Cool Natural Light, High Energy Contrast)"
        voice = "Punchy, bertenaga, membakar motivasi, artikulasi mantap 135 WPM"

    # 7. KOPI, CAFE, MINUMAN & BARISTA
    elif any(k in combined for k in ["kopi", "cafe", "kafe", "barista", "espresso", "latte", "manual brew", "cafe hopping"]):
        theme = "📖 Storytelling Pengalaman Nyata (Relatable & Emosional)"
        if not existing_audience.strip():
            aud = "Pecinta kopi, penikmat suasana kafe & home barista muda 20-35 tahun"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "😌 Lega & Tenang (Sensasi Rileks & Kenikmatan Momen)"
        visual = "🎥 Cinematic Warm Macro UGC 4K (Pour-over & Coffee Steam Focus)"
        env = "Coffee Shop Estetik / Espresso Bar Modern (Warm Bokeh Background & Meja Kayu)"
        color = "Moody Warm Coffee Shop (Deep Amber, Soft Wood Tone)"
        voice = "Storyteller Hangat & Tenang, artikulasi santai 125 WPM"

    # 8. TEKNOLOGI, GADGET, HP, PC & DESK SETUP
    elif any(k in combined for k in ["gadget", "hp", "charger", "tws", "desk setup", "laptop", "tablet", "pc", "komputer"]):
        theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
        if not existing_audience.strip():
            aud = "Tech enthusiast & pekerja produktif usia 20-35 tahun yang haus efisiensi"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "🤯 Mind-Blown / Kaget (Membongkar Fitur Tersembunyi)"
        visual = "🎥 Live Action Tech Desk UGC 4K (Punch-In Layar & Produk)"
        env = "Desk Setup Gadget & Ambient Neon Light (Tech Minimalist Dark)"
        color = "Clean High-Key SaaS & Tech (Bright Natural, Cool Blue Accent)"
        voice = "Punchy, percaya diri, artikulasi renyah, tempo 135 WPM"

    # 9. AI TOOLS, CODING, CHATGPT & OTOMASI DIGITAL
    elif any(k in combined for k in ["ai", "tech", "coding", "software", "prompt", "chatgpt", "midjourney", "otomasi", "workflow"]):
        theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
        if not existing_audience.strip():
            aud = "Freelancer, digital creator & pekerja kantoran yang ingin efisiensi kerja 10x"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "🤯 Mind-Blown / Kaget (Membongkar Rahasia Efisiensi Ekstrem)"
        visual = "🎥 Live Action Tech Desk UGC 4K (Dinamis Punch-In)"
        env = "Desk Setup Minimalis Modern dengan Dual Monitor & Soft Ambient Glow"
        color = "Clean High-Key Tech (Bright Daylight, Cool Blue Accent)"
        voice = "Punchy, taktis, percaya diri, tempo 135 WPM"

    # 10. BISNIS ONLINE, AFFILIATE TIKTOK/SHOPEE & SIDE HUSTLE
    elif any(k in combined for k in ["bisnis", "affiliate", "side hustle", "cuan", "jualan", "dropship", "reseller", "toko"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Pekerja kantoran & pemula 22-35 tahun yang mencari side-income nyata"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "😱 FOMO & Dorongan Pertumbuhan Finansial Nyata"
        visual = "🎥 Live Action UGC Sinematik 4K (Dinamis Punch-In Dashboard & Layar)"
        env = "Smart Workspace Modern / Meja Kerja Rapi dengan Laptop & Tanaman Indoor"
        color = "Moody Teal & Warm Orange Sinematik (Hollywood Blockbuster Look)"
        voice = "Santai tapi tegas, penuh keyakinan, artikulasi padat 132 WPM"

    # 11. KEUANGAN PRIBADI, SAHAM, BEBAS UTANG PINJOL & INVESTASI
    elif any(k in combined for k in ["keuangan", "uang", "finansial", "saham", "reksadana", "investasi", "utang", "pinjol", "anggaran", "gaji"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Pekerja muda 22-38 tahun yang ingin mengelola gaji & terbebas dari jeratan finansial"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "😱 FOMO & Kelegaan Finansial (Solusi Bebas Stress)"
        visual = "🎥 Live Action UGC Sinematik 4K (Grafik Finansial & Ekspresi Empati)"
        env = "Ruang Kerja Modern Bersih / Smart Workspace dengan Laptop & Grafik Finansial"
        color = "Clean Professional Contrast (Deep Blue Accent, Warm Natural Fill)"
        voice = "Tegas & Berwibawa, menenangkan dan kredibel, tempo 128 WPM"

    # 12. KARIR, INTERVIEW KERJA, CV ATS & FREELANCER
    elif any(k in combined for k in ["karir", "interview", "cv", "ats", "kerja", "kantor", "gaji", "promosi", "freelance"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Jobseeker & pekerja muda usia 20-30 tahun yang ingin percepatan karir"
        slang = "👔 Saya - Anda / Rekan-rekan (Profesional, Otoritatif, Ramah)"
        emotion = "💪 Semangat & Percaya Diri Hadapi Rekruter"
        visual = "🎥 Live Action Sinematik Korporat Modern"
        env = "Kantor Korporat Modern / Meja Kerja Rapi dengan Pencahayaan Profesional"
        color = "Clean Corporate Natural (Soft Daylight, Neutral Tone)"
        voice = "Otoritatif, profesional, artikulasi sangat jelas dan percaya diri 130 WPM"

    # 13. PARENTING, ANAK, BAYI, MPASI & KELUARGA
    elif any(k in combined for k in ["parenting", "anak", "ibu", "keluarga", "bayi", "ayah", "mpasi", "stroller", "mainan"]):
        theme = "📖 Storytelling Pengalaman Nyata (Relatable & Emosional)"
        if not existing_audience.strip():
            aud = "Orang tua muda (Moms & Dads) usia 24-38 tahun"
        slang = "🤝 Aku - Kamu / Teman-teman (Hangat, Empatik, Ramah Sahabat)"
        emotion = "😌 Lega & Tenang (Mendapatkan Solusi Instan Atas Masalah Anak)"
        visual = "🎥 Live Action Warm Family Lifestyle 4K"
        env = "Ruang Bermain Anak Ceria & Ruang Keluarga Hangat Bersih (Natural Daylight)"
        color = "Pastel Dreamy Aesthetic (Soft Glow, Warm Highlights, Airy Feel)"
        voice = "Storyteller Hangat & Reflektif (Penuh Emosi & Sentuhan Personal)"

    # 14. HEWAN PELIHARAAN (KUCING, ANJING & AKSESORIS)
    elif any(k in combined for k in ["hewan", "kucing", "anjing", "pet", "cat", "dog", "anabul"]):
        theme = "📖 Storytelling Pengalaman Nyata (Relatable & Emosional)"
        if not existing_audience.strip():
            aud = "Pecinta anabul & pemilik hewan peliharaan usia 18-35 tahun"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "🥰 Menggemaskan & Rasa Ingin Tahu Perilaku Hewan"
        visual = "🎥 Macro Close-Up UGC 4K (Pet Eye-Level Angle)"
        env = "Ruang Keluarga Hangat Bersih dengan Karpet Lembut & Pet Corner Estetik"
        color = "Warm Coziness Glow (Natural Soft Sunlight & Clean Floor)"
        voice = "Ceria, ramah, penuh kasih sayang, tempo bersahabat 130 WPM"

    # 15. TANAMAN HIAS, BERKEBUN & URBAN FARMING
    elif any(k in combined for k in ["tanaman", "kebun", "taman", "bunga", "urban farming", "bonsai", "hidroponik", "pupuk"]):
        theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
        if not existing_audience.strip():
            aud = "Penghobi tanaman & pegiat urban farming rumah usia 22-50 tahun"
        slang = "🤝 Aku - Kamu / Teman-teman (Hangat, Empatik, Ramah Sahabat)"
        emotion = "🌱 Segar & Terinspirasi (Aha! Moment Menumbuhkan Tanaman Subur)"
        visual = "🎥 Live Action Natural Macro 4K (Sunlit Leaf Texture & Soil)"
        env = "Taman Rumah Minimalis / Balkon Urban Farming Hijau (Natural Daylight & Fresh Foliage)"
        color = "Vibrant Botanical Green (Fresh Organic Contrast, Crisp Sunlit Tone)"
        voice = "Santai, sejuk, mengalir ramah, tempo tenang 126 WPM"

    # 16. DESAIN, EDITING VIDEO CAPCUT & KONTEN KREATOR
    elif any(k in combined for k in ["desain", "canva", "video editing", "capcut", "konten kreator", "preset", "thumbnail"]):
        theme = "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)"
        if not existing_audience.strip():
            aud = "Konten kreator pemula, video editor HP & pebisnis yang butuh visual menarik"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "🤯 Mind-Blown / Kaget (Trik Cepat Editing 1 Menit Jadi Keren)"
        visual = "🎥 Live Action Creator Desk UGC 4K (Screen UI Zoom-In)"
        env = "Creative Creator Desk dengan Ring Light, Dual Monitor & Acoustic Backdrop"
        color = "Moody Creator Neon Accent (Warm Key Light, Subtle Violet/Cyan Fill)"
        voice = "Punchy, kreatif, bersemangat dan to-the-point 135 WPM"

    # 17. PERLENGKAPAN RUMAH TANGGA & CLEANTOK
    elif any(k in combined for k in ["rumah tangga", "bersih", "cleantok", "dekorasi", "kamar", "sapu", "pel", "organizer"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Penyuka rumah rapi, ibu rumah tangga & anak kos yang suka aesthetic living"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "😌 Lega & Sangat Puas (Satisfying Transformation & Clean Room)"
        visual = "🎥 Satisfying Clean ASMR Live Action 4K"
        env = "Dapur & Ruang Tamu Rumah Bersih Estetik (CleanTok Modern Look)"
        color = "Crisp Ultra-Clean Bright (High Contrast, Sparkling White Highlights)"
        voice = "Santai, menenangkan, artikulasi renyah dan bersahabat 128 WPM"

    # 18. TRAVEL, WISATA, LIBURAN & JALAN-JALAN
    elif any(k in combined for k in ["travel", "wisata", "liburan", "hotel", "healing", "jalan-jalan", "alam", "pantai", "gunung"]):
        theme = "📖 Storytelling Pengalaman Nyata (Relatable & Emosional)"
        if not existing_audience.strip():
            aud = "Traveler muda 20-35 tahun pencari hidden gem & liburan hemat"
        slang = "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)"
        emotion = "👀 Rasa Penasaran Ekstrem (Curiosity Gap - Hidden Gem)"
        visual = "🎥 Cinematic Wide Angle Outdoor 4K (Golden Hour Sunlight)"
        env = "Outdoor Dinamis / Panorama Alam & Spot Wisata Estetik (Natural Sunlight)"
        color = "Vibrant Travel Cinematic (Golden Hour Sky, Rich Blue Waters)"
        voice = "Punchy, Hype & Berenergi Tinggi (Pemicu Adrenalin, Semangat Membara)"

    # 19. GAMING, ESPORT & MABAR
    elif any(k in combined for k in ["game", "gaming", "esport", "streamer", "mabar", "gameplay", "mobile legends", "ff", "pubg"]):
        theme = "🎭 Skit Komedi / Parodi Relatable (Humor Situasi Sehari-hari)"
        if not existing_audience.strip():
            aud = "Gamers & Gen Z 15-28 tahun penikmat gameplay & tips mabar"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "🤯 Mind-Blown / Kaget (Membongkar Meta Rahasia Game)"
        visual = "🎥 Dynamic Dark Gamer POV 4K (Screen Capture & Facecam)"
        env = "Dark Gaming Room dengan Ambient RGB Neon & Gaming Chair Setup"
        color = "Vibrant Cyberpunk Pop (Neon Cyan & Magenta Edge Light)"
        voice = "Punchy, Hype & Berenergi Tinggi (Pemicu Adrenalin, Semangat Membara)"

    # 20. PENGEMBANGAN DIRI, BUKU & PRODUKTIVITAS
    elif any(k in combined for k in ["pengembangan diri", "produktivitas", "mindset", "buku", "kebiasaan", "atomic habits", "fokus"]):
        theme = "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)"
        if not existing_audience.strip():
            aud = "Pekerja muda & pembelajar mandiri 20-35 tahun yang ingin upgrade kualitas hidup"
        slang = "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)"
        emotion = "💪 Semangat & Termotivasi (Refleksi Mendalam & Dorongan Maju)"
        visual = "🎥 Live Action Moody Warm 4K (Focus Macro ke Buku & Jurnal)"
        env = "Ruang Baca Estetik / Meja Kerja Kayu Minimalis dengan Rak Buku & Tanaman Indoor"
        color = "Moody Warm Intellectual (Soft Amber Light, Film Grain Texture)"
        voice = "Tegas, tenang, berwibawa tapi akrab, tempo teratur 126 WPM"

    return {
        "theme": theme,
        "audience": aud,
        "slang": slang,
        "emotion": emotion,
        "visual_style": visual,
        "environment": env,
        "color_grading": color,
        "voice_style": voice
    }


def get_contextual_pro_cinematography(niche_or_topic: str = "", scene_num: int = 1, scene_type: str = "") -> dict:
    """
    Menghasilkan direktif sinematografi sutradara profesional dan style editing komersial
    secara 100% kontekstual dan otomatis sesuai niche dan urutan scene.
    Mendukung generator video AI kelas atas: Kling AI, Runway Gen-3 Alpha, Luma Dream Machine, Sora, dan Midjourney v6.
    """
    text_lower = (niche_or_topic or "").lower()
    s_idx = max(1, scene_num)

    # 1. KULINER, RESEP, MAKANAN & DAPUR
    if any(k in text_lower for k in ["masak", "resep", "kuliner", "makanan", "panci", "bumbu", "dapur", "kuah", "bawang", "food", "snack", "kue"]):
        if s_idx == 1:
            cam = "Dynamic 1.2x whip-pan punch-in to sizzling cooking pan, eye-level perspective"
        elif s_idx in [2, 4]:
            cam = "Extreme macro probe lens gliding 10mm smoothly above fresh ingredients, shallow depth of field"
        elif s_idx == 3:
            cam = "Slow cinematic high-angle 45-degree cooking glide, steam swirling upwards into warm backlight"
        else:
            cam = "Smooth handheld Steadicam push-in towards plated dish, appetizing presentation angle"
        
        lens = "Shot on 100mm Macro Probe Lens f/2.8, creamy circular optical bokeh, Black Pro-Mist 1/4 diffusion"
        lighting = "Warm 3200K tungsten backlight illuminating rising steam and liquid droplets, soft 5600K key light, subtle specular highlights"
        color_lut = "Warm Delicious Food Grade, Kodak Vision3 500T color science, rich appetizing saturation & organic contrast"
        physics = "120fps high-speed capture on sizzling oil droplets, fluid steam condensation, natural food textures, photorealistic 8k uhd"
        editing = "ASMR jump-cut cadence, cutting on knife chop and sizzle beats, zero dead air"
        badge = "🍳 Macro Probe 100mm | 3200K Tungsten Steam Backlight"

    # 2. SKINCARE, BODYCARE, PERAWATAN KULIT & BEAUTY
    elif any(k in text_lower for k in ["skincare", "serum", "kulit", "jerawat", "glowing", "toner", "sunscreen", "bodycare", "niacinamide", "pelembab", "retinol", "beauty"]):
        if s_idx == 1:
            cam = "Slow 1.2x cinematic push-in on subject's clean glowing skin, confident eye contact locking into lens"
        elif s_idx in [2, 4]:
            cam = "Extreme macro 85mm glide on authentic skin pores and liquid serum droplet slowly gliding down cheek"
        elif s_idx == 3:
            cam = "Smooth 45-degree orbiting pan around clean vanity mirror setup, capturing subtle light reflections"
        else:
            cam = "Gentle handheld beauty portrait tracking, natural smiling expression in mirror"
        
        lens = "Shot on 85mm Portrait Prime Lens f/1.4, creamy circular optical bokeh, subtle Pro-Mist soft highlight roll-off"
        lighting = "High-key luxury cosmetic lighting: diffused softbox ring light with crisp catchlight in iris, gentle warm wrap-around fill"
        color_lut = "Pastel Clean Skin-Tone Glow, soft warm white with natural rosy tones, low contrast luxury aesthetic"
        physics = "Subsurface scattering (SSS) on natural skin pores, zero plastic AI face smoothing, realistic moist serum sheen, 24fps film motion cadence"
        editing = "Fluid micro-whip transitions, matching cut on gentle skin patting beats, clean modern pace"
        badge = "✨ High-Key Cosmetic 85mm f/1.4 | Subsurface Scattering Pores"

    # 3. GADGET, TECH, AI, CODING & SOFTWARE
    elif any(k in text_lower for k in ["gadget", "hp", "charger", "tws", "desk setup", "laptop", "pc", "ai", "tech", "coding", "software", "prompt", "chatgpt"]):
        if s_idx == 1:
            cam = "Rapid 1.25x punch-in push on high-tech desk setup and focused creator expression, energetic dynamic zoom"
        elif s_idx in [2, 4]:
            cam = "Smooth lateral tracking slider across dual monitors displaying code and AI dashboards with shallow depth"
        elif s_idx == 3:
            cam = "Low-angle Dutch tilt tracking dolly with subtle motion blur, highlighting glowing keyboard and laptop chassis"
        else:
            cam = "Direct eye-level medium close-up, creator smiling with firm authority, screen glow reflecting on eyeglasses"
        
        lens = "Shot on 35mm Anamorphic Prime Lens f/1.8, horizontal anamorphic blue streak flares, razor-sharp optical edge-to-edge"
        lighting = "Cyberpunk Tech Noir lighting: 6500K cool daylight key light, neon cyan and magenta rim light separating edges, matte screen ambient fill"
        color_lut = "Sleek Apple Keynote aesthetic, deep matte blacks with punchy electric cyan and cold steel contrast"
        physics = "Matte metal chassis specular highlights, crystal-clear glass reflections, crisp 24fps film motion cadence, zero temporal jitter"
        editing = "Speed-ramp zoom punch-ins on UI elements, digital glitch whip transitions, fast tech cadence"
        badge = "⚡ 35mm Anamorphic Punch-In | Cyber Neon Rim & Matte Metal"

    # 4. OTOMOTIF, MOTOR, MOBIL & BENGKEL
    elif any(k in text_lower for k in ["otomotif", "motor", "mobil", "bengkel", "mesin", "modifikasi", "oli", "ban", "belt", "pulley"]):
        if s_idx == 1:
            cam = "Aggressive low-angle Dutch tilt tracking dolly alongside vehicle, fast cinematic approach with asphalt grit"
        elif s_idx in [2, 4]:
            cam = "Macro probe lens sliding smoothly inside engine bay, focusing on mechanical belts and rotating pulleys"
        elif s_idx == 3:
            cam = "Handheld documentary sway with subtle mechanical vibration at vehicle eye-level, focused hands adjusting tools"
        else:
            cam = "Hero low-angle medium shot, creator firmly shutting vehicle hood, triumphant confident smile"
        
        lens = "Shot on 28mm Wide Anamorphic Lens f/2.0, high-speed shutter angle (crisp motion freeze), deep field of view"
        lighting = "Dramatic industrial contrast: cool white 6000K neon overhead work lights, warm incandescent work lamp rim glow, specular metallic flares"
        color_lut = "Industrial Gritty Contrast, deep metallic slate greys, warm orange accent highlights, Michael Bay filmic grading"
        physics = "Glossy car paint specular reflections, authentic chrome metallic sheen, realistic engine heat haze distortion, 24fps film cadence"
        editing = "Hard impact cuts on ratchet clicks and engine revs, quick flash-frame transitions, gritty pacing"
        badge = "🏎️ Low-Angle Dutch Tilt 28mm | Industrial Neon & Chrome Flares"

    # 5. FITNESS, GYM, DIET, KALORI & OLAHRAGA
    elif any(k in text_lower for k in ["fitness", "gym", "diet", "kalori", "nutrisi", "workout", "otot", "dumbel", "olahraga", "fat loss"]):
        if s_idx == 1:
            cam = "Low-angle upward-tilted tracking shot following athletic movement, high-energy forward glide"
        elif s_idx in [2, 4]:
            cam = "Side profile medium tracking dolly matching subject's workout tempo and muscle contraction"
        elif s_idx == 3:
            cam = "Dynamic 360-degree orbital pan around athlete with tense focus and determined facial expression"
        else:
            cam = "Direct medium close-up, athletic creator catching breath with confident smile, wiping sweat"
        
        lens = "Shot on 24mm Wide Cine Prime f/2.2, crisp 90-degree fast shutter angle (zero motion blur on sweat droplets)"
        lighting = "High-contrast athletic chiaroscuro: harsh overhead top-down rim light carving muscle definition, soft side fill"
        color_lut = "Nike Commercial High-Contrast athletic look, desaturated background with warm golden skin highlights"
        physics = "Realistic sweat glistening on skin, visible muscle fiber definition under tension, zero digital smoothing, 24fps film cadence"
        editing = "Impact jump-cuts synced with heavy lifting reps and bass-heavy beat drops, high-tempo cadence"
        badge = "💪 24mm Wide Cine | 90° Fast Shutter & Chiaroscuro Muscle Rim"

    # 6. KOPI, CAFE, MINUMAN & BARISTA
    elif any(k in text_lower for k in ["kopi", "cafe", "kafe", "barista", "espresso", "latte", "manual brew"]):
        cam = "Slow-motion macro glide following pour-over stream, rising steam swirling in warm backlight"
        lens = "Shot on 100mm Macro Prime Lens f/2.8, creamy circular optical bokeh, vintage analog lens warmth"
        lighting = "Warm 2800K amber rim lighting illuminating liquid droplets and steam, soft golden hour key light"
        color_lut = "Artisan Coffee House, rich earthy espresso browns, golden honey amber tones, film grain emulation"
        physics = "High-speed 120fps fluid pour dynamics, swirling crema micro-bubbles, rising aromatic steam"
        editing = "Gentle match-cuts on liquid pouring rhythms, warm acoustic pacing"
        badge = "☕ Artisan 100mm Macro | 2800K Amber Rim & 120fps Fluid Crema"

    # 7. FASHION, OUTFIT, HIJAB, GAMIS & STYLE
    elif any(k in text_lower for k in ["fashion", "outfit", "ootd", "hijab", "gamis", "baju", "celana", "sepatu", "sneaker", "dress"]):
        cam = "Full-body walking tracking dolly backwards, smooth Steadicam glide at torso level capturing fabric flow"
        lens = "Shot on 50mm Prime Lens f/1.2, dreamy edge-to-edge optical roll-off, Black Pro-Mist 1/4 diffusion"
        lighting = "Vogue Editorial natural golden hour backlight, soft bounce board key fill, rim separation"
        color_lut = "Editorial Fashion Warm LUT, muted pastel background, rich vibrant fabric textures"
        physics = "Realistic fabric sway and drape dynamics in motion, authentic textile weave textures, natural model pacing"
        editing = "Rhythmic beat cuts on footsteps and spin turns, runway fashion cadence"
        badge = "👗 Vogue Editorial 50mm f/1.2 | Pro-Mist Diffusion & Fabric Sway"

    # 8. BISNIS, FINANSIAL, EDUKASI, KARIR & GENERAL
    else:
        if s_idx == 1:
            cam = "Slow authoritative 1.15x push-in on creator speaking directly to camera, firm eye contact and confident stance"
        elif s_idx in [2, 4]:
            cam = "Parallax tracking slider move with foreground modern interior element blurring past smoothly into subject"
        elif s_idx == 3:
            cam = "45-degree angle profile medium shot transitioning smoothly into close-up on key gesture"
        else:
            cam = "Direct eye-level medium shot, warm welcoming smile, natural hand gesture inviting audience action"
        
        lens = "Shot on 35mm Arri Signature Prime Lens f/1.8, creamy shallow depth of field, subtle Black Pro-Mist 1/8"
        lighting = "Masterclass corporate documentary lighting: soft 45-degree Rembrandt key light, volumetric warm window daylight rim glow"
        color_lut = "Moody Teal & Warm Amber Sinematik (Hollywood Blockbuster & Bloomberg aesthetic), rich dynamic range"
        physics = "Authentic skin micro-textures, natural facial expressions with micro-twitches, architectural depth, 24fps cinema cadence"
        editing = "Punchy J-cut audio leading visual transition, micro-zoom on power words, zero dead air"
        badge = "🎬 Arri 35mm Prime f/1.8 | Rembrandt 45° Key & Volumetric Daylight"

    full_suffix = f"{lens}, {lighting}, {color_lut}, {physics}, master commercial cinematography --ar 9:16 --v 6.1 --style raw"

    return {
        "camera_motion": cam,
        "lens_optics": lens,
        "lighting_setup": lighting,
        "color_lut": color_lut,
        "texture_physics": physics,
        "editing_style": editing,
        "display_badge": badge,
        "engine_suffix": full_suffix
    }


def build_pro_ai_video_prompt(
    base_prompt: str = "",
    niche_or_topic: str = "",
    scene_num: int = 1,
    visual_dir: str = "",
    env: str = "",
    color: str = ""
) -> str:
    """
    Menyusun prompt video AI kelas sutradara Hollywood/Komersial (Kling, Runway Gen-3, Sora, Midjourney)
    menggunakan formula 6-layer yang kaya pergerakan kamera, optik, tata cahaya, dan fisika rendering.
    """
    cine = get_contextual_pro_cinematography(niche_or_topic, scene_num=scene_num)
    
    # Bersihkan base prompt dari sisa tag teknis
    clean_base = (base_prompt or "").strip()
    clean_base = re.sub(r'--ar\s+[0-9\:]+', '', clean_base, flags=re.IGNORECASE).strip()
    clean_base = re.sub(r'--v\s+[0-9\.]+', '', clean_base, flags=re.IGNORECASE).strip()
    clean_base = re.sub(r'--style\s+\w+', '', clean_base, flags=re.IGNORECASE).strip()

    # Cek apakah base_prompt sudah sangat kaya (sudah memiliki direktif sutradara pro)
    has_pro_cues = any(w in clean_base.lower() for w in [
        "anamorphic", "lens f/", "bokeh", "shutter", "rembrandt", "rim light", 
        "subsurface scattering", "pro-mist", "dutch tilt", "push-in", "probe lens"
    ])

    if clean_base and len(clean_base) > 120 and has_pro_cues:
        # Prompt sudah sangat kaya dari LLM, pastikan hanya ditutup dengan aspect ratio baku
        return f"{clean_base} --ar 9:16 --v 6.1 --style raw"

    # Jika prompt masih pendek atau generik, sintesis dengan formula 6-layer sutradara pro
    action_core = clean_base if (clean_base and len(clean_base) > 25 and not clean_base.lower().startswith("cinematic vertical 9:16 shot")) else (visual_dir or "subject looking directly into camera with intense authentic expression")
    env_str = f"set in {env}" if env else "authentic detailed setting"
    color_str = f"{color}" if color else cine["color_lut"]

    pro_prompt = (
        f"{cine['camera_motion']}, {action_core}, {env_str}, "
        f"{cine['lens_optics']}, {cine['lighting_setup']}, {color_str}, "
        f"{cine['texture_physics']}, master commercial cinematography --ar 9:16 --v 6.1 --style raw"
    )

    return pro_prompt






