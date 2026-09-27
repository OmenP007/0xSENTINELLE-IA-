from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from services import ai_service
from security import risk_engine

router = APIRouter()


@router.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...), claimed_brand: Optional[str] = Form(None)):
    image_bytes = await file.read()
    mime_type = file.content_type or "image/png"

    ai_result = ai_service.analyze_image(image_bytes, mime_type, claimed_brand)
    signals = ai_result.get("signals", [])
    result = risk_engine.build_risk_result(
        signals=signals,
        scam_type=ai_result.get("scam_type", "indetermine"),
        explanation=ai_result.get("explanation", ""),
        recommendations=ai_result.get("recommendations", []),
        target_brand=claimed_brand,
        original_input=f"Capture d'écran importée : {file.filename or 'image'}",
        ai_score=ai_result.get("score"),
        psychological_triggers=ai_result.get("psychological_triggers"),
        official_report=ai_result.get("official_report"),
    )
    return result


