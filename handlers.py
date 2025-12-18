import logging
import traceback
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode
from datetime import datetime, timedelta, timezone

import config
from config import ADMIN_CHAT_ID, logger
from ai_engine import analyze_request, get_witty_rejection, get_admin_acceptance_msg

# Using a more reliable direct link format
START_IMAGE = "https://graph.org/file/4dad0cc16f190468454ee.jpg"

def get_eta(hours):
    d = datetime.now(timezone.utc) + timedelta(hours=hours)
    return f"{hours}h (by {d.strftime('%H:%M UTC')})"

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ BACK TO MENU", callback_data="back")]])

def admin_keyboard(uid):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Done", callback_data=f"done:{uid}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject:{uid}")
    ]])

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and notify the admin."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.traceback)
    tb_string = "".join(tb_list)
    
    if ADMIN_CHAT_ID:
        try:
            # Send the first 4000 chars of the traceback to admin
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⚠️ <b>BOT ERROR</b>\n\n<code>{tb_string[-4000:]}</code>",
                parse_mode=ParseMode.HTML
            )
        except:
            pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (
        "🎬 <b>NETFLIXIAN X — REQUEST BOT</b>\n\n"
        "📝 Request movies or series naturally.\n"
        "Example: <i>interstellar movie</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD ME TO GROUP", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("🆘 HELP", callback_data="help"), InlineKeyboardButton("ℹ️ ABOUT", callback_data="about")],
        [InlineKeyboardButton("⏱️ MY REQUESTS", callback_data="requests"), InlineKeyboardButton("⭐️ UPGRADE", callback_data="upgrade")]
    ])
    
    try:
        if update.message:
            await update.message.reply_photo(
                photo=START_IMAGE, 
                caption=caption, 
                reply_markup=keyboard, 
                parse_mode=ParseMode.HTML
            )
        else:
            # If coming from a button, we edit the existing media caption
            await update.callback_query.message.edit_caption(
                caption=caption, 
                reply_markup=keyboard, 
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Failed to send/edit photo: {e}")
        # Fallback to plain text if photo fails
        if update.message:
            await update.message.reply_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.message.edit_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def start_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "back":
        await start_command(update, context)
        return

    text_map = {
        "help": "🆘 <b>HELP</b>\n\nSend the movie or series name naturally. Our AI will detect it and alert admins.",
        "about": "ℹ️ <b>ABOUT</b>\n\nNetflixian X Request Bot\nPowered by THE UPDATED GUYS 😎",
        "requests": "⏱️ <b>STATUS</b>\n\nYour requests are currently being processed by the team.",
        "upgrade": "⭐️ <b>PREMIUM</b>\n\nPriority requests and 1h ETA available. Contact admin."
        }
    
    # We edit the caption of the existing photo
    await q.message.edit_caption(
        caption=text_map.get(q.data, "Option not found."),
        reply_markup=back_button(),
        parse_mode=ParseMode.HTML
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    data = await analyze_request(update.message.text)
    
    if not data or data.get("intent") in ("chat", "unclear"):
        reply = data.get("reply", "🙂") if data else "I'm having trouble understanding. Try giving me a movie name!"
        await update.message.reply_text(reply)
        return

    title = data.get("title", "Unknown Title")
    hours = context.application.bot_data.get("deadline_hours", config.DEFAULT_DEADLINE_HOURS)

    await update.message.reply_text(
        f"📥 <b>REQUEST RECEIVED</b>\n\n🎬 <b>{title}</b>\n⏳ ETA: {get_eta(hours)}", 
        parse_mode=ParseMode.HTML
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID, 
        text=f"🔔 <b>NEW REQUEST</b>\n👤 User: <code>{update.effective_user.id}</code>\n🎬 <b>{title}</b>", 
        reply_markup=admin_keyboard(update.effective_user.id),
        parse_mode=ParseMode.HTML
    )

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    try:
        action, uid = q.data.split(":")
        # Robustly extract title even if format changed
        if "🎬" in q.message.text:
            title = q.message.text.split("🎬")[-1].strip()
        else:
            title = "Unknown Content"

        if action == "done":
            msg = await get_admin_acceptance_msg(title)
            status_text = "✅ Fulfilled"
        else:
            msg = await get_witty_rejection(title)
            status_text = "❌ Rejected"

        await q.edit_message_text(f"{q.message.text}\n\n{status_text}", parse_mode=ParseMode.HTML)
        await context.bot.send_message(uid, msg)
        
    except Exception as e:
        logger.warning(f"Admin action failed: {e}")
