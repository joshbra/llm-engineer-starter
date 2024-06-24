from langchain_core.pydantic_v1 import BaseModel, Field

from typing import List, Optional

class MedicalEvent(BaseModel):
    date: str = Field(description="Date of a medical procedure or notes")
    details: str = Field(description="Relevant details about the medical procedure. Leave an empty string if none")
    keywords: Optional[List[str]] = Field(description="Keywords used, only choose a few important keywords")

class MedicalRecord(BaseModel):
    events: list[MedicalEvent] = Field(description="A list of medical events that pertain to a patient")
