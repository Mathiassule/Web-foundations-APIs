from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable description of the error")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class SubjectCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=10, description="Unique subject code, e.g. MTH101")
    name: str = Field(..., min_length=3, max_length=100, description="Subject title, e.g. Mathematics")
    credit_units: int = Field(default=3, ge=1, le=6, description="Credit units (1 to 6)")

    @field_validator("id")
    @classmethod
    def id_alphanumeric(cls, v: str) -> str:
        clean = v.strip().upper()
        if not clean.isalnum():
            raise ValueError("Subject ID must be alphanumeric without spaces")
        return clean


class SubjectResponse(BaseModel):
    id: str
    name: str
    credit_units: int


class AssessmentCreate(BaseModel):
    id: str = Field(..., min_length=2, max_length=20, description="Unique assessment code, e.g. QUIZ1, MIDTERM")
    subject_id: str = Field(..., description="Subject code the assessment belongs to")
    title: str = Field(..., min_length=3, max_length=100, description="Assessment name")
    max_score: float = Field(..., gt=0.0, le=100.0, description="Maximum attainable score (0-100)")
    weight_percentage: float = Field(..., gt=0.0, le=100.0, description="Weight towards final grade (0-100%)")

    @field_validator("id", "subject_id")
    @classmethod
    def clean_id(cls, v: str) -> str:
        return v.strip().upper()


class AssessmentResponse(BaseModel):
    id: str
    subject_id: str
    title: str
    max_score: float
    weight_percentage: float


class ScoreCreate(BaseModel):
    student_id: str = Field(..., min_length=3, max_length=20, description="Student matriculation or admission number")
    assessment_id: str = Field(..., description="Assessment identifier")
    obtained_score: float = Field(..., ge=0.0, description="Score attained by student")

    @field_validator("student_id", "assessment_id")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        return v.strip().upper()


class ScoreUpdate(BaseModel):
    obtained_score: float = Field(..., ge=0.0, description="Updated score attained by student")


class ScoreResponse(BaseModel):
    id: str
    student_id: str
    assessment_id: str
    subject_id: str
    obtained_score: float
    max_score: float
    percentage: float
    grade: str


class StudentResultSummary(BaseModel):
    student_id: str
    total_assessments: int
    overall_average: float
    scores: List[ScoreResponse]
