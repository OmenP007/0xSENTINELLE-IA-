import re
from urllib.parse import urlparse, parse_qs
from typing import Optional

from . import trusted_sources

SUSPICIOUS_KEYWORDS = [
    "verify", "verification", "secure", "update", "confirm", "account",
    "gagnant", "gain", "bonus", "urgent", "suspend", "recover", "reset",
    "wallet", "otp", "deblocage", "connexion", "login", "auth", "banque",
    "pay", "recharge", "gratuit", "kdo", "cadeau",
]

BRAND_LOOKALIKES = ["wave", "orange", "mtn", "momo", "djamo", "moov", "jumia", "cnps"]

HIGH_RISK_TLDS = [
    ".xyz", ".top", ".site", ".online", ".cc", ".tk", ".ml", ".ga", ".cf",
    ".gq", ".click", ".buzz", ".club", ".vip", ".work", ".info", ".link",
]


def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def detect_typosquatting(domain_no_port: str) -> Optional[dict]:
    parts = re.split(r"[\.-]", domain_no_port)
    for part in parts:
        part_clean = part.lower().strip()
        if len(part_clean) < 3:
            continue
        for brand in BRAND_LOOKALIKES:
            if part_clean == brand:
                continue
            dist = levenshtein_distance(part_clean, brand)
            if dist == 1 or (dist == 2 and len(brand) >= 5):
                return {
                    "suspicious_part": part_clean,
                    "target_brand": brand,
                    "distance": dist,
                }
    return None


def analyze_url(url: str, claimed_brand: Optional[str] = None) -> dict:
    signals = []
    notes = []
    findings = []

    raw_url = url.strip()
    if not re.match(r"^https?://", raw_url, re.IGNORECASE):
        url_to_parse = "http://" + raw_url
        signals.append("suspicious_url")
        notes.append("Protocole HTTPS manquant.")
        findings.append("⚠️ Protocole HTTPS absent ou non spécifié.")
    else:
        url_to_parse = raw_url

    parsed = urlparse(url_to_parse)
    domain = parsed.netloc.lower()
    domain_no_port = domain.split(":")[0]
    path = parsed.path.lower()
    query = parsed.query

    # 1. Analyse du protocole
    is_https = parsed.scheme == "https"
    if not is_https:
        signals.append("suspicious_url")
        notes.append("Connexion non sécurisée (HTTP au lieu de HTTPS).")
        findings.append("🔴 Connexion HTTP non sécurisée (absence de certificat SSL).")

    # 2. Détection d'adresse IP brute (ex: http://192.168.1.1/wave)
    is_ip_address = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain_no_port))
    if is_ip_address:
        signals.append("suspicious_url")
        notes.append("L'URL utilise une adresse IP brute au lieu d'un nom de domaine officiel.")
        findings.append("🔴 Adresse IP brute détectée au lieu d'un nom de domaine.")

    # 3. Analyse des TLD à haut risque
    tld_detected = None
    for tld in HIGH_RISK_TLDS:
        if domain_no_port.endswith(tld):
            tld_detected = tld
            signals.append("suspicious_url")
            notes.append(f"Extension de domaine à haut risque ({tld}) très fréquemment utilisée en hameçonnage.")
            findings.append(f"🟠 Extension TLD à haut risque détectée ({tld}).")
            break

    # 4. Structure des sous-domaines (ex: wave.kdo.com -> sous-domaine = wave, domaine réel = kdo.com)
    subdomains = domain_no_port.split(".")
    subdomain_count = len(subdomains) - 2 if len(subdomains) > 2 else 0
    subdomain_impersonation = None
    if len(subdomains) >= 3:
        subdomain_part = subdomains[0]
        for brand in BRAND_LOOKALIKES:
            if brand in subdomain_part:
                subdomain_impersonation = brand
                signals.append("brand_impersonation")
                signals.append("suspicious_url")
                notes.append(
                    f"Le sous-domaine '{subdomain_part}' tente d'imiter la marque '{brand}' alors que le vrai domaine est '{'.'.join(subdomains[1:])}'."
                )
                findings.append(
                    f"🚨 Faux sous-domaine d'usurpation : '{subdomain_part}' cherche à faire croire que la page appartient à '{brand}'."
                )

    if any(ch in domain_no_port for ch in ["--", "_"]):
        signals.append("suspicious_url")
        notes.append("Caractères suspects ('--', '_') dans le nom de domaine.")
        findings.append("⚠️ Tirets multiples ou caractères spéciaux dans le nom de domaine.")

    # 5. Typosquatting
    typosquat = detect_typosquatting(domain_no_port)
    if typosquat:
        signals.append("brand_impersonation")
        signals.append("suspicious_url")
        notes.append(
            f"Détection de typosquatting : '{typosquat['suspicious_part']}' imite la marque '{typosquat['target_brand']}'."
        )
        findings.append(
            f"🚨 Typosquatting détecté : '{typosquat['suspicious_part']}' tente d'imiter la marque officielle '{typosquat['target_brand']}'."
        )

    # 6. Marque détectée et vérification
    detected_brand = claimed_brand
    if not detected_brand:
        if subdomain_impersonation:
            detected_brand = subdomain_impersonation
        else:
            for brand in BRAND_LOOKALIKES:
                if brand in domain_no_port:
                    detected_brand = brand
                    break

    verification = None
    if detected_brand:
        official = trusted_sources.is_domain_official(detected_brand, domain_no_port)
        if official is False:
            signals.append("brand_impersonation")
            signals.append("suspicious_url")
            notes.append(
                f"Le domaine '{domain_no_port}' ne correspond à aucun domaine officiel connu pour '{detected_brand}'."
            )
            findings.append(
                f"🔴 Domaine non officiel pour la marque '{detected_brand}'. (Domaine réel: {domain_no_port})"
            )
            verification = "non_confirme"
        elif official is True:
            verification = "confirme"
            notes.append(f"Domaine reconnu comme officiel pour '{detected_brand}'.")
            findings.append(f"✅ Domaine officiel confirmé pour '{detected_brand}'.")

    # 7. Mots-clés de phishing dans le domaine, le chemin ou les paramètres
    found_keywords = []
    full_url_lower = raw_url.lower()
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in full_url_lower:
            found_keywords.append(kw)

    if found_keywords:
        if "suspicious_url" not in signals:
            signals.append("suspicious_url")
        notes.append(f"Mots-clés de phishing détectés dans l'URL : {', '.join(found_keywords)}.")
        findings.append(f"🟠 Mots-clés suspects trouvés dans l'URL : {', '.join(found_keywords)}.")

    # 8. Analyse du chemin (path) & paramètres (query)
    if any(login_kw in path for login_kw in ["login", "connexion", "auth", "signin", "otp", "deblocage"]):
        findings.append("🔑 Page de connexion ou formulaire d'authentification / OTP suspect détecté dans l'URL.")
        signals.append("sensitive_info_request")

    parsed_params = parse_qs(query)
    query_param_keys = list(parsed_params.keys())

    return {
        "domain": domain_no_port,
        "scheme": parsed.scheme,
        "is_https": is_https,
        "is_ip_address": is_ip_address,
        "tld_detected": tld_detected,
        "path_analyzed": path,
        "query_param_keys": query_param_keys,
        "detected_brand": detected_brand,
        "signals": list(dict.fromkeys(signals)),
        "notes": notes,
        "findings": findings,
        "verification": verification,
        "typosquatting_detected": typosquat is not None or subdomain_impersonation is not None,
        "details": {
            "full_url": raw_url,
            "host": domain_no_port,
            "protocol": parsed.scheme.upper(),
            "path": path or "/",
            "query_parameters": query_param_keys,
            "suspicious_keywords_found": found_keywords,
            "technical_findings": findings,
        },
    }


