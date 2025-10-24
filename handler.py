import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ChatAction
from telegram.helpers import escape_markdown
from core import bot
from config import AUTHORIZED_CHAT_ID
from genquery import generate_random_distribution, parse_size_to_bytes

SESSIONS, SIZE = range(2)


# ------------------ Chat Action ------------------- #
async def send_chat_action(bot, chat_id, action=ChatAction.TYPING, delay=1):
    await bot.send_chat_action(chat_id=chat_id, action=action)
    await asyncio.sleep(delay)


# ------------------ Query Generation Start ------------------ #
async def start_query_conversation(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Start the query conversation regardless of source"""
    context.user_data.clear()  # Clear any previous conversation data
    context.user_data['in_conversation'] = True
    text = "<b>Enter The sessions IDs\n/cancel to stop.</b>"
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML"
    )
    return SESSIONS


async def gen_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(AUTHORIZED_CHAT_ID):
        return  # ignore unauthorized user

    await send_chat_action(bot, update.effective_chat.id, ChatAction.TYPING, delay=0.5)
    return await start_query_conversation(update.effective_chat.id, context)


# ------------------ Buttons Handler ------------------ #
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback = update.callback_query
    chat_id = callback.message.chat.id

    if str(chat_id) != str(AUTHORIZED_CHAT_ID):
        await callback.answer("You are not authorized to use this bot.", show_alert=True)
        return

    await callback.answer()
    data = callback.data

    if data == "query":
        await callback.message.delete()
        return await start_query_conversation(chat_id, context)


# ------------------ Conversation ------------------ #
async def gen_receive_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if str(chat_id) != str(AUTHORIZED_CHAT_ID):
        return  # ignore unauthorized user

    text = update.message.text or ""
    sessions = [s.strip() for s in text.replace(",", " ").split() if s.strip() and s.strip().isalnum()]

    if not sessions:
        await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
        await update.message.reply_text("No valid session IDs detected.\n/cancel to stop.")
        return SESSIONS

    context.user_data['gen_sessions'] = sessions

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text("Got sessions. Now enter desired total size (e.g., 2.1GB or 500MB):")
    return SIZE


async def gen_receive_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if str(chat_id) != str(AUTHORIZED_CHAT_ID):
        return  # ignore unauthorized user

    text = update.message.text or ""
    try:
        total_bytes = parse_size_to_bytes(text)
    except ValueError:
        await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
        await update.message.reply_text("Invalid size input. Try again or /cancel.")
        return SIZE

    context.user_data['gen_total_bytes'] = total_bytes
    sessions = context.user_data.get('gen_sessions', [])
    total_gb = total_bytes / (1024 ** 3)

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text(
        f"*Sessions:* {len(sessions)}\n*Total size:* {total_gb:.2f} GB\n\n",
        parse_mode='Markdown'
    )

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=1.0)
    queries = generate_random_distribution(sessions, total_bytes)
    full_text = "\n".join(queries)

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text(f"<pre language='sql'>\n{full_text}\n</pre>", parse_mode='HTML')

    return ConversationHandler.END


async def gen_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if str(chat_id) != str(AUTHORIZED_CHAT_ID):
        return  # ignore unauthorized user

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text("Generation cancelled.")
    return ConversationHandler.END


# ------------------ Conversation Handler ------------------ #
def get_generate_conv_handler():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^/genquery$'), gen_start),
            CallbackQueryHandler(button_handler, pattern='^query$'),
        ],
        states={
            SESSIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gen_receive_sessions)
            ],
            SIZE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gen_receive_size)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex('^/cancel$'), gen_cancel),
            MessageHandler(filters.COMMAND, gen_cancel),
        ],
        allow_reentry=True,
        name="query_conversation",
        persistent=False,
        per_chat=True
    )


# ------------------ Start ------------------ #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if str(chat_id) != str(AUTHORIZED_CHAT_ID):
        return

    chat = await context.bot.get_chat(chat_id)
    fname = chat.first_name
    username = chat.username
    escaped_fname = escape_markdown(fname, version=2)

    if username == "belalammar":
        escaped_admin = escape_markdown("Admin", version=2)
        welcome_msg = f"*Hello {escaped_admin} 👋🏼*\n\nDrop The Video Link"
        buttons = [[InlineKeyboardButton("🔁 Gen Query", callback_data="query")]]
        keyboard = InlineKeyboardMarkup(buttons)
    else:
        welcome_msg = f"*Hello {escaped_fname} 👋🏼*\n\nDrop The Video Link"
        keyboard = None

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await context.bot.send_message(
        chat_id=chat_id,
        text=welcome_msg,
        parse_mode='MarkdownV2',
        reply_markup=keyboard
    )

# ------------------ About ------------------ #
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if str(chat_id) != str(AUTHORIZED_CHAT_ID):
        return

    auther = "belalammar"
    about_text = f"""*Private Bot*\n\n*_Auther:_* *_[Textme](https://t.me/{auther})_*"""

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text(about_text, parse_mode="MarkdownV2")
