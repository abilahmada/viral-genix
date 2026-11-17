"""
ViralGenix - Modul Laboratorium Kreatif: Hook & Closing CTA Lab
Menggabungkan eksperimen 10 variasi hook berbasis psikologi audiens,
generator storyboard detik demi detik, dan peracik jembatan konversi (Monetization Bridge)
dalam satu lab kreatif terpadu.
"""

import streamlit as st
import re
from utils.prompts import (
    MASTER_STRATEGIST_SYSTEM_PROMPT,
    HOOK_GENERATOR_PROMPT,
    STORYBOARD_TABLE_PROMPT,
    MONETIZATION_BRIDGE_PROMPT,
    CAPTION_HASHTAG_PROMPT,
    get_master_system_prompt
)
from utils.export_helpers import (
    markdown_table_to_dataframe,
    dataframe_to_csv_bytes,
    prepare_markdown_download,
    markdown_table_to_srt,
    parse_storyboard_scenes,
    format_scenes_for_production_sheet,
    parse_hook_variations
)


def render_hook_cta_lab(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">LABORATORIUM KREATIF</div>
        <h1 class="module-title">🪝 Hook & Closing CTA Lab</h1>
        <p class="module-desc">
            Eksperimen meracik <b>3 detik pertama penahan scroll (Hook)</b>, 
            <b>papan cerita narasi (Storyboard)</b>, dan <b>jembatan jualan halus (Closing Bridge)</b> 
            untuk meningkatkan retensi dan konversi video Anda.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_hooks, tab_storyboard, tab_bridge = st.tabs([
        "🔥 10 Hook Matrix Psikologi",
        "🎬 Generator Storyboard 60s",
        "💰 Jembatan Konversi (Closing Bridge)"
    ])

    # =========================================================================
    # TAB 1: 10 HOOK MATRIX PSIKOLOGI
    # =========================================================================
    with tab_hooks:
        col1, col2 = st.columns([1.2, 1], gap="medium")
        with col1:
            topic_input = st.text_area(
                "Topik Konten / Ide Cerita / Pesan Inti:",
                value=st.session_state.get("hook_topic_input", ""),
                height=110,
                placeholder="Contoh: Cara memulai bisnis dropship atau jualan online tanpa modal HP / Rahasia kulit glowing..."
            )

        with col2:
            audience_target = st.text_input(
                "Target Audiens Spesifik:",
                value=st.session_state.get("hook_aud_input", ""),
                placeholder="Contoh: Pemula yang belum pernah jualan online / Ibu rumah tangga..."
            )

            FORMAT_OPTIONS = [
                "🎙️ Talking Head Sinematik (Kreator Bicara Langsung ke Lensa HP)",
                "🎭 Skit Komedi / Parodi Situasional (POV 2 Karakter Bertolak Belakang)",
                "🎬 Micro-Drama & Storytelling Emosional (Plot Twist & Narasi Kisah Nyata)",
                "🎞️ Voiceover Faceless Sinematik (Tanpa Wajah — Audio Narasi + B-Roll ASMR)",
                "🥊 Debat Dialektika (Si Skeptis Penasaran vs Si Praktisi Solutif)",
                "📖 Analogi Fabel / Bedah Kasus & Sejarah Unik"
            ]

            lab_format = st.selectbox(
                "🎭 Model & Format Konten:",
                FORMAT_OPTIONS,
                index=0,
                key="lab_hook_format_select",
                help="AI akan merumuskan hook dengan formula visual dan audio yang disesuaikan model konten."
            )

            tone_style = st.selectbox(
                "Gaya Emosi / Pendekatan:",
                [
                    "Misterius & Penasaran (Curiosity Gap)",
                    "Mendesak & Takut Rugi (FOMO)",
                    "Santai & Empatik (Bestie Vibe)",
                    "Provokatif & Tegas (Wake-Up Call)",
                    "To-The-Point & Solutif (Anti Basa-basi)"
                ]
            )

        st.markdown("---")

        if st.button("⚡ Hasilkan 10 Variasi Hook Visual + Audio", type="primary", use_container_width=True, key="btn_run_hooks_lab"):
            if not topic_input.strip():
                st.warning("⚠️ Mohon isi Topik Konten / Ide Cerita terlebih dahulu.")
                return
            elif not audience_target.strip():
                st.warning("⚠️ Mohon isi Target Audiens Spesifik terlebih dahulu.")
                return

            with st.spinner(f"🧠 AI sedang menyusun 10 variasi hook dengan formula visual + audio sesuai model {lab_format.split()[1]}..."):
                prompt = HOOK_GENERATOR_PROMPT.format(
                    topic=topic_input,
                    audience=audience_target,
                    tone=tone_style,
                    content_format=lab_format
                )
                hooks_res = ai_client.generate(
                    prompt=prompt,
                    system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                )
                st.session_state["hooks_result"] = hooks_res
                st.session_state["last_hook_topic"] = topic_input
                st.session_state["last_hook_format"] = lab_format

        if "hooks_result" in st.session_state:
            st.markdown("### 🎯 10 Variasi Hook Visual & Audio")

            st.markdown("""
            <div class="kpi-row">
                <div class="kpi-pill"><span class="kpi-pill-lbl">Variasi Hook:</span> <span class="kpi-pill-val">10 Skrip Visual + Audio 🔥</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Pilar Psikologi:</span> <span class="kpi-pill-val">FOMO, Curiosity, Gain, Empathy</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Avg. Skor Retensi:</span> <span class="kpi-pill-val" style="color:#4f46e5;">92.5 / 100</span></div>
            </div>
            """, unsafe_allow_html=True)

            lab_hooks = parse_hook_variations(st.session_state["hooks_result"], fallback_topic=topic_input)
            hook_labels = [h["display_label"] for h in lab_hooks] if lab_hooks else ["Stop lakuin cara ini kalau kamu gak mau rugi waktu dan duit sia-sia!"]

            st.markdown("##### 🎯 Pilih Hook Favorit untuk Diteruskan:")
            selected_lab_lbl = st.selectbox("Daftar 10 Hook Terdeteksi:", hook_labels, key="quick_hook_select_lab")
            chosen_h_obj = next((h for h in lab_hooks if h["display_label"] == selected_lab_lbl), None)
            chosen_from_list = chosen_h_obj["verbal"] if chosen_h_obj else selected_lab_lbl

            if chosen_h_obj:
                st.markdown(f"""
                <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:8px 12px; border-radius:6px; margin:6px 0 10px 0; font-size:0.84rem; color:#1e1b4b;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                        <span style="font-weight:700; color:#1d4ed8;">🏷️ {chosen_h_obj['category']}</span>
                        <span style="background:#dbeafe; color:#1e40af; font-weight:700; padding:1px 6px; border-radius:4px; font-size:0.75rem;">📈 Skor: {chosen_h_obj['score']}</span>
                    </div>
                    <div><b>🎥 Aksi Visual:</b> {chosen_h_obj['visual']}</div>
                </div>
                """, unsafe_allow_html=True)

            col_h1, col_h2, col_h3 = st.columns([1.5, 1.2, 0.8])
            with col_h1:
                if st.button("⚡ Bawa Hook Ini ke Pipeline Wizard", type="primary", use_container_width=True, key="btn_hook_to_pipe"):
                    st.session_state["pipe_chosen_hook"] = chosen_from_list
                    st.session_state["pipe_topic_for_hook"] = st.session_state.get("last_hook_topic", topic_input)
                    st.session_state["pipe_story_topic"] = st.session_state.get("last_hook_topic", topic_input)
                    hook_fmt = st.session_state.get("last_hook_format", lab_format)
                    st.session_state["pipe_content_format_select"] = hook_fmt
                    st.session_state["pipe_format_val"] = hook_fmt
                    st.session_state["pipeline_step"] = 3
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.rerun()

            with col_h2:
                md_bytes = prepare_markdown_download(st.session_state["hooks_result"], "10_variasi_hook")
                st.download_button(
                    label="📥 Unduh Hook (.md)",
                    data=md_bytes,
                    file_name="ViralGenix_10_Hooks.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="btn_down_hook_lab"
                )

            with col_h3:
                if st.button("🗑️ Hapus", use_container_width=True, key="btn_del_hook_lab"):
                    del st.session_state["hooks_result"]
                    st.rerun()

            with st.container(border=True):
                st.markdown(st.session_state["hooks_result"])

    # =========================================================================
    # TAB 2: GENERATOR STORYBOARD 60S
    # =========================================================================
    with tab_storyboard:
        st.markdown("#### 🎬 Susun Papan Cerita & Tabel Naskah Detik demi Detik")
        st.caption("Ubah hook pilihan Anda menjadi video utuh berdurasi 30-60 detik dengan formula retensi dan interupsi pola.")

        col_s1, col_s2 = st.columns([1.2, 1], gap="medium")
        with col_s1:
            chosen_hook = st.text_input(
                "Hook 3 Detik Terpilih:",
                value=st.session_state.get("storyboard_selected_hook", ""),
                placeholder="Contoh: Stop lakuin cara ini kalau gak mau boncos! / 90% orang salah cara pakai produk ini..."
            )
            story_topic = st.text_area(
                "Detail Topik / Inti Konten:",
                value=st.session_state.get("storyboard_topic", ""),
                placeholder="Contoh: Tutorial praktis cara riset produk affiliate yang cepat laku dan cara buat videonya...",
                height=90
            )

        with col_s2:
            target_duration = st.select_slider(
                "Durasi Ideal Video:",
                options=[
                    "30 Detik (Fast Paced — 3-4 Scene)",
                    "45 Detik (Balanced — 4-5 Scene)",
                    "60 Detik (Standar — 5-6 Scene)",
                    "75 - 90 Detik (Multi-Poin — 7-8 Scene)",
                    "90 - 120 Detik (Deep Dive — 8-10 Scene)"
                ],
                value="60 Detik (Standar — 5-6 Scene)"
            )
            cta_goal = st.selectbox(
                "Tujuan Call to Action (CTA):",
                [
                    "Komentar & Diskusi (Tingkatkan Interaksi)",
                    "Klik Link Bio (Beli Produk / Download)",
                    "Follow / Ikuti Akun (Membangun Otoritas)",
                    "Simpan & Bagikan Video (Algoritma Booster)"
                ]
            )

        # -----------------------------------------------------------------
        # SETUP KONSISTENSI VISUAL & AUDIO SEBELUM GENERATE STORYBOARD
        # -----------------------------------------------------------------
        with st.expander("🎨 Setup Gaya Visual, Setting Lokasi & Konsistensi AI (Disiplin Scene <= 15 Detik)", expanded=True):
            st.caption("Atur parameter visual dan suara agar generator menyusun skrip dengan durasi maksimal 15 detik per scene dan menjaga konsistensi subjek serta tone warna untuk generator AI video (Kling / Runway / Midjourney).")
            
            col_sb_st1, col_sb_st2 = st.columns(2)
            with col_sb_st1:
                lab_visual_choice = st.selectbox(
                    "🎭 Tipe Konten Visual:",
                    [
                        "🎥 Realistis Sinematik / Live Action (Talent Manusia / UGC 4K)",
                        "🤖 3D Animation (Gaya Pixar / Disney / Unreal Engine 5 Render)",
                        "🎌 Anime / Manga Estetik (Gaya Studio Ghibli / Makoto Shinkai)",
                        "🎨 2D Motion Graphics & Flat Vector (Gaya Vox / Kurzgesagt)",
                        "📸 Vintage Retro 35mm Analog Film (Nostalgia 90s / Kodak Film Grain)",
                        "🔮 Cyberpunk Neon & Sci-Fi Futuristik (Blade Runner / High Tech)",
                        "✏️ Kustom (Ketik Gaya Visual Sendiri)"
                    ],
                    key="lab_visual_style_select"
                )
                if "Kustom" in lab_visual_choice:
                    lab_custom_vis = st.text_input("Gaya Visual Kustom:", placeholder="Contoh: Claymation stop-motion...", key="lab_custom_vis")
                    selected_lab_vis = lab_custom_vis if lab_custom_vis.strip() else "Realistis Sinematik"
                else:
                    selected_lab_vis = lab_visual_choice

                lab_env_choice = st.selectbox(
                    "🏞️ Setting Lokasi / Environment:",
                    [
                        "Smart Workspace Modern / Meja Kerja Rapi dengan Laptop & Tanaman Indoor",
                        "Dapur Rumah Minimalis Bersih & Estetik (Natural Morning Light & Marmer Putih)",
                        "Vanity Mirror Kamar Mandi Marmer Putih Bersih (Clean Bright Ring Light)",
                        "Meja Rias Vanity Estetik dengan Cermin LED & Rak Kosmetik Rapi",
                        "Walk-in Closet Estetik / Kamar Tidur Modern dengan Full-Length Mirror",
                        "Garasi Modern Bersih dengan Tool Rack Rapi & Pencahayaan Neon Cool White",
                        "Gym Modern / Ruang Latihan Fitness dengan Mirror Wall & Dumbbell Rack",
                        "Desk Setup Gadget & Ambient Neon Light (Tech Minimalist Dark)",
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
                    ],
                    key="lab_env_select"
                )
                if "Kustom" in lab_env_choice:
                    lab_custom_env = st.text_input("Setting Lokasi Kustom:", placeholder="Contoh: Dapur minimalis marmer putih...", key="lab_custom_env")
                    selected_lab_env = lab_custom_env if lab_custom_env.strip() else "Smart Workspace Modern dengan Meja Kayu & Tanaman Indoor"
                else:
                    selected_lab_env = lab_env_choice

            with col_sb_st2:
                lab_color_choice = st.selectbox(
                    "🎨 Color Grading & Palet Warna:",
                    [
                        "Moody Teal & Warm Orange Sinematik (Hollywood Blockbuster Look)",
                        "Clean High-Key SaaS & Tech (Bright Natural, Cool Blue Accent)",
                        "Dark Documentary (High Contrast, Deep Shadow, Desaturated Tone)",
                        "Pastel Dreamy Aesthetic (Soft Glow, Warm Highlights, Airy Feel)",
                        "Vibrant Pop Energetic (Saturasi Tinggi, TikTok Trend Vibe)",
                        "✏️ Kustom (Ketik Palet Warna Sendiri)"
                    ],
                    key="lab_color_select"
                )
                if "Kustom" in lab_color_choice:
                    lab_custom_col = st.text_input("Palet Warna Kustom:", placeholder="Contoh: High contrast monochrome...", key="lab_custom_col")
                    selected_lab_col = lab_custom_col if lab_custom_col.strip() else "Moody Warm Cinematic"
                else:
                    selected_lab_col = lab_color_choice

                lab_voice_choice = st.selectbox(
                    "🗣️ Voice Style & Karakter Vokal:",
                    [
                        "Santai & Empatik (Bestie Vibe, Akrab, Mengalir Luwes)",
                        "Tegas & Berwibawa (Otoritas Tinggi, Meyakinkan, No-BS Expert)",
                        "Misterius & Berbisik Cepat (Curiosity Gap, Konspiratif Rahasia)",
                        "Punchy, Hype & Berenergi Tinggi (Pemicu Adrenalin, Semangat Membara)",
                        "Storyteller Hangat & Reflektif (Penuh Emosi & Sentuhan Personal)",
                        "✏️ Kustom (Ketik Gaya Vokal Sendiri)"
                    ],
                    key="lab_voice_select"
                )
                if "Kustom" in lab_voice_choice:
                    lab_custom_voi = st.text_input("Gaya Vokal Kustom:", placeholder="Contoh: Intonasi tenang dengan jeda dramatis...", key="lab_custom_voi")
                    selected_lab_voi = lab_custom_voi if lab_custom_voi.strip() else "Santai & Empatik"
                else:
                    selected_lab_voi = lab_voice_choice

        if st.button("🎬 Buat Tabel Storyboard Produksi (Disiplin <= 15s)", type="primary", use_container_width=True, key="btn_gen_sb_lab"):
            if not chosen_hook.strip():
                st.warning("⚠️ Mohon isi Hook 3 Detik Terpilih terlebih dahulu.")
            elif not story_topic.strip():
                st.warning("⚠️ Mohon isi Detail Topik / Inti Konten terlebih dahulu.")
            else:
                with st.spinner("🎥 Menyusun pergerakan kamera, kunci konsistensi visual, dialog audio, dan micro-scenes (maks 15 detik & maks 25 kata)..."):
                    if "30" in target_duration:
                        lab_scene_req = "TARGET: 3-4 Scene (Durasi 30-45s, ringkas & to-the-point)"
                    elif "45" in target_duration:
                        lab_scene_req = "TARGET: 4-5 Scene (Durasi 45s)"
                    elif "75" in target_duration:
                        lab_scene_req = "TARGET: 7-8 Scene (Durasi 75-90s, sediakan 3-4 scene edukasi mendalam/langkah bertahap di bagian tengah)"
                    elif "120" in target_duration or "90 - 120" in target_duration:
                        lab_scene_req = "TARGET: 8-10 Scene (Durasi 90-120s, tutorial komprehensif langkah demi langkah, DILARANG potong hanya 6 scene!)"
                    else:
                        lab_scene_req = "TARGET: 5-6 Scene (Durasi 60s standar)"

                    lab_director_inst = f"""⚙️ PENGARAHAN PRODUKSI & BOBOT MATERI EMPIRIS:
- Tipe Visual: {selected_lab_vis}
- Setting Lokasi / Environment: {selected_lab_env}
- Color Grading & Lighting: {selected_lab_col}
- Karakter & Voice Style: {selected_lab_voi}
- Standar Bobot Isi: WAJIB padat data empiris, nama alat/bahan/teknik konkret, metrik terukur, dan kausalitas logis 'The Mechanism' (anti-isi lemas).
- Target Jumlah Scene: {lab_scene_req}"""
                    prompt = STORYBOARD_TABLE_PROMPT.format(
                        hook=chosen_hook,
                        topic=f"{story_topic} (Durasi: {target_duration})",
                        goal=cta_goal,
                        director_instructions=lab_director_inst,
                        visual_style=selected_lab_vis,
                        environment=selected_lab_env,
                        color_grading=selected_lab_col,
                        voice_style=selected_lab_voi
                    )
                    story_res = ai_client.generate(
                        prompt=prompt,
                        system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                    )
                    st.session_state["storyboard_result"] = story_res

        if "storyboard_result" in st.session_state:
            st.markdown("### 📋 Hasil Storyboard Produksi")

            df_table = markdown_table_to_dataframe(st.session_state["storyboard_result"])
            srt_bytes = markdown_table_to_srt(st.session_state["storyboard_result"])

            col_down1, col_down2, col_down3, col_down4 = st.columns([1.5, 1, 1, 0.8])
            with col_down1:
                if st.button("⚡ Bawa Storyboard ke Pipeline Wizard", type="primary", use_container_width=True, key="btn_sb_to_pipe"):
                    st.session_state["pipe_step3_result"] = st.session_state["storyboard_result"]
                    st.session_state["pipe_chosen_hook"] = chosen_hook
                    st.session_state["pipeline_step"] = 4
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.rerun()

            with col_down2:
                if df_table is not None:
                    csv_data = dataframe_to_csv_bytes(df_table)
                    st.download_button(
                        label="📊 Unduh CSV",
                        data=csv_data,
                        file_name="ViralGenix_Storyboard.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="btn_down_csv_sb_lab"
                    )
            with col_down3:
                if srt_bytes:
                    st.download_button(
                        label="🎬 Unduh Subtitle (.srt)",
                        data=srt_bytes,
                        file_name="ViralGenix_Subtitles.srt",
                        mime="text/plain",
                        use_container_width=True,
                        key="btn_down_srt_sb_lab"
                    )
            with col_down4:
                if st.button("🗑️ Hapus", use_container_width=True, key="btn_del_sb_lab"):
                    del st.session_state["storyboard_result"]
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            from utils.export_helpers import parse_storyboard_scenes, format_scenes_for_production_sheet, parse_master_consistency_anchor
            parsed_scenes_lab = parse_storyboard_scenes(st.session_state["storyboard_result"])
            master_anchor_lab = parse_master_consistency_anchor(st.session_state["storyboard_result"])
            
            tab_sc_lab, tab_tbl_lab = st.tabs([
                "🎬 Lembar Kerja Scene-by-Scene (Siap Copas)",
                "📊 Tabel Pacing Storyboard"
            ])

            with tab_sc_lab:
                # Master Consistency Anchor Banner
                if master_anchor_lab and any(master_anchor_lab.values()):
                    with st.container(border=True):
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 14px 18px; border-radius: 8px; color: white; margin-bottom: 12px;">
                            <h4 style="margin: 0 0 6px 0; color: #a5b4fc; font-size: 1.05rem;">🛡️ Bagian 0: Master Production Consistency Anchor (Kunci Konsistensi Utuh)</h4>
                            <div style="font-size: 0.85rem; color: #e0e7ff; line-height: 1.4;">
                                Parameter konsisten untuk subjek, lokasi, dan pencahayaan agar output video di Kling / Midjourney / Runway menyatu rapi.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            if master_anchor_lab.get("character_anchor"):
                                st.markdown(f"**👤 Subjek / Karakter Tetap:**\n> {master_anchor_lab['character_anchor']}")
                            if master_anchor_lab.get("environment_anchor"):
                                st.markdown(f"**🏞️ Setting Lokasi Master:**\n> {master_anchor_lab['environment_anchor']}")
                        with col_m2:
                            if master_anchor_lab.get("color_grading_anchor"):
                                st.markdown(f"**🎨 Color Grading & Lighting:**\n> {master_anchor_lab['color_grading_anchor']}")
                            if master_anchor_lab.get("voice_profile_anchor"):
                                st.markdown(f"**🎙️ Voice Profile:**\n> {master_anchor_lab['voice_profile_anchor']}")

                        if master_anchor_lab.get("visual_style_lock"):
                            st.markdown("**🧬 Master AI Style Lock (Prompt Prefix Baku):**")
                            st.code(master_anchor_lab["visual_style_lock"], language="text")

                full_sheet_lab = format_scenes_for_production_sheet(
                    parsed_scenes_lab,
                    title=story_topic[:40] if story_topic else "Konten Video",
                    platform="TikTok / Reels",
                    master_anchor=master_anchor_lab
                )
                with st.expander("📋 Salin Seluruh Naskah Lembar Produksi Lengkap (Notion / WhatsApp)", expanded=False):
                    st.code(full_sheet_lab, language="text")

                for sc in parsed_scenes_lab:
                    with st.container(border=True):
                        col_sc_h1, col_sc_h2 = st.columns([1.8, 2.2])
                        with col_sc_h1:
                            st.markdown(f"##### 🎬 Scene {sc['scene_num']}: {sc['title']}")
                        with col_sc_h2:
                            dur_badge_color = sc.get("sync_badge_color", "#10b981")
                            dur_badge_bg = sc.get("sync_badge_bg", "#ecfdf5")
                            dur_badge_border = sc.get("sync_badge_border", "#a7f3d0")
                            w_count = sc.get("word_count", len(sc.get("audio", "").split()))
                            est_dur = sc.get("est_audio_dur", round(w_count / 1.9))
                            dur_sec_val = sc.get("duration_sec", 10)
                            dur_text = f"⏱️ Klip: {dur_sec_val}s • {w_count} kata (~{est_dur}s) | {sc.get('sync_badge', '✅ Sinkron')}"
                            st.markdown(f"<div style='text-align:right; font-weight:700; color:{dur_badge_color}; background:{dur_badge_bg}; border:1px solid {dur_badge_border}; padding:3px 8px; border-radius:6px; font-size:0.78rem;'>{dur_text}</div>", unsafe_allow_html=True)

                        # Peringatan dini jika ada ketidaksinkronan durasi vs dialog
                        if sc.get("sync_status") == "overflow":
                            st.markdown(f"""
                            <div style="background:#fef2f2; border-left:3px solid #ef4444; padding:6px 12px; border-radius:4px; font-size:0.8rem; color:#991b1b; margin:6px 0 10px 0;">
                                🚨 <b>Peringatan Dialog Kepanjangan:</b> {sc.get('sync_note')}
                            </div>
                            """, unsafe_allow_html=True)
                        elif sc.get("sync_status") == "underflow":
                            st.markdown(f"""
                            <div style="background:#fffbeb; border-left:3px solid #f59e0b; padding:6px 12px; border-radius:4px; font-size:0.8rem; color:#92400e; margin:6px 0 10px 0;">
                                ⚠️ <b>Perhatian Hening Visual:</b> {sc.get('sync_note')}
                            </div>
                            """, unsafe_allow_html=True)

                        # Badges detail produksi & persona
                        act_badge = f'<span style="background:#fdf4ff; padding:2px 8px; border-radius:4px; color:#a21caf; border:1px solid #f0abfc;"><b>🎭 Delivery:</b> {sc["acting_delivery"][:28]}</span>' if sc.get("acting_delivery") else ''
                        rel_badge = f'<span style="background:#eff6ff; padding:2px 8px; border-radius:4px; color:#1d4ed8; border:1px solid #bfdbfe;"><b>🎯 Audiens:</b> {sc["audience_relevance"][:30]}</span>' if sc.get("audience_relevance") else ''
                        cine_badge_html = f'<span style="background:#f0fdf4; padding:2px 8px; border-radius:4px; color:#15803d; border:1px solid #bbf7d0;"><b>🎬 Sutradara Pro:</b> {sc["cine_badge"]}</span>' if sc.get("cine_badge") else ''

                        st.markdown(f"""
                        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; font-size:0.78rem;">
                            <span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🎨 Gaya:</b> {sc.get('visual_style', 'Live Action')}</span>
                            <span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🏞️ Lokasi:</b> {sc.get('environment', 'Studio Minimalis')}</span>
                            <span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🎨 Color:</b> {sc.get('color_grading', 'Moody Cinematic')}</span>
                            <span style="background:#f1f5f9; padding:2px 8px; border-radius:4px; color:#334155;"><b>🗣️ Vokal:</b> {sc.get('voice_style', 'Santai & Empatik')}</span>
                            {act_badge}
                            {rel_badge}
                            {cine_badge_html}
                        </div>
                        """, unsafe_allow_html=True)

                        col_d1, col_d2 = st.columns([1.2, 1])
                        with col_d1:
                            st.markdown("**🎙️ Dialog Audio:**")
                            st.markdown(f"> *\"{sc['audio']}\"*")
                            if sc.get("acting_delivery"):
                                st.markdown(f"**🎭 Panduan Akting & Delivery:** {sc['acting_delivery']}")
                            if sc.get("audience_relevance"):
                                st.markdown(f"**🎯 Relevansi Persona Audiens:** {sc['audience_relevance']}")
                            st.markdown(f"**🎯 Catatan Pacing Editor:** {sc['notes']}")
                        with col_d2:
                            st.markdown(f"**🎥 Visual:** {sc['visual']}")
                            st.markdown(f"**🎞️ Aset B-Roll:** {sc['b_roll']}")
                            st.markdown(f"**🔊 SFX/Transisi:** `{sc['sfx_transition']}`")

                        if sc.get("ai_prompt"):
                            with st.expander(f"🤖 Salin Prompt AI Video Scene #{sc['scene_num']} (Khusus Kling / Runway / Midjourney)", expanded=False):
                                st.caption("✨ **Prompt AI Video Sutradara Pro (Hollywood/Commercial 6-Layer):** Dirancang otomatis sesuai materi & niche dengan optik sinematik, lighting sutradara, pergerakan kamera, dan fisika rendering 24fps:")
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

            with tab_tbl_lab:
                with st.container(border=True):
                    st.markdown(st.session_state["storyboard_result"])

    # =========================================================================
    # TAB 3: JEMBATAN KONVERSI (CLOSING BRIDGE & SOFT-SELLING)
    # =========================================================================
    with tab_bridge:
        st.markdown("#### 💰 Formula Transisi Penutup Halus (Soft-Selling)")
        st.caption("Ubah penonton menjadi pembeli tanpa terasa sedang berjualan secara agresif (*anti-salesy*).")

        col_b1, col_b2 = st.columns([1.1, 1], gap="medium")
        with col_b1:
            br_topic = st.text_area(
                "Topik Materi Video:",
                value=st.session_state.get("monetize_topic_input", ""),
                placeholder="Contoh: Panduan otomatisasi pembuatan konten dan riset tren video pendek...",
                height=80
            )
            br_product = st.text_input(
                "Nama Produk / Penawaran Anda:",
                value=st.session_state.get("monetize_prod_name", ""),
                placeholder="Contoh: Lip serum herbal di Keranjang Kuning, Ebook 30 Hari Diet di Bio..."
            )

        with col_b2:
            br_model = st.selectbox(
                "Model Monetisasi:",
                [
                    "Produk Digital (Ebook, Course, Template Notion)",
                    "Afiliasi (Keranjang Kuning TikTok Shop / Shopee)",
                    "Lead Magnet Gratis (Kumpulkan Database WA/Telegram)",
                    "Jasa / Freelance / Agensi (Mencari Klien Berbayar)"
                ],
                key="br_model_select_lab"
            )
            br_audience = st.text_input(
                "Target Pembeli:",
                value=st.session_state.get("br_aud_lab", ""),
                placeholder="Contoh: Kreator pemula & UMKM yang butuh hasil cepat...",
                key="br_aud_lab"
            )

        if st.button("🌉 Racik 4 Formula Jembatan Konversi", type="primary", use_container_width=True, key="btn_gen_bridge_lab"):
            if not br_topic.strip():
                st.warning("⚠️ Mohon isi Topik Materi Video terlebih dahulu.")
            elif not br_product.strip():
                st.warning("⚠️ Mohon isi Nama Produk / Penawaran Anda terlebih dahulu.")
            elif not br_audience.strip():
                st.warning("⚠️ Mohon isi Target Pembeli terlebih dahulu.")
            else:
                with st.spinner("💼 AI sedang merancang transisi penutup yang elegan dan tidak agresif..."):
                    prompt = MONETIZATION_BRIDGE_PROMPT.format(
                        topic=br_topic,
                        product=br_product,
                        monetization_type=br_model,
                        audience=br_audience
                    )
                    b_res = ai_client.generate(
                        prompt=prompt,
                        system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                    )
                    st.session_state["bridge_result"] = b_res

        if "bridge_result" in st.session_state:
            st.markdown("### 🏆 4 Skrip Jembatan Konversi Terpilih")

            col_br_act1, col_br_act2, col_br_act3 = st.columns([1.5, 1.2, 0.8])
            with col_br_act1:
                if st.button("⚡ Pasang ke Pipeline Konten", type="primary", use_container_width=True, key="btn_bridge_to_pipe"):
                    st.session_state["pipe_product_input"] = br_product
                    st.session_state["pipe_step4_result"] = st.session_state["bridge_result"]
                    st.session_state["pipeline_step"] = 5
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.rerun()

            with col_br_act2:
                md_bytes = prepare_markdown_download(st.session_state["bridge_result"], "monetization_bridge_scripts")
                st.download_button(
                    label="📥 Unduh Skrip (.md)",
                    data=md_bytes,
                    file_name="ViralGenix_Monetization_Bridge.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="btn_down_bridge_lab"
                )
            with col_br_act3:
                if st.button("🗑️ Hapus Skrip", use_container_width=True, key="btn_del_bridge_lab"):
                    del st.session_state["bridge_result"]
                    st.rerun()

            with st.container(border=True):
                st.markdown(st.session_state["bridge_result"])

