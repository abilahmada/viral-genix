"""
ViralGenix - Transcript Extractor
Modul ekstraksi transkrip video YouTube / Shorts dengan URL parser fleksibel,
multi-bahasa, serta fallback otomatis ke metadata judul & deskripsi jika video tidak memiliki closed-caption.
"""

import re
import requests
from typing import Dict, Any, Optional

def extract_video_id(url: str) -> Optional[str]:
    """
    Mengekstraksi 11 karakter video ID dari berbagai varian URL YouTube:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?feature=shared&v=VIDEO_ID
    - https://youtu.be/VIDEO_ID?si=...
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - VIDEO_ID langsung (11 karakter)
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Jika pengguna langsung memasukkan ID 11 karakter
    if len(url) == 11 and re.match(r'^[A-Za-z0-9_-]{11}$', url):
        return url

    # Universal YouTube ID matcher
    patterns = [
        r'(?:v=|\/v\/|\/embed\/|\/shorts\/|youtu\.be\/)([A-Za-z0-9_-]{11})',
        r'[\?&]v=([A-Za-z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def fetch_youtube_metadata(video_id: str) -> Dict[str, str]:
    """
    Mengambil judul dan informasi video melalui API publik oEmbed YouTube
    (100% tanpa API key dan tidak pernah diblokir).
    """
    info = {"title": "", "author": "", "description": ""}
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        res = requests.get(oembed_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            info["title"] = data.get("title", "")
            info["author"] = data.get("author_name", "")
    except Exception:
        pass

    try:
        # Coba ambil deskripsi ringkas dari meta tag
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        page_res = requests.get(f"https://www.youtube.com/watch?v={video_id}", headers=headers, timeout=5)
        if page_res.status_code == 200:
            desc_match = re.search(r'<meta name="description" content="(.*?)">', page_res.text)
            if desc_match:
                info["description"] = desc_match.group(1).strip()
    except Exception:
        pass

    return info


def fetch_youtube_transcript(url_or_id: str) -> Dict[str, Any]:
    """
    Mengambil transkrip otomatis YouTube menggunakan library youtube-transcript-api.
    Jika video tidak memiliki subtitle (closed caption), otomatis mengambil metadata
    judul dan deskripsi agar AI tetap dapat membedah kontennya!
    """
    video_id = extract_video_id(url_or_id)
    if not video_id:
        return {
            "success": False,
            "error": "URL YouTube tidak valid atau ID video tidak dikenali. Pastikan memasukkan URL lengkap (contoh: https://youtube.com/shorts/xyz atau https://youtu.be/xyz).",
            "video_id": None,
            "transcript_text": "",
            "plain_text": "",
            "fallback_to_metadata": False,
            "raw_entries": []
        }

    # Coba ekstraksi subtitle dengan youtube-transcript-api
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        # 1. Coba ambil transcript langsung dengan prioritas bahasa Indonesia & Inggris
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=['id', 'id-ID', 'en', 'en-US', 'en-GB'])
        except Exception:
            # 2. Jika tidak ada bahasa spesifik, cari di list_transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript = transcript_list.find_generated_transcript(['id', 'en'])
            except Exception:
                all_transcripts = list(transcript_list)
                if all_transcripts:
                    transcript = all_transcripts[0]
                else:
                    raise Exception("NoTranscriptFound")
            data = transcript.fetch()

        if data:
            formatted_lines = []
            plain_sentences = []

            for item in data:
                start_sec = int(item['start'])
                minutes = start_sec // 60
                seconds = start_sec % 60
                timestamp_str = f"[{minutes:02d}:{seconds:02d}]"
                clean_text = re.sub(r'\[.*?\]', '', item['text']).strip()
                if clean_text:
                    formatted_lines.append(f"{timestamp_str} {clean_text}")
                    plain_sentences.append(clean_text)

            full_text = " ".join(plain_sentences)
            timestamped_text = "\n".join(formatted_lines)

            return {
                "success": True,
                "video_id": video_id,
                "transcript_text": timestamped_text,
                "plain_text": full_text,
                "fallback_to_metadata": False,
                "raw_entries": data,
                "total_snippets": len(data),
                "estimated_duration_sec": int(data[-1]['start'] + data[-1]['duration']) if data else 0
            }

    except Exception:
        # Jika subtitle tertutup tidak tersedia (sangat umum pada YouTube Shorts/TikTok),
        # aktifkan Fallback Cerdas ke Metadata Video!
        pass

    # --- FALLBACK CERDAS KE METADATA VIDEO ---
    meta = fetch_youtube_metadata(video_id)
    if meta.get("title"):
        title = meta.get("title", "")
        author = meta.get("author", "")
        desc = meta.get("description", "")

        synthetic_plain = f"Judul Video: {title}\nKreator: {author}\nDeskripsi / Konteks: {desc}"
        synthetic_formatted = f"[00:00] [Judul Video]: {title}\n[00:03] [Kreator / Channel]: {author}\n[00:05] [Deskripsi]: {desc}"

        return {
            "success": True,
            "video_id": video_id,
            "transcript_text": synthetic_formatted,
            "plain_text": synthetic_plain,
            "fallback_to_metadata": True,
            "meta": meta,
            "raw_entries": [],
            "total_snippets": 1,
            "estimated_duration_sec": 60
        }

    return {
        "success": False,
        "error": "Video ini tidak memiliki teks subtitle bawaan dan metadata tidak dapat diakses. Silakan salin atau ketikkan ringkasan dialog video secara manual di tab 'Input Manual'.",
        "video_id": video_id,
        "transcript_text": "",
        "plain_text": "",
        "fallback_to_metadata": False,
        "raw_entries": []
    }
