from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import chat_id

def restricted(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_chat_id = update.effective_chat.id

        if user_chat_id != chat_id:
            await update.message.reply_text("🚫 Access Denied.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper
