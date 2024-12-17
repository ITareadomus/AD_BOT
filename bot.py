from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging, passkey

# Token del bot fornito da BotFather
BOT_TOKEN = (passkey.TOKEN)

# ID dei canali di smistamento
CHANNEL_EXTRA_TIME = '-1002403326958'
CHANNEL_REMOTE_OPEN = '-1002402258086'
CHANNEL_OTHER_ISSUES = '-1002350584252'

# Configurazione logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dizionario per tracciare gli utenti che inviano richieste
user_requests = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text(
        "Ciao! Sono il bot per la gestione degli appartamenti. Inviami un messaggio "
        "con la tua richiesta e lo smisterò al canale appropriato."
    )

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte degli amministratori e le inoltra all'utente originale tramite il bot."""
    if update.channel_post:
        channel_message = update.channel_post

        # Controlla se il messaggio è una risposta
        if channel_message.reply_to_message and channel_message.reply_to_message.message_id in user_requests:
            original_message_id = channel_message.reply_to_message.message_id
            original_user_id = user_requests[original_message_id]

            # Invia la risposta all'utente originario
            await context.bot.send_message(
                chat_id=original_user_id,
                text=f"{channel_message.text}"
            )
        else:
            # Invia un messaggio di avviso nel canale che la risposta non è stata inviata correttamente
            await context.bot.send_message(
                chat_id=update.channel_post.chat.id,
                text="⚠️ La risposta non è stata inviata correttamente. Si prega di utilizzare il comando 'reply' per rispondere a un messaggio."
            )
            logger.warning("Messaggio di risposta ricevuto senza riferimento a un messaggio originale.")
    else:
        logger.warning("Messaggio non valido ricevuto.")

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte degli amministratori e le inoltra all'utente originale tramite il bot."""
    if update.channel_post:
        channel_message = update.channel_post

        # Controlla se il messaggio è una risposta
        if channel_message.reply_to_message and channel_message.reply_to_message.message_id in user_requests:
            original_message_id = channel_message.reply_to_message.message_id
            original_user_id = user_requests[original_message_id]

            # Invia la risposta all'utente originario
            await context.bot.send_message(
                chat_id=original_user_id,
                text=f"{channel_message.text}"
            )
        else:
            # Avviso nel canale se il messaggio non è stato inviato come reply
            await context.bot.send_message(
                chat_id=channel_message.chat_id,
                text="Il messaggio non è stato inviato! Per inviare una risposta all'utente, rispondi al messaggio originale!"
            )
            logger.warning("Messaggio di risposta ricevuto senza riferimento a un messaggio originale.")
    else:
        logger.warning("Messaggio non valido ricevuto.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce errori ed eccezioni."""
    logger.error("Eccezione durante l'aggiornamento: %s", context.error)

def main():
    """Avvia il bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Gestore dei comandi
    application.add_handler(CommandHandler("start", start))

    # Gestore dei messaggi ricevuti dalla chat del bot
    application.add_handler(MessageHandler(filters.TEXT & ~filters.REPLY, handle_message))

    # Gestore delle risposte degli amministratori (anche per media)
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_response))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
