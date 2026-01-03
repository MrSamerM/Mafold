from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import models
from database import engine
from routers import folders, files

load_dotenv()

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(folders.router)
app.include_router(files.router)

# uvicorn server:app --reload  to run fastAPI
