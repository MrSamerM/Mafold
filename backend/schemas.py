from pydantic import BaseModel
from typing import List #to show the type that is expected


# --- Requirement ---
class RequirementCreate(BaseModel): #input
    description: str

class Requirement(BaseModel): #output
    id: int
    description: str

    class Config:
        orm_mode = True

# --- Folder ---
class FolderCreate(BaseModel):
    folder_name: str
    folder_path: str
    requirements: List[RequirementCreate] = []


class Folder(BaseModel):
    id: int
    folder_name: str
    folder_path: str
    requirements: List[Requirement] = []

    class Config:
        orm_mode = True
