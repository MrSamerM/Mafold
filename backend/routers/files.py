from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
import os
import json
# import ollama
from dotenv import load_dotenv
import models
from database import get_db
from file_converter import get_converter
from openai import OpenAI
import re


load_dotenv()
na_requirements = os.getenv("NA_PATH")

router = APIRouter(tags=["files"])

client = OpenAI(
    api_key=os.getenv("RUNPOD_API_KEY"),
    base_url=os.getenv("RUNPOD_ENDPOINT")
)

class FileInformation(BaseModel):
    uuid: str
    name: str
    path: str


@router.post("/manage-file/")
async def manage_file(
    file: FileInformation,
    db: Session = Depends(get_db)
):
    # """Classify and move a file based on requirements."""
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

    # prompt = f"""
    # You are a **STRICT, DETERMINISTIC** rule-checking classification engine.
    # Your sole job is to evaluate user-written requirements against file data.
    # You **MUST** follow the instructions below exactly.

    # ============================================================
    # FILE DATA (STRICT LITERAL VALUES)
    # - EXTENSION_LITERAL: {ext}
    # - FILENAME_LITERAL: {file_name}

    # CONTENT (Literal text between markers):
    # ---- CONTENT START ----
    # {content}
    # ---- CONTENT END ----

    # ============================================================
    # REQUIREMENTS FORMAT
    # The REQUIREMENTS object is a JSON mapping:
    # folder_id (string) → array of requirement sentences.

    # Example:
    # "4": ["Must have 2 pages"],
    # "5": ["Must be a txt file", "Filename must contain CV"]


    # Each array represents the FULL list of requirements for that folder.
    # A folder qualifies ONLY if **ALL** requirements in its array are satisfied.
    # This is **STRICT AND LOGIC**.

    # ============================================================
    # CRITICAL RULES FOR EVALUATION
    # These rules **MUST** be applied during your internal process and reflected in your reasoning.

    # 1.  **DATA SOURCE CHECK:**
    #     * If a requirement specifies the **FILE NAME** (e.g., "The file name must...") you **MUST ONLY** check the **FILENAME_LITERAL** string. **DO NOT** check the CONTENT.
    #     * If a requirement specifies the **CONTENT** (e.g., "Must contain...") you **MUST ONLY** check the CONTENT text. **DO NOT** check the FILENAME_LITERAL.
        
    # 2.  **LITERAL MATCHING:**
    #     * The file name check **MUST** be a literal, character-for-character substring match. **Do not use auto-correction, semantic substitution, or fuzzy matching.**
        
    # 3.  **FAILURE CONDITION:**
    #     * **DO NOT GUESS**. If unsure, or if the requirement's target data (Name vs. Content) is ambiguously satisfied by another data point, mark the requirement as **FAIL**.

    # ============================================================
    # YOUR INTERNAL PROCESS (MUST BE FOLLOWED)

    # 1.  For each folder_id, check every requirement using the **CRITICAL RULES FOR EVALUATION**.
        
    # 2.  Determine which folders, if any, have **ALL** requirements marked PASS.
        
    # 3.  Apply the final selection logic:
    #     * If multiple folders qualify: Choose the folder with the MOST requirements, or the LOWEST folder\_id if tied.
    #     * If none qualify: result = N/A.

    # ============================================================
    # FINAL ANSWER FORMAT (CRITICAL)
    # Your output must be a single JSON object.

    # The object MUST contain a key:
    # 1.  **"folder_id"**: A string containing the final determined folder ID (e.g., "5") OR the string "N/A".

    # NO extra text. NO preceding or trailing text. OUTPUT ONLY THE JSON OBJECT.

    # ============================================================

    # REQUIREMENTS: {req_map_json}
    # """

    prompt = f"""
    You are a strict, deterministic rule-checking classifier.
    Evaluate file data against folder requirements and return a single JSON object.

    FILE DATA:
    - EXTENSION_LITERAL: {ext}
    - FILENAME_LITERAL: {file_name}
    - CONTENT:
    ---- CONTENT START ----
    {content}
    ---- CONTENT END ----

    REQUIREMENTS FORMAT:
    REQUIREMENTS is a JSON map: folder_id (string) → array of requirement sentences.
    Example:
    "4": ["Must have 2 pages"],
    "5": ["Must be a txt file", "Filename must contain CV"]

    EVALUATION RULES:
    1) If a requirement refers to the FILE NAME, use ONLY FILENAME_LITERAL. Do NOT look at CONTENT.
    2) If a requirement refers to the CONTENT, use ONLY CONTENT. Do NOT look at FILENAME_LITERAL.
    3) For file-name checks, use exact literal substring match. No fuzzy or semantic matching.
    4) Do NOT guess. If you are unsure whether a requirement is satisfied, treat it as FAIL.

    FOLDER SELECTION:
    - A folder qualifies only if ALL of its requirements pass.
    - If multiple folders qualify, choose the one with the MOST requirements.
    - If still tied, choose the one with the LOWEST folder_id.
    - If no folders qualify, the result is "N/A".

    OUTPUT:
    Return ONLY a JSON object:
    {{
    "folder_id": "<winning folder_id or 'N/A'>"
    }}

    REQUIREMENTS: {req_map_json}
    """

    response = client.chat.completions.create(
    model="deepseek-r1:14b",
    messages=[
        {
            "role": "system",
            "content": "You are a file classification system. You output only folder IDs or N/A, nothing else."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0,
    response_format={"type": "json_object"},
    timeout=120
)

    print(prompt)
    # output_string = response['message']['content'].strip()
    output_string = response.choices[0].message.content.strip()
    output_string = re.sub(r'<think>.*?</think>', '', output_string, flags=re.DOTALL).strip()
    output_string = output_string.replace("```json", "").replace("```", "").strip()
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

