from fastapi import APIRouter, Request

router = APIRouter(prefix="/api")

@router.get("/config")
def fake_config():
    return {"config": "access denied"}

@router.post("/query")
async def fake_sql_query(request: Request):
    body = await request.body()
    
    # Fake SQL error response (classic bait)
    return {
        "error": "SQL syntax error near 'SELECT * FROM users'",
        "detail": body.decode(errors="ignore")
    }
