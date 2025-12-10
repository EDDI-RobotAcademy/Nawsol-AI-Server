from datetime import datetime

from pydantic import BaseModel

class FinanceResponse(BaseModel):
    id: int
    user_id: str
    type: str
    base_dt: str
    key: str
    value: str