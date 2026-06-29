from firebase_admin import firestore

from app.core.firebase import db


def log_activity(
    user_id: str,
    user_name: str,
    user_email: str,
    module: str,
    action: str,
    description: str,
):
    db.collection(
        "activity_logs"
    ).add({
        "user_id": user_id,
        "user_name": user_name,
        "user_email": user_email,
        "module": module,
        "action": action,
        "description": description,
        "created_at": firestore.SERVER_TIMESTAMP,
    })