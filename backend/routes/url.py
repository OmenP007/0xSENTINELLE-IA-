from fastapi import APIRouter
from models.schemas import UrlAnalyzeRequest
from services import url_service
from security import risk_engine

router = APIRouter()


@router.post("/analyze/url")
def analyze_url(req: UrlAnalyzeRequest):
    url_result = url_service.analyze_url(req.url, req.claimed_brand)
    signals = url_result["signals"]

    explanation_parts = url_result["notes"]
    explanation = " ".join(explanation_parts) if explanation_parts else "Aucun signal notable detecte sur cette URL."

    scam_type = "phishing / usurpation" if "brand_impersonation" in signals else (
        "url suspecte" if signals else "url sans signal detecte"
    )

    recommendations = []
    if signals:
        recommendations = [
            "Ne cliquez pas sur ce lien avant verification.",
            "Verifiez le service depuis son canal officiel.",
        ]
    else:
        recommendations = ["Restez prudent meme si aucun signal n'a ete detecte."]

    verification_note = None
    if url_result["verification"] == "non_confirme":
        verification_note = f"Domaine non confirme pour la marque '{url_result['detected_brand']}'."
    elif url_result["verification"] == "confirme":
        verification_note = f"Domaine confirme pour la marque '{url_result['detected_brand']}'."

    result = risk_engine.build_risk_result(
        signals=signals,
        scam_type=scam_type,
        explanation=explanation,
        recommendations=recommendations,
        verification_note=verification_note,
        target_brand=url_result.get("detected_brand") or req.claimed_brand,
        original_input=req.url,
    )
    result["domain"] = url_result["domain"]
    result["typosquatting_detected"] = url_result.get("typosquatting_detected", False)
    result["url_details"] = url_result.get("details", {})
    result["technical_findings"] = url_result.get("findings", [])
    return result


