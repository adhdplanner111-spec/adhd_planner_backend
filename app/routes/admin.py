from datetime import datetime
import os

from fastapi import Depends
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.core.admin_dependencies import get_current_admin
from app.core.firebase import db
from fastapi import Depends
from datetime import datetime, timedelta
from datetime import datetime, timedelta

from app.schemas.admin_pending_schema import (
    UpdatePendingOtpSchema,
)

from app.utils.email_sender import (
    send_otp_email,
)

from app.utils.activity_logger import (
    log_activity,
)

from app.core.admin_dependencies import (
    get_current_admin
)

from app.schemas.admin_schema import (
    AdminLoginSchema
)

from app.schemas.admin_task_schema import (
    AdminUpdateTaskSchema
)

from app.schemas.admin_user_schema import (
    CreateUserSchema,
)

from app.core.security import (
    create_access_token
)

from firebase_admin import auth, firestore
from app.schemas.admin_user_schema import (
    AdminUpdateUserSchema
)
from app.utils.activity_logger import log_activity

load_dotenv()

router = APIRouter(
    tags=["admin"]
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

@router.post("/users")
def create_user(
    data: CreateUserSchema,
    admin=Depends(get_current_admin)
):

    try:

        try:

            auth.get_user_by_email(
                data.email
            )

            raise HTTPException(
                status_code=400,
                detail="Email sudah terdaftar"
            )

        except auth.UserNotFoundError:
            pass

        user = auth.create_user(
            email=data.email,
            password=data.password,
            display_name=data.fullname
        )

        db.collection(
            "users"
        ).document(
            user.uid
        ).set({

            "fullname":
                data.fullname,

            "email":
                data.email,

            "streak": 0,

            "productivity_score": 0,

            "created_at":
                firestore.SERVER_TIMESTAMP

        })

        log_activity(
            user_id="ADMIN",
            user_name="System Admin",
            user_email="admin@adhdplanner.com",
            module="Admin",
            action="Create User",
            description=(
                f"Membuat user "
                f"{data.fullname}"
            )
        )

        return {

            "success": True,

            "message":
                "User berhasil dibuat."

        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/users")
def get_users(
    admin=Depends(get_current_admin)
):

    docs = db.collection(
        "users"
    ).stream()

    users = []

    for doc in docs:

        user = doc.to_dict()

        task_docs = (
            db.collection("tasks")
            .where(
                filter=firestore.FieldFilter(
                    "user_id",
                    "==",
                    doc.id
                )
            )
            .stream()
        )

        total_tasks = len(
            list(task_docs)
        )

        created_at = user.get(
            "created_at"
        )

        users.append({

            "uid": doc.id,

            "fullname":
                user.get(
                    "fullname"
                ),

            "email":
                user.get(
                    "email"
                ),

            "streak":
                user.get(
                    "streak",
                    0
                ),

            "productivity_score":
                user.get(
                    "productivity_score",
                    0
                ),

            "total_tasks":
                total_tasks,

            "created_at":
                (
                    created_at.isoformat()
                    if created_at
                    else None
                )

        })

    users.sort(
        key=lambda x:
        x["fullname"].lower()
    )

    return {
        "success": True,
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

    log_activity(
        user_id="ADMIN",
        user_name="Admin",
        user_email="adhdadmin@adhdplanner.com",
        module="Admin",
        action="Delete User",
        description=(
            f"Menghapus user "
            f"{user_data['fullname']} "
            f"({user_data['email']})"
        )
    )

    db.collection(
        "users"
    ).document(uid).delete()

    return {
        "success": True,
        "message": "User berhasil dihapus"
    }

@router.get("/tasks")
def get_tasks(
    admin=Depends(get_current_admin)
):
    docs = db.collection(
        "tasks"
    ).stream()

    tasks = []

    for doc in docs:

        task = doc.to_dict()

        email = None

        user_doc = (
            db.collection("users")
            .document(task["user_id"])
            .get()
        )

        if user_doc.exists:
            email = (
                user_doc.to_dict()
                .get("email")
            )

        tasks.append({
            "task_id": doc.id,
            "user_email": email,
            **task
        })

    return {
        "success": True,
        "total": len(tasks),
        "data": tasks
    }

@router.get("/tasks/{task_id}")
def get_task(
    task_id: str,
    admin=Depends(get_current_admin)
):
    doc = (
        db.collection("tasks")
        .document(task_id)
        .get()
    )

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    return {
        "success": True,
        "data": {
            "task_id": doc.id,
            **doc.to_dict()
        }
    }

@router.put("/tasks/{task_id}")
def update_task(
    task_id: str,
    data: AdminUpdateTaskSchema,
    admin=Depends(get_current_admin)
):
    ref = db.collection(
        "tasks"
    ).document(task_id)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    update_data = {}

    if data.title is not None:
        update_data["title"] = data.title

    if data.description is not None:
        update_data["description"] = data.description

    if data.completed is not None:
        update_data["completed"] = data.completed

    if data.priority is not None:
        update_data["priority"] = data.priority

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada data yang diubah"
        )

    ref.update(update_data)

    return {
        "success": True,
        "message": "Task berhasil diperbarui"
    }

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: str,
    admin=Depends(get_current_admin)
):
    ref = db.collection(
        "tasks"
    ).document(task_id)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    task = doc.to_dict()

    log_activity(
        user_id="ADMIN",
        user_name="Admin",
        user_email="adhdadmin@adhdplanner.com",
        module="Admin",
        action="Delete Task",
        description=(
            f"Menghapus task "
            f"'{task.get('title', '-')}'"
        )
    )
    
    ref.delete()

    return {
        "success": True,
        "message": "Task berhasil dihapus"
    }

@router.get("/focus/plans")
def get_focus_plans(
    admin=Depends(get_current_admin)
):
    docs = db.collection(
        "focus_plans"
    ).stream()

    plans = []

    for doc in docs:

        plan = doc.to_dict()

        user_email = None

        user_doc = (
            db.collection("users")
            .document(plan["user_id"])
            .get()
        )

        if user_doc.exists:
            user_email = (
                user_doc.to_dict()
                .get("email")
            )

        plans.append({
            "plan_id": doc.id,
            "user_email": user_email,
            **plan
        })

    return {
        "success": True,
        "total": len(plans),
        "data": plans
    }

@router.get("/focus/plans/{plan_id}")
def get_focus_plan(
    plan_id: str,
    admin=Depends(get_current_admin)
):
    doc = (
        db.collection("focus_plans")
        .document(plan_id)
        .get()
    )

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Plan tidak ditemukan"
        )

    return {
        "success": True,
        "data": {
            "plan_id": doc.id,
            **doc.to_dict()
        }
    }

@router.get("/focus/sessions")
def get_focus_sessions(
    admin=Depends(get_current_admin)
):
    docs = db.collection(
        "focus_sessions"
    ).stream()

    sessions = []

    for doc in docs:

        session = doc.to_dict()

        user_email = None

        user_doc = (
            db.collection("users")
            .document(session["user_id"])
            .get()
        )

        if user_doc.exists:
            user_email = (
                user_doc.to_dict()
                .get("email")
            )

        sessions.append({
            "session_id": doc.id,
            "user_email": user_email,
            **session
        })

    return {
        "success": True,
        "total": len(sessions),
        "data": sessions
    }

@router.get("/focus/sessions/{session_id}")
def get_focus_session(
    session_id: str,
    admin=Depends(get_current_admin)
):
    doc = (
        db.collection("focus_sessions")
        .document(session_id)
        .get()
    )

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Session tidak ditemukan"
        )

    return {
        "success": True,
        "data": {
            "session_id": doc.id,
            **doc.to_dict()
        }
    }

@router.delete("/focus/sessions/{session_id}")
def delete_session(
    session_id: str,
    admin=Depends(get_current_admin)
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

    log_activity(
        user_id="ADMIN",
        user_name="Admin",
        user_email="adhdadmin@adhdplanner.com",
        module="Admin",
        action="Delete Focus Session",
        description=(
            f"Menghapus session milik "
            f"{session.get('user_email', '-')}"
        )
    )

    ref.delete()

    return {
        "success": True,
        "message":
            "Session berhasil dihapus"
    }

@router.get("/pending-registrations")
def get_pending_registrations(
    admin=Depends(get_current_admin)
):
    docs = db.collection(
        "pending_registrations"
    ).stream()

    registrations = []

    for doc in docs:

        data = doc.to_dict()

        is_expired = (
            datetime.utcnow()
            >
            data["expires_at"].replace(
                tzinfo=None
            )
        )

        registrations.append({

            "email": doc.id,

            "fullname": data.get(
                "fullname"
            ),

            "otp": data.get(
                "otp"
            ),

            "status": (
                "expired"
                if is_expired
                else "active"
            ),

            "expires_at": (
                data.get("expires_at").isoformat()
                if data.get("expires_at")
                else None
            ),

            "created_at": (
                data.get("created_at").isoformat()
                if data.get("created_at")
                else None
            )

        })

    return {
        "success": True,
        "total": len(registrations),
        "data": registrations
    }

@router.get(
    "/pending-registrations/{email}"
)
def get_pending_registration(
    email: str,
    admin=Depends(get_current_admin)
):
    doc = (
        db.collection(
            "pending_registrations"
        )
        .document(email)
        .get()
    )

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Data tidak ditemukan"
        )

    data = doc.to_dict()

    is_expired = (
        datetime.utcnow()
        >
        data["expires_at"].replace(
            tzinfo=None
        )
    )

    return {
        "success": True,
        "data": {
            "email": doc.id,
            "fullname": data["fullname"],
            "status": (
                "expired"
                if is_expired
                else "active"
            ),
            "created_at": data["created_at"],
            "expires_at": data["expires_at"]
        }
    }

@router.delete("/pending-registrations/{email}")
def delete_pending_registration(
    email: str,
    admin=Depends(get_current_admin)
):
    ref = db.collection(
        "pending_registrations"
    ).document(email)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Data tidak ditemukan"
        )

    log_activity(
        user_id="ADMIN",
        user_name="Admin",
        user_email="adhdadmin@adhdplanner.com",
        module="Admin",
        action="Delete Pending OTP",
        description=(
            f"Menghapus pending registrasi "
            f"{email}"
        )
    )

    ref.delete()

    return {
        "success": True,
        "message":
            "Pending registration berhasil dihapus"
    }

@router.get("/analytics/weekly")
def admin_weekly(
    admin=Depends(get_current_admin)
):
    docs = (
        db.collection(
            "focus_sessions"
        ).stream()
    )

    weekly = {
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0,
        "Sunday": 0
    }

    for doc in docs:

        session = doc.to_dict()

        if (
            session.get("type") == "focus"
            and session.get("completed")
            and session.get("ended_at")
        ):

            day = session[
                "ended_at"
            ].strftime("%A")

            weekly[day] += session.get(
                "duration",
                0
            )

    result = []

    for day, value in weekly.items():
        result.append({
            "day": day,
            "focus": value
        })

    return {
        "success": True,
        "data": result
    }

@router.get("/activity-logs")
def get_activity_logs(
    admin=Depends(get_current_admin)
):
    docs = (
        db.collection("activity_logs")
        .order_by(
            "created_at",
            direction=firestore.Query.DESCENDING
        )
        .limit(20)
        .stream()
    )

    logs = []

    for doc in docs:

        data = doc.to_dict()

        created_at = data.get("created_at")

        logs.append({
            "id": doc.id,
            "user_name": data.get("user_name"),
            "user_email": data.get("user_email"),
            "module": data.get("module"),
            "action": data.get("action"),
            "description": data.get("description"),
            "created_at": (
                created_at.isoformat()
                if created_at
                else None
            )
        })

    return {
        "success": True,
        "data": logs
    }

@router.put("/pending-registrations/{email}")
def update_pending_registration(
    email: str,
    data: UpdatePendingOtpSchema,
    admin=Depends(get_current_admin)
):

    ref = (
        db.collection(
            "pending_registrations"
        )
        .document(email)
    )

    doc = ref.get()

    if not doc.exists:

        raise HTTPException(
            status_code=404,
            detail="Pending registration tidak ditemukan"
        )

    pending = doc.to_dict()

    expires_at = (
        datetime.utcnow()
        +
        timedelta(
            minutes=data.expire_minutes
        )
    )

    ref.update({

        "otp": data.otp,

        "expires_at": expires_at

    })

    email_sent = send_otp_email(

        recipient_email=email,

        fullname=pending["fullname"],

        otp=data.otp

    )

    log_activity(

        user_id="ADMIN",

        user_name="System Admin",

        user_email="admin@adhdplanner.com",

        module="Admin",

        action="Edit Pending OTP",

        description=(
            f"Mengubah OTP dan mengirim ulang ke {email}"
        )

    )

    return {

        "success": True,

        "email_sent": email_sent,

        "message":
            "OTP berhasil diperbarui."

    }