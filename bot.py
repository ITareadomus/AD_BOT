from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging
import passkey

# Token del bot fornito da BotFather
BOT_TOKEN = passkey.TOKEN

# ID dei canali di smistamento
CHANNEL_EXTRA_TIME = '-1002403326958'
CHANNEL_REMOTE_OPEN = '-1002402258086'
CHANNEL_OTHER_ISSUES = '-1002350584252'

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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
    """Gestisce i messaggi degli utenti e invia un banner con opzioni."""
    if not update.message:
        logger.warning("Aggiornamento ricevuto senza un messaggio valido.")
        return

    user_message = update.message.text.lower().strip()
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_id = user.id

    # Genera un banner con opzioni
    keyboard = [
        [InlineKeyboardButton("Tempo extra", callback_data=f"extra_time|{user_id}")],
        [InlineKeyboardButton("Non riesco ad entrare", callback_data=f"remote_open|{user_id}")],
        [InlineKeyboardButton("Altro", callback_data=f"other_issues|{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Invia il banner e avvia il timer
    sent_message = await update.message.reply_text(
        "Non sono riuscito a capire il tuo problema. Seleziona una delle seguenti opzioni entro 1 minuto:",
        reply_markup=reply_markup
    )

    # Salva i dettagli del messaggio e avvia un job per l'auto-smistamento
    user_requests[sent_message.message_id] = user_id
    context.job_queue.run_once(auto_forward_message, 60, data={
        "message_id": sent_message.message_id,
        "user_id": user_id,
        "user_message": user_message,
        "username": username
    }, name=str(user_id))

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il clic sui pulsanti del banner."""
    query = update.callback_query
    await query.answer()

    try:
        action, user_id = query.data.split('|')
        user_id = int(user_id)

        # Smista il messaggio in base all'azione scelta
        if action == "extra_time":
            channel_id, message = CHANNEL_EXTRA_TIME, "Tempo extra"
        elif action == "remote_open":
            channel_id, message = CHANNEL_REMOTE_OPEN, "Non riesco ad entrare"
        elif action == "other_issues":
            channel_id, message = CHANNEL_OTHER_ISSUES, "Altro"
        else:
            await query.edit_message_text("Opzione non valida.")
            return

        await context.bot.send_message(
            chat_id=channel_id,
            text=f"{query.from_user.mention_html()} ha selezionato: {message}.",
            parse_mode='HTML'
        )
        await query.edit_message_text(f"Hai selezionato: {message}.")

        # Rimuovi il job associato, se esiste
        jobs = context.job_queue.get_jobs_by_name(str(user_id))
        for job in jobs:
            job.schedule_removal()

    except Exception as e:
        logger.error("Errore durante il click del pulsante: %s", e)

async def auto_forward_message(context: ContextTypes.DEFAULT_TYPE):
    """Smista automaticamente il messaggio se l'utente non seleziona un'opzione entro un minuto."""
    try:
        data = context.job.data
        message_id = data['message_id']
        user_id = data['user_id']
        user_message = data['user_message']
        username = data['username']

        if message_id in user_requests:
            del user_requests[message_id]

            # Invia al canale appropriato
            await context.bot.send_message(
                chat_id=CHANNEL_OTHER_ISSUES,
                text=f"{username}:
{user_message}"
            )
    except Exception as e:
        logger.error("Errore durante lo smistamento automatico: %s", e)

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
