"""
ViralGenix - Environment & API Key Persistence Manager
Menyimpan dan memuat API key secara permanen ke file .env
sehingga pengguna tidak perlu mengetik ulang setiap kali me-refresh atau membuka aplikasi.
"""

import os
import re

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

def get_env_var(key: str, default: str = "") -> str:
    """
    Membaca variabel dari os.environ atau membaca langsung dari file .env.
    """
    val = os.getenv(key)
    if val and val.strip():
        return val.strip()

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
    Menyimpan atau memperbarui kunci API ke file .env secara permanen,
    dan langsung memperbarui os.environ pada runtime aplikasi saat ini.
    """
    clean_val = value.strip()
    os.environ[key] = clean_val

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

