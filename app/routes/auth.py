from datetime import datetime, timedelta
import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from firebase_admin import auth, firestore

from app.core.firebase import db
from app.core.security import create_access_token

from app.schemas.auth_schema import (
    LoginSchema,
    RegisterSchema,
    GoogleLoginSchema,
)

from app.schemas.otp_schema import (
    RegisterOTPRequest,
    ResendOTPRequest,
    VerifyOTPRequest,
)

from app.utils.email_sender import send_otp_email
from app.utils.activity_logger import log_activity
from app.utils.otp import generate_otp
from app.utils.security_utils import (
    decrypt_password,
    encrypt_password,
)

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(
    data: RegisterOTPRequest
):
    try:

        try:
            auth.get_user_by_email(
                data.email
            )

            raise HTTPException(
                status_code=400,
                detail="Email sudah terdaftar"
            )

        except auth.UserNotFoundError:
            pass

        otp = generate_otp()

        encrypted_password = (
            encrypt_password(
                data.password
            )
        )

        expire_minutes = int(
            os.getenv(
                "OTP_EXPIRE_MINUTES",
                5
            )
        )

        expires_at = (
            datetime.utcnow()
            +
            timedelta(
                minutes=expire_minutes
            )
        )

        db.collection(
            "pending_registrations"
        ).document(
            data.email
        ).set({
            "fullname": data.fullname,
            "email": data.email,
            "encrypted_password":
                encrypted_password,
            "otp": otp,
            "expires_at": expires_at,
            "created_at":
                firestore.SERVER_TIMESTAMP
        })

        email_sent = send_otp_email(
            recipient_email=data.email,
            fullname=data.fullname,
            otp=otp
        )

        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail="Gagal mengirim OTP"
            )

        return {
            "success": True,
            "message":
                "OTP berhasil dikirim."
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest
):
    try:

        doc_ref = db.collection(
            "pending_registrations"
        ).document(data.email)

        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Data registrasi tidak ditemukan"
            )

        pending = doc.to_dict()

        if pending["otp"] != data.otp:
            raise HTTPException(
                status_code=400,
                detail="OTP tidak valid"
            )

        expires_at = pending["expires_at"]

        if datetime.utcnow() > expires_at.replace(
            tzinfo=None
        ):
            raise HTTPException(
                status_code=400,
                detail="OTP sudah kadaluarsa"
            )

        try:
            auth.get_user_by_email(
                pending["email"]
            )

            raise HTTPException(
                status_code=400,
                detail="Email sudah terdaftar"
            )

        except auth.UserNotFoundError:
            pass

        original_password = (
            decrypt_password(
                pending[
                    "encrypted_password"
                ]
            )
        )

        user = auth.create_user(
            email=pending["email"],
            password=original_password,
            display_name=pending["fullname"]
        )

        log_activity(
            user.uid,
            pending["fullname"],
            pending["email"],
            "Authentication",
            "Verify OTP",
            "Verifikasi OTP berhasil"
        )

        log_activity(
            user.uid,
            pending["fullname"],
            pending["email"],
            "Authentication",
            "Register",
            "User berhasil membuat akun"
        )

        db.collection("users").document(
            user.uid
        ).set({
            "fullname":
                pending["fullname"],

            "email":
                pending["email"],

            "streak": 0,

            "productivity_score": 0,

            "created_at":
                firestore.SERVER_TIMESTAMP
        })

        doc_ref.delete()

        return {
            "success": True,
            "message": "Registrasi berhasil. Silakan login."
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.post("/resend-otp")
def resend_otp(
    data: ResendOTPRequest
):
    try:

        doc_ref = db.collection(
            "pending_registrations"
        ).document(data.email)

        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Data registrasi tidak ditemukan. "
                    "Silakan register kembali."
                )
            )

        pending = doc.to_dict()

        otp = generate_otp()

        expire_minutes = int(
            os.getenv(
                "OTP_EXPIRE_MINUTES",
                5
            )
        )

        expires_at = (
            datetime.utcnow()
            +
            timedelta(
                minutes=expire_minutes
            )
        )

        doc_ref.update({
            "otp": otp,
            "expires_at": expires_at
        })

        email_sent = send_otp_email(
            recipient_email=pending["email"],
            fullname=pending["fullname"],
            otp=otp
        )

        log_activity(
            "",
            pending["fullname"],
            pending["email"],
            "Authentication",
            "Resend OTP",
            "Mengirim ulang kode OTP"
        )

        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail="Gagal mengirim OTP"
            )

        return {
            "success": True,
            "message": (
                "OTP baru berhasil dikirim. "
                "Silakan cek email Anda."
            )
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login")
def login(data: LoginSchema):

    api_key = os.getenv("FIREBASE_WEB_API_KEY")

    url = (
        "https://identitytoolkit.googleapis.com"
        f"/v1/accounts:signInWithPassword?key={api_key}"
    )

    payload = {
        "email": data.email,
        "password": data.password,
        "returnSecureToken": True
    }

    response = requests.post(
        url,
        json=payload
    )

    if response.status_code != 200:

        pending_doc = (
            db.collection(
                "pending_registrations"
            )
            .document(data.email)
            .get()
        )

        if pending_doc.exists:

            pending = pending_doc.to_dict()

            expires_at = pending["expires_at"]

            if datetime.utcnow() > expires_at.replace(
                tzinfo=None
            ):
                raise HTTPException(
                    status_code=403,
                    detail="OTP sudah kadaluarsa. Silakan kirim ulang OTP."
                )

            raise HTTPException(
                status_code=403,
                detail=(
                    "Akun belum diverifikasi. "
                    "Silakan masukkan kode OTP."
                )
            )

        raise HTTPException(
            status_code=401,
            detail="Email atau password salah"
        )

    firebase_data = response.json()

    token = create_access_token({
        "uid": firebase_data["localId"],
        "email": data.email
    })

    user_doc = (
        db.collection("users")
        .document(firebase_data["localId"])
        .get()
    )

    user_data = user_doc.to_dict()

    log_activity(
        firebase_data["localId"],
        user_data["fullname"],
        user_data["email"],
        "Authentication",
        "Login",
        "User login ke aplikasi"
    )

    return {
        "success": True,
        "message": "Login berhasil",
        "data": {
            "uid": firebase_data["localId"],
            "fullname": user_data["fullname"],
            "email": user_data["email"],
            "photo_url": user_data.get("photo_url", ""),
            "streak": user_data.get("streak", 0),
            "productivity_score": user_data.get("productivity_score", 0),
            "access_token": token,
        }
    }

@router.post("/google-login")
def google_login(
    data: GoogleLoginSchema,
):

    decoded_token = auth.verify_id_token(
        data.id_token
    )

    uid = decoded_token["uid"]

    email = decoded_token["email"]

    fullname = decoded_token.get(
        "name",
        email.split("@")[0],
    )

    photo_url = decoded_token.get(
        "picture",
        "",
    )

    user_ref = db.collection(
        "users"
    ).document(uid)

    user_doc = user_ref.get()

    if not user_doc.exists:

        user_ref.set({

            "fullname": fullname,

            "email": email,

            "photo_url": photo_url,

            "streak": 0,

            "productivity_score": 0,

            "created_at":
                firestore.SERVER_TIMESTAMP,

        })

    else:

        user_ref.update({

            "fullname": fullname,

            "photo_url": photo_url,

        })

    log_activity(

        uid,

        fullname,

        email,

        "Authentication",

        "Google Login",

        "User berhasil login menggunakan Google"

    )

    token = create_access_token({

        "uid": uid,

        "email": email,

    })

    return {
        "success": True,
        "message": "Login Google berhasil",
        "data": {
            "uid": uid,
            "fullname": fullname,
            "email": email,
            "photo_url": photo_url,
            "streak": 0,
            "productivity_score": 0,
            "access_token": token,
        }
    }

