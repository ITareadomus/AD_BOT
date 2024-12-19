from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging, passkey

# Token del bot fornito da BotFather
BOT_TOKEN = (passkey.TOKEN)

# ID dei canali di smistamento
CHANNEL_EXTRA_TIME = '-1002403326958'
CHANNEL_REMOTE_OPEN = '-1002402258086'
CHANNEL_OTHER_ISSUES = '-1002350584252'

# Parole chiave per lo smistamento automatico
KEYWORDS_EXTRA_TIME = ['tempo extra', 'richiesta tempo extra']
KEYWORDS_REMOTE_OPEN = ['non riesco ad entrare', 'problema apertura porta', 'accesso remoto']

# Configurazione logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dizionario per tracciare i messaggi degli utenti
user_requests = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text(
        "Ciao! Sono il bot per la gestione degli appartamenti. Inviami un messaggio "
        "con la tua richiesta e lo smisterò al canale appropriato."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi ricevuti direttamente dagli utenti e invia un banner con opzioni se necessario."""
    if not update.message:
        logger.warning("Aggiornamento ricevuto senza un messaggio valido.")
        return

    user_message = update.message.text.strip().lower()
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_id = user.id  # ID dell'utente che ha inviato il messaggio

    # Verifica se il messaggio contiene le parole chiave per lo smistamento automatico
    if any(keyword in user_message for keyword in KEYWORDS_EXTRA_TIME):
        await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"{username}:\n{user_message}")
        return
    elif any(keyword in user_message for keyword in KEYWORDS_REMOTE_OPEN):
        await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"{username}:\n{user_message}")
        return

    # Se il messaggio non contiene le parole chiave specifiche, invia il menu di selezione
    keyboard = [
        [InlineKeyboardButton("Tempo extra", callback_data=f"extra_time|{user_id}")],
        [InlineKeyboardButton("Non riesco ad entrare", callback_data=f"remote_open|{user_id}")],
        [InlineKeyboardButton("Altro", callback_data=f"other_issues|{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Invia il banner
    sent_message = await update.message.reply_text(
        "Non sono riuscito a capire il tuo problema. Seleziona una delle seguenti opzioni entro 1 minuto:",
        reply_markup=reply_markup
    )

    # Salva i dettagli del messaggio
    user_requests[sent_message.message_id] = {
        "user_id": user_id,
        "username": username,
        "user_message": user_message
    }

    # Avvia un job per l'auto-smistamento (dopo 1 minuto)
    context.job_queue.run_once(auto_forward_message, 10, data={"message_id": sent_message.message_id}, name=str(sent_message.message_id))

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il clic sui pulsanti del banner."""
    query = update.callback_query
    await query.answer()  # Conferma che il bottone è stato premuto

    data = query.data.split('|')
    action = data[0]
    message_id = int(query.message.message_id)

    if message_id not in user_requests:
        await query.edit_message_text("Il tempo per selezionare un'opzione è scaduto.")
        return

    user_data = user_requests.pop(message_id)
    user_message = user_data["user_message"]
    username = user_data["username"]

    # Smista il messaggio in base all'azione scelta
    if action == "extra_time":
        await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"{username}:\n{user_message}")
        await query.edit_message_text("Hai selezionato: Tempo extra.")
    elif action == "remote_open":
        await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"{username}:\n{user_message}")
        await query.edit_message_text("Hai selezionato: Non riesco ad entrare.")
    elif action == "other_issues":
        await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"{username}:\n{user_message}")
        await query.edit_message_text("Hai selezionato: Altro.")

    # Rimuovi il job associato, se esiste
    jobs = context.job_queue.get_jobs_by_name(str(message_id))
    for job in jobs:
        job.schedule_removal()

async def auto_forward_message(context: ContextTypes.DEFAULT_TYPE):
    """Smista automaticamente il messaggio se l'utente non seleziona un'opzione entro un minuto."""
    job_data = context.job.data
    message_id = job_data["message_id"]

    if message_id in user_requests:
        user_data = user_requests.pop(message_id)
        user_message = user_data["user_message"]
        username = user_data["username"]

        # Invia al canale di default "Altro" se non ci sono parole chiave corrispondenti
        await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"{username}:\n{user_message}")

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

    # Gestore del clic sui pulsanti
    application.add_handler(CallbackQueryHandler(handle_button_click))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
