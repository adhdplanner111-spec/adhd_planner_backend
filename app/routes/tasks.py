from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from app.core.firebase import db
from app.core.dependencies import get_current_user
from app.schemas.task_schema import TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/")
def create_task(
    data: TaskCreate,
    user=Depends(get_current_user)
):
    task_ref = db.collection("tasks").document()

    task_ref.set({
        "user_id": user["uid"],
        "title": data.title,
        "description": data.description,
        "priority": data.priority,
        "status": "Pending",
        "due_date": data.due_date,
        "start_time": data.start_time,
        "duration_minutes": data.duration_minutes,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    return {
        "success": True,
        "task_id": task_ref.id,
        "message": "Task berhasil dibuat"
    }

@router.get("/")
def get_tasks(
    user=Depends(get_current_user)
):
    docs = (
        db.collection("tasks")
        .where("user_id", "==", user["uid"])
        .stream()
    )

    tasks = []

    for doc in docs:
        task = doc.to_dict()

        tasks.append({
            "id": doc.id,
            **task
        })

    return {
        "success": True,
        "data": tasks
    }

@router.get("/{task_id}")
def get_task(
    task_id: str,
    user=Depends(get_current_user)
):
    doc = db.collection("tasks").document(task_id).get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    task = doc.to_dict()

    if task["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    return {
        "success": True,
        "data": {
            "id": doc.id,
            **task
        }
    }

@router.put("/{task_id}")
def update_task(
    task_id: str,
    data: TaskUpdate,
    user=Depends(get_current_user)
):
    ref = db.collection("tasks").document(task_id)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    task = doc.to_dict()

    if task["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    update_data = {
        key: value
        for key, value in data.dict().items()
        if value is not None
    }

    update_data["updated_at"] = firestore.SERVER_TIMESTAMP

    ref.update(update_data)

    return {
        "success": True,
        "message": "Task berhasil diperbarui"
    }

@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    user=Depends(get_current_user)
):
    ref = db.collection("tasks").document(task_id)

    doc = ref.get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    task = doc.to_dict()

    if task["user_id"] != user["uid"]:
        raise HTTPException(
            status_code=403,
            detail="Akses ditolak"
        )

    ref.delete()

    return {
        "success": True,
        "message": "Task berhasil dihapus"
    }