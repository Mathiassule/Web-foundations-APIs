from typing import Dict, List, Optional
import uuid


def calculate_grade(percentage: float) -> str:
    """Helper to convert standard percentage into academic letter grades."""
    if percentage >= 90.0:
        return "A"
    elif percentage >= 80.0:
        return "B"
    elif percentage >= 70.0:
        return "C"
    elif percentage >= 60.0:
        return "D"
    return "F"


class AcademicService:
    """
    Deep Module for academic operations.
    Hides storage data structures, ID generation, integrity constraints,
    grade scoring logic, and average computations behind concise domain methods.
    """

    def __init__(self):
        # In-memory storage structures
        self._subjects: Dict[str, dict] = {}
        self._assessments: Dict[str, dict] = {}
        self._scores: Dict[str, dict] = {}  # key: score_id

    # ---------------- Subject Methods ----------------
    def create_subject(self, subject_id: str, name: str, credit_units: int) -> dict:
        if subject_id in self._subjects:
            raise ValueError(f"Subject '{subject_id}' already exists")
        record = {
            "id": subject_id,
            "name": name,
            "credit_units": credit_units
        }
        self._subjects[subject_id] = record
        return record

    def list_subjects(self) -> List[dict]:
        return list(self._subjects.values())

    def get_subject(self, subject_id: str) -> Optional[dict]:
        return self._subjects.get(subject_id)

    # ---------------- Assessment Methods ----------------
    def create_assessment(self, assessment_id: str, subject_id: str, title: str, max_score: float, weight_percentage: float) -> dict:
        if assessment_id in self._assessments:
            raise ValueError(f"Assessment '{assessment_id}' already exists")
        if subject_id not in self._subjects:
            raise LookupError(f"Subject '{subject_id}' does not exist")

        record = {
            "id": assessment_id,
            "subject_id": subject_id,
            "title": title,
            "max_score": max_score,
            "weight_percentage": weight_percentage
        }
        self._assessments[assessment_id] = record
        return record

    def list_assessments(self) -> List[dict]:
        return list(self._assessments.values())

    def get_assessment(self, assessment_id: str) -> Optional[dict]:
        return self._assessments.get(assessment_id)

    # ---------------- Score Methods ----------------
    def record_score(self, student_id: str, assessment_id: str, obtained_score: float) -> dict:
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            raise LookupError(f"Assessment '{assessment_id}' does not exist")

        if obtained_score > assessment["max_score"]:
            raise ValueError(
                f"Obtained score ({obtained_score}) cannot exceed maximum allowed ({assessment['max_score']})"
            )

        # Check for duplicate score entry for this student and assessment
        for score in self._scores.values():
            if score["student_id"] == student_id and score["assessment_id"] == assessment_id:
                raise ValueError(f"Score already recorded for student '{student_id}' on assessment '{assessment_id}'")

        score_id = str(uuid.uuid4())[:8].upper()
        percentage = round((obtained_score / assessment["max_score"]) * 100, 2)
        grade = calculate_grade(percentage)

        record = {
            "id": score_id,
            "student_id": student_id,
            "assessment_id": assessment_id,
            "subject_id": assessment["subject_id"],
            "obtained_score": obtained_score,
            "max_score": assessment["max_score"],
            "percentage": percentage,
            "grade": grade
        }
        self._scores[score_id] = record
        return record

    def update_score(self, score_id: str, new_obtained_score: float) -> dict:
        if score_id not in self._scores:
            raise LookupError(f"Score record '{score_id}' not found")

        score = self._scores[score_id]
        assessment = self._assessments[score["assessment_id"]]

        if new_obtained_score > assessment["max_score"]:
            raise ValueError(
                f"Obtained score ({new_obtained_score}) cannot exceed maximum allowed ({assessment['max_score']})"
            )

        percentage = round((new_obtained_score / assessment["max_score"]) * 100, 2)
        score["obtained_score"] = new_obtained_score
        score["percentage"] = percentage
        score["grade"] = calculate_grade(percentage)
        return score

    def get_student_results(self, student_id: str) -> dict:
        student_scores = [s for s in self._scores.values() if s["student_id"] == student_id]
        if not student_scores:
            raise LookupError(f"No results found for student '{student_id}'")

        overall_average = round(sum(s["percentage"] for s in student_scores) / len(student_scores), 2)
        return {
            "student_id": student_id,
            "total_assessments": len(student_scores),
            "overall_average": overall_average,
            "scores": student_scores
        }

    def calculate_subject_average(self, subject_id: str) -> dict:
        if subject_id not in self._subjects:
            raise LookupError(f"Subject '{subject_id}' does not exist")

        subject_scores = [s for s in self._scores.values() if s["subject_id"] == subject_id]
        if not subject_scores:
            return {
                "subject_id": subject_id,
                "total_records": 0,
                "average_percentage": 0.0,
                "message": "No scores recorded yet for this subject"
            }

        avg = round(sum(s["percentage"] for s in subject_scores) / len(subject_scores), 2)
        return {
            "subject_id": subject_id,
            "total_records": len(subject_scores),
            "average_percentage": avg
        }


# Singleton instance for simple stateful execution
academic_service = AcademicService()
