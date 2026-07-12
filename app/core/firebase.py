import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

db = None

try:
    # Prioritas 1: baca dari env var (dipakai saat deploy, misal di Railway)
    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
    else:
        # Prioritas 2: fallback ke file lokal (dipakai saat dev di laptop)
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