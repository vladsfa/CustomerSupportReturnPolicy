import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

from openai_src.assistant_definition import OpenAiBot
from openai_src.native_assistant import assistant
from constants import welcome_msg

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7356062896:AAGdLC5Xd9Wzqq1rLdnu4cw7OOQo26EVmA8"

chatbot = OpenAiBot(assistant)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chatbot.start_conversation(welcome_msg)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_msg)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assistant_reponse = await chatbot.chat(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=assistant_reponse)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()