"""Chatbot Groq + Gradio untuk demonstrasi portofolio (satu sesi per browser)."""

import os

import gradio as gr
from dotenv import load_dotenv
from groq import Groq, GroqError

load_dotenv()

MODEL = "openai/gpt-oss-20b"
API_KEY = os.getenv("GROQ_API_KEY")
GRADIO_PASSWORD = os.getenv("GRADIO_PASSWORD")
SHARE = os.getenv("GRADIO_SHARE", "false").lower() == "true"

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY belum diatur. Periksa Secrets atau .env lokal.")

if SHARE and not GRADIO_PASSWORD:
    raise RuntimeError("Set GRADIO_PASSWORD sebelum membuat link publik.")

client = Groq(api_key=API_KEY)


def ambil_teks(content):
    """Normalisasi teks riwayat, termasuk format Gradio 6."""
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


def jawab_ai(pesan, riwayat):
    """Menjawab pesan dan menggunakan 3 pasangan percakapan terakhir."""
    if not isinstance(pesan, str) or not pesan.strip():
        return "Silakan ketik pertanyaan terlebih dahulu."

    konteks = []
    for item in (riwayat or [])[-6:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = ambil_teks(item.get("content"))
        if role in ("user", "assistant") and content.strip():
            konteks.append({"role": role, "content": content})

    messages = [
        {
            "role": "system",
            "content": (
                "Kamu asisten AI ramah berbahasa Indonesia. "
                "Jawab secara akurat, jelas, dan mudah dipahami pemula."
            ),
        },
        *konteks,
        {"role": "user", "content": pesan.strip()},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_completion_tokens=500,
        )
        return response.choices[0].message.content or "Model belum menghasilkan jawaban."
    except GroqError as error:
        # Jangan tampilkan header atau isi rahasia dari exception pada UI publik.
        return f"Layanan AI belum bisa diakses ({type(error).__name__}). Coba lagi nanti."


demo = gr.ChatInterface(
    fn=jawab_ai,
    title="🤖 Chatbot AI — Portofolio",
    description="Chatbot Python dengan Gradio dan Groq. Konteks berlaku selama sesi ini.",
    examples=["Apa itu Python?", "Jelaskan machine learning untuk pemula"],
)

if __name__ == "__main__":
    demo.launch(
        share=SHARE,
        auth=("belajar-ai", GRADIO_PASSWORD) if GRADIO_PASSWORD else None,
    )
