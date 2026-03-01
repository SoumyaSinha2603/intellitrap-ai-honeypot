from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Event(BaseModel):
    ip: str
    endpoint: str
    method: str
    user_agent: Optional[str]
    payload: Optional[str]
    timestamp: datetime
