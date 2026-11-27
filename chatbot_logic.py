"""Fungsi murni chatbot: aman diuji tanpa API key atau panggilan internet."""

INSTRUKSI = (
    "Kamu asisten AI ramah berbahasa Indonesia. "
    "Jawab secara akurat, jelas, dan mudah dipahami pemula."
)


def ambil_teks(content):
    """Ambil teks dari string atau konten terstruktur Gradio 6."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        teks = []
        for blok in content:
            if isinstance(blok, dict) and blok.get("type") == "text":
                nilai = blok.get("text", "")
                if isinstance(nilai, str):
                    teks.append(nilai)
        return "\n".join(teks)

    return ""


def susun_pesan(pesan, riwayat):
    """Susun instruksi, maksimal 6 pesan riwayat, dan pertanyaan terbaru."""
    if not isinstance(pesan, str) or not pesan.strip():
        raise ValueError("Pesan tidak boleh kosong.")

    konteks = []
    for item in (riwayat or [])[-6:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = ambil_teks(item.get("content"))
        if role in ("user", "assistant") and content.strip():
            konteks.append({"role": role, "content": content})

    return [
        {"role": "system", "content": INSTRUKSI},
        *konteks,
        {"role": "user", "content": pesan.strip()},
    ]
