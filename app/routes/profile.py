import os
import uuid
import requests

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from typing import Optional

from app.core.firebase import db
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 5

# ─── Konfigurasi penyimpanan foto lokal (pengganti Firebase Storage) ──────────
# BASE_DIR = root project (folder yang berisi app/, lib/, dst)
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)
MEDIA_DIR = os.path.join(BASE_DIR, "media")
PROFILE_PHOTOS_DIR = os.path.join(MEDIA_DIR, "profile_photos")
os.makedirs(PROFILE_PHOTOS_DIR, exist_ok=True)

EXT_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

# Kalau backend di-deploy di domain/server sendiri, set env BASE_URL
# contoh: BASE_URL=https://api.punyamu.com
# Kalau tidak di-set, otomatis pakai base_url dari request (host+port saat itu)
def _get_base_url(request: Request) -> str:
    env_base = os.getenv("BASE_URL")
    if env_base:
        return env_base.rstrip("/")
    return str(request.base_url).rstrip("/")


# ─── Schemas ──────────────────────────────────────────────────────────────────

class UpdateProfileRequest(BaseModel):
    fullname: Optional[str] = None
    photo_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ─── GET /profile ─────────────────────────────────────────────────────────────

@router.get("")
def get_profile(
    user=Depends(get_current_user)
):
    try:
        doc = (
            db.collection("users")
            .document(user["uid"])
            .get()
        )

        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Profil user tidak ditemukan"
            )

        data = doc.to_dict()

        return {
            "success": True,
            "data": {
                "uid": user["uid"],
                "fullname": data.get("fullname", ""),
                "email": data.get("email", ""),
                "photo_url": data.get("photo_url", ""),
                "streak": data.get("streak", 0),
                "productivity_score": data.get("productivity_score", 0),
                "focus_time": data.get("focus_time", 0),
                "tasks_done": data.get("tasks_done", 0),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /profile/upload-photo ───────────────────────────────────────────────

@router.post("/upload-photo")
async def upload_photo(
    request: Request,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        # Validasi tipe file
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Format foto tidak didukung. Gunakan JPG, PNG, atau WebP."
            )

        # Baca isi file
        contents = await file.read()

        # Validasi ukuran file (max 5 MB)
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"Ukuran foto maksimal {MAX_FILE_SIZE_MB} MB"
            )

        # Tentukan ekstensi dari content type
        ext = EXT_MAP.get(file.content_type, "jpg")

        # Hapus foto lama milik user ini kalau ekstensinya beda
        # (misal dulu upload .png, sekarang upload .jpg)
        for old_ext in EXT_MAP.values():
            if old_ext == ext:
                continue
            old_path = os.path.join(
                PROFILE_PHOTOS_DIR, f"{user['uid']}.{old_ext}"
            )
            if os.path.exists(old_path):
                os.remove(old_path)

        # Nama file = UID user, sehingga foto lama otomatis tertimpa
        filename = f"{user['uid']}.{ext}"
        file_path = os.path.join(PROFILE_PHOTOS_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        # Tambahkan query param acak supaya cache browser/app ter-refresh
        # setiap kali foto baru diupload (nama file tetap sama)
        cache_bust = uuid.uuid4().hex[:8]
        base_url = _get_base_url(request)
        photo_url = f"{base_url}/media/profile_photos/{filename}?v={cache_bust}"

        # Simpan URL ke Firestore
        (
            db.collection("users")
            .document(user["uid"])
            .update({"photo_url": photo_url})
        )

        return {
            "success": True,
            "message": "Foto profil berhasil diupload",
            "photo_url": photo_url,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── PUT /profile ─────────────────────────────────────────────────────────────

@router.put("")
def update_profile(
    data: UpdateProfileRequest,
    user=Depends(get_current_user)
):
    try:
        doc_ref = (
            db.collection("users")
            .document(user["uid"])
        )

        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Profil user tidak ditemukan"
            )

        update_data = {}

        if data.fullname is not None:
            fullname = data.fullname.strip()
            if not fullname:
                raise HTTPException(
                    status_code=400,
                    detail="Nama tidak boleh kosong"
                )
            update_data["fullname"] = fullname

        if data.photo_url is not None:
            update_data["photo_url"] = data.photo_url.strip()

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="Tidak ada data yang diperbarui"
            )

        doc_ref.update(update_data)

        updated_doc = doc_ref.get().to_dict()

        return {
            "success": True,
            "message": "Profil berhasil diperbarui",
            "data": {
                "uid": user["uid"],
                "fullname": updated_doc.get("fullname", ""),
                "email": updated_doc.get("email", ""),
                "photo_url": updated_doc.get("photo_url", ""),
                "streak": updated_doc.get("streak", 0),
                "productivity_score": updated_doc.get("productivity_score", 0),
                "focus_time": updated_doc.get("focus_time", 0),
                "tasks_done": updated_doc.get("tasks_done", 0),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /profile/change-password ────────────────────────────────────────────

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user=Depends(get_current_user)
):
    try:
        if len(data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password baru minimal 6 karakter"
            )

        api_key = os.getenv("FIREBASE_WEB_API_KEY")

        user_doc = (
            db.collection("users")
            .document(user["uid"])
            .get()
        )

        if not user_doc.exists:
            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan"
            )

        email = user_doc.to_dict().get("email", "")

        verify_url = (
            "https://identitytoolkit.googleapis.com"
            f"/v1/accounts:signInWithPassword?key={api_key}"
        )

        verify_response = requests.post(
            verify_url,
            json={
                "email": email,
                "password": data.current_password,
                "returnSecureToken": True,
            }
        )

        if verify_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Password saat ini tidak sesuai"
            )

        from firebase_admin import auth as firebase_auth
        firebase_auth.update_user(
            user["uid"],
            password=data.new_password
        )

        return {
            "success": True,
            "message": "Password berhasil diubah"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
