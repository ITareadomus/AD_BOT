import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funzione per gestire i messaggi di testo
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        logger.info(f"Messaggio ricevuto nella chat con ID: {update.message.chat.id}")

        # Verifica che il messaggio sia di tipo testo
        if not update.message.text:
            logger.info("Il messaggio ricevuto non è un testo.")
            return

        # Se il messaggio è una risposta a un altro messaggio, non fare nulla
        if update.message.reply_to_message:
            logger.info("Il messaggio è una reply, nessuna azione intrapresa.")
            return

        # Se il messaggio non è una reply, esegui la logica desiderata
        logger.info("Il messaggio NON è una reply, invio risposta...")
        # Esegui qui le azioni che desideri (ad esempio inviare una risposta o inoltrare il messaggio)
        await update.message.reply_text("Questo messaggio non è una reply")

# Funzione principale per avviare il bot
def main():
    # Inserisci il tuo token fornito da BotFather
    BOT_TOKEN = "7730646498:AAEvHUQjZSc_5OHoXiCwm64SDceyBEJO2go"

    # Crea l'applicazione del bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Aggiunge un handler per i messaggi di testo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Avvia il bot
    logger.info("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()
