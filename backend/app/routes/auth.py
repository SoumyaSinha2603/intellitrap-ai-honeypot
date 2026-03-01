from fastapi import APIRouter, Form

router = APIRouter(prefix="/auth")

@router.post("/login")
def fake_login(username: str = Form(...), password: str = Form(...)):
    return {"error": "Invalid credentials"}
