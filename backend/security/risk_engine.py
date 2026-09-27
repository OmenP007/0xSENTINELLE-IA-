from typing import List, Tuple, Optional, Any
import re

# Table universelle de pondération des signaux (FR & EN, avec ou sans espaces/accents)
SIGNAL_WEIGHTS = {
    # Anglais
    "payment_request": 25,
    "urgent_request": 15,
    "exceptional_promise": 20,
    "suspicious_url": 25,
    "brand_impersonation": 25,
    "sensitive_info_request": 25,
    "manipulation": 15,
    "inconsistency": 10,
    # Français normalisé
    "demande_paiement": 25,
    "urgence": 15,
    "promesse_exceptionnelle": 20,
    "url_suspecte": 25,
    "usurpation_marque": 25,
    "demande_infos_sensibles": 25,
    "manipulation_psychologique": 15,
    "incoherence": 10,
}

# Types d'arnaques avérées qui imposent un plancher de score minimal
DANGEROUS_SCAM_TYPES = {
    "phishing": 85,
    "broutage": 85,
    "faux_concours": 75,
    "faux_recrutement": 75,
    "arnaque_colis": 80,
    "arnaque_crypto": 85,
    "faux_investissement": 85,
    "sextorsion": 90,
    "aide_gouvernement_frauduleuse": 85,
    "faux_marchand": 75,
    "arnaque_avance": 80,
    "usurpation": 85,
    "phishing / usurpation": 85,
    "url suspecte": 75,
}

LEVELS = [
    (0, 29, "FAIBLE", "🟢"),
    (30, 59, "MODÉRÉ", "🟡"),
    (60, 79, "ÉLEVÉ", "🟠"),
    (80, 100, "CRITIQUE", "🔴"),
]

from services import agent_orchestrator


def _normalize_signal(s: str) -> str:
    """Normalise une chaîne de signal (sans majuscules, sans espaces, sans accents)."""
    s = s.lower().strip()
    s = s.replace(" ", "_")
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[àâä]", "a", s)
    s = re.sub(r"[îï]", "i", s)
    s = re.sub(r"[ôö]", "o", s)
    s = re.sub(r"[ùûü]", "u", s)
    s = re.sub(r"[ç]", "c", s)
    return s


def compute_score(signals: List[str], scam_type: str = "", ai_score: Optional[int] = None) -> int:
    # 1. Calcul basé sur la somme des poids des signaux
    signal_score = 0
    for s in signals:
        norm = _normalize_signal(s)
        # Recherche exacte ou partielle dans SIGNAL_WEIGHTS
        matched_weight = 0
        for key, weight in SIGNAL_WEIGHTS.items():
            if key in norm or norm in key:
                matched_weight = max(matched_weight, weight)
        signal_score += matched_weight if matched_weight > 0 else 15

    # 2. Plancher minimum selon le type d'arnaque
    scam_floor = DANGEROUS_SCAM_TYPES.get(scam_type.lower().strip(), 0)

    # 3. Récupération du score IA s'il existe
    base_ai_score = ai_score if ai_score is not None else 0

    # Score final = maximum entre le score des signaux, le plancher du type d'arnaque et le score IA
    final_score = max(signal_score, scam_floor, base_ai_score)

    # Si des signaux critiques sont présents (ex: URL suspecte, Usurpation, OTP), garantir au moins 70
    normalized_signals = [_normalize_signal(s) for s in signals]
    critical_terms = ["usurpation", "url", "sensibles", "otp", "promesse", "paiement", "broutage", "brand", "phishing"]
    if any(any(term in s for term in critical_terms) for s in normalized_signals):
        final_score = max(final_score, 70)

    return min(100, max(0, final_score))


def get_level(score: int) -> Tuple[str, str]:
    for low, high, name, emoji in LEVELS:
        if low <= score <= high:
            return name, emoji
    return "CRITIQUE", "🔴"


def build_risk_result(
    signals: List[str],
    scam_type: str,
    explanation: str,
    recommendations: List[str],
    verification_note: Optional[str] = None,
    target_brand: Optional[str] = None,
    original_input: Optional[str] = None,
    ai_score: Optional[int] = None,
    psychological_triggers: Optional[List[Any]] = None,
    official_report: Optional[str] = None,
) -> dict:
    score = compute_score(signals, scam_type=scam_type, ai_score=ai_score)
    level, emoji = get_level(score)

    # Utiliser les triggers de l'IA s'ils existent, sinon utiliser l'orchestrateur
    if not psychological_triggers:
        psychological_triggers = agent_orchestrator.analyze_psychological_triggers(signals, explanation)

    if not official_report:
        official_report = agent_orchestrator.generate_official_abuse_report(
            scam_type=scam_type,
            signals=signals,
            explanation=explanation,
            target_brand=target_brand,
            original_input=original_input,
        )

    return {
        "score": score,
        "level": level,
        "level_emoji": emoji,
        "scam_type": scam_type,
        "signals": signals,
        "explanation": explanation,
        "recommendations": recommendations,
        "verification_note": verification_note,
        "psychological_triggers": psychological_triggers,
        "official_report": official_report,
    }


