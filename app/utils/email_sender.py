import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()


def send_otp_email(
    recipient_email: str,
    fullname: str,
    otp: str
):
    sender_email = os.getenv(
        "EMAIL_HOST_USER"
    )

    sender_password = os.getenv(
        "EMAIL_HOST_PASSWORD"
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

    message = MIMEMultipart(
        "alternative"
    )

    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    message.attach(
        MIMEText(
            html,
            "html"
        )
    )

    try:
        server = smtplib.SMTP(
            os.getenv("EMAIL_HOST"),
            int(
                os.getenv(
                    "EMAIL_PORT"
                )
            )
        )

        server.starttls()

        server.login(
            sender_email,
            sender_password
        )

        server.sendmail(
            sender_email,
            recipient_email,
            message.as_string()
        )

        server.quit()

        return True

    except Exception as e:
        print(
            "EMAIL ERROR:",
            str(e)
        )

        return False