import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# In-memory authorized staff credentials: {username: password}
CREDENTIALS_STORE = {
    "admin": "admin123",
    "teacher": "teachpass2026"
}


def authenticate_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Validates Basic Authentication credentials using constant-time comparison.
    Hides password verification logic behind a simple security seam.
    """
    stored_password = CREDENTIALS_STORE.get(credentials.username)
    if not stored_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"},
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(credentials.username, credentials.username)
    correct_password = secrets.compare_digest(credentials.password, stored_password)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"},
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
