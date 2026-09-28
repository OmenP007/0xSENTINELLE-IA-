import os
import httpx
import json
import re
from typing import Optional, List

def _get_brev_config():
    host = os.getenv("BREV_OLLAMA_HOST", "").strip()
    if host and not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    model = os.getenv("BREV_MODEL", "").strip()
    return host, model


def get_available_models(host: str) -> List[str]:
    """Récupère dynamiquement la liste des modèles installés sur Ollama."""
    try:
        resp = httpx.get(f"{host}/api/tags", timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            return [m.get("name") for m in data.get("models", []) if m.get("name")]
    except Exception:
        pass
    return []


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


def _extract_json_from_response(text: str) -> Optional[dict]:
    """Extrait le JSON d'une réponse LLM, en retirant les balises <think> (DeepSeek-R1)."""
    if not text:
        return None
    # Suppression des balises de raisonnement DeepSeek-R1 <think>...</think>
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    # Recherche d'un bloc JSON avec regex
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return None


def query_ollama_brev(prompt: str, system_instruction: str = "") -> Optional[dict]:
    """Interroge le modèle IA hébergé sur le GPU NVIDIA Brev via Ollama."""
    host, model = _get_brev_config()
    if not host:
        return None

    url = f"{host}/api/generate"
    
    # 1. Modèles dynamiquement détectés sur le serveur Brev
    available = get_available_models(host)

    # 2. Liste de priorité des modèles
    model_candidates = []
    if model:
        model_candidates.extend([model, f"{model}:latest"])

    model_candidates.extend(available)

    # 3. Candidats par défaut (nouveaux modèles Brev GPU)
    model_candidates.extend([
        "hf.co/bartowski/DeepSeek-R1-Distill-Qwen-32B-GGUF:Q4_K_M",
        "qwen2.5-coder:32b",
        "dolphin-mixtral:latest",
        "dolphin-mixtral",
        "dolphin-llama3:latest",
        "dolphin-llama3",
        "mistral:latest",
        "mistral"
    ])

    models_to_try = list(dict.fromkeys([m for m in model_candidates if m]))

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
            # 45s de timeout pour supporter les modèles 32B (DeepSeek-R1 / Qwen2.5-Coder)
            resp = httpx.post(url, json=payload, timeout=45.0)
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "").strip()
                parsed = _extract_json_from_response(response_text)
                if isinstance(parsed, dict):
                    print(f"[Ollama Brev GPU] Réponse réussie avec le modèle GPU NVIDIA: {m}")
                    return {
                        "scam_type": parsed.get("scam_type", "message_legitime" if parsed.get("score", 0) < 30 else "indetermine"),
                        "score": parsed.get("score", 0),
                        "signals": parsed.get("signals", []),
                        "psychological_triggers": parsed.get("psychological_triggers", []),
                        "explanation": parsed.get("explanation", "Analyse effectuée par 0xSentinelle IA."),
                        "recommendations": parsed.get("recommendations", ["Restez vigilant."]),
                        "confidence": parsed.get("confidence", "medium"),
                        "language_detected": parsed.get("language_detected", "fr"),
                        "verification_note": parsed.get("verification_note", ""),
                        "typosquatting_detected": parsed.get("typosquatting_detected", False),
                        "official_report": parsed.get("official_report", ""),
                    }
        except Exception as e:
            print(f"[Ollama Brev GPU] Essai modèle {m} échoué: {e}")
            continue

    return None



