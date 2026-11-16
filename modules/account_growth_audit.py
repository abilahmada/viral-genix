"""
ViralGenix - Modul Solusi Pertumbuhan Akun A-Z (Account Growth & Positioning Engine)
Membedah, mengaudit, dan menyusun blueprint strategis akun media sosial (TikTok, Instagram, Shorts)
mulai dari optimasi bio 3 detik, matriks 4 pilar konten, hingga roadmap 30 hari monetisasi.
"""

import streamlit as st
import re
import utils.prompts
from utils.prompts import get_master_system_prompt
from utils.niche_data import COMPREHENSIVE_NICHES, get_clean_niche

try:
    from utils.prompts import ACCOUNT_GROWTH_BLUEPRINT_PROMPT
except ImportError:
    import importlib
    importlib.reload(utils.prompts)
    from utils.prompts import ACCOUNT_GROWTH_BLUEPRINT_PROMPT

from utils.export_helpers import prepare_markdown_download


def render_account_growth_audit(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">SOLUSI STRATEGI HULU-KE-HILIR</div>
        <h1 class="module-title">🎯 Bedah & Blueprint Akun (Growth Solution A-Z)</h1>
        <p class="module-desc">
            Bukan sekadar engine produktivitas, melainkan <b>arsitek pertumbuhan akun Anda dari nol</b>.
            Audit profil, temukan diferensiasi unik (positioning), susun 4 pilar konten teruji, 
            dan terapkan roadmap 30 hari untuk mendongkrak pengikut setia serta konversi penjualan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_audit, tab_checklist = st.tabs([
        "🔍 Formulator Blueprint & Audit Akun",
        "📋 SOP Kesiapan Algoritma Akun Baru"
    ])

    with tab_audit:
        col1, col2 = st.columns([1.1, 1], gap="medium")

        with col1:
            st.markdown("#### 👤 Profil & Niche Akun")

            saved_ag_niche = st.session_state.get("ag_saved_niche", "")
            ag_niche_idx = COMPREHENSIVE_NICHES.index(saved_ag_niche) if saved_ag_niche in COMPREHENSIVE_NICHES else 0
            selected_niche = st.selectbox("Pilih Kategori Niche / Industri:", COMPREHENSIVE_NICHES, index=ag_niche_idx)
            custom_ag_niche = ""
            if "Custom Niche" in selected_niche:
                custom_ag_niche = st.text_input("Ketik Niche Spesifik Anda:", placeholder="Misal: Jasa Desain Canva untuk UMKM", key="ag_custom_niche_input")
            active_niche = get_clean_niche(selected_niche, custom_ag_niche)

            current_handle = st.text_input(
                "Username / Handle Akun Saat Ini (Opsional):",
                value=st.session_state.get("ag_handle", ""),
                placeholder="Contoh: @budi_cerdasfinansial (opsional)"
            )

            current_bio = st.text_area(
                "Bio Profil Saat Ini (Kosongkan jika akun baru):",
                value=st.session_state.get("ag_bio", ""),
                height=80,
                placeholder="Tuliskan bio profil Anda sekarang untuk diaudit dan diperbaiki oleh AI..."
            )

            st.caption("🔥 Preset Cepat Studi Kasus Sukses:")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                if st.button("💼 Affiliate Creator", use_container_width=True):
                    st.session_state["ag_handle"] = "@racun.katalog.id"
                    st.session_state["ag_bio"] = "Rekomendasi barang unik & murah TikTok Shop tiap hari! Link beli di bawah 👇"
                    st.session_state["ag_aud"] = "Audiens muda pemburu barang fungsional & diskon"
                    st.session_state["ag_mon"] = "Afiliasi TikTok Shop & Shopee (Komisi Keranjang Kuning)"
                    st.session_state["ag_usp"] = "Review jujur tanpa endorse palsu, uji ketahanan produk"
                    st.rerun()
            with col_p2:
                if st.button("🤖 Solo Builder AI", use_container_width=True):
                    st.session_state["ag_handle"] = "@kreator.otomasi"
                    st.session_state["ag_bio"] = "Bantu kamu hemat 10 jam kerja seminggu pakai AI. Belajar prompt & tools."
                    st.session_state["ag_aud"] = "Pekerja kantoran & freelancer yang kewalahan tugas harian"
                    st.session_state["ag_mon"] = "Produk Digital (Template Notion, Ebook Panduan Prompts)"
                    st.session_state["ag_usp"] = "Workflow praktis langsung pakai modal HP tanpa coding ribet"
                    st.rerun()
            with col_p3:
                if st.button("📈 Mentor Finansial", use_container_width=True):
                    st.session_state["ag_handle"] = "@bebas.utang"
                    st.session_state["ag_bio"] = "Tips kelola gaji UMR biar bisa nabung saham & lunas utang."
                    st.session_state["ag_aud"] = "Generasi sandwich & karyawan baru gajian"
                    st.session_state["ag_mon"] = "Lead Magnet WhatsApp Group & Komunitas Belajar"
                    st.session_state["ag_usp"] = "Metode psikologis Debt Snowball yang ramah gaji pas-pasan"
                    st.rerun()

        with col2:
            st.markdown("#### 🎯 Target Audiens & Monetisasi")

            platform_target = st.selectbox(
                "Platform Utama:",
                ["TikTok & Instagram Reels (Format 9:16)", "TikTok Shop Khusus", "YouTube Shorts Focus", "Semua Platform"],
                index=0
            )

            target_audience = st.text_input(
                "Target Audiens Ideal:",
                value=st.session_state.get("ag_aud", ""),
                placeholder="Contoh: Pekerja kantoran 20-35 tahun / Ibu rumah tangga pemula..."
            )

            monetization_goal = st.selectbox(
                "Model Monetisasi Utama:",
                [
                    "Afiliasi (TikTok Shop Keranjang Kuning / Shopee Affiliate)",
                    "Produk Digital (Template Notion, Ebook, Course, Preset)",
                    "Lead Magnet (Kumpul Database WA / Email / Grup Komunitas)",
                    "Jasa / Freelance / Agensi (Mendapatkan Klien Berbayar)",
                    "Brand Awareness / Personal Branding untuk Karir"
                ],
                index=0
            )

            usp_statement = st.text_area(
                "Nilai Tambah Unik (USP) / Janji Transformasi:",
                value=st.session_state.get("ag_usp", ""),
                height=80,
                placeholder="Contoh: Tutorial langkah demi langkah ramah pemula tanpa modal jutaan..."
            )

        st.markdown("---")

        btn_run_blueprint = st.button("🚀 Bedah Akun & Bangun Master Blueprint Pertumbuhan A-Z", type="primary", use_container_width=True)

        if btn_run_blueprint:
            if not active_niche:
                st.warning("⚠️ Mohon pilih Kategori Niche terlebih dahulu sebelum membangun blueprint.")
            elif not target_audience.strip():
                st.warning("⚠️ Mohon isi Target Audiens Ideal akun Anda.")
            elif not usp_statement.strip():
                st.warning("⚠️ Mohon isi Nilai Tambah Unik (USP) / Janji Transformasi akun Anda.")
            else:
                with st.spinner("🧠 AI Strategist sedang membedah anatomi akun, merancang bio 3 detik, dan menyusun roadmap 30 hari..."):
                    prompt = ACCOUNT_GROWTH_BLUEPRINT_PROMPT.format(
                        niche=active_niche,
                        platform=platform_target,
                        current_handle=current_handle,
                        current_bio=current_bio if current_bio.strip() else "(Akun Baru / Belum ada)",
                        audience=target_audience,
                        monetization_goal=monetization_goal,
                        usp=usp_statement
                    )
                    
                    res = ai_client.generate(
                        prompt=prompt,
                        system_prompt=get_master_system_prompt(st.session_state.get("creator_persona", "santai"))
                    )
                    st.session_state["account_blueprint_result"] = res
                    st.session_state["ag_saved_niche"] = active_niche
                    st.session_state["ag_saved_audience"] = target_audience
                st.session_state["ag_saved_goal"] = monetization_goal

        if "account_blueprint_result" in st.session_state:
            st.markdown("### 🏛️ Master Blueprint Pertumbuhan Akun")

            st.markdown("""
            <div class="kpi-row">
                <div class="kpi-pill"><span class="kpi-pill-lbl">Fase Akun:</span> <span class="kpi-pill-val">Pondasi Otoritas 0-30 Hari 🚀</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Formula Bio:</span> <span class="kpi-pill-val">Hook ➔ Transformasi ➔ CTA</span></div>
                <div class="kpi-pill"><span class="kpi-pill-lbl">Distribusi Pilar:</span> <span class="kpi-pill-val" style="color:#4f46e5;">40 : 30 : 20 : 10 Authority</span></div>
            </div>
            """, unsafe_allow_html=True)

            col_act1, col_act2, col_act3 = st.columns([1.5, 1.2, 0.8])
            with col_act1:
                if st.button("⚡ Terapkan Blueprint Ini ke Pipeline Konten", type="primary", use_container_width=True):
                    saved_n = st.session_state.get("ag_saved_niche", "Bisnis Online")
                    st.session_state["pipe_niche"] = saved_n
                    matched_n = None
                    for cn in COMPREHENSIVE_NICHES:
                        if saved_n and (saved_n.lower() in cn.lower() or cn.lower() in saved_n.lower()):
                            matched_n = cn
                            break
                    if matched_n:
                        st.session_state["pipe_niche_select"] = matched_n
                        st.session_state["pipe_niche"] = matched_n

                    st.session_state["pipe_audience"] = st.session_state.get("ag_saved_audience", "Pemula")
                    st.session_state["pipe_keyword"] = f"Pilar Konten {saved_n}"
                    st.session_state["pipe_keyword_input"] = f"Pilar Konten {saved_n}"
                    st.session_state["pipeline_step"] = 1
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.toast("Blueprint berhasil diterapkan ke Pipeline!", icon="🚀")
                    st.rerun()

            with col_act2:
                md_bytes = prepare_markdown_download(
                    st.session_state["account_blueprint_result"],
                    f"Blueprint_Akun_{st.session_state.get('ag_saved_niche', 'ViralGenix').replace(' ', '_')}"
                )
                st.download_button(
                    label="📥 Unduh Playbook Akun (.md)",
                    data=md_bytes,
                    file_name="ViralGenix_Account_Growth_Playbook.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col_act3:
                if st.button("🗑️ Hapus Blueprint", use_container_width=True):
                    del st.session_state["account_blueprint_result"]
                    st.rerun()

            # Deteksi otomatis teks bio dari hasil blueprint untuk 1-klik copy
            res_text = st.session_state["account_blueprint_result"]
            with st.expander("📋 Salin Cepat Rekomendasi Bio Profil (1-Klik)", expanded=True):
                bio_matches = re.findall(r'(?:Variasi \d|Pilihan \d)[^\n]*\n(.*?)(?=\n\s*(?:-\s*\*)?(?:Variasi|Pilihan|\#\#\#|\Z))', res_text, re.DOTALL | re.IGNORECASE)
                if bio_matches and len(bio_matches) >= 2:
                    for b_idx, b_val in enumerate(bio_matches[:3]):
                        clean_b = b_val.strip().strip('>').strip().strip('"').strip('*')
                        if clean_b:
                            st.caption(f"✨ **Pilihan Bio #{b_idx+1}:**")
                            st.code(clean_b, language=None)
                else:
                    st.caption("💡 Salin variasi bio favorit Anda langsung dari panduan di bawah untuk dipasang di profil TikTok / Instagram.")

            with st.container(border=True):
                st.markdown(st.session_state["account_blueprint_result"])

    # =========================================================================
    # TAB 2: SOP KESIAPAN ALGORITMA AKUN BARU
    # =========================================================================
    with tab_checklist:
        st.markdown("### 📋 Protokol Kesiapan Algoritma Akun Baru (*Zero to FYP*)")
        st.caption("Ikuti daftar periksa ini sebelum dan sesudah Anda memposting video pertama agar akun tidak terdeteksi bot atau terjebak di batas 200 views.")

        with st.container(border=True):
            st.markdown("#### ⏳ Fase 1: Protokol Pemanasan Akun (Warm-Up 24-48 Jam Pertama)")
            st.checkbox("1. Jangan langsung posting video di jam pertama akun dibuat.", value=True, help="Algoritma membutuhkan waktu untuk mencocokkan IP dan minat akun Anda.")
            st.checkbox("2. Tonton dan beri interaksi alami (Like, Simpan, Komentar bermutu) pada 10-15 video di niche Anda.")
            st.checkbox("3. Lengkapi Foto Profil beresolusi tajam (wajah terlihat jelas atau logo kontras tinggi).")
            st.checkbox("4. Pasang Display Name yang mengandung Keyword SEO (Contoh: *Nama | Niche Anda*).")

        with st.container(border=True):
            st.markdown("#### 🎬 Fase 2: Peluncuran 5 Video Pilar Pertama (Hari 3 - Hari 7)")
            st.checkbox("5. Gunakan hook pemicu dopamin di 3 detik pertama (Pilar 40% Otoritas).")
            st.checkbox("6. Pastikan audio jernih (suara vokal lebih dominan dibanding backsound musik).")
            st.checkbox("7. Pasang teks on-screen kontras di detik 0-3 untuk audiens yang memutar video tanpa suara.")
            st.checkbox("8. Berikan Call to Action lembut di penutup (misal: bookmark video atau cek bio).")

        with st.container(border=True):
            st.markdown("#### 📊 Fase 3: Evaluasi Metrik Kunci Algoritma")
            st.info("""
            **3 Metrik Penentu Video Dilempar ke Gelombang FYP Berikutnya:**
            - **Watch Time / Completion Rate**: Minimal > 60% penonton bertahan sampai video selesai.
            - **Share / Repost Ratio**: Video yang dibagikan ke WhatsApp / DM mendapat bobot skor 3x lebih tinggi dari Like biasa.
            - **Save / Bookmark Ratio**: Tanda utama bahwa video Anda dianggap bernilai tinggi untuk disimpan.
            """)

