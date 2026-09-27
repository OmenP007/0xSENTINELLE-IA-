"""
Service de synthèse vocale — 0xSentinelle IA
Utilise gTTS (Google Text-to-Speech) pour générer une voix naturelle française.
Fallback vers Web Speech API si gTTS indisponible.
"""

import os
import io
import re
from typing import Optional

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


def _clean_text_for_tts(text: str) -> str:
    """Nettoie le texte pour la synthèse vocale : retire emojis, URLs, balises."""
    # Retirer emojis
    text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
    text = re.sub(r'[\u2600-\u26FF]', '', text)
    text = re.sub(r'[\u2700-\u27BF]', '', text)
    # Retirer URLs
    text = re.sub(r'https?://\S+', 'une URL suspecte', text)
    # Retirer caractères spéciaux excessifs
    text = re.sub(r'[#@*_~`]', '', text)
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _build_alert_text(score: int, level: str, explanation: str, scam_type: str) -> str:
    """Construit le texte d'alerte vocale structuré."""
    level_phrases = {
        "CRITIQUE": "Alerte critique ! Danger immédiat détecté.",
        "ÉLEVÉ": "Alerte. Risque élevé détecté.",
        "MODÉRÉ": "Attention. Risque modéré détecté.",
        "FAIBLE": "Analyse terminée. Faible risque détecté.",
    }
    intro = level_phrases.get(level, "Analyse terminée.")
    scam_map = {
        "phishing": "tentative de hameçonnage",
        "faux_concours": "faux concours",
        "faux_vendeur": "faux vendeur",
        "usurpation_marque": "usurpation de marque",
        "sextorsion": "sextorsion",
        "faux_emploi": "fausse offre d'emploi",
        "arnaque_crypto": "arnaque aux cryptomonnaies",
        "aide_gouvernement_frauduleuse": "aide gouvernementale frauduleuse",
        "message_legitime": "message légitime",
    }
    type_fr = scam_map.get(scam_type, scam_type or "arnaque")
    clean_expl = _clean_text_for_tts(explanation)
    text = f"{intro} Score de risque : {score} sur cent. Type détecté : {type_fr}. {clean_expl}"
    return text


def generate_voice_mp3(
    score: int,
    level: str,
    explanation: str,
    scam_type: str = "",
    lang: str = "fr",
) -> Optional[bytes]:
    """
    Génère un fichier MP3 de l'alerte vocale.
    Retourne les bytes MP3 ou None si gTTS non disponible.
    """
    if not GTTS_AVAILABLE:
        return None

    text = _build_alert_text(score, level, explanation, scam_type)

    # Limiter à 500 caractères pour gTTS
    if len(text) > 500:
        text = text[:497] + "..."

    try:
        tts = gTTS(text=text, lang=lang, slow=False, tld="fr")
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)
        return mp3_buffer.read()
    except Exception as e:
        print(f"[voice_service] Erreur gTTS: {e}")
        return None


def is_available() -> bool:
    """Vérifie si le service TTS est disponible."""
    return GTTS_AVAILABLE
