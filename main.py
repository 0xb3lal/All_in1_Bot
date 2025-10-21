import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler
from handler import button_handler, start
from config import TOKEN

if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .build()
    )

    async def on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Error: {context.error}")

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(on_error)

    print("Bot is running...")
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        if sys.stdin and sys.stdin.isatty():
            input("Press Enter to exit...")
