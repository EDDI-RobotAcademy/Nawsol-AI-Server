from datetime import datetime

from pydantic import BaseModel

class CreateFinanceRequest(BaseModel):
    user_id: str
    type: str
    base_dt: datetime
    key: str
    value: str