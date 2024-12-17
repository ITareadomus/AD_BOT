from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import passkey

# ID del canale dove inviare il messaggio
CHANNEL_ID = '-1002350584252'

# ID dell'amministratore del canale
ADMIN_ID = 7799323246 # Sostituisci con l'ID dell'amministratore

# Funzione per iniziare il bot
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Ciao! Mandami il tuo messaggio e lo inoltrerò al canale.")

# Funzione per gestire i messaggi degli utenti
def handle_message(update: Update, context: CallbackContext) -> None:
    # Prendi il messaggio dell'utente
    user_message = update.message.text
    user_id = update.message.from_user.id

    # Invia il messaggio al canale
    context.bot.send_message(chat_id=CHANNEL_ID, text=f"Messaggio da {update.message.from_user.first_name} ({user_id}): {user_message}", reply_markup=None)

    # Rispondi all'utente che il messaggio è stato inoltrato
    update.message.reply_text("Il tuo messaggio è stato inviato al canale. Attendi una risposta.")

# Funzione per gestire le risposte nel canale
def handle_reply(update: Update, context: CallbackContext) -> None:
    # Verifica se la risposta è un "reply" (risposta a un messaggio specifico)
    if update.message.reply_to_message:
        # Prendi l'ID dell'utente che ha inviato il messaggio originale
        original_user_id = int(update.message.reply_to_message.text.split(":")[1].split(")")[0])

        # Invia la risposta all'utente originale
        context.bot.send_message(chat_id=original_user_id, text=f"Risposta dell'amministratore: {update.message.text}")
    else:
        # Se non è una risposta, invia il messaggio di default
        update.message.reply_text("Messaggio non inviato correttamente. Si prega di rispondere utilizzando la funzione di reply.")

def main():
    # Inserisci il token del tuo bot
    updater = Updater(passkey.TOKEN)

    # Ottieni il dispatcher per registrare i gestori
    dispatcher = updater.dispatcher

    # Aggiungi un gestore per il comando /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Aggiungi un gestore per i messaggi di testo
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, handle_message))

    # Aggiungi un gestore per le risposte nel canale
    dispatcher.add_handler(MessageHandler(filters.reply, handle_reply))

    # Avvia il bot
    updater.start_polling()

    # Mantieni il bot in esecuzione
    updater.idle()

if __name__ == '__main__':
    main()
