from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging, passkey

# Token del bot fornito da BotFather
BOT_TOKEN = (passkey.TOKEN)

# ID del canale principale e dei canali secondari
SOURCE_CHANNEL = '-1002406576806'
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

async def handle_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi dal canale principale e li smista nei canali appropriati."""
    if update.channel_post and update.channel_post.text:
        text = update.channel_post.text.lower()
        user_message = update.channel_post.text
        user_id = update.channel_post.from_user.id  # ID dell'utente che ha inviato il messaggio nel canale

        if any(keyword in text for keyword in ['tempo', 'pulire', 'extra']):
            message = await context.bot.send_message(chat_id=CHANNEL_EXTRA_TIME, text=f"Richiesta ricevuta:\n{user_message}")
            # Salviamo l'ID del messaggio in modo che possa essere utilizzato per rispondere
            context.chat_data['message_id'] = message.message_id
            context.chat_data['user_id'] = user_id  # Memorizziamo l'ID dell'utente per inviare la risposta

        elif any(keyword in text for keyword in ['apri', 'apertura', 'remoto']):
            message = await context.bot.send_message(chat_id=CHANNEL_REMOTE_OPEN, text=f"Richiesta ricevuta:\n{user_message}")
            context.chat_data['message_id'] = message.message_id
            context.chat_data['user_id'] = user_id

        else:
            message = await context.bot.send_message(chat_id=CHANNEL_OTHER_ISSUES, text=f"Segnalazione ricevuta:\n{user_message}")
            context.chat_data['message_id'] = message.message_id
            context.chat_data['user_id'] = user_id

    else:
        logger.warning("Messaggio dal canale non contiene testo.")

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le risposte degli utenti e smista i messaggi nei canali appropriati."""
    user_message = update.message.text.lower()  # Ottieni il testo del messaggio inviato dall'utente
    user = update.message.from_user
    username = f"@{user.username}" if user.username else user.full_name
    user_id = user.id  # ID dell'utente che invia la risposta

    # Recupera l'ID del messaggio e l'ID dell'utente dal dizionario 'chat_data'
    original_message_id = context.chat_data.get('message_id')
    original_user_id = context.chat_data.get('user_id')

    if original_message_id and original_user_id:
        # Il bot invia la risposta all'utente che ha inviato il messaggio originale
        await context.bot.send_message(
            chat_id=original_user_id,
            text=f"Risposta ricevuta da {username}:\n{user_message}"
        )

        # Se l'admin risponde nel canale, il bot inoltra la risposta
        await context.bot.send_message(
            chat_id=CHANNEL_OTHER_ISSUES,  # Puoi cambiarlo a uno dei tuoi canali specifici
            text=f"Risposta per l'utente {username}: {user_message}",
            reply_to_message_id=original_message_id  # Aggiunge la funzionalità di "reply" al messaggio originale
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
