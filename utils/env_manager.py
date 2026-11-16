"""
ViralGenix - Environment & API Key Persistence Manager
Mendukung Streamlit Cloud Secrets (st.secrets), Streamlit Session State (UI input langsung),
Environment Variables (os.environ), serta file lokal .env secara transparan dan aman.
"""

import os
import re

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

def get_env_var(key: str, default: str = "") -> str:
    """
    Membaca variabel API key dengan prioritas cerdas:
    1. st.session_state (input langsung pengguna di UI pada sesi saat ini)
    2. os.environ (Environment variables sistem / container)
    3. st.secrets (Streamlit Community Cloud Secrets Dashboard)
    4. file .env lokal (untuk mode development di PC)
    5. default
    """
    # 1. Cek st.session_state jika sedang berjalan di dalam konteks Streamlit
    try:
        import streamlit as st
        # Cek beberapa variasi key yang mungkin tersimpan di session_state
        for s_key in [f"api_key_{key}", f"input_key_{key}", f"api_key_input_{key.lower().replace('_api_key', '')}", key, key.lower()]:
            if s_key in st.session_state and st.session_state[s_key]:
                val_ss = str(st.session_state[s_key]).strip()
                if len(val_ss) > 3:
                    os.environ[key] = val_ss
                    return val_ss
    except Exception:
        pass

    # 2. Cek os.environ
    val = os.getenv(key)
    if val and val.strip():
        return val.strip()

    # 3. Cek Streamlit Secrets (PENTING untuk live di viral-genix.streamlit.app)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets is not None:
            # Cek key persis (misal GROQ_API_KEY)
            if key in st.secrets and str(st.secrets[key]).strip():
                secret_val = str(st.secrets[key]).strip()
                os.environ[key] = secret_val
                return secret_val
            # Cek key lowercase (misal groq_api_key)
            key_l = key.lower()
            if key_l in st.secrets and str(st.secrets[key_l]).strip():
                secret_val = str(st.secrets[key_l]).strip()
                os.environ[key] = secret_val
                return secret_val
            # Cek jika dimasukkan dalam sub-section [api_keys] atau [groq]
            for sec_name in ["api_keys", "general", "env", key.lower().replace("_api_key", "")]:
                if sec_name in st.secrets and hasattr(st.secrets[sec_name], "get"):
                    sub_val = st.secrets[sec_name].get(key) or st.secrets[sec_name].get(key_l) or st.secrets[sec_name].get("api_key")
                    if sub_val and str(sub_val).strip():
                        res_sec = str(sub_val).strip()
                        os.environ[key] = res_sec
                        return res_sec
    except Exception:
        pass

    # 4. Cek file .env lokal (untuk development offline / PC)
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(rf'^{key}\s*=\s*(.*)$', content, re.MULTILINE)
            if match:
                clean_val = match.group(1).strip().strip('"').strip("'")
                if clean_val:
                    os.environ[key] = clean_val
                    return clean_val
        except Exception:
            pass

    return default

def save_env_var(key: str, value: str) -> bool:
    """
    Menyimpan atau memperbarui kunci API ke session_state dan os.environ,
    serta mencoba menulis ke file .env lokal jika izin file tersedia.
    """
    clean_val = value.strip()
    os.environ[key] = clean_val

    # Simpan ke Streamlit Session State agar langsung aktif seketika di sesi cloud
    try:
        import streamlit as st
        st.session_state[f"api_key_{key}"] = clean_val
        st.session_state[key] = clean_val
        prov_short = key.lower().replace("_api_key", "")
        st.session_state[f"api_key_input_{prov_short}"] = clean_val
    except Exception:
        pass

    # Tulis ke file .env lokal jika memungkinkan
    try:
        content = ""
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                content = f.read()

        pattern = rf'^{key}\s*=\s*.*$'
        new_line = f"{key}={clean_val}"

        if re.search(pattern, content, re.MULTILINE):
            new_content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
        else:
            if content and not content.endswith("\n"):
                content += "\n"
            new_content = content + new_line + "\n"

        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception:
        return False


