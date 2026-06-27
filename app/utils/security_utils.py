import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise ValueError(
        "FERNET_KEY belum diisi pada file .env"
    )

fernet = Fernet(
    FERNET_KEY.encode()
)


def encrypt_password(password: str):
    return fernet.encrypt(
        password.encode()
    ).decode()


def decrypt_password(
    encrypted_password: str
):
    return fernet.decrypt(
        encrypted_password.encode()
    ).decode()