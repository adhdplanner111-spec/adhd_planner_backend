import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException

# Load file .env
load_dotenv()

# Ambil konfigurasi dari environment
SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "supersecretkey123"
)

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
<<<<<<< HEAD
        600000
=======
        43800
>>>>>>> d0112576577fb8c67e8fd78705ac51e270b83c99
    )
)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication error: {str(e)}"
        )