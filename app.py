"""
ViralGenix - Solusi Terpadu Riset, Produksi, dan Pertumbuhan Akun Video Pendek (Short-Form Engine)
Engine A-to-Z untuk TikTok, Instagram Reels, dan YouTube Shorts.
"""

import streamlit as st
import time
import os
import io

# Konfigurasi Halaman Wajib di Baris Pertama
st.set_page_config(
    page_title="ViralGenix - Continuous AI Short-Form Content Intelligence & Production Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Ultra-Clean Modern SaaS Light Mode CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            html, body, [class*="css"] { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f8fafc; color: #0f172a; }
            .main-brand { font-size: 2rem; font-weight: 800; color: #4f46e5; }
        </style>
        """, unsafe_allow_html=True)

load_css()

# Import Modul & Utilitas dengan Auto-Reload (Reload utils terlebih dahulu agar modul selalu mendapat definisi terbaru)
import importlib
import utils.ai_client
import utils.transcript_extractor
import utils.prompts
import utils.export_helpers
import utils.vault_manager
import utils.niche_data

importlib.reload(utils.ai_client)
importlib.reload(utils.transcript_extractor)
importlib.reload(utils.prompts)
importlib.reload(utils.export_helpers)
importlib.reload(utils.vault_manager)
importlib.reload(utils.niche_data)

import modules.fast_track_pipeline
import modules.production_studio
import modules.account_growth_audit
import modules.video_analyzer
import modules.trend_radar
import modules.hook_cta_lab

importlib.reload(modules.fast_track_pipeline)
importlib.reload(modules.production_studio)
importlib.reload(modules.account_growth_audit)
importlib.reload(modules.video_analyzer)
importlib.reload(modules.trend_radar)
importlib.reload(modules.hook_cta_lab)

from utils.ai_client import AIClient
from utils.env_manager import get_env_var, save_env_var
from utils.vault_manager import load_vault, delete_draft, generate_draft_bundle_zip, generate_all_vault_bundle_zip
from modules.fast_track_pipeline import render_fast_track_pipeline
from modules.production_studio import render_production_studio
from modules.account_growth_audit import render_account_growth_audit
from modules.video_analyzer import render_video_analyzer
from modules.trend_radar import render_trend_radar
from modules.hook_cta_lab import render_hook_cta_lab

# Inisialisasi Session State Navigasi
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"

# --- SIDEBAR PUSAT KENDALI (CLEAN & GROUPED UI) ---

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span class="main-brand">VIRALGENIX</span>
            <span class="brand-badge">GROWTH PRO</span>
        </div>
        <div class="brand-tagline">End-to-End Content & Account Growth Engine</div>
    </div>
    """, unsafe_allow_html=True)

    # Arsitektur Navigasi Terstruktur (The 3-Zone Mental Model)
    st.markdown("### 🧭 Menu Navigasi")

    nav_options = [
        "⚡ Generator Konten (Pipeline & Sprint)",
        "🗂️ Studio Produksi & Teleprompter",
        "🎯 Bedah & Blueprint Akun (Growth A-Z)",
        "🔬 Bedah Video Viral (Reverse Eng.)",
        "📡 Trend Radar & Celah Pasar",
        "🪝 Hook & Closing CTA Lab",
        "⭐ Brankas Konten & Master Stok",
        "⚙️ Pengaturan & Panduan Engine"
    ]

    # Mapping backward-compatible untuk tombol redirect internal
    nav_alias_map = {
        "⚡ Fast-Track Pipeline (Pemula)": "⚡ Generator Konten (Pipeline & Sprint)",
        "⚡ Fast-Track Pipeline": "⚡ Generator Konten (Pipeline & Sprint)",
        "🗂️ Studio Produksi (Kanban)": "🗂️ Studio Produksi & Teleprompter",
        "🗂️ Studio Produksi": "🗂️ Studio Produksi & Teleprompter",
        "📡 Trend Radar": "📡 Trend Radar & Celah Pasar",
        "🔬 Bedah Video Viral": "🔬 Bedah Video Viral (Reverse Eng.)",
        "🪝 Hook Generator": "🪝 Hook & Closing CTA Lab",
        "💰 Monetization Bridge": "🪝 Hook & Closing CTA Lab",
        "⭐ Koleksi Skrip": "⭐ Brankas Konten & Master Stok",
        "⚙️ Pengaturan AI & API": "⚙️ Pengaturan & Panduan Engine",
        "📖 Panduan & Monetisasi": "⚙️ Pengaturan & Panduan Engine"
    }

    # Sinkronisasi navigasi terprogram antar-halaman
    if "_target_nav" in st.session_state:
        target = st.session_state.pop("_target_nav")
        target = nav_alias_map.get(target, target)
        if target in nav_options:
            st.session_state["active_nav"] = target
            st.session_state["nav_radio"] = target
            st.session_state["_current_nav"] = target
    elif st.session_state.get("active_nav") != st.session_state.get("_current_nav"):
        target = st.session_state.get("active_nav")
        target = nav_alias_map.get(target, target)
        if target in nav_options:
            st.session_state["nav_radio"] = target
            st.session_state["_current_nav"] = target
            st.session_state["active_nav"] = target
    elif "nav_radio" not in st.session_state or st.session_state["nav_radio"] not in nav_options:
        cur_act = st.session_state.get("active_nav", nav_options[0])
        st.session_state["nav_radio"] = nav_alias_map.get(cur_act, nav_options[0])

    def _on_nav_change():
        st.session_state["active_nav"] = st.session_state["nav_radio"]
        st.session_state["_current_nav"] = st.session_state["nav_radio"]
        if st.session_state["nav_radio"] == "⚡ Generator Konten (Pipeline & Sprint)":
            # Jika tidak sedang mengedit draf tertentu dan step tertinggal di 5, kembalikan ke Tahap 1
            if st.session_state.get("pipeline_step") == 5 and not st.session_state.get("current_pipeline_draft_id"):
                st.session_state["pipeline_step"] = 1

    selected_nav = st.radio(
        "Pilih Modul:",
        nav_options,
        key="nav_radio",
        on_change=_on_nav_change,
        label_visibility="collapsed"
    )
    st.session_state["active_nav"] = selected_nav
    st.session_state["_current_nav"] = selected_nav

    st.markdown("---")

    # --- SELECTOR PERSONA GAYA BICARA KREATOR ---
    st.markdown("### 🎭 Persona Gaya Bicara")
    from utils.prompts import CREATOR_PERSONAS
    persona_labels = [p["label"] for p in CREATOR_PERSONAS.values()]
    persona_keys = list(CREATOR_PERSONAS.keys())

    cur_p = st.session_state.get("creator_persona", "santai")
    idx_p = persona_keys.index(cur_p) if cur_p in persona_keys else 0

    sel_persona_lbl = st.selectbox(
        "Karakter & Nada Bicara:",
        persona_labels,
        index=idx_p,
        key="creator_persona_sidebar",
        label_visibility="collapsed",
        help="AI akan menyesuaikan kosakata, intonasi, struktur kalimat, dan ritme naskah sesuai kepribadian unik Anda."
    )
    chosen_pkey = persona_keys[persona_labels.index(sel_persona_lbl)]
    st.session_state["creator_persona"] = chosen_pkey
    st.session_state["creator_persona_label"] = sel_persona_lbl
    st.caption(f"💡 *{CREATOR_PERSONAS[chosen_pkey]['tone']}*")

    st.markdown("---")

    # --- KONFIGURASI AI ENGINE (COMPACT & RINGKAS) ---
    st.markdown("### 🧠 Mesin Kecerdasan AI")

    ai_provider = st.selectbox(
        "AI Provider:",
        [
            "Google Gemini (Gratis 1.500 Req/Hari)",
            "Groq Cloud (100% Gratis & Kilat)",
            "DeepSeek (V3 & R1)",
            "Qwen (Alibaba Cloud)",
            "Ollama (Lokal 100% Offline)",
            "OpenAI (GPT-4o)",
            "Anthropic (Claude 3.5)",
            "OpenRouter (Universal)",
            "Mode Simulasi (Demo Tanpa Key)"
        ],
        index=0,
        label_visibility="collapsed"
    )

    provider_map = {
        "Google Gemini (Gratis 1.500 Req/Hari)": "gemini",
        "Groq Cloud (100% Gratis & Kilat)": "groq",
        "DeepSeek (V3 & R1)": "deepseek",
        "Qwen (Alibaba Cloud)": "qwen",
        "Ollama (Lokal 100% Offline)": "ollama",
        "OpenAI (GPT-4o)": "openai",
        "Anthropic (Claude 3.5)": "anthropic",
        "OpenRouter (Universal)": "openrouter",
        "Mode Simulasi (Demo Tanpa Key)": "demo"
    }

    active_provider = provider_map[ai_provider]
    user_api_key = None
    custom_base_url = None
    model_name = ""

    # Ambil kunci tersimpan otomatis dari .env
    if active_provider == "gemini":
        user_api_key = get_env_var("GEMINI_API_KEY", "")
        model_name = "gemini-2.0-flash"
    elif active_provider == "groq":
        user_api_key = get_env_var("GROQ_API_KEY", "")
        model_name = "llama-3.3-70b-versatile"
    elif active_provider == "deepseek":
        user_api_key = get_env_var("DEEPSEEK_API_KEY", "")
        model_name = "deepseek-chat"
    elif active_provider == "qwen":
        user_api_key = get_env_var("DASHSCOPE_API_KEY", "")
        model_name = "qwen-plus"
        custom_base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
    elif active_provider == "openai":
        user_api_key = get_env_var("OPENAI_API_KEY", "")
        model_name = "gpt-4o"
    elif active_provider == "anthropic":
        user_api_key = get_env_var("ANTHROPIC_API_KEY", "")
        model_name = "claude-3-5-sonnet-20241022"
    elif active_provider == "ollama":
        user_api_key = "ollama-local"
        model_name = "qwen2.5:latest"
        custom_base_url = "http://localhost:11434/v1"
    elif active_provider == "openrouter":
        user_api_key = get_env_var("OPENROUTER_API_KEY", "")
        model_name = "deepseek/deepseek-chat"
    else:
        model_name = "simulated-engine"

    # Expander Kunci API & Model (Tetap ringkas & tidak mengacaukan sidebar)
    with st.expander("⚙️ Ubah Kunci / Model AI", expanded=False):
        if active_provider == "gemini":
            user_api_key = st.text_input("Gemini API Key:", type="password", value=user_api_key, placeholder="AIzaSy...")
            model_name = st.selectbox("Model Gemini:", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
            if user_api_key: save_env_var("GEMINI_API_KEY", user_api_key)
        elif active_provider == "groq":
            user_api_key = st.text_input("Groq API Key:", type="password", value=user_api_key, placeholder="gsk_...")
            model_name = st.selectbox("Model Groq:", ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b", "mixtral-8x7b-32768"])
            if user_api_key: save_env_var("GROQ_API_KEY", user_api_key)
        elif active_provider == "deepseek":
            user_api_key = st.text_input("DeepSeek Key:", type="password", value=user_api_key, placeholder="sk-...")
            model_name = st.selectbox("Model DeepSeek:", ["deepseek-chat", "deepseek-reasoner"])
            if user_api_key: save_env_var("DEEPSEEK_API_KEY", user_api_key)
        elif active_provider == "openai":
            user_api_key = st.text_input("OpenAI Key:", type="password", value=user_api_key, placeholder="sk-...")
            model_name = st.selectbox("Model OpenAI:", ["gpt-4o", "gpt-4o-mini"])
            if user_api_key: save_env_var("OPENAI_API_KEY", user_api_key)
        elif active_provider == "qwen":
            user_api_key = st.text_input("DashScope Key:", type="password", value=user_api_key, placeholder="sk-...")
            model_name = st.selectbox("Model Qwen:", ["qwen-plus", "qwen-max", "qwen-turbo"])
            if user_api_key: save_env_var("DASHSCOPE_API_KEY", user_api_key)
        elif active_provider == "ollama":
            custom_base_url = st.text_input("Ollama Base URL:", value=custom_base_url or "http://localhost:11434/v1")
            model_name = st.text_input("Nama Model di Ollama:", value=model_name or "qwen2.5:latest")
        else:
            st.caption("Mode simulasi aktif tanpa kunci API.")

    # Inisialisasi AI Client
    client = AIClient(
        provider=active_provider,
        api_key=user_api_key,
        model=model_name,
        base_url=custom_base_url
    )

    # Status Pill dengan LED Indicator
    if client.is_configured():
        st.markdown(f"""
        <div class="sidebar-status-card">
            <span class="led-dot" style="background-color: #16a34a; color: #16a34a;"></span>
            <div><b style="color:#0f172a;">Status:</b> <span style="color:#16a34a; font-weight:600;">{active_provider.upper()} ({model_name.split('/')[-1][:12]})</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-status-card">
            <span class="led-dot" style="background-color: #d97706; color: #d97706;"></span>
            <div><b style="color:#0f172a;">Status:</b> <span style="color:#d97706; font-weight:600;">Mode Demo Siap Pakai</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.78rem; color: #64748b; text-align: center;">
        ViralGenix v2.0 &bull; Continuous Engine<br>
        <i>Growth & Virality Architecture</i>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# HELPER VIEWS: BRANKAS MASTER & PENGATURAN ENGINE
# =============================================================================

def render_vault_master_page():
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">ASET & PENYIMPANAN</div>
        <h1 class="module-title">⭐ Brankas Konten & Master Stok</h1>
        <p class="module-desc">
            Pusat penyimpanan permanen seluruh proyek video pendek Anda. Akses naskah, subtitle CapCut, 
            caption siap posting, serta unduh paket produksi master dalam satu tempat.
        </p>
    </div>
    """, unsafe_allow_html=True)

    vault = load_vault()

    # KPI Summary Counters
    count_all = len(vault)
    count_ready_shoot = sum(1 for d in vault if d.get("status") in ["📝 Skrip Selesai", "🎙️ Siap Syuting"])
    count_ready_post = sum(1 for d in vault if d.get("status") == "🚀 Siap Posting")
    count_done = sum(1 for d in vault if d.get("status") == "✅ Sudah Tayang")

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-pill"><span class="kpi-pill-lbl">Total Proyek:</span> <span class="kpi-pill-val">{count_all} Video 📁</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">Siap Syuting:</span> <span class="kpi-pill-val" style="color:#4f46e5;">{count_ready_shoot}</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">Siap Upload:</span> <span class="kpi-pill-val" style="color:#16a34a;">{count_ready_post}</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">Sudah Tayang:</span> <span class="kpi-pill-val" style="color:#64748b;">{count_done}</span></div>
    </div>
    """, unsafe_allow_html=True)

    if not vault:
        with st.container(border=True):
            st.info("💡 Belum ada proyek di Brankas. Mulai racik video pertama Anda di menu **'⚡ Generator Konten (Pipeline & Sprint)'**.")
            if st.button("🚀 Buat Konten Pertama Sekarang", type="primary"):
                st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.rerun()
        return

    # Master Export & Action Bar
    col_mb1, col_mb2 = st.columns([1.5, 1])
    with col_mb1:
        master_zip = generate_all_vault_bundle_zip(vault)
        st.download_button(
            label=f"📦 Unduh Seluruh Proyek ({count_all} Video) - Master .ZIP",
            data=master_zip,
            file_name="ViralGenix_Master_Stok_Konten.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
    with col_mb2:
        if st.button("➕ Buat Video Baru di Pipeline", use_container_width=True):
            st.session_state["pipeline_step"] = 1
            st.session_state["current_pipeline_draft_id"] = None
            st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
            st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter & Search Bar
    col_s1, col_s2 = st.columns([1.5, 1])
    with col_s1:
        search_query = st.text_input("🔍 Cari Judul, Topik, atau Kata Kunci:", placeholder="Ketik pencarian...")
    with col_s2:
        filter_status = st.selectbox(
            "Filter Status:",
            ["Semua Status", "💡 Ide & Riset", "🎙️ Siap Syuting", "🎬 Editing CapCut", "🚀 Siap Posting", "✅ Sudah Tayang"]
        )

    # Filter Logic
    filtered_items = vault
    if search_query.strip():
        q = search_query.lower()
        filtered_items = [d for d in filtered_items if q in d.get("title", "").lower() or q in d.get("keyword", "").lower() or q in d.get("niche", "").lower()]
    if filter_status != "Semua Status":
        filtered_items = [d for d in filtered_items if d.get("status") == filter_status or (filter_status == "🎙️ Siap Syuting" and d.get("status") == "📝 Skrip Selesai")]

    st.caption(f"Menampilkan **{len(filtered_items)}** dari {len(vault)} video tersimpan:")

    for idx, item in enumerate(filtered_items):
        draft_id = item.get("id", f"draft_{idx}")
        with st.container(border=True):
            st.markdown(f"#### 🎬 {idx+1}. {item.get('title', 'Draf Video')}")
            st.caption(f"🏷️ `{item.get('niche', 'Umum')}` | Platform: `{item.get('platform', 'Semua')}` | Status: **{item.get('status', 'Draf')}** | Durasi: `~{item.get('est_duration_sec', 60)}s`")
            
            if item.get("hook_verbal"):
                st.markdown(f"**Hook 3 Detik:** *\"{item.get('hook_verbal')}\"*")

            with st.expander("👁️ Lihat Detail Naskah & Storyboard", expanded=False):
                st.markdown(item.get("storyboard_table_md", "_Belum ada naskah dialog._"))

            col_card_p1, col_card_p2, col_card_p3 = st.columns([1.5, 1.2, 0.6])
            with col_card_p1:
                if st.button("⚡ Buka di Pipeline Wizard", key=f"v_open_pipe_{idx}_{draft_id}", type="primary", use_container_width=True):
                    st.session_state["current_pipeline_draft_id"] = draft_id
                    st.session_state["pipe_keyword"] = item.get("keyword", "")
                    st.session_state["pipe_keyword_input"] = item.get("keyword", "")
                    st.session_state["pipe_topic_for_hook"] = item.get("content_angle") or item.get("title", "")
                    st.session_state["pipe_chosen_hook"] = item.get("hook_verbal", "")
                    st.session_state["pipe_story_topic"] = item.get("content_angle") or item.get("title", "")
                    st.session_state["pipe_product_input"] = item.get("product_name", "")
                    st.session_state["pipe_step3_result"] = item.get("storyboard_table_md", "")
                    st.session_state["pipeline_step"] = 3
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.rerun()

            with col_card_p2:
                zip_data = generate_draft_bundle_zip(item)
                st.download_button(
                    label="📦 Unduh Paket .ZIP",
                    data=zip_data,
                    file_name=f"ViralGenix_{draft_id}.zip",
                    mime="application/zip",
                    key=f"v_down_zip_{idx}_{draft_id}",
                    use_container_width=True
                )

            with col_card_p3:
                if st.button("🗑️ Hapus", key=f"v_del_{idx}_{draft_id}", use_container_width=True):
                    delete_draft(draft_id)
                    st.rerun()


def render_settings_and_guide_page(cur_provider, cur_model, ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">KONFIGURASI & PANDUAN</div>
        <h1 class="module-title">⚙️ Pengaturan & Panduan Engine</h1>
        <p class="module-desc">
            Pusat manajemen kunci API permanen, uji diagnostik respon mesin AI, 
            serta panduan SOP monetisasi dari A sampai Z.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_api, tab_persona, tab_guide = st.tabs([
        "⚙️ Kunci API & Diagnostik Mesin",
        "🎭 Karakter & Panduan Persona Suara",
        "📖 Blueprint Bisnis & SOP Monetisasi"
    ])

    with tab_api:
        with st.container(border=True):
            st.markdown("#### 🧪 Diagnostik Uji Respon Mesin AI")
            st.write(f"Provider Aktif: **{cur_provider}** | Model: `{cur_model}` | Status: `{('Terhubung' if ai_client.is_configured() else 'Mode Demo Tanpa Key')}`")

            if st.button("⚡ Uji Respon & Koneksi API Sekarang", type="primary", use_container_width=True):
                with st.spinner(f"Mengirim ping pengujian ke server {cur_provider}..."):
                    start_t = time.time()
                    try:
                        reply = ai_client.generate(
                            prompt="Jawab singkat 1 kalimat: Apakah sistem ViralGenix siap membuat konten viral hari ini?",
                            system_prompt="Kamu adalah AI tester. Jawab ramah dan bersemangat dalam bahasa Indonesia."
                        )
                        elapsed = round(time.time() - start_t, 2)
                        st.success(f"✅ Koneksi Berhasil! Waktu respon: **{elapsed} detik**.")
                        st.markdown(f"**Respon AI:** *\"{reply.strip()}\"*")
                    except Exception as e:
                        st.error(f"❌ Gagal Terhubung: {str(e)}")

        with st.container(border=True):
            st.markdown("#### 🔐 Penyimpanan Kunci API Permanen (.env)")
            st.caption("Kunci yang Anda simpan di sini otomatis ditulis ke file `.env` di komputer Anda sehingga aman, tersimpan permanen, dan tidak perlu diketik ulang setiap buka aplikasi.")

            with st.form("form_permanent_keys"):
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    input_gemini = st.text_input("Google Gemini API Key:", value=get_env_var("GEMINI_API_KEY", ""), type="password")
                    input_groq = st.text_input("Groq Cloud API Key:", value=get_env_var("GROQ_API_KEY", ""), type="password")
                    input_deepseek = st.text_input("DeepSeek API Key:", value=get_env_var("DEEPSEEK_API_KEY", ""), type="password")
                with col_k2:
                    input_openai = st.text_input("OpenAI API Key:", value=get_env_var("OPENAI_API_KEY", ""), type="password")
                    input_anthropic = st.text_input("Anthropic API Key:", value=get_env_var("ANTHROPIC_API_KEY", ""), type="password")
                    input_qwen = st.text_input("Qwen / DashScope Key:", value=get_env_var("DASHSCOPE_API_KEY", ""), type="password")

                btn_save = st.form_submit_button("💾 Simpan Semua Kunci Permanen ke .env", type="primary", use_container_width=True)
                if btn_save:
                    if input_gemini: save_env_var("GEMINI_API_KEY", input_gemini)
                    if input_groq: save_env_var("GROQ_API_KEY", input_groq)
                    if input_deepseek: save_env_var("DEEPSEEK_API_KEY", input_deepseek)
                    if input_openai: save_env_var("OPENAI_API_KEY", input_openai)
                    if input_anthropic: save_env_var("ANTHROPIC_API_KEY", input_anthropic)
                    if input_qwen: save_env_var("DASHSCOPE_API_KEY", input_qwen)
                    st.success("✅ Kunci API berhasil disimpan secara permanen!")
                    st.rerun()

    with tab_persona:
        st.markdown("#### 🎭 4 Karakter Persona Gaya Bicara Kreator")
        st.caption("Pilih persona di sidebar untuk otomatis menyesuaikan seluruh naskah narasi, kalimat hook, dan closing CTA sesuai persona Anda.")

        from utils.prompts import CREATOR_PERSONAS
        col_ps1, col_ps2 = st.columns(2)
        items_p = list(CREATOR_PERSONAS.items())

        with col_ps1:
            for k, p in items_p[:2]:
                with st.container(border=True):
                    st.markdown(f"**{p['label']}**")
                    st.caption(f"**Kata Ganti:** `{p['pronouns']}`")
                    st.write(p["tone"])
                    with st.expander("Aturan Bahasa", expanded=False):
                        st.markdown(p["rules"])

        with col_ps2:
            for k, p in items_p[2:]:
                with st.container(border=True):
                    st.markdown(f"**{p['label']}**")
                    st.caption(f"**Kata Ganti:** `{p['pronouns']}`")
                    st.write(p["tone"])
                    with st.expander("Aturan Bahasa", expanded=False):
                        st.markdown(p["rules"])

    with tab_guide:
        st.markdown("### 📖 Blueprint Bisnis & SOP Monetisasi")
        st.markdown("""
        #### 1. In-House Media Engine (SOP 30 Menit Harian)
        - **00 - 05 Menit**: Buka **Bedah Video Viral** untuk mencuri sudut pandang video kompetitor yang sedang meledak.
        - **05 - 15 Menit**: Jalankan **Generator Konten (Pipeline)** untuk mendapatkan naskah 60s dan closing bridge.
        - **15 - 25 Menit**: Masuk ke **Studio Teleprompter** untuk syuting di kamera HP dengan panduan auto-scroll.
        - **25 - 30 Menit**: Salin 1-klik Caption & 10 Hashtag saat upload ke TikTok/Reels di jam prime time!

        ---
        #### 2. Formula Retensi Video Pendek (Standar Industri)
        | Bagian | Detik | Target Psikologis | Formula Utama |
        |---|---|---|---|
        | **Hook Pembuka** | 0 - 3s | Kejut dopamin & stop scroll | Kalimat peringatan / FOMO ekstrem |
        | **Agitasi Masalah** | 3 - 15s | Menyadarkan kerugian | Bukti nyata & rasa sakit yang relate |
        | **Pattern Interrupt** | 15 - 25s | Mencegah penonton kabur | Data mengejutkan / plot twist |
        | **Solusi Praktis** | 25 - 45s | Memberi pencerahan | 3 langkah mudah langsung coba |
        | **Closing Bridge** | 45 - 60s | Konversi halus | Solusi lanjutan ke link di bio |
        """)


# =============================================================================
# ROUTING HALAMAN UTAMA (CLEAN 3-ZONE ARCHITECTURE)
# =============================================================================

if selected_nav == "⚡ Generator Konten (Pipeline & Sprint)":
    render_fast_track_pipeline(client)

elif selected_nav == "🗂️ Studio Produksi & Teleprompter":
    render_production_studio(client)

elif selected_nav == "🎯 Bedah & Blueprint Akun (Growth A-Z)":
    render_account_growth_audit(client)

elif selected_nav == "🔬 Bedah Video Viral (Reverse Eng.)":
    render_video_analyzer(client)

elif selected_nav == "📡 Trend Radar & Celah Pasar":
    render_trend_radar(client)

elif selected_nav == "🪝 Hook & Closing CTA Lab":
    render_hook_cta_lab(client)

elif selected_nav == "⭐ Brankas Konten & Master Stok":
    render_vault_master_page()

elif selected_nav == "⚙️ Pengaturan & Panduan Engine":
    render_settings_and_guide_page(ai_provider, model_name, client)
