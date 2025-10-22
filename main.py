from config import TOKEN
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes
)
from telegram import Update
from handler import (
    get_generate_conv_handler,
    button_handler,
    start,
    about
)

if __name__ == "__main__":

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .connection_pool_size(30)
        .pool_timeout(20)
        .build()
    )


    async def on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Error: {context.error}")
        try:
            chat_id = update.effective_chat.id
            await context.bot.send_message(chat_id, "⚠️ Please try again.")
        except:
            pass

    
    # Add conversation handler first (to handle query button and conversation)
    app.add_handler(get_generate_conv_handler())
    
    # Add other command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    
    # Add balance button handler
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^balance$"))

    app.add_error_handler(on_error)

    print("Bot is running...")
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\nStopped by user.")
