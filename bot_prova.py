from telegram import Update, Bot, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import logging, passkey

# Configura il logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ID del canale dove inoltrare i messaggi
CHANNEL_ID = '-1002350584252'

# Dizionario per tracciare gli utenti che inviano richieste
user_requests = {}

# Funzione per gestire i messaggi in arrivo dagli utenti
def handle_user_message(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message

    # Inoltra il messaggio al canale e salva l'ID del messaggio inoltrato
    sent_message = context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Richiesta da @{user.username or user.id} (ID: {user.id}):\n{message.text}"
    )

    # Salva l'ID dell'utente in base all'ID del messaggio nel canale
    user_requests[sent_message.message_id] = user.id

    # Conferma la ricezione all'utente
    message.reply_text("La tua richiesta è stata inviata. Riceverai una risposta appena possibile.")

# Funzione per gestire le risposte dal canale
def handle_channel_reply(update: Update, context: CallbackContext):
    channel_message = update.channel_post

    # Controlla se il messaggio è una risposta
    if channel_message.reply_to_message and channel_message.reply_to_message.message_id in user_requests:
        original_message_id = channel_message.reply_to_message.message_id
        user_id = user_requests[original_message_id]

        # Invia la risposta all'utente originario
        context.bot.send_message(
            chat_id=user_id,
            text=f"Risposta alla tua richiesta:\n{channel_message.text}"
        )

# Funzione per avviare il bot (/start)
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Benvenuto! Inviami un messaggio e lo inoltrerò al canale. Riceverai una risposta appena possibile.")

# Funzione principale per configurare ed eseguire il bot
def main():
    # Inserisci il token del tuo bot
    BOT_TOKEN = (passkey.TOKEN)

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Gestore per il comando /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Gestore per i messaggi degli utenti
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_message))

    # Gestore per i messaggi nel canale
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.channel, handle_channel_reply))

    # Avvia il bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
