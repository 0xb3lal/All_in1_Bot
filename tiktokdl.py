import os
import yt_dlp
import asyncio
from telegram import Update, ChatAction
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters


async def send_chat_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action=ChatAction.TYPING, delay=1.5):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
    await asyncio.sleep(delay)


async def show_fake_progress(update: Update, context: ContextTypes.DEFAULT_TYPE, delay=0.8, start_msg="Downloading...\n"):
    progress_states = [
        "█▒▒▒▒▒▒▒▒▒ 10%",
        "██▒▒▒▒▒▒▒▒ 20%",
        "███▒▒▒▒▒▒▒ 30%",
        "████▒▒▒▒▒▒ 40%",
        "█████▒▒▒▒▒ 50%",
        "██████▒▒▒▒ 60%",
        "███████▒▒▒ 70%",
        "████████▒▒ 80%",
        "█████████▒ 90%",
        "██████████ 100%"
    ]
    msg = await update.message.reply_text(f"{start_msg}\n{progress_states[0]}")
    for state in progress_states[1:]:
        await asyncio.sleep(delay)
        await msg.edit_text(f"{start_msg}\n{state}")
    await msg.edit_text(f"<b>Done ✔️</b>\n\n{progress_states[-1]}", parse_mode="HTML")


async def tiktok_downloader(link, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'merge_output_format': 'mp4',
        'concurrent_fragment_downloads': 3,
        'quiet': True,
    }
    os.makedirs('downloads', exist_ok=True)
    try:
        await send_chat_action(update, context, ChatAction.UPLOAD_VIDEO, delay=1)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            await show_fake_progress(update, context, delay=1.5, start_msg="Downloading...")
            filename = ydl.prepare_filename(info)
        file_size = os.path.getsize(filename)
        if file_size > 50 * 1024 * 1024:
            await update.message.reply_text("⚠️ Video too large for Telegram (over 50MB).")
            return None
        return filename
    except Exception as e:
        print(f"[!] Download error: {e}")
        await update.message.reply_text("⚠️ Failed to download video. Try again later.")
        return None


async def start_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uname = update.effective_user.first_name
    username = update.effective_user.username
    if username == "belalammar":
        msg = f"Welcome Back <b>Admin 👋</b>\n\nSend The Video <b>Link ↘</b>"
    else:
        msg = f"Hello <b>{uname}</b>, Welcome To Bot 👋\n\nSend The Video <b>Link ↘</b>"
    await send_chat_action(update, context, ChatAction.TYPING, delay=1)
    await update.message.reply_text(msg, parse_mode="HTML")


async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith("https"):
        await update.message.reply_text("Invalid link ❗")
        return
    file_name = await tiktok_downloader(text, update, context)
    if not file_name:
        return
    with open(file_name, "rb") as video:
        await update.message.reply_video(video, caption="<b>Done ✔️</b>", parse_mode="HTML")
    os.remove(file_name)


def register_tiktok_handlers(app):

    app.add_handler(CommandHandler("tiktok", start_tiktok))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
