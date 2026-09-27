import os
import json
import base64
import httpx
from typing import Optional

from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


def _get_gemini_config():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp").strip() or "gemini-2.0-flash-exp"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    return api_key, url


# ─── Prompt Système — Contexte Côte d'Ivoire ─────────────────────────────────
SYSTEM_INSTRUCTION = """Tu es 0xSentinelle IA, un expert en cybersécurité et détection d'arnaques numériques,
spécialisé dans le contexte de la Côte d'Ivoire (Abidjan, Bouaké, Yamoussoukro, San-Pédro, Korhogo, etc.).

Tu analyses les messages en FRANÇAIS, DIOULA, NOUCHI (argot ivoirien), ANGLAIS ou tout mélange de langues.

Contexte local ivoirien à prendre en compte :
- Services mobiles money : Orange Money CI, MTN Mobile Money CI, Wave CI, Moov Money CI, Free Money CI
- Plateformes : WhatsApp, Telegram, Facebook, TikTok, Instagram, Snapchat
- Institutions : BCEAO, SIB, Ecobank, Société Générale CI, NSIA Banque
- Services gouvernementaux : CNPS, CEPICI, DGI, Trésor Public, SOTRA
- Arnaques fréquentes en CI :
  * Faux concours Orange Money / MTN (SMS "Vous avez gagné 500.000 FCFA")
  * Faux recrutements (emplois fantômes, faux contrats ONG/mines)
  * Arnaques colis/DHL (faux douaniers, frais de déblocage)
  * Faux investissements crypto / Ponzi (Zircon, BitAfrique, etc.)
  * Escroquerie aux sentiments / broutage (faux militaires, faux blancs)
  * Fausse aide gouvernementale (faux CNPS, faux allocations)
  * Sextorsion / chantage photo
  * Faux marchands Jumia/Amazon
  * Arnaque au faux chèque ou virement en avance

Vocabulaire Nouchi / ivoirien à détecter :
- "gbê" (vrai/faux), "dja" (argent), "gâter" (escroquer), "gbaka" (attraper)
- "on se retrouve" (rendez-vous suspect), "c'est chaud" (urgent/dangereux)
- Formules typiques des brouteurs ivoiriens à reconnaître

Détecte les signaux suivants avec précision :
1. URGENCE artificielle (limité à 24h, compte bloqué, action immédiate)
2. DEMANDE_PAIEMENT inattendue, frais de déblocage, avance requise
3. PROMESSE_EXCEPTIONNELLE (gains, héritages, gains de loterie, FCFA en jeu)
4. MANIPULATION_PSYCHOLOGIQUE (peur, cupidité, compassion, autorité)
5. DEMANDE_INFOS_SENSIBLES (code OTP/PIN, mot de passe, NIN, CNI, carte bancaire)
6. USURPATION_MARQUE (faux logo Orange Money, faux agent MTN, faux CNPS)
7. URL_SUSPECTE ou typosquatting (orange-ci.com vs orange.ci, etc.)
8. INCOHERENCE (numéro étranger pour service local, grammaire suspecte)

Déclencheurs psychologiques à identifier :
- URGENCE, PEUR, CUPIDITE, AUTORITE, RECIPROCITE, COMPASSION, RARETE, VALIDATION_SOCIALE

Analyse de manière EXHAUSTIVE et réponds UNIQUEMENT en JSON valide, sans texte autour, sans balises markdown :
{
  "scam_type": "string (phishing | faux_concours | faux_recrutement | broutage | arnaque_colis | arnaque_crypto | faux_investissement | sextorsion | aide_gouvernement_frauduleuse | faux_marchand | arnaque_avance | message_legitime | indetermine)",
  "score": <entier 0-100, score de risque calculé>,
  "signals": ["liste des codes de signaux détectés"],
  "psychological_triggers": [
    {"name": "URGENCE", "description": "Explication courte du déclencheur détecté"}
  ],
  "explanation": "Explication claire et pédagogique en français ivoirien (2-4 phrases)",
  "recommendations": ["Actions concrètes à faire ou éviter"],
  "confidence": "low | medium | high",
  "language_detected": "fr | dioula | nouchi | en | mixte",
  "verification_note": "Note sur l'authenticité si marque connue (ou chaîne vide)",
  "typosquatting_detected": false,
  "official_report": "Modèle de signalement officiel pré-rempli pour la CI (ou chaîne vide)"
}

Calcul du score :
- 0-29 : message légitime ou très faible risque
- 30-59 : risque modéré, vigilance recommandée
- 60-79 : risque élevé, probablement une arnaque
- 80-100 : arnaque quasi-certaine, danger immédiat (STOP !)

Reste TOUJOURS dans l'estimation de risque — ne certifie jamais à 100% qu'il s'agit d'une fraude.
Pour les signalements, indique les contacts ivoiriens : ARTCI (Autorité de régulation), Cybercriminalité PJ CI (+225 27 20 25 98 72)."""


# ─── Score Bayésien Local — Côte d'Ivoire ────────────────────────────────────
HEURISTIC_KEYWORDS = {
    "fr": [
        "urgent", "félicitations", "gagné", "cliquez", "paiement", "code otp", "code pin",
        "bloqué", "récompense", "gratuit", "offre limitée", "24h", "immédiatement",
        "frais de déblocage", "frais de livraison", "avance", "virement",
        "fcfa", "500.000", "1.000.000", "numéro gagnant", "billet", "héritage",
        "agent", "douane", "colis bloqué", "mines", "contrat", "recrutement",
        "whatsapp uniquement", "ne parlez à personne", "c'est confidentiel",
    ],
    "nouchi": [
        "gâter", "dja", "on se retrouve", "c'est chaud", "gbê", "gbaka",
        "c'est bon hein", "fais vite", "envoie d'abord",
    ],
    "dioula": ["kari", "wari", "seben"],  # argent, document
    "en": ["congratulations", "winner", "click here", "limited", "urgent", "free", "otp", "secret code"],
}

SUSPICIOUS_DOMAINS = [
    "orange-money-ci", "orangemoney-ci", "mtn-money-ci", "mtn-ci-money",
    "wave-ci", "moov-money-ci", "cnps-ci", "tresor-ci", "cepici-gouv",
    "jumia-ci-promo", "dhl-ci-colis", "gouvernement-ci", "artci-gouv",
    "bceao-ci", "nsia-banque-ci",
]


def _bayesian_score_boost(text: str, ai_score: int) -> int:
    """Renforce le score IA avec des heuristiques locales."""
    text_lower = text.lower()
    boost = 0
    for lang, keywords in HEURISTIC_KEYWORDS.items():
        hits = sum(1 for k in keywords if k in text_lower)
        boost += hits * 3
    for domain in SUSPICIOUS_DOMAINS:
        if domain in text_lower:
            boost += 15
    return min(100, ai_score + boost)


def _level_from_score(score: int) -> tuple:
    if score >= 80:
        return "CRITIQUE", "🔴"
    elif score >= 60:
        return "ÉLEVÉ", "🟠"
    elif score >= 30:
        return "MODÉRÉ", "🟡"
    else:
        return "FAIBLE", "🟢"


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def _fallback_result(reason: str, message: str = "") -> dict:
    detected_signals = []
    text_lower = message.lower()
    if any(k in text_lower for k in ["code", "otp", "pin", "secret"]):
        detected_signals.append("DEMANDE_INFOS_SENSIBLES")
    if any(k in text_lower for k in ["urgent", "bloqué", "suspension", "24h", "immédiatement"]):
        detected_signals.append("URGENCE")
    if any(k in text_lower for k in ["payer", "acompte", "avance", "virement", "frais", "orange money", "mtn", "wave"]):
        detected_signals.append("DEMANDE_PAIEMENT")

    score = _bayesian_score_boost(message, 0) if message else 0
    if detected_signals and score < 50:
        score = 65
    level, emoji = _level_from_score(score)

    return {
        "scam_type": "phishing" if "DEMANDE_INFOS_SENSIBLES" in detected_signals else "indetermine",
        "score": score,
        "signals": detected_signals,
        "psychological_triggers": [{"name": "URGENCE", "description": "Menace de blocage ou délai court"}] if "URGENCE" in detected_signals else [],
        "explanation": f"Analyse heuristique de secours activée ({reason}). Signaux détectés par le moteur RAG local.",
        "recommendations": [
            "Ne communiquez aucune information sensible ni aucun code par SMS.",
            "Contactez directement le service client officiel avant d'effectuer un paiement.",
        ],
        "confidence": "medium" if detected_signals else "low",
        "language_detected": "fr",
        "verification_note": "",
        "typosquatting_detected": False,
        "official_report": "Signalement automatique de secours.",
        "level": level,
        "level_emoji": emoji,
    }



def _post_with_retry(payload: dict, timeout: float = 30.0) -> dict:
    api_key, _ = _get_gemini_config()
    if not api_key:
        raise ValueError("clé API manquante")

    configured_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp").strip() or "gemini-2.0-flash-exp"
    candidates = [configured_model, "gemini-2.0-flash-exp", "gemini-1.5-flash-latest", "gemini-flash-latest"]
    models = []
    for m in candidates:
        if m not in models:
            models.append(m)

    last_error = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(2):
            try:
                resp = httpx.post(url, json=payload, timeout=timeout)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 503:
                    import time
                    time.sleep(1)
                    continue
                else:
                    resp.raise_for_status()
            except Exception as e:
                last_error = e

    if last_error:
        raise last_error
    raise RuntimeError("Erreur API Gemini")


def _enrich_result(result: dict, raw_text: str) -> dict:
    """Enrichit le résultat avec niveau, emoji et score bayésien."""
    score = result.get("score", 0)
    # Calcul bayésien si le texte est disponible
    if raw_text:
        score = _bayesian_score_boost(raw_text, score)
        result["score"] = score
    level, emoji = _level_from_score(score)
    result["level"] = level
    result["level_emoji"] = emoji
    return result


from services import rag_service, ollama_service


BENIGN_SHORT_WORDS = {
    "ok", "okay", "k", "dak", "d'accord", "daccord", "merci", "salut", "bonjour",
    "bonsoir", "coucou", "hello", "hi", "yes", "oui", "non", "cool", "super",
    "merci bcp", "merci beaucoup", "test", "ca va", "ça va", "yo"
}


def analyze_text(message: str, claimed_brand: Optional[str] = None) -> dict:
    clean_msg = message.strip().lower()
    if clean_msg in BENIGN_SHORT_WORDS or (len(clean_msg) <= 3 and not any(c.isdigit() for c in clean_msg)):
        return {
            "scam_type": "message_legitime",
            "score": 0,
            "signals": [],
            "psychological_triggers": [],
            "explanation": "Ce message est un mot d'échange ou une salutation usuelle. Aucun indicateur de risque n'a été détecté.",
            "recommendations": ["Aucune action requise."],
            "confidence": "high",
            "language_detected": "fr",
            "verification_note": "",
            "typosquatting_detected": False,
            "official_report": "",
            "level": "FAIBLE",
            "level_emoji": "🟢"
        }

    # Recherche RAG des passages pertinents
    rag_context = rag_service.get_relevant_rag_context(f"{claimed_brand or ''} {message}", top_k=3)

    prompt = (
        f"Marque revendiquée (si connue): {claimed_brand or 'aucune'}\n\n"
        f"{rag_context}\n"
        f"Contenu à analyser:\n{message}"
    )

    # 1. Essai prioritaire via le GPU NVIDIA Brev (Ollama) si configuré
    if ollama_service.is_ollama_available():
        ollama_result = ollama_service.query_ollama_brev(prompt, SYSTEM_INSTRUCTION)
        if ollama_result:
            return _enrich_result(ollama_result, message)

    # 2. Sinon appel API Gemini
    api_key, _ = _get_gemini_config()
    if not api_key:
        return _fallback_result("clé API manquante", message)

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.15, "topP": 0.9},
    }
    try:
        data = _post_with_retry(payload, timeout=30.0)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = _extract_json(text)
        return _enrich_result(result, message)
    except Exception as e:
        return _fallback_result(str(e), message)



def analyze_conversation(transcript: str, claimed_brand: Optional[str] = None) -> dict:
    api_key, _ = _get_gemini_config()
    if not api_key:
        return _fallback_result("clé API manquante", transcript)

    # Recherche RAG des passages pertinents pour la conversation
    rag_context = rag_service.get_relevant_rag_context(f"{claimed_brand or ''} {transcript}", top_k=3)

    conv_prompt = (
        f"Tu es 0xSentinelle IA. Analyse cet ÉCHANGE COMPLET DE CONVERSATION (WhatsApp / Facebook Marketplace / SMS).\n"
        f"Marque/Service revendiqué: {claimed_brand or 'aucun'}\n\n"
        f"{rag_context}\n"
        f"--- TRANSCRIPT DE LA CONVERSATION ---\n"
        f"{transcript}\n"
        f"-------------------------------------\n\n"
        f"Examine attentivement si le correspondant agit comme un FAUX VENDEUR, demande un ACOMPTE/PAYEMENT EN AVANCE "
        f"via Mobile Money (Orange Money, MTN, Wave, Moov) avant livraison, ou partage des LIENS SUSPECTS.\n"
        f"Réponds UNIQUEMENT en JSON selon le format demandé dans les instructions système."
    )

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [{"parts": [{"text": conv_prompt}]}],
        "generationConfig": {"temperature": 0.15, "topP": 0.9},
    }
    try:
        data = _post_with_retry(payload, timeout=35.0)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = _extract_json(text)
        return _enrich_result(result, transcript)
    except Exception as e:
        return _fallback_result(str(e), transcript)



def analyze_image(image_bytes: bytes, mime_type: str, claimed_brand: Optional[str] = None) -> dict:
    api_key, _ = _get_gemini_config()
    if not api_key:
        return _fallback_result("clé API manquante")

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    rag_context = rag_service.get_relevant_rag_context(claimed_brand or "capture d'écran arnaque mobile money", top_k=2)

    prompt = (
        f"Marque revendiquée (si connue): {claimed_brand or 'aucune'}\n\n"
        f"{rag_context}\n"
        "Analyse cette image ou capture d'écran (SMS, WhatsApp, email, photo de profil, page web, ou extrait vidéo).\n"
        "Détecte :\n"
        "1. Les signaux d'arnaque (vol d'OTP, faux transfert, ingénierie sociale, nouchi/français).\n"
        "2. Les faux logos plagiés (Wave, Orange, MTN, BACI, Moov).\n"
        "3. Les artefacts d'IMAGES GÉNÉRÉES PAR IA / DEEPFAKES (visages synthétiques, fausses cartes d'identité créées par IA, lissage artificiel, artefacts de Deepfake vidéo/photo)."
    )
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": b64}},
                ]
            }
        ],
        "generationConfig": {"temperature": 0.15, "topP": 0.9},
    }
    try:
        data = _post_with_retry(payload, timeout=45.0)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = _extract_json(text)
        return _enrich_result(result, "")
    except Exception as e:
        return _fallback_result(str(e))



def generate_cautious_reply(original_message: str, scam_type: Optional[str] = None) -> str:
    api_key, _ = _get_gemini_config()
    if not api_key:
        return (
            "Bonjour, je préfère vérifier cette demande directement auprès du service officiel "
            "avant d'effectuer un paiement ou de communiquer une information. Merci."
        )
    prompt = (
        "Rédige une réponse courte, polie et prudente (2-3 phrases, en français) à envoyer "
        f"à ce correspondant suspect, sans confirmer aucune info sensible. Type: {scam_type or 'inconnu'}.\n\n"
        f"Message reçu:\n{original_message}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4},
    }
    try:
        data = _post_with_retry(payload, timeout=30.0)
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return (
            "Bonjour, je préfère vérifier cette demande directement auprès du service officiel "
            "avant d'effectuer un paiement ou de communiquer une information. Merci."
        )
