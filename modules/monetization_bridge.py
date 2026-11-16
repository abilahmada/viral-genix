"""
ViralGenix - Modul 4: Monetization Bridge (Jembatan Konversi)
Menghubungkan konten edukasi/hiburan dengan Call to Action (CTA) jualan atau afiliasi secara halus (soft selling),
membuat penonton merasa butuh mengklik link di bio tanpa merasa sedang dipaksa beli.
"""

import streamlit as st
from utils.prompts import MASTER_STRATEGIST_SYSTEM_PROMPT, MONETIZATION_BRIDGE_PROMPT
from utils.export_helpers import prepare_markdown_download

def render_monetization_bridge(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">MODUL 4: MONETISASI & KONVERSI</div>
        <h1 class="module-title">💰 Monetization Bridge (Jembatan Konversi)</h1>
        <p class="module-desc">
            Konten viral tanpa konversi hanyalah vanity metrics. 
            Modul ini meracik jembatan penutup (<i>closing segue</i>) halus yang mengubah penonton biasa menjadi pembeli 
            produk afiliasi, digital product, atau klien jasa tanpa terkesan agresif (*anti-salesy*).
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 1], gap="medium")

    with col1:
        st.markdown("#### 📦 Info Produk / Penawaran Anda")
        
        default_topic = st.session_state.get(
            "monetize_topic_input",
            "Panduan otomatisasi pembuatan konten dan riset tren video pendek"
        )
        content_topic = st.text_area(
            "Topik Inti Video:",
            value=default_topic,
            height=90,
            placeholder="Jelaskan topik materi video yang baru saja ditonton audiens..."
        )

        product_name = st.text_input(
            "Nama Produk / Penawaran:",
            value=st.session_state.get("monetize_prod_name", "Template Notion Creator OS + Prompt Kit ViralGenix"),
            placeholder="Contoh: Lip serum herbal, Ebook 30 Hari Diet, Jasa Desain Logo..."
        )

        st.caption("🔥 Preset Cepat Model Monetisasi:")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            if st.button("🛍️ TikTok Shop", use_container_width=True):
                st.session_state["monetize_prod_name"] = "Produk Keranjang Kuning / Shopee Affiliate Rekomendasi"
                st.session_state["monetize_model_idx"] = 1
                st.rerun()
        with col_m2:
            if st.button("📚 Produk Digital", use_container_width=True):
                st.session_state["monetize_prod_name"] = "Ebook Panduan Praktis & Template Notion Creator OS"
                st.session_state["monetize_model_idx"] = 0
                st.rerun()
        with col_m3:
            if st.button("🎁 Free Lead Magnet", use_container_width=True):
                st.session_state["monetize_prod_name"] = "Checklist & Template PDF Gratis (Link di Bio)"
                st.session_state["monetize_model_idx"] = 2
                st.rerun()

    with col2:
        st.markdown("#### 🎯 Model Monetisasi & Target")
        
        monetization_options = [
            "Produk Digital (Ebook, Course, Template Notion/Canva)",
            "Produk Afiliasi (Keranjang Kuning TikTok Shop / Shopee Affiliate)",
            "Lead Magnet Gratis (Kumpulkan Database WA / Telegram / Email)",
            "Jasa & Konsultasi (Freelancer, Agensi, Jasa Bimbingan)",
            "Produk Fisik Sendiri (Brand Owner / Toko Online)"
        ]

        active_model_idx = st.session_state.get("monetize_model_idx", 0)
        if active_model_idx >= len(monetization_options):
            active_model_idx = 0

        monetization_type = st.selectbox(
            "Model Bisnis / Tipe Konversi:",
            monetization_options,
            index=active_model_idx
        )

        target_audience = st.text_input(
            "Target Pembeli:",
            value="Kreator pemula & UMKM yang ingin konsisten ngonten tanpa kehabisan ide",
            placeholder="Siapa yang paling butuh produk ini?"
        )

    st.markdown("---")

    btn_build_bridge = st.button("🌉 Racik 4 Formula Jembatan Konversi Soft-Selling", type="primary", use_container_width=True)

    if btn_build_bridge:
        if not content_topic.strip() or not product_name.strip():
            st.error("Mohon lengkapi topik video dan nama produk penawaran Anda.")
            return

        with st.spinner("💼 AI sedang menyusun psikologi transisi, kalimat pengantar, arahan visual, dan teks layar penutup..."):
            prompt = MONETIZATION_BRIDGE_PROMPT.format(
                topic=content_topic,
                product=product_name,
                monetization_type=monetization_type,
                audience=target_audience
            )
            bridge_res = ai_client.generate(prompt=prompt, system_prompt=MASTER_STRATEGIST_SYSTEM_PROMPT)
            st.session_state["bridge_result"] = bridge_res

    if "bridge_result" in st.session_state:
        st.markdown("### 🏆 4 Skrip Jembatan Konversi Terpilih")

        st.markdown("""
        <div class="kpi-row">
            <div class="kpi-pill"><span class="kpi-pill-lbl">Pendekatan:</span> <span class="kpi-pill-val">100% Anti-Salesy / Soft-Selling 🍃</span></div>
            <div class="kpi-pill"><span class="kpi-pill-lbl">Golden Ratio:</span> <span class="kpi-pill-val">80% Pure Value : 20% Closing</span></div>
            <div class="kpi-pill"><span class="kpi-pill-lbl">Target Tindakan:</span> <span class="kpi-pill-val" style="color:#4f46e5;">Klik Link Bio / Save Video</span></div>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2, col_act3 = st.columns([1.2, 1, 0.8])
        with col_act1:
            md_bytes = prepare_markdown_download(st.session_state["bridge_result"], "monetization_bridge_scripts")
            st.download_button(
                label="📥 Unduh Skrip (.md)",
                data=md_bytes,
                file_name="ViralGenix_Monetization_Bridge.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_act2:
            if st.button("⭐ Simpan ke Koleksi", use_container_width=True):
                if "saved_scripts" not in st.session_state:
                    st.session_state["saved_scripts"] = []
                new_item = {
                    "title": f"Closing Bridge: {product_name[:30]}",
                    "hook": f"Tipe: {monetization_type}",
                    "script": st.session_state["bridge_result"]
                }
                st.session_state["saved_scripts"].append(new_item)
                st.success("✅ Jembatan konversi disimpan ke koleksi!")
        with col_act3:
            if st.button("🗑️ Hapus Skrip", use_container_width=True):
                del st.session_state["bridge_result"]
                st.rerun()

        with st.container(border=True):
            st.markdown(st.session_state["bridge_result"])

        st.markdown("""
        ---
        #### 💡 Tips Eksekusi Monetisasi Halus:
        - **Prinsip 80/20**: 80% durasi video harus murni memberikan nilai (*pure value*), hanya 20% terakhir untuk jembatan konversi.
        - **Visual Cue Sederhana**: Jangan taruh banner diskon besar yang terkesan 'iklan jadul'. Cukup tunjukkan produk secara organik sedang dipakai.
        - **Bio Clarity**: Pastikan link di profil Anda menggunakan nama domain atau teks yang jelas (contoh: *"Template Gratis di Sini"*).
        """)

