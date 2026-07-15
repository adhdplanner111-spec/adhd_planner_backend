import json
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from google import genai
from google.genai import types

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)

_client = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"]
)

_TASK_EXTRACTION_PROMPT = """
Kamu adalah AI Task Extractor untuk aplikasi Smart ADHD Planner.

Kamu menerima transkrip percakapan atau perintah suara dalam bahasa Indonesia atau Inggris.

Tugasmu adalah mengekstrak task dari transkrip tersebut.

=====================================================
OUTPUT
=====================================================

SELALU jawab HANYA dengan JSON VALID. Tanpa markdown, tanpa penjelasan.

{
    "transcript": "<teks transkrip asli>",
    "tasks": [
        {
            "title": "",
            "description": "",
            "priority": "",
            "due_date": "",
            "start_time": "",
            "duration_minutes": null
        }
    ],
    "summary": "",
    "detected_language": "",
    "total_tasks": 0
}

=====================================================
ATURAN
=====================================================

title: Maksimal 8 kata. Singkat dan jelas.

priority: Salah satu dari: Low, Medium, High
- High: ada kata urgent, penting, segera, deadline, hari ini, ASAP, ujian, presentasi, sidang
- Medium: tugas kuliah, belajar, coding, review, meeting biasa
- Low: belanja, santai, opsional

due_date: Format YYYY-MM-DD. null jika tidak diketahui.
  - "hari ini" → null (frontend yang tahu tanggal hari ini)
  - "besok" → null
  - Tanggal eksplisit seperti "25 Januari 2025" → 2025-01-25

start_time: Format HH:MM (24 jam). null jika tidak ada.

duration_minutes: Integer. null jika tidak ada.
  - "2 jam" → 120
  - "30 menit" → 30

Jika tidak ditemukan task:
{
    "transcript": "...",
    "tasks": [],
    "summary": "Tidak ditemukan task dari perintah suara.",
    "detected_language": "Indonesian",
    "total_tasks": 0
}
"""


@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    """
    Terima file audio dari Flutter (m4a/wav/ogg/webm),
    transkripsi + ekstrak task menggunakan Gemini,
    kembalikan JSON tasks.
    """
    content_type = file.content_type or ""

    # Mapping mime type audio yang didukung Gemini
    SUPPORTED_AUDIO = {
        "audio/m4a": "audio/mp4",
        "audio/x-m4a": "audio/mp4",
        "audio/mp4": "audio/mp4",
        "audio/wav": "audio/wav",
        "audio/x-wav": "audio/wav",
        "audio/wave": "audio/wav",
        "audio/ogg": "audio/ogg",
        "audio/webm": "audio/webm",
        "audio/mpeg": "audio/mpeg",
        "audio/mp3": "audio/mpeg",
        "application/octet-stream": "audio/mp4",  # fallback untuk m4a
    }

    mime_type = SUPPORTED_AUDIO.get(content_type)

    # Jika mime type tidak dikenali, coba deteksi dari extension filename
    if mime_type is None:
        filename = file.filename or ""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        ext_map = {
            "m4a": "audio/mp4",
            "mp4": "audio/mp4",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "webm": "audio/webm",
            "mp3": "audio/mpeg",
        }
        mime_type = ext_map.get(ext)

    if mime_type is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Format audio tidak didukung. "
                "Gunakan: m4a, wav, ogg, webm, mp3"
            ),
        )

    # Baca bytes
    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="File audio kosong.",
        )
    if len(audio_bytes) > 25 * 1024 * 1024:  # 25 MB limit
        raise HTTPException(
            status_code=400,
            detail="Ukuran audio maksimal 25 MB.",
        )

    try:
        # Step 1: Transkripsi audio menggunakan Gemini
        transcription_response = _client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type,
                ),
                (
                    "Transkripsi audio ini secara verbatim. "
                    "Jawab HANYA dengan teks transkrip, tanpa tambahan apapun. "
                    "Jika audio tidak terdengar jelas, tulis apa yang kamu dengar."
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
            ),
        )

        transcript = transcription_response.text.strip()

        if not transcript:
            return {
                "success": True,
                "data": {
                    "transcript": "",
                    "tasks": [],
                    "summary": "Audio tidak dapat ditranskripsi. Pastikan mikrofon aktif dan rekaman jelas.",
                    "detected_language": "Indonesian",
                    "total_tasks": 0,
                },
            }

        # Step 2: Ekstrak task dari transkrip
        extraction_response = _client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                f"Transkrip perintah suara:\n\n{transcript}"
            ],
            config=types.GenerateContentConfig(
                system_instruction=_TASK_EXTRACTION_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )

        raw_json = extraction_response.text.strip()

        # Strip markdown fences jika ada (defensive)
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
            raw_json = raw_json.strip()

        result = json.loads(raw_json)

        # Pastikan transcript field terisi dari step 1
        result["transcript"] = transcript

        return {
            "success": True,
            "data": result,
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=422,
            detail="Gagal mem-parse respons AI. Coba rekam ulang dengan lebih jelas.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Layanan AI tidak tersedia: {str(e)}",
        )