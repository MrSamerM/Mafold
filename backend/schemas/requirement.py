from pydantic import BaseModel


class RequirementCreate(BaseModel):  # input
    description: str


class Requirement(BaseModel):  # output
    id: int
    description: str

    class Config:
        orm_mode = True

