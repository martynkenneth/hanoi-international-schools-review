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
    accreditation: str = ""
    language_of_instruction: str = ""
    age_range: str = ""
    website_url: str = ""
    founded_year: str = ""
    total_students: str = ""
    class_size_max: str = ""
    address: str = ""
    facilities: str = ""
    pros: str = ""
    cons: str = ""
    university_pathways: str = ""
    admissions_timeline: str = ""
    required_documents: str = ""
    faq_questions: str = ""
    faq_answers: str = ""
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


class PendingOffer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(index=True)
    title: str
    raw_text: str
    source_url: str
    offer_type: str = "Unknown"
    confidence: float = 0.0
    detail: str = ""
    deadline: str = ""
    status: str = "pending"   # pending | approved | rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
