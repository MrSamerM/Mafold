from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List
import models
import schemas


def create_folder(db: Session, folder_in: schemas.FolderCreate) -> models.Folder:
    """Create a new folder with its requirements."""
    # Check if folder_path already exists
    existing_folder = db.query(models.Folder).filter(
        models.Folder.folder_path == folder_in.folder_path
    ).first()
    if existing_folder:
        raise HTTPException(
            status_code=400,
            detail="Folder with this path already exists."
        )

    # Create folder
    db_folder = models.Folder(
        folder_name=folder_in.folder_name,
        folder_path=folder_in.folder_path
    )

    # Add nested requirements if any
    for r in folder_in.requirements:
        db_folder.requirements.append(
            models.Requirement(description=r.description)
        )

    # Save to database
    db.add(db_folder)
    try:
        db.commit()
        db.refresh(db_folder)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return db_folder


def get_folders(db: Session) -> List[models.Folder]:
    """Get all folders."""
    return db.query(models.Folder).all()


def get_folder(db: Session, folder_id: int) -> models.Folder:
    """Get a folder by ID."""
    db_folder = db.query(models.Folder).filter(
        models.Folder.id == folder_id
    ).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return db_folder


def get_folder_by_path(db: Session, folder_path: str) -> models.Folder:
    """Get a folder by path."""
    return db.query(models.Folder).filter(
        models.Folder.folder_path == folder_path
    ).first()


def update_folder(
    db: Session,
    folder_id: int,
    folder_in: schemas.FolderCreate
) -> models.Folder:
    """Update a folder and its requirements."""
    db_folder = db.query(models.Folder).filter(
        models.Folder.id == folder_id
    ).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    db_folder.folder_name = folder_in.folder_name
    db_folder.folder_path = folder_in.folder_path

    db_folder.requirements.clear()
    for r in folder_in.requirements:
        db_folder.requirements.append(
            models.Requirement(description=r.description)
        )

    try:
        db.commit()
        db.refresh(db_folder)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    return db_folder


def delete_folder(db: Session, folder_id: int) -> dict:
    """Delete a folder."""
    db_folder = db.query(models.Folder).filter(
        models.Folder.id == folder_id
    ).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    db.delete(db_folder)
    db.commit()
    return {"message": "Folder deleted successfully"}

