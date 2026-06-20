import os

from fastapi import Depends
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.core.admin_dependencies import get_current_admin
from app.core.firebase import db
from fastapi import Depends
from app.core.admin_dependencies import (
    get_current_admin
)

from app.schemas.admin_schema import (
    AdminLoginSchema
)

from app.core.security import (
    create_access_token
)

from firebase_admin import auth
from app.schemas.admin_user_schema import (
    AdminUpdateUserSchema
)

load_dotenv()

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/login")
def admin_login(
    data: AdminLoginSchema
):

    admin_username = os.getenv(
        "ADMIN_USERNAME"
    )

    admin_password = os.getenv(
        "ADMIN_PASSWORD"
    )

    if (
        data.username != admin_username
        or
        data.password != admin_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Username atau password salah"
        )

    token = create_access_token({
        "sub": "admin",
        "username": admin_username,
        "is_admin": True
    })

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def admin_me(
    admin=Depends(get_current_admin)
):
    return {
        "success": True,
        "admin": admin
    }

@router.get("/dashboard")
def admin_dashboard(
    admin=Depends(get_current_admin)
):

    total_users = len(
        list(
            db.collection("users").stream()
        )
    )

    tasks = list(
        db.collection("tasks").stream()
    )

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if task.to_dict().get(
            "completed",
            False
        )
    )

    pending_tasks = (
        total_tasks
        - completed_tasks
    )

    focus_plans = list(
        db.collection(
            "focus_plans"
        ).stream()
    )

    total_focus_plans = len(
        focus_plans
    )

    active_focus_plans = sum(
        1
        for plan in focus_plans
        if plan.to_dict().get(
            "status"
        ) == "active"
    )

    completed_focus_plans = sum(
        1
        for plan in focus_plans
        if plan.to_dict().get(
            "status"
        ) == "completed"
    )

    total_focus_sessions = len(
        list(
            db.collection(
                "focus_sessions"
            ).stream()
        )
    )

    pending_registrations = len(
        list(
            db.collection(
                "pending_registrations"
            ).stream()
        )
    )

    return {
        "success": True,
        "data": {
            "total_users":
                total_users,

            "total_tasks":
                total_tasks,

            "completed_tasks":
                completed_tasks,

            "pending_tasks":
                pending_tasks,

            "total_focus_plans":
                total_focus_plans,

            "active_focus_plans":
                active_focus_plans,

            "completed_focus_plans":
                completed_focus_plans,

            "total_focus_sessions":
                total_focus_sessions,

            "pending_registrations":
                pending_registrations
        }
    }

@router.get("/users")
def get_users(
    admin=Depends(get_current_admin)
):
    docs = db.collection("users").stream()

    users = []

    for doc in docs:
        users.append({
            "uid": doc.id,
            **doc.to_dict()
        })

    return {
        "success": True,
        "total": len(users),
        "data": users
    }

@router.get("/users/{uid}")
def get_user(
    uid: str,
    admin=Depends(get_current_admin)
):
    doc = db.collection(
        "users"
    ).document(uid).get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan"
        )

    return {
        "success": True,
        "data": {
            "uid": doc.id,
            **doc.to_dict()
        }
    }

@router.put("/users/{uid}")
def update_user(
    uid: str,
    data: AdminUpdateUserSchema,
    admin=Depends(get_current_admin)
):
    ref = db.collection(
        "users"
    ).document(uid)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan"
        )

    update_data = {}

    if data.fullname is not None:
        update_data["fullname"] = data.fullname

    if data.streak is not None:
        update_data["streak"] = data.streak

    if data.productivity_score is not None:
        update_data[
            "productivity_score"
        ] = data.productivity_score

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada data yang diubah"
        )

    ref.update(update_data)

    return {
        "success": True,
        "message": "User berhasil diperbarui"
    }

@router.delete("/users/{uid}")
def delete_user(
    uid: str,
    admin=Depends(get_current_admin)
):
    doc = db.collection(
        "users"
    ).document(uid).get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="User tidak ditemukan"
        )

    user_data = doc.to_dict()

    try:
        firebase_user = auth.get_user_by_email(
            user_data["email"]
        )

        auth.delete_user(
            firebase_user.uid
        )

    except:
        pass

    db.collection(
        "users"
    ).document(uid).delete()

    return {
        "success": True,
        "message": "User berhasil dihapus"
    }