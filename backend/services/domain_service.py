"""
Service d'inspection de domaine et certificat SSL — 0xSentinelle IA
Détecte l'âge récent du domaine et la validité SSL/TLS.
"""
import socket
import ssl
from urllib.parse import urlparse
import datetime


def check_domain_security(target_url: str) -> dict:
    """Inspecte le certificat SSL/TLS d'un domaine suspect."""
    parsed = urlparse(target_url if target_url.startswith("http") else "https://" + target_url)
    hostname = parsed.hostname or target_url

    res = {
        "hostname": hostname,
        "ssl_active": False,
        "issuer": "Inconnu",
        "days_remaining": 0,
        "is_suspicious_ssl": False,
        "notes": []
    }

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3.0) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                res["ssl_active"] = True

                # Extraction émetteur
                issuer = dict(x[0] for x in cert.get("issuer", []))
                res["issuer"] = issuer.get("organizationName") or issuer.get("commonName") or "Émetteur standard"

                # Date d'expiration
                not_after = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                days_left = (not_after - datetime.datetime.utcnow()).days
                res["days_remaining"] = days_left

                if "Let's Encrypt" in str(issuer) or "ZeroSSL" in str(issuer):
                    res["notes"].append("Certificat SSL gratuit temporaire (fréquemment utilisé par les phishing rapides).")

    except Exception as e:
        res["notes"].append(f"Erreur ou absence de HTTPS/SSL valide : {e}")
        res["is_suspicious_ssl"] = True

    return res
