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
    # Extended fields
    accreditation: str = ""
    language_of_instruction: str = ""
    age_range: str = ""
    website_url: str = ""
    founded_year: str = ""
    total_students: str = ""
    class_size_max: str = ""
    address: str = ""
    facilities: str = ""   # pipe-separated
    pros: str = ""         # pipe-separated
    cons: str = ""         # pipe-separated
    university_pathways: str = ""
    admissions_timeline: str = ""  # pipe-separated "Month: event"
    required_documents: str = ""   # pipe-separated
    faq_questions: str = ""        # pipe-separated
    faq_answers: str = ""          # pipe-separated
    last_updated: datetime = Field(default_factory=datetime.utcnow)


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
