from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services import phone_service

router = APIRouter()


class PhoneCheckRequest(BaseModel):
    numero: str


class PhoneReportRequest(BaseModel):
    numero: str
    type_arnaque: str
    region: Optional[str] = "Inconnue"


@router.post("/analyze/phone")
def check_phone(req: PhoneCheckRequest):
    return phone_service.check_phone_blacklist(req.numero)


@router.post("/report/phone")
def report_phone(req: PhoneReportRequest):
    return phone_service.report_phone(req.numero, req.type_arnaque, req.region)
