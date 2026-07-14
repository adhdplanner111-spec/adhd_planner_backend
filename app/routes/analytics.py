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
def dashboard(
    user=Depends(get_current_user)
):
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

    tasks = [doc.to_dict() for doc in task_docs]

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if str(task.get("status", "")).lower() == "completed"
    )

    pending_tasks = sum(
        1
        for task in tasks
        if str(task.get("status", "")).lower() == "pending"
    )

    plan_docs = (
        db.collection("focus_plans")
        .where(
            filter=firestore.FieldFilter(
                "user_id",
                "==",
                user["uid"]
            )
        )
        .stream()
    )

    plans = [doc.to_dict() for doc in plan_docs]

    total_plans = len(plans)

    completed_plans = sum(
        1
        for plan in plans
        if plan.get("status") == "completed"
    )

    active_plans = sum(
        1
        for plan in plans
        if plan.get("status") == "active"
    )

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

    total_focus_minutes = sum(
        session.get("duration", 0)
        for session in sessions
        if (
            session.get("type") == "focus"
            and session.get("completed")
        )
    )

    focus_hours = round(total_focus_minutes / 60, 1)

    focus_dates = set()

    for session in sessions:
        if (
            session.get("type") == "focus"
            and session.get("completed")
            and session.get("ended_at")
        ):
            ended = session["ended_at"]
            if hasattr(ended, "date"):
                focus_dates.add(ended.date())

    streak = 0

    current_date = datetime.utcnow().date()

    while current_date in focus_dates:
        streak += 1
        current_date -= timedelta(days=1)

    productivity_score = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

    return {
        "success": True,
        "data": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "focus_hours": focus_hours,
            "completed_focus_plans": completed_plans,
            "active_focus_plans": active_plans,
            "current_streak": streak,
            "productivity_score": productivity_score
        }
    }

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
    