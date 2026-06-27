import os
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

db = None

try:
    cred = credentials.Certificate(
        os.path.join(
            BASE_DIR,
            "serviceAccountKey.json"
        )
    )

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()

except Exception as e:
    print(f"Firebase tidak aktif: {e}")