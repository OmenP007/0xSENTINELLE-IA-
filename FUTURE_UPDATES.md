# 🚀 0xSentinelle IA — Feuille de Route & Futures Améliorations

> Document de planification technique — Hackathon GOMYCODE × NVIDIA

---

## 🔑 Ressources & Tokens Disponibles

| Ressource | Statut | Capacité |
|---|---|---|
| **Gemini API Key** | ✅ Actif | Text, Vision, Audio — quotas gratuits larges |
| **NVIDIA L40S 48GB VRAM** | ✅ Actif (Brev) | Mistral 7B, Llama 3, fine-tuning possible |
| **Crédit Brev.dev** | ✅ $100 restants | ~94h de GPU à $1.06/hr |
| **ChromaDB RAG local** | ✅ Actif | Illimité (local) |
| **Telegram Bot Token** | ❌ Manquant | Gratuit sur @BotFather |
| **Playwright / Puppeteer** | ❌ Non installé | Gratuit (pip install) |

---

## 🔴 Priorité 1 — Faisable Maintenant avec tes Tokens

### 🔍 1. Extraction Complète du Texte de la Page
**Tokens requis :** Aucun — httpx déjà installé  
**Effort :** ~30 minutes de code  
**Impact :** L'IA lit le contenu complet de la page suspecte au lieu du seul titre

```python
# Ajout dans fetch_live_page_content() — url_service.py
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, "html.parser")
visible_text = soup.get_text(separator=" ", strip=True)[:2000]
# → Transmis au LLM pour analyse contextuelle complète
```

> ✅ **Gemini API peut lire ce texte** — ton quota Gemini couvre largement ça.

---

### 📱 2. Blacklist de Numéros Arnaqueurs Connus
**Tokens requis :** Aucun — base locale JSON  
**Effort :** ~1 heure  
**Impact :** Vérification instantanée si un numéro `+225 07...` est signalé

```
POST /analyze/phone → { "numero": "+22507XXXXXXXX" }
→ { "score": 95, "signalements": 12, "type": "Faux agent Orange Money" }
```

> ✅ **0 token consommé** — pure base de données locale enrichie par la communauté.

---

### 📄 3. Rapport PDF Officiel PLCC
**Tokens requis :** Aucun — `reportlab` (pip install)  
**Effort :** ~1 heure  
**Impact :** Génère un PDF de plainte pré-rempli pour la PLCC CI

```
POST /report/generate → PDF avec : URL, screenshot, score, recommandations, contacts PLCC
```

> ✅ **Gratuit** — aucun token nécessaire, juste une dépendance Python.

---

## 🟠 Priorité 2 — Faisable avec Tokens Existants + Petite Config

### 📸 4. Screenshot Automatique des Pages Suspectes
**Tokens requis :** `pip install playwright` (gratuit) + **Gemini Vision** (déjà disponible ✅)  
**Effort :** ~2 heures  
**Impact :** Détecte visuellement les faux logos Wave/Orange/MTN copiés

```
URL → Playwright prend screenshot → Gemini Vision analyse l'image
→ "Faux site Wave détecté : logo copié, formulaire de vol d'OTP présent"
```

> ✅ **Gemini Vision inclus dans ta clé API** — aucun coût supplémentaire dans les quotas gratuits.

---

### 🤖 5. Bot Telegram Anti-Arnaque
**Tokens requis :** **Token Telegram Bot** (gratuit sur @BotFather) + ta clé Gemini  
**Effort :** ~2 heures  
**Impact :** Démultiplication massive — les gens transfèrent un message → réponse en 5 secondes

```
Utilisateur → Forward message suspect au bot Telegram
Bot → Appel backend 0xSentinelle → Score + explication en français ivoirien
```

> ✅ **Gratuit** — Telegram Bot API est 100% gratuit. Token obtenu en 2 minutes via @BotFather.

> ⚠️ Nécessite que ton backend soit accessible publiquement (ngrok ou déploiement).

---

### 🎙️ 6. Analyse Vocale des Appels Suspects
**Tokens requis :** **Gemini Audio** (inclus dans ta clé ✅) ou Whisper sur ton GPU L40S  
**Effort :** ~3 heures  
**Impact :** Transcrire et analyser un enregistrement d'un faux agent Mobile Money

```
POST /analyze/audio → fichier .mp3/.wav
→ Transcription Whisper GPU → Analyse arnaque → Score de risque
```

> ✅ **Ton GPU L40S peut faire tourner Whisper large-v3 gratuitement** — 0 token API consommé.

---

## 🟡 Priorité 3 — Nécessite Budget ou Ressources Supplémentaires

### 📊 7. Dashboard Admin — Carte des Arnaques en Temps Réel
**Tokens requis :** Aucun  
**Effort :** ~1 semaine (frontend React + backend stats)  
**Impact :** Visualiser les arnaques tendance en CI, les domaines les plus signalés

> ✅ **Faisable avec tes ressources actuelles** — juste du temps de développement.

---

### 🧠 8. Fine-Tuning de Mistral sur Données Ivoiriennes
**Tokens requis :** **GPU L40S** (déjà disponible ✅) + dataset d'entraînement  
**Effort :** ~2-3 jours (collecte données + entraînement)  
**Coût estimé :** ~$20-40 en GPU Brev (~20-40h à $1.06/hr)

```
Dataset : 500-1000 exemples de vrais messages d'arnaques CI labelisés
→ Fine-tuning LoRA sur Mistral 7B via ton L40S
→ Modèle 0xSentinelle-Mistral-CI spécialisé
```

> ⚠️ **Consomme du crédit Brev** — prévoir ~$30 de budget GPU pour un bon fine-tuning.

---

### 📲 9. Application Mobile Android
**Tokens requis :** Aucun token supplémentaire  
**Effort :** ~2-3 semaines (React Native)  
**Impact :** Analyse des SMS entrants directement sur le téléphone

> ⚠️ **Hors scope Hackathon** — projet moyen terme.

---

### 🏘️ 10. Signalement Communautaire
**Tokens requis :** Base de données (PostgreSQL ou Supabase gratuit)  
**Effort :** ~1 semaine  
**Impact :** Les utilisateurs valident/signalent → enrichissement automatique du RAG

> ✅ **Supabase Free Tier** — 500MB gratuit, suffisant pour démarrer.

---

## 🗓️ Planning Recommandé

```
Semaine 1 (maintenant) :
  ✅ Extraction texte complet de page    → 30min, 0 token
  ✅ Blacklist numéros                   → 1h,    0 token
  ✅ Rapport PDF PLCC                    → 1h,    0 token

Semaine 2 :
  🔧 Screenshot Playwright + Vision IA  → 2h, Gemini Vision ✅
  🔧 Bot Telegram                        → 2h, Token gratuit @BotFather

Mois 2 :
  📊 Dashboard carte arnaques           → 1 semaine
  🎙️ Analyse audio appels              → 3h, GPU L40S ✅

Mois 3 :
  🧠 Fine-tuning Mistral CI             → $30 GPU Brev
  🏘️ Signalement communautaire          → Supabase gratuit
```

---

## 💰 Résumé Budget Token

| Amélioration | Coût Token | Faisable maintenant ? |
|---|---|---|
| Extraction texte complet | 0€ | ✅ Oui |
| Blacklist numéros | 0€ | ✅ Oui |
| Rapport PDF PLCC | 0€ | ✅ Oui |
| Screenshot + Vision IA | 0€ (quota Gemini) | ✅ Oui |
| Bot Telegram | 0€ | ✅ Oui (juste le token) |
| Analyse vocale Whisper | 0€ (GPU L40S) | ✅ Oui |
| Dashboard analytics | 0€ | ✅ Oui (temps dev) |
| Fine-tuning Mistral | ~$30 GPU | ⚠️ Budget |
| App Mobile Android | 0€ | ⚠️ Temps |
| Signalement communautaire | 0€ | ✅ Supabase gratuit |

> 💡 **80% des améliorations sont réalisables avec tes ressources actuelles !**
> Seul le fine-tuning consomme du crédit GPU ($30 sur tes $100 disponibles).
