import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import Base, engine

from routers import (
    auth,
    users,
    companies,
    experiences,
    questions,
    roadmaps,
    interactions,
    notifications,
    admin,
)

# ----------------------------------------------------
# Create Database Tables
# ----------------------------------------------------
Base.metadata.create_all(bind=engine)

# ----------------------------------------------------
# FastAPI App
# ----------------------------------------------------
app = FastAPI(
    title="CampusConnect API",
    version="1.0.0",
    description="Backend API for CampusConnect"
)

# ----------------------------------------------------
# CORS
# ----------------------------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
extra_origins = os.getenv("FRONTEND_URL")
if extra_origins and extra_origins not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(extra_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# API Routers
# ----------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(experiences.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(roadmaps.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# ----------------------------------------------------
# Uploads Folder
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

# ----------------------------------------------------
# Frontend Folder
# ----------------------------------------------------
FRONTEND_DIR = os.path.join(
    os.path.dirname(BASE_DIR),
    "frontend"
)

if os.path.exists(FRONTEND_DIR):

    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    images_dir = os.path.join(FRONTEND_DIR, "images")

    if os.path.exists(css_dir):
        app.mount(
            "/css",
            StaticFiles(directory=css_dir),
            name="css"
        )

    if os.path.exists(js_dir):
        app.mount(
            "/js",
            StaticFiles(directory=js_dir),
            name="js"
        )

    if os.path.exists(images_dir):
        app.mount(
            "/images",
            StaticFiles(directory=images_dir),
            name="images"
        )

    @app.get("/")
    async def home():
        return FileResponse(
            os.path.join(FRONTEND_DIR, "index.html")
        )

    @app.get("/{page}.html")
    async def pages(page: str):
        page_path = os.path.join(
            FRONTEND_DIR,
            f"{page}.html"
        )

        if os.path.exists(page_path):
            return FileResponse(page_path)

        return FileResponse(
            os.path.join(FRONTEND_DIR, "index.html")
        )

else:

    @app.get("/")
    async def home():
        return {
            "status": "success",
            "message": "CampusConnect Backend Running Successfully"
        }

# ----------------------------------------------------
# Health Check
# ----------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "OK",
        "message": "CampusConnect API is running"
    }