"""
Route /voice — Synthèse Vocale IA
Génère un MP3 d'alerte à la volée avec gTTS.
"""

from fastapi import APIRouter
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import Optional

from services.voice_service import generate_voice_mp3, is_available

router = APIRouter(prefix="/voice")


class VoiceRequest(BaseModel):
    score: int
    level: str
    explanation: str
    scam_type: Optional[str] = ""
    lang: Optional[str] = "fr"


@router.post("/alert")
async def voice_alert(req: VoiceRequest):
    """
    POST /voice/alert
    Génère et retourne un fichier MP3 de l'alerte vocale 0xSentinelle.
    """
    if not is_available():
        return JSONResponse(
            status_code=503,
            content={"error": "TTS non disponible. Installez gTTS : pip install gtts"},
        )

    mp3_bytes = generate_voice_mp3(
        score=req.score,
        level=req.level,
        explanation=req.explanation,
        scam_type=req.scam_type or "",
        lang=req.lang or "fr",
    )

    if mp3_bytes is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Erreur lors de la génération audio."},
        )

    return Response(
        content=mp3_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=alerte_0xsentinelle.mp3",
            "Cache-Control": "no-cache",
        },
    )


@router.get("/status")
async def voice_status():
    """GET /voice/status — Vérifie si le TTS est disponible."""
    return {
        "tts_available": is_available(),
        "engine": "gTTS (Google Text-to-Speech)" if is_available() else "Web Speech API (fallback)",
    }
