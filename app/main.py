import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Import semua router
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.focus import router as focus_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.routes.profile import router as profile_router
<<<<<<< HEAD
from app.routes.scanner import router as scanner_router
from app.routes.voice import router as voice_router       # ← TAMBAH INI
from app.core.config import config


=======
from app.routes.scanner import router as scanner_router  
from app.core.config import config

>>>>>>> 010946aad6a51edf876a012f199cfe201c0f1bb0
def create_app() -> FastAPI:
    app = FastAPI(
        title="ADHD Planner API",
        version="1.0.0",
        redirect_slashes=True
    )

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root endpoint untuk redirect ke dokumentasi
    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse(url="/docs")

    app.include_router(auth_router)
    app.include_router(tasks_router)
    app.include_router(focus_router)
    app.include_router(analytics_router)
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    app.include_router(profile_router)
    app.include_router(scanner_router)
    app.include_router(voice_router)                      # ← TAMBAH INI

    return app


app = create_app()