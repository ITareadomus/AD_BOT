import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ID del canale in cui effettuare il controllo
TARGET_CHANNEL_ID = -1002350584252

# Funzione per gestire i messaggi di testo
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        logger.info(f"Messaggio ricevuto nella chat con ID: {update.message.chat.id}")

        if not update.message.text:  # Controlla se il messaggio non è testo
            logger.info("Il messaggio ricevuto non è un testo.")
            return

        if update.message.chat.id == TARGET_CHANNEL_ID:  # Controlla se il messaggio è nel canale target
            if update.message.reply_to_message:  # Controlla se il messaggio è una reply
                logger.info("Il messaggio è una reply, nessuna azione intrapresa.")
                return  # Non fa nulla se è una reply
            else:
                # Risponde nella chat con il messaggio desiderato
                logger.info("Il messaggio NON è una reply, invio risposta...")
                await update.message.reply_text("Questo messaggio non è una reply")

# Funzione principale per avviare il bot
def main():
    # Inserisci il tuo token fornito da BotFather
    BOT_TOKEN = "INSERISCI_IL_TUO_TOKEN_QUI"

    # Crea l'applicazione del bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Aggiunge un handler per i messaggi di testo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Avvia il bot
    logger.info("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()
