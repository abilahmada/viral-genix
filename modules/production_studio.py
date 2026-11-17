"""
ViralGenix - Modul Studio Produksi & Papan Kanban (Production Studio)
Papan kendali visual untuk melacak dan memproduksi video pendek dari ide awal,
syuting dengan teleprompter interaktif berkecepatan baca teratur (WPM),
editing CapCut, hingga siap diposting ke TikTok/Reels dengan 1-klik salin caption & hashtag.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from utils.vault_manager import (
    load_vault,
    update_draft,
    delete_draft,
    change_draft_status,
    generate_draft_bundle_zip,
    generate_all_vault_bundle_zip,
    extract_copywriting_kit,
    extract_clean_speech_dialogue,
    extract_closing_bridge,
    STATUS_OPTIONS
)
from utils.export_helpers import prepare_markdown_download
from utils.niche_data import COMPREHENSIVE_NICHES


def render_production_studio(ai_client):
    st.markdown("""
    <div class="module-header">
        <div class="module-badge">STUDIO PRODUKSI & KANBAN</div>
        <h1 class="module-title">🗂️ Studio Produksi Konten Berkelanjutan</h1>
        <p class="module-desc">
            Papan kendali visual untuk memantau alur pembuatan video Anda dari tahap ide, syuting, 
            editing CapCut, hingga siap di-upload ke TikTok, Instagram Reels, dan YouTube Shorts.
        </p>
    </div>
    """, unsafe_allow_html=True)

    vault = load_vault()

    # --- KPI SUMMARY COUNTERS ---
    count_idea = sum(1 for d in vault if d.get("status") == "💡 Ide & Riset")
    count_shoot = sum(1 for d in vault if d.get("status") in ["📝 Skrip Selesai", "🎙️ Siap Syuting"])
    count_edit = sum(1 for d in vault if d.get("status") == "🎬 Editing CapCut")
    count_ready = sum(1 for d in vault if d.get("status") == "🚀 Siap Posting")
    count_done = sum(1 for d in vault if d.get("status") == "✅ Sudah Tayang")

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-pill"><span class="kpi-pill-lbl">💡 Ide Baru:</span> <span class="kpi-pill-val">{count_idea}</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">🎙️ Siap Syuting:</span> <span class="kpi-pill-val" style="color:#4f46e5;">{count_shoot}</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">🎬 Editing CapCut:</span> <span class="kpi-pill-val" style="color:#0284c7;">{count_edit}</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">🚀 Siap Posting:</span> <span class="kpi-pill-val" style="color:#16a34a;">{count_ready}</span></div>
        <div class="kpi-pill"><span class="kpi-pill-lbl">✅ Sudah Tayang:</span> <span class="kpi-pill-val" style="color:#64748b;">{count_done}</span></div>
    </div>
    """, unsafe_allow_html=True)

    tab_kanban, tab_teleprompter, tab_table, tab_scheduler = st.tabs([
        "📋 Papan Alur Kanban (Visual)",
        "🎙️ Studio Teleprompter (Siap Rekam)",
        "📊 Tabel Daftar Kerja (Checklist)",
        "📅 Kalender Rilis Mingguan (Scheduler)"
    ])

    # =========================================================================
    # TAB 1: PAPAN KANBAN VISUAL (DENGAN 1-KLIK GESER STATUS & SALIN CEPAT)
    # =========================================================================
    with tab_kanban:
        if not vault:
            with st.container(border=True):
                st.info("""
                💡 **Belum ada proyek konten di Brankas.**
                
                Untuk memulai, buka menu **'⚡ Generator Konten (Pipeline & Sprint)'** di sidebar untuk meracik ide konten pertama Anda dalam 5 langkah mudah!
                """)
                if st.button("🚀 Buka Generator Konten Sekarang", type="primary"):
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.rerun()
            return

        col_bar1, col_bar2 = st.columns([1.5, 1])
        with col_bar1:
            all_zip_data = generate_all_vault_bundle_zip(vault)
            st.download_button(
                label=f"📦 Unduh Seluruh Proyek ({len(vault)} Video) - Master .ZIP",
                data=all_zip_data,
                file_name="ViralGenix_Master_Stok_Konten.zip",
                mime="application/zip",
                use_container_width=True
            )
        with col_bar2:
            if st.button("➕ Buat Video Baru di Pipeline", type="primary", use_container_width=True):
                st.session_state["pipeline_step"] = 1
                st.session_state["current_pipeline_draft_id"] = None
                st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5, gap="small")

        # Kolom 1: Ide & Riset
        with col_k1:
            st.markdown("#### 💡 1. Ide & Riset")
            st.caption("Konsep & celah tren")
            items_step1 = [d for d in vault if d.get("status") == "💡 Ide & Riset"]
            if not items_step1:
                st.markdown("<div style='color:#94a3b8; font-size:0.82rem; padding:10px; background:#f8fafc; border-radius:8px; text-align:center;'>Kosong</div>", unsafe_allow_html=True)
            for idx, item in enumerate(items_step1):
                _render_kanban_card(item, f"col1_{idx}")

        # Kolom 2: Siap Syuting
        with col_k2:
            st.markdown("#### 🎙️ 2. Siap Syuting")
            st.caption("Skrip & naskah siap")
            items_step2 = [d for d in vault if d.get("status") in ["📝 Skrip Selesai", "🎙️ Siap Syuting"]]
            if not items_step2:
                st.markdown("<div style='color:#94a3b8; font-size:0.82rem; padding:10px; background:#f8fafc; border-radius:8px; text-align:center;'>Kosong</div>", unsafe_allow_html=True)
            for idx, item in enumerate(items_step2):
                _render_kanban_card(item, f"col2_{idx}")

        # Kolom 3: Editing CapCut
        with col_k3:
            st.markdown("#### 🎬 3. Editing CapCut")
            st.caption("B-Roll & Subtitle SRT")
            items_step3 = [d for d in vault if d.get("status") == "🎬 Editing CapCut"]
            if not items_step3:
                st.markdown("<div style='color:#94a3b8; font-size:0.82rem; padding:10px; background:#f8fafc; border-radius:8px; text-align:center;'>Kosong</div>", unsafe_allow_html=True)
            for idx, item in enumerate(items_step3):
                _render_kanban_card(item, f"col3_{idx}")

        # Kolom 4: Siap Upload (Hanya yang siap diposting ke medsos)
        with col_k4:
            st.markdown("#### 🚀 4. Siap Upload")
            st.caption("Caption & tag siap")
            items_step4 = [d for d in vault if d.get("status") == "🚀 Siap Posting"]
            if not items_step4:
                st.markdown("<div style='color:#94a3b8; font-size:0.82rem; padding:10px; background:#f8fafc; border-radius:8px; text-align:center;'>Kosong</div>", unsafe_allow_html=True)
            for idx, item in enumerate(items_step4):
                _render_kanban_card(item, f"col4_{idx}")

        # Kolom 5: Sudah Tayang (Arsip konten yang sudah live)
        with col_k5:
            st.markdown("#### ✅ 5. Sudah Tayang")
            st.caption("Live di media sosial")
            items_step5 = [d for d in vault if d.get("status") == "✅ Sudah Tayang"]
            if not items_step5:
                st.markdown("<div style='color:#94a3b8; font-size:0.82rem; padding:10px; background:#f8fafc; border-radius:8px; text-align:center;'>Kosong</div>", unsafe_allow_html=True)
            for idx, item in enumerate(items_step5):
                _render_kanban_card(item, f"col5_{idx}")

    # =========================================================================
    # TAB 2: MODE TELEPROMPTER KHUSUS SYUTING (AUTO-SCROLL & HP FRIENDLY)
    # =========================================================================
    with tab_teleprompter:
        st.markdown("### 🎙️ Studio Teleprompter & Perekaman HP")
        st.caption("Gunakan mode ini saat Anda merekam video di depan kamera HP. Teks dialog dialirkan otomatis dengan kecepatan baca terukur dan penanda fokus mata.")

        ready_to_shoot = [d for d in vault if d.get("storyboard_table_md")]
        if not ready_to_shoot:
            st.info("Belum ada video yang memiliki naskah dialog. Buat skrip terlebih dahulu melalui menu **'⚡ Fast-Track Pipeline'**.")
        else:
            draft_options = {d["id"]: f"{d.get('title', 'Konten')} ({d.get('platform', '-')})" for d in ready_to_shoot}
            selected_id = st.selectbox(
                "Pilih Video yang Mau Disyuting Hari Ini:",
                options=list(draft_options.keys()),
                format_func=lambda x: draft_options[x]
            )
            selected_draft = next((d for d in ready_to_shoot if d["id"] == selected_id), None)

            if selected_draft:
                col_tele_meta1, col_tele_meta2 = st.columns([1.2, 1])
                with col_tele_meta1:
                    st.write(f"**Target Platform:** `{selected_draft.get('platform', 'Semua')}`")
                    st.write(f"**Status Saat Ini:** `{selected_draft.get('status', '-')}`")
                with col_tele_meta2:
                    if st.button("✅ Tandai Selesai Syuting ➔ Pindah ke Editing CapCut", type="primary", use_container_width=True):
                        change_draft_status(selected_id, "🎬 Editing CapCut")
                        st.toast("Status berhasil diubah ke '🎬 Editing CapCut'!", icon="🎬")
                        st.rerun()

                st.markdown("---")
                
                # --- PENGATURAN TELEPROMPTER ---
                col_ctl1, col_ctl2, col_ctl3 = st.columns([1, 1, 1])
                with col_ctl1:
                    font_size_opt = st.selectbox(
                        "🔠 Ukuran Teks:",
                        ["22px (Sedang)", "28px (Besar - Nyaman)", "36px (Raksasa - Khusus HP Jarak Jauh)"],
                        index=1
                    )
                    font_px = font_size_opt.split()[0]
                with col_ctl2:
                    pacing_wpm_opt = st.selectbox(
                        "⚡ Kecepatan Baca (Pacing):",
                        ["110 WPM (Santai & Emosional)", "135 WPM (Normal Percakapan)", "165 WPM (Cepat - High Dopamine)"],
                        index=1
                    )
                    wpm_val = int(pacing_wpm_opt.split()[0])
                with col_ctl3:
                    mirror_mode = st.checkbox(
                        "🪞 Mode Cermin (Mirror)",
                        value=False,
                        help="Aktifkan jika Anda menggunakan rigging cermin / teleprompter glass rig depan kamera."
                    )

                clean_dialogue = extract_clean_speech_dialogue(selected_draft)
                speech_words = len(clean_dialogue.split())
                est_sec = max(20, round((speech_words / wpm_val) * 60))

                st.markdown(f"""
                <div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 10px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 0.88rem; color: #1e1b4b;">
                    📊 <b>Pacing Monitor:</b> Naskah berisi <b>{speech_words} kata</b>. Pada kecepatan <b>{wpm_val} WPM</b>, estimasi durasi video adalah <b>~{est_sec} detik</b>.
                </div>
                """, unsafe_allow_html=True)

                # Format Dialog untuk HTML Scroller
                hook_text = selected_draft.get("hook_verbal", "").strip()
                closing_text = selected_draft.get("closing_bridge_script", "").strip()
                if not closing_text:
                    closing_text = extract_closing_bridge(selected_draft)

                # Paragraf-paragraf naskah dengan Deteksi Tag Karakter & Voiceover
                import re
                paras = [p.strip() for p in clean_dialogue.split("\n\n") if p.strip()]
                html_paras = []
                for p in paras:
                    # Deteksi apakah ada tag karakter di awal: [Nama Karakter]: "..." atau Nama Karakter: "..."
                    spk_m = re.match(r'^\s*\[([^\]]+)\]\s*:\s*(.*)', p, re.DOTALL)
                    if not spk_m:
                        spk_m = re.match(r'^(Kreator|Voiceover|Si Skeptis|Si Praktisi|Talent|Karakter \w+|Tokoh \w+)\s*:\s*(.*)', p, re.DOTALL | re.IGNORECASE)

                    if spk_m:
                        spk_name = spk_m.group(1).strip()
                        spk_speech = spk_m.group(2).strip().strip('"').strip()
                        spk_l = spk_name.lower()
                        if any(w in spk_l for w in ["skeptis", "boros", "korban", "pembeli"]):
                            char_class = "char-amber"
                            badge_color = "#f59e0b"
                        elif any(w in spk_l for w in ["voiceover", "narator", "audio"]):
                            char_class = "char-indigo"
                            badge_color = "#818cf8"
                        elif any(w in spk_l for w in ["praktisi", "ahli", "solusi", "cermat", "penjual"]):
                            char_class = "char-emerald"
                            badge_color = "#10b981"
                        else:
                            char_class = "char-cyan"
                            badge_color = "#06b6d4"

                        html_paras.append(
                            f'<div class="body-para {char_class}">'
                            f'<div class="char-pill" style="border-color:{badge_color}; color:{badge_color};">🗣️ {spk_name}</div>'
                            f'"{spk_speech}"'
                            f'</div>'
                        )
                    elif hook_text and hook_text.lower() in p.lower():
                        html_paras.append(f'<div class="hook-box"><div class="hook-label">🔥 HOOK 3 DETIK PERTAMA</div><div class="hook-text">"{p}"</div></div>')
                    elif closing_text and closing_text.lower() in p.lower():
                        html_paras.append(f'<div class="cta-box"><div class="cta-label">🎯 JEMBATAN PENUTUP & CTA</div><div class="cta-text">"{p}"</div></div>')
                    else:
                        html_paras.append(f'<div class="body-para">{p}</div>')

                dialogue_html_content = "".join(html_paras)
                mirror_class = "mirror-mode" if mirror_mode else ""

                # Komponen HTML / JS Teleprompter
                prompter_component_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                <style>
                  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                  body {{
                    background: #090d16;
                    color: #f8fafc;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    overflow: hidden;
                    height: 520px;
                    user-select: none;
                  }}
                  .prompter-toolbar {{
                    position: absolute;
                    top: 0; left: 0; right: 0;
                    height: 54px;
                    background: rgba(15, 23, 42, 0.95);
                    backdrop-filter: blur(8px);
                    border-bottom: 1px solid #334155;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0 16px;
                    z-index: 100;
                  }}
                  .btn-grp {{
                    display: flex;
                    gap: 8px;
                    align-items: center;
                  }}
                  .btn {{
                    background: #1e293b;
                    color: #ffffff;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    padding: 6px 14px;
                    font-size: 13px;
                    font-weight: 700;
                    cursor: pointer;
                    transition: all 0.15s ease;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  }}
                  .btn:hover {{
                    background: #334155;
                    border-color: #94a3b8;
                  }}
                  .btn-primary {{
                    background: #4f46e5;
                    border-color: #6366f1;
                  }}
                  .btn-primary:hover {{
                    background: #4338ca;
                  }}
                  .timer-pill {{
                    background: #020617;
                    border: 1px solid #334155;
                    border-radius: 20px;
                    padding: 5px 12px;
                    font-family: monospace;
                    font-size: 14px;
                    font-weight: 700;
                    color: #38bdf8;
                    letter-spacing: 1px;
                  }}
                  .speed-lbl {{
                    font-size: 12px;
                    color: #94a3b8;
                    font-weight: 600;
                  }}
                  .guide-overlay {{
                    position: absolute;
                    top: 36%;
                    left: 0;
                    right: 0;
                    height: 75px;
                    background: rgba(79, 70, 229, 0.15);
                    border-top: 2px dashed rgba(129, 140, 248, 0.7);
                    border-bottom: 2px dashed rgba(129, 140, 248, 0.7);
                    pointer-events: none;
                    z-index: 50;
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    padding-right: 16px;
                  }}
                  .guide-tag {{
                    background: #4f46e5;
                    color: #ffffff;
                    font-size: 10px;
                    font-weight: 800;
                    padding: 3px 8px;
                    border-radius: 10px;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                  }}
                  .scroll-container {{
                    height: 520px;
                    overflow-y: scroll;
                    scroll-behavior: auto;
                    padding: 130px 30px 260px 30px;
                    scrollbar-width: none;
                    -ms-overflow-style: none;
                  }}
                  .scroll-container::-webkit-scrollbar {{ display: none; }}
                  .script-content {{
                    max-width: 760px;
                    margin: 0 auto;
                    font-size: {font_px};
                    line-height: 1.65;
                    font-weight: 600;
                    text-align: left;
                    transition: transform 0.2s ease;
                  }}
                  .mirror-mode {{
                    transform: scaleX(-1);
                  }}
                  .hook-box {{
                    background: #1e1b4b;
                    border-left: 5px solid #818cf8;
                    padding: 14px 18px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    color: #e0e7ff;
                  }}
                  .hook-label {{
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    color: #a5b4fc;
                    font-weight: 800;
                    margin-bottom: 4px;
                  }}
                  .hook-text {{
                    font-size: 1.1em;
                    font-weight: 800;
                    color: #ffffff;
                  }}
                  .body-para {{
                    margin-bottom: 20px;
                    color: #f1f5f9;
                  }}
                  .char-pill {{
                    display: inline-block;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    border: 1.5px solid;
                    border-radius: 6px;
                    padding: 2px 8px;
                    margin-bottom: 6px;
                    background: rgba(15, 23, 42, 0.7);
                  }}
                  .char-amber {{ border-left: 4px solid #f59e0b; padding-left: 14px; }}
                  .char-indigo {{ border-left: 4px solid #818cf8; padding-left: 14px; }}
                  .char-emerald {{ border-left: 4px solid #10b981; padding-left: 14px; }}
                  .char-cyan {{ border-left: 4px solid #06b6d4; padding-left: 14px; }}
                  .cta-box {{
                    background: #064e3b;
                    border-left: 5px solid #34d399;
                    padding: 14px 18px;
                    border-radius: 10px;
                    margin-top: 20px;
                    color: #d1fae5;
                  }}
                  .cta-label {{
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    color: #6ee7b7;
                    font-weight: 800;
                    margin-bottom: 4px;
                  }}
                  .cta-text {{
                    font-size: 1.05em;
                    font-weight: 700;
                    color: #ffffff;
                  }}
                </style>
                </head>
                <body>
                  <div class="prompter-toolbar">
                    <div class="btn-grp">
                      <button id="toggleBtn" class="btn btn-primary" onclick="togglePlay()">▶️ Mulai Auto-Scroll</button>
                      <button class="btn" onclick="resetScroll()">🔄 Ulangi</button>
                      <button class="btn" onclick="adjustSpeed(-0.25)">➖ Lebih Lambat</button>
                      <button class="btn" onclick="adjustSpeed(0.25)">➕ Lebih Cepat</button>
                      <span id="speedDisplay" class="speed-lbl">1.0x</span>
                    </div>
                    <div class="timer-pill" id="timerDisplay">⏱️ 00:00 / ~{est_sec//60:02d}:{est_sec%60:02d}</div>
                  </div>

                  <div class="guide-overlay">
                    <span class="guide-tag">👁️ FOKUS MATA KE LENSA HP</span>
                  </div>

                  <div class="scroll-container" id="scrollContainer" onclick="togglePlay()">
                    <div class="script-content {mirror_class}" id="scriptContent">
                      {dialogue_html_content}
                    </div>
                  </div>

                  <script>
                    const container = document.getElementById('scrollContainer');
                    const toggleBtn = document.getElementById('toggleBtn');
                    const timerDisplay = document.getElementById('timerDisplay');
                    const speedDisplay = document.getElementById('speedDisplay');

                    let isPlaying = false;
                    let speedFactor = 1.0;
                    let basePixelsPerFrame = {max(0.6, (speech_words * 4.2) / (est_sec * 60))};
                    let animationFrameId = null;
                    let elapsedSeconds = 0;
                    let timerInterval = null;
                    const targetSec = {est_sec};

                    function formatTime(s) {{
                      const m = Math.floor(s / 60);
                      const sec = s % 60;
                      return (m < 10 ? '0' : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
                    }}

                    function updateTimer() {{
                      if (isPlaying) {{
                        elapsedSeconds++;
                        timerDisplay.innerText = '⏱️ ' + formatTime(elapsedSeconds) + ' / ~' + formatTime(targetSec);
                      }}
                    }}

                    function scrollStep() {{
                      if (isPlaying) {{
                        container.scrollTop += (basePixelsPerFrame * speedFactor);
                        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 5) {{
                          pause();
                          return;
                        }}
                        animationFrameId = requestAnimationFrame(scrollStep);
                      }}
                    }}

                    function play() {{
                      isPlaying = true;
                      toggleBtn.innerHTML = '⏸️ Jeda (Pause)';
                      toggleBtn.classList.remove('btn-primary');
                      if (!timerInterval) {{
                        timerInterval = setInterval(updateTimer, 1000);
                      }}
                      animationFrameId = requestAnimationFrame(scrollStep);
                    }}

                    function pause() {{
                      isPlaying = false;
                      toggleBtn.innerHTML = '▶️ Lanjutkan Scroll';
                      toggleBtn.classList.add('btn-primary');
                      if (animationFrameId) {{
                        cancelAnimationFrame(animationFrameId);
                        animationFrameId = null;
                      }}
                      if (timerInterval) {{
                        clearInterval(timerInterval);
                        timerInterval = null;
                      }}
                    }}

                    function togglePlay() {{
                      if (isPlaying) {{
                        pause();
                      }} else {{
                        play();
                      }}
                    }}

                    function resetScroll() {{
                      pause();
                      container.scrollTop = 0;
                      elapsedSeconds = 0;
                      timerDisplay.innerText = '⏱️ 00:00 / ~' + formatTime(targetSec);
                    }}

                    function adjustSpeed(delta) {{
                      speedFactor = Math.max(0.5, Math.min(3.0, speedFactor + delta));
                      speedDisplay.innerText = speedFactor.toFixed(1) + 'x';
                    }}

                    window.addEventListener('keydown', function(e) {{
                      if (e.code === 'Space') {{
                        e.preventDefault();
                        togglePlay();
                      }} else if (e.code === 'Escape') {{
                        resetScroll();
                      }}
                    }});
                  </script>
                </body>
                </html>
                """

                components.html(prompter_component_html, height=530)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- FITUR 1: 1-KLIK SALIN NASKAH BERSIH KE HP ---
                st.markdown("#### 📋 Salin Naskah Dialog Bersih (1-Klik untuk Teleprompter HP / CapCut)")
                st.caption("Klik tombol salin di sudut kanan atas kotak untuk menyalin seluruh naskah tanpa instruksi kamera.")
                st.code(clean_dialogue, language=None)

                # --- EXPANDER STORYBOARD LENGKAP ---
                with st.expander("🎬 Lihat Tabel Lengkap Storyboard & Arahan B-Roll Kamera", expanded=False):
                    st.markdown(selected_draft.get("storyboard_table_md", ""))

                with st.expander("📋 Lembar Kerja Produksi Per Scene (Siap Copas Editor & Videografer)", expanded=False):
                    from utils.export_helpers import parse_storyboard_scenes, format_scenes_for_production_sheet, parse_master_consistency_anchor
                    sb_raw = selected_draft.get("storyboard_table_md", "")
                    sc_list = parse_storyboard_scenes(sb_raw)
                    m_anchor = parse_master_consistency_anchor(sb_raw)
                    full_sc_text = format_scenes_for_production_sheet(
                        sc_list,
                        title=selected_draft.get("title", "Video"),
                        platform=selected_draft.get("platform", "TikTok / Reels"),
                        master_anchor=m_anchor
                    )
                    st.code(full_sc_text, language="text")

    # =========================================================================
    # TAB 3: TABEL DAFTAR KERJA (CHECKLIST)
    # =========================================================================
    with tab_table:
        st.markdown("### 📊 Ringkasan Seluruh Konten di Brankas")
        if not vault:
            st.info("Belum ada data proyek.")
        else:
            table_data = []
            for d in vault:
                table_data.append({
                    "ID": d.get("id", ""),
                    "Judul Video": d.get("title", ""),
                    "Niche": d.get("niche", ""),
                    "Platform": d.get("platform", ""),
                    "Status": d.get("status", ""),
                    "Durasi": f"{d.get('est_duration_sec', 60)}s",
                    "Dibuat": d.get("created_at", "")[:10]
                })

            import pandas as pd
            df_vault = pd.DataFrame(table_data)
            st.dataframe(df_vault, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 4: KALENDER RILIS MINGGUAN (CONTENT SCHEDULER & PRIME TIME)
    # =========================================================================
    with tab_scheduler:
        st.markdown("### 📅 Kalender & Jadwal Rilis Mingguan (Content Scheduler)")
        st.caption("Petakan konsistensi upload harian (Senin–Minggu) dengan jam tayang terbaik (Prime Time) dan strategi pilar mingguan standar agensi top.")

        st.markdown("""
        <div style="background: #eef2ff; border-left: 4px solid #4f46e5; padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-size: 0.9rem; color: #1e1b4b; line-height: 1.5;">
            💡 <b>Rahasia Konsistensi Algoritma:</b> Mengupload 1 video berkualitas setiap hari di jam tayang yang sama melatih algoritma TikTok & Reels untuk memprioritaskan akun Anda ke audiens aktif. Slotkan draf konten Anda ke hari-hari di bawah ini!
        </div>
        """, unsafe_allow_html=True)

        DAYS_CONFIG = [
            ("Senin", "🥊 The Myth-Buster", "Bongkar salah kaprah populer di niche Anda", "12:00 & 19:30 WIB", "#ef4444"),
            ("Selasa", "🛠️ The Practical Playbook", "Tutorial taktis 3 langkah langsung praktek", "12:30 & 20:00 WIB", "#3b82f6"),
            ("Rabu", "🤝 The Relatable Story", "Curhat / cerita emosional pengalaman nyata", "13:00 & 19:00 WIB", "#8b5cf6"),
            ("Kamis", "⚠️ The Costly Mistake", "Peringatan kesalahan fatal yang bikin rugi", "12:00 & 20:30 WIB", "#f59e0b"),
            ("Jumat", "🔮 The Insider Hack", "Bocoran alat/trik rahasia yang jarang diketahui", "11:30 & 19:30 WIB", "#10b981"),
            ("Sabtu", "💬 The Community Debate", "Pertanyaan kontroversial pemancing interaksi", "14:00 & 21:00 WIB", "#ec4899"),
            ("Minggu", "💰 The Direct CTA & Mindset", "Motivasi mingguan & jembatan konversi bio", "10:30 & 19:30 WIB", "#6366f1"),
        ]

        col_sch_left, col_sch_right = st.columns(2, gap="medium")
        half = 4
        left_days = DAYS_CONFIG[:half]
        right_days = DAYS_CONFIG[half:]

        def _render_scheduler_day(d_tuple):
            day_name, pilar_title, pilar_desc, prime_time, color_tag = d_tuple
            assigned_drafts = [d for d in vault if d.get("scheduled_day") == day_name]

            with st.container(border=True):
                col_dh1, col_dh2 = st.columns([1.8, 1.2])
                with col_dh1:
                    st.markdown(f"##### 🗓️ {day_name}")
                    st.markdown(f"<span style='background:{color_tag}15; color:{color_tag}; font-weight:700; padding:2px 8px; border-radius:4px; font-size:0.78rem;'>{pilar_title}</span>", unsafe_allow_html=True)
                with col_dh2:
                    st.markdown(f"<div style='text-align:right; font-size:0.75rem; color:#64748b;'>⏰ Prime Time:<br><b style='color:#0f172a;'>{prime_time}</b></div>", unsafe_allow_html=True)

                st.caption(f"🎯 *Fokus:* {pilar_desc}")

                if assigned_drafts:
                    for ad in assigned_drafts:
                        st.markdown(f"""
                        <div style="background:#f8fafc; border-left:3px solid {color_tag}; padding:8px 12px; border-radius:6px; margin:6px 0;">
                            <div style="font-weight:700; font-size:0.85rem; color:#1e293b;">{ad.get('title', 'Video Konten')}</div>
                            <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                                <span>📱 {ad.get('platform', 'TikTok')}</span> • 
                                <span>⏱️ ~{ad.get('est_duration_sec', 60)}s</span> • 
                                <span style="font-weight:600; color:#0284c7;">{ad.get('status', 'Siap Posting')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col_da1, col_da2 = st.columns(2)
                        with col_da1:
                            if ad.get("status") != "✅ Sudah Tayang":
                                if st.button(f"✅ Tandai Tayang", key=f"sch_live_{ad['id']}_{day_name}", use_container_width=True):
                                    change_draft_status(ad["id"], "✅ Sudah Tayang")
                                    st.toast(f"Status video diperbarui ke 'Sudah Tayang'!", icon="🎉")
                                    st.rerun()
                        with col_da2:
                            if st.button(f"❌ Lepas Slot", key=f"sch_unslot_{ad['id']}_{day_name}", use_container_width=True):
                                update_draft(ad["id"], {"scheduled_day": ""})
                                st.rerun()
                else:
                    st.markdown("<div style='color:#94a3b8; font-size:0.78rem; padding:8px; background:#f8fafc; border-radius:6px; text-align:center;'>Belum ada video dijadwalkan untuk hari ini.</div>", unsafe_allow_html=True)

                available_drafts = [d for d in vault if not d.get("scheduled_day") or d.get("scheduled_day") == ""]
                if available_drafts:
                    draft_map = {f"[{d.get('status', 'Draf')[:8]}] {d.get('title', 'Konten')[:35]}": d["id"] for d in available_drafts}
                    chosen_assign = st.selectbox(
                        f"Pilih draf untuk {day_name}:",
                        options=["-- Pasang Draf dari Brankas --"] + list(draft_map.keys()),
                        key=f"sel_assign_{day_name}"
                    )
                    if chosen_assign != "-- Pasang Draf dari Brankas --":
                        chosen_id = draft_map[chosen_assign]
                        if st.button(f"📌 Pasang ke {day_name}", key=f"btn_assign_{day_name}", type="primary", use_container_width=True):
                            update_draft(chosen_id, {"scheduled_day": day_name})
                            st.toast(f"Draf berhasil dijadwalkan untuk {day_name}!", icon="📌")
                            st.rerun()

        with col_sch_left:
            for d_tuple in left_days:
                _render_scheduler_day(d_tuple)

        with col_sch_right:
            for d_tuple in right_days:
                _render_scheduler_day(d_tuple)


def _render_kanban_card(item: dict, prefix: str):
    """Merender kartu konten individu di dalam kolom Kanban dengan tombol geser 1-klik dan salin cepat."""
    draft_id = item.get("id", "")
    current_status = item.get("status", "💡 Ide & Riset")

    status_badge_map = {
        "💡 Ide & Riset": ("#f1f5f9", "#475569", "💡 Ide & Riset"),
        "📝 Skrip Selesai": ("#eef2ff", "#4f46e5", "📝 Skrip Selesai"),
        "🎙️ Siap Syuting": ("#eef2ff", "#4f46e5", "🎙️ Siap Syuting"),
        "🎬 Editing CapCut": ("#f0f9ff", "#0284c7", "🎬 Editing CapCut"),
        "🚀 Siap Posting": ("#fff7ed", "#ea580c", "🚀 Siap Upload"),
        "✅ Sudah Tayang": ("#ecfdf5", "#16a34a", "✅ Sudah Tayang (Live)")
    }
    bg_c, text_c, label_c = status_badge_map.get(current_status, ("#f1f5f9", "#475569", current_status))

    with st.container(border=True):
        st.markdown(f"**{item.get('title', 'Draf Konten')}**")
        aud_meta = f"<div style='font-size:0.74rem; color:#475569; margin:2px 0 6px 0; background:#f8fafc; padding:3px 6px; border-radius:4px;'>👥 <b>Target:</b> {item.get('target_audience')[:38]}</div>" if item.get('target_audience') else ""
        
        fmt_val = item.get("content_format", "")
        fmt_badge = ""
        if fmt_val:
            short_fmt = fmt_val.split("(")[0].strip()
            fmt_badge = f"<div style='margin-bottom:4px;'><span style='font-size:0.72rem; font-weight:700; background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; padding:1px 6px; border-radius:4px;'>{short_fmt}</span></div>"

        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:0.75rem; font-weight:700; background:{bg_c}; color:{text_c}; padding:2px 8px; border-radius:4px;">{label_c}</span>
            <span style="font-size:0.75rem; color:#64748b;">🏷️ {item.get('niche', 'Umum')}</span>
        </div>
        {fmt_badge}
        {aud_meta}
        """, unsafe_allow_html=True)

        if item.get("hook_verbal"):
            st.markdown(f"<div style='font-size:0.82rem; color:#475569; background:#f8fafc; border-left:3px solid #6366f1; padding:6px 10px; border-radius:4px; margin:6px 0;'>\"{item.get('hook_verbal')[:75]}...\"</div>", unsafe_allow_html=True)

        # Tombol aksi utama langsung terlihat di kartu (1-Click Open Pipeline)
        if st.button("⚡ Buka di Pipeline Wizard", key=f"open_pipe_{prefix}_{draft_id}", type="primary", use_container_width=True):
            st.session_state["current_pipeline_draft_id"] = draft_id
            st.session_state["pipe_keyword"] = item.get("keyword", "")
            st.session_state["pipe_keyword_input"] = item.get("keyword", "")
            raw_niche = item.get("niche", "")
            matched_niche = None
            if raw_niche:
                for cn in COMPREHENSIVE_NICHES:
                    if raw_niche.lower() in cn.lower() or cn.lower() in raw_niche.lower():
                        matched_niche = cn
                        break
            st.session_state["pipe_niche"] = matched_niche if matched_niche else "✍️ Custom Niche (Ketik Niche Sendiri)"
            if not matched_niche and raw_niche:
                st.session_state["pipe_custom_niche"] = raw_niche

            plat_opts = ["TikTok", "Instagram Reels", "YouTube Shorts", "TikTok / Reels"]
            raw_plat = item.get("platform", "TikTok")
            st.session_state["pipe_platform"] = raw_plat if raw_plat in plat_opts else "TikTok"

            st.session_state["pipe_audience"] = item.get("target_audience", "Penonton umum")
            if item.get("content_format"):
                st.session_state["pipe_content_format_select"] = item.get("content_format")
                st.session_state["pipe_format_val"] = item.get("content_format")
            if item.get("content_theme"):
                st.session_state["pipe_theme_select"] = item.get("content_theme")
            if item.get("audience_slang"):
                st.session_state["pipe_slang_select"] = item.get("audience_slang")
            if item.get("emotional_trigger"):
                st.session_state["pipe_emotion_select"] = item.get("emotional_trigger")
            st.session_state["pipe_topic_for_hook"] = item.get("content_angle") or item.get("title", "")
            st.session_state["pipe_hook_topic_input"] = item.get("content_angle") or item.get("title", "")
            st.session_state["pipe_chosen_hook"] = item.get("hook_verbal", "")
            st.session_state["pipe_story_topic"] = item.get("content_angle") or item.get("title", "")
            st.session_state["pipe_product_input"] = item.get("product_name", "")
            if item.get("communication_style"):
                st.session_state["pipe_comm_style"] = item.get("communication_style")
                st.session_state["pipe_comm_style_select"] = item.get("communication_style")
                st.session_state["pipe_angle_type"] = item.get("communication_style")
            if item.get("cta_goal"):
                st.session_state["pipe_cta_target"] = item.get("cta_goal")

            if item.get("storyboard_table_md"):
                st.session_state["pipe_step3_result"] = item.get("storyboard_table_md", "")
            if item.get("publication_kit_md"):
                st.session_state["pipe_step5_result"] = item.get("publication_kit_md", "")

            # Arahkan ke Tahap 3 (Storyboard & Naskah) jika draf sudah memiliki skrip,
            # atau Tahap 1 jika draf baru/ide, agar pengguna tidak langsung terlempar ke penutup (Tahap 5).
            if item.get("storyboard_table_md"):
                st.session_state["pipeline_step"] = 3
            elif item.get("hook_verbal"):
                st.session_state["pipeline_step"] = 2
            else:
                st.session_state["pipeline_step"] = 1

            st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
            st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
            st.rerun()

        # --- FITUR 4: TOMBOL ALUR KANBAN (MAJU & MUNDUR SATU TAHAP) ---
        if current_status == "💡 Ide & Riset":
            if st.button("🎙️ Lanjut ke Siap Syuting ➔", key=f"mv_shoot_{prefix}_{draft_id}", use_container_width=True):
                change_draft_status(draft_id, "🎙️ Siap Syuting")
                st.toast("Dipindahkan ke kolom Siap Syuting!", icon="🎙️")
                st.rerun()

        elif current_status in ["📝 Skrip Selesai", "🎙️ Siap Syuting"]:
            col_mv_a, col_mv_b = st.columns([1.6, 1])
            with col_mv_a:
                if st.button("🎬 Lanjut Editing ➔", key=f"mv_edit_{prefix}_{draft_id}", use_container_width=True):
                    change_draft_status(draft_id, "🎬 Editing CapCut")
                    st.toast("Dipindahkan ke kolom Editing CapCut!", icon="🎬")
                    st.rerun()
            with col_mv_b:
                if st.button("⬅️ Ide", key=f"mv_b_idea_{prefix}_{draft_id}", use_container_width=True, help="Kembalikan ke Ide & Riset"):
                    change_draft_status(draft_id, "💡 Ide & Riset")
                    st.toast("Dikembalikan ke Ide & Riset", icon="💡")
                    st.rerun()

        elif current_status == "🎬 Editing CapCut":
            col_mv_a, col_mv_b = st.columns([1.6, 1])
            with col_mv_a:
                if st.button("🚀 Siap Upload ➔", key=f"mv_ready_{prefix}_{draft_id}", use_container_width=True):
                    change_draft_status(draft_id, "🚀 Siap Posting")
                    st.toast("Dipindahkan ke kolom Siap Upload!", icon="🚀")
                    st.rerun()
            with col_mv_b:
                if st.button("⬅️ Syuting", key=f"mv_b_shoot_{prefix}_{draft_id}", use_container_width=True, help="Kembalikan ke Siap Syuting"):
                    change_draft_status(draft_id, "🎙️ Siap Syuting")
                    st.toast("Dikembalikan ke Siap Syuting", icon="🎙️")
                    st.rerun()

        elif current_status == "🚀 Siap Posting":
            col_mv_a, col_mv_b = st.columns([1.7, 1])
            with col_mv_a:
                if st.button("✅ Sudah Tayang ➔", key=f"mv_done_{prefix}_{draft_id}", type="primary", use_container_width=True):
                    change_draft_status(draft_id, "✅ Sudah Tayang")
                    st.toast("🎉 Selamat! Konten berpindah ke kolom Sudah Tayang!", icon="✅")
                    st.rerun()
            with col_mv_b:
                if st.button("⬅️ Edit", key=f"mv_b_edit_{prefix}_{draft_id}", use_container_width=True, help="Kembalikan ke Editing CapCut"):
                    change_draft_status(draft_id, "🎬 Editing CapCut")
                    st.toast("Dikembalikan ke Editing CapCut", icon="🎬")
                    st.rerun()

        elif current_status == "✅ Sudah Tayang":
            st.markdown("""
            <div style="background:#ecfdf5; border:1.5px solid #10b981; border-radius:8px; padding:6px 10px; text-align:center; margin:4px 0 8px 0;">
                <span style="color:#065f46; font-weight:700; font-size:0.82rem;">🎉 SUDAH LIVE DI MEDSOS</span>
                <div style="color:#047857; font-size:0.72rem;">Selesai diposting ke audiens</div>
            </div>
            """, unsafe_allow_html=True)
            col_don_a, col_don_b = st.columns([1.6, 1])
            with col_don_a:
                if st.button("🔄 Buat Sekuel", key=f"mv_recycle_{prefix}_{draft_id}", use_container_width=True, help="Buka Pipeline untuk membuat video part 2 / sekuel"):
                    st.session_state["pipe_keyword"] = f"Lanjutan: {item.get('keyword', '')}"
                    st.session_state["pipe_keyword_input"] = f"Lanjutan: {item.get('keyword', '')}"
                    st.session_state["pipe_topic_for_hook"] = f"Part 2 dari: {item.get('title', '')}"
                    st.session_state["pipeline_step"] = 1
                    st.session_state["current_pipeline_draft_id"] = None
                    st.session_state["_target_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.session_state["active_nav"] = "⚡ Generator Konten (Pipeline & Sprint)"
                    st.rerun()
            with col_don_b:
                if st.button("↩️ Batal", key=f"mv_undo_{prefix}_{draft_id}", use_container_width=True, help="Kembalikan ke Siap Upload jika belum benar-benar tayang"):
                    change_draft_status(draft_id, "🚀 Siap Posting")
                    st.toast("Konten dikembalikan ke Siap Upload", icon="🚀")
                    st.rerun()

        # --- FITUR 1: TOMBOL 1-KLIK SALIN CEPAT PADA KARTU ---
        with st.expander("📋 Salin Cepat (Caption & Tag)", expanded=False):
            kit = extract_copywriting_kit(item)
            speech = extract_clean_speech_dialogue(item)

            st.caption("📝 **Caption Pilihan A (Storytelling & Emosional)**:")
            st.code(kit["caption_storytelling"], language=None)

            st.caption("⚡ **Caption Pilihan B (To-the-Point & Agitatif)**:")
            st.code(kit["caption_punchy"], language=None)

            st.caption("🏷️ **10 Hashtag FYP Terkurasi**:")
            st.code(kit["hashtags_str"], language=None)

            st.caption("🗣️ **Naskah Suara Bersih (Siap Baca/HP)**:")
            st.code(speech, language=None)

            from utils.export_helpers import parse_storyboard_scenes, format_scenes_for_production_sheet
            card_scenes = parse_storyboard_scenes(item.get("storyboard_table_md", ""))
            if card_scenes:
                st.caption("🎬 **Lembar Kerja Per Scene (Siap Kirim ke Editor)**:")
                st.code(format_scenes_for_production_sheet(card_scenes, title=item.get("title", "Video"), platform=item.get("platform", "TikTok")), language="text")

            st.caption(f"⏰ **Jam Upload:** {kit['prime_time_recommendation']}")

        # Menu Opsi & Status Lengkap
        with st.expander("⚙️ Opsi & Status", expanded=False):
            new_status = st.selectbox(
                "Ubah Status Manual:",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0,
                key=f"status_sel_{prefix}_{draft_id}"
            )
            if new_status != current_status:
                change_draft_status(draft_id, new_status)
                st.rerun()

            col_card_act1, col_card_act2 = st.columns([1, 1])
            with col_card_act1:
                zip_bytes = generate_draft_bundle_zip(item)
                st.download_button(
                    label="📥 Unduh .ZIP",
                    data=zip_bytes,
                    file_name=f"ViralGenix_{draft_id}.zip",
                    mime="application/zip",
                    key=f"zip_{prefix}_{draft_id}",
                    use_container_width=True
                )
            with col_card_act2:
                if st.button("🗑️ Hapus", key=f"del_{prefix}_{draft_id}", use_container_width=True):
                    delete_draft(draft_id)
                    st.rerun()
