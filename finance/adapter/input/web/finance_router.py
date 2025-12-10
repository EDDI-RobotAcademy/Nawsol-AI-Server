from typing import List
from fastapi import APIRouter, Body, HTTPException

from finance.adapter.input.web.request.create_finance_request import CreateFinanceRequest
from finance.adapter.input.web.response.finance_response import FinanceResponse
from finance.application.usecase.finance_usecase import FinanceUseCase

usecase = FinanceUseCase().get_instance()

finance_router = APIRouter(tags=["finance"])
@finance_router.post("", response_model=List[FinanceResponse])
def save_etf(create_finance: List[CreateFinanceRequest] = Body(...)):
    finance = usecase.save_finance_data(create_finance)
    if not finance:
        raise HTTPException(status_code=400, detail="Finance data is empty")
    return finance
