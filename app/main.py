from fastapi import FastAPI
from fastapi import Depends

from app.core.dependencies import get_current_user
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.focus import router as focus_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ADHD Planner API",
    version="1.0.0",
    description="Backend API untuk ADHD Smart Daily Planner"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(focus_router)
app.include_router(analytics_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "message": "ADHD Planner API Running"
    }

@app.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "message": "Authorized",
        "user": user
    }