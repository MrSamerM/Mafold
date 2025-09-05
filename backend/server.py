from fastapi import FastAPI, Depends, HTTPException,Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
import os
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError
from typing import List


load_dotenv()
app = FastAPI()

models.Base.metadata.create_all(bind=engine) #creates the database tables

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal() #creates a new database session to interact with database. Which is used as a dependency in fastAPI
    try:
        yield db #here yield make get_db a generator function
    finally:
        db.close() #after all is done, then it closes the db

@app.get("/pick-folder")
@app.get("/pick-folder")
def pick_folder():
    root = tk.Tk()
    root.withdraw()  # hide main window
    root.attributes('-topmost', True)
    folder_selected = filedialog.askdirectory() 
    root.destroy()
    if folder_selected:
        folder_name = os.path.basename(folder_selected)
        return {"folderName": folder_name, "folderPath": folder_selected}
    
    return {"folderName": None, "folderPath": None}



# Schemas vs Models

# Models (models.Folder)
# These represent the actual database tables.
# SQLAlchemy uses them to create queries and save data.
# They know how to talk to the database, handle relationships, etc.

# Schemas (schemas.FolderCreate)
# These are Pydantic models.
# They are used for data validation and serialization:
# Input from the user (request body)
# Output to the client (response)
# Schemas don’t know anything about the database.

#response_model=schemas.Folder
#basically this is used as a restriction to what the client is able to see. 
#So here the id could be part of the response, but only send what you need to send

#db: Session = Depends(get_db)
#Session is a type hint to inform you that db is sqlAlchamy db session
#Depends(get_db) This is FastAPI’s way of saying “give me whatever get_db() provides

#folder_in: schemas.FolderCreate
#This basically means, I am expecting the request body to have whatever the schema specifies

@app.post("/save-folder/", response_model=schemas.Folder)
def save_folder(folder_in: schemas.FolderCreate, db: Session = Depends(get_db)):
    # 1️⃣ Check if folder_path already exists
    existing_folder = db.query(models.Folder).filter(models.Folder.folder_path == folder_in.folder_path).first()
    if existing_folder:
        raise HTTPException(status_code=400, detail="Folder with this path already exists.")

    # 2️⃣ Create folder
    db_folder = models.Folder(
        folder_name=folder_in.folder_name,
        folder_path=folder_in.folder_path
    )

    # 3️⃣ Add nested requirements if any
    for r in folder_in.requirements:
        db_folder.requirements.append(models.Requirement(description=r.description))

    # 4️⃣ Save to database
    db.add(db_folder)
    try:
        db.commit()
        db.refresh(db_folder)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return db_folder

#the List[] is used to show that the response is responding with multiple objects
@app.get("/get-folders/", response_model=List[schemas.Folder])
def get_folders(db: Session = Depends(get_db)):
    folders = db.query(models.Folder).all()
    return folders
    

# uvicorn server:app --reload  to run fastAPI