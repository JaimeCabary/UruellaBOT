import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from llm_router import LLMRouter

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Security: List of user IDs allowed to use the bot
ALLOWED_USER_IDS = [
    int(uid.strip()) for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid.strip()
]

def is_authorized(update: Update) -> bool:
    """Security check to ensure only you can use this bot."""
    if not ALLOWED_USER_IDS:
        logger.warning("No ALLOWED_USER_IDS set! Bot is public (DANGEROUS).")
        return True # Change to False in production if you want strict denyby defaults
    return update.effective_user.id in ALLOWED_USER_IDS

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access.")
        return
        
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! 👋 I am your new Virtual Assistant. "
        "I can help automate your tasks using Google Workspace and answer questions using AI. "
        "What would you like to do?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    if not is_authorized(update):
        return
    await update.message.reply_text("Just talk to me naturally! Tell me what you want to automate or ask.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route user messages to the AI agent."""
    if not is_authorized(update):
        return
        
    text = update.message.text
    user_id = str(update.effective_user.id)
    logger.info(f"Received message from {user_id}: {text}")
    
    # Initialize router once (could be moved to application startup for efficiency)
    llm = LLMRouter()
    
    # Send a "typing..." action to Telegram so the user knows the AI is thinking
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Pick the first available provider automatically
    provider = "openai"
    if not os.getenv("OPENAI_API_KEY") and os.getenv("ANTHROPIC_API_KEY"):
        provider = "anthropic"
    elif not os.getenv("OPENAI_API_KEY") and os.getenv("GROQ_API_KEY"):
        provider = "llama"
    
    response = llm.process_message(text, user_id=user_id, provider=provider)
    
    await update.message.reply_text(response)

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    # Create the app
    application = Application.builder().token(token).build()

    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Respond to all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
