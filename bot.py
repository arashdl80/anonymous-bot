import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = "arashdl"
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def is_owner(user):
    return user.username and user.username.lower() == OWNER_USERNAME.lower()

def reply_kb(uid):
    return InlineKeyboardMarkup([[InlineKeyboardButton("↩️ پاسخ", callback_data="reply_" + str(uid))]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_info = await context.bot.get_me()
    if is_owner(user):
        await update.message.reply_text("ربات آماده است!\nلینک: https://t.me/" + bot_info.username)
        return
    msg = "👤 *ربات پیام ناشناس*\n\nمی‌تونی به @arashdl پیام ناشناس بفرستی.\nهویتت کاملاً مخفی می‌مونه! ✉️"
    await update.message.reply_text(msg, parse_mode="Markdown")
    context.user_data["active"] = True

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if is_owner(user):
        if context.user_data.get("replying"):
            await send_reply(update, context)
        return
    if not context.user_data.get("active"):
        await msg.reply_text("ابتدا /start بزنید.")
        return
    uid = user.id
    prefix = "📩 *پیام ناشناس جدید:*\n\n"
    try:
        if msg.text:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=prefix + msg.text, parse_mode="Markdown", reply_markup=reply_kb(uid))
        elif msg.photo:
            await context.bot.send_photo(chat_id=OWNER_CHAT_ID, photo=msg.photo[-1].file_id, caption=prefix + (msg.caption or ""), parse_mode="Markdown", reply_markup=reply_kb(uid))
        elif msg.video:
            await context.bot.send_video(chat_id=OWNER_CHAT_ID, video=msg.video.file_id, caption=prefix + (msg.caption or ""), parse_mode="Markdown", reply_markup=reply_kb(uid))
        elif msg.audio:
            await context.bot.send_audio(chat_id=OWNER_CHAT_ID, audio=msg.audio.file_id, caption=prefix + (msg.caption or ""), parse_mode="Markdown", reply_markup=reply_kb(uid))
        elif msg.voice:
            await context.bot.send_voice(chat_id=OWNER_CHAT_ID, voice=msg.voice.file_id, reply_markup=reply_kb(uid))
        elif msg.animation:
            await context.bot.send_animation(chat_id=OWNER_CHAT_ID, animation=msg.animation.file_id, caption=prefix + (msg.caption or ""), parse_mode="Markdown", reply_markup=reply_kb(uid))
        elif msg.sticker:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=prefix + "[استیکر]", parse_mode="Markdown", reply_markup=reply_kb(uid))
            await context.bot.send_sticker(chat_id=OWNER_CHAT_ID, sticker=msg.sticker.file_id)
        elif msg.document:
            await context.bot.send_document(chat_id=OWNER_CHAT_ID, document=msg.document.file_id, caption=prefix + (msg.caption or ""), parse_mode="Markdown", reply_markup=reply_kb(uid))
        elif msg.video_note:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=prefix + "[ویدیو نوت]", parse_mode="Markdown", reply_markup=reply_kb(uid))
            await context.bot.send_video_note(chat_id=OWNER_CHAT_ID, video_note=msg.video_note.file_id)
        else:
            await msg.reply_text("این نوع محتوا پشتیبانی نمیشه.")
            return
        context.user_data["active"] = False
        await msg.reply_text("✅ پیام ارسال شد! برای ارسال پیام دیگه /start بزن.")
    except Exception as e:
        logger.error(str(e))
        await msg.reply_text("خطا در ارسال. دوباره امتحان کن.")

async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sender_id = int(query.data.split("_")[1])
    context.user_data["replying"] = sender_id
    await query.message.reply_text("✏️ پاسخت رو بنویس:")

async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = context.user_data.get("replying")
    if not sender_id:
        return
    msg = update.message
    prefix = "💬 *پاسخ:*\n\n"
    try:
        if msg.text:
            await context.bot.send_message(chat_id=sender_id, text=prefix + msg.text, parse_mode="Markdown")
        elif msg.photo:
            await context.bot.send_photo(chat_id=sender_id, photo=msg.photo[-1].file_id, caption=msg.caption or "")
        elif msg.video:
            await context.bot.send_video(chat_id=sender_id, video=msg.video.file_id, caption=msg.caption or "")
        elif msg.audio:
            await context.bot.send_audio(chat_id=sender_id, audio=msg.audio.file_id)
        elif msg.voice:
            await context.bot.send_voice(chat_id=sender_id, voice=msg.voice.file_id)
        elif msg.animation:
            await context.bot.send_animation(chat_id=sender_id, animation=msg.animation.file_id)
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=sender_id, sticker=msg.sticker.file_id)
        elif msg.document:
            await context.bot.send_document(chat_id=sender_id, document=msg.document.file_id)
        elif msg.video_note:
            await context.bot.send_video_note(chat_id=sender_id, video_note=msg.video_note.file_id)
        context.user_data["replying"] = None
        await msg.reply_text("✅ پاسخ ارسال شد!")
    except Exception as e:
        await msg.reply_text("خطا: " + str(e))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_callback, pattern="^reply_"))
    all_media = filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.ANIMATION | filters.Sticker.ALL | filters.Document.ALL | filters.VIDEO_NOTE
    app.add_handler(MessageHandler(all_media & ~filters.COMMAND, handle))
    logger.info("ربات شروع شد...")
    app.run_polling()

if __name__ == "__main__":
    main()