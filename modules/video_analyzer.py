"""
ViralGenix - Modul 2: URL Reverse-Engineering (Pembedah Kompetitor)
Membedah struktur video viral kompetitor dari transkrip audio,
menganalisis pemicu viralitas, dan meracik 3 ide turunan "Steal Like an Artist".
"""

import streamlit as st
from utils.transcript_extractor import fetch_youtube_transcript, extract_video_id
from utils.prompts import MASTER_STRATEGIST_SYSTEM_PROMPT, VIDEO_REVERSE_ENGINEER_PROMPT, get_master_system_prompt
from utils.export_helpers import prepare_markdown_download

def render_video_analyzer(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">MODUL 2: REVERSE ENGINEERING</div>
        <h1 class="module-title">🔬 URL Reverse-Engineering (Bedah Kompetitor)</h1>
        <p class="module-desc">
            Masukkan tautan video YouTube/Shorts kompetitor yang sedang viral. 
            AI akan mengekstrak transkrip dialog, membedah anatomi retensi emosionalnya, 
            dan menyajikan 3 ide konten turunan yang jauh lebih unggul dengan prinsip <i>Steal Like an Artist</i>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_auto, tab_manual = st.tabs(["🎥 Ekstraksi Otomatis URL YouTube", "✍️ Input Transkrip / Deskripsi Manual (TikTok & Reels)"])

    video_input_content = ""
    source_label = ""

    with tab_auto:
        st.markdown("Masukkan URL YouTube Shorts atau Video Reguler:")
        yt_url = st.text_input(
            "Tautan Video YouTube:",
            value=st.session_state.get("last_yt_url", ""),
            placeholder="https://www.youtube.com/shorts/eY9HqN7123 atau https://youtu.be/..."
        )

        col_fetch, col_clear = st.columns([2, 1])
        with col_fetch:
            fetch_btn = st.button("📥 Ambil Transkrip Video Otomatis", use_container_width=True)

        if fetch_btn:
            if not yt_url.strip():
                st.warning("⚠️ Silakan masukkan URL YouTube terlebih dahulu.")
            else:
                with st.spinner("Mengambil transkrip dialog dari server YouTube..."):
                    res = fetch_youtube_transcript(yt_url)
                    if res["success"]:
                        st.session_state["fetched_transcript"] = res["transcript_text"]
                        st.session_state["fetched_plain"] = res["plain_text"]
                        st.session_state["fetched_video_id"] = res["video_id"]
                        st.session_state["last_yt_url"] = yt_url
                        if res.get("fallback_to_metadata"):
                            st.info("ℹ️ Video ini tidak menyediakan closed-caption (CC) bawaan di YouTube (kemungkinan teks ditempel langsung di video via CapCut). ViralGenix berhasil mengambil Judul & Deskripsi video ini sehingga tetap siap dibedah oleh AI!")
                        else:
                            st.success(f"✅ Transkrip dialog berhasil diambil! Total cuplikan: {res['total_snippets']} fragmen.")
                    else:
                        st.warning(res["error"])

        if "fetched_transcript" in st.session_state:
            # Tampilkan Video Player langsung agar kreator bisa membandingkan visual dan transkrip
            if yt_url.strip() and ("youtube.com" in yt_url or "youtu.be" in yt_url):
                with st.expander("📺 Tonton Video Kompetitor (Side-by-Side Player)", expanded=True):
                    try:
                        st.video(yt_url)
                    except Exception:
                        st.caption("Pratinjau video tidak dapat dimuat langsung dari URL ini.")

            with st.expander("👁️ Pratinjau Transkrip yang Berhasil Diambil (Klik untuk Membuka)", expanded=False):
                st.text_area("Teks Transkrip Berstempel Waktu:", value=st.session_state["fetched_transcript"], height=200)
            video_input_content = st.session_state["fetched_plain"]
            source_label = f"YouTube URL: {st.session_state.get('last_yt_url', '')}"

    with tab_manual:
        st.markdown("Untuk video TikTok, Instagram Reels, atau video tanpa subtitle otomatis:")
        manual_text = st.text_area(
            "Salin (Paste) Narasi / Dialog / Ringkasan Video Kompetitor di Sini:",
            value=st.session_state.get("manual_transcript", ""),
            height=180,
            placeholder="Contoh: 'Jangan beli iPhone 15 sebelum tahu hal ini. Kemarin gue coba bandingin baterainya sama seri lama, dan hasilnya mengejutkan banget...'"
        )
        if manual_text.strip():
            video_input_content = manual_text.strip()
            source_label = "Transkrip / Deskripsi Manual"

    st.markdown("---")

    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        analyze_btn = st.button("🧠 Bedah Struktur Viral & Racik 3 Ide Turunan", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("💡 Gunakan Contoh Kasus Viral", use_container_width=True):
            sample_transcript = (
                "[00:00] Stop scroll dulu kalau kamu masih punya utang pinjol atau kartu kredit.\n"
                "[00:04] 90% orang gak tahu kalau ada metode 'Debt Snowball' yang bisa lunasin utang 2x lebih cepat.\n"
                "[00:12] Caranya: urutkan dari utang dengan nominal terkecil, bukan bunga terbesar.\n"
                "[00:20] Otak manusia butuh dopamine hit saat melihat satu pos utang berhasil dicoret!\n"
                "[00:32] Banyak perencana keuangan bilang fokus ke bunga dulu, tapi itu salah karena secara psikologis bikin cepat menyerah.\n"
                "[00:45] Gua udah buatin kalkulator simulasi utang gratis di bio profil gue. Cek sekarang sebelum postingan ini ditakedown!"
            )
            st.session_state["fetched_transcript"] = sample_transcript
            st.session_state["fetched_plain"] = sample_transcript
            st.session_state["last_yt_url"] = "https://youtube.com/shorts/sample_viral_finance"
            st.rerun()

    if analyze_btn:
        final_content = video_input_content or st.session_state.get("fetched_plain", "")
        if not final_content.strip():
            st.warning("⚠️ Transkrip atau teks dialog kompetitor masih kosong! Silakan ambil transkrip dari YouTube atau tempelkan teks dialog manual di tab sebelah.")
            return

        with st.spinner("🕵️ AI sedang membedah anatomi emosi, pola pacing 3 detik, jebakan retensi, dan merumuskan ide turunan..."):
            prompt = VIDEO_REVERSE_ENGINEER_PROMPT.format(transcript=final_content)
            result = ai_client.generate(
                prompt=prompt,
                system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
            )
            st.session_state["reverse_engineer_result"] = result

    if "reverse_engineer_result" in st.session_state:
        st.markdown("### 🧬 Hasil Bedah Anatomi & Ide Konten Turunan")
        
        st.markdown("""
        <div class="kpi-row">
            <div class="kpi-pill"><span class="kpi-pill-lbl">Retensi Detik 0-3:</span> <span class="kpi-pill-val">Pemicu Dopamin Tinggi 🎯</span></div>
            <div class="kpi-pill"><span class="kpi-pill-lbl">Pola Interupsi:</span> <span class="kpi-pill-val">Setiap 3.5 Detik</span></div>
            <div class="kpi-pill"><span class="kpi-pill-lbl">Formula Turunan:</span> <span class="kpi-pill-val" style="color:#4f46e5;">3 Konsep "Steal Like an Artist"</span></div>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2, col_act3, col_act4 = st.columns([1.2, 1.2, 0.9, 0.6])
        with col_act1:
            if st.button("⚡ Lanjut di Fast-Track Pipeline", type="primary", use_container_width=True):
                st.session_state["pipe_keyword"] = "Konsep turunan hasil bedah video kompetitor"
                st.session_state["pipe_keyword_input"] = "Konsep turunan hasil bedah video kompetitor"
                st.session_state["pipe_topic_for_hook"] = "Ide turunan lebih unggul dari video kompetitor viral"
                st.session_state["pipe_step1_result"] = st.session_state["reverse_engineer_result"]
                st.session_state["pipeline_step"] = 2
                st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.rerun()

        with col_act2:
            if st.button("🪝 Kirim ke Hook Generator", use_container_width=True):
                st.session_state["hook_topic_input"] = "Sudut pandang alternatif dari video viral kompetitor yang baru dibedah"
                st.session_state["_target_nav"] = "🪝 Hook & Closing CTA Lab"
                st.session_state["active_nav"] = "🪝 Hook & Closing CTA Lab"
                st.rerun()

        with col_act3:
            md_bytes = prepare_markdown_download(st.session_state["reverse_engineer_result"], "bedah_kompetitor_viral")
            st.download_button(
                label="📥 Unduh Hasil (.md)",
                data=md_bytes,
                file_name="ViralGenix_Reverse_Engineering.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_act4:
            if st.button("🗑️ Hapus Analisis", use_container_width=True):
                del st.session_state["reverse_engineer_result"]
                st.rerun()

        with st.container(border=True):
            st.markdown(st.session_state["reverse_engineer_result"])

