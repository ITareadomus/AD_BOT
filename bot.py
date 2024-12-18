import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Configura il logging
logging.basicConfig(level=logging.DEBUG)  # Usa DEBUG per avere più informazioni
logger = logging.getLogger(__name__)

# Funzione per gestire i messaggi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        logger.debug(f"Messaggio ricevuto nella chat con ID: {update.message.chat.id}")
        
        # Log del tipo di messaggio ricevuto
        logger.debug(f"Tipo di messaggio: {update.message.content_type}")
        logger.debug(f"Contenuto del messaggio: {update.message.text}")

        # Verifica se il messaggio è una reply
        if update.message.reply_to_message:  # Se il messaggio è una reply
            logger.debug("Il messaggio è una reply. Nessuna azione intrapresa.")
            return  # Non fare nulla se è una reply
        else:
            # Risponde con un messaggio di avviso
            logger.debug("Il messaggio NON è una reply, invio risposta...")
            await update.message.reply_text("Questo messaggio non è una reply")

# Funzione principale per avviare il bot
def main():
    # Inserisci il tuo token fornito da BotFather
    BOT_TOKEN = "7730646498:AAEvHUQjZSc_5OHoXiCwm64SDceyBEJO2go"

    # Crea l'applicazione del bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Aggiungi l'handler per qualsiasi tipo di messaggio (non comandi)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    # Avvia il bot
    logger.info("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()
