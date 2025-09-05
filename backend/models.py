from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String, index=True)
    folder_path = Column(String, index=True)

    # One-to-many: a folder has many requirements
    requirements = relationship("Requirement", back_populates="folder")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id"))

    # Many-to-one: a requirement belongs to one folder
    folder = relationship("Folder", back_populates="requirements")
