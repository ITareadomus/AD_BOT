from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging, passkey

# Token del bot fornito da BotFather
BOT_TOKEN = passkey.TOKEN

# ID dei canali di smistamento
CHANNEL_EXTRA_TIME = '-1002403326958'
CHANNEL_REMOTE_OPEN = '-1002402258086'
CHANNEL_OTHER_ISSUES = '-1002350584252'

# Configurazione logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text(
        "Ciao! Sono il bot per la gestione degli appartamenti. Inviami un messaggio "
        "con la tua richiesta e lo smisterò al canale appropriato."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi ricevuti nei canali e determina se è una reply o un messaggio normale."""
    if not update.message:
        logger.warning("Aggiornamento ricevuto senza un messaggio valido.")
        return

    user_message = ""
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_id = user.id  # ID dell'utente che ha inviato il messaggio

    # Controlla se il messaggio è una reply
    if update.message.reply_to_message:
        logger.info(f"Il messaggio è una reply di {username}.")
        message_type = "reply"
    else:
        logger.info(f"Il messaggio è un messaggio normale di {username}.")
        message_type = "normal"

    # Ora smista il messaggio in base al tipo (reply o normale)
    if message_type == "reply":
        # Il messaggio è una reply, lo smistiamo in un canale specifico
        message = await context.bot.send_message(
            chat_id=CHANNEL_EXTRA_TIME,
            text=f"Risposta da {username}:\n{update.message.text if update.message.text else 'Nessun testo nel messaggio.'}"
        )
    else:
        # Il messaggio non è una reply, lo smistiamo in un altro canale
        message = await context.bot.send_message(
            chat_id=CHANNEL_REMOTE_OPEN,
            text=f"Messaggio normale da {username}:\n{update.message.text if update.message.text else 'Nessun testo nel messaggio.'}"
        )

    logger.info(f"Messaggio smistato da {username} al canale corretto.")

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte degli amministratori e le inoltra all'utente originale tramite il bot."""
    if update.channel_post:
        channel_message = update.channel_post

        # Controlla se il messaggio è una risposta
        if channel_message.reply_to_message:
            original_message_id = channel_message.reply_to_message.message_id
            original_user_id = channel_message.reply_to_message.from_user.id

            # Invia la risposta all'utente originario
            await context.bot.send_message(
                chat_id=original_user_id,
                text=f"Risposta dall'amministratore: {channel_message.text}"
            )
        else:
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

    # Gestore dei messaggi ricevuti nei canali
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Gestore delle risposte degli amministratori (anche per media)
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_response))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
