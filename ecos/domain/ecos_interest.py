from datetime import datetime

class EcosInterest:
    def __init__(self, interest_type: str, interest_rate: float, erm_date: datetime, created_at: datetime):
        self.interest_type = interest_type
        self.interest_rate = interest_rate
        self.erm_date = erm_date
        self.created_at = created_at