import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.routes import auth, users, listings, tenant, compatibility, interest, chat, notification, admin

logging.basicConfig(level=logging.INFO)

# Creates tables if they don't exist. For production, use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rent & Flatmate Finder API",
    description="Room listings, AI-powered compatibility scoring, real-time chat, and notifications.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tenant.router)
app.include_router(listings.router)
app.include_router(compatibility.router)
app.include_router(interest.router)
app.include_router(chat.router)
app.include_router(notification.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Rent & Flatmate Finder API"}
