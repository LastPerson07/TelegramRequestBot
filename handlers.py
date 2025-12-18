from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode
from datetime import datetime, timedelta, timezone
import config
from config import ADMIN_CHAT_ID, logger
from ai_engine import analyze_request, get_witty_rejection, get_admin_acceptance_msg

START_IMAGE = "https://graph.org/file/YOUR_IMAGE_ID.jpg" # Ensure this is a valid URL

def get_eta(hours):
    d = datetime.now(timezone.utc) + timedelta(hours=hours)
    return f"{hours}h (by {d.strftime('%H:%M UTC')})"

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅ BACK TO MENU", callback_data="back")]])

def admin_keyboard(uid):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Done", callback_data=f"done:{uid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject:{uid}")
    ]])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (
        "🎬 NETFLIXIAN X — REQUEST BOT\n\n"
        "📝 Request movies or series naturally.\n"
        "Example: interstellar movie"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("🆘 HELP", callback_data="help"), InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")],
        [InlineKeyboardButton("⏱ MY REQUESTS", callback_data="requests"), InlineKeyboardButton("⭐ UPGRADE", callback_data="upgrade")]
    ])
    
    # Check if this is a message or a callback query
    if update.message:
        await update.message.reply_photo(photo=START_IMAGE, caption=caption, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.callback_query.message.edit_caption(caption=caption, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def start_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "back":
        await start_command(update, context)
        return

    text_map = {
        "help": "🆘 Send movie/series name naturally.\nAdmins will handle it.",
        "about": "ℹ️ Netflixian X Request Bot\nPowered by THE UPDATED GUYS 😎",
        "requests": "⏱ Your requests are being processed.",
        "upgrade": "⭐ Priority requests available.\nContact admin."
    }
    await q.message.edit_caption(caption=text_map[q.data], reply_markup=back_button())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    data = await analyze_request(update.message.text)
    
    if not data or data.get("intent") in ("chat", "unclear"):
        await update.message.reply_text(data.get("reply", "🙂") if data else "Something went wrong.")
        return

    title = data.get("title", "Unknown")
    hours = context.application.bot_data.get("deadline_hours", config.DEFAULT_DEADLINE_HOURS)

    await update.message.reply_text(f"📥 REQUEST RECEIVED\n\n🎬 {title}\n⏳ ETA: {get_eta(hours)}", parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🔔 NEW REQUEST\n👤 ID: {update.effective_user.id}\n🎬 {title}", reply_markup=admin_keyboard(update.effective_user.id))

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    action, uid = q.data.split(":")
    title = q.message.text.split("🎬")[-1].strip()

    if action == "done":
        msg = await get_admin_acceptance_msg(title)
        await q.edit_message_text(q.message.text + "\n\n✅ Fulfilled")
    else:
        msg = await get_witty_rejection(title)
        await q.edit_message_text(q.message.text + "\n\n❌ Rejected")

    try:
        await context.bot.send_message(uid, msg)
    except Exception as e:
        logger.warning(f"Could not notify user: {e}")