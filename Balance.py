import os
from dotenv import load_dotenv
import requests
import hashlib
import hmac
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler
from telegram.helpers import escape_markdown
from bs4 import BeautifulSoup
from pprint import pprint
import sys
load_dotenv()
base_url = "http://10.0.0.254/radiusmanager"
login_url = f"{base_url}/user.php?cont=login"
lang_url = f"{base_url}/user.php?cont=change_lang&lang=English"

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

username = os.getenv("username")
password = os.getenv("password")

md5_pass = hashlib.md5(password.encode()).hexdigest()
md5_hmac = hmac.new(username.encode(), md5_pass.encode(), hashlib.md5).hexdigest()

data = {
    'username': username,
    'password': '',
    'md5': md5_hmac,
    'lang': 'English',
    'Submit': 'Login'
}

session = requests.Session()
session.get(lang_url)
r = session.post(login_url, data=data)
soup = BeautifulSoup(r.text, "html.parser")
meta = soup.find('meta', attrs={'http-equiv': 'refresh'})


if meta and 'URL' in meta.get('content', ''):
    redirect_url = meta['content'].split('URL=')[-1]
    if not redirect_url.startswith('http'):
        redirect_url = f"{base_url}/{redirect_url}"
    r = session.get(redirect_url)
soup = BeautifulSoup(r.text, "html.parser")

info = {}
for row in soup.find_all("tr"):
    key_cell = row.find("td", class_="td1")
    value_cell = row.find("td", class_="b1")
    if key_cell and value_cell:
        key = key_cell.text.strip().rstrip(':')
        value = value_cell.text.strip()
        info[key] = value

# for formating deadline time
deadline = info.get("Account expiry")
if deadline:
    date_only = deadline.split(" ")[0]

# Telegram handlers
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "balance":
        await query.edit_message_text(f"💰 Balance: {info['Available total traffic']}")
    elif data == "deadline":
        await query.edit_message_text(f"⏰ Deadline: {date_only}")

# send data to telegram /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = await bot.get_chat(CHAT_ID)
    first_name = chat.first_name
    escaped_name = escape_markdown(first_name, version=2)
    message = f"*Hello {escaped_name} 👋*"
    buttons = [
        [InlineKeyboardButton("💰 Your Balance", callback_data="balance"), InlineKeyboardButton("📅 Deadline", callback_data="deadline")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )

# Main
if __name__ == "__main__":
    
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .build()
    )
    
    async def on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            print(f"Exception: {context.error}")
        except Exception:
            pass

    app.add_handler(CallbackQueryHandler(button_handler))

    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)

    app.add_error_handler(on_error)

    print("Bot is running...")
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        if sys.stdin and sys.stdin.isatty():
            try:
                input("Press Enter to exit...")
            except EOFError:
                pass
    except Exception as e:
        print(f"Error: {e}")
        if sys.stdin and sys.stdin.isatty():
            try:
                input("Press Enter to exit...")
            except EOFError:
                pass
