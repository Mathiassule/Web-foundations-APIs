# Student Academic & Assessment Management API

A robust, enterprise-grade RESTful API built with **FastAPI**, **Pydantic v2**, and **HTTP Basic Authentication** to manage subjects, assessments, and student evaluation scores.

---

## 📋 Table of Contents
1. [Overview & Deliverables](#-overview--deliverables)
2. [Concepts in Product & Engineering Language](#-concepts-in-product--engineering-language)
3. [Architecture & Codebase Design](#-architecture--codebase-design)
4. [Tradeoffs, Risks, and Limitations](#-tradeoffs-risks-and-limitations)
5. [Getting Started & Installation](#-getting-started--installation)
6. [API Endpoints & Documentation](#-api-endpoints--documentation)
7. [Running Tests](#-running-tests)
8. [Postman Collection & Verification](#-postman-collection--verification)

---

## 📦 Overview & Deliverables

This repository contains all mandatory artifacts required for the **Web Foundations and APIs** submission:

| Deliverable | Location in Repository | Description |
| :--- | :--- | :--- |
| **FastAPI Source Code** | `app/main.py`, `app/services.py` | Complete ASGI application and service domain implementation |
| **Pydantic Validation Models** | `app/schemas.py` | Strict request validation models, custom validators & response types |
| **Basic Authentication** | `app/auth.py` | Constant-time digest comparison protecting administrative routes |
| **Postman Collection** | `docs/Student_Academic_API.postman_collection.json` | Postman v2.1 collection covering all endpoints, headers & test scripts |
| **Sample JSON Payloads** | `docs/sample_requests_responses.json` | Request and response representations for 200, 201, 400, 401, 422 |
| **API Documentation** | Interactive Swagger (`/docs`), ReDoc (`/redoc`) | Auto-generated OpenAPI 3.1 specification with schemas & error models |
| **Automated Tests** | `tests/test_api.py`, `pytest.ini` | Pytest test suite asserting contract validity and integrity constraints |

---

## 💡 Concepts in Product & Engineering Language

### 1. HTTP & REST
* **Product Perspective**: Establishes standard nouns (resources) such as `/subjects`, `/assessments`, and `/scores`, allowing school web portals, mobile apps, and administrative reporting dashboards to interact reliably without custom communication protocols.
* **Engineering Perspective**: Adheres to stateless client-server architectural constraints. Employs semantic HTTP verbs (`POST` for creation, `GET` for safe and idempotent reads, `PUT` for complete resource updates) paired with standard status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `422 Unprocessable Entity`).

### 2. Request Validation (Pydantic)
* **Product Perspective**: Guarantees that corrupted, negative, or physically impossible grades (such as scoring 150 points on a 100-point quiz) never enter academic transcripts or skew GPA metrics.
* **Engineering Perspective**: Schema enforcement at the HTTP ingress seam. Inputs are validated before executing controller logic:
  * String trimming and uppercase normalization on identifiers (`MTH101`).
  * Boundary constraints (`ge=0.0`, `le=100.0`, `gt=0.0`).
  * Cross-field and business rule enforcement (verifying that `obtained_score <= assessment.max_score`).

### 3. Authentication & Error Responses
* **Product Perspective**: Protects student confidentiality and academic integrity by restricting grade alteration to authorized instructors. When a request fails, the API gives a transparent reason instead of an ambiguous failure screen.
* **Engineering Perspective**:
  * **Basic Authentication Seam**: Validates credentials using `secrets.compare_digest` to prevent timing attacks.
  * **Structured Error Bodies**: Errors consistently return an `{"error": {"code": "...", "message": "..."}}` envelope so client applications can parse machine-readable error codes programmatically.

---

## 🏛 Architecture & Codebase Design

This codebase follows **Deep Module** principles:

```
┌────────────────────────────────────────────────────────┐
│               HTTP Seam: app/main.py                   │
│   (Shallow interface: Route mapping, Status codes)     │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│     Security Seam       │  │    Deep Service Module   │
│      app/auth.py        │  │     app/services.py      │
│  - Constant-time digest │  │  - Grade computation     │
│  - HTTPBasic protocol   │  │  - Integrity constraints │
└─────────────────────────┘  │  - Metric aggregations   │
                             └─────────────────────────┘
```

1. **Leverage for Callers**: The `AcademicService` exposes simple primitives (`record_score`, `update_score`, `get_student_results`, `calculate_subject_average`) while encapsulating all grade bracket conversions, percentage normalization, and relational checks internally.
2. **Locality for Maintainers**: Modifications to how letter grades are assigned (e.g., standardizing from 90/80/70/60 to a 7-point scale) occur exclusively within `app/services.py` without touching HTTP routing or authentication logic.
3. **Seam Discipline**: `app/auth.py` serves as a pluggable dependency injection provider (`Depends(authenticate_credentials)`), allowing seamless transitions from HTTP Basic Auth to OAuth2 Bearer Tokens without restructuring domain logic.

---

## ⚖ Tradeoffs, Risks, and Limitations

| Dimension | Current Choice | Tradeoffs & Risks | Production Mitigation |
| :--- | :--- | :--- | :--- |
| **Authentication** | HTTP Basic Auth | Credentials transmitted per request encoded in Base64; vulnerable over unencrypted HTTP. | Enforce TLS/HTTPS; transition to JWT/OAuth2 tokens with short lifespans and refresh rotation. |
| **Storage Engine** | In-Memory Dictionaries | Rapid development with zero external dependencies; data resets upon server restart. | Introduce an abstract repository interface backed by PostgreSQL with SQLAlchemy/Tortoise ORM. |
| **Concurrency** | Synchronous In-Memory | High throughput for read workloads; race conditions possible during simultaneous score mutations across multiple worker processes. | Implement atomic database transactions with row-level locks or optimistic concurrency versioning. |
| **Rate Limiting** | None | Potential vulnerability to brute-force credential stuffing or denial-of-service. | Implement Redis token-bucket rate limiting (e.g., `slowapi`). |

---

## 🚀 Getting Started & Installation

### Prerequisites
* Python 3.10+
* Git

### 1. Clone & Setup
```bash
git clone https://github.com/<your-username>/Web-foundations-APIs.git
cd Web-foundations-APIs
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
The server will start at `http://127.0.0.1:8000`.

---

## 📖 API Endpoints & Documentation

Interactive API documentation is automatically accessible when the service is running:
* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Summary of Routes

| HTTP Method | Route | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/` | No | Service health check |
| `POST` | `/subjects` | **Yes** | Register a new subject |
| `GET` | `/subjects` | No | List all active subjects |
| `POST` | `/assessments` | **Yes** | Create an assessment for a subject |
| `GET` | `/assessments` | No | List all assessments |
| `POST` | `/scores` | **Yes** | Record a student score |
| `PUT` | `/scores/{score_id}` | **Yes** | Update a recorded score |
| `GET` | `/students/{student_id}/results`| No | Retrieve all scores and overall average |
| `GET` | `/subjects/{subject_id}/average`| No | Calculate the mean score across a subject |

### Default Credentials
* **Username**: `admin`
* **Password**: `admin123`
* *(Also accepts `teacher` / `teachpass2026`)*

---

## 🧪 Running Tests

Execute the automated test suite using `pytest`:

```bash
pytest -v
```

All 5 test cases will run and assert:
* Service health response
* Rejection of unauthenticated write attempts (`401 Unauthorized`)
* Subject creation and duplication constraints (`201 Created` vs `400 Bad Request`)
* Assessment mapping and referential integrity (`404 Not Found`)
* Score bounds validation, updates, grade assignment, and student & subject average computations.

---

## 📬 Postman Collection & Verification

Import the collection located at:
`docs/Student_Academic_API.postman_collection.json`

### Key features of the collection:
* Configured with collection-level variables (`baseUrl`, `admin_user`, `admin_password`).
* Built-in test script on `POST /scores` that automatically captures the generated `score_id` into a collection variable for the subsequent `PUT /scores/:score_id` test.
* Includes both authenticated requests (Subject/Assessment/Score creations) and unauthenticated consumer requests (Student results and averages).
