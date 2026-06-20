import math

from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore

from app.core.firebase import db
from app.core.dependencies import get_current_user
from app.schemas.focus_schema import (
    FocusPlanCreate,
    FocusSessionCreate
)

router = APIRouter(
    prefix="/focus",
    tags=["Focus Sessions"]
)

@router.post("/plans")
def create_plan(
    data: FocusPlanCreate,
    user=Depends(get_current_user)
):
    active_plan = (
        db.collection("focus_plans")
        .where(filter=firestore.FieldFilter(
            "user_id", "==", user["uid"]
        ))
        .where(filter=firestore.FieldFilter(
            "status", "==", "active"
        ))
        .stream()
    )

    if any(active_plan):
        raise HTTPException(
            status_code=400,
            detail="Masih ada focus plan yang aktif"
        )

    total_cycles = math.ceil(
        data.total_focus_minutes /
        data.focus_duration
    )

    ref = db.collection(
        "focus_plans"
    ).document()

    ref.set({
        "user_id": user["uid"],
        "task_id": data.task_id,
        "total_focus_minutes": data.total_focus_minutes,
        "focus_duration": data.focus_duration,
        "break_duration": data.break_duration,
        "total_cycles": total_cycles,
        "completed_cycles": 0,
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP
    })

    return {
        "success": True,
        "plan_id": ref.id,
        "total_cycles": total_cycles,
        "message": "Focus plan berhasil dibuat"
    }

@router.get("/plans")
def get_plans(
    user=Depends(get_current_user)
):
    docs = (
        db.collection("focus_plans")
        .where(filter=firestore.FieldFilter(
            "user_id", "==", user["uid"]
        ))
        .stream()
    )

    plans = []

    for doc in docs:
        plans.append({
            "plan_id": doc.id,
            **doc.to_dict()
        })

    return {
        "success": True,
        "data": plans
    }

@router.get("/plans/{plan_id}")
def get_plan(
    plan_id: str,
    user=Depends(get_current_user)
):
    doc = db.collection(
        "focus_plans"
    ).document(plan_id).get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Plan tidak ditemukan"
        )

    data = doc.to_dict()

    if data["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    return {
        "success": True,
        "data": {
            "plan_id": doc.id,
            **data
        }
    }

@router.get("/plans/{plan_id}/progress")
def get_progress(
    plan_id: str,
    user=Depends(get_current_user)
):
    doc = db.collection(
        "focus_plans"
    ).document(plan_id).get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Plan tidak ditemukan"
        )

    data = doc.to_dict()

    if data["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    percentage = (
        data["completed_cycles"] /
        data["total_cycles"]
    ) * 100

    return {
        "success": True,
        "completed_cycles": data["completed_cycles"],
        "total_cycles": data["total_cycles"],
        "progress": round(percentage, 2),
        "status": data["status"]
    }

@router.post("/plans/{plan_id}/sessions")
def start_session(
    plan_id: str,
    data: FocusSessionCreate,
    user=Depends(get_current_user)
):
    plan_doc = db.collection(
        "focus_plans"
    ).document(plan_id).get()

    if not plan_doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Plan tidak ditemukan"
        )

    plan = plan_doc.to_dict()

    if plan["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    if plan["status"] == "completed":
        raise HTTPException(
            status_code=400,
            detail="Plan sudah selesai"
        )

    active = (
        db.collection("focus_sessions")
        .where(filter=firestore.FieldFilter(
            "user_id", "==", user["uid"]
        ))
        .where(filter=firestore.FieldFilter(
            "completed", "==", False
        ))
        .stream()
    )

    if any(active):
        raise HTTPException(
            status_code=400,
            detail="Masih ada session aktif"
        )

    ref = db.collection(
        "focus_sessions"
    ).document()

    ref.set({
        "plan_id": plan_id,
        "user_id": user["uid"],
        "cycle": data.cycle,
        "type": data.type,
        "duration": data.duration,
        "completed": False,
        "started_at": firestore.SERVER_TIMESTAMP,
        "ended_at": None
    })

    return {
        "success": True,
        "session_id": ref.id,
        "message": "Session dimulai"
    }

@router.post("/sessions/{session_id}/complete")
def complete_session(
    session_id: str,
    user=Depends(get_current_user)
):
    ref = db.collection(
        "focus_sessions"
    ).document(session_id)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Session tidak ditemukan"
        )

    session = doc.to_dict()

    if session["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    if session["completed"]:
        raise HTTPException(
            status_code=400,
            detail="Session sudah selesai"
        )

    ref.update({
        "completed": True,
        "ended_at": firestore.SERVER_TIMESTAMP
    })

    if session["type"] == "focus":
        plan_ref = db.collection(
            "focus_plans"
        ).document(session["plan_id"])

        plan_doc = plan_ref.get()

        if plan_doc.exists:
            plan = plan_doc.to_dict()

            completed = (
                plan["completed_cycles"] + 1
            )

            update_data = {
                "completed_cycles": completed
            }

            if completed >= plan["total_cycles"]:
                update_data["status"] = "completed"

            plan_ref.update(update_data)

    return {
        "success": True,
        "message": "Session berhasil diselesaikan"
    }

@router.get("/history")
def focus_history(
    user=Depends(get_current_user)
):
    docs = (
        db.collection("focus_sessions")
        .where(filter=firestore.FieldFilter(
            "user_id", "==", user["uid"]
        ))
        .stream()
    )

    sessions = []

    for doc in docs:
        sessions.append({
            "session_id": doc.id,
            **doc.to_dict()
        })

    return {
        "success": True,
        "data": sessions
    }
