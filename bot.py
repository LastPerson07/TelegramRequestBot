from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import config
import handlers

def print_banner():
    logo = [
        "██████╗ ██╗  ██╗ █████╗ ███╗   ██╗██████╗  █████╗ ██╗      ",
        "██╔══██╗██║  ██║██╔══██╗████╗  ██║██╔══██╗██╔══██╗██║      ",
        "██║  ██║███████║███████║██╔██╗ ██║██████╔╝███████║██║      ",
        "██║  ██║██╔══██║██╔══██║██║╚██╗██║██╔═══╝ ██╔══██║██║      ",
        "██████╔╝██║  ██║██║  ██║██║ ╚████║██║     ██║  ██║███████╗ ",
        "╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝  ╚═╝╚══════╝ "
    ]

    width = 66
    print("\n╔" + "═" * width + "╗")
    for line in logo:
        print(f"║   {line.ljust(width - 6)}   ║")
    print("║" + " " * width + "║")

    def center(text):
        pad = width - len(text)
        l = pad // 2
        r = pad - l
        return f"║{' ' * l}{text}{' ' * r}║"

    print(center("REQUEST BOT"))
    print(center("Powered by DHANPAL"))
    print("║" + " " * width + "║")
    print("╚" + "═" * width + "╝\n")

def main():
    print_banner()
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    config.load_deadline(app.bot_data)

    app.add_handler(CommandHandler("start", handlers.start_command))
    
    # FIX: Use patterns to distinguish between User and Admin buttons
    app.add_handler(CallbackQueryHandler(handlers.start_buttons, pattern="^(help|about|requests|upgrade|back)$"))
    app.add_handler(CallbackQueryHandler(handlers.admin_buttons, pattern="^(done|reject):"))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))

    print("✅ Request Bot is running...\n")
    app.run_polling(close_loop=False)

if name == "main":
    main()