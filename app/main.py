from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.focus import router as focus_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.routes.profile import router as profile_router
from app.core.config import config

def create_app() -> FastAPI:
    app = FastAPI(
        title="ADHD Planner API",
        version="1.0.0",
        redirect_slashes=True
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Menambahkan semua router
    app.include_router(auth_router)
    app.include_router(tasks_router)
    app.include_router(focus_router)
    app.include_router(analytics_router)
    
    # PERUBAHAN DI SINI: Menambahkan prefix="/admin"
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    
    app.include_router(profile_router)

    return app

app = create_app()