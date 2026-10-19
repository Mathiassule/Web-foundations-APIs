# API Documentation Reference

This document details all endpoints, authentication requirements, schemas, and error responses for the **Student Academic & Assessment Management API**.

---

## 🌐 Server URLs & Interactive Documentation
When the server is running:
* **Base URL**: `http://127.0.0.1:8000`
* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Raw OpenAPI Specification File**: [`docs/openapi.json`](file:///c:/Users/LENOVO/Desktop/git/Web-foundations-APIs/docs/openapi.json)

---

## 🔐 Authentication
* **Type**: HTTP Basic Authentication
* **Header**: `Authorization: Basic <base64(username:password)>`
* **Default Credentials**:
  * Username: `admin` | Password: `admin123` (Base64: `YWRtaW46YWRtaW4xMjM=`)
  * Username: `teacher` | Password: `teachpass2026`

Endpoints marked with 🔒 require authentication. Public endpoints can be queried by anyone.

---

## 📌 Endpoints Reference

### 1. System Health
#### `GET /`
Check service operational status.
* **Auth**: None
* **Response `200 OK`**:
```json
{
  "service": "Student Academic & Assessment Management API",
  "status": "operational",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 2. Subjects
#### `POST /subjects` 🔒
Create a new subject code and title.
* **Auth**: Basic Auth
* **Request Body**:
```json
{
  "id": "MTH101",
  "name": "General Mathematics I",
  "credit_units": 3
}
```
* **Responses**:
  * `201 Created`: Returns created subject object.
  * `400 Bad Request`: Subject code already exists.
  * `401 Unauthorized`: Missing or invalid credentials.
  * `422 Unprocessable Entity`: Validation failure (e.g. invalid characters or credit units out of 1-6 range).

#### `GET /subjects`
List all registered subjects.
* **Auth**: None
* **Response `200 OK`**: Array of Subject objects.

---

### 3. Assessments
#### `POST /assessments` 🔒
Create an assessment under an existing subject.
* **Auth**: Basic Auth
* **Request Body**:
```json
{
  "id": "MTH-QUIZ1",
  "subject_id": "MTH101",
  "title": "Quiz 1 - Linear Algebra",
  "max_score": 30.0,
  "weight_percentage": 20.0
}
```
* **Responses**:
  * `201 Created`: Assessment created.
  * `404 Not Found`: Subject does not exist.
  * `400 Bad Request`: Assessment ID already exists.

#### `GET /assessments`
List all created assessments across all subjects.
* **Auth**: None
* **Response `200 OK`**: Array of Assessment objects.

---

### 4. Scores
#### `POST /scores` 🔒
Record a score attained by a student on an assessment.
* **Auth**: Basic Auth
* **Request Body**:
```json
{
  "student_id": "STD2026-0042",
  "assessment_id": "MTH-QUIZ1",
  "obtained_score": 27.5
}
```
* **Responses**:
  * `201 Created`:
```json
{
  "id": "4B1A2C3D",
  "student_id": "STD2026-0042",
  "assessment_id": "MTH-QUIZ1",
  "subject_id": "MTH101",
  "obtained_score": 27.5,
  "max_score": 30.0,
  "percentage": 91.67,
  "grade": "A"
}
```
  * `400 Bad Request`: Score exceeds assessment `max_score` or duplicate entry exists.
  * `404 Not Found`: Assessment does not exist.

#### `PUT /scores/{score_id}` 🔒
Update a previously recorded student score.
* **Auth**: Basic Auth
* **Request Body**:
```json
{
  "obtained_score": 29.0
}
```
* **Responses**:
  * `200 OK`: Updated score object with recalculated percentage and grade.
  * `404 Not Found`: Score ID not found.

---

### 5. Results & Averages
#### `GET /students/{student_id}/results`
Retrieve a student's full result breakdown and computed overall percentage average.
* **Auth**: None
* **Response `200 OK`**:
```json
{
  "student_id": "STD2026-0042",
  "total_assessments": 1,
  "overall_average": 96.67,
  "scores": [
    {
      "id": "4B1A2C3D",
      "student_id": "STD2026-0042",
      "assessment_id": "MTH-QUIZ1",
      "subject_id": "MTH101",
      "obtained_score": 29.0,
      "max_score": 30.0,
      "percentage": 96.67,
      "grade": "A"
    }
  ]
}
```

#### `GET /subjects/{subject_id}/average`
Compute aggregate average percentage across all students and assessments for a specific subject.
* **Auth**: None
* **Response `200 OK`**:
```json
{
  "subject_id": "MTH101",
  "total_records": 1,
  "average_percentage": 96.67
}
```

---

## ⚠️ Consistent Error Envelope

All non-2xx responses adhere to this structure:
```json
{
  "error": {
    "code": "ERROR_CODE_NAME",
    "message": "Human-readable explanation of what failed"
  }
}
```
