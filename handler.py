from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown
from config import CHAT_ID
from core import bot, info, date_only


# Buttons Handler Function
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "balance":
        await query.edit_message_text(f"💰 Balance: {info.get('Available total traffic', 'N/A')}")
    elif data == "deadline":
        await query.edit_message_text(f"⏰ Deadline: {date_only}")

# Start Bot Function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = await bot.get_chat(CHAT_ID)
    first_name = chat.first_name
    escaped_name = escape_markdown(first_name, version=2)
    message = f"*Hello {escaped_name} 👋*"

    buttons = [
        [InlineKeyboardButton("💰 Your Balance", callback_data="balance")],
         [InlineKeyboardButton("📅 Deadline", callback_data="deadline")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode='MarkdownV2',
        reply_markup=keyboard
    )
