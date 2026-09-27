# 🛡️ 0xSentinelle IA — Contexte Côte d'Ivoire 🇨🇮

**Scan before you trust.** — *Solution IA Multi-Agent de Protection contre les Arnaques Numériques & le Broutage (Hackathon GOMYCODE × NVIDIA)*

---

## 🚀 Nouveautés & Fonctionnalités

### 🧠 1. IA Multi-Langue & Contexte Côte d'Ivoire
- **Langues gérées :** Français, **Nouchi** (argot ivoirien), **Dioula**, Anglais et messages mixtes.
- **Services locaux pris en compte :** Orange Money CI, MTN Mobile Money CI, Wave CI, Moov Money CI, Free Money, SIB, Ecobank, CEPICI, CNPS.
- **Détection des arnaques typiques CI :** Faux concours Mobile Money, broutage / escroquerie sentimentale, faux recrutements & contrats de mines/ONG, arnaque au colis/douane, faux investissements crypto/Ponzi.
- **Contacts officiels de signalement :** ARTCI & Plateforme de Lutte Contre la Cybercriminalité (PLCC CI - +225 27 20 25 98 72).

### 🔍 2. Inspection Approfondie des URLs (Deep URL Breakdown)
- **Détection des trouvailles techniques :**
  - Validation du protocole (HTTP non sécurisé vs HTTPS avec SSL).
  - Détection d'adresses IP brutes (ex: `http://192.168.1.1/wave`).
  - Filtrage des TLD à haut risque (`.xyz`, `.top`, `.online`, `.site`, `.cc`, `.tk`).
  - Repérage des faux sous-domaines d'usurpation (ex: `wave.kdo.com` -> vrai domaine = `kdo.com`).
  - Détection de typosquatting par distance de Levenshtein (ex: `orangemoney-ci`).
  - Analyse des mots-clés de hameçonnage et formulaires de connexion/OTP suspects dans le chemin de l'URL.

### 🧩 3. Extension de Navigateur (WhatsApp Web & Facebook) — `extension-chrome/`
- **WhatsApp Web (`web.whatsapp.com`) :** Injection automatique d'un bouton **🛡️ Scan IA** à côté des messages + surlignage visuel des liens suspects.
- **Facebook / Messenger (`facebook.com`) :** Scan des messages Marketplace, posts et commentaires frauduleux.
- **Alerte visuelle instantanée :** Affichage d'une bannière rouge **🔴 RISQUE CRITIQUE** directement sur la page avec le score et les recommandations.
- **Popup Extension :** Fenêtre d'analyse manuelle rapide de textes ou d'URLs en un clic.

### 🛡️ 4. Moteur de Risque Hybride (`risk_engine.py`)
- Mappage universel des signaux (FR & EN).
- Garde-fou de sécurité : Plancher minimum garanti (>= 75-85/100) si le type détecté est du `phishing`, `broutage`, `faux_concours`, etc.

---

## 💻 Installation & Démarrage Rapide

### 1. Démarrer le Backend & Frontend
```bash
# Rendre le script d'initialisation exécutable
chmod +x start.sh

# Lancer le projet complet (Backend FastAPI + Frontend React)
./start.sh
```
- **Frontend React :** `http://localhost:3000`
- **API Backend :** `http://localhost:8000`
- **Docs Swagger :** `http://localhost:8000/docs`

---

### 2. Installer l'Extension dans Firefox 🦊

1. Ouvre Firefox et tape **`about:debugging#/runtime/this-firefox`** dans la barre d'adresse.
2. Clique sur le bouton **"Charger un module complémentaire temporaire..."** (*Load Temporary Add-on...*).
3. Rends-toi dans le dossier de ton projet, entre dans **`extension-chrome/`** et sélectionne le fichier **`manifest.json`**.
4. L'extension **0xSentinelle Shield 🇨🇮** s'active immédiatement !
5. Ouvre **WhatsApp Web** (`web.whatsapp.com`) ou **Facebook** pour voir les boutons **🛡️ Scan IA** et les détections de liens.

*(Pour Chrome, Brave ou Edge : accède à `chrome://extensions`, active le mode développeur, et clique sur "Charger l'extension non empaquetée" en sélectionnant le dossier `extension-chrome/`)*.


---

## 📁 Structure du Projet

```
0xSentinelle/
├── backend/
│   ├── main.py
│   ├── routes/              (analyze.py, image.py, url.py, voice.py)
│   ├── services/            (ai_service.py, url_service.py, voice_service.py, trusted_sources.py)
│   ├── security/            (risk_engine.py)
│   └── models/              (schemas.py)
├── frontend-react/          (App.jsx, components/, Vite + Framer Motion)
├── extension-chrome/        (manifest.json, content_script.js, background.js, popup.html, styles.css)
├── start.sh
├── requirements.txt
└── README.md
```

---

## 📡 Endpoints API

| Méthode | Route | Description |
|---|---|---|
| POST | `/analyze/text` | Analyse un message texte (FR, Nouchi, Dioula, EN) |
| POST | `/analyze/image` | Analyse une capture d'écran SMS/WhatsApp (Vision IA) |
| POST | `/analyze/url` | Inspection approfondie d'URL (Trouvailles techniques & Typosquatting) |
| POST | `/analyze/voice` | Transcrit et analyse une note vocale d'arnaque |
| POST | `/analyze/reply` | Génère une réponse prudente à renvoyer au brouteur |
| GET | `/health` | Statut du service |
