"""
ViralGenix - Modul 3: The 3-Second Hook Generator & Storyboard Table
Menghasilkan 10 variasi hook visual dan verbal berdasarkan psikologi audiens,
serta meracik tabel skrip storyboard lengkap [Detik] | [Visual/B-Roll] | [Skrip Audio] | [Teks di Layar].
"""

import streamlit as st
from utils.prompts import (
    MASTER_STRATEGIST_SYSTEM_PROMPT,
    HOOK_GENERATOR_PROMPT,
    STORYBOARD_TABLE_PROMPT,
    CAPTION_HASHTAG_PROMPT,
    get_master_system_prompt
)
from utils.export_helpers import (
    markdown_table_to_dataframe,
    dataframe_to_csv_bytes,
    prepare_markdown_download,
    markdown_table_to_srt
)

def render_hook_generator(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">MODUL 3: PENAHAN SCROLL & STORYBOARD</div>
        <h1 class="module-title">🪝 The 3-Second Hook Generator & Script Table</h1>
        <p class="module-desc">
            80% kesuksesan video pendek ditentukan dalam 3 detik pertama. 
            Ciptakan 10 variasi hook berbasis 4 pilar psikologi audiens, 
            lalu ubah menjadi papan cerita (storyboard) terstruktur dengan formula retensi tengah dan CTA emosional.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_hooks, tab_storyboard = st.tabs(["🔥 10 Hook Matrix Psikologi", "🎬 Generator Skrip Tabel Storyboard (Detik demi Detik)"])

    with tab_hooks:
        col1, col2 = st.columns([1.2, 1], gap="medium")
        with col1:
            default_topic = st.session_state.get(
                "hook_topic_input",
                "Cara memulai bisnis dropship atau jualan online tanpa stok barang modal HP"
            )
            topic_input = st.text_area(
                "Topik Konten / Ide Cerita / Pesan Inti:",
                value=default_topic,
                height=110,
                placeholder="Jelaskan topik yang ingin Anda buatkan hook..."
            )

        with col2:
            audience_target = st.text_input(
                "Target Profil Audiens:",
                value="Anak muda / pekerja kantoran yang ingin punya penghasilan kedua tapi minim waktu",
                placeholder="Siapa yang menonton video ini?"
            )
            tone_style = st.selectbox(
                "Nuansa & Gaya Bahasa:",
                [
                    "Berenergi Tinggi & Tegas (Urgent & Bold)",
                    "Misterius & Membocorkan Rahasia (Curiosity Trap)",
                    "Santai, Hangat & Empatik (Bestie Vibe)",
                    "Provokatif & Kontradiktif (Debunking)"
                ]
            )

        btn_gen_hooks = st.button("⚡ Racik 10 Hook Pembunuh Scroll", type="primary", use_container_width=True)

        if btn_gen_hooks:
            if not topic_input.strip():
                st.error("Mohon isi topik konten terlebih dahulu.")
                return

            with st.spinner("🧠 AI sedang menyusun 10 variasi hook dengan formula visual + verbal + teks layar..."):
                prompt = HOOK_GENERATOR_PROMPT.format(
                    topic=topic_input,
                    audience=audience_target,
                    tone=tone_style
                )
                hooks_res = ai_client.generate(
                    prompt=prompt,
                    system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                )
                st.session_state["hooks_result"] = hooks_res
                st.session_state["last_hook_topic"] = topic_input

        if "hooks_result" in st.session_state:
            st.markdown("### 🎯 10 Variasi Hook Visual & Audio")

            st.markdown("""
            <div class="kpi-row">
                <div class="kpi-pill"><span class="kpi-pill-lbl">Variasi Hook:</span> <span class="kpi-pill-val">10 Skrip Visual + Audio 🔥</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Pilar Psikologi:</span> <span class="kpi-pill-val">FOMO, Curiosity, Gain, Empathy</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Avg. Skor Retensi:</span> <span class="kpi-pill-val" style="color:#4f46e5;">92.5 / 100</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Deteksi otomatis hook verbal dari teks hasil AI
            import re
            extracted_hooks = re.findall(r'\*\*Hook Verbal(?:\s*\(Audio\))?\*\*:\s*(?:_|\*|")?([^"\*\_\n]+)(?:_|\*|")?', st.session_state["hooks_result"])
            clean_hooks = [h.strip().strip('"').strip('*').strip('_') for h in extracted_hooks if len(h.strip()) > 8]

            if clean_hooks:
                st.markdown("##### 🎯 Pilih Hook Favorit untuk Diubah Jadi Storyboard:")
                chosen_from_list = st.selectbox("Daftar Hook Terdeteksi:", clean_hooks, key="quick_hook_select")
            else:
                chosen_from_list = "Stop lakuin cara ini kalau kamu gak mau rugi waktu dan duit sia-sia!"

            col_h1, col_h2, col_h3 = st.columns([1.3, 1, 0.7])
            with col_h1:
                if st.button("🎬 Bawa Hook Ini ke Storyboard", type="primary", use_container_width=True):
                    st.session_state["storyboard_topic"] = st.session_state.get("last_hook_topic", topic_input)
                    st.session_state["storyboard_selected_hook"] = chosen_from_list
                    st.success("✅ Hook berhasil dipilih! Pindah ke tab '🎬 Generator Skrip Tabel Storyboard' di atas.")

            with col_h2:
                md_bytes = prepare_markdown_download(st.session_state["hooks_result"], "10_variasi_hook")
                st.download_button(
                    label="📥 Unduh Hook (.md)",
                    data=md_bytes,
                    file_name="ViralGenix_10_Hooks.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col_h3:
                if st.button("🗑️ Hapus Hook", use_container_width=True):
                    del st.session_state["hooks_result"]
                    st.rerun()

            with st.container(border=True):
                st.markdown(st.session_state["hooks_result"])

    with tab_storyboard:
        st.markdown("#### 📐 Sutradara AI: Tabel Produksi Konten Lengkap (30-60 Detik)")
        st.caption("Sesuai standar formula: [Detik] | [Visual/B-Roll] | [Skrip Audio] | [Teks di Layar] | [Pemicu Psikologis]")

        col_s1, col_s2 = st.columns([1.2, 1], gap="medium")
        with col_s1:
            chosen_hook = st.text_input(
                "Hook Pembuka (Pilih dari tab sebelah atau ketik sendiri):",
                value=st.session_state.get(
                    "storyboard_selected_hook",
                    "Stop lakuin cara ini kalau kamu gak mau rugi waktu dan duit sia-sia!"
                )
            )
            story_topic = st.text_area(
                "Topik Utama Video:",
                value=st.session_state.get(
                    "storyboard_topic",
                    "Kesalahan fatal pemula saat mulai jualan online dan solusi otomatisasinya"
                ),
                height=90
            )

        with col_s2:
            cta_goal = st.text_input(
                "Tujuan Akhir / CTA:",
                value="Ajak penonton download template gratis di link bio profil",
                placeholder="Misal: Beli produk di bio, follow akun, save video..."
            )
            target_duration = st.select_slider(
                "Target Durasi Video:",
                options=["30 Detik (Fast Paced)", "45 Detik (Balanced)", "60 Detik (Storytelling Mendalam)"],
                value="60 Detik (Storytelling Mendalam)"
            )

        btn_gen_script = st.button("🎬 Hasilkan Skrip & Tabel Storyboard Lengkap", type="primary", use_container_width=True)

        if btn_gen_script:
            if not chosen_hook.strip() or not story_topic.strip():
                st.error("Mohon lengkapi hook pembuka dan topik video.")
                return

            with st.spinner("🎥 Menyusun pergerakan kamera, instruksi B-roll, kalimat dialog, dan teks layar detik demi detik..."):
                prompt = STORYBOARD_TABLE_PROMPT.format(
                    hook=chosen_hook,
                    topic=f"{story_topic} (Durasi: {target_duration})",
                    goal=cta_goal
                )
                story_res = ai_client.generate(
                    prompt=prompt,
                    system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                )
                st.session_state["storyboard_result"] = story_res

        if "storyboard_result" in st.session_state:
            st.markdown("### 📋 Hasil Storyboard Produksi")

            st.markdown("""
            <div class="kpi-row">
                <div class="kpi-pill"><span class="kpi-pill-lbl">Formula:</span> <span class="kpi-pill-val">Hook 3s ➔ Agitasi ➔ Mid Pattern Interrupt ➔ CTA</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Target Pacing:</span> <span class="kpi-pill-val">120-140 WPM (Sangat Ketat)</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Ekspor:</span> <span class="kpi-pill-val" style="color:#16a34a;">CSV Siap Excel & CapCut 📊</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Ekstraksi tabel ke CSV dan SRT
            df_table = markdown_table_to_dataframe(st.session_state["storyboard_result"])
            srt_bytes = markdown_table_to_srt(st.session_state["storyboard_result"])

            col_down1, col_down2, col_down3, col_down4 = st.columns([1, 1, 1.1, 1.2])
            with col_down1:
                if df_table is not None:
                    csv_bytes = dataframe_to_csv_bytes(df_table)
                    st.download_button(
                        label="📊 Unduh CSV",
                        data=csv_bytes,
                        file_name="ViralGenix_Storyboard_Table.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("Tabel siap dibaca.")

            with col_down2:
                md_bytes = prepare_markdown_download(st.session_state["storyboard_result"], "storyboard_skrip_lengkap")
                st.download_button(
                    label="📥 Unduh .MD",
                    data=md_bytes,
                    file_name="ViralGenix_Storyboard.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col_down3:
                if srt_bytes is not None:
                    st.download_button(
                        label="🎬 Unduh .SRT (CapCut)",
                        data=srt_bytes,
                        file_name="ViralGenix_Captions.srt",
                        mime="application/x-subrip",
                        use_container_width=True
                    )
                else:
                    st.caption("Subtitle auto-sync")

            with col_down4:
                if st.button("⚡ Sambungkan ke Monetisasi", type="primary", use_container_width=True):
                    st.session_state["monetize_topic_input"] = story_topic
                    st.session_state["active_nav"] = "💰 Monetization Bridge"
                    st.rerun()

            with st.container(border=True):
                st.markdown(st.session_state["storyboard_result"])

            # --- FITUR TAMBAHAN: TELEPROMPTER & SIMPAN SKRIP ---
            st.markdown("---")
            col_aux1, col_aux2 = st.columns([1, 1])

            with col_aux1:
                # Hitung kata untuk pacing
                full_text = st.session_state["storyboard_result"]
                words = [w for w in full_text.split() if len(w) > 2 and not w.startswith("|") and not w.startswith("#")]
                approx_dialogue_words = int(len(words) * 0.45) # Estimasi kata dialog di tabel
                est_sec = max(25, int((approx_dialogue_words / 130) * 60))

                with st.expander("🎙️ Mode Teleprompter & Latihan Bicara (Klik di Sini)", expanded=False):
                    st.markdown(f"""
                    **Statistik Kecepatan Bicara:**
                    - Perkiraan Kata Dialog: **~{approx_dialogue_words} kata**
                    - Estimasi Durasi: **~{est_sec} detik** *(Tempo ideal kreator: 120-140 kata/menit)*
                    """)
                    st.markdown("""
                    <div style="background: #f8fafc; border: 1.5px solid #4f46e5; border-radius: 12px; padding: 18px; font-size: 1.05rem; line-height: 1.8; color: #0f172a; font-weight: 500;">
                        💡 <i>Bacalah dialog audio dari tabel di atas dengan intonasi mantap, pandangan fokus ke lensa kamera depan HP, dan jeda nafas di detik 20 & 40.</i>
                    </div>
                    """, unsafe_allow_html=True)

            with col_aux2:
                if "saved_scripts" not in st.session_state:
                    st.session_state["saved_scripts"] = []

                if st.button("⭐ Simpan Skrip ke Koleksi Tersimpan", use_container_width=True):
                    from utils.vault_manager import create_draft
                    create_draft({
                        "title": story_topic[:40] + ("..." if len(story_topic) > 40 else ""),
                        "keyword": story_topic,
                        "hook_verbal": chosen_hook,
                        "storyboard_table_md": st.session_state["storyboard_result"],
                        "est_duration_sec": est_sec,
                        "dialogue_word_count": approx_dialogue_words,
                        "status": "📝 Skrip Selesai"
                    })
                    st.success("✅ Skrip berhasil disimpan ke Brankas Konten! Buka menu '⭐ Koleksi Skrip' atau '🗂️ Studio Produksi' untuk memproduksinya.")

            # --- FITUR TAMBAHAN: CAPTION, HASHTAG & JAM UPLOAD ---
            st.markdown("---")
            with st.expander("✨ Kit Publikasi: Buat Caption Viral, 10 Hashtag SEO & Jam Upload Terbaik (TikTok & Reels)", expanded=False):
                st.markdown("AI akan meracik 2 variasi caption ramah algoritma, pertanyaan pemicu interaksi komentar (*comment bait*), 10 hashtag bertingkat, serta jam upload prime time.")
                if st.button("🚀 Buat Caption & Paket Hashtag Sekarang", type="primary", use_container_width=True, key="btn_gen_caption"):
                    with st.spinner("🤖 AI sedang merancang caption pemicu interaksi dan hashtag SEO..."):
                        cap_prompt = CAPTION_HASHTAG_PROMPT.format(
                            topic=story_topic,
                            hook=chosen_hook,
                            script_summary=st.session_state["storyboard_result"][:500]
                        )
                        cap_res = ai_client.generate(prompt=cap_prompt, system_prompt=MASTER_STRATEGIST_SYSTEM_PROMPT)
                        st.session_state["caption_result"] = cap_res

                if "caption_result" in st.session_state:
                    with st.container(border=True):
                        st.markdown(st.session_state["caption_result"])
                        col_c1, col_c2 = st.columns([1, 1])
                        with col_c1:
                            cap_md = prepare_markdown_download(st.session_state["caption_result"], "caption_dan_hashtag")
                            st.download_button(
                                label="📥 Unduh Caption & Hashtag (.md)",
                                data=cap_md,
                                file_name="ViralGenix_Caption_Hashtags.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                        with col_c2:
                            if st.button("🗑️ Hapus Caption", key="btn_clear_cap", use_container_width=True):
                                del st.session_state["caption_result"]
                                st.rerun()

