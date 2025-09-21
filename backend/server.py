from fastapi import FastAPI, Depends, HTTPException,File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
import os
from sqlalchemy.orm import Session
import models
from file_converter.md_converter import get_converter
import schemas
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError
from typing import List
import pypandoc
from pathlib import Path
from collections import defaultdict
import ollama
import json



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
    # Check if folder_path already exists
    existing_folder = db.query(models.Folder).filter(models.Folder.folder_path == folder_in.folder_path).first()
    if existing_folder:
        raise HTTPException(status_code=400, detail="Folder with this path already exists.")

    # Create folder
    db_folder = models.Folder(
        folder_name=folder_in.folder_name,
        folder_path=folder_in.folder_path
    )

    # Add nested requirements if any
    for r in folder_in.requirements:
        db_folder.requirements.append(models.Requirement(description=r.description))

    # Save to database
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

@app.put("/edit/{folder_id}")
async def update_folder(folder_id: int,folder_in: schemas.FolderCreate,db: Session = Depends(get_db)):
    
    db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    db_folder.folder_name = folder_in.folder_name #replaces old folder name and path with new inputs
    db_folder.folder_path = folder_in.folder_path

    db_folder.requirements.clear() #removes the old requirements and makes a new one
    for r in folder_in.requirements:
        db_folder.requirements.append(models.Requirement(description=r.description))

    try:
        db.commit()
        db.refresh(db_folder)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return db_folder

@app.delete("/delete/{folder_id}")
async def delete_folder(folder_id: int,db: Session = Depends(get_db)):

    db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    db.delete(db_folder)
    db.commit()
    return {"message": "Folder deleted successfully"}

@app.get("/get/{folder_id}",response_model=schemas.Folder)
async def delete_folder(folder_id: int,db: Session = Depends(get_db)):

    db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return db_folder

@app.post("/manage-file/")
async def save_folder(file: UploadFile = File(...), uuid: str = Form(...),db: Session = Depends(get_db)):
    
    requirements = db.query(models.Requirement).all()
    req_map={}
    ids=set()
    for r in requirements:
        if r.folder_id not in req_map:
            req_map[r.folder_id]=[]

        req_map[r.folder_id].append(r.description)
        ids.add(r.folder_id)

    
    converter = get_converter(file) #this gets the class it mataches
    converted = await converter.convert_to_md()#Then run the convert to md method. All the same


    req_map_json = json.dumps(
        {str(k): list(v) for k, v in req_map.items()},
        indent=2,
        sort_keys=True
    )

    prompt = f"""
    You are a strict requirements checker and a context analyzer.

    RULES:
    - A folder qualifies ONLY if **EVERY** requirement listed for that folder_id is satisfied.
    - Ignore letter casing unless specified.
    - Only check the requirements listed for each folder_id. Do not apply requirements from one folder_id to another.
    - If a requirement says “must be a <document>” (CV, letter, etc.), consider it satisfied if the file contains content typical for that type for example:
        - CV: Education, Work Experience, Skills etc.
        - Letter: Greeting, body text, closing etc.
        - Newspaper article: Headline, byline, body etc.
    - If multiple folders qualify, choose the one with the most requirements.
    - If still tied, choose the lowest numeric folder_id.
    - If no folder qualifies, output "N/A".

    INPUT:

    File name: {file.filename}
    --- FILE CONTENT ---
    {converted}
    --- END FILE CONTENT ---

    --- REQUIREMENTS (JSON) ---
    {req_map_json}
    --- END REQUIREMENTS ---

    OUTPUT:
    - Respond with **only** the folder_id of the qualifying folder, or "N/A" if none qualify.
    """

    response = ollama.generate(
            # model='llama3.2:3b',
            model='mistral:7b-instruct',
            prompt=prompt,
            options={"temperature": 0}
        )

    print(response["response"])
    output=response["response"].strip()

    if output.upper() =="N/A":
        target_dir = Path('C:/Users/Samer/OneDrive - Brunel University London/Desktop/Flop')
    else:
        folder_id = int(output)
        db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
        if not db_folder:
            raise ValueError(f"No folder found for id {folder_id}")
        target_dir = Path(db_folder.folder_path)

    target_dir.mkdir(parents=True, exist_ok=True)
    dest_path = target_dir / f"{file.filename}"

    file.file.seek(0)
    raw_bytes = await file.read()
    with dest_path.open("wb") as f:
        f.write(raw_bytes)


    return {"message": "File saved"}

# uvicorn server:app --reload  to run fastAPI