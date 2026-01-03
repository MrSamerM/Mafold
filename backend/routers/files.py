from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
import os
import json
import ollama
from dotenv import load_dotenv
import models
from database import get_db
from file_converter import get_converter

load_dotenv()
na_requirements = os.getenv("NA_PATH")

router = APIRouter(tags=["files"])


class FileInformation(BaseModel):
    uuid: str
    name: str
    path: str


@router.post("/manage-file/")
async def manage_file(
    file: FileInformation,
    db: Session = Depends(get_db)
):
    """Classify and move a file based on requirements."""
    requirements = db.query(models.Requirement).all()
    req_map = {}
    ids = set()
    for r in requirements:
        if r.folder_id not in req_map:
            req_map[r.folder_id] = []

        req_map[r.folder_id].append(r.description)
        ids.add(r.folder_id)

    full_path = file.path
    file_name = file.name
    converter = get_converter(full_path, file_name)
    content = await converter.convert_to_md()

    req_map_json = json.dumps(
        {str(k): list(v) for k, v in req_map.items()},
        indent=2,
        sort_keys=True
    )
    ext = file_name.split(".")[-1].lower()
    print(content)

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
    Your output must be a single JSON object.

    The object MUST contain two keys:
    1.  **"reasoning"**: An array of strings detailing the step-by-step evaluation of every folder.
    2.  **"folder_id"**: A string containing the final determined folder ID (e.g., "5") OR the string "N/A".

    NO extra text. NO preceding or trailing text. OUTPUT ONLY THE JSON OBJECT.

    ============================================================

    REQUIREMENTS: {req_map_json}
    """

    response = ollama.chat(
        model='mistral',
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
            "format": "json"
        }
    )
    print(prompt)
    output_string = response['message']['content'].strip()
    print(f"Raw output: '{output_string}'")

    try:
        llm_result_dict = json.loads(output_string)
        output = llm_result_dict.get("folder_id", None)

        if output is None:
            raise ValueError("LLM output is missing the 'folder_id' key.")
        if output.upper() == "N/A":
            target_dir = str(Path(na_requirements) / file_name)
            original_path = str(Path(full_path))
            os.replace(original_path, target_dir)
        else:
            folder_id = int(output)
            db_folder = db.query(models.Folder).filter(
                models.Folder.id == folder_id
            ).first()
            if not db_folder:
                raise ValueError(f"No folder found for id {folder_id}")
            target_dir = str(Path(db_folder.folder_path) / file_name)
            original_path = str(Path(full_path))
            os.replace(original_path, target_dir)

        return {"message": "File saved"}

    except json.JSONDecodeError:
        print("Error: LLM output was not valid JSON and could not be parsed.")
        return {"message": "Classification Failed: Invalid LLM Output"}

    except ValueError as e:
        return {"message": f"Classification Failed: {e}"}

