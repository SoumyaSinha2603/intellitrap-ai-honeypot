from fastapi import APIRouter

router = APIRouter(prefix="/files")

@router.get("/backup.zip")
def fake_backup():
    return {
        "error": "Permission denied",
        "hint": "Try accessing /files/db_backup.sql"
    }

@router.get("/db_backup.sql")
def fake_db_dump():
    return {
        "users": [
            {"id": 1, "username": "admin", "password": "admin123"},
            {"id": 2, "username": "test", "password": "test123"}
        ]
    }
