from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import (
    ErrorResponse,
    SubjectCreate,
    SubjectResponse,
    AssessmentCreate,
    AssessmentResponse,
    ScoreCreate,
    ScoreUpdate,
    ScoreResponse,
    StudentResultSummary,
)
from app.auth import authenticate_credentials
from app.services import academic_service

app = FastAPI(
    title="Student Academic & Assessment Management API",
    description="""
A robust, secure RESTful API built with FastAPI for managing subjects, assessments, and student scores.
Features:
- **Pydantic Validation**: Strong request data models and types.
- **Basic Authentication**: Secures write/admin routes.
- **Clean REST Patterns & Predictable Status Codes**: 200, 201, 400, 401, 404, 422.
- **Deep Service Architecture**: Clean separation between HTTP routing and academic business logic.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ---------------- Custom Exception Handlers ----------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = f"Validation error at '{'.'.join(str(loc) for loc in first_error.get('loc', []))}': {first_error.get('msg', 'Invalid input')}"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": {"code": "VALIDATION_FAILED", "message": msg, "details": errors}},
    )


# ---------------- Health & Meta Endpoints ----------------
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Student Academic & Assessment Management API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ---------------- Subject Endpoints ----------------
@app.post(
    "/subjects",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Subjects"],
    summary="Create a new Subject",
    responses={
        400: {"model": ErrorResponse, "description": "Subject already exists"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Validation failure"},
    }
)
def create_subject(
    payload: SubjectCreate,
    username: str = Depends(authenticate_credentials)
):
    try:
        return academic_service.create_subject(
            subject_id=payload.id,
            name=payload.name,
            credit_units=payload.credit_units
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SUBJECT_EXISTS", "message": str(e)}
        )


@app.get(
    "/subjects",
    response_model=List[SubjectResponse],
    tags=["Subjects"],
    summary="List all Subjects"
)
def list_subjects():
    return academic_service.list_subjects()


# ---------------- Assessment Endpoints ----------------
@app.post(
    "/assessments",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Assessments"],
    summary="Create a new Assessment",
    responses={
        400: {"model": ErrorResponse, "description": "Duplicate ID"},
        404: {"model": ErrorResponse, "description": "Subject not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def create_assessment(
    payload: AssessmentCreate,
    username: str = Depends(authenticate_credentials)
):
    try:
        return academic_service.create_assessment(
            assessment_id=payload.id,
            subject_id=payload.subject_id,
            title=payload.title,
            max_score=payload.max_score,
            weight_percentage=payload.weight_percentage
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SUBJECT_NOT_FOUND", "message": str(e)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ASSESSMENT_EXISTS", "message": str(e)}
        )


@app.get(
    "/assessments",
    response_model=List[AssessmentResponse],
    tags=["Assessments"],
    summary="List all Assessments"
)
def list_assessments():
    return academic_service.list_assessments()


# ---------------- Score Endpoints ----------------
@app.post(
    "/scores",
    response_model=ScoreResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Scores"],
    summary="Record a student score",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid score value or duplicate"},
        404: {"model": ErrorResponse, "description": "Assessment not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def record_score(
    payload: ScoreCreate,
    username: str = Depends(authenticate_credentials)
):
    try:
        return academic_service.record_score(
            student_id=payload.student_id,
            assessment_id=payload.assessment_id,
            obtained_score=payload.obtained_score
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ASSESSMENT_NOT_FOUND", "message": str(e)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SCORE", "message": str(e)}
        )


@app.put(
    "/scores/{score_id}",
    response_model=ScoreResponse,
    tags=["Scores"],
    summary="Update a recorded score",
    responses={
        400: {"model": ErrorResponse, "description": "Score exceeds maximum allowed"},
        404: {"model": ErrorResponse, "description": "Score record not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
def update_score(
    score_id: str,
    payload: ScoreUpdate,
    username: str = Depends(authenticate_credentials)
):
    try:
        return academic_service.update_score(
            score_id=score_id,
            new_obtained_score=payload.obtained_score
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SCORE_NOT_FOUND", "message": str(e)}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_SCORE", "message": str(e)}
        )


# ---------------- Student Results & Analytics Endpoints ----------------
@app.get(
    "/students/{student_id}/results",
    response_model=StudentResultSummary,
    tags=["Results & Analytics"],
    summary="Retrieve results and overall average for a specific student",
    responses={
        404: {"model": ErrorResponse, "description": "Student results not found"}
    }
)
def get_student_results(student_id: str):
    clean_id = student_id.strip().upper()
    try:
        return academic_service.get_student_results(student_id=clean_id)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "STUDENT_NOT_FOUND", "message": str(e)}
        )


@app.get(
    "/subjects/{subject_id}/average",
    tags=["Results & Analytics"],
    summary="Calculate average performance across all assessments in a subject",
    responses={
        404: {"model": ErrorResponse, "description": "Subject not found"}
    }
)
def get_subject_average(subject_id: str):
    clean_id = subject_id.strip().upper()
    try:
        return academic_service.calculate_subject_average(subject_id=clean_id)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SUBJECT_NOT_FOUND", "message": str(e)}
        )
