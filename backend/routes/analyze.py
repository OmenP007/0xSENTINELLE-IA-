from fastapi import APIRouter
from models.schemas import TextAnalyzeRequest, ReplyGenerationRequest
from services import ai_service
from security import risk_engine

router = APIRouter()


@router.post("/analyze/text")
def analyze_text(req: TextAnalyzeRequest):
    ai_result = ai_service.analyze_text(req.message, req.claimed_brand)
    signals = ai_result.get("signals", [])
    result = risk_engine.build_risk_result(
        signals=signals,
        scam_type=ai_result.get("scam_type", "indetermine"),
        explanation=ai_result.get("explanation", ""),
        recommendations=ai_result.get("recommendations", []),
        target_brand=req.claimed_brand,
        original_input=req.message,
        ai_score=ai_result.get("score"),
        psychological_triggers=ai_result.get("psychological_triggers"),
        official_report=ai_result.get("official_report"),
    )
    return result




@router.post("/analyze/conversation")
def analyze_conversation(req: TextAnalyzeRequest):
    ai_result = ai_service.analyze_conversation(req.message, req.claimed_brand)
    signals = ai_result.get("signals", [])
    result = risk_engine.build_risk_result(
        signals=signals,
        scam_type=ai_result.get("scam_type", "indetermine"),
        explanation=ai_result.get("explanation", ""),
        recommendations=ai_result.get("recommendations", []),
        target_brand=req.claimed_brand,
        original_input=req.message,
        ai_score=ai_result.get("score"),
        psychological_triggers=ai_result.get("psychological_triggers"),
        official_report=ai_result.get("official_report"),
    )
    return result


@router.post("/analyze/reply")
def generate_reply(req: ReplyGenerationRequest):
    reply = ai_service.generate_cautious_reply(req.original_message, req.scam_type)
    return {"reply": reply}

