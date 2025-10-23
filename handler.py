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
from genquery import generate_random_distribution, parse_size_to_bytes
SESSIONS, SIZE = range(2)


# ------------------ Chat Action ------------------ #

async def send_chat_action(bot, chat_id, action=ChatAction.TYPING, delay=1):
    await bot.send_chat_action(chat_id=chat_id, action=action)
    await asyncio.sleep(delay)

# How can i git it ?
# await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5) # caht action

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
    await send_chat_action(bot, update.effective_chat.id, ChatAction.TYPING, delay=0.5)
    return await start_query_conversation(update.effective_chat.id, context)

# ------------------ Buttons Handler ------------------ #
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback = update.callback_query
    await callback.answer()
    data = callback.data
    chat_id = callback.message.chat.id

    if data == "query":
        # Start the conversation
        await callback.message.delete()  # Remove the inline keyboard
        return await start_query_conversation(chat_id, context)


# ------------------ Conversation ------------------ #
async def gen_receive_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    # Handle both space and comma separators, and clean up input
    sessions = [s.strip() for s in text.replace(",", " ").split() if s.strip() and s.strip().isalnum()]

    if not sessions:
        await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
        await update.message.reply_text("No valid session IDs detected.\n/cancel to stop.")
        return SESSIONS

    # Set sessions in context
    context.user_data['gen_sessions'] = sessions
    
    # Send typing action before response
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text("Got sessions. Now enter desired total size (e.g., 2.1GB or 500MB):")
    return SIZE


async def gen_receive_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id # for chat action
    try:
        total_bytes = parse_size_to_bytes(text)
    except ValueError:
        await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
        await update.message.reply_text("Invalid size input. Try again or /cancel.")
        return SIZE

    context.user_data['gen_total_bytes'] = total_bytes
    sessions = context.user_data.get('gen_sessions', [])
    total_gb = total_bytes / (1024 ** 3)

    # Show typing for session info
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text(
        f"*Sessions:* {len(sessions)}\n*Total size:* {total_gb:.2f} GB\n\n",
        parse_mode='Markdown'
    )

    # Generate queries
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=1.0)  # Longer delay for query generation
    queries = generate_random_distribution(sessions, total_bytes)
    full_text = "\n".join(queries)
    
    # Show typing before sending the result
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text(f"<pre language='sql'>\n{full_text}\n</pre>", parse_mode='HTML')

    return ConversationHandler.END


async def gen_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id # for caht action
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5) #chat action

    await update.message.reply_text("Generation cancelled.")
    return ConversationHandler.END


# ------------------ Conversation Handler ------------------ #
def get_generate_conv_handler():
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^/genquery$'), gen_start),  # Command entry point
            CallbackQueryHandler(button_handler, pattern='^query$'),  # Button entry point
        ],
        states={
            SESSIONS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, 
                    gen_receive_sessions
                )
            ],
            SIZE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, 
                    gen_receive_size
                )
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex('^/cancel$'), gen_cancel),
            MessageHandler(filters.COMMAND, gen_cancel),  # Handle any command as cancel
        ],
        allow_reentry=True,
        name="query_conversation",
        persistent=False,
        per_chat=True
    )


# ------------------ Start ------------------ #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = await bot.get_chat(update.effective_chat.id)
    chat_id = update.effective_chat.id # for chat action
    fname = chat.first_name
    admin = "Admin"
    username = chat.username  

    escaped_fname = escape_markdown(fname, version=2)
    escaped_admin = escape_markdown(admin, version=2)

    if username == "belalammar":
        welcome_msg = f""" *Hello {escaped_admin} 👋🏼*\n*dl:* /dl """
    else:
        welcome_msg = f"""*Hello {escaped_fname} 👋🏼*\n*dl:* /dl """
   
    buttons = [
    
        [InlineKeyboardButton(" 🔁 Gen Query", callback_data="query")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5) #caht action
    await bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_msg,
        parse_mode='MarkdownV2',
        reply_markup=keyboard
    )
# ------------------ About ------------------ #
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auther = "belalammar"
    about_text = f"""*Private Bot*\n\n*_Auther:_* *_[Textme](https://t.me/{auther})_*"""

    chat_id = update.effective_chat.id 
    await send_chat_action(bot, chat_id, ChatAction.TYPING, delay=0.5)
    await update.message.reply_text(about_text, parse_mode="MarkdownV2")
    