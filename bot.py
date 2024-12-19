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

# Dizionario per tracciare gli utenti che inviano richieste
user_requests = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text(
        "Ciao! Sono il bot per la gestione degli appartamenti. Inviami un messaggio "
        "con la tua richiesta e lo smisterò al canale appropriato."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi ricevuti direttamente dagli utenti e li smista nei canali appropriati."""
    if not update.message:
        logger.warning("Aggiornamento ricevuto senza un messaggio valido.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
        )
        return

    # Verifica il tipo di messaggio
    if update.message.text and update.message.text.strip():
        user_message = update.message.text.lower().strip()
    elif update.message.caption and update.message.caption.strip():
        user_message = f"Messaggio con media: {update.message.caption.strip()}"
    else:
        user_message = None

    if not user_message:
        logger.warning("Messaggio non valido inviato dall'utente.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
        )
        return

    user = update.message.from_user
    if user:
        username = f"@{user.username}" if user.username else user.full_name
        user_id = user.id  # ID dell'utente che ha inviato il messaggio
    else:
        logger.warning("Impossibile identificare l'utente.")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
        )
        return

    # Smista il messaggio al canale appropriato
    if any(keyword in user_message for keyword in ['tempo', 'pulire', 'extra']):
        channel_id = CHANNEL_EXTRA_TIME
    elif any(keyword in user_message for keyword in ['apri', 'apertura', 'remoto']):
        channel_id = CHANNEL_REMOTE_OPEN
    else:
        channel_id = CHANNEL_OTHER_ISSUES

    message = await context.bot.send_message(chat_id=channel_id, text=f"{username}:\n{user_message}")

    # Memorizza l'ID del messaggio e l'ID dell'utente
    user_requests[message.message_id] = user_id

    logger.info(f"Messaggio smistato da {username} al canale corretto.")

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte degli amministratori e le inoltra all'utente originale tramite il bot."""
    if update.channel_post:
        channel_message = update.channel_post

        # Logga l'ID del canale di destinazione
        logger.info(f"Canale di destinazione: {channel_message.chat_id}")

        # Controlla se il messaggio è una risposta
        if channel_message.reply_to_message:
            logger.info(f"Risposta collegata al messaggio ID: {channel_message.reply_to_message.message_id}")

            if channel_message.reply_to_message.message_id in user_requests:
                original_message_id = channel_message.reply_to_message.message_id
                original_user_id = user_requests[original_message_id]

                # Invia la risposta all'utente originario
                await context.bot.send_message(
                    chat_id=original_user_id,
                    text=f"{channel_message.text}"
                )
                logger.info(f"Risposta inviata all'utente con ID: {original_user_id}")
            else:
                logger.warning("Messaggio di risposta ricevuto senza riferimento a un messaggio originale valido.")
                # Invio di un avviso al canale
                await context.bot.send_message(
                    chat_id=channel_message.chat_id,
                    text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
                )
        else:
            logger.warning("Messaggio non è una risposta valida.")
            # Invio di un avviso al canale
            await context.bot.send_message(
                chat_id=channel_message.chat_id,
                text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
            )
    else:
        logger.warning("Messaggio non valido ricevuto.")
        # Invio di un avviso al canale
        await context.bot.send_message(
            chat_id=update.channel_post.chat_id,
            text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
        )

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
