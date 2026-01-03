from pydantic import BaseModel
from typing import List
from .requirement import RequirementCreate, Requirement


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

