# 🛡️ 0xSentinelle IA — Contexte Côte d'Ivoire 🇨🇮

**Scan before you trust.** — *Solution IA Multi-Agent & RAG de Protection contre les Arnaques Numériques & le Broutage (Hackathon GOMYCODE × NVIDIA)*

---

## 🚀 Fonctionnalités & Architecture Complète

### 🚀 1. Inférence GPU NVIDIA Souveraine (Brev.dev — NVIDIA L40S 48GB VRAM)
- **Hébergement LLM Dédié :** Inférence ultra-rapide (< 100ms) avec **Mistral 7B / Llama 3** hébergée sur GPU NVIDIA via **Brev.dev**.
- **Basculement Hybride Automatique :** Bascule transparente entre le GPU NVIDIA Brev et l'API Gemini / RAG local.
- **Accès Open WebUI :** Interface conversationnelle de test disponible via tunnel Brev (`brev port-forward wispy-bronze-snipe --port 3000:3000` → http://localhost:3000).

### 🧠 2. Moteur RAG & Vector DB ChromaDB (`backend/rag/`)
- **Base de Connaissances Spécialisée :** Micro-chunks (400–800 tokens) sur les arnaques ivoiriennes (Orange Money CI, Wave CI, MTN MoMo, Moov, CEPICI, CNPS, ARTCI, PLCC).
- **Indexation Vectorielle ChromaDB :** Recherche sémantique ciblée (seuls les 2-3 passages pertinents sont transmis au LLM).
- **Ingestion Dynamique (`POST /upload/knowledge`) :** Possibilité d'ingérer de nouvelles bases Markdown `.md` à tout moment.

### 🕷️ 3. OpenClaw — Crawler & Scraper Web Temps Réel
- **Visite Réelle des URLs :** Le scraper visite automatiquement chaque URL suspecte soumise (`fetch_live_page_content`).
- **Inspection HTML du DOM :** Analyse le code source de la page pour détecter les éléments de piratage.
- **Détection des Formulaires Malveillants :** Détecte les champs de saisie de mot de passe, codes OTP/PIN et numéros de téléphone sur les fausses pages.
- **Suivi des Redirections :** Suit les chaînes de redirections pour démasquer les liens raccourcis (bit.ly, etc.).
- **Typosquatting & TLD :** Détection automatique des domaines qui imitent Wave, Orange, MTN, Djamo via distance de Levenshtein.

### 💬 4. Analyse Globale de Conversation (WhatsApp & Facebook Marketplace)
- **Scan de Fil de Discussion Complet :** Détection des scénarios de faux vendeurs, demandes d'acomptes Mobile Money par avance, et brouteurs sentimentaux.
- **Rapport de Signalement Officiel :** Génération automatique de modèles de plaintes pré-remplis pour la **PLCC CI** (+225 27 20 25 98 72) et l'**ARTCI**.

### 🦊 5. Extension de Navigateur Firefox & Chrome v2.1 (`extension-chrome/`)
- **Intégration WhatsApp Web & Facebook :** Injection de boutons d'analyse **🛡️ Scan IA**, bannières d'alerte et surlignage des liens dangereux.
- **Analyse par Message :** Bouton Scan IA sur chaque bulle de conversation WhatsApp.
- **Analyse de Conversation Entière :** Détection automatique des discussions à risque (mots-clés vendeur, liens suspects) avec bouton d'analyse globale.
- **Analyse d'URL depuis la Popup :** La popup détecte automatiquement si le texte collé est une URL ou un message.
- **Indicateur Statut Backend :** La popup affiche en temps réel si le backend FastAPI est connecté ou hors ligne.
- **Design Vectoriel Épuré :** Icônes SVG Lucide modernes, sans dépendance d'émojis texte.
- **Compatibilité Firefox & Chrome/Brave :** Détection automatique de l'API (`browser` vs `chrome`).

### 📱 6. Blacklist Communautaire de Numéros CI (`backend/services/phone_service.py`)
- **Normalisation Automatique :** Formate tous les numéros au format international ivoirien `+22507...`.
- **Scoring & Alertes :** Vérifie le numéro contre la base de données JSON locale, calcule le score de risque et retourne l'historique des signalements (type d'escroquerie et région).
- **API de Signalement :** Permet aux citoyens de signaler un nouveau numéro d'arnaqueur en temps réel (`POST /report/phone`).

### 📄 7. Générateur de Rapport PDF Officiel PLCC (`backend/services/pdf_service.py`)
- **Format Officiel PLCC / DITT :** Génère un dossier de signalement PDF prêt à soumettre à la Plateforme de Lutte Contre la Cybercriminalité de Côte d'Ivoire.
- **Preuves Techniques & Numéro de Référence :** Génère une référence unique `SENT-PLCC-YYYYMMDDHHMMSS`, le score de risque, la synthèse de l'IA, et les conseils de sécurité.

### 🔒 8. Inspection Domaine & Certificat SSL/TLS (`backend/services/domain_service.py`)
- **Analyse Cryptographique HTTPS :** Vérifie la présence d'un certificat SSL/TLS valide, l'émetteur (Let's Encrypt / ZeroSSL) et la durée d'expiration restante.

### 👁️ 9. Détection Multimodale Deepfakes & Images IA (`backend/services/ai_service.py`)
- **Vision IA Avancée :** Détecte les artefacts d'images synthétiques, les visages générés par IA, les cartes d'identité contrefaites et l'usurpation visuelle de logos.

---

## 💻 Installation & Démarrage Rapide

### 1. Démarrer le Backend & Frontend React
```bash
# Rendre le script d'initialisation exécutable
chmod +x start.sh

# Lancer le projet complet (Backend FastAPI + Frontend React)
./start.sh
```
- **Frontend React :** `http://localhost:5173`
- **API Backend :** `http://localhost:8000`
- **Statut RAG :** `http://localhost:8000/rag/status`
- **Docs Swagger :** `http://localhost:8000/docs`

---

### 2. Configurer le GPU NVIDIA Brev (`.env`)
```env
GEMINI_API_KEY=votre_cle_gemini
BREV_OLLAMA_HOST=http://216.81.248.197:11434
BREV_MODEL=mistral
```

**Accès Open WebUI (interface test GPU) :**
```bash
brev port-forward wispy-bronze-snipe --port 3000:3000
# Puis ouvrir → http://localhost:3000
```

---

### 3. Installer l'Extension dans Firefox 🦊

1. Ouvre Firefox et tape **`about:debugging#/runtime/this-firefox`** dans la barre d'adresse.
2. Clique sur **"Charger un module complémentaire temporaire..."**.
3. Rends-toi dans `extension-chrome/` et sélectionne **`manifest.json`**.
4. L'extension **0xSentinelle Shield 🇨🇮** est opérationnelle sur **WhatsApp Web** et **Facebook** !

**Pour recharger après une mise à jour :** `about:debugging` → bouton **Recharger** sur l'extension.

### 4. Installer l'Extension dans Chrome / Brave
1. Ouvre `chrome://extensions/`
2. Active le **Mode développeur** (en haut à droite).
3. Clique **"Charger l'extension non empaquetée"** → sélectionne le dossier `extension-chrome/`.

---

## 📁 Structure du Projet

```
0xSentinelle/
├── backend/
│   ├── main.py
│   ├── routes/              (analyze.py, upload.py, image.py, url.py, voice.py)
│   ├── services/            (ai_service.py, rag_service.py, ollama_service.py, url_service.py, voice_service.py)
│   ├── security/            (risk_engine.py)
│   └── rag/                 (knowledge.md, documents.json, chroma/)
├── frontend-react/          (App.jsx, components/, Lucide React + Framer Motion)
├── extension-chrome/
│   ├── manifest.json        (v2.1 — Manifest V3, host_permissions élargis)
│   ├── background.js        (Service Worker — ANALYZE_TEXT/URL/CONVERSATION/IMAGE)
│   ├── content_script.js    (Injection WhatsApp Web & Facebook, SVG Lucide)
│   ├── popup.html           (Interface popup avec indicateur statut backend)
│   ├── popup.js             (Fallback emoji, runtime.lastError, health check)
│   └── styles.css           (Thème sombre, bannières risque, modales)
├── start.sh
├── requirements.txt
└── README.md
```

---

## 📡 Endpoints API Principal

| Méthode | Route | Description |
|---|---|---|
| POST | `/analyze/text` | Analyse un message texte (FR, Nouchi, Dioula, EN) |
| POST | `/analyze/conversation` | Diagnostic d'un échange complet de discussion |
| POST | `/analyze/url` | Inspection d'URL + OpenClaw Crawler HTML temps réel |
| POST | `/analyze/image` | Analyse de capture d'écran SMS/WhatsApp (Vision IA) |
| POST | `/upload/knowledge` | Ingestion dynamique de fichiers Markdown RAG (.md) |
| GET  | `/rag/status` | Métriques & statut de la Vector DB ChromaDB |
| GET  | `/health` | Statut du service + GPU Brev |

---

## 🔒 Flux de Décision IA

```
Message / URL / Image entrant
        ↓
  [risk_engine.py] → Score déterministe (0-100)
        ↓
  [rag_service.py] → Contexte sémantique ChromaDB
        ↓
  [ollama_service.py] → GPU NVIDIA L40S Brev (Mistral)
        ↑ fallback si GPU indisponible
  [ai_service.py]  → Gemini API
        ↓
  Réponse JSON : score, level, explanation, recommendations, official_report
```

---

## 🆘 Contacts Officiels Anti-Arnaque CI

| Organisme | Contact |
|---|---|
| PLCC (Plateforme de Lutte contre la Cybercriminalité) | +225 27 20 25 98 72 |
| ARTCI | artci.ci |
| Police Nationale CI | 100 / 110 |
