import os

import requests as http_requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from firebase_admin import auth, firestore
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.core.firebase import db
from app.utils.activity_logger import log_activity

router = APIRouter(
    tags=["Account Deletion"]
)


# ─── Helper: hapus SEMUA data milik satu user ─────────────────────────────

def _delete_all_user_data(uid: str):
    """
    Hapus seluruh jejak data seorang user:
    - dokumen di collection "users"
    - semua "tasks" milik user
    - semua "focus_plans" milik user
    - semua "focus_sessions" milik user
    - semua "activity_logs" milik user
    - foto profil (file lokal) milik user
    - akun Firebase Authentication user
    """

    # Ambil data user dulu (buat logging & cek foto profil), sebelum dihapus
    user_doc = db.collection("users").document(uid).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}

    # 1. Hapus semua tasks milik user
    tasks = (
        db.collection("tasks")
        .where("user_id", "==", uid)
        .stream()
    )
    for doc in tasks:
        doc.reference.delete()

    # 2. Hapus semua focus_plans milik user
    focus_plans = (
        db.collection("focus_plans")
        .where(filter=firestore.FieldFilter("user_id", "==", uid))
        .stream()
    )
    for doc in focus_plans:
        doc.reference.delete()

    # 3. Hapus semua focus_sessions milik user
    focus_sessions = (
        db.collection("focus_sessions")
        .where(filter=firestore.FieldFilter("user_id", "==", uid))
        .stream()
    )
    for doc in focus_sessions:
        doc.reference.delete()

    # 4. Hapus semua activity_logs milik user
    activity_logs = (
        db.collection("activity_logs")
        .where(filter=firestore.FieldFilter("user_id", "==", uid))
        .stream()
    )
    for doc in activity_logs:
        doc.reference.delete()

    # 5. Hapus file foto profil lokal (kalau ada)
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )
    PROFILE_PHOTOS_DIR = os.path.join(
        BASE_DIR, "media", "profile_photos"
    )
    for ext in ("jpg", "png", "webp"):
        photo_path = os.path.join(
            PROFILE_PHOTOS_DIR, f"{uid}.{ext}"
        )
        if os.path.exists(photo_path):
            os.remove(photo_path)

    # 6. Hapus dokumen utama user di Firestore
    db.collection("users").document(uid).delete()

    # 7. Hapus akun dari Firebase Authentication
    try:
        auth.delete_user(uid)
    except Exception:
        # Kalau memang sudah tidak ada di Firebase Auth, abaikan saja
        pass

    # 8. Catat log (opsional, untuk audit trail internal Anda sendiri)
    try:
        log_activity(
            user_id=uid,
            user_name=user_data.get("fullname", ""),
            user_email=user_data.get("email", ""),
            module="Account",
            action="Delete Account",
            description="User menghapus akun & seluruh datanya secara permanen",
        )
    except Exception:
        pass


# ─── 1. Endpoint terautentikasi (dipanggil dari dalam aplikasi) ───────────
# Dipakai kalau user sudah login di app dan menekan tombol "Hapus Akun"
# di halaman Profile/Settings.

@router.delete("/profile/delete-account")
def delete_my_account(
    user=Depends(get_current_user)
):
    try:
        _delete_all_user_data(user["uid"])

        return {
            "success": True,
            "message": "Akun dan seluruh data Anda berhasil dihapus secara permanen."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 2. Endpoint publik: login lalu langsung hapus ─────────────────────────
# Dipakai oleh halaman /deleted (form email + password) untuk pengguna
# yang datang dari link di listing Google Play, tanpa perlu install app.

class DeleteAccountLoginRequest(BaseModel):
    email: str
    password: str


@router.post("/account/request-deletion")
def request_deletion_with_login(
    data: DeleteAccountLoginRequest
):
    api_key = os.getenv("FIREBASE_WEB_API_KEY")

    verify_url = (
        "https://identitytoolkit.googleapis.com"
        f"/v1/accounts:signInWithPassword?key={api_key}"
    )

    verify_response = http_requests.post(
        verify_url,
        json={
            "email": data.email,
            "password": data.password,
            "returnSecureToken": True,
        },
    )

    if verify_response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Email atau password salah."
        )

    uid = verify_response.json()["localId"]

    try:
        _delete_all_user_data(uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "success": True,
        "message": "Akun dan seluruh data Anda berhasil dihapus secara permanen."
    }


# ─── 3. Halaman publik /deleted ─────────────────────────────────────────────
# Ini link yang dimasukkan ke form "Data Deletion URL" di Play Console.
# Halaman ini bisa dibuka siapa saja (memenuhi syarat Play harus publicly
# accessible), tapi proses penghapusan datanya sendiri tetap mewajibkan
# pengguna login dengan email & password akun ADHD Planner mereka.

DELETE_PAGE_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hapus Data Akun - ADHD Planner</title>
<style>
  body {
    font-family: -apple-system, Arial, sans-serif;
    background: #0d0d12;
    color: #eaeaea;
    max-width: 560px;
    margin: 0 auto;
    padding: 32px 20px 60px;
    line-height: 1.6;
  }
  h1 { font-size: 22px; margin-bottom: 4px; }
  h2 { font-size: 16px; margin-top: 32px; color: #fff; }
  p, li { color: #b8b8c0; font-size: 14px; }
  ol { padding-left: 20px; }
  .card {
    background: #16161d;
    border: 1px solid #26262f;
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
  }
  input {
    width: 100%;
    box-sizing: border-box;
    padding: 12px 14px;
    margin-top: 10px;
    border-radius: 10px;
    border: 1px solid #33333e;
    background: #0d0d12;
    color: #fff;
    font-size: 14px;
  }
  button {
    width: 100%;
    margin-top: 16px;
    padding: 13px 14px;
    border: none;
    border-radius: 10px;
    background: #e5484d;
    color: #fff;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
  }
  button:disabled { opacity: 0.6; cursor: not-allowed; }
  #msg { margin-top: 14px; font-size: 14px; }
  .success { color: #4ade80; }
  .error { color: #f87171; }
  .warning {
    background: #2a1414;
    border: 1px solid #5c2323;
    color: #fca5a5;
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 13px;
    margin-top: 20px;
  }
</style>
</head>
<body>

  <h1>Permintaan Penghapusan Data</h1>
  <p>ADHD Planner &mdash; aplikasi manajemen fokus &amp; produktivitas</p>

  <h2>Langkah-langkah</h2>
  <ol>
    <li>Masukkan email dan password akun ADHD Planner Anda pada form di bawah.</li>
    <li>Tekan tombol <b>"Hapus Akun &amp; Data Saya"</b>.</li>
    <li>Setelah berhasil, akun dan seluruh data Anda akan dihapus permanen dari server kami dan tidak dapat dipulihkan.</li>
  </ol>

  <h2>Data yang dihapus</h2>
  <p>
    Saat Anda menghapus akun, kami menghapus secara permanen: nama lengkap,
    alamat email, foto profil, daftar tugas (tasks), sesi &amp; rencana
    fokus (focus sessions/plans), serta riwayat aktivitas Anda di aplikasi.
  </p>

  <h2>Periode retensi data</h2>
  <p>
    Data dihapus secara langsung (real-time) begitu permintaan penghapusan
    berhasil diproses. Kami tidak menyimpan salinan cadangan tambahan
    setelah proses ini selesai.
  </p>

  <div class="card">
    <label for="email">Email</label>
    <input type="email" id="email" placeholder="email@contoh.com">

    <label for="password" style="display:block; margin-top:14px;">Password</label>
    <input type="password" id="password" placeholder="Password akun Anda">

    <button id="deleteBtn" onclick="requestDeletion()">Hapus Akun &amp; Data Saya</button>
    <div id="msg"></div>
  </div>

  <div class="warning">
    Tindakan ini bersifat permanen dan tidak dapat dibatalkan. Pastikan Anda
    yakin sebelum melanjutkan.
  </div>

<script>
async function requestDeletion() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const msg = document.getElementById('msg');
  const btn = document.getElementById('deleteBtn');

  if (!email || !password) {
    msg.className = 'error';
    msg.textContent = 'Email dan password wajib diisi.';
    return;
  }

  const confirmed = confirm(
    'Akun dan SELURUH data Anda akan dihapus permanen. Lanjutkan?'
  );
  if (!confirmed) return;

  btn.disabled = true;
  msg.className = '';
  msg.textContent = 'Memproses permintaan...';

  try {
    const res = await fetch('/account/request-deletion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok && data.success) {
      msg.className = 'success';
      msg.textContent = data.message || 'Akun berhasil dihapus.';
      document.getElementById('email').value = '';
      document.getElementById('password').value = '';
    } else {
      msg.className = 'error';
      msg.textContent = data.detail || 'Gagal menghapus akun.';
      btn.disabled = false;
    }
  } catch (e) {
    msg.className = 'error';
    msg.textContent = 'Terjadi kesalahan jaringan. Coba lagi.';
    btn.disabled = false;
  }
}
</script>

</body>
</html>
"""


@router.get("/deleted", response_class=HTMLResponse)
def data_deletion_page():
    return HTMLResponse(content=DELETE_PAGE_HTML)