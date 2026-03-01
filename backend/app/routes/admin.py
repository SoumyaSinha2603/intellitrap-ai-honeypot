from fastapi import APIRouter
import time

from app.core.threat_state import get_threat_level

router = APIRouter(prefix="/admin")

@router.get("/dashboard")
def admin_dashboard():
    threat = get_threat_level()
    return {
        "message": "Unauthorized access detected",
        "current_threat_level": threat
    }

@router.get("/config")
def fake_admin_config():
    threat = get_threat_level()

    if threat == "LOW":
        return {
            "note": "Access denied",
            "status": "restricted"
        }

    elif threat == "MEDIUM":
        time.sleep(2)
        return {
            "db_user": "admin",
            "db_pass": "********",
            "secret_key": "sk_test_partial_key",
            "note": "Limited configuration exposed"
        }

    else:  # HIGH threat
        time.sleep(4)
        return {
            "db_user": "admin",
            "db_pass": "admin123",
            "secret_key": "sk_test_51_fake_key",
            "aws_access_key": "AKIA_FAKE_KEY",
            "note": "Full configuration leak (honeypot)"
        }
