import os
import sys
import logging
from dotenv import load_dotenv

# Path setup to import backend modules
sys.path.append(os.path.dirname(__file__))

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from services import ai_service
from security import risk_engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("0xSentinelleBot")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛡️ **Bienvenue sur 0xSentinelle IA Bot !**\n\n"
        "Je suis votre assistant de biosécurité numérique et anti-scam.\n"
        "Envoyez-moi un message suspect, une URL ou un texte pour l'analyser instantanément !\n\n"
        "💡 **Exemple :** Envoyez un SMS suspect ou un lien comme `http://banque-securite-login.com`"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛡️ **Comment utiliser 0xSentinelle IA ?**\n\n"
        "• **Analyser un message/SMS :** Collez simplement le texte ici.\n"
        "• **Analyser une URL :** Envoyez directement le lien.\n"
        "• **Commande /start :** Revenir au menu principal."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def analyze_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # Message de prise en charge
    status_msg = await update.message.reply_text("🔍 *Analyse en cours par 0xSentinelle IA...*", parse_mode="Markdown")

    try:
        # Analyse via le moteur AI de 0xSentinelle
        ai_result = ai_service.analyze_text(user_text)
        signals = ai_result.get("signals", [])
        result = risk_engine.build_risk_result(
            signals=signals,
            scam_type=ai_result.get("scam_type", "indetermine"),
            explanation=ai_result.get("explanation", ""),
            recommendations=ai_result.get("recommendations", []),
            target_brand=None,
            original_input=user_text,
            ai_score=ai_result.get("score"),
            psychological_triggers=ai_result.get("psychological_triggers"),
            official_report=ai_result.get("official_report"),
        )

        level = result.get("level", "inconnu").upper()
        score = result.get("score", 0)
        scam_type = result.get("scam_type", "Non identifié")
        explanation = result.get("explanation", "Aucune explication fournie.")
        recommendations = result.get("recommendations", [])

        # Formater les indicateurs
        signals_text = ""
        if signals:
            signals_text = "\n\n⚠️ **Signaux de risque :**\n" + "\n".join([f"• {s}" for s in signals[:4]])

        # Formater les recommandations
        recs_text = ""
        if recommendations:
            recs_text = "\n\n💡 **Recommandations :**\n" + "\n".join([f"👉 {r}" for r in recommendations[:3]])

        # Couleur / Badge selon le niveau de risque
        risk_emoji = "🟢" if score < 30 else ("🟡" if score < 70 else "🔴")

        response = (
            f"🛡️ **0xSentinelle IA - Rapport d'Analyse**\n\n"
            f"{risk_emoji} **Niveau de Risque :** `{level}` ({score}/100)\n"
            f"🎯 **Type de menace :** `{scam_type}`\n\n"
            f"📝 **Explication :**\n{explanation}"
            f"{signals_text}"
            f"{recs_text}\n\n"
            f"🔒 *Scan before you trust — 0xSentinelle v2.0*"
        )

        try:
            await status_msg.edit_text(response, parse_mode="Markdown")
        except Exception as parse_err:
            logger.warning(f"Fallback plain text car erreur Markdown: {parse_err}")
            # Enlever la mise en forme markdown
            clean_resp = response.replace("**", "").replace("`", "").replace("*", "")
            await status_msg.edit_text(clean_resp)

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse : {e}")
        await status_msg.edit_text("❌ Une erreur est survenue lors de l'analyse par l'IA.")

def main():
    if not TOKEN:
        print("❌ Erreur : TELEGRAM_BOT_TOKEN manquant dans le fichier .env")
        sys.exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze_message_handler))

    print(f"🚀 Bot Telegram 0xSentinelle lancé avec succès (@deadbeef225bot) !")
    app.run_polling()

if __name__ == '__main__':
    main()
