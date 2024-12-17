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

# Dizionario per tracciare i messaggi inoltrati e gli utenti originali
forwarded_messages = {}

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
        user = update.channel_post.sender_chat or update.channel_post.from_user
        original_user_id = user.id if user else None
        username = f"@{user.username}" if user.username else user.full_name

        if any(keyword in text for keyword in ['tempo', 'pulire', 'extra']):
            message = await context.bot.send_message(
                chat_id=CHANNEL_EXTRA_TIME,
                text=f"Richiesta ricevuta da {username}:\n{text}"
            )
        elif any(keyword in text for keyword in ['apri', 'apertura', 'remoto']):
            message = await context.bot.send_message(
                chat_id=CHANNEL_REMOTE_OPEN,
                text=f"Richiesta ricevuta da {username}:\n{text}"
            )
        else:
            message = await context.bot.send_message(
                chat_id=CHANNEL_OTHER_ISSUES,
                text=f"Segnalazione ricevuta da {username}:\n{text}"
            )
        
        # Salva l'ID del messaggio inoltrato e l'utente originale
        if message and original_user_id:
            forwarded_messages[message.message_id] = {'user_id': original_user_id, 'username': username}

async def handle_pinned_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi pinnati e risponde all'utente originale."""
    if update.pinned_message and update.pinned_message.reply_to_message:
        pinned_message_id = update.pinned_message.reply_to_message.message_id
        user_data = forwarded_messages.get(pinned_message_id)

        if user_data:
            original_user_id = user_data['user_id']
            username = user_data['username']

            # Ottieni la risposta al messaggio pinnato
            response = update.pinned_message.text or "Nessun testo nella risposta."
            await context.bot.send_message(
                chat_id=original_user_id,
                text=f"Risposta dal canale {username}: {response}"
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

    # Gestore dei messaggi pinnati nei canali secondari
    application.add_handler(MessageHandler(filters.UpdateType.PINNED_MESSAGE, handle_pinned_message))

    # Gestore degli errori
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
