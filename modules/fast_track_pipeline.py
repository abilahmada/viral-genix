"""
ViralGenix - Fast-Track Pipeline (Jalur Cepat Konten Berkelanjutan)
Alur kerja terpadu 5-Langkah yang mengalirkan data riset secara otomatis dari:
[1. Riset Tren] ➔ [2. 10 Hook] ➔ [3. Storyboard 60s] ➔ [4. Monetisasi] ➔ [5. Kit Siap Posting]
Serta Mode Sprint 7 Hari untuk memproduksi kalender konten 1 minggu penuh dalam 1x klik.
"""

import streamlit as st
import re
from utils.prompts import (
    MASTER_STRATEGIST_SYSTEM_PROMPT,
    TREND_RADAR_PROMPT,
    HOOK_GENERATOR_PROMPT,
    STORYBOARD_TABLE_PROMPT,
    MONETIZATION_BRIDGE_PROMPT,
    CAPTION_HASHTAG_PROMPT,
    SEVEN_DAY_SPRINT_PROMPT,
    get_master_system_prompt,
    get_persona_directive,
    CREATOR_PERSONAS
)
from utils.niche_data import COMPREHENSIVE_NICHES, get_clean_niche
from utils.vault_manager import (
    create_draft,
    update_draft,
    get_draft,
    generate_draft_bundle_zip,
    extract_copywriting_kit,
    extract_closing_bridge
)
from utils.export_helpers import (
    markdown_table_to_dataframe,
    dataframe_to_csv_bytes,
    markdown_table_to_srt,
    prepare_markdown_download,
    parse_storyboard_scenes,
    format_scenes_for_production_sheet,
    parse_content_angles,
    parse_hook_variations
)

def render_fast_track_pipeline(ai_client):
    st.markdown(
        '<div class="module-header">'
        '<div class="module-badge">PIPELINE OTOMATIS: JALUR CEPAT</div>'
        '<h1 class="module-title">⚡ Fast-Track Continuous Content Engine</h1>'
        '<p class="module-desc">'
        'Alur kerja tanpa putus dari <b>Riset Tren ➔ Hook ➔ Storyboard ➔ Jembatan Penjualan ➔ Kit Posting Siap Upload</b>. '
        'Setiap data yang Anda racik otomatis dialirkan ke tahap berikutnya dan disimpan ke brankas produksi.'
        '</p></div>',
        unsafe_allow_html=True
    )

    # Indikator Persona Gaya Bicara Aktif
    active_p_key = st.session_state.get("creator_persona", "santai")
    persona_data = CREATOR_PERSONAS.get(active_p_key, CREATOR_PERSONAS["santai"])
    st.markdown(
        f'<div style="display:flex; align-items:center; justify-content:space-between; background:#ffffff; border:1.5px solid #e2e8f0; border-radius:10px; padding:10px 16px; margin-bottom:18px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">'
        f'<div><span style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">🎭 Persona Suara Aktif:</span>'
        f'<div style="font-size:0.95rem; font-weight:700; color:#4f46e5;">{persona_data["label"]}</div></div>'
        f'<div style="font-size:0.82rem; color:#475569; max-width:55%; text-align:right;">'
        f'<i>"{persona_data["tone"]}"</i>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    tab_single, tab_batch = st.tabs([
        "⚡ Panduan 1 Video (Langkah demi Langkah)",
        "🚀 Sprint Konten 7 Hari (Batch 1 Minggu Sekaligus)"
    ])

    # =========================================================================
    # TAB 1: PANDUAN ALUR 1 VIDEO (STEP-BY-STEP WIZARD)
    # =========================================================================
    with tab_single:
        # Inisialisasi State Pipeline
        if "pipeline_step" not in st.session_state:
            st.session_state["pipeline_step"] = 1

        if "current_pipeline_draft_id" not in st.session_state:
            st.session_state["current_pipeline_draft_id"] = None

        # Anti-Stuck: Jika tidak sedang mengedit draf tertentu dan posisi step sebelumnya berada di 5,
        # otomatis reset ke Tahap 1 agar pengguna tidak langsung terlempar ke halaman akhir
        if st.session_state.get("pipeline_step") == 5 and not st.session_state.get("current_pipeline_draft_id"):
            st.session_state["pipeline_step"] = 1

        current_step = st.session_state["pipeline_step"]

        # STEPPER HEADER (Indikator & Navigasi Tahap yang Dapat Diklik + Tombol Reset Cepat)
        col_stepper, col_new_top = st.columns([4.2, 1.2])
        with col_new_top:
            if st.button("➕ Draf Baru", key="btn_quick_reset_top", use_container_width=True, help="Bersihkan form untuk membuat konten baru dari Tahap 1"):
                st.session_state["current_pipeline_draft_id"] = None
                st.session_state["pipeline_step"] = 1
                for k in ["pipe_step1_result", "pipe_step2_result", "pipe_step3_result", "pipe_step4_result", "pipe_step5_result"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        with col_stepper:
            step_cols = st.columns(5)
            steps_info = [
                ("1. Riset Celah", 1),
                ("2. Hook 3 Detik", 2),
                ("3. Storyboard 60s", 3),
                ("4. Monetisasi", 4),
                ("5. Siap Posting", 5)
            ]

            for col, (label, s_num) in zip(step_cols, steps_info):
                with col:
                    btn_type = "primary" if s_num == current_step else "secondary"
                    step_icon = "📌 " if s_num == current_step else ("✓ " if s_num < current_step else "")
                    if st.button(f"{step_icon}{label}", key=f"btn_step_nav_{s_num}", type=btn_type, use_container_width=True):
                        st.session_state["pipeline_step"] = s_num
                        st.rerun()

        # Banner informasi draf yang sedang diedit
        active_id = st.session_state.get("current_pipeline_draft_id")
        if active_id:
            active_d = get_draft(active_id)
            d_title = active_d.get("title", active_id) if active_d else active_id
            st.markdown(
                f'<div style="background: #eef2ff; border-left: 4px solid #4f46e5; border-radius: 8px; padding: 8px 14px; margin-top: 6px; font-size: 0.88rem; color: #1e1b4b;">'
                f'✏️ <b>Sedang Mengedit Draf:</b> <span style="font-weight: 700; color: #4f46e5;">{d_title}</span> <span style="color:#64748b; font-size: 0.78rem;">(ID: {active_id})</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TAHAP 1: RISET & CELAH PASAR
        # ---------------------------------------------------------------------
        if current_step == 1:
            if not active_id:
                col_hint1, col_hint2 = st.columns([1.6, 1])
                with col_hint1:
                    st.markdown(
                        '<div style="background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%); border: 1.5px solid #c7d2fe; border-radius: 12px; padding: 10px 16px; margin-bottom: 12px;">'
                        '<span style="color: #4f46e5; font-weight: 700; font-size: 0.82rem;">🎯 STRATEGI PERTUMBUHAN AKUN:</span>'
                        '<div style="color: #1e1b4b; font-size: 0.85rem; margin-top: 2px;">'
                        'Ingin hasil maksimal? Pastikan akun Anda sudah memiliki <b>Bio 3 Detik</b> dan <b>4 Pilar Konten</b> yang terstruktur.'
                        '</div></div>',
                        unsafe_allow_html=True
                    )
                with col_hint2:
                    if st.button("🎯 Buat Blueprint Akun A-Z Dulu ➔", use_container_width=True, help="Bedah akun, buat bio 3 detik, dan susun 4 pilar konten di modul Growth A-Z"):
                        st.session_state["_target_nav"] = "🎯 Bedah & Blueprint Akun (Growth A-Z)"
                        st.session_state["active_nav"] = "🎯 Bedah & Blueprint Akun (Growth A-Z)"
                        st.rerun()

            st.markdown("### 📡 Tahap 1: Temukan Sudut Pandang Konten Unik")
            st.caption("Pilih niche dan topik yang ingin diangkat. AI akan mencari celah pasar yang belum dijawab tuntas oleh kompetitor.")

            st.markdown(
                '<div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">'
                '💡 <b>Panduan Pemula:</b> Tidak perlu bingung mencari ide dari nol. Cukup pilih niche dan klik salah satu preset topik di bawah, atau ketik topik apa saja yang ingin Anda bahas. AI akan menganalisis sudut pandang yang paling dicari audiens tapi jarang dibahas oleh kreator lain!'
                '</div>',
                unsafe_allow_html=True
            )

            col1, col2 = st.columns([1.2, 1], gap="medium")
            with col1:
                saved_niche = st.session_state.get("pipe_niche", "")
                niche_idx = COMPREHENSIVE_NICHES.index(saved_niche) if saved_niche in COMPREHENSIVE_NICHES else 0
                niche = st.selectbox(
                    "Kategori Niche Konten:",
                    COMPREHENSIVE_NICHES,
                    index=niche_idx,
                    key="pipe_niche_select"
                )
                custom_niche_input = ""
                if "Custom Niche" in niche:
                    custom_niche_input = st.text_input(
                        "Ketik Niche Spesifik Anda:",
                        value=st.session_state.get("pipe_custom_niche", ""),
                        placeholder="Contoh: Katering Bento Anak / Tanaman Hias Bonsai",
                        key="pipe_custom_niche"
                    )

                def _set_pipe_keyword(val):
                    st.session_state["pipe_keyword_input"] = val

                st.caption("🔥 Preset Cepat Topik (Klik untuk Memilih):")
                cp1, cp2, cp3 = st.columns(3)
                with cp1:
                    st.button("🤖 AI Modal HP", key="p_preset1", on_click=_set_pipe_keyword, args=("Cara hasilkan uang tambahan dari AI modal HP untuk pemula",), use_container_width=True)
                with cp2:
                    st.button("💳 Trik Bebas Utang", key="p_preset2", on_click=_set_pipe_keyword, args=("Trik psikologis melunasi utang pinjol dan kartu kredit dengan cepat",), use_container_width=True)
                with cp3:
                    st.button("🥗 Diet Tanpa Lapar", key="p_preset3", on_click=_set_pipe_keyword, args=("Defisit kalori santai tanpa lapar dan tanpa pantang nasi",), use_container_width=True)

                keyword = st.text_input(
                    "Kata Kunci / Topik yang Ingin Dibahas:",
                    value=st.session_state.get("pipe_keyword_input", ""),
                    placeholder="Contoh: Cara pakai AI untuk pemula / Rekomendasi sunscreen kulit berminyak / Resep bekal hemat...",
                    key="pipe_keyword_input"
                )

            with col2:
                platform = st.radio("Platform Utama:", ["TikTok", "Instagram Reels", "YouTube Shorts", "TikTok / Reels"], horizontal=True, key="pipe_platform")
                target_aud = st.text_input(
                    "Target Audiens:",
                    value=st.session_state.get("pipe_audience", ""),
                    placeholder="Contoh: Pekerja kantoran 20-35 tahun / Ibu rumah tangga pemula...",
                    key="pipe_audience"
                )
                COMMUNICATION_STYLES = [
                    "🔬 Otoritatif & Berbasis Riset (The Scientific Practitioner — Data Metrik & Kausalitas)",
                    "🥊 Kritis & Kontra-Arus (The Unfiltered Challenger — Hantam Salah Kaprah Lapangan)",
                    "🎭 Satir, Parodi & Humor Relatable (The Satirical Realist — Komedi Situasional & Ironi)",
                    "🎬 Dramatik & High-Stakes (The Storyteller — Alur Krisis Emosional & Plot Twist)",
                    "🤝 Empatik & Kawan Senasib (The Relatable Ally — Hangat, Solutif Tanpa Menggurui)",
                    "⚡ Taktis & Efisiensi Ekstrem (The Actionable Hacker — Playbook Cepat & Hemat Waktu)"
                ]

                saved_comm_style = st.session_state.get("pipe_comm_style") or st.session_state.get("pipe_angle_type", "")
                comm_idx = 0
                for c_i, c_opt in enumerate(COMMUNICATION_STYLES):
                    if saved_comm_style and (c_opt.split()[1].lower() in saved_comm_style.lower() or saved_comm_style.lower() in c_opt.lower()):
                        comm_idx = c_i
                        break

                angle_type = st.selectbox(
                    "Gaya Komunikasi & Lensa Strategis:",
                    options=COMMUNICATION_STYLES,
                    index=comm_idx,
                    key="pipe_comm_style_select",
                    help="Pilih kacamata strategis: AI akan membedah celah kelemahan kompetitor dan merumuskan 5 sudut pandang unik menggunakan lensa persona ini."
                )

                comm_notes = {
                    "Otoritatif": "🔬 <b>Kredibilitas Sains & Data:</b> AI membongkar celah dangkal kompetitor dengan metrik angka %, data riset, dan kausalitas logis ('The Mechanism').",
                    "Kritis": "🥊 <b>Bongkar Salah Kaprah:</b> AI merumuskan sudut pandang yang berani mendebat mitos populer industri dan membungkam keraguan secara lugas.",
                    "Satir": "🎭 <b>Humor & Parodi Situasional:</b> AI merancang skenario yang menertawakan kesalahan umum audiens secara relatable (cocok untuk Skit Komedi).",
                    "Dramatik": "🎬 <b>Ketegangan & Alur Emosional:</b> AI menyusun premis yang menyoroti risiko fatal bila masalah diabaikan, berujung plot twist pencerahan.",
                    "Empatik": "🤝 <b>Kawan Seperjuangan:</b> AI merangkul keresahan terdalam dan rasa insecure audiens dengan hangat tanpa menggurui.",
                    "Taktis": "⚡ <b>Actionable Cheat-Sheet:</b> AI memangkas teori bertele-tele, menyusun langkah konkret yang langsung menghemat waktu audiens."
                }
                active_comm_note = "🔬 Lensa strategis analisis celah pasar"
                for cn_k, cn_v in comm_notes.items():
                    if cn_k.lower() in angle_type.lower():
                        active_comm_note = cn_v
                        break
                st.markdown(f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px 10px; font-size:0.78rem; color:#334155; margin-bottom:12px; line-height:1.4;'>{active_comm_note}</div>", unsafe_allow_html=True)

            btn_run_step1 = st.button("🔍 Pindai Tren & Rumuskan 5 Sudut Pandang Unik", type="primary", use_container_width=True)

            if btn_run_step1:
                final_niche = get_clean_niche(niche, custom_niche_input)
                if not final_niche:
                    st.warning("⚠️ Mohon pilih Kategori Niche Anda terlebih dahulu sebelum memindai tren.")
                elif not keyword.strip():
                    st.warning("⚠️ Mohon isi Kata Kunci / Topik yang ingin dibahas.")
                elif not target_aud.strip():
                    st.warning("⚠️ Mohon isi Target Audiens agar analisis AI akurat dan tepat sasaran.")
                else:
                    with st.spinner("🤖 AI sedang memindai pola percakapan audiens dan menyusun 5 sudut pandang unik..."):
                        prompt = TREND_RADAR_PROMPT.format(
                            niche=final_niche,
                            keyword=keyword,
                            platform=platform,
                            communication_style=angle_type
                        )
                        res1 = ai_client.generate(
                            prompt=prompt,
                            system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                        )
                        st.session_state["pipe_step1_result"] = res1
                        st.session_state["pipe_keyword"] = keyword
                        st.session_state["pipe_niche"] = niche
                        st.session_state["pipe_comm_style"] = angle_type
                        st.session_state["pipe_angle_type"] = angle_type

            if "pipe_step1_result" in st.session_state:
                with st.container(border=True):
                    st.markdown(st.session_state["pipe_step1_result"])

                kw_hint = st.session_state.get("pipe_keyword", keyword) or "topik ini"
                detected_angles = parse_content_angles(st.session_state["pipe_step1_result"], fallback_topic=kw_hint)

                st.markdown("#### 🎯 Pilih 1 dari 5 Sudut Pandang Konten yang Dihasilkan:")
                st.caption("Klik salah satu angle di bawah untuk otomatis mengisi konsep cerita, atau pilih '✍️ Kustom' untuk menulis konsep sendiri.")

                angle_labels = [a["display_label"] for a in detected_angles]
                angle_labels.append("✍️ Kustom (Ketik Konsep Cerita Sendiri)")

                selected_angle_label = st.radio(
                    "Daftar Sudut Pandang Konten (Viral Angles):",
                    options=angle_labels,
                    index=0,
                    key="pipe_angle_radio"
                )

                chosen_angle_obj = next((a for a in detected_angles if a["display_label"] == selected_angle_label), None)

                # Sinkronisasi dinamis ketika radio button berganti
                if "prev_pipe_angle_radio" not in st.session_state or st.session_state["prev_pipe_angle_radio"] != selected_angle_label:
                    st.session_state["prev_pipe_angle_radio"] = selected_angle_label
                    if chosen_angle_obj:
                        st.session_state["pipe_custom_concept_text"] = chosen_angle_obj["full_concept"]
                    elif "Kustom" in selected_angle_label:
                        st.session_state["pipe_custom_concept_text"] = st.session_state.get("pipe_chosen_concept", f"Bongkar rahasia: {kw_hint}")

                if chosen_angle_obj:
                    rec_fmt = chosen_angle_obj.get("recommended_format", "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)")
                    rec_fmt_short = rec_fmt.split()[1] if len(rec_fmt.split()) > 1 else rec_fmt
                    angle_card_html = (
                        f'<div style="background:#f0f9ff; border-left:4px solid #0284c7; padding:10px 14px; border-radius:6px; margin:8px 0 12px 0; font-size:0.86rem; color:#0f172a;">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                        f'<span style="font-weight:700; color:#0369a1;">💡 {chosen_angle_obj["title"]}</span>'
                        f'<span style="background:#e0e7ff; color:#4338ca; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.75rem;">🎭 Model: {rec_fmt_short}</span>'
                        f'</div>'
                        f'<div style="margin-bottom:4px;"><b>📖 Premis & Data Empiris:</b> {chosen_angle_obj["premise"]}</div>'
                        f'<div style="margin-bottom:4px; font-size:0.82rem; color:#3730a3;"><b>🎭 Model Konten Rekomendasi:</b> {rec_fmt}</div>'
                        f'<div style="display:flex; gap:16px; font-size:0.8rem; color:#475569;">'
                        f'<span><b>⚡ Emosi:</b> {chosen_angle_obj["trigger"]}</span>'
                        f'<span><b>🔥 Potensi Viral:</b> {chosen_angle_obj["viral_pot"]}</span>'
                        f'</div></div>'
                    )
                    st.markdown(angle_card_html, unsafe_allow_html=True)

                concept_default = chosen_angle_obj["full_concept"] if chosen_angle_obj else f"Bongkar rahasia: {kw_hint}"
                chosen_concept = st.text_area(
                    "Konsep / Premis Cerita yang Dipilih (Bisa Diedit Bebas):",
                    value=st.session_state.get("pipe_custom_concept_text", concept_default),
                    placeholder="Contoh: Bongkar rahasia cara affiliate tanpa modal...",
                    height=85,
                    key="pipe_custom_concept_text"
                )

                col_next1, _ = st.columns([2, 1])
                with col_next1:
                    if st.button("➡️ Setujui Ide & Lanjut ke Tahap 2: Hook 3 Detik", type="primary", use_container_width=True):
                        if not chosen_concept.strip():
                            st.warning("⚠️ Mohon isi atau tentukan Konsep Cerita sebelum lanjut ke Tahap 2.")
                        else:
                            final_niche = get_clean_niche(niche, custom_niche_input)
                            d_title = chosen_angle_obj["title"] if chosen_angle_obj else chosen_concept[:60]
                            rec_fmt = chosen_angle_obj.get("recommended_format", "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)") if chosen_angle_obj else "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)"

                            if not st.session_state.get("current_pipeline_draft_id"):
                                new_draft = create_draft({
                                    "title": d_title,
                                    "niche": final_niche or niche,
                                    "keyword": st.session_state.get("pipe_keyword", keyword),
                                    "platform": platform,
                                    "target_audience": target_aud,
                                    "communication_style": angle_type,
                                    "content_angle": chosen_concept,
                                    "content_format": rec_fmt,
                                    "research_notes": st.session_state["pipe_step1_result"][:1200]
                                })
                                st.session_state["current_pipeline_draft_id"] = new_draft["id"]
                            else:
                                update_draft(st.session_state["current_pipeline_draft_id"], {
                                    "title": d_title,
                                    "content_angle": chosen_concept,
                                    "content_format": rec_fmt,
                                    "communication_style": angle_type,
                                    "target_audience": target_aud
                                })
                            
                            st.session_state["pipe_chosen_concept"] = chosen_concept
                            st.session_state["pipe_topic_for_hook"] = chosen_concept
                            st.session_state["pipe_hook_topic_input"] = chosen_concept
                            st.session_state["pipe_story_topic"] = chosen_concept
                            st.session_state["pipe_comm_style"] = angle_type
                            st.session_state["pipe_angle_type"] = angle_type
                            st.session_state["pipe_format_val"] = rec_fmt

                            # Sinkronisasi Cerdas ke Tahap 2 (Pre-select Hook Tone sesuai Lensa Komunikasi)
                            if "dramatik" in angle_type.lower():
                                st.session_state["pipe_hook_tone_input"] = "Misterius & Penasaran (Curiosity Gap)"
                            elif "taktis" in angle_type.lower():
                                st.session_state["pipe_hook_tone_input"] = "Mendesak & Takut Rugi (FOMO)"
                            elif any(k in angle_type.lower() for k in ["satir", "empatik"]):
                                st.session_state["pipe_hook_tone_input"] = "Santai & Empatik (Bestie Vibe)"
                            elif any(k in angle_type.lower() for k in ["kritis", "otoritatif"]):
                                st.session_state["pipe_hook_tone_input"] = "Provokatif & Tegas"

                            st.session_state["pipeline_step"] = 2
                            st.rerun()

        # ---------------------------------------------------------------------
        # TAHAP 2: HOOK 3 DETIK (PENAHAN SCROLL)
        # ---------------------------------------------------------------------
        elif current_step == 2:
            st.markdown("### 🪝 Tahap 2: Racik 10 Hook Pembunuh Scroll")
            st.caption("80% keberhasilan video ditentukan dalam 3 detik pertama. Pilih hook terbaik dari 4 pilar psikologi audiens sesuai model konten.")

            st.markdown(
                '<div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">'
                '💡 <b>Panduan Pemula:</b> <i>Hook</i> adalah kalimat pembuka di 3 detik pertama. Penonton di TikTok & Reels memutuskan swipe atau lanjut menonton dalam sekejap. Hook kini secara cerdas menyesuaikan <b>Model Konten</b> Anda (misal: dialog 2 karakter untuk Skit Komedi, voiceover estetik untuk Faceless, adu argumen untuk Debat, atau tatapan intens untuk Talking Head)!'
                '</div>',
                unsafe_allow_html=True
            )

            FORMAT_OPTIONS = [
                "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)",
                "🎭 Skit Komedi / Parodi Situasional (POV 2 Karakter Bertolak Belakang)",
                "🎬 Micro-Drama & Storytelling Emosional (Plot Twist & Narasi Kisah Nyata)",
                "🎞️ Voiceover Faceless Sinematik (Tanpa Wajah — Audio Narasi + B-Roll ASMR)",
                "🥊 Debat Dialektika (Si Skeptis Penasaran vs Si Praktisi Solutif)",
                "📖 Analogi Fabel / Bedah Kasus & Sejarah Unik"
            ]

            active_draft_fmt = None
            if st.session_state.get("current_pipeline_draft_id"):
                active_d = get_draft(st.session_state.get("current_pipeline_draft_id"))
                if active_d:
                    active_draft_fmt = active_d.get("content_format")

            current_fmt_session = st.session_state.get("pipe_format_val") or active_draft_fmt
            if not current_fmt_session and st.session_state.get("pipe_step1_result"):
                parsed_a = parse_content_angles(st.session_state["pipe_step1_result"])
                if parsed_a and parsed_a[0].get("recommended_format"):
                    current_fmt_session = parsed_a[0]["recommended_format"]
            if not current_fmt_session:
                current_fmt_session = FORMAT_OPTIONS[0]
            fmt_idx = 0
            for f_i, f_opt in enumerate(FORMAT_OPTIONS):
                if f_opt.split()[1].lower() in str(current_fmt_session).lower() or str(current_fmt_session).lower() in f_opt.lower():
                    fmt_idx = f_i
                    break

            col1, col2 = st.columns([1.15, 1], gap="medium")
            with col1:
                hook_topic = st.text_area(
                    "Topik Konsep (Otomatis dari Tahap 1):",
                    value=st.session_state.get("pipe_topic_for_hook", ""),
                    placeholder="Contoh: Cara rahasia memulai affiliate TikTok Shop modal HP tanpa nunjukin muka...",
                    height=145,
                    key="pipe_hook_topic_input"
                )
            with col2:
                hook_aud = st.text_input(
                    "Target Audiens:",
                    value=st.session_state.get("pipe_audience", ""),
                    placeholder="Contoh: Pekerja kantoran 20-35 tahun / Ibu rumah tangga pemula...",
                    key="pipe_hook_aud_input"
                )

                hook_format = st.selectbox(
                    "🎭 Model & Format Konten:",
                    FORMAT_OPTIONS,
                    index=fmt_idx,
                    key="pipe_step2_format_widget",
                    help="Model konten menentukan formula aksi kamera visual dan gaya dialog hook 3 detik pertama."
                )

                HOOK_TONE_OPTIONS = [
                    "Misterius & Penasaran (Curiosity Gap)",
                    "Mendesak & Takut Rugi (FOMO)",
                    "Santai & Empatik (Bestie Vibe)",
                    "Provokatif & Tegas"
                ]
                current_tone_val = st.session_state.get("pipe_hook_tone_input", HOOK_TONE_OPTIONS[0])
                tone_idx = HOOK_TONE_OPTIONS.index(current_tone_val) if current_tone_val in HOOK_TONE_OPTIONS else 0

                hook_tone = st.selectbox(
                    "Gaya Bahasa Hook:",
                    HOOK_TONE_OPTIONS,
                    index=tone_idx,
                    key="pipe_hook_tone_input"
                )

            btn_run_step2 = st.button("⚡ Hasilkan 10 Variasi Hook Visual + Audio", type="primary", use_container_width=True)

            if btn_run_step2:
                if not hook_topic.strip():
                    st.warning("⚠️ Mohon isi Topik Konsep terlebih dahulu (atau selesaikan Tahap 1 terlebih dahulu).")
                elif not hook_aud.strip():
                    st.warning("⚠️ Mohon isi Target Audiens terlebih dahulu.")
                else:
                    with st.spinner(f"🧠 AI sedang merumuskan 10 variasi hook dengan formula visual, teks layar, dan audio sesuai model {hook_format.split()[1]}..."):
                        prompt = HOOK_GENERATOR_PROMPT.format(
                            topic=hook_topic,
                            audience=hook_aud,
                            tone=hook_tone,
                            content_format=hook_format
                        )
                        res2 = ai_client.generate(
                            prompt=prompt,
                            system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                        )
                        st.session_state["pipe_step2_result"] = res2

            if "pipe_step2_result" in st.session_state:
                with st.container(border=True):
                    st.markdown(st.session_state["pipe_step2_result"])

                parsed_hooks = parse_hook_variations(st.session_state["pipe_step2_result"], fallback_topic=hook_topic)

                st.markdown("#### 🎯 Pilih 1 Hook Pembuka Favorit (3 Detik Pertama):")
                st.caption("AI telah merumuskan 10 variasi hook dalam 4 pilar psikologi audiens. Pilih salah satu kalimat di bawah untuk dijadikan naskah pembuka:")

                hook_options = [h["display_label"] for h in parsed_hooks]
                hook_options.append("✍️ Kustom (Tulis Kalimat Hook Sendiri)")

                selected_hook_label = st.radio(
                    "Daftar 10 Variasi Hook Terdeteksi:",
                    options=hook_options,
                    index=0,
                    key="pipe_hook_radio"
                )

                chosen_hook_obj = next((h for h in parsed_hooks if h["display_label"] == selected_hook_label), None)

                # Sinkronisasi dinamis ketika radio button berganti
                if "prev_pipe_hook_radio" not in st.session_state or st.session_state["prev_pipe_hook_radio"] != selected_hook_label:
                    st.session_state["prev_pipe_hook_radio"] = selected_hook_label
                    if chosen_hook_obj:
                        st.session_state["pipe_custom_hook_text"] = chosen_hook_obj["verbal"]
                    elif "Kustom" in selected_hook_label:
                        st.session_state["pipe_custom_hook_text"] = st.session_state.get("pipe_chosen_hook", "Stop scroll kalau kamu gak mau rugi waktu dan duit sia-sia!")

                if chosen_hook_obj:
                    fact_pill = f"<div style='margin-top:4px; font-size:0.78rem; color:#4338ca;'><b>📊 Pijakan Fakta:</b> {chosen_hook_obj.get('fact_anchor', '')}</div>" if chosen_hook_obj.get('fact_anchor') else ""
                    hook_card_html = (
                        f'<div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:10px 14px; border-radius:6px; margin:8px 0 12px 0; font-size:0.86rem; color:#1e1b4b;">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                        f'<span style="font-weight:700; color:#1d4ed8;">🏷️ {chosen_hook_obj["category"]}</span>'
                        f'<div style="display:flex; gap:6px; align-items:center;">'
                        f'<span style="background:#e0e7ff; color:#3730a3; font-weight:600; padding:2px 8px; border-radius:4px; font-size:0.75rem;">🎭 {hook_format.split()[0]} {hook_format.split()[1]}</span>'
                        f'<span style="background:#dbeafe; color:#1e40af; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.75rem;">📈 Skor Retensi: {chosen_hook_obj["score"]}</span>'
                        f'</div>'
                        f'</div>'
                        f'<div style="margin-bottom:4px;"><b>🎥 Aksi Kamera (Visual):</b> {chosen_hook_obj["visual"]}</div>'
                        f'<div style="font-size:0.8rem; color:#475569;"><b>📝 Teks di Layar:</b> {chosen_hook_obj["screen_text"]}</div>'
                        f'{fact_pill}'
                        f'</div>'
                    )
                    st.markdown(hook_card_html, unsafe_allow_html=True)

                hook_default = chosen_hook_obj["verbal"] if chosen_hook_obj else st.session_state.get("pipe_chosen_hook", "Stop scroll kalau kamu gak mau rugi waktu dan duit sia-sia!")
                chosen_hook_text = st.text_area(
                    "Naskah Hook Verbal Terpilih (Bisa Anda Sempurnakan / Edit):",
                    value=st.session_state.get("pipe_custom_hook_text", hook_default),
                    placeholder="Contoh: Stop scroll kalau kamu gak mau boncos tiap bulan...",
                    height=85,
                    key="pipe_custom_hook_text"
                )

                col_prev2, col_next2 = st.columns([1, 2])
                with col_prev2:
                    if st.button("⬅️ Kembali ke Tahap 1", use_container_width=True):
                        st.session_state["pipeline_step"] = 1
                        st.rerun()
                with col_next2:
                    if st.button("➡️ Gunakan Hook Ini & Lanjut ke Tahap 3: Storyboard", type="primary", use_container_width=True):
                        if not chosen_hook_text.strip():
                            st.warning("⚠️ Mohon pilih atau tentukan Hook pembuka terlebih dahulu.")
                        else:
                            if st.session_state.get("current_pipeline_draft_id"):
                                update_draft(st.session_state["current_pipeline_draft_id"], {
                                    "hook_verbal": chosen_hook_text,
                                    "content_format": hook_format,
                                    "status": "📝 Skrip Selesai"
                                })
                            st.session_state["pipe_chosen_hook"] = chosen_hook_text
                            st.session_state["pipe_story_topic"] = hook_topic
                            st.session_state["pipe_format_val"] = hook_format
                            st.session_state["pipeline_step"] = 3
                            st.rerun()

        # ---------------------------------------------------------------------
        # TAHAP 3: STORYBOARD & TABEL PRODUKSI DETIK DEMI DETIK
        # ---------------------------------------------------------------------
        elif current_step == 3:
            from utils.export_helpers import get_smart_autopilot_presets

            st.markdown("### 🎬 Tahap 3: Generator Storyboard & Papan Cerita Detik demi Detik")
            st.caption("AI akan meracik naskah narasi, instruksi kamera, B-roll, prompt video AI, dan micro-scenes aman <= 15 detik.")

            st.markdown(
                '<div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">'
                '💡 <b>Panduan Pemula (Anti-Terpotong AI Video):</b> Dialog di setiap scene dibatasi maksimal <b>20-25 kata (~10-12 detik)</b> agar ketika Anda generate video di Kling AI, Runway Gen-3, atau ElevenLabs, vokal dan adegan <b>tidak akan pernah terpotong di tengah jalan</b>. Anda juga bisa memilih durasi fleksibel agar materi mendalam (>60s) dapat diakomodir tuntas!'
                '</div>',
                unsafe_allow_html=True
            )

            current_pipe_hook = st.session_state.get("pipe_chosen_hook", "")
            if not current_pipe_hook:
                st.warning("⚠️ Anda belum memilih Hook di Tahap 2. Silakan kembali ke Tahap 2 untuk memilih hook, atau tulis hook langsung di bawah.")

            # Ambil data draft & hitung rekomendasi Auto-Pilot awal
            active_draft_obj = get_draft(st.session_state.get("current_pipeline_draft_id")) if st.session_state.get("current_pipeline_draft_id") else None
            niche_source = st.session_state.get("pipe_niche", "") or (active_draft_obj.get("niche", "") if active_draft_obj else "")
            aud_source = st.session_state.get("pipe_audience", "") or (active_draft_obj.get("target_audience", "") if active_draft_obj else "")
            comm_source = st.session_state.get("pipe_comm_style", "") or (active_draft_obj.get("communication_style", "") if active_draft_obj else "")
            initial_story_topic = st.session_state.get("pipe_story_topic") or st.session_state.get("pipe_hook_topic_input", "")

            autopilot = get_smart_autopilot_presets(
                niche=niche_source,
                hook=current_pipe_hook,
                topic=initial_story_topic,
                existing_audience=aud_source,
                communication_style=comm_source
            )

            # -------------------------------------------------------------
            # FORMAT & MODEL EKSEKUSI KONTEN KREATIF (6 PILIHAN FORMAT)
            # -------------------------------------------------------------
            FORMAT_OPTIONS = [
                "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)",
                "🎭 Skit Komedi / Parodi Situasional (POV 2 Karakter Bertolak Belakang)",
                "🎬 Micro-Drama & Storytelling Emosional (Plot Twist & Narasi Kisah Nyata)",
                "🎞️ Voiceover Faceless Sinematik (Tanpa Wajah — Audio Narasi + B-Roll ASMR)",
                "🥊 Debat Dialektika (Si Skeptis Penasaran vs Si Praktisi Solutif)",
                "📖 Analogi Fabel / Bedah Kasus & Sejarah Unik"
            ]

            raw_saved_fmt = st.session_state.get("pipe_format_val") or (active_draft_obj.get("content_format") if active_draft_obj else "") or autopilot.get("content_format", FORMAT_OPTIONS[0])
            fmt_idx = 0
            for f_i, f_opt in enumerate(FORMAT_OPTIONS):
                if f_opt.split()[1].lower() in str(raw_saved_fmt).lower() or str(raw_saved_fmt).lower() in f_opt.lower():
                    fmt_idx = f_i
                    break

            # -------------------------------------------------------------
            # ZONA 1: THE CREATIVE CORE (2-COLUMN BALANCED COCKPIT)
            # -------------------------------------------------------------
            col1, col2 = st.columns([1.15, 1], gap="medium")
            with col1:
                st.info(f"**Hook Terpilih:** *\"{current_pipe_hook or '(Belum dipilih - kembali ke Tahap 2)'}\"*")
                story_topic_final = st.text_area(
                    "Topik Konten:",
                    value=initial_story_topic,
                    placeholder="Contoh: Bahas 3 langkah praktis mulai dari riset produk, cara buat video tanpa muka, sampai cara dapat komisi pertama...",
                    height=100,
                    key="pipe_story_topic"
                )
            with col2:
                selected_format = st.selectbox(
                    "🎭 Format & Model Eksekusi Konten:",
                    options=FORMAT_OPTIONS,
                    index=fmt_idx,
                    key="pipe_step3_format_widget",
                    help="Pilih format penyampaian: Talking head, Skit komedi 2 orang, micro-drama emosional, video tanpa wajah (faceless ASMR), debat dialektika, atau analogi fabel."
                )
                format_notes = {
                    "Talking Head": "🎙️ <b>Talking Head Sinematik:</b> Tatapan intens ke kamera HP, mikro-ekspresi tajam, jump-cut cepat, dan B-roll pendukung.",
                    "Skit Komedi": "🎭 <b>POV 2 Karakter Kontras:</b> Naskah dialog dibagi otomatis per peran (misal: <code>[Si Boros]</code> vs <code>[Si Cermat]</code>) dengan sudut kamera shot-reverse-shot.",
                    "Micro-Drama": "🎬 <b>Alur 3 Babak Emosional:</b> Struktur krisis mendalam, perjuangan, dan plot twist dramatis dengan pencahayaan moody sinematik.",
                    "Voiceover Faceless": "🎞️ <b>100% Tanpa Wajah:</b> Menyorot aksi tangan estetik (hands-in-action), proses mekanis, dan visual B-roll ASMR tactile.",
                    "Debat Dialektika": "🥊 <b>Adu Argumen Seru:</b> Konfrontasi <code>[Si Skeptis]</code> vs <code>[Si Praktisi]</code> yang membungkam keraguan memakai data dan logika.",
                    "Analogi Fabel": "📖 <b>Pembedah Konsep Rumit:</b> Menjelaskan topik sulit memakai perumpamaan analogi fabel, eksperimen unik, atau studi kasus bersejarah."
                }
                note_text = "🎙️ Format penyampaian kreatif"
                for fn_k, fn_v in format_notes.items():
                    if fn_k.lower() in selected_format.lower():
                        note_text = fn_v
                        break
                st.markdown(f"<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:6px 10px; font-size:0.78rem; color:#334155; margin-bottom:8px; line-height:1.4;'>{note_text}</div>", unsafe_allow_html=True)

                dur_options = [
                    "⚡ Otomatis Fleksibel (AI Analisis Kedalaman Topik: 30s - 120s)",
                    "⚡ 30 - 45 Detik (Ringkas & Fast-Paced — 3-4 Scene)",
                    "⚡ 60 Detik (Standar Shorts, Reels & TikTok — 5-6 Scene)",
                    "⚡ 75 - 90 Detik (Penjelasan Berbobot / Multi-Poin — 6-8 Scene)",
                    "⚡ 90 - 120 Detik (Edukasi Mendalam / Deep-Dive — 8-10 Scene)"
                ]
                target_dur = st.selectbox(
                    "⏱️ Pilihan Durasi Video:",
                    options=dur_options,
                    index=0,
                    key="pipe_dur_select",
                    help="Pilih 'Otomatis Fleksibel' agar AI menyesuaikan durasi (30-120s) secara cerdas sesuai kebutuhan konten tanpa batasan kaku."
                )

            # -------------------------------------------------------------
            # ZONA 2: SMART FORMAT-AWARE CTA PRESETS (AKSI AKHIR RELEVAN)
            # -------------------------------------------------------------
            def _get_format_cta_presets(fmt: str):
                f_lower = fmt.lower()
                if "skit" in f_lower or "komedi" in f_lower:
                    return [
                        ("👥 Tag Teman yang Mirip", "Tag teman lu yang kelakuannya persis kayak gini di kolom komentar!"),
                        ("⚖️ Komen: Lu Tim Mana?", "Tulis di komentar: lu tim mana, karakter yang pertama atau yang kedua?"),
                        ("🔗 Solusi Lengkap di Bio", "Cek link di bio untuk solusi dan panduan lengkapnya sekarang!")
                    ]
                elif "debat" in f_lower or "dialektika" in f_lower:
                    return [
                        ("🥊 Adu Argumen di Komen", "Kira-kira argumen mana yang paling masuk akal buat lu? Tulis di kolom komentar!"),
                        ("📊 Ketik 'BUKTI' di Komen", "Ketik 'BUKTI' di kolom komentar untuk dapatkan lembar data & riset komparasi lengkapnya!"),
                        ("🔗 Baca Riset di Bio", "Cek link bio untuk akses sumber data ilmiah dan studi kasus lengkapnya!")
                    ]
                elif "micro-drama" in f_lower or "drama" in f_lower:
                    return [
                        ("💾 Simpan & Share Video", "Simpan video ini biar nggak hilang, dan share ke orang terdekat yang lagi butuh!"),
                        ("💬 Pernah Ngalamin? (Komen)", "Pernah ngalamin momen kayak gini juga dalam hidup lu? Ceritain di kolom komentar ya!"),
                        ("🔗 Solusi Lengkap di Bio", "Pelajari cara mengatasi masalah ini langkah demi langkah lewat panduan di link bio!")
                    ]
                elif "faceless" in f_lower or "voiceover" in f_lower or "asmr" in f_lower:
                    return [
                        ("💾 Save Buat Contekan", "Save video ini sekarang buat contekan dan panduan praktis lu nanti!"),
                        ("💬 Ketik 'PANDUAN' di Komen", "Ketik 'PANDUAN' di kolom komentar buat dapetin checklist tools & langkah lengkapnya!"),
                        ("🛒 Cek Keranjang Kuning", "Cek keranjang kuning sekarang selagi stok promo dan diskon masih tersedia!")
                    ]
                elif "fabel" in f_lower or "analogi" in f_lower:
                    return [
                        ("🤯 Share ke Teman", "Share video ini ke teman atau rekan kerja yang wajib paham konsep ini!"),
                        ("💬 Menurut Lu Gimana?", "Menurut lu perumpamaan tadi udah pas belum? Tulis pandangan lu di komentar!"),
                        ("🔗 Bedah Lengkap di Bio", "Cek link bio untuk bedah kasus mendalam dan studi lengkapnya!")
                    ]
                else:  # Talking Head / default
                    return [
                        ("🔗 Cek Link di Bio", "Ajak penonton cek link bio untuk download template / panduan lengkap gratis..."),
                        ("🛍️ Cek Keranjang Kuning", "Ajak penonton klik keranjang kuning sekarang selagi promo masih tersedia..."),
                        ("💬 Tanya di Komentar", "Minta penonton ketik 'MAU' di kolom komentar untuk dikirimkan panduannya...")
                    ]

            curr_cta_presets = _get_format_cta_presets(selected_format)

            def _set_pipe_cta(val):
                st.session_state["pipe_cta_target"] = val

            st.markdown("<div style='font-size:0.83rem; font-weight:600; color:#475569; margin: 14px 0 4px 0;'>🎯 Rekomendasi Aksi Akhir (CTA) Sesuai Format — Klik Cepat untuk Menerapkan:</div>", unsafe_allow_html=True)
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.button(curr_cta_presets[0][0], key="btn_cta_p1", on_click=_set_pipe_cta, args=(curr_cta_presets[0][1],), use_container_width=True)
            with col_c2:
                st.button(curr_cta_presets[1][0], key="btn_cta_p2", on_click=_set_pipe_cta, args=(curr_cta_presets[1][1],), use_container_width=True)
            with col_c3:
                st.button(curr_cta_presets[2][0], key="btn_cta_p3", on_click=_set_pipe_cta, args=(curr_cta_presets[2][1],), use_container_width=True)

            if "pipe_cta_target" not in st.session_state:
                st.session_state["pipe_cta_target"] = ""

            cta_target = st.text_input(
                "Aksi Akhir / CTA Video (Opsional — Auto-Pilot otomatis memilih jika kosong):",
                placeholder=f"Contoh: {curr_cta_presets[0][1]}",
                key="pipe_cta_target",
                help="Bebas dikosongkan. Jika tidak diisi, AI Auto-Pilot akan otomatis meracik CTA paling pas sesuai format konten."
            )

            # -------------------------------------------------------------
            # ZONA 3: PROGRESSIVE DISCLOSURE (OTORITAS & KUSTOM SUTRADARA)
            # -------------------------------------------------------------
            # Inisialisasi awal nilai setup sutradara dari Auto-Pilot (Anti UnboundLocalError)
            selected_theme = autopilot["theme"]
            selected_audience = autopilot["audience"]
            selected_slang = autopilot["slang"]
            selected_emotion = autopilot["emotion"]
            selected_visual_style = autopilot["visual_style"]
            selected_env = autopilot["environment"]
            selected_color = autopilot["color_grading"]
            selected_voice = autopilot["voice_style"]

            authority_level = "🔬 Praktisi / Berbasis Data & Riset (Wajib metrik %, nama teknis konkret & studi komparasi)"
            custom_evidence = ""
            is_pure_autopilot = True

            with st.expander("⚙️ Pengaturan Lanjutan, Otoritas & Kustom Sutradara (Opsional)", expanded=False):
                st.markdown("<div style='font-size:0.88rem; font-weight:700; color:#334155; margin-bottom:6px;'>🔬 Tingkat Otoritas Konten & Bukti Data (Anti-AI Slop)</div>", unsafe_allow_html=True)
                col_auth1, col_auth2 = st.columns([1.3, 1], gap="medium")
                with col_auth1:
                    authority_level = st.selectbox(
                        "Level Otoritas & Kedalaman Materi:",
                        [
                            "🔬 Praktisi / Berbasis Data & Riset (Wajib metrik %, nama teknis konkret & studi komparasi)",
                            "🛠️ Tutorial Taktis Langkah Demi Langkah (Parameter angka eksak, takaran & instruksi presisi)",
                            "📈 Studi Kasus & Bedah Eksperimen (Bedah angka Before-After riil)",
                            "💡 Edukasi Ringkas Populer (Istilah sederhana dengan analogi cerdas)"
                        ],
                        index=0,
                        key="pipe_authority_level",
                        help="Menentukan tingkat bobot data dan kedalaman teknis naskah agar terhindar dari konten umum/klise."
                    )
                with col_auth2:
                    custom_evidence = st.text_input(
                        "Data / Fakta / Studi Kasus Khusus (Opsional):",
                        value=st.session_state.get("pipe_custom_evidence", ""),
                        placeholder="Contoh: Split test 1.000 user konversi naik 42%, Jurnal dermatologi 2023...",
                        key="pipe_custom_evidence",
                        help="Tuliskan angka/studi/fakta khusus jika ada. Jika kosong, AI otomatis meracik data otoritas terbaik sesuai industri."
                    )

                st.markdown("<hr style='margin:14px 0; border:none; border-top:1px solid #e2e8f0;'>", unsafe_allow_html=True)
                st.markdown("<div style='font-size:0.88rem; font-weight:700; color:#334155; margin-bottom:6px;'>🎬 Mode Pengarahan Sutradara</div>", unsafe_allow_html=True)

                director_mode = st.radio(
                    "Pilih Mode Pengarahan Sutradara:",
                    [
                        "⚡ Auto-Pilot Penuh (AI Otomatis Racik Lokasi, Visual, Vokal & Mood Sesuai Topik)",
                        "⚙️ Kustom Manual (Tentukan Sendiri Gaya Visual, Lokasi & Vokal di Bawah)"
                    ],
                    index=0,
                    horizontal=True,
                    key="pipe_director_mode_radio"
                )

                is_pure_autopilot = ("Auto-Pilot" in director_mode)

                if is_pure_autopilot:
                    autopilot_banner_html = (
                        '<div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); border: 1.5px solid #4338ca; border-radius: 10px; padding: 12px 16px; margin: 10px 0 6px 0; color: white;">'
                        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
                        '<span style="font-weight: 700; font-size: 0.95rem; color: #a5b4fc;">⚡ Mode Auto-Pilot Cerdas Aktif</span>'
                        '<span style="background: #10b981; color: #ffffff; font-weight: 700; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem;">100% Dinamis & Kontekstual</span>'
                        '</div>'
                        '<div style="font-size: 0.84rem; color: #c7d2fe; line-height: 1.5;">'
                        'AI bertindak sebagai Sutradara Utama. AI merancang setting lokasi kontekstual (misal dapur resep, tech desk neon, kamar mandi skincare), palet warna, vokal, dan karakter <b>100% hidup & nyata</b>.'
                        '</div>'
                        '<div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">'
                        '<span style="background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(165, 180, 252, 0.3); border-radius: 6px; padding: 2px 8px; font-size: 0.73rem; color: #e0e7ff;">📊 Data Empiris & Metrik Terukur</span>'
                        '<span style="background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(165, 180, 252, 0.3); border-radius: 6px; padding: 2px 8px; font-size: 0.73rem; color: #e0e7ff;">⚙️ Kausalitas \'The Mechanism\'</span>'
                        '<span style="background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(165, 180, 252, 0.3); border-radius: 6px; padding: 2px 8px; font-size: 0.73rem; color: #e0e7ff;">💡 Free Actionable Value-Bomb</span>'
                        '<span style="background: rgba(16, 185, 129, 0.25); border: 1px solid rgba(110, 231, 183, 0.3); border-radius: 6px; padding: 2px 8px; font-size: 0.73rem; color: #a7f3d0;">⏱️ Sinkron Vokal & Visual &lt;= 15s</span>'
                        '</div>'
                        '</div>'
                    )
                    st.markdown(autopilot_banner_html, unsafe_allow_html=True)
                else:
                    st.caption("Ubah opsi di bawah ini jika Anda ingin kustomisasi manual gaya visual (misal: 3D Animasi, Anime, Retro Film), lokasi studio tertentu, atau target audiens spesifik.")

                    theme_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "💡 Edukasi Solutif & Hack Cepat (Value-Bomb)",
                        "🥊 Bongkar Mitos & Realita Pahit (Hard Truth / Kontras)",
                        "📖 Storytelling Pengalaman Nyata (Relatable & Emosional)",
                        "🛠️ Tutorial Taktis Langkah Demi Langkah (Actionable Playbook)",
                        "🛍️ Review Jujur & Soft-Selling (Solusi Masalah)",
                        "🎭 Skit Komedi / Parodi Relatable (Humor Situasi Sehari-hari)",
                        "✏️ Kustom (Ketik Pilar Tema Sendiri)"
                    ]

                    slang_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "🔥 Lu - Gua / Bro - Sis (Santai, Gaul, Akrab Gen Z/Millennial)",
                        "🤝 Aku - Kamu / Teman-teman (Hangat, Empatik, Ramah Sahabat)",
                        "👔 Saya - Anda / Rekan-rekan (Profesional, Otoritatif, Edukasi Formal)",
                        "✨ Bestie / Guys (Trendy, Kasual, Vibe Cerita Tongkrongan)",
                        "✏️ Kustom (Ketik Gaya Sapaan Sendiri)"
                    ]

                    emotion_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "👀 Rasa Penasaran Ekstrem (Curiosity Gap - Wajib Nonton Sampai Akhir)",
                        "😱 FOMO & Ketakutan Rugi (Takut Ketinggalan / Rugi Kalau Gak Tahu)",
                        "🤯 Mind-Blown / Kaget (Membongkar Rahasia yang Tidak Disangka)",
                        "😌 Lega & Tenang (Mendapatkan Solusi Instan Atas Masalah Berat)",
                        "💪 Semangat & Termotivasi (Dorongan Aksi Cepat Tanpa Nanti)",
                        "✏️ Kustom (Ketik Emosi Sendiri)"
                    ]

                    vis_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "🎥 Realistis Sinematik / Live Action (Talent Manusia / UGC 4K)",
                        "🤖 3D Animation (Gaya Pixar / Disney / Unreal Engine 5 Render)",
                        "🎌 Anime / Manga Estetik (Gaya Studio Ghibli / Makoto Shinkai)",
                        "🎨 2D Motion Graphics & Flat Vector (Gaya Vox / Kurzgesagt)",
                        "📸 Vintage Retro 35mm Analog Film (Nostalgia 90s / Kodak Film Grain)",
                        "🔮 Cyberpunk Neon & Sci-Fi Futuristik (Blade Runner / High Tech)",
                        "✏️ Kustom (Ketik Gaya Visual Sendiri)"
                    ]

                    env_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "Dapur Rumah Minimalis Bersih & Estetik (Natural Morning Light & Marmer Putih)",
                        "Vanity Mirror Kamar Mandi Marmer Putih Bersih (Clean Bright Ring Light)",
                        "Meja Rias Vanity Estetik dengan Cermin LED & Rak Kosmetik Rapi",
                        "Walk-in Closet Estetik / Kamar Tidur Modern dengan Full-Length Mirror",
                        "Garasi Modern Bersih dengan Tool Rack Rapi & Pencahayaan Neon Cool White",
                        "Gym Modern / Ruang Latihan Fitness dengan Mirror Wall & Dumbbell Rack",
                        "Desk Setup Gadget & Ambient Neon Light (Tech Minimalist Dark)",
                        "Smart Workspace Modern / Meja Kerja Rapi dengan Laptop & Tanaman Indoor",
                        "Coffee Shop Estetik / Espresso Bar Modern (Warm Bokeh Background)",
                        "Kantor Korporat Modern / Meja Kerja Rapi Profesional",
                        "Ruang Bermain Anak Ceria & Ruang Keluarga Hangat Bersih",
                        "Ruang Santai Kasual / Living Room Estetik (Natural Daylight)",
                        "Taman Rumah Minimalis / Balkon Urban Farming Hijau",
                        "Outdoor Dinamis / Suasana Urban Kota Modern Sinematik",
                        "Dark Gaming Room dengan Ambient RGB Neon & Gaming Chair Setup",
                        "Studio Kerja Minimalis Modern (Warm Wood & Soft Amber Lighting)",
                        "Dark Studio Sinematik (Latar Hitam & Rim Light Kuat)",
                        "✏️ Kustom (Ketik Setting Lokasi Sendiri)"
                    ]

                    color_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "Moody Teal & Warm Orange Sinematik (Hollywood Blockbuster Look)",
                        "Clean High-Key SaaS & Tech (Bright Natural, Cool Blue Accent)",
                        "Dark Documentary (High Contrast, Deep Shadow, Desaturated Tone)",
                        "Pastel Dreamy Aesthetic (Soft Glow, Warm Highlights, Airy Feel)",
                        "Vibrant Pop Energetic (Saturasi Tinggi, TikTok Trend Vibe)",
                        "✏️ Kustom (Ketik Palet Warna Sendiri)"
                    ]

                    voice_options = [
                        "-- ⚡ Ikuti Rekomendasi Auto-Pilot --",
                        "Santai & Empatik (Bestie Vibe, Akrab, Mengalir Luwes)",
                        "Tegas & Berwibawa (Otoritas Tinggi, Meyakinkan, No-BS Expert)",
                        "Misterius & Berbisik Cepat (Curiosity Gap, Konspiratif Rahasia)",
                        "Punchy, Hype & Berenergi Tinggi (Pemicu Adrenalin, Semangat Membara)",
                        "Storyteller Hangat & Reflektif (Penuh Emosi & Sentuhan Personal)",
                        "✏️ Kustom (Ketik Gaya Vokal Sendiri)"
                    ]

                    col_dna1, col_dna2 = st.columns(2)
                    with col_dna1:
                        theme_choice = st.selectbox("💡 Pilar Tema Konten:", theme_options, index=0, key="pipe_theme_select")
                        if theme_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_theme = autopilot["theme"]
                        elif "Kustom" in theme_choice:
                            custom_theme = st.text_input("Ketik Pilar Tema Kustom:", value="", placeholder="Contoh: Analisis tren masa depan...", key="pipe_custom_theme")
                            selected_theme = custom_theme.strip() if custom_theme.strip() else autopilot["theme"]
                        else:
                            selected_theme = theme_choice

                        target_audience_input = st.text_input(
                            "👥 Target Audiens Spesifik & Usia:",
                            value="",
                            placeholder=f"Kosongkan untuk ikuti Auto-Pilot: ({autopilot['audience'][:45]}...)",
                            key="pipe_aud_target_input"
                        )
                        selected_audience = target_audience_input.strip() if target_audience_input.strip() else autopilot["audience"]

                        slang_choice = st.selectbox("🗣️ Gaya Sapaan & Diksi Bahasa Audiens:", slang_options, index=0, key="pipe_slang_select")
                        if slang_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_slang = autopilot["slang"]
                        elif "Kustom" in slang_choice:
                            custom_slang = st.text_input("Ketik Gaya Sapaan Kustom:", value="", placeholder="Contoh: Sapaan 'Bapak/Ibu'...", key="pipe_custom_slang")
                            selected_slang = custom_slang.strip() if custom_slang.strip() else autopilot["slang"]
                        else:
                            selected_slang = slang_choice

                        emotion_choice = st.selectbox("⚡ Trigger Emosi Dominan:", emotion_options, index=0, key="pipe_emotion_select")
                        if emotion_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_emotion = autopilot["emotion"]
                        elif "Kustom" in emotion_choice:
                            custom_emotion = st.text_input("Ketik Trigger Emosi:", value="", placeholder="Contoh: Rasa tertantang...", key="pipe_custom_emotion")
                            selected_emotion = custom_emotion.strip() if custom_emotion.strip() else autopilot["emotion"]
                        else:
                            selected_emotion = emotion_choice

                    with col_dna2:
                        visual_style_choice = st.selectbox("🎭 Tipe Konten Visual:", vis_options, index=0, key="pipe_visual_style_select")
                        if visual_style_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_visual_style = autopilot["visual_style"]
                        elif "Kustom" in visual_style_choice:
                            custom_visual_style = st.text_input("Ketik Gaya Visual Kustom:", value="", placeholder="Contoh: Stop-motion animation...", key="pipe_custom_visual_style")
                            selected_visual_style = custom_visual_style.strip() if custom_visual_style.strip() else autopilot["visual_style"]
                        else:
                            selected_visual_style = visual_style_choice

                        environment_choice = st.selectbox("🏞️ Setting Lokasi / Environment:", env_options, index=0, key="pipe_env_select")
                        if environment_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_env = autopilot["environment"]
                        elif "Kustom" in environment_choice:
                            custom_env = st.text_input("Ketik Setting Lokasi Kustom:", value="", placeholder="Contoh: Kafe outdoor...", key="pipe_custom_env")
                            selected_env = custom_env.strip() if custom_env.strip() else autopilot["environment"]
                        else:
                            selected_env = environment_choice

                        color_choice = st.selectbox("🎨 Color Grading & Palet Warna:", color_options, index=0, key="pipe_color_select")
                        if color_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_color = autopilot["color_grading"]
                        elif "Kustom" in color_choice:
                            custom_color = st.text_input("Ketik Palet Warna Kustom:", value="", placeholder="Contoh: Monokrom kontras tinggi...", key="pipe_custom_color")
                            selected_color = custom_color.strip() if custom_color.strip() else autopilot["color_grading"]
                        else:
                            selected_color = color_choice

                        voice_choice = st.selectbox("🗣️ Voice Style & Karakter Vokal:", voice_options, index=0, key="pipe_voice_select")
                        if voice_choice == "-- ⚡ Ikuti Rekomendasi Auto-Pilot --":
                            selected_voice = autopilot["voice_style"]
                        elif "Kustom" in voice_choice:
                            custom_voice = st.text_input("Ketik Gaya Vokal Kustom:", value="", placeholder="Contoh: Suara bariton...", key="pipe_custom_voice")
                            selected_voice = custom_voice.strip() if custom_voice.strip() else autopilot["voice_style"]
                        else:
                            selected_voice = voice_choice

            btn_run_step3 = st.button("🎬 1-Klik Hasilkan Papan Cerita & Storyboard (Auto-Pilot & Disiplin <= 15s)", type="primary", use_container_width=True)

            if btn_run_step3:
                if not current_pipe_hook.strip():
                    st.warning("⚠️ Hook pembuka masih kosong. Silakan kembali ke Tahap 2 untuk memilih hook terlebih dahulu.")
                elif not story_topic_final.strip():
                    st.warning("⚠️ Mohon isi Topik Konten terlebih dahulu.")
                else:
                    # Zero-Blocking CTA: gunakan teks user jika ada, atau fallback otomatis ke preset terbaik format
                    final_cta = cta_target.strip() if cta_target.strip() else curr_cta_presets[0][1]
                    st.session_state["pipe_final_cta"] = final_cta

                    with st.spinner("🎥 Menyusun pergerakan kamera, kunci konsistensi gaya, dialog audio berjiwa persona, dan micro-scenes (maks 15 detik & maks 25 kata)..."):
                        if "30 - 45" in target_dur:
                            scene_req_text = "TARGET JUMLAH SCENE: TEPAT 3 - 4 SCENE (Total durasi 30-45 detik, ringkas & to-the-point)."
                        elif "75 - 90" in target_dur:
                            scene_req_text = "TARGET JUMLAH SCENE: 7 - 8 SCENE (Total durasi 75-90 detik. Wajib sediakan 3-4 scene edukasi mendalam/langkah bertahap di bagian tengah agar materi tuntas! DILARANG membatasi hanya 6 scene!)."
                        elif "90 - 120" in target_dur:
                            scene_req_text = "TARGET JUMLAH SCENE: 8 - 12 SCENE (Total durasi 90-120 detik. Rancang tutorial/masterclass komprehensif langkah demi langkah, multi-poin bukti, dan tips praktis. DILARANG memotong hanya jadi 6 scene!)."
                        elif "60" in target_dur:
                            scene_req_text = "TARGET JUMLAH SCENE: 5 - 6 SCENE (Total durasi 55-60 detik standar media sosial)."
                        else:
                            scene_req_text = "TARGET JUMLAH SCENE: DINAMIS FLEKSIBEL (Analisis kedalaman materi: jika ringan buat 3-4 scene, jika standar buat 5-6 scene, jika topik butuh penjelasan mendalam/banyak langkah kembangkan secara bebas jadi 7-10 scene agar materi tuntas!)."

                        if is_pure_autopilot:
                            director_instructions = f"""⚡ MODE SUTRADARA: AUTO-PILOT CERDAS PENUH (AI SUTRADARA DINAMIS & KONTEKSTUAL)
PERHATIAN SUTRADARA AI:
DILARANG menggunakan template lokasi studio yang monoton/generik jika ada setting lokasi yang jauh lebih nyata, hidup, dan relevan dengan topik ini!
- MODEL & FORMAT EKSEKUSI KONTEN: {selected_format}
- TOPIK KONTEN: {story_topic_final}
- HOOK PEMBUKA: {current_pipe_hook}
- TARGET PLATFORM: {st.session_state.get('pipe_platform', 'TikTok / Reels')}
- NICHE INDUSTRI: {niche_source or 'Umum'}

TUGAS DIREKSI SUTRADARA AI (Rancang secara mandiri dan spesifik):
1. FORMAT EKSEKUSI KONTEN: Patuhi secara ketat format '{selected_format}'. Jika Skit 2 Karakter, wajib gunakan tag dialog per peran (contoh: [Si Boros] vs [Si Cermat]) dan arahan kamera shot-reverse-shot. Jika Faceless ASMR, 100% tanpa wajah dengan tag [Voiceover] dan aksi tangan macro. Jika Debat, tampilkan duel [Si Skeptis] vs [Si Praktisi]. Jika Micro-Drama, hadirkan alur plot twist emosional.
2. ENVIRONMENT / LOKASI: Ciptakan setting lokasi fisik yang PALING ASLI & KONTEKSTUAL untuk topik ini (Contoh: jika masak/resep -> Dapur rumah estetik; jika kecantikan/skincare -> Kamar mandi marmer putih bersih / vanity mirror; jika tech/coding -> Dark tech desk ambient neon; jika otomotif -> Garasi modern atau jalanan kota; jika bisnis/finansial -> Coworking space modern / meja kerja rapi; jika parenting -> Ruang keluarga hangat; jika olahraga/diet -> Gym atau ruang santai).
3. TIPE VISUAL: Tentukan gaya visual terbaik (Realistis Sinematik 4K / UGC bernuansa otentik yang paling mengikat emosi audiens).
4. COLOR GRADING: Palet warna dan pencahayaan sinematik yang memperkuat mood topik (Warm Golden, Clean High-Key Bright, Moody Teal & Orange, Vibrant Pop, dsb).
5. VOICE STYLE: Karakter vokal, tempo bicara natural, dan artikulasi yang paling meyakinkan audiens.
6. PERSONA & DIKSI AUDIENS: Sapaan (Lu-Gua / Aku-Kamu / Bestie / Saya-Anda) dan kosakata percakapan yang paling relate dengan penonton topik ini.
7. KEDALAMAN MATERI, OTORITAS & BUKTI EMPIRIS (ANTI-KONTEN UMUM & ANTI-AI SLOP):
   - Level Otoritas: {authority_level}
   - {f"Data/Fakta Spesifik Pengguna: {custom_evidence.strip()}" if custom_evidence.strip() else "Data Otoritas: AI wajib menyematkan metrik terukur konkret (persentase %, durasi waktu riil yang dipangkas, angka suhu/kadar/torsi/takaran presisi), nama alat/bahan/teknik spesifik tanpa kata kabur, dan membongkar salah kaprah umum."}
   - Kausalitas 'The Mechanism': Jelaskan secara gamblang MENGAPA solusi ini bekerja secara logis/ilmiah agar penonton mendapatkan sensasi 'Aha! Moment' dari seorang Subject Matter Expert sejati.
   - B-Roll Bukti Fisik: B-roll wajib menyorot bukti nyata fisik (alat ukur, layar dashboard analitik, makro perbandingan, dsb).
8. JUMLAH SCENE & DURASI: {scene_req_text}"""
                        else:
                            director_instructions = f"""⚙️ MODE SUTRADARA: KUSTOM MANUAL (PILIHAN KHUSUS PENGGUNA)
Wajib mematuhi instruksi kustom pengguna berikut:
- Model & Format Eksekusi Konten: {selected_format} (Patuhi pembagian dialog dan staging format ini)
- Tipe Visual: {selected_visual_style}
- Environment / Setting Lokasi: {selected_env}
- Color Grading & Lighting: {selected_color}
- Karakter & Voice Style: {selected_voice}
- Pilar Tema Konten: {selected_theme}
- Target Audiens Spesifik: {selected_audience}
- Gaya Bahasa & Sapaan: {selected_slang}
- Trigger Emosi Dominan: {selected_emotion}
- Standar Bobot Isi & Otoritas: {authority_level}. {f"Data Khusus Pengguna: {custom_evidence.strip()}." if custom_evidence.strip() else "WAJIB padat data empiris, nama alat/bahan konkret, metrik terukur, dan kausalitas logis 'The Mechanism'."}
- B-Roll Bukti Fisik: Wajib menyorot bukti nyata fisik (alat ukur, grafik data, split-screen makro, dsb).
- Jumlah Scene & Durasi: {scene_req_text}"""

                        prompt = STORYBOARD_TABLE_PROMPT.format(
                            hook=current_pipe_hook,
                            topic=f"{story_topic_final} (Pilihan Durasi: {target_dur})",
                            goal=final_cta,
                            content_format=selected_format,
                            director_instructions=director_instructions,
                            visual_style=selected_visual_style,
                            environment=selected_env,
                            color_grading=selected_color,
                            voice_style=selected_voice,
                            content_theme=selected_theme,
                            target_audience=selected_audience,
                            audience_tone_slang=selected_slang,
                            emotional_trigger=selected_emotion
                        )
                        res3 = ai_client.generate(
                            prompt=prompt,
                            system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                        )
                        st.session_state["pipe_step3_result"] = res3
                        st.session_state["pipe_format_val"] = selected_format
                        st.session_state["pipe_theme_val"] = selected_theme
                        st.session_state["pipe_aud_val"] = selected_audience
                        st.session_state["pipe_slang_val"] = selected_slang
                        st.session_state["pipe_emotion_val"] = selected_emotion

            if "pipe_step3_result" in st.session_state:
                sb_result = st.session_state["pipe_step3_result"]
                from utils.export_helpers import parse_storyboard_scenes, format_scenes_for_production_sheet, parse_master_consistency_anchor
                parsed_scenes = parse_storyboard_scenes(sb_result)
                master_anchor = parse_master_consistency_anchor(sb_result)

                full_script = sb_result
                if parsed_scenes:
                    approx_words = sum(sc.get("word_count", 0) for sc in parsed_scenes)
                    est_sec = sum(sc.get("duration_sec", 0) for sc in parsed_scenes)
                else:
                    words = [w for w in full_script.split() if len(w) > 2 and not w.startswith("|") and not w.startswith("#")]
                    approx_words = int(len(words) * 0.45)
                    est_sec = max(25, int((approx_words / 130) * 60))

                tab_scene_view, tab_retention_view, tab_table_view, tab_tele_view = st.tabs([
                    "🎬 Format Scene Per Scene (Siap Copas Produksi)",
                    "📈 Prediksi Retensi & Pacing Video",
                    "📊 Tabel Pacing Storyboard",
                    "🎙️ Mode Teleprompter (Latihan Bicara)"
                ])

                with tab_scene_view:
                    st.markdown("#### 🎬 Lembar Kerja Produksi: Breakdown Per Scene")
                    st.caption("Disusun dengan disiplin retensi: maksimal 15 detik per scene. Dilengkapi Environment, Color Grading, Voice Style, dan Prompt Generator AI yang konsisten.")

                    # Tampilkan Master Consistency & DNA Persona Anchor Banner jika ada
                    if master_anchor and any(master_anchor.values()):
                        with st.container(border=True):
                            st.markdown(
                                '<div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 14px 18px; border-radius: 8px; color: white; margin-bottom: 12px;">'
                                '<h4 style="margin: 0 0 6px 0; color: #a5b4fc; font-size: 1.05rem;">🛡️ DNA Strategi Konten & Master Production Consistency Anchor</h4>'
                                '<div style="font-size: 0.85rem; color: #e0e7ff; line-height: 1.4;">'
                                'Seluruh scene, gaya bahasa percakapan, dan visual telah diselaraskan agar mengikat persona audiens target dan menjaga konsistensi render AI 100%.'
                                '</div></div>',
                                unsafe_allow_html=True
                            )

                            # Tampilkan DNA Brief Persona jika ada
                            if master_anchor.get("content_theme") or master_anchor.get("target_audience") or master_anchor.get("content_format"):
                                col_dna_v1, col_dna_v2 = st.columns(2)
                                with col_dna_v1:
                                    fmt_val = master_anchor.get("content_format") or st.session_state.get("pipe_format_val", "🎙️ Talking Head")
                                    st.markdown(f"**🎭 Format Eksekusi:**\n> {fmt_val}")
                                    if master_anchor.get("content_theme"):
                                        st.markdown(f"**💡 Pilar Tema:**\n> {master_anchor['content_theme']}")
                                with col_dna_v2:
                                    if master_anchor.get("target_audience"):
                                        st.markdown(f"**👥 Target Audiens:**\n> {master_anchor['target_audience']}")
                                    if master_anchor.get("audience_tone_slang"):
                                        st.markdown(f"**🗣️ Diksi & Sapaan:**\n> {master_anchor['audience_tone_slang']}")
                                    if master_anchor.get("emotional_trigger"):
                                        st.markdown(f"**⚡ Trigger Emosi:**\n> {master_anchor['emotional_trigger']}")
                                st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
                            
                            col_anc1, col_anc2 = st.columns(2)
                            with col_anc1:
                                if master_anchor.get("character_anchor"):
                                    st.markdown(f"**👤 Subjek / Karakter Tetap:**\n> {master_anchor['character_anchor']}")
                                if master_anchor.get("environment_anchor"):
                                    st.markdown(f"**🏞️ Setting Lokasi Master:**\n> {master_anchor['environment_anchor']}")
                            with col_anc2:
                                if master_anchor.get("color_grading_anchor"):
                                    st.markdown(f"**🎨 Color Grading & Lighting:**\n> {master_anchor['color_grading_anchor']}")
                                if master_anchor.get("voice_profile_anchor"):
                                    st.markdown(f"**🎙️ Voice Profile (ElevenLabs / Talent):**\n> {master_anchor['voice_profile_anchor']}")

                            if master_anchor.get("visual_style_lock"):
                                st.markdown("**🧬 Master AI Style Lock (Prompt Prefix Baku):**")
                                st.code(master_anchor["visual_style_lock"], language="text")

                    full_sheet = format_scenes_for_production_sheet(
                        parsed_scenes,
                        title=st.session_state.get("pipe_keyword", "Konten Video"),
                        platform=st.session_state.get("pipe_platform", "TikTok / Reels"),
                        master_anchor=master_anchor
                    )

                    with st.expander("📋 Salin Seluruh Naskah Lembar Produksi Lengkap (Untuk WhatsApp / Notion)", expanded=False):
                        st.code(full_sheet, language="text")

                    # Cek deteksi mismatch sinkronisasi durasi audio vs klip video
                    has_sync_issue = any(not sc.get("is_synced", True) for sc in parsed_scenes)
                    if has_sync_issue:
                        overflow_cnt = sum(1 for sc in parsed_scenes if sc.get("sync_status") == "overflow")
                        underflow_cnt = sum(1 for sc in parsed_scenes if sc.get("sync_status") == "underflow")
                        st.markdown(
                            f'<div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 1.5px solid #f59e0b; border-radius: 10px; padding: 12px 16px; margin: 10px 0 16px 0;">'
                            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                            f'<span style="font-weight: 700; color: #92400e; font-size: 0.95rem;">'
                            f'⏱️ Deteksi Sinkronisasi: {overflow_cnt} Scene Dialog Kepanjangan & {underflow_cnt} Scene Hening Visual</span>'
                            f'<span style="background: #f59e0b; color: white; padding: 2px 10px; border-radius: 10px; font-size: 0.75rem; font-weight:700;">'
                            f'Audio-Visual Sync Assist</span></div>'
                            f'<div style="font-size: 0.83rem; color: #78350f; margin-top: 5px; line-height: 1.5;">'
                            f'Terdeteksi perbedaan antara tempo bicara dialog (~1.9 kata/detik) dengan durasi klip visual (misal: klip 3 detik tapi dialog butuh 7 detik bicara, atau klip 12 detik tapi dialog hanya 4 detik). Anda dapat menyelaraskan durasi klip secara instan dengan 1-klik di bawah!'
                            f'</div></div>',
                            unsafe_allow_html=True
                        )
                        
                        col_sync_act1, col_sync_act2 = st.columns([1.5, 1])
                        with col_sync_act1:
                            if st.button("🧩 1-Klik Pecah Scene Panjang (Shot Sharding — 100% Pertahankan Kata Dramatis)", type="primary", use_container_width=True, key="btn_auto_shard_dialogues"):
                                from utils.export_helpers import shard_storyboard_scenes_by_clauses
                                sharded_md = shard_storyboard_scenes_by_clauses(sb_result, max_words_per_shot=14)
                                st.session_state["pipe_step3_result"] = sharded_md
                                if st.session_state.get("current_pipeline_draft_id"):
                                    update_draft(st.session_state["current_pipeline_draft_id"], {"storyboard_table_md": sharded_md})
                                st.success("✅ Seluruh scene panjang berhasil dipecah menjadi klip sinematik mandiri (Shot A & Shot B)! Seluruh kata dramatis dan data dipertahankan 100%!")
                                st.rerun()
                        with col_sync_act2:
                            if st.button("⚡ Selaraskan Durasi Klip Visual", type="secondary", use_container_width=True, key="btn_auto_sync_timeline"):
                                from utils.export_helpers import sync_storyboard_scenes_timeline, apply_synced_timeline_to_markdown
                                synced = sync_storyboard_scenes_timeline(parsed_scenes)
                                new_md = apply_synced_timeline_to_markdown(sb_result, synced)
                                st.session_state["pipe_step3_result"] = new_md
                                if st.session_state.get("current_pipeline_draft_id"):
                                    update_draft(st.session_state["current_pipeline_draft_id"], {"storyboard_table_md": new_md})
                                st.success("✅ Seluruh durasi scene dan timeline visual berhasil diselaraskan!")
                                st.rerun()

                    # Render kartu per scene siap copas
                    for sc in parsed_scenes:
                        with st.container(border=True):
                            col_sc_h1, col_sc_h2 = st.columns([2.0, 2.2])
                            with col_sc_h1:
                                st.markdown(f"##### 🎬 Scene {sc['scene_num']}: {sc['title']}")
                            with col_sc_h2:
                                dur_badge_color = sc.get("sync_badge_color", "#10b981")
                                dur_badge_bg = sc.get("sync_badge_bg", "#ecfdf5")
                                dur_badge_border = sc.get("sync_badge_border", "#a7f3d0")
                                w_count = sc.get("word_count", len(sc.get("audio", "").split()))
                                est_dur = sc.get("est_audio_dur", round(w_count / 1.9))
                                dur_sec_val = sc.get("duration_sec", 10)
                                dur_text = f"⏱️ Klip: {dur_sec_val}s • Naskah: {w_count} kata (~{est_dur}s) | {sc.get('sync_badge', '✅ Sinkron')}"
                                st.markdown(f"<div style='text-align:right; font-weight:700; color:{dur_badge_color}; background:{dur_badge_bg}; border:1px solid {dur_badge_border}; padding:3px 10px; border-radius:6px; font-size:0.78rem;'>{dur_text}</div>", unsafe_allow_html=True)

                            # Peringatan dini jika ada ketidaksinkronan durasi vs dialog
                            if sc.get("sync_status") == "overflow":
                                warn_html = (
                                    f'<div style="background:#fef2f2; border-left:3px solid #ef4444; padding:6px 12px; border-radius:4px; font-size:0.8rem; color:#991b1b; margin:6px 0 10px 0;">'
                                    f'🚨 <b>Peringatan Dialog Kepanjangan:</b> {sc.get("sync_note")} (Gunakan tombol \'1-Klik Pecah Scene Panjang\' di atas untuk memecahnya menjadi 2 shot tanpa mengurangi kata).'
                                    f'</div>'
                                )
                                st.markdown(warn_html, unsafe_allow_html=True)
                            elif sc.get("sync_status") == "underflow":
                                warn_html = (
                                    f'<div style="background:#fffbeb; border-left:3px solid #f59e0b; padding:6px 12px; border-radius:4px; font-size:0.8rem; color:#92400e; margin:6px 0 10px 0;">'
                                    f'⚠️ <b>Perhatian Hening Visual:</b> {sc.get("sync_note")}'
                                    f'</div>'
                                )
                                st.markdown(warn_html, unsafe_allow_html=True)
                            elif sc.get("word_count", 0) > 16:
                                warn_html = (
                                    f'<div style="background:#fffbeb; border-left:3px solid #f59e0b; padding:6px 12px; border-radius:4px; font-size:0.8rem; color:#92400e; margin:6px 0 10px 0;">'
                                    f'⚠️ <b>Tips Anti-Terpotong AI Video:</b> Dialog ini memiliki <b>{sc.get("word_count")} kata (~{sc.get("est_audio_dur")} detik)</b>. Untuk render di Kling AI / Runway Gen-3 (klip 5-10s), klik tombol <b>\'🧩 1-Klik Pecah Scene Panjang\'</b> di atas agar scene ini dipecah menjadi 2 shot sinematik (Shot A & Shot B) tanpa mengurangi satu kata pun!'
                                    f'</div>'
                                )
                                st.markdown(warn_html, unsafe_allow_html=True)

                            # Badges detail produksi, sutradara & persona (Rendered as clean HTML pills)
                            badge_items = []

                            # Badge Pembicara / Karakter jika ada
                            spk_tag = sc.get("speaker_tag", "")
                            if spk_tag:
                                spk_l = spk_tag.lower()
                                if any(w in spk_l for w in ["skeptis", "boros", "korban", "pembeli"]):
                                    spk_bg, spk_color, spk_border = "#fef3c7", "#92400e", "#fde68a"
                                elif any(w in spk_l for w in ["voiceover", "narator", "audio"]):
                                    spk_bg, spk_color, spk_border = "#e0e7ff", "#3730a3", "#c7d2fe"
                                elif any(w in spk_l for w in ["praktisi", "ahli", "solusi", "cermat", "penjual"]):
                                    spk_bg, spk_color, spk_border = "#ecfdf5", "#065f46", "#a7f3d0"
                                else:
                                    spk_bg, spk_color, spk_border = "#fdf4ff", "#86198f", "#f0abfc"
                                badge_items.append(f'<span style="background:{spk_bg}; padding:2px 8px; border-radius:4px; color:{spk_color}; border:1px solid {spk_border}; font-weight:700;">🗣️ {spk_tag}</span>')

                            v_style = sc.get('visual_style') or master_anchor.get('visual_style_lock') or 'Live Action Sinematik'
                            v_env = sc.get('environment') or master_anchor.get('environment_anchor') or 'Setting Lokasi Kontekstual'
                            v_color = sc.get('color_grading') or master_anchor.get('color_grading_anchor') or 'Moody Cinematic'
                            v_voice = sc.get('voice_style', 'Santai & Empatik')

                            badge_items.append(f'<span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🎨 Gaya:</b> {v_style}</span>')
                            badge_items.append(f'<span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🏞️ Lokasi:</b> {v_env}</span>')
                            badge_items.append(f'<span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🎨 Color:</b> {v_color}</span>')
                            badge_items.append(f'<span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🗣️ Vokal:</b> {v_voice}</span>')

                            if sc.get("acting_delivery"):
                                badge_items.append(f'<span style="background:#fdf4ff; padding:2px 8px; border-radius:4px; color:#a21caf; border:1px solid #f0abfc;"><b>🎭 Delivery:</b> {sc["acting_delivery"][:28]}</span>')
                            if sc.get("audience_relevance"):
                                badge_items.append(f'<span style="background:#eff6ff; padding:2px 8px; border-radius:4px; color:#1d4ed8; border:1px solid #bfdbfe;"><b>🎯 Audiens:</b> {sc["audience_relevance"][:30]}</span>')
                            if sc.get("cine_badge"):
                                badge_items.append(f'<span style="background:#f0fdf4; padding:2px 8px; border-radius:4px; color:#15803d; border:1px solid #bbf7d0;"><b>🎬 Sutradara Pro:</b> {sc["cine_badge"]}</span>')

                            badges_html = f'<div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; font-size:0.78rem;">{" ".join(badge_items)}</div>'
                            st.markdown(badges_html, unsafe_allow_html=True)

                            col_d1, col_d2 = st.columns([1.2, 1])
                            with col_d1:
                                if sc.get("speaker_tag"):
                                    st.markdown(f"**🗣️ Karakter / Suara:** <span style='background:{spk_bg}; padding:2px 8px; border-radius:4px; color:{spk_color}; font-weight:700; font-size:0.85rem;'>{sc['speaker_tag']}</span>", unsafe_allow_html=True)
                                st.markdown("**🎙️ Dialog Audio (Kata per Kata):**")
                                st.markdown(f"> *\"{sc['audio']}\"*")
                                if sc.get("acting_delivery"):
                                    st.markdown(f"**🎭 Panduan Akting & Delivery:** {sc['acting_delivery']}")
                                if sc.get("audience_relevance"):
                                    st.markdown(f"**🎯 Relevansi Persona Audiens:** {sc['audience_relevance']}")
                                st.markdown(f"**🎯 Catatan Pacing Editor:** {sc['notes']}")
                            with col_d2:
                                st.markdown(f"**🎥 Visual & Kamera:** {sc['visual']}")
                                st.markdown(f"**🎞️ Aset B-Roll:** {sc['b_roll']}")
                                st.markdown(f"**🔊 SFX & Transisi:** `{sc['sfx_transition']}`")

                            # Expander Prompt Khusus AI Video Generator
                            if sc.get("ai_prompt"):
                                with st.expander(f"🤖 Salin Prompt AI Video Scene #{sc['scene_num']} (Khusus Kling / Runway / Midjourney)", expanded=False):
                                    st.caption("✨ **Prompt AI Video Sutradara Pro (Hollywood/Commercial 6-Layer):** Dirancang otomatis sesuai materi & niche dengan optik sinematik, lighting sutradara, pergerakan kamera, dan fisika rendering 24fps (Bebas dari teks dialog dan status teknis):")
                                    st.code(sc["ai_prompt"], language="text")
                                    if sc.get("camera_motion") or sc.get("lens_optics"):
                                        col_c1, col_c2 = st.columns(2)
                                        with col_c1:
                                            if sc.get("camera_motion"):
                                                st.markdown(f"<span style='font-size:0.8rem; color:#475569;'>🎥 <b>Kamera:</b> {sc['camera_motion']}</span>", unsafe_allow_html=True)
                                            if sc.get("lens_optics"):
                                                st.markdown(f"<span style='font-size:0.8rem; color:#475569;'>🔍 <b>Optik:</b> {sc['lens_optics']}</span>", unsafe_allow_html=True)
                                        with col_c2:
                                            if sc.get("lighting_setup"):
                                                st.markdown(f"<span style='font-size:0.8rem; color:#475569;'>💡 <b>Lighting:</b> {sc['lighting_setup']}</span>", unsafe_allow_html=True)
                                            if sc.get("editing_style"):
                                                st.markdown(f"<span style='font-size:0.8rem; color:#475569;'>✂️ <b>Editing Cadence:</b> {sc['editing_style']}</span>", unsafe_allow_html=True)

                            with st.expander(f"📋 Salin Lembar Kerja Produksi Scene #{sc['scene_num']} (Untuk Talent & Editor CapCut)", expanded=False):
                                st.caption("🎬 **Khusus Tim Produksi:** Rangkuman naskah dialog kata per kata, arahan kamera, B-Roll, dan SFX:")
                                st.code(sc["copy_text"], language="text")

                with tab_retention_view:
                    from utils.export_helpers import calculate_retention_curve, evaluate_content_authority
                    ret_data = calculate_retention_curve(parsed_scenes)
                    auth_data = evaluate_content_authority(parsed_scenes, full_text=sb_result)

                    col_rt1, col_rt2, col_rt3 = st.columns(3)
                    with col_rt1:
                        st.metric("Skor Potensi Viral", f"{ret_data['virality_score']}/100", ret_data['retention_tier'])
                    with col_rt2:
                        st.metric("Skor Otoritas & Data", f"{auth_data['authority_score']}/100", auth_data['status'])
                    with col_rt3:
                        tot_chart_d = ret_data.get("total_duration", 60)
                        st.metric(f"Estimasi Retensi Akhir (~{tot_chart_d}s)", f"{ret_data['final_retention']}%", "Anti-Drop Pacing")

                    # Banner Audit Kedalaman & Bukti Data (Anti-AI Slop)
                    with st.container(border=True):
                        st.markdown(
                            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
                            f'<span style="font-weight:700; color:{auth_data["badge_color"]}; font-size:0.95rem;">'
                            f'🔬 Audit Kedalaman Materi: {auth_data["authority_tier"]}</span>'
                            f'<span style="background:{auth_data["badge_color"]}; color:white; padding:2px 10px; border-radius:10px; font-size:0.75rem; font-weight:700;">'
                            f'Anti-AI Slop Verified</span></div>',
                            unsafe_allow_html=True
                        )
                        
                        col_dt1, col_dt2 = st.columns(2)
                        with col_dt1:
                            st.markdown("**📊 Metrik Angka & Data Konkret Terdeteksi:**")
                            if auth_data["metrics_found"]:
                                m_badges = " ".join([f"`{m}`" for m in auth_data["metrics_found"]])
                                st.markdown(f"Ditemukan {len(auth_data['metrics_found'])} metrik terukur: {m_badges}")
                            else:
                                st.caption("Belum terdeteksi angka metrik eksplisit.")
                        
                        with col_dt2:
                            st.markdown("**⚙️ Kausalitas 'The Mechanism' & Bukti B-Roll:**")
                            c_line = f"Kausalitas: {' '.join([f'`{c}`' for c in auth_data['causality_signals']])}" if auth_data["causality_signals"] else ""
                            v_line = f"Bukti Fisik: {' '.join([f'`{v}`' for v in auth_data['visual_proof_signals']])}" if auth_data["visual_proof_signals"] else ""
                            if c_line or v_line:
                                if c_line:
                                    st.markdown(c_line)
                                if v_line:
                                    st.markdown(v_line)
                            else:
                                st.caption("Kausalitas & B-Roll deskriptif.")

                    st.markdown(f"##### 📉 Simulasi Kurva Retensi Audiens (Detik 0–{ret_data.get('total_duration', 60)})")
                    st.caption("Prediksi persentase penonton yang bertahan berdasarkan pergantian scene dan durasi:")
                    st.line_chart(ret_data["df_chart"])

                    with st.container(border=True):
                        st.markdown("**🔍 Diagnosa Retensi & Catatan Pacing Editor:**")
                        for rp in ret_data["risk_points"]:
                            st.markdown(f"- {rp}")

                with tab_table_view:
                    with st.container(border=True):
                        st.markdown(sb_result)

                with tab_tele_view:
                    st.markdown(f"**Estimasi Bicara:** ~{approx_words} kata dialog | Durasi: ~{est_sec} detik.")
                    st.markdown(
                        '<div style="background: #f8fafc; border: 1.5px solid #4f46e5; border-radius: 12px; padding: 15px; color: #0f172a; font-weight: 500;">'
                        '💡 Bacalah dialog dari scene di atas dengan pandangan mata lurus ke kamera HP.'
                        '</div>',
                        unsafe_allow_html=True
                    )

                col_prev3, col_next3 = st.columns([1, 2])
                with col_prev3:
                    if st.button("⬅️ Kembali ke Tahap 2", use_container_width=True):
                        st.session_state["pipeline_step"] = 2
                        st.rerun()
                with col_next3:
                    if st.button("➡️ Lanjut ke Tahap 4: Tambah Jembatan Monetisasi", type="primary", use_container_width=True):
                        if st.session_state.get("current_pipeline_draft_id"):
                            update_draft(st.session_state["current_pipeline_draft_id"], {
                                "storyboard_table_md": st.session_state["pipe_step3_result"],
                                "content_format": master_anchor.get("content_format") or st.session_state.get("pipe_format_val", selected_format),
                                "content_theme": master_anchor.get("content_theme") or st.session_state.get("pipe_theme_val", selected_theme),
                                "target_audience": master_anchor.get("target_audience") or st.session_state.get("pipe_aud_val", selected_audience),
                                "audience_slang": master_anchor.get("audience_tone_slang") or st.session_state.get("pipe_slang_val", selected_slang),
                                "emotional_trigger": master_anchor.get("emotional_trigger") or st.session_state.get("pipe_emotion_val", selected_emotion),
                                "environment": master_anchor.get("environment_anchor") or selected_env,
                                "color_grading": master_anchor.get("color_grading_anchor") or selected_color,
                                "voice_style": master_anchor.get("voice_profile_anchor") or selected_voice,
                                "dialogue_word_count": approx_words,
                                "est_duration_sec": est_sec,
                                "cta_goal": st.session_state.get("pipe_final_cta", "") or st.session_state.get("pipe_cta_target", ""),
                                "status": "🎙️ Siap Syuting"
                            })
                        st.session_state["pipeline_step"] = 4
                        st.rerun()

        # ---------------------------------------------------------------------
        # TAHAP 4: JEMBATAN MONETISASI (SOFT-SELLING CLOSING BRIDGE)
        # ---------------------------------------------------------------------
        elif current_step == 4:
            st.markdown("### 💰 Tahap 4: Jembatan Konversi & Penjualan Halus (*Soft Selling*)")
            st.caption("Ubah penonton menjadi pembeli tanpa terasa sedang jualan. Pilih formula transisi penutup yang paling mengalir.")

            st.markdown(
                '<div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">'
                '💡 <b>Panduan Pemula:</b> Jangan jualan kasar di awal video. Jembatan konversi (<i>Monetization Bridge</i>) adalah seni menyambungkan masalah di video dengan produk Anda secara alami di bagian penutup (contoh: <i>"Biar gak pusing bikin dari awal, template lengkapnya udah aku taruh di bio ya"</i>).'
                '</div>',
                unsafe_allow_html=True
            )

            col1, col2 = st.columns([1.1, 1], gap="medium")
            with col1:
                def _set_product_offer(val):
                    st.session_state["pipe_product_input"] = val

                st.caption("🔥 Preset Cepat Model Monetisasi (Klik untuk Memilih):")
                col_pm1, col_pm2, col_pm3 = st.columns(3)
                with col_pm1:
                    st.button("🛍️ Keranjang Kuning", key="p_m1", on_click=_set_product_offer, args=("Produk Keranjang Kuning TikTok Shop / Shopee Rekomendasi",), use_container_width=True)
                with col_pm2:
                    st.button("📚 Produk Digital", key="p_m2", on_click=_set_product_offer, args=("Template Notion + Ebook Panduan Praktis di Bio",), use_container_width=True)
                with col_pm3:
                    st.button("🎁 Lead Magnet WA", key="p_m3", on_click=_set_product_offer, args=("Checklist PDF Gratis via Link Bio Profil",), use_container_width=True)

                product_offer = st.text_input(
                    "Nama Produk / Penawaran Anda:",
                    value=st.session_state.get("pipe_product_input", ""),
                    placeholder="Contoh: Serum Anti-Acne di Keranjang Kuning / Ebook Bisnis di Link Bio...",
                    key="pipe_product_input"
                )

            with col2:
                mon_type = st.selectbox(
                    "Model Monetisasi:",
                    ["Produk Digital (Ebook/Template)", "Afiliasi (TikTok Shop / Shopee)", "Lead Magnet (Kumpul Database)", "Jasa / Freelance"],
                    key="pipe_mon_type"
                )

            btn_run_step4 = st.button("🌉 Racik 4 Formula Jembatan Konversi", type="primary", use_container_width=True)

            if btn_run_step4:
                if not product_offer.strip():
                    st.warning("⚠️ Mohon isi Nama Produk / Penawaran Anda terlebih dahulu.")
                else:
                    with st.spinner("💼 AI sedang merancang transisi penutup yang elegan dan tidak agresif..."):
                        prompt = MONETIZATION_BRIDGE_PROMPT.format(
                            topic=st.session_state.get("pipe_story_topic", "Strategi Konten"),
                            product=product_offer,
                            monetization_type=mon_type,
                            audience=st.session_state.get("pipe_audience", "Penonton umum")
                        )
                        res4 = ai_client.generate(
                            prompt=prompt,
                            system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                        )
                        st.session_state["pipe_step4_result"] = res4

            if "pipe_step4_result" in st.session_state:
                with st.container(border=True):
                    st.markdown(st.session_state["pipe_step4_result"])

                col_prev4, col_next4 = st.columns([1, 2])
                with col_prev4:
                    if st.button("⬅️ Kembali ke Tahap 3", use_container_width=True):
                        st.session_state["pipeline_step"] = 3
                        st.rerun()
                with col_next4:
                    if st.button("➡️ Lanjut ke Tahap 5: Kit Publikasi Siap Posting", type="primary", use_container_width=True):
                        if st.session_state.get("current_pipeline_draft_id"):
                            update_draft(st.session_state["current_pipeline_draft_id"], {
                                "monetization_type": mon_type,
                                "product_name": product_offer,
                                "closing_bridge_script": st.session_state["pipe_step4_result"][:800],
                                "status": "🎬 Editing CapCut"
                            })
                        st.session_state["pipeline_step"] = 5
                        st.rerun()

        # ---------------------------------------------------------------------
        # TAHAP 5: KIT PUBLIKASI SIAP POSTING & UNDUH BUNDLE (.ZIP)
        # ---------------------------------------------------------------------
        elif current_step == 5:
            st.markdown("### ✨ Tahap 5: Kit Publikasi Siap Posting (SEO & Copywriting)")
            st.caption("AI meracik caption pilihan, pertanyaan pemancing komentar (comment bait), 10 hashtag SEO, dan jam upload terbaik.")

            st.markdown(
                '<div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">'
                '💡 <b>Panduan Pemula:</b> Paket video Anda sudah 100% lengkap! Klik tombol <b>Unduh Paket Produksi Lengkap (.ZIP)</b> di bawah untuk mendapatkan skrip, subtitle CapCut, dan caption dalam 1 folder. Saat mau upload ke TikTok/Instagram, tinggal salin caption di bawah pada jam yang direkomendasikan.'
                '</div>',
                unsafe_allow_html=True
            )

            btn_run_step5 = st.button("🚀 Buat Kit Caption, Hashtag & Jam Upload Sekarang", type="primary", use_container_width=True)

            if btn_run_step5:
                with st.spinner("🤖 AI sedang meracik copywriting ramah algoritma TikTok & Reels..."):
                    prompt = CAPTION_HASHTAG_PROMPT.format(
                        topic=st.session_state.get("pipe_keyword", "Konten Edukasi"),
                        hook=st.session_state.get("pipe_chosen_hook", "Hook Pembuka"),
                        script_summary=st.session_state.get("pipe_step3_result", "")[:500]
                    )
                    res5 = ai_client.generate(
                        prompt=prompt,
                        system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                    )
                    st.session_state["pipe_step5_result"] = res5

            if "pipe_step5_result" not in st.session_state:
                st.info("💡 Klik tombol **'🚀 Buat Kit Caption, Hashtag & Jam Upload Sekarang'** di atas untuk meracik copywriting ramah algoritma dan menyelesaikan paket produksi.")

            if "pipe_step5_result" in st.session_state:
                pub_text = st.session_state["pipe_step5_result"]
                kit = extract_copywriting_kit({
                    "publication_kit_md": pub_text,
                    "keyword": st.session_state.get("pipe_keyword", "Tips Viral"),
                    "title": st.session_state.get("pipe_story_topic", "Video Edukasi"),
                    "product_name": st.session_state.get("pipe_product_input", "link di bio")
                })

                if st.session_state.get("current_pipeline_draft_id"):
                    update_draft(st.session_state["current_pipeline_draft_id"], {
                        "publication_kit_md": pub_text,
                        "caption_storytelling": kit["caption_storytelling"],
                        "caption_punchy": kit["caption_punchy"],
                        "comment_bait_question": kit["comment_bait_question"],
                        "prime_time_recommendation": kit["prime_time_recommendation"],
                        "hashtags": kit["hashtags"][:10],
                        "status": "🚀 Siap Posting"
                    })

                cap_a = kit.get("caption_storytelling", "").strip()
                cap_b = kit.get("caption_punchy", "").strip()
                cb = kit.get("comment_bait_question", "").strip()
                tags_str = kit.get("hashtags_str", "").strip()
                prime_time = kit.get("prime_time_recommendation", "").strip()

                # Buat paket posting lengkap all-in-one (Caption + Pertanyaan Interaksi + 10 Hashtag)
                full_ready_a = f"{cap_a}\n\n💬 {cb}\n\n{tags_str}"
                full_ready_b = f"{cap_b}\n\n💬 {cb}\n\n{tags_str}"

                st.markdown("#### 📋 Salin Caption Siap Posting (1-Klik Copy)")
                st.caption("Klik tombol ikon salin 📋 di pojok kanan atas kotak untuk langsung menempelkan (paste) naskah ke TikTok, Instagram Reels, atau YouTube Shorts:")

                tab_cap_a, tab_cap_b, tab_elements = st.tabs([
                    "🌟 Variasi A: Storytelling Lengkap (Siap Paste)",
                    "⚡ Variasi B: To-The-Point Agitatif (Siap Paste)",
                    "🔍 Bedah Elemen Terpisah (Caption / Comment Bait / Hashtags)"
                ])

                with tab_cap_a:
                    st.markdown("**📝 Paket Lengkap Variasi A (Caption Storytelling + Comment Bait + 10 Hashtag):**")
                    st.caption("Format terlengkap: tinggal klik ikon salin di kanan atas kotak ini dan langsung paste ke deskripsi postingan Anda:")
                    st.code(full_ready_a, language="text")

                with tab_cap_b:
                    st.markdown("**📝 Paket Lengkap Variasi B (Caption Agitatif + Comment Bait + 10 Hashtag):**")
                    st.caption("Format ringkas to-the-point: tinggal klik ikon salin di kanan atas kotak ini dan langsung paste ke deskripsi postingan Anda:")
                    st.code(full_ready_b, language="text")

                with tab_elements:
                    col_el1, col_el2 = st.columns(2)
                    with col_el1:
                        st.markdown("**💬 Pertanyaan Pemancing Komentar (Comment Bait):**")
                        st.code(cb, language="text")
                        st.markdown("**⏰ Rekomendasi Jam Tayang (Prime Time):**")
                        st.code(prime_time, language="text")
                    with col_el2:
                        st.markdown("**🏷️ 10 Hashtag SEO Algoritma:**")
                        st.code(tags_str, language="text")
                        st.markdown("**📖 Naskah Caption Murni Variasi A (Tanpa Hashtags):**")
                        st.code(cap_a, language="text")

                with st.expander("📄 Tampilkan Laporan Analisis SEO & Copywriting Utuh", expanded=False):
                    st.markdown(pub_text)

                st.markdown("---")
                st.markdown("### 📦 Paket Produksi Lengkap Selesai!")
                st.success("🎉 Seluruh data riset, skrip, dan copywriting telah tersimpan permanen di Brankas Produksi!")

                col_zip, col_studio, col_new = st.columns([1.5, 1.2, 1])

                with col_zip:
                    active_draft = get_draft(st.session_state.get("current_pipeline_draft_id", ""))
                    if active_draft:
                        zip_data = generate_draft_bundle_zip(active_draft)
                        st.download_button(
                            label="📥 Unduh Paket Produksi Lengkap (.ZIP)",
                            data=zip_data,
                            file_name=f"ViralGenix_Produksi_{active_draft.get('id', 'paket')}.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.info("Draf siap diunduh.")

                with col_studio:
                    if st.button("🗂️ Buka Papan Produksi (Kanban)", use_container_width=True):
                        st.session_state["_target_nav"] = "🗂️ Studio Produksi & Teleprompter"
                        st.session_state["active_nav"] = "🗂️ Studio Produksi & Teleprompter"
                        st.rerun()

                with col_new:
                    if st.button("➕ Buat Konten Baru", use_container_width=True):
                        st.session_state["pipeline_step"] = 1
                        st.session_state["current_pipeline_draft_id"] = None
                        if "pipe_step1_result" in st.session_state: del st.session_state["pipe_step1_result"]
                        if "pipe_step2_result" in st.session_state: del st.session_state["pipe_step2_result"]
                        if "pipe_step3_result" in st.session_state: del st.session_state["pipe_step3_result"]
                        if "pipe_step4_result" in st.session_state: del st.session_state["pipe_step4_result"]
                        if "pipe_step5_result" in st.session_state: del st.session_state["pipe_step5_result"]
                        st.rerun()

    # =========================================================================
    # TAB 2: MODE SPRINT KONTEN 7 HARI (BATCH 1 MINGGU PENUH)
    # =========================================================================
    with tab_batch:
        st.markdown("### 🚀 Sprint Konten 7 Hari: Rancang 1 Minggu Sekaligus")
        st.caption("Khusus untuk kreator yang ingin menyelesaikan seluruh stok video dari Senin sampai Minggu dalam satu kali klik.")

        st.markdown(
            '<div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">'
            '💡 <b>Cara Kerja Mode Sprint:</b> Cukup masukkan 1 niche dan topik utama. AI akan menyusun strategi 7 pilar konten mingguan (Mitos, Tutorial, Kisah Nyata, Blunder Fatal, Tools Rahasia, Debat Interaktif, dan Reset Mingguan). Setelah selesai, Anda bisa mengimpor ketujuh video tersebut ke Studio Produksi dengan 1 klik!'
            '</div>',
            unsafe_allow_html=True
        )

        col_b1, col_b2 = st.columns([1.2, 1], gap="medium")
        with col_b1:
            batch_niche = st.selectbox(
                "Pilih Kategori Niche:",
                COMPREHENSIVE_NICHES,
                index=0,
                key="batch_niche_select"
            )
            custom_batch_niche = ""
            if "Custom Niche" in batch_niche:
                custom_batch_niche = st.text_input(
                    "Ketik Niche Spesifik Anda:",
                    placeholder="Contoh: Katering Bento Anak / Tanaman Hias Bonsai",
                    key="batch_custom_niche"
                )
            batch_topic = st.text_input(
                "Topik Utama / Fokus Minggu Ini:",
                value=st.session_state.get("batch_topic_input", ""),
                placeholder="Contoh: Strategi Affiliate TikTok Shop Modal HP untuk Pemula",
                key="batch_topic_input"
            )

        with col_b2:
            batch_audience = st.text_input(
                "Target Audiens:",
                value=st.session_state.get("batch_audience_input", ""),
                placeholder="Contoh: Pekerja kantoran 20-35 th / Pemula yang butuh penghasilan tambahan",
                key="batch_audience_input"
            )
            batch_product = st.text_input(
                "Produk / CTA Penawaran Utama:",
                value=st.session_state.get("batch_product_input", ""),
                placeholder="Contoh: Rekomendasi barang unik di Keranjang Kuning / Ebook di Bio",
                key="batch_product_input"
            )

        # Inisialisasi Niche Bersih untuk Seluruh Scope Tab Batch
        final_bniche = get_clean_niche(batch_niche, custom_batch_niche)

        if st.button("🚀 Hasilkan Kalender & Skrip 7 Hari Sekaligus", type="primary", use_container_width=True, key="btn_run_sprint"):
            if not final_bniche:
                st.warning("⚠️ Mohon pilih Kategori Niche terlebih dahulu sebelum memulai Sprint 7 Hari.")
            elif not batch_topic.strip():
                st.warning("⚠️ Mohon isi Topik Utama / Fokus Minggu Ini.")
            elif not batch_audience.strip():
                st.warning("⚠️ Mohon isi Target Audiens.")
            elif not batch_product.strip():
                st.warning("⚠️ Mohon isi Produk / CTA Penawaran Utama.")
            else:
                with st.spinner("🤖 AI sedang merancang strategi 7 pilar, hook, skrip, dan caption untuk Senin s/d Minggu..."):
                    prompt = SEVEN_DAY_SPRINT_PROMPT.format(
                        niche=final_bniche,
                        topic=batch_topic,
                        audience=batch_audience,
                        product=batch_product
                    )
                    res_sprint = ai_client.generate(
                        prompt=prompt,
                        system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                    )
                    st.session_state["sprint_result"] = res_sprint
                    st.session_state["sprint_niche"] = final_bniche
                    st.session_state["sprint_topic"] = batch_topic
                    st.session_state["sprint_audience"] = batch_audience
                    st.session_state["sprint_product"] = batch_product

        if "sprint_result" in st.session_state:
            with st.container(border=True):
                st.markdown(st.session_state["sprint_result"])

            col_sp_act1, col_sp_act2, col_sp_act3 = st.columns([1.5, 1, 0.8])
            with col_sp_act1:
                if st.button("📥 Impor Semua 7 Video ke Studio Produksi (Kanban)", type="primary", use_container_width=True):
                    text = st.session_state["sprint_result"]
                    day_blocks = re.split(r'###\s*HARI\s*\[?\d+\]?[\:\-\.\s]', text, flags=re.IGNORECASE)[1:]
                    
                    if not day_blocks or len(day_blocks) < 2:
                        day_blocks = [b.strip() for b in text.split("---") if "Hook 3 Detik" in b or "Pilar" in b]

                    imported_count = 0
                    day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

                    active_sprint_niche = st.session_state.get("sprint_niche") or final_bniche or batch_niche
                    active_sprint_topic = st.session_state.get("sprint_topic") or batch_topic
                    active_sprint_aud = st.session_state.get("sprint_audience") or batch_audience
                    active_sprint_prod = st.session_state.get("sprint_product") or batch_product

                    for idx, block in enumerate(day_blocks[:7]):
                        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
                        title_line = lines[0].replace("-", "").strip() if lines else f"Video Hari {idx+1}"
                        
                        # Ekstraksi cerdas elemen
                        hook_match = re.search(r'Hook 3 Detik.*?:\s*(?:_|\*|")?([^"\*\_\n]+)', block, re.IGNORECASE)
                        hook_val = hook_match.group(1).strip() if hook_match else f"Hook video hari {idx+1}"

                        mock_d = {
                            "title": title_line,
                            "keyword": active_sprint_topic,
                            "niche": active_sprint_niche,
                            "product_name": active_sprint_prod,
                            "storyboard_table_md": block,
                            "hook_verbal": hook_val
                        }
                        kit = extract_copywriting_kit(mock_d)
                        bridge = extract_closing_bridge(mock_d)

                        create_draft({
                            "title": f"[{day_names[idx] if idx < 7 else f'Hari {idx+1}'}] {title_line[:40]}",
                            "niche": active_sprint_niche,
                            "keyword": active_sprint_topic,
                            "platform": "TikTok / Reels",
                            "target_audience": active_sprint_aud,
                            "content_angle": title_line,
                            "hook_verbal": hook_val,
                            "storyboard_table_md": block,
                            "product_name": active_sprint_prod,
                            "closing_bridge_script": bridge,
                            "caption_storytelling": kit["caption_storytelling"],
                            "caption_punchy": kit["caption_punchy"],
                            "comment_bait_question": kit["comment_bait_question"],
                            "prime_time_recommendation": kit["prime_time_recommendation"],
                            "hashtags": kit["hashtags"][:10],
                            "publication_kit_md": kit["publication_kit_md"],
                            "status": "📝 Skrip Selesai"
                        })
                        imported_count += 1

                    st.success(f"🎉 Berhasil mengimpor {imported_count} video ke Studio Produksi!")
                    st.session_state["_target_nav"] = "🗂️ Studio Produksi & Teleprompter"
                    st.session_state["active_nav"] = "🗂️ Studio Produksi & Teleprompter"
                    st.rerun()

            with col_sp_act2:
                sp_md = prepare_markdown_download(st.session_state["sprint_result"], "kalender_konten_7_hari")
                st.download_button(
                    label="📥 Unduh Kalender (.MD)",
                    data=sp_md,
                    file_name="ViralGenix_Sprint_7_Hari.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col_sp_act3:
                if st.button("🗑️ Bersihkan", key="btn_clear_sprint", use_container_width=True):
                    del st.session_state["sprint_result"]
                    st.rerun()
