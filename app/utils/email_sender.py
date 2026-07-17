import os
import socket

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()


# --- Paksa requests/urllib3 pakai IPv4 saja ---
# Railway (dan beberapa PaaS lain) mematikan outbound IPv6 secara default.
# Kalau host tujuan (mis. api.resend.com) punya AAAA record (IPv6),
# socket akan coba IPv6 dulu dan gagal dengan "Network is unreachable".
# Patch ini memaksa resolusi DNS hanya mengembalikan alamat IPv4.
_orig_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(
        host, port, socket.AF_INET, type, proto, flags
    )


socket.getaddrinfo = _getaddrinfo_ipv4_only
# --- akhir patch IPv4 ---


def send_otp_email(
    recipient_email: str,
    fullname: str,
    otp: str
):
    api_key = os.getenv("RESEND_API_KEY")

    sender_email = os.getenv(
        "RESEND_FROM_EMAIL",
        "onboarding@resend.dev"
    )

    subject = "ADHD Planner - Verifikasi OTP"

    html = f"""
    <html>
    <body style="font-family: Arial;">

        <h2>
            Halo, {fullname}! 👋
        </h2>

        <p>
            Terima kasih telah mendaftar
            di <b>ADHD Planner</b>.
        </p>

        <p>
            Gunakan kode OTP berikut
            untuk menyelesaikan proses
            registrasi:
        </p>

        <div
            style="
                font-size:32px;
                font-weight:bold;
                letter-spacing:6px;
                margin:20px 0;
                color:#2563eb;
            "
        >
            {otp}
        </div>

        <p>
            OTP berlaku selama
            <b>5 menit</b>.
        </p>

        <p>
            Jika Anda tidak merasa
            melakukan registrasi,
            abaikan email ini.
        </p>

        <hr>

        <small>
            ADHD Planner Team
        </small>

    </body>
    </html>
    """

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": sender_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html,
            },
            timeout=10,
        )

        if response.status_code >= 400:
            print(
                "EMAIL ERROR:",
                response.status_code,
                response.text,
            )
            return False

        return True

    except Exception as e:
        print(
            "EMAIL ERROR:",
            str(e)
        )

        return False