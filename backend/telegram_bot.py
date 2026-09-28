import os
import sys
import logging
import re
import time
from dotenv import load_dotenv

# Path setup to import backend modules
sys.path.append(os.path.dirname(__file__))

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from services import ai_service, url_service, phone_service
from security import risk_engine

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("0xSentinelleBot")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Patterns de détection automatique
URL_PATTERN = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:com|net|org|ci|xyz|info|top|site|store|online|vip|app|dev)(?:/[^\s]*)?)",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(\+?225[\s\.\-]?0?[157][0-9]{2}[\s\.\-]?[0-9]{2}[\s\.\-]?[0-9]{2}[\s\.\-]?[0-9]{2}|0[157][0-9]{8})"
)

USER_REQUEST_TIMES = {}
MAX_REQUESTS_PER_WINDOW = 6
WINDOW_SECONDS = 30


def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    user_times = USER_REQUEST_TIMES.get(user_id, [])
    valid_times = [t for t in user_times if now - t < WINDOW_SECONDS]
    if len(valid_times) >= MAX_REQUESTS_PER_WINDOW:
        return False
    valid_times.append(now)
    USER_REQUEST_TIMES[user_id] = valid_times
    return True


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ **Bienvenue sur 0xSentinelle IA — Gardien de Groupe & Anti-Arnaques 🇨🇮**\n\n"
        "Je suis votre modérateur de sécurité IA contre le broutage, le phishing et les arnaques Mobile Money (Wave, Orange, MTN, Moov).\n\n"
        "👥 **Comment m'utiliser dans un Groupe :**\n"
        "1. Ajoutez-moi à votre groupe Telegram : `@deadbeef225bot`\n"
        "2. Donnez-moi la permission de lire les messages (Modérateur).\n"
        "3. Je surveillerai automatiquement les **liens suspects** et **numéros d'arnaqueurs** publiés par les membres !\n\n"
        "⚡ **Commandes utiles :**\n"
        "• `/check <texte / URL / numéro>` : Analyser un élément spécifique.\n"
        "• Répondre à un message avec `/check` : Analyser directement le message d'un membre.\n"
        "• `/help` : Guide complet d'utilisation."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛡️ **0xSentinelle IA — Guide du Modérateur de Groupe**\n\n"
        "🟢 **Sûr / Aucun signal** : Aucun indicateur de risque majeur.\n"
        "🟡 **Suspect** (30-59/100) : Prudence recommandée.\n"
        "🟠 **Risque Élevé** (60-79/100) : Plusieurs signaux de phishing/usurpation.\n"
        "🔴 **Danger Confirmé** (80-100/100) : Typosquatting / Numéro blacklisté.\n\n"
        "💡 **Utilisation dans les groupes :**\n"
        "• Modération automatique des URLs & Numéros.\n"
        "• Commande `/check` disponible pour tous les membres.\n"
        "• Détection des catégories : Wave, Orange Money, MTN MoMo, Faux Recrutement, Phishing Bancaire, Faux Concours."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


def _get_risk_badge(score: int) -> tuple[str, str]:
    if score >= 80:
        return "🔴 DANGER / PHISHING CONFIRMÉ", "🔴"
    elif score >= 60:
        return "🟠 RISQUE ÉLEVÉ", "🟠"
    elif score >= 30:
        return "🟡 SUSPECT", "🟡"
    else:
        return "🟢 SÛR / FAIBLE RISQUE", "🟢"


async def process_analysis(text: str) -> str:
    """Analyse un texte (URL, Téléphone ou Message brut) et produit un rapport Markdown."""
    urls = URL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)

    # 1. Analyse si c'est une URL
    if urls:
        raw_url = urls[0][0] if isinstance(urls[0], tuple) else urls[0]
        url_res = url_service.analyze_url(raw_url)
        signals = url_res.get("signals", [])
        scam_type = "Phishing / Usurpation Web" if "brand_impersonation" in signals else "Lien Web Suspect"
        
        # Enrichissement IA
        ai_res = ai_service.analyze_text(f"URL: {raw_url}. Notes: {' '.join(url_res.get('notes', []))}")
        score = max(url_res.get("score", 0), ai_res.get("score", 0))
        if url_res.get("typosquatting_detected"):
            score = max(score, 85)

        level_text, emoji = _get_risk_badge(score)
        notes = url_res.get("notes", [])
        recs = ai_res.get("recommendations", ["Ne cliquez pas sur ce lien avant vérification."])

        recs_str = "\n".join([f"👉 {r}" for r in recs[:3]])
        notes_str = "\n".join([f"• {n}" for n in notes[:4]]) if notes else "• Lien analysé avec succès."

        return (
            f"🚨 **ALERTE SÉCURITÉ 0xSENTINELLE — URL**\n\n"
            f"🔗 **Lien analysé :** `{raw_url}`\n"
            f"{emoji} **Statut :** `{level_text}` ({score}/100)\n"
            f"🎯 **Catégorie :** `{scam_type}`\n\n"
            f"📝 **Éléments détectés :**\n{notes_str}\n\n"
            f"💡 **Recommandation :**\n{recs_str}\n\n"
            f"🛡️ *Scan before you trust — 0xSentinelle v2.0*"
        )

    # 2. Analyse si c'est un numéro de téléphone
    if phones:
        raw_phone = phones[0][0] if isinstance(phones[0], tuple) else phones[0]
        phone_res = phone_service.check_phone_blacklist(raw_phone)
        score = phone_res.get("score", 0)
        found = phone_res.get("found_in_blacklist", False)

        if found:
            score = max(score, 80)

        level_text, emoji = _get_risk_badge(score)
        signalements = phone_res.get("signalements", 0)
        type_arnaque = phone_res.get("type_arnaque", "Usurpation / Arnaque Mobile Money")

        msg_body = (
            f"📞 **ALERTE SÉCURITÉ 0xSENTINELLE — NUMÉRO**\n\n"
            f"📱 **Numéro :** `{phone_res.get('numero', raw_phone)}`\n"
            f"{emoji} **Statut :** `{level_text}` ({score}/100)\n"
            f"🎯 **Historique :** `{type_arnaque}` ({signalements} signalement(s))\n\n"
            f"📝 **Message d'alerte :**\n{phone_res.get('message', '')}\n\n"
            f"❌ **Conseil de Sécurité :**\n"
            f"• Ne donnez JAMAIS votre code secret PIN, code OTP ou mot de passe.\n"
            f"• Ne faites aucun transfert d'argent sans confirmation officielle.\n\n"
            f"🛡️ *Protection Anti-Arnaque Côte d'Ivoire 🇨🇮*"
        )
        return msg_body

    # 3. Analyse de message texte général
    ai_res = ai_service.analyze_text(text)
    signals = ai_res.get("signals", [])
    result = risk_engine.build_risk_result(
        signals=signals,
        scam_type=ai_res.get("scam_type", "indetermine"),
        explanation=ai_res.get("explanation", ""),
        recommendations=ai_res.get("recommendations", []),
        original_input=text,
        ai_score=ai_res.get("score"),
        psychological_triggers=ai_res.get("psychological_triggers"),
        official_report=ai_res.get("official_report"),
    )

    score = result.get("score", 0)
    level_text, emoji = _get_risk_badge(score)
    scam_type = result.get("scam_type", "Non identifié")
    explanation = result.get("explanation", "Aucune explication disponible.")
    recs = result.get("recommendations", [])

    signals_text = ""
    if signals:
        signals_text = "\n\n⚠️ **Signaux de risque :**\n" + "\n".join([f"• {s}" for s in signals[:4]])

    recs_text = ""
    if recs:
        recs_text = "\n\n💡 **Recommandation :**\n" + "\n".join([f"👉 {r}" for r in recs[:3]])

    return (
        f"🛡️ **0xSentinelle IA — Rapport de Modération**\n\n"
        f"{emoji} **Statut :** `{level_text}` ({score}/100)\n"
        f"🎯 **Menace potentielle :** `{scam_type}`\n\n"
        f"📝 **Synthèse :**\n{explanation}"
        f"{signals_text}"
        f"{recs_text}\n\n"
        f"🔒 *Scan before you trust — 0xSentinelle v2.0*"
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /check pour analyser un texte explicite ou un message répondu."""
    if not update.message:
        return

    user_id = update.effective_user.id
    if not check_rate_limit(user_id):
        await update.message.reply_text("⏱️ **Limite de requêtes atteinte.** Veuillez patienter 30s.")
        return

    # Vérifier si c'est une réponse à un message
    target_text = ""
    if update.message.reply_to_message and update.message.reply_to_message.text:
        target_text = update.message.reply_to_message.text
    elif context.args:
        target_text = " ".join(context.args)
    else:
        await update.message.reply_text(
            "💡 **Utilisation de /check :**\n"
            "• `/check https://site-suspect.com`\n"
            "• `/check +2250700000000`\n"
            "• Répondez à n'importe quel message du groupe en écrivant `/check`.",
            parse_mode="Markdown",
        )
        return

    status_msg = await update.message.reply_text("🔍 *Analyse 0xSentinelle en cours...*", parse_mode="Markdown")
    try:
        response_md = await process_analysis(target_text)
        await status_msg.edit_text(response_md, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Erreur /check: {e}")
        await status_msg.edit_text("❌ Erreur lors de l'analyse du message.")


async def auto_group_monitor_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Moniteur automatique pour les groupes Telegram : scanne automatiquement les URLs & Numéros."""
    if not update.message or not update.message.text:
        return

    text = update.message.text
    is_group = update.message.chat.type in ["group", "supergroup"]

    urls = URL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)

    # Si c'est un groupe et qu'aucun lien/numéro n'est détecté, ignorer pour ne pas polluer la discussion
    if is_group and not urls and not phones:
        return

    user_id = update.effective_user.id
    if not check_rate_limit(user_id):
        return

    try:
        response_md = await process_analysis(text)

        if not is_group:
            status_msg = await update.message.reply_text("🔍 *Analyse 0xSentinelle en cours...*", parse_mode="Markdown")
            await status_msg.edit_text(response_md, parse_mode="Markdown")
        else:
            # En groupe : alerter seulement si le risque est >= 30 ou si numéro/url suspecte
            if "🟢 SÛR" not in response_md or urls or phones:
                await update.message.reply_text(response_md, parse_mode="Markdown", reply_to_message_id=update.message.message_id)

    except Exception as e:
        logger.error(f"Erreur auto_group_monitor: {e}")


def main():
    if not TOKEN:
        print("❌ Erreur : TELEGRAM_BOT_TOKEN manquant dans le fichier .env")
        sys.exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), auto_group_monitor_handler))

    print(f"🚀 Bot Telegram 0xSentinelle Gardien de Groupe lancé avec succès (@deadbeef225bot) !")
    app.run_polling()


if __name__ == "__main__":
    main()

