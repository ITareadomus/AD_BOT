from telegram import Update, Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging, passkey, time

# Token del bot fornito da BotFather
BOT_TOKEN = passkey.TOKEN

# ID dei canali di smistamento
CHANNEL_EXTRA_TIME = '-1002403326958'
CHANNEL_REMOTE_OPEN = '-1002402258086'
CHANNEL_OTHER_ISSUES = '-1002350584252'

# Configurazione logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dizionari per tracciare le richieste e le categorie assegnate
user_requests = {}
user_categories = {}

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
        else:
            logger.warning("Messaggio normale non è una risposta valida.")
            # Invio di un avviso al canale
            await context.bot.send_message(
                chat_id=channel_message.chat_id,
                text="⚠️ ATTENZIONE, IL MESSAGGIO NON È STATO INVIATO PERCHÈ NON È UNA RISPOSTA A UN ALTRO MESSAGGIO! ⚠️"
            )

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il clic sui pulsanti del banner."""
    query = update.callback_query
    await query.answer()
    data = query.data.split('|')
    action = data[0]
    user_id = int(data[1])

    if query.message.message_id not in user_requests:
        await query.edit_message_text("Il tempo per selezionare un'opzione è scaduto.")
        return

    user_data = user_requests.pop(query.message.message_id)
    user_message = user_data["user_message"]
    username = user_data["username"]

    user_categories[user_id] = (action, time.time())
    await smista_messaggio(action, username, user_message, context)
    await query.edit_message_text(f"Hai selezionato: {action.replace('_', ' ').capitalize()}.")

async def smista_messaggio(category, username, user_message, context):
    """Smista il messaggio al canale appropriato."""
    if category == "extra_time":
        await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"{username}:\n{user_message}")
    elif category == "remote_open":
        await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"{username}:\n{user_message}")
    elif category == "other_issues":
        await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"{username}:\n{user_message}")

async def check_messages(context: ContextTypes.DEFAULT_TYPE):
    """Verifica se ci sono messaggi scaduti da smistare automaticamente nel canale 'other issues'."""
    current_time = time.time()
    to_remove = []
    for message_id, user_data in user_requests.items():
        if current_time - user_data["timestamp"] > 60:
            username = user_data["username"]
            user_message = user_data["user_message"]
            await smista_messaggio("other_issues", username, user_message, context)
            to_remove.append(message_id)
    for message_id in to_remove:
        del user_requests[message_id]

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

    # Gestore dei clic sui pulsanti
    application.add_handler(CallbackQueryHandler(handle_button_click))

    # Gestore delle risposte degli amministratori (anche per media)
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_response))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    # Aggiungi un job che controlla ogni 5 secondi se ci sono messaggi scaduti (60 secondi totali)
    application.job_queue.run_repeating(check_messages, interval=5, first=5)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

