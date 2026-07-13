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

    # Pastikan user["uid"] tersedia
    user_id = user.get("uid")
    
    task_ref.set({
        "user_id": user_id,
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
<<<<<<< HEAD
def get_tasks(
    user=Depends(get_current_user)
):
    # --- DEBUGGER ---
    user_id = user.get("uid")
    print(f"DEBUG: Mencari task untuk user_id: {user_id}")
    # ----------------
    
    docs = (
        db.collection("tasks")
        .where("user_id", "==", user_id)
        .stream()
    )
=======
def get_tasks(user=Depends(get_current_user)):
    user_id = user.get("uid")
    
    # Ambil dokumen dari Firebase
    docs = db.collection("tasks").where("user_id", "==", user_id).stream()
>>>>>>> d0112576577fb8c67e8fd78705ac51e270b83c99

    tasks = []
    for doc in docs:
<<<<<<< HEAD
        task = doc.to_dict()
        tasks.append({
            "id": doc.id,
            **task
        })
=======
        task_data = doc.to_dict()
        if task_data:
            # Membuat dictionary baru yang menggabungkan ID dan isi data
            combined = {"id": doc.id}
            combined.update(task_data)
            tasks.append(combined)
>>>>>>> d0112576577fb8c67e8fd78705ac51e270b83c99

    # --- DEBUGGER ---
    print(f"DEBUG: Jumlah task ditemukan: {len(tasks)}")
    # ----------------

    return {
        "success": True,
        "data": tasks
    }

@router.get("/")
def get_tasks(user=Depends(get_current_user)):
    user_id = user.get("uid")
    
    # Ambil dokumen
    docs = db.collection("tasks").where("user_id", "==", user_id).stream()

    tasks = []
    for doc in docs:
        task_data = doc.to_dict()
        if task_data:  # Pastikan task_data tidak None
            # Gabungkan id dan data task
            combined = {"id": doc.id}
            combined.update(task_data)
            tasks.append(combined)

    return {
        "success": True,
        "data": tasks
    }
<<<<<<< HEAD

=======
@router.get("/{task_id}")
def get_task(
    task_id: str,
    user=Depends(get_current_user)
):
>>>>>>> d0112576577fb8c67e8fd78705ac51e270b83c99
    doc = db.collection("tasks").document(task_id).get()

    if not doc.exists:
        raise HTTPException(
            status_code=404,
            detail="Task tidak ditemukan"
        )

    task = doc.to_dict()

    if task["user_id"] != user.get("uid"):
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
        raise HTTPException(status_code=404, detail="Task tidak ditemukan")

    task = doc.to_dict()
    if task["user_id"] != user.get("uid"):
        raise HTTPException(status_code=403, detail="Akses ditolak")

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    update_data["updated_at"] = firestore.SERVER_TIMESTAMP

    ref.update(update_data)
    return {"success": True, "message": "Task berhasil diperbarui"}

@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    user=Depends(get_current_user)
):
    ref = db.collection("tasks").document(task_id)
    doc = ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Task tidak ditemukan")

    task = doc.to_dict()
    if task["user_id"] != user.get("uid"):
        raise HTTPException(status_code=403, detail="Akses ditolak")

    ref.delete()
<<<<<<< HEAD
    return {"success": True, "message": "Task berhasil dihapus"}
=======

    return {
        "success": True,
        "message": "Task berhasil dihapus"
    }
>>>>>>> d0112576577fb8c67e8fd78705ac51e270b83c99
