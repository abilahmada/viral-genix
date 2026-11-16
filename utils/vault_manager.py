"""
ViralGenix - Content Vault & Project Pipeline Manager
Menyimpan, memperbarui, dan mengelola draf proyek konten terpadu (ContentDraft) secara permanen
di penyimpanan lokal (data/content_vault.json) untuk alur kerja riset berkelanjutan.
"""

import os
import json
import time
import io
import re
import uuid
import zipfile
from datetime import datetime
from typing import List, Dict, Any, Optional

VAULT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "content_vault.json")

STATUS_OPTIONS = [
    "💡 Ide & Riset",
    "📝 Skrip Selesai",
    "🎙️ Siap Syuting",
    "🎬 Editing CapCut",
    "🚀 Siap Posting",
    "✅ Sudah Tayang"
]

def _ensure_vault_exists():
    """Memastikan folder data dan file content_vault.json sudah ada."""
    os.makedirs(os.path.dirname(VAULT_FILE), exist_ok=True)
    if not os.path.exists(VAULT_FILE):
        with open(VAULT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def extract_closing_bridge(draft: Dict[str, Any]) -> str:
    """Mengekstraksi atau menyusun skrip jembatan penutup (CTA) yang dijamin tidak kosong."""
    script = draft.get("closing_bridge_script", "").strip()
    if script and len(script) > 10:
        return script
    
    table_md = draft.get("storyboard_table_md", "")
    cta_m = re.search(r'Jembatan Penutup.*?:?\s*(?:_|\*|")?([^"\*\_\n]+)', table_md, re.IGNORECASE)
    if cta_m:
        return cta_m.group(1).strip()
    
    cta_m2 = re.search(r'CTA.*?:\s*(?:_|\*|")?([^"\*\_\n]+)', table_md, re.IGNORECASE)
    if cta_m2:
        return cta_m2.group(1).strip()

    product = draft.get("product_name") or "informasi lengkapnya"
    return f"Mau tahu rahasia dan langkah praktisnya? Langsung cek {product} lewat link di bio profil sekarang sebelum terlambat!"


def extract_clean_speech_dialogue(draft: Dict[str, Any]) -> str:
    """
    Mengekstraksi narasi skrip suara bersih (pure spoken dialogue) tanpa instruksi teknis visual/B-roll
    dan tanpa timestamp, sehingga siap dibaca mengalir di Teleprompter atau disalin ke HP dalam 1 klik.
    """
    table_md = draft.get("storyboard_table_md", "").strip()
    hook = draft.get("hook_verbal", "").strip()
    bridge = extract_closing_bridge(draft).strip()

    spoken_lines = []

    if table_md:
        try:
            from utils.export_helpers import markdown_table_to_dataframe
            df = markdown_table_to_dataframe(table_md)
            if df is not None and not df.empty:
                col_target = None
                for col in df.columns:
                    cl = col.lower()
                    if "audio" in cl or "skrip" in cl or "dialog" in cl or "naskah" in cl:
                        col_target = col
                        break
                if not col_target and len(df.columns) >= 3:
                    col_target = df.columns[2]

                if col_target:
                    for _, row in df.iterrows():
                        val = str(row[col_target]).strip().strip('"').strip('*')
                        if val and val.lower() != "nan" and len(val) > 2:
                            spoken_lines.append(val)
        except Exception:
            pass

    # Jika tabel belum menghasilkan dialog, coba ekstrak dari beat narasi berbutir
    if not spoken_lines and table_md:
        beats = re.findall(
            r'[\*\-]\s*\*?Detik\s*\d+\s*[\-\–]\s*\d+[^:]*:\s*(.*?)(?=\n\s*[\*\-]\s*\*?Detik|\n\s*[\*\-]\s*\*?Jembatan|\n\s*[\*\-]\s*\*?Caption|\Z)',
            table_md,
            re.DOTALL | re.IGNORECASE
        )
        if beats:
            for b in beats:
                cl = b.strip().strip('"').strip('*').strip()
                if cl:
                    spoken_lines.append(cl)

    # Pastikan hook ada di awal jika belum tercakup
    full_text = " ".join(spoken_lines)
    if hook and (not spoken_lines or hook.lower() not in full_text.lower()[:150]):
        spoken_lines.insert(0, hook)

    # Pastikan closing bridge ada di akhir jika belum tercakup
    full_text = " ".join(spoken_lines)
    if bridge and (bridge.lower() not in full_text.lower()[-200:]):
        spoken_lines.append(bridge)

    if spoken_lines:
        return "\n\n".join(spoken_lines)

    # Fallback jika naskah benar-benar belum di-generate
    fallback = []
    if hook:
        fallback.append(hook)
    fallback.append(f"Hari ini kita bakal bahas tuntas tentang {draft.get('keyword', draft.get('title', 'topik ini'))}. Banyak orang yang belum tahu kalau rahasia terbesarnya sebenarnya sesederhana ini.")
    if bridge:
        fallback.append(bridge)
    return "\n\n".join(fallback)



def extract_copywriting_kit(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mengekstraksi atau menyusun seluruh komponen kit publikasi:
    - Caption A (Storytelling & Emosional)
    - Caption B (To-the-point & Agitatif)
    - Comment Bait
    - 10 Hashtags
    - Rekomendasi Jam Upload
    Dijamin 100% lengkap dan tidak ada bagian yang kosong.
    """
    pub_md = draft.get("publication_kit_md", "").strip()
    table_md = draft.get("storyboard_table_md", "").strip()

    cap_a = draft.get("caption_storytelling", "").strip()
    cap_b = draft.get("caption_punchy", "").strip()
    comment_bait = draft.get("comment_bait_question", "").strip()
    hashtags = draft.get("hashtags", [])
    prime_time = draft.get("prime_time_recommendation", "").strip()

    # 1. Ekstrak dari publication_kit_md jika ada
    if pub_md:
        if not cap_a:
            m_a = re.search(r'(?:Variasi\s*A|Pilihan\s*A|Caption\s*A)[^:\n]*:?\s*(.*?)(?=\n\s*(?:-\s*\*)?(?:Variasi\s*B|Pilihan\s*B|Caption\s*B|###|\Z))', pub_md, re.DOTALL | re.IGNORECASE)
            if m_a:
                cap_a = m_a.group(1).strip().strip('>').strip('*').strip()
        
        if not cap_b:
            m_b = re.search(r'(?:Variasi\s*B|Pilihan\s*B|Caption\s*B)[^:\n]*:?\s*(.*?)(?=\n\s*(?:-\s*\*)?(?:###|Paket|Hashtag|Comment\s*Bait|\Z))', pub_md, re.DOTALL | re.IGNORECASE)
            if m_b:
                cap_b = m_b.group(1).strip().strip('>').strip('*').strip()

        if not comment_bait:
            m_cb = re.search(r'(?:Comment\s*Bait|Pemicu\s*Komentar|Pertanyaan\s*Komentar)[^:\n]*:?\s*([^\n]+)', pub_md, re.IGNORECASE)
            if m_cb:
                comment_bait = m_cb.group(1).strip().strip('*').strip('_').strip()

        if not prime_time:
            m_pt = re.search(r'(?:Jendela\s*1|Prime\s*Time|Jam\s*Tayang|Waktu\s*Upload)[^:\n]*:?\s*([^\n]+)', pub_md, re.IGNORECASE)
            if m_pt:
                prime_time = m_pt.group(1).strip().strip('*').strip('_').strip()

        if not hashtags:
            hashtags = re.findall(r'#\w+', pub_md)

    # 2. Coba ekstrak dari storyboard_table_md jika masih kosong (format Sprint 7 Hari)
    if not cap_a and table_md:
        m_cap = re.search(r'Caption Siap Copas.*?:\s*\n?(.*?)(?:\n-\s*\*\*Hashtag|\n-\s*\*\*Jembatan|\Z)', table_md, re.DOTALL | re.IGNORECASE)
        if m_cap:
            cap_a = m_cap.group(1).strip().strip('>').strip()

    if not hashtags and table_md:
        hashtags = re.findall(r'#\w+', table_md)

    # 3. Fallbacks jika masih kosong agar TIDAK PERNAH ADA YANG KOSONG
    title = draft.get("title", "Video Konten")
    keyword = draft.get("keyword") or title
    niche = draft.get("niche", "Edukasi")
    product = draft.get("product_name") or "link di bio profil"

    if not cap_a:
        cap_a = f"""Jujur, banyak orang yang ngerasa stuck saat mau capai hasil maksimal di topik ini. Kebanyakan gagal bukan karena kurang pintar, tapi karena gak pernah diajarin teknik aslinya secara step-by-step.

Kalau kamu capek buang waktu dan tenaga tanpa hasil yang jelas, video ini wajib kamu tonton dan simpan sekarang juga.

Mau tahu cara praktis dan panduan lengkapnya? Cek {product} sekarang sebelum terlambat! 👇"""

    if not cap_b:
        cap_b = f"""Stop lakukan cara lama kalau gak mau buang waktu dan tenaga sia-sia! ❌

Video ini bongkar fakta keras tentang {keyword} yang jarang dibahas kreator lain di luar sana. 

Simpan video ini biar gak lupa dan share ke temen yang butuh info ini! 🔥"""

    if not comment_bait:
        comment_bait = f"Menurut kalian, mana yang paling relate sama pengalaman kalian selama ini? Tulis di kolom komentar ya! 👇💬"

    if not hashtags:
        raw_tags = [niche, keyword, "fyp", "tipsbermanfaat", "viralindonesia", "edukasitiktok"]
        clean_tags = []
        for t in raw_tags:
            w = "".join(c for c in t if c.isalnum())
            if w:
                clean_tags.append(f"#{w.lower()}")
        hashtags = clean_tags[:8]

    if not prime_time:
        prime_time = "12.00 - 13.00 WIB (Istirahat Siang) & 19.30 - 21.00 WIB (Prime Time Malam)"

    tags_str = " ".join(hashtags) if isinstance(hashtags, list) else str(hashtags)

    if not pub_md:
        pub_md = f"""### 1. 📝 Variasi Caption Siap Copas
#### Variasi A (Storytelling & Emosional):
{cap_a}

#### Variasi B (To-The-Point & Agitatif):
{cap_b}

---
### 2. 💬 Pertanyaan Pemancing Komentar (Comment Bait)
{comment_bait}

---
### 3. 🏷️ Rekomendasi Hashtag
{tags_str}

---
### 4. ⏰ Rekomendasi Jam Tayang Terbaik
{prime_time}
"""

    return {
        "caption_storytelling": cap_a,
        "caption_punchy": cap_b,
        "comment_bait_question": comment_bait,
        "hashtags": hashtags,
        "hashtags_str": tags_str,
        "prime_time_recommendation": prime_time,
        "publication_kit_md": pub_md
    }


def load_vault() -> List[Dict[str, Any]]:
    """
    Membaca seluruh proyek konten dari penyimpanan lokal.
    Otomatis memperbaiki ID duplikat dan mengisi bagian draf yang kosong (self-healing & enrichment).
    """
    _ensure_vault_exists()
    try:
        with open(VAULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                seen_ids = set()
                repaired = False
                for idx, item in enumerate(data):
                    cur_id = item.get("id")
                    if not cur_id or cur_id in seen_ids:
                        new_id = f"vg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
                        item["id"] = new_id
                        repaired = True
                    seen_ids.add(item["id"])

                    # Auto-Enrichment jika ada field copywriting/closing yang kosong
                    if not item.get("caption_storytelling") or not item.get("closing_bridge_script") or not item.get("publication_kit_md"):
                        kit = extract_copywriting_kit(item)
                        bridge = extract_closing_bridge(item)
                        if not item.get("caption_storytelling"):
                            item["caption_storytelling"] = kit["caption_storytelling"]
                            item["caption_punchy"] = kit["caption_punchy"]
                            item["comment_bait_question"] = kit["comment_bait_question"]
                            item["prime_time_recommendation"] = kit["prime_time_recommendation"]
                            item["publication_kit_md"] = kit["publication_kit_md"]
                            if not item.get("hashtags"):
                                item["hashtags"] = kit["hashtags"]
                            repaired = True
                        if not item.get("closing_bridge_script"):
                            item["closing_bridge_script"] = bridge
                            repaired = True
                        if not item.get("publication_kit_md"):
                            item["publication_kit_md"] = kit["publication_kit_md"]
                            repaired = True

                if repaired:
                    save_vault(data)
                return data
            return []
    except Exception:
        return []

def save_vault(items: List[Dict[str, Any]]) -> bool:
    """Menyimpan seluruh daftar proyek konten ke penyimpanan lokal."""
    _ensure_vault_exists()
    try:
        with open(VAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def create_draft(initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Membuat draf konten baru dengan ID unik (dilengkapi UUID) dan struktur data Unified Content Project (UCP).
    """
    now = datetime.now()
    unique_id = f"vg_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    new_draft = {
        "id": unique_id,
        "title": f"Konten {now.strftime('%d/%m/%Y %H:%M')}",
        "created_at": timestamp_str,
        "updated_at": timestamp_str,
        "status": "💡 Ide & Riset",
        
        # Tahap 1: Riset & Celah Pasar
        "niche": "Bisnis Online & Side Hustle",
        "keyword": "",
        "platform": "TikTok",
        "target_audience": "",
        "content_angle": "",
        "research_notes": "",
        
        # Tahap 2: Inspirasi Kompetitor
        "source_url": "",
        "competitor_analysis": "",
        
        # Tahap 3: Hook & Storyboard (dengan DNA Persona & Konsistensi AI)
        "hook_verbal": "",
        "hook_visual": "",
        "hook_screen_text": "",
        "content_theme": "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)",
        "audience_slang": "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)",
        "emotional_trigger": "👀 Rasa Penasaran Ekstrem (Curiosity Gap) & Validasi Solusi",
        "visual_style": "🎥 Realistis Sinematik / Live Action (Talent Manusia / UGC 4K)",
        "environment": "Studio Kerja Minimalis Modern",
        "color_grading": "Moody Teal & Warm Orange Sinematik",
        "voice_style": "Santai & Empatik (Bestie Vibe)",
        "storyboard_table_md": "",
        "storyboard_srt": "",
        "dialogue_word_count": 0,
        "est_duration_sec": 60,
        
        # Tahap 4: Monetisasi & CTA
        "monetization_type": "Produk Digital (Ebook/Template)",
        "product_name": "",
        "closing_bridge_script": "",
        
        # Tahap 5: Kit Publikasi & Jadwal
        "caption_storytelling": "",
        "caption_punchy": "",
        "comment_bait_question": "",
        "hashtags": [],
        "prime_time_recommendation": "",
        "publication_kit_md": "",
        "scheduled_day": ""
    }

    if initial_data:
        new_draft.update(initial_data)

    vault = load_vault()
    # Letakkan draf terbaru di urutan pertama
    vault.insert(0, new_draft)
    save_vault(vault)
    return new_draft

def get_draft(draft_id: str) -> Optional[Dict[str, Any]]:
    """Mengambil satu draf konten berdasarkan ID unik."""
    vault = load_vault()
    for item in vault:
        if item.get("id") == draft_id:
            return item
    return None

def update_draft(draft_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Memperbarui data draf konten yang sudah ada."""
    vault = load_vault()
    for idx, item in enumerate(vault):
        if item.get("id") == draft_id:
            updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item.update(updates)
            vault[idx] = item
            save_vault(vault)
            return item
    return None

def delete_draft(draft_id: str) -> bool:
    """Menghapus draf konten dari penyimpanan."""
    vault = load_vault()
    filtered = [item for item in vault if item.get("id") != draft_id]
    if len(filtered) != len(vault):
        save_vault(filtered)
        return True
    return False

def change_draft_status(draft_id: str, new_status: str) -> bool:
    """Mengubah status tahapan produksi suatu draf."""
    if new_status not in STATUS_OPTIONS:
        return False
    vault = load_vault()
    for idx, item in enumerate(vault):
        if item.get("id") == draft_id:
            item["status"] = new_status
            item["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vault[idx] = item
            save_vault(vault)
            return True
    return False

def generate_draft_bundle_zip(draft: Dict[str, Any]) -> bytes:
    """
    Memaketkan seluruh aset konten ke dalam satu berkas .ZIP siap produksi:
    1. 1_Skrip_Storyboard_Produksi.md
    2. 2_Tabel_Produksi.csv
    3. 3_Subtitles_CapCut.srt
    4. 4_Copywriting_Caption_dan_Hashtag.txt
    Semua berkas dijamin lengkap dan tidak ada bagian yang kosong.
    """
    zip_buffer = io.BytesIO()
    
    closing_bridge = extract_closing_bridge(draft)
    copy_kit = extract_copywriting_kit(draft)

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        title_clean = "".join(c for c in draft.get("title", "konten") if c.isalnum() or c in (' ', '_', '-')).strip()
        
        # 1. Markdown Skrip & Catatan
        md_content = f"""# {draft.get('title', 'Draf Konten')}
ID Proyek: {draft.get('id', '-')}
Dibuat: {draft.get('created_at', '-')}
Niche: {draft.get('niche', '-')} | Platform: {draft.get('platform', '-')}
Status: {draft.get('status', '-')}

---

## 🪝 HOOK UTAMA (3 DETIK PERTAMA)
- **Audio/Verbal**: "{draft.get('hook_verbal', '-')}"
- **Visual/B-Roll**: {draft.get('hook_visual') or 'Tatapan fokus ke lensa kamera, ekspresi serius / penasaran'}

---

## 🎬 PAPAN CERITA & TABEL PRODUKSI
{draft.get('storyboard_table_md', 'Belum ada tabel storyboard.')}

---

## 💰 JEMBATAN KONVERSI (CLOSING BRIDGE)
- **Tipe Penawaran**: {draft.get('monetization_type', '-')}
- **Nama Produk**: {draft.get('product_name', '-')}
- **Skrip Penutup**:
{closing_bridge}

---

## ✨ KIT PUBLIKASI MEDIA SOSIAL
{copy_kit['publication_kit_md']}
"""
        zf.writestr(f"1_Skrip_Storyboard_{title_clean}.md", md_content.encode("utf-8"))

        # 2. Tabel CSV (Mendukung tabel pipa dan format outline)
        table_md = draft.get("storyboard_table_md", "")
        from utils.export_helpers import markdown_table_to_dataframe, dataframe_to_csv_bytes
        df = markdown_table_to_dataframe(table_md) if table_md else None
        if df is None:
            import pandas as pd
            df = pd.DataFrame([
                ["00-03", "Tatapan tajam fokus ke kamera", draft.get("hook_verbal") or "Hook Pembuka Video", "Footage penahan scroll / SFX Glitch", "Pattern Interrupt & Dopamin Spike"],
                ["03-30", "B-Roll cepat sesuai konteks masalah", f"Pembahasan masalah & fakta penting seputar {draft.get('keyword', 'topik ini')}", "Overlay screen recording / SFX Whoosh", "Agitasi & Edukasi Mendalam"],
                ["30-60", "Close-up ke kamera, tunjuk ke link bio", closing_bridge, "Tunjuk link bio / SFX Click", "Call to Action (Closing Bridge)"]
            ], columns=["Detik", "Visual / B-Roll Camera Direction", "Skrip Audio (Word for Word)", "Aset B-Roll & SFX", "Pemicu Psikologis"])
        
        csv_bytes = dataframe_to_csv_bytes(df)
        zf.writestr(f"2_Tabel_Produksi_{title_clean}.csv", csv_bytes)

        # 3. Subtitles SRT (CapCut)
        srt_content = draft.get("storyboard_srt", "")
        if not srt_content and table_md:
            from utils.export_helpers import markdown_table_to_srt
            srt_bytes = markdown_table_to_srt(table_md)
            if srt_bytes:
                srt_content = srt_bytes.decode("utf-8")
        
        if not srt_content:
            hook = draft.get("hook_verbal") or "Hook pembuka video viral"
            srt_content = f"1\n00:00:00,000 --> 00:00:03,500\n{hook}\n\n2\n00:00:03,500 --> 00:00:30,000\nSimak informasi penting dan fakta seputar {draft.get('keyword', 'topik ini')} sampai tuntas.\n\n3\n00:00:30,000 --> 00:00:58,000\n{closing_bridge}\n"

        zf.writestr(f"3_Subtitles_CapCut_{title_clean}.srt", srt_content.encode("utf-8"))

        # 4. Copywriting Caption & Hashtag (Lengkap 100%)
        copy_text = f"""==================================================
KIT COPYWRITING & PUBLIKASI SIAP POSTING
Video: {draft.get('title', '')}
Niche: {draft.get('niche', '')} | Platform: {draft.get('platform', '')}
==================================================

[CAPTION PILIHAN A - STORYTELLING & EMOSIONAL (HIGH CTR)]:
{copy_kit['caption_storytelling']}

--------------------------------------------------

[CAPTION PILIHAN B - TO-THE-POINT & AGITATIF]:
{copy_kit['caption_punchy']}

--------------------------------------------------

[PERTANYAAN PANCINGAN KOMENTAR (COMMENT BAIT)]:
{copy_kit['comment_bait_question']}

--------------------------------------------------

[10 HASHTAG REKOMENDASI TERKURASI]:
{copy_kit['hashtags_str']}

--------------------------------------------------

[REKOMENDASI JAM UPLOAD TERBAIK (PRIME TIME WIB)]:
{copy_kit['prime_time_recommendation']}

==================================================
Tips: Salin langsung teks caption di atas saat upload di TikTok / IG Reels.
Teks sudah dioptimasi untuk mendongkrak Retensi, Komentar, dan Algoritma FYP.
"""
        zf.writestr(f"4_Copywriting_Posting_{title_clean}.txt", copy_text.encode("utf-8"))

        # 5. Skrip Dialog Bersih untuk Teleprompter / Rekaman HP
        teleprompter_speech = extract_clean_speech_dialogue(draft)
        zf.writestr(f"5_Dialog_Teleprompter_{title_clean}.txt", teleprompter_speech.encode("utf-8"))

        # 6. Lembar Kerja Produksi Per Scene (Siap Copas Tim Editor & Videografer)
        from utils.export_helpers import parse_storyboard_scenes, format_scenes_for_production_sheet, parse_master_consistency_anchor
        sb_text = draft.get("storyboard_table_md", "")
        scenes_data = parse_storyboard_scenes(sb_text)
        master_anchor = parse_master_consistency_anchor(sb_text)
        sheet_text = format_scenes_for_production_sheet(
            scenes_data, 
            title=draft.get("title", "Video Konten"), 
            platform=draft.get("platform", "TikTok / Reels"),
            master_anchor=master_anchor
        )
        if sheet_text:
            zf.writestr(f"2b_Storyboard_Per_Scene_{title_clean}.txt", sheet_text.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def generate_all_vault_bundle_zip(vault_items: List[Dict[str, Any]]) -> bytes:
    """
    Memaketkan SELURUH video di dalam brankas ke dalam satu berkas Master .ZIP
    dengan struktur folder rapi per video untuk dibagikan ke tim editor atau disimpan di HP.
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        summary_lines = ["# 📅 JADWAL PRODUKSI MASTER KONTEN - VIRALGENIX\n"]
        for idx, d in enumerate(vault_items):
            c_kit = extract_copywriting_kit(d)
            summary_lines.append(f"### {idx+1}. {d.get('title', 'Konten')}")
            summary_lines.append(f"- **Status**: {d.get('status', '-')}")
            summary_lines.append(f"- **Niche**: {d.get('niche', '-')} | Platform: {d.get('platform', '-')}")
            summary_lines.append(f"- **Hook**: \"{d.get('hook_verbal', '-')}\"")
            summary_lines.append(f"- **Produk / CTA**: {d.get('product_name', '-')}")
            summary_lines.append(f"- **Jam Upload**: {c_kit['prime_time_recommendation']}")
            summary_lines.append(f"- **Hashtag Utama**: {c_kit['hashtags_str']}")
            summary_lines.append("")
        
        zf.writestr("0_REKAP_JADWAL_PRODUKSI.md", "\n".join(summary_lines).encode("utf-8"))

        for idx, draft in enumerate(vault_items):
            title_clean = "".join(c for c in draft.get("title", f"video_{idx+1}") if c.isalnum() or c in (' ', '_', '-')).strip()
            folder_prefix = f"Video_{idx+1}_{title_clean[:25].replace(' ', '_')}"

            closing_bridge = extract_closing_bridge(draft)
            copy_kit = extract_copywriting_kit(draft)

            # 1. Naskah Storyboard
            md_content = f"""# {draft.get('title', 'Draf Konten')}
ID Proyek: {draft.get('id', '-')}
Niche: {draft.get('niche', '-')} | Platform: {draft.get('platform', '-')}
Status: {draft.get('status', '-')}

## 🪝 HOOK UTAMA (3 DETIK)
- **Audio/Verbal**: "{draft.get('hook_verbal', '-')}"
- **Visual**: {draft.get('hook_visual') or 'Tatapan tajam ke arah lensa kamera'}
- **Teks di Layar**: {draft.get('hook_screen_text') or 'PERHATIKAN INI! ⚠️'}

## 🎬 STORYBOARD & TABEL PRODUKSI
{draft.get('storyboard_table_md', '-')}

## 💰 JEMBATAN MONETISASI & CTA
{closing_bridge}

## ✨ KIT PUBLIKASI MEDIA SOSIAL
{copy_kit['publication_kit_md']}
"""
            zf.writestr(f"{folder_prefix}/1_Naskah_Storyboard.md", md_content.encode("utf-8"))

            # 2. Tabel CSV (Mendukung format pipa dan outline)
            table_md = draft.get("storyboard_table_md", "")
            from utils.export_helpers import markdown_table_to_dataframe, dataframe_to_csv_bytes
            df = markdown_table_to_dataframe(table_md) if table_md else None
            if df is None:
                import pandas as pd
                df = pd.DataFrame([
                    ["00-03", "Tatapan tajam fokus ke kamera", draft.get("hook_verbal") or "Hook Pembuka Video", draft.get("hook_screen_text") or "PERHATIKAN INI! ⚠️", "Pattern Interrupt & Dopamin Spike"],
                    ["03-30", "B-Roll cepat sesuai konteks masalah", f"Pembahasan masalah & fakta penting seputar {draft.get('keyword', 'topik ini')}", "FAKTA PENTING 🔥", "Agitasi & Edukasi Mendalam"],
                    ["30-60", "Close-up ke kamera, tunjuk ke link bio", closing_bridge, "KLIK LINK DI BIO 🔗", "Call to Action (Closing Bridge)"]
                ], columns=["Detik", "Visual / B-Roll Camera Direction", "Skrip Audio (Word for Word)", "Teks di Layar (On-Screen Text)", "Pemicu Psikologis"])
            
            csv_bytes = dataframe_to_csv_bytes(df)
            zf.writestr(f"{folder_prefix}/2_Tabel_Produksi.csv", csv_bytes)

            # 3. Subtitles SRT (CapCut)
            srt_content = draft.get("storyboard_srt", "")
            if not srt_content and table_md:
                from utils.export_helpers import markdown_table_to_srt
                srt_bytes = markdown_table_to_srt(table_md)
                if srt_bytes:
                    srt_content = srt_bytes.decode("utf-8")
            
            if not srt_content:
                hook = draft.get("hook_verbal") or "Hook pembuka video viral"
                srt_content = f"1\n00:00:00,000 --> 00:00:03,500\n{hook}\n\n2\n00:00:03,500 --> 00:00:30,000\nSimak informasi penting dan fakta seputar {draft.get('keyword', 'topik ini')} sampai tuntas.\n\n3\n00:00:30,000 --> 00:00:58,000\n{closing_bridge}\n"

            zf.writestr(f"{folder_prefix}/3_Subtitles_CapCut.srt", srt_content.encode("utf-8"))

            # 4. Caption dan Hashtag Lengkap
            copy_text = f"""==================================================
KIT COPYWRITING & PUBLIKASI SIAP POSTING
Video: {draft.get('title', '')}
Niche: {draft.get('niche', '')} | Platform: {draft.get('platform', '')}
==================================================

[CAPTION PILIHAN A - STORYTELLING]:
{copy_kit['caption_storytelling']}

--------------------------------------------------

[CAPTION PILIHAN B - PUNCHY/AGITATIF]:
{copy_kit['caption_punchy']}

--------------------------------------------------

[PERTANYAAN PANCINGAN KOMENTAR]:
{copy_kit['comment_bait_question']}

--------------------------------------------------

[HASHTAG REKOMENDASI]:
{copy_kit['hashtags_str']}

--------------------------------------------------

[JAM UPLOAD TERBAIK]:
{copy_kit['prime_time_recommendation']}
"""
            zf.writestr(f"{folder_prefix}/4_Caption_dan_Hashtag.txt", copy_text.encode("utf-8"))

            # 5. Skrip Dialog Bersih untuk Teleprompter / Rekaman HP
            teleprompter_speech = extract_clean_speech_dialogue(draft)
            zf.writestr(f"{folder_prefix}/5_Dialog_Teleprompter.txt", teleprompter_speech.encode("utf-8"))

            # 6. Lembar Kerja Produksi Per Scene (Siap Copas Tim Editor)
            from utils.export_helpers import parse_storyboard_scenes, format_scenes_for_production_sheet
            scenes_data = parse_storyboard_scenes(draft.get("storyboard_table_md", ""))
            sheet_text = format_scenes_for_production_sheet(scenes_data, title=draft.get("title", f"Video {idx+1}"), platform=draft.get("platform", "TikTok / Reels"))
            if sheet_text:
                zf.writestr(f"{folder_prefix}/2b_Storyboard_Per_Scene.txt", sheet_text.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()

