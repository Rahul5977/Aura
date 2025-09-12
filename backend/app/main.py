from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.sessions import connect_database, disconnect_database
from .api import auth, conversation
from .core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    This function handles startup and shutdown events for the application.
    It connects to the database on startup and disconnects on shutdown.
    """
    # Startup
    await connect_database()
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} started")
    yield
    # Shutdown
    await disconnect_database()
    print("🛑 Application shutdown")


# Create FastAPI application with lifespan events
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A modern ML platform with user authentication and conversation management",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(conversation.router, prefix="/api")


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Aura ML Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/protected")
def protected_route(current_user: dict = Depends(auth.get_current_user)):
    """
    Example protected route.
    
    This endpoint requires a valid JWT token in the Authorization header.
    It demonstrates how to protect routes using the get_current_user dependency.
    """
    return {
        "message": f"Hello {current_user.email}!",
        "user_id": current_user.id,
        "access_granted": True
    }