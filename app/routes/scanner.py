import base64
import json
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import anthropic

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/scanner",
    tags=["Scanner"],
)

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

_SYSTEM_PROMPT = """Kamu adalah asisten ekstraksi tugas dari gambar untuk aplikasi ADHD Planner.

Tugasmu adalah membaca teks dari gambar (foto catatan, whiteboard, jadwal, daftar tugas, dll)
dan mengekstrak informasi task secara terstruktur.

SELALU jawab HANYA dengan JSON yang valid tanpa preamble, penjelasan, atau markdown fence.

Format JSON yang harus dikembalikan:
{
  "raw_text": "<semua teks yang terbaca dari gambar>",
  "tasks": [
    {
      "title": "<judul task yang jelas dan ringkas>",
      "description": "<deskripsi detail jika ada, null jika tidak ada>",
      "priority": "<Low | Medium | High — perkirakan dari konteks>",
      "due_date": "<YYYY-MM-DD jika ada tanggal, null jika tidak>",
      "start_time": "<HH:MM 24-jam jika ada jam, null jika tidak>",
      "duration_minutes": <angka menit jika ada durasi, null jika tidak>
    }
  ],
  "summary": "<ringkasan singkat apa yang ditemukan di gambar>"
}

Panduan:
- Jika ada beberapa tugas dalam satu gambar, buat array tasks dengan semua task.
- Jika hanya ada satu task, tetap buat array dengan 1 item.
- Jika tidak ada task yang bisa diidentifikasi, kembalikan array tasks kosong [].
- Priority: High jika ada kata "urgent/penting/segera/deadline dekat", Low jika santai, Medium untuk sisanya.
- Tanggal relatif seperti "besok" → null (tidak bisa ditentukan tanpa konteks hari ini).
- Format due_date HARUS YYYY-MM-DD atau null.
- Format start_time HARUS HH:MM atau null.
"""


@router.post("/scan")
async def scan_image(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """
    Terima gambar dari Flutter, kirim ke Claude Vision,
    kembalikan hasil ekstraksi task terstruktur.
    """
    # Validasi tipe file
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File harus berupa gambar (image/jpeg, image/png, dll)",
        )

    # Baca bytes dan encode base64
    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(
            status_code=400,
            detail="Ukuran gambar maksimal 10 MB",
        )

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Normalize media type
    media_type = content_type if content_type in (
        "image/jpeg", "image/png", "image/gif", "image/webp"
    ) else "image/jpeg"

    try:
        message = _client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Ekstrak semua task dari gambar ini.",
                        },
                    ],
                }
            ],
        )

        raw_response = message.content[0].text.strip()

        # Strip markdown fences jika ada
        if raw_response.startswith("```"):
            raw_response = raw_response.split("```")[1]
            if raw_response.startswith("json"):
                raw_response = raw_response[4:]
            raw_response = raw_response.strip()

        result = json.loads(raw_response)

        return {
            "success": True,
            "data": result,
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=422,
            detail="Gagal mem-parse respons AI. Coba foto ulang dengan pencahayaan lebih baik.",
        )
    except anthropic.APIError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Layanan AI tidak tersedia: {str(e)}",
        )
