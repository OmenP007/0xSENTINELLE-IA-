# 🛡️ 0xSentinelle IA — Contexte Côte d'Ivoire 🇨🇮

**Scan before you trust.** — *Solution IA Multi-Agent & RAG de Protection contre les Arnaques Numériques & le Broutage (Hackathon GOMYCODE × NVIDIA)*

---

## 🚀 Fonctionnalités & Architecture Complète

### 🚀 1. Inférence GPU NVIDIA Souveraine (Brev.dev — NVIDIA L40S 44GB VRAM)
- **Hébergement LLM Dédié :** Inférence ultra-rapide (< 100ms) avec **Mistral 7B / Llama 3** hébergée sur GPU NVIDIA via **Brev.dev**.
- **Basculement Hybride Automatique :** Bascule transparente entre le GPU NVIDIA Brev et l'API Gemini / RAG local.

### 🧠 2. Moteur RAG & Vector DB ChromaDB (`backend/rag/`)
- **Base de Connaissances Spécialisée :** Micro-chunks (400–800 tokens) sur les arnaques ivoiriennes (Orange Money CI, Wave CI, MTN MoMo, Moov, CEPICI, CNPS, ARTCI, PLCC).
- **Indexation Vectorielle ChromaDB :** Recherche sémantique ciblée (seuls les 2-3 passages pertinents sont transmis au LLM).
- **Ingestion Dynamique (`POST /upload/knowledge`) :** Possibilité d'ingérer de nouvelles bases Markdown `.md` à tout moment.

### 🕷️ 3. OpenClaw / Crawler & Scraper Web Temps Réel
- **Inspection HTML du DOM :** Visite automatique des URLs suspectes en tâche de fond (`fetch_live_page_content`).
- **Détection des Formulaires de Piratage :** Détecte les champs masqués de saisie de mot de passe, codes OTP, PIN et numéros de téléphone sur les fausses pages Web.

### 💬 4. Analyse Globale de Conversation (WhatsApp & Facebook Marketplace)
- **Scan de Fil de Discussion Complet :** Détection des scénarios de faux vendeurs, demandes d'acomptes Mobile Money par avance, et brouteurs sentimentaux.
- **Rapport de Signalement Officiel :** Génération automatique de modèles de plaintes pré-remplis pour la **PLCC CI** (+225 27 20 25 98 72) et l'**ARTCI**.

### 🦊 5. Extension de Navigateur Firefox & Chrome (`extension-chrome/`)
- **Integration WhatsApp Web & Facebook :** Injection de boutons d'analyse **🛡️ Scan IA**, bannières d'alerte et surlignage des liens dangereux.
- **Design Vectoriel Épuré :** Icônes SVG modernes (Lucide) sans dépendance d'émojis texte.

---

## 💻 Installation & Démarrage Rapide

### 1. Démarrer le Backend & Frontend React
```bash
# Rendre le script d'initialisation exécutable
chmod +x start.sh

# Lancer le projet complet (Backend FastAPI + Frontend React)
./start.sh
```
- **Frontend React :** `http://localhost:3000`
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

---

### 3. Installer l'Extension dans Firefox 🦊

1. Ouvre Firefox et tape **`about:debugging#/runtime/this-firefox`** dans la barre d'adresse.
2. Clique sur le bouton **"Charger un module complémentaire temporaire..."** (*Load Temporary Add-on...*).
3. Rends-toi dans le dossier du projet, entre dans **`extension-chrome/`** et sélectionne le fichier **`manifest.json`**.
4. L'extension **0xSentinelle Shield 🇨🇮** est immédiatement opérationnelle sur **WhatsApp Web** et **Facebook** !

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
├── extension-chrome/        (manifest.json, content_script.js, background.js, popup.html, styles.css)
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
| GET | `/rag/status` | Métriques & statut de la Vector DB ChromaDB |
| GET | `/health` | Statut du service |
