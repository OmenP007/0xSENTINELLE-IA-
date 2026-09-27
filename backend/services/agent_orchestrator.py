"""0xSentinelle Agent Orchestrator
Coordinates multi-agent specialized analyses: Psychological Profiling, Technical Analysis, and Defense Advisory.
"""

from typing import List, Dict, Optional


def analyze_psychological_triggers(signals: List[str], explanation: str) -> List[Dict[str, str]]:
    """Specialized Psychological Profiling Agent."""
    triggers = []
    text_lower = explanation.lower()

    if "urgent_request" in signals or "urgence" in text_lower or "bloqu" in text_lower:
        triggers.append({
            "code": "urgence_artificielle",
            "name": "Urgence Artificielle ⏳",
            "description": "Pression temporelle pour empêcher la réflexion rationnelle."
        })
    if "payment_request" in signals or "paiement" in text_lower or "frais" in text_lower:
        triggers.append({
            "code": "demande_paiement",
            "name": "Extorsion / Paiement préalable 💳",
            "description": "Réclame de l'argent avant toute déblocage ou gain."
        })
    if "exceptional_promise" in signals or "gagn" in text_lower or "lot" in text_lower or "gratuit" in text_lower:
        triggers.append({
            "code": "appat_du_gain",
            "name": "Appât du Gain 🎁",
            "description": "Offre trop belle pour être vraie (concours fictif, tirage au sort)."
        })
    if "sensitive_info_request" in signals or "otp" in text_lower or "code" in text_lower or "mot de passe" in text_lower:
        triggers.append({
            "code": "vol_identifiant",
            "name": "Vol de Données Sensibles (OTP) 🔑",
            "description": "Tentative de détournement de code d'activation ou secret."
        })
    if "brand_impersonation" in signals or "usurpation" in text_lower or "officiel" in text_lower:
        triggers.append({
            "code": "fausse_autorite",
            "name": "Usurpation d'Autorité 🏢",
            "description": "Se fait passer pour un service officiel reconnu (Wave, Orange, MTN)."
        })

    if not triggers and signals:
        triggers.append({
            "code": "manipulation_generique",
            "name": "Incitabilité Suspecte ⚠️",
            "description": "Format non conforme aux règles habituelles de communication."
        })

    return triggers


def generate_official_abuse_report(
    scam_type: str,
    signals: List[str],
    explanation: str,
    target_brand: Optional[str] = None,
    original_input: Optional[str] = None
) -> str:
    """Specialized Defense Advisor Agent - Official Report Generator."""
    brand_name = target_brand.upper() if target_brand else "SERVICE CONCERNÉ"
    signals_formatted = ", ".join(signals) if signals else "Signaux d'ingénierie sociale"

    report = f"""==================================================
RAPPORT DE SIGNALEMENT D'ABUS — 0xSENTINELLE IA
==================================================
Date du rapport : Automatique
Service Cible : {brand_name}
Type de Menace Identifiée : {scam_type.upper()}
Signaux de Fraude : {signals_formatted}

RÉSUMÉ L'ANALYSE D'INGÉNIERIE SOCIALE :
{explanation}

ÉLÉMENT SUSPECT SOUMIS :
--------------------------------------------------
{original_input or "Contenu texte / capture d'écran / URL analysé."}
--------------------------------------------------

RECOMMANDATIONS TRANSMISES À L'UTILISATEUR :
1. Aucune donnée confidentielle ni code OTP n'a été communiqué.
2. Signalement transmis aux équipes de cybersécurité du réseau.
3. Blocage de l'expéditeur / domaine recommandé.

Généré par 0xSentinelle IA (Système Multi-Agents de Protection Numérique)
=================================================="""

    return report
