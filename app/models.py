from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class School(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str
    curriculum: str
    tuition_range: str
    district: str
    image_url: str
    summary: str


class Offer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(index=True)
    title: str
    offer_type: str
    detail: str
    deadline: str
    source_url: str
    verification_status: str = "Source-verified"
    last_verified_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True


class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    child_age: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
