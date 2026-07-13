import os
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies import get_current_user
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.focus import router as focus_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.routes.profile import router as profile_router

def create_app() -> FastAPI:
    # PERBAIKAN 1: Menambahkan redirect_slashes=False untuk mencegah error CORS 307
    app = FastAPI(
        title="ADHD Planner API",
        version="1.0.0",
        description="Backend API untuk ADHD Smart Daily Planner",
        redirect_slashes=False,
    )

    BASE_DIR = os.path.dirname(__file__)
    MEDIA_DIR = os.path.join(BASE_DIR, "media")
    os.makedirs(os.path.join(MEDIA_DIR, "profile_photos"), exist_ok=True)

    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    # PERBAIKAN 2: Penanganan variable lingkungan yang lebih aman
    default_origins = ["http://localhost:5173"]
    extra_origins = os.getenv("ALLOWED_ORIGINS", "")
    origins = default_origins
    if extra_origins:
        origins += [origin.strip() for origin in extra_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(tasks_router)
    app.include_router(focus_router)
    app.include_router(analytics_router)
    app.include_router(admin_router)
    app.include_router(profile_router)

    @app.get("/")
    def root():
        return {"message": "ADHD Planner API Running"}

    @app.get("/me")
    def me(user=Depends(get_current_user)):
        return {"message": "Authorized", "user": user}

    return app

app = create_app()
