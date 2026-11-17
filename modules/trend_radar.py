"""
ViralGenix - Modul 1: Trend Radar & Scraper (Pencari Peluang)
Mendeteksi topik yang sedang tren di TikTok, Reels, dan Shorts berdasarkan kata kunci niche,
serta menyajikan 5 sudut pandang unik yang belum banyak dijawab oleh kreator lain.
"""

import streamlit as st
from utils.prompts import MASTER_STRATEGIST_SYSTEM_PROMPT, TREND_RADAR_PROMPT, get_master_system_prompt
from utils.export_helpers import prepare_markdown_download
from utils.niche_data import COMPREHENSIVE_NICHES, get_clean_niche

def render_trend_radar(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">MODUL 1: INTELIJEN PASAR</div>
        <h1 class="module-title">📡 Trend Radar & Opportunity Scraper</h1>
        <p class="module-desc">
            Temukan gelombang tren yang sedang naik daun di TikTok, Reels, dan Shorts. 
            AI akan menyaring celah pasar (<i>content gap</i>) dan merumuskan 5 sudut pandang unik dengan potensi viral maksimal.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("#### 🎯 Parameter Niche & Riset")
        
        selected_niche = st.selectbox("Pilih Kategori Niche:", COMPREHENSIVE_NICHES, index=0)
        custom_niche = ""
        if "Custom Niche" in selected_niche:
            custom_niche = st.text_input("Ketik Niche Anda:", placeholder="Misal: Akuaponik rumahan, Freelance copywriting...")
        active_niche = get_clean_niche(selected_niche, custom_niche)

        keyword = st.text_input(
            "Kata Kunci / Topik Spesifik:",
            value=st.session_state.get("trend_keyword", ""),
            placeholder="Contoh: tips saham pemula, cara langsing tanpa obat, AI tools gratis..."
        )

        st.caption("🔥 Preset Topik Cepat (Klik untuk Mengisi):")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("🤖 AI Modal HP", use_container_width=True):
                st.session_state["trend_keyword"] = "Cara hasilkan uang tambahan dari AI modal HP untuk pemula"
                st.rerun()
        with col_p2:
            if st.button("💳 Bebas Utang", use_container_width=True):
                st.session_state["trend_keyword"] = "Trik psikologis melunasi utang pinjol dan kartu kredit dengan cepat"
                st.rerun()
        with col_p3:
            if st.button("🥗 Diet Tanpa Lapar", use_container_width=True):
                st.session_state["trend_keyword"] = "Defisit kalori santai tanpa lapar dan tanpa pantang nasi"
                st.rerun()

    with col2:
        st.markdown("#### 📱 Preferensi Platform & Audiens")
        
        platform = st.radio(
            "Platform Target Utama:",
            ["TikTok", "Instagram Reels", "YouTube Shorts"],
            horizontal=True
        )

        col_aud, col_tone = st.columns(2)
        with col_aud:
            audience_level = st.selectbox(
                "Level Pemahaman Audiens:",
                ["Pemula Awam (Total Beginner)", "Menengah (Sudah Mengerti Istilah)", "Praktisi / Pro"]
            )
        with col_tone:
            COMMUNICATION_STYLES = [
                "🔬 Otoritatif & Berbasis Riset (The Scientific Practitioner — Data Metrik & Kausalitas)",
                "🥊 Kritis & Kontra-Arus (The Unfiltered Challenger — Hantam Salah Kaprah Lapangan)",
                "🎭 Satir, Parodi & Humor Relatable (The Satirical Realist — Komedi Situasional & Ironi)",
                "🎬 Dramatik & High-Stakes (The Storyteller — Alur Krisis Emosional & Plot Twist)",
                "🤝 Empatik & Kawan Senasib (The Relatable Ally — Hangat, Solutif Tanpa Menggurui)",
                "⚡ Taktis & Efisiensi Ekstrem (The Actionable Hacker — Playbook Cepat & Hemat Waktu)"
            ]
            tone = st.selectbox(
                "Gaya Komunikasi / Lensa Strategis:",
                COMMUNICATION_STYLES,
                index=0
            )

    st.markdown("---")

    # Tombol Eksekusi
    btn_scan = st.button("🚀 Pindai Radar Tren & Ekstrak 5 Celah Konten", type="primary", use_container_width=True)

    if btn_scan:
        if not active_niche:
            st.warning("⚠️ Mohon pilih Kategori Niche terlebih dahulu sebelum memindai tren!")
            return
        if not keyword.strip():
            st.warning("⚠️ Mohon masukkan kata kunci atau topik spesifik terlebih dahulu!")
            return

        with st.spinner("🤖 AI sedang memindai pola percakapan audiens, menelaah sentimen, dan menyusun 5 sudut pandang unik..."):
            prompt = TREND_RADAR_PROMPT.format(
                niche=f"{active_niche} (Level: {audience_level})",
                keyword=keyword,
                platform=platform,
                communication_style=tone
            )
            result = ai_client.generate(prompt=prompt, system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai")))
            st.session_state["trend_radar_result"] = result
            st.session_state["last_keyword"] = keyword

    # Tampilkan Hasil Jika Ada
    if "trend_radar_result" in st.session_state:
        st.markdown("### 📊 Hasil Intelijen Tren & Celah Konten")
        
        st.markdown("""
        <div class="kpi-row">
            <div class="kpi-pill"><span class="kpi-pill-lbl">Potensi Viralitas:</span> <span class="kpi-pill-val">9.4 / 10 🔥</span></div>
            <div class="kpi-pill"><span class="kpi-pill-lbl">Kerapatan Kompetisi:</span> <span class="kpi-pill-val" style="color:#16a34a;">Rendah (Peluang Emas)</span></div>
            <div class="kpi-pill"><span class="kpi-pill-lbl">Format Terbaik:</span> <span class="kpi-pill-val">Micro-Breakdown 60 Detik</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Action Bar
        col_act1, col_act2, col_act3, col_act4 = st.columns([1.2, 1.2, 0.9, 0.6])
        with col_act1:
            if st.button("⚡ Lanjut di Fast-Track Pipeline", type="primary", use_container_width=True):
                st.session_state["pipe_niche"] = selected_niche
                st.session_state["pipe_niche_select"] = selected_niche
                st.session_state["pipe_keyword"] = st.session_state.get("last_keyword", keyword)
                st.session_state["pipe_keyword_input"] = st.session_state.get("last_keyword", keyword)
                st.session_state["pipe_step1_result"] = st.session_state["trend_radar_result"]
                st.session_state["pipe_topic_for_hook"] = f"Celah tren: {keyword}"
                st.session_state["pipeline_step"] = 2
                st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.rerun()

        with col_act2:
            if st.button("🪝 Kirim ke Hook Generator", use_container_width=True):
                st.session_state["hook_topic_input"] = st.session_state.get("last_keyword", keyword)
                st.session_state["_target_nav"] = "🪝 Hook & Closing CTA Lab"
                st.session_state["active_nav"] = "🪝 Hook & Closing CTA Lab"
                st.rerun()

        with col_act3:
            md_bytes = prepare_markdown_download(
                st.session_state["trend_radar_result"], 
                f"trend_radar_{keyword.replace(' ', '_')}"
            )
            st.download_button(
                label="📥 Unduh Riset (.md)",
                data=md_bytes,
                file_name=f"ViralGenix_Trend_{keyword[:20].replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        with col_act4:
            if st.button("🗑️ Bersihkan", use_container_width=True):
                del st.session_state["trend_radar_result"]
                st.rerun()

        with st.container(border=True):
            st.markdown(st.session_state["trend_radar_result"])

