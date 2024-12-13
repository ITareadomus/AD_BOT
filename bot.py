from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging, passkey

# Token del bot fornito da BotFather
BOT_TOKEN = (passkey.TOKEN)

# ID del canale principale e dei canali secondari
SOURCE_CHANNEL = '-1002406576806'
CHANNEL_EXTRA_TIME = '-1002403326958'
CHANNEL_REMOTE_OPEN = '-1002402258086'
CHANNEL_OTHER_ISSUES = '-1002284946866'

# Configurazione logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text(
        "Ciao! Sono il bot per la gestione degli appartamenti. Inviami un messaggio "
        "con la tua richiesta e lo smisterò al canale appropriato."
    )

async def handle_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi dal canale principale e li smista nei canali appropriati."""
    if update.channel_post and update.channel_post.text:
        text = update.channel_post.text.lower()
        if any(keyword in text for keyword in ['tempo', 'pulire', 'extra']):
            await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"Richiesta ricevuta:\n{text}")
        elif any(keyword in text for keyword in ['apri', 'apertura', 'remoto']):
            await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"Richiesta ricevuta:\n{text}")
        else:
            await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"Segnalazione ricevuta:\n{text}")
    else:
        logger.warning("Messaggio dal canale non contiene testo.")

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte degli utenti e smista i messaggi nei canali appropriati."""
    user_message = update.message.text.lower()  # Ottieni il testo del messaggio inviato dall'utente

    if any(keyword in user_message for keyword in ['tempo', 'pulire', 'extra']):
        # Risponde al canale che richiede più tempo
        await context.bot.send_message(
            chat_id=CHANNEL_EXTRA_TIME,
            text=f"Risposta ricevuta: {user_message}"
        )
    elif any(keyword in user_message for keyword in ['apri', 'apertura', 'remoto']):
        # Risponde al canale che richiede apertura da remoto
        await context.bot.send_message(
            chat_id=CHANNEL_REMOTE_OPEN,
            text=f"Risposta ricevuta: {user_message}"
        )
    else:
        # Risponde al canale che segnala altri problemi
        await context.bot.send_message(
            chat_id=CHANNEL_OTHER_ISSUES,
            text=f"Risposta ricevuta: {user_message}"
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce errori ed eccezioni."""
    logger.error("Eccezione durante l'aggiornamento: %s", context.error)

def main():
    """Avvia il bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Gestore dei comandi
    application.add_handler(CommandHandler("start", start))

    # Gestore dei messaggi dal canale principale
    application.add_handler(MessageHandler(filters.Chat(chat_id=SOURCE_CHANNEL) & filters.UpdateType.CHANNEL_POST, handle_channel_message))

    # Gestore delle risposte degli utenti
    application.add_handler(MessageHandler(filters.TEXT, handle_response))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()