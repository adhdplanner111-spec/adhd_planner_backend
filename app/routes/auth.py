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
)

from app.schemas.otp_schema import (
    RegisterOTPRequest,
    ResendOTPRequest,
    VerifyOTPRequest,
)

from app.utils.email_sender import send_otp_email
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
            "uid": user.uid,
            "message":
                "Registrasi berhasil. Silakan login."
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

        # timpa OTP lama
        doc_ref.update({
            "otp": otp,
            "expires_at": expires_at
        })

        # kirim email baru
        email_sent = send_otp_email(
            recipient_email=pending["email"],
            fullname=pending["fullname"],
            otp=otp
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

    return {
        "success": True,
        "uid": firebase_data["localId"],
        "access_token": token
    }

