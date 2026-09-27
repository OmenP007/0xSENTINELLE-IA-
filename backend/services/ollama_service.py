import os
import httpx
import json
from typing import Optional

def _get_brev_config():
    host = os.getenv("BREV_OLLAMA_HOST", "").strip()
    model = os.getenv("BREV_MODEL", "mistral").strip() or "mistral"
    return host, model


def is_ollama_available() -> bool:
    """Vérifie si l'instance NVIDIA Brev Ollama est accessible."""
    host, _ = _get_brev_config()
    if not host:
        return False
    try:
        resp = httpx.get(f"{host}/api/tags", timeout=3.0)
        return resp.status_code == 200
    except Exception:
        return False


def query_ollama_brev(prompt: str, system_instruction: str = "") -> Optional[dict]:
    """Interroge le modèle IA hébergé sur le GPU NVIDIA Brev via Ollama."""
    host, model = _get_brev_config()
    if not host:
        return None

    url = f"{host}/api/generate"
    model_candidates = [model, f"{model}:latest", "mistral:latest", "mistral"]
    models_to_try = list(dict.fromkeys(model_candidates))

    for m in models_to_try:
        payload = {
            "model": m,
            "prompt": prompt,
            "system": system_instruction,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.15,
            },
        }
        try:
            resp = httpx.post(url, json=payload, timeout=25.0)
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "").strip()
                parsed = json.loads(response_text)
                if isinstance(parsed, dict):
                    print(f"[Ollama Brev GPU] Réponse réussie avec le modèle GPU NVIDIA: {m}")
                    # Normalisation des champs pour garantir la compatibilité
                    return {
                        "scam_type": parsed.get("scam_type", "phishing"),
                        "score": parsed.get("score", 85),
                        "signals": parsed.get("signals", ["demande_paiement", "urgence"]),
                        "psychological_triggers": parsed.get("psychological_triggers", []),
                        "explanation": parsed.get("explanation", "Analyse effectuée par le modèle hébergé sur le GPU NVIDIA Brev."),
                        "recommendations": parsed.get("recommendations", ["Ne communiquez aucun code secret par SMS.", "Vérifiez auprès du service officiel."]),
                        "confidence": parsed.get("confidence", "high"),
                        "language_detected": parsed.get("language_detected", "fr"),
                        "verification_note": parsed.get("verification_note"),
                        "typosquatting_detected": parsed.get("typosquatting_detected", False),
                        "official_report": parsed.get("official_report", ""),
                    }
        except Exception as e:
            print(f"[Ollama Brev GPU] Essai modèle {m} échoué: {e}")
            continue

    return None


