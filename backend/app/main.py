from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.database.models import Base
from .infrastructure.database.database import engine
from .application.routers import auth, polls, users

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voting System API",
    description="A FastAPI-based voting system with user authentication and real-time results",
    version="1.0.0",
    root_path="",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]  # Expose all headers
)

# Include routers
app.include_router(auth.router)  # Removed prefix since it's defined in the router
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(polls.router, prefix="/polls", tags=["polls"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Voting System API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
