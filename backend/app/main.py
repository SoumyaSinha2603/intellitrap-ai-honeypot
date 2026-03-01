from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pandas as pd
from datetime import datetime

from fastapi import FastAPI, Request
from app.core.logger import log_event
from app.routes import (
    auth_router,
    admin_router,
    api_router,
    files_router,
    threat_router
)

app = FastAPI(title="Adaptive AI Honeypot")

# Template directory (Docker-safe)
templates = Jinja2Templates(directory="app/templates")

# -------------------- MIDDLEWARE --------------------
@app.middleware("http")
async def capture_events(request: Request, call_next):

    body = None

    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()

    event = {
        "ip": request.client.host if request.client else "unknown",
        "endpoint": request.url.path,
        "method": request.method,
        "user_agent": request.headers.get("user-agent"),
        "payload": body.decode(errors="ignore") if body else None
    }

    log_event(event)
    response = await call_next(request)
    return response


# -------------------- ROUTERS --------------------
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(api_router)
app.include_router(files_router)
app.include_router(threat_router)


# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {"status": "Honeypot Active"}


# -------------------- DASHBOARD --------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    df = pd.read_csv("ml/attacker_dataset.csv")
    latest = df.iloc[-1]

    # ---------------- RISK SCORE (LATEST SESSION) ----------------
    risk_score = min(
        int(latest["request_count"]) * 5 +
        int(latest["sql_keyword_count"]) * 20,
        100
    )

    # ---------------- THREAT LEVEL ----------------
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # ---------------- EXPLAINABLE AI ----------------
    reasons = []

    if latest["sql_keyword_count"] == 0:
        reasons.append("No SQL injection patterns detected")
    else:
        reasons.append("SQL injection indicators detected")

    if latest["request_count"] < 10:
        reasons.append("Normal request frequency")
    elif latest["request_count"] < 20:
        reasons.append("Elevated request frequency")
    else:
        reasons.append("High request rate (possible attack)")

    # ---------------- ADAPTIVE RESPONSE ----------------
    adaptive_response = [
        "Fake credentials served",
        "Decoy endpoints enabled",
        "Attack logging intensified"
    ]

    # ---------------- SYSTEM HEALTH ----------------
    system_status = {
        "Honeypot": "Active",
        "Logging": "Enabled",
        "ML Model": "Loaded",
        "Container": "Running"
    }

    # ---------------- RISK TREND (FOR GRAPH) ----------------
    risk_scores = []
    for _, row in df.iterrows():
        score = min(
            int(row["request_count"]) * 5 +
            int(row["sql_keyword_count"]) * 20,
            100
        )
        risk_scores.append(score)

    session_labels = list(range(1, len(risk_scores) + 1))

    # ---------------- RENDER TEMPLATE ----------------
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "request_count": int(latest["request_count"]),
            "sql_keyword_count": int(latest["sql_keyword_count"]),
            "reasons": reasons,
            "adaptive_response": adaptive_response,
            "system_status": system_status,
            "risk_scores": risk_scores,
            "session_labels": session_labels,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
