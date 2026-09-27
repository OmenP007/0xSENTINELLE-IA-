from fastapi import APIRouter, Response
from pydantic import BaseModel
from typing import Optional, List
from services import pdf_service

router = APIRouter()


class PDFReportRequest(BaseModel):
    target_input: str
    input_type: str = "url"
    risk_level: str = "ÉLEVÉ"
    risk_score: int = 85
    scam_type: str = "Phishing / Usurpation de Marque"
    target_brand: Optional[str] = "Non spécifiée"
    explanation: str = "Signal de phishing détecté par 0xSentinelle IA."
    recommendations: List[str] = ["Ne pas cliquer sur le lien.", "Contacter votre banque."]


@router.post("/report/pdf")
def generate_pdf(req: PDFReportRequest):
    pdf_content = pdf_service.generate_plcc_report(
        target_input=req.target_input,
        input_type=req.input_type,
        risk_level=req.risk_level,
        risk_score=req.risk_score,
        scam_type=req.scam_type,
        target_brand=req.target_brand,
        explanation=req.explanation,
        recommendations=req.recommendations
    )

    filename = f"Rapport_PLCC_0xSentinelle_{req.risk_score}pct.pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
