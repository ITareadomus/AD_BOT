from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi ricevuti direttamente dagli utenti e li smista nei canali appropriati."""
    if not update.message:
        logger.warning("Aggiornamento ricevuto senza un messaggio valido.")
        return

    user_message = ""

    # Verifica il tipo di messaggio
    if update.message.text and update.message.text.strip():
        user_message = update.message.text.lower().strip()
    elif update.message.caption and update.message.caption.strip():
        user_message = f"Messaggio con media: {update.message.caption.strip()}"
    else:
        user_message = "L'utente ha inviato un tipo di messaggio non riconosciuto."

    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_id = user.id  # ID dell'utente che ha inviato il messaggio

    # Smista il messaggio al canale appropriato
    if any(keyword in user_message for keyword in ['tempo', 'pulire', 'extra']):
        message = await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"{username}:\n{user_message}")
    elif any(keyword in user_message for keyword in ['apri', 'apertura', 'remoto']):
        message = await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"{username}:\n{user_message}")
    else:
        message = await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"{username}:\n{user_message}")
        await send_problem_options(update, context)  # Invio banner con opzioni

    # Memorizza l'ID del messaggio e l'ID dell'utente
    user_requests[message.message_id] = user_id

    logger.info(f"Messaggio smistato da {username} al canale corretto.")

async def send_problem_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia un banner con tre opzioni di problema."""
    keyboard = [
        [InlineKeyboardButton("Tempo extra", callback_data="extra_time")],
        [InlineKeyboardButton("Non riesco ad entrare", callback_data="remote_open")],
        [InlineKeyboardButton("Altro", callback_data="other_issues")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Non sono riuscito a capire il tuo problema. Seleziona una delle seguenti opzioni:",
        reply_markup=reply_markup
    )

async def handle_problem_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce la selezione dell'utente dalle opzioni del banner."""
    query = update.callback_query
    await query.answer()  # Conferma che il bottone è stato premuto

    user = query.from_user
    username = f"@{user.username}" if user.username else user.full_name

    if query.data == "extra_time":
        await query.edit_message_text("Hai chiesto tempo extra. La tua richiesta sarà elaborata.")
        await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"{username} ha chisto tempo extra")
    elif query.data == "remote_open":
        await query.edit_message_text("Hai selezionato: Non riesco ad entrare. La tua richiesta sarà elaborata.")
        await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"{username} ha problemi ad accedere")
    elif query.data == "other_issues":
        await query.edit_message_text("Hai selezionato: Altro. La tua richiesta sarà elaborata.")
        await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"{username} ha segnalato un problma")

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

    # Gestore dei callback dei pulsanti
    application.add_handler(CallbackQueryHandler(handle_problem_selection))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
