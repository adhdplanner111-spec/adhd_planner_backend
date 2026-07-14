from fastapi import APIRouter, Depends
from firebase_admin import firestore
from datetime import datetime, timedelta

from app.core.firebase import db
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    print("===== DASHBOARD =====")
    print("UID:", user["uid"])

    task_docs = (
        db.collection("tasks")
        .where(
            filter=firestore.FieldFilter(
                "user_id",
                "==",
                user["uid"]
            )
        )
        .stream()
    )

    tasks = []

    for doc in task_docs:
        data = doc.to_dict()
        print("DOC:", doc.id)
        print(data)
        tasks.append(data)

    print("TOTAL TASKS:", len(tasks))

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if str(task.get("status", "")).lower() == "completed"
    )

    print("COMPLETED:", completed_tasks)

@router.get("/weekly")
def weekly(
    user=Depends(get_current_user)
):
    session_docs = (
        db.collection("focus_sessions")
        .where(
            filter=firestore.FieldFilter(
                "user_id",
                "==",
                user["uid"]
            )
        )
        .stream()
    )

    sessions = [doc.to_dict() for doc in session_docs]

    weekly_data = {
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0,
        "Sunday": 0
    }

    for session in sessions:
        if (
            session.get("type") == "focus"
            and session.get("completed")
            and session.get("ended_at")
        ):
            day = session[
                "ended_at"
            ].strftime("%A")

            weekly_data[day] += session.get(
                "duration",
                0
            )

    return {
        "success": True,
        "data": weekly_data
    }
    