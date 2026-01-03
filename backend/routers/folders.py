from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import schemas
from database import get_db
from crud import folder as folder_crud

router = APIRouter(tags=["folders"])


@router.post("/save-folder/", response_model=schemas.Folder)
def save_folder(
    folder_in: schemas.FolderCreate,
    db: Session = Depends(get_db)
):
    """Create a new folder."""
    return folder_crud.create_folder(db, folder_in)


@router.get("/get-folders/", response_model=List[schemas.Folder])
def get_folders(db: Session = Depends(get_db)):
    """Get all folders."""
    return folder_crud.get_folders(db)


@router.get("/get/{folder_id}", response_model=schemas.Folder)
def get_folder(folder_id: int, db: Session = Depends(get_db)):
    """Get a folder by ID."""
    return folder_crud.get_folder(db, folder_id)


@router.put("/edit/{folder_id}", response_model=schemas.Folder)
def update_folder(
    folder_id: int,
    folder_in: schemas.FolderCreate,
    db: Session = Depends(get_db)
):
    """Update a folder."""
    return folder_crud.update_folder(db, folder_id, folder_in)


@router.delete("/delete/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db)):
    """Delete a folder."""
    return folder_crud.delete_folder(db, folder_id)

