from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
import models
from file_converter.md_converter import get_converter
import schemas
from database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError
from typing import List
from pathlib import Path
import ollama
import json
from dotenv import load_dotenv
from pydantic import BaseModel
import json

load_dotenv()
na_requirements = os.getenv("NA_PATH")

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


class FileInformation(BaseModel):
    uuid: str
    name: str
    path: str

@app.post("/manage-file/")
async def save_folder(file: FileInformation, db: Session = Depends(get_db)):

    requirements = db.query(models.Requirement).all()
    req_map={}
    ids=set()
    for r in requirements:
        if r.folder_id not in req_map:
            req_map[r.folder_id]=[]

        req_map[r.folder_id].append(r.description)
        ids.add(r.folder_id)

    full_path=file.path
    file_name=file.name
    converter = get_converter(full_path,file_name) #this gets the class it mataches
    content = await converter.convert_to_md()#Then run the convert to md method. All the same


    req_map_json = json.dumps(
        {str(k): list(v) for k, v in req_map.items()},
        indent=2,
        sort_keys=True
    )
    ext = file_name.split(".")[-1].lower() #the last of the split
    print(content)
    # prompt = f"""
    # You are a strict requirements checker and a context analyzer.

    # RULES:
    # - A folder qualifies ONLY if **EVERY** requirement listed for that folder_id is satisfied.
    # - Ignore letter casing unless specified.
    # - Only check the requirements listed for each folder_id. Do not apply requirements from one folder_id to another.
    # - If a requirement says “must be a <document>” (CV, letter, etc.), consider it satisfied if the file contains content typical for that type for example:
    #     - CV: Education, Work Experience, Skills etc.
    #     - Letter: Greeting, body text, closing etc.
    #     - Newspaper article: Headline, byline, body etc.
    # - If requirment is about page numbers, you can see the content in each page number written something like this ---Page 1---
    # - If multiple folders qualify, choose the one with the most requirements.
    # - If still tied, choose the lowest numeric folder_id.
    # - If no folder qualifies, output "N/A".

    # INPUT:
    # --- FILE DETAILS ---

    # File extension: .{ext}
    # File name: {file_name}
    # --- END FILE DETAILS ---
 

    # --- FILE CONTENT ---
    # {converted}
    # --- END FILE CONTENT ---

    # --- REQUIREMENTS (JSON) ---
    # {req_map_json}
    # --- END REQUIREMENTS ---

    # OUTPUT:
    # - Respond exactly with the folder_id of the qualifying folder as a raw number (no quotes, no formatting).
    # - If no folder qualifies, respond exactly with N/A (no quotes).    
    # - Do **not** provide any explanations, reasoning, or extra text.  
    # - Example valid output: 1
    # - Example valid output: N/A
    # """

    # print(prompt)
    # response = ollama.generate(
    #         # model='llama3.2:3b',
    #         model='mistral:7b-instruct',
    #         prompt=prompt,
    #         options={"temperature": 0}
    #     )

    # prompt = f"""


    # You are a deterministic file classifier.

    # Before giving the final answer, you MUST internally:
    # 1. Evaluate each requirement EXACTLY as written.
    # 2. Create a hidden checklist for EACH folder_id.
    # 3. Mark EACH requirement as PASS or FAIL.
    # 4. Only folders with ALL PASS qualify.

    # You MUST still output ONLY the final number or N/A at the end with no explanations.

    # -----

    # FILE:
    # - Extension: .{ext}
    # - Name: {file_name}

    # CONTENT:
    # {converted}

    # -----

    # REQUIREMENTS:
    # {req_map_json}


    # RULES:
    # - ALL requirements must be satisfied (logical AND)
    # - Ignore case
    # - Page numbers appear as ---Page N---
    # - If multiple qualify: choose the one with the MOST requirements, then LOWEST folder_id
    # - If none qualify: output N/A

    # FINAL ANSWER FORMAT:
    # Output ONLY the folder_id number (e.g., 5) or N/A.

    # THINK CLEARLY AND DO NOT GUESS.
    # """


    prompt = f"""
    You are a **STRICT, DETERMINISTIC** rule-checking classification engine.
    Your sole job is to evaluate user-written requirements against file data.
    You **MUST** follow the instructions below exactly.

    ============================================================
    FILE DATA (STRICT LITERAL VALUES)
    - EXTENSION_LITERAL: {ext}
    - FILENAME_LITERAL: {file_name}

    CONTENT (Literal text between markers):
    ---- CONTENT START ----
    {content}
    ---- CONTENT END ----

    ============================================================
    REQUIREMENTS FORMAT
    The REQUIREMENTS object is a JSON mapping:
    folder_id (string) → array of requirement sentences.

    Example:
    "3": ["Must contain Baba"],
    "4": ["Must have 2 pages"],
    "5": ["Must be a txt file", "Filename must contain CV"]


    Each array represents the FULL list of requirements for that folder.
    A folder qualifies ONLY if **ALL** requirements in its array are satisfied.
    This is **STRICT AND LOGIC**.

    ============================================================
    CRITICAL RULES FOR EVALUATION
    These rules **MUST** be applied during your internal process and reflected in your reasoning.

    1.  **DATA SOURCE CHECK:**
        * If a requirement specifies the **FILE NAME** (e.g., "The file name must...") you **MUST ONLY** check the **FILENAME_LITERAL** string. **DO NOT** check the CONTENT.
        * If a requirement specifies the **CONTENT** (e.g., "Must contain...") you **MUST ONLY** check the CONTENT text. **DO NOT** check the FILENAME_LITERAL.
        
    2.  **LITERAL MATCHING:**
        * The file name check **MUST** be a literal, character-for-character substring match. **Do not use auto-correction, semantic substitution, or fuzzy matching.**
        
    3.  **FAILURE CONDITION:**
        * **DO NOT GUESS**. If unsure, or if the requirement's target data (Name vs. Content) is ambiguously satisfied by another data point, mark the requirement as **FAIL**.

    ============================================================
    YOUR INTERNAL PROCESS (MUST BE FOLLOWED)

    1.  For each folder_id, check every requirement using the **CRITICAL RULES FOR EVALUATION**.
    2.  Determine which folders, if any, have **ALL** requirements marked PASS.
    3.  Apply the final selection logic:
        * If multiple folders qualify: Choose the folder with the MOST requirements, or the LOWEST folder\_id if tied.
        * If none qualify: result = N/A.

    ============================================================
    FINAL ANSWER FORMAT (CRITICAL)
    Output **ONLY** a single JSON object containing your step-by-step reasoning and the final result.

    If a folder qualifies, the format must be:
    ```json
    {{
    "reasoning": [
        "Evaluated Folder [ID_A]: All requirements passed.",
        "Evaluated Folder [ID_B]: Requirement '...' failed because [reason].",
        "Final Logic: Folder [ID_A] was the only folder to qualify OR was chosen based on tie-breaker rules."
    ],
    "folder_id": "[ID_A]"
    }}
    If the result is N/A, the format must be:

    JSON

    {{
    "reasoning": [
        "Evaluated Folder [ID_A]: All requirements failed.",
        "Evaluated Folder [ID_B]: All requirements failed.",
        "Final Logic: No folders qualified."
    ],
    "folder_id": "N/A"
    }}
    NO extra text. NO preceding or trailing text. OUTPUT ONLY THE JSON OBJECT.

    ============================================================

    REQUIREMENTS: {req_map_json} """

    response = ollama.chat(
        model='llama3:8b',
        messages=[
            {
                'role': 'system',
                'content': 'You are a file classification system. You output only folder IDs or N/A, nothing else.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        options={
            "temperature": 0,
            # "num_predict": 10  # Limit output length
        }
    )
    print(prompt)
    output_string = response['message']['content'].strip()
    print(f"Raw output: '{output_string}'")

    llm_result_dict = json.loads(output_string)
    output = llm_result_dict.get("folder_id", None)

    try:

        if output is None:
            raise ValueError("LLM output is missing the 'folder_id' key.")
        if output.upper() =="N/A":
            target_dir = str(Path(na_requirements)/file_name)
            original_path = str(Path(full_path))
            os.replace(original_path,target_dir)
        else:
            folder_id = int(output)
            db_folder = db.query(models.Folder).filter(models.Folder.id == folder_id).first()
            if not db_folder:
                raise ValueError(f"No folder found for id {folder_id}")
            target_dir = str(Path(db_folder.folder_path)/file_name)
            original_path = str(Path(full_path))
            os.replace(original_path,target_dir)

        return {"message": "File saved"}

    except json.JSONDecodeError:
        # Handle cases where the LLM output was malformed (e.g., truncated)
        print("Error: LLM output was not valid JSON and could not be parsed.")
        return {"message": "Classification Failed: Invalid LLM Output"}
        
    except ValueError as e:
        # Handles errors raised in the 'if not db_folder' block
        return {"message": f"Classification Failed: {e}"}

# uvicorn server:app --reload  to run fastAPI