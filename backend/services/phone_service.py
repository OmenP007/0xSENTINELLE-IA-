"""
Service de vérification de numéros de téléphone suspects — 0xSentinelle
Blacklist communautaire des arnaqueurs connus en Côte d'Ivoire
"""
import json
import re
import os
from typing import Optional

BLACKLIST_PATH = os.path.join(os.path.dirname(__file__), "../rag/phone_blacklist.json")


def normalize_phone(numero: str) -> str:
    """Normalise un numéro de téléphone en format international +225XXXXXXXXXX."""
    cleaned = re.sub(r"[\s\-\.\(\)]", "", numero.strip())
    # Ajouter +225 si numéro local ivoirien à 10 chiffres
    if re.match(r"^0[0-9]{9}$", cleaned):
        cleaned = "+225" + cleaned[1:]
    # Ajouter +225 si numéro à 8 chiffres (ancien format CI)
    elif re.match(r"^[0-9]{8}$", cleaned):
        cleaned = "+225" + cleaned
    # Ajouter + si absent
    elif re.match(r"^225[0-9]{10}$", cleaned):
        cleaned = "+" + cleaned
    return cleaned


def check_phone_blacklist(numero: str) -> dict:
    """Vérifie si un numéro est dans la blacklist des arnaqueurs connus."""
    normalized = normalize_phone(numero)

    try:
        with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception as e:
        return {"error": f"Impossible de charger la blacklist : {e}"}

    for entry in db.get("numbers", []):
        if normalize_phone(entry["numero"]) == normalized:
            signalements = entry.get("signalements", 1)
            return {
                "numero": normalized,
                "found_in_blacklist": True,
                "signalements": signalements,
                "type_arnaque": entry.get("type", "Inconnu"),
                "region": entry.get("region", "Inconnue"),
                "score": min(95, 50 + signalements * 5),
                "level": "CRITIQUE" if signalements >= 5 else "ÉLEVÉ",
                "message": f"⚠️ Ce numéro a été signalé {signalements} fois pour : {entry.get('type', 'arnaque')}."
            }

    return {
        "numero": normalized,
        "found_in_blacklist": False,
        "signalements": 0,
        "score": 0,
        "level": "NON SIGNALÉ",
        "message": "✅ Ce numéro n'est pas dans notre blacklist. Restez vigilant."
    }


def report_phone(numero: str, type_arnaque: str, region: str = "Inconnue") -> dict:
    """Ajoute ou incrémente un signalement dans la blacklist communautaire."""
    normalized = normalize_phone(numero)

    try:
        with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception:
        db = {"last_updated": "", "total_entries": 0, "numbers": []}

    for entry in db["numbers"]:
        if normalize_phone(entry["numero"]) == normalized:
            entry["signalements"] += 1
            db["last_updated"] = "2026-09-27"
            with open(BLACKLIST_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            return {"status": "updated", "signalements": entry["signalements"], "numero": normalized}

    # Nouveau numéro
    db["numbers"].append({
        "numero": normalized,
        "signalements": 1,
        "type": type_arnaque,
        "region": region
    })
    db["total_entries"] = len(db["numbers"])
    db["last_updated"] = "2026-09-27"

    with open(BLACKLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    return {"status": "added", "signalements": 1, "numero": normalized}
