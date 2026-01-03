from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String, index=True)
    folder_path = Column(String, index=True)

    requirements = relationship(
        "Requirement",
        back_populates="folder",
        cascade="all, delete-orphan"
    )

