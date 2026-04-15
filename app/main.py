from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_db, close_db
from app.middleware.logger import LoggerMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="My Backend API",
    description="Reusable FastAPI + MongoDB backend",
    version="1.0.0",
    lifespan=lifespan,
    # Disable docs in production
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS — restrict to your actual domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Request logger
app.add_middleware(LoggerMiddleware)

# Routers
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
