from pydantic import BaseModel
from typing import List, Optional


class TextAnalyzeRequest(BaseModel):
    message: str
    claimed_brand: Optional[str] = None


class UrlAnalyzeRequest(BaseModel):
    url: str
    claimed_brand: Optional[str] = None


class AISignalOutput(BaseModel):
    scam_type: str
    signals: List[str]
    explanation: str
    recommendations: List[str]
    confidence: Optional[str] = "medium"


class RiskResult(BaseModel):
    score: int
    level: str
    level_emoji: str
    scam_type: str
    signals: List[str]
    explanation: str
    recommendations: List[str]
    verification_note: Optional[str] = None
    psychological_triggers: Optional[List[dict]] = None
    official_report: Optional[str] = None
    typosquatting_detected: Optional[bool] = False



class ReplyGenerationRequest(BaseModel):
    original_message: str
    scam_type: Optional[str] = None
