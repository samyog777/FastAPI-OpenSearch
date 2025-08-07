from pydantic import BaseModel
from typing import Optional

class SaveResult(BaseModel):
    total_fetched: int
    total_saved: int

class UniversityCreate(BaseModel):
    web_pages: list[str]
    state_province: Optional[str] = None
    name: str
    domains: list[str]
    country: str
    alpha_two_code: str

class UniversityUpdate(BaseModel):
    web_pages: Optional[list[str]] = None
    state_province: Optional[str] = None
    name: Optional[str] = None
    domains: Optional[list[str]] = None
    country: Optional[str] = None
    alpha_two_code: Optional[str] = None
    

class University(UniversityCreate):
    id: str

    class Config:
        from_attributes = True
