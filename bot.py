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
    return InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data="reply_" + str(uid))]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_info = await context.bot.get_me()
    if is_owner(user):
        await update.message.reply_text("Bot ready! Link: https://t.me/" + bot_info.username)
        return
    await update.message.reply_text("Send your anonymous message (text, photo, video, file, audio, gif, sticker):")
    context.user_data["active"] = True

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    if is_owner(user):
        if context.user_data.get("replying"):
            await send_reply(update, context)
        return
    if not context.user_data.get("active"):
        await msg.reply_text("Send /start first.")
        return
    uid = user.id
    prefix = "New anonymous message:\n\n"
    try:
        if msg.text:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=prefix + msg.text, reply_markup=reply_kb(uid))
        elif msg.photo:
            await context.bot.send_photo(chat_id=OWNER_CHAT_ID, photo=msg.photo[-1].file_id, caption=prefix + (msg.caption or ""), reply_markup=reply_kb(uid))
        elif msg.video:
            await context.bot.send_video(chat_id=OWNER_CHAT_ID, video=msg.video.file_id, caption=prefix + (msg.caption or ""), reply_markup=reply_kb(uid))
        elif msg.audio:
            await context.bot.send_audio(chat_id=OWNER_CHAT_ID, audio=msg.audio.file_id, caption=prefix + (msg.caption or ""), reply_markup=reply_kb(uid))
        elif msg.voice:
            await context.bot.send_voice(chat_id=OWNER_CHAT_ID, voice=msg.voice.file_id, reply_markup=reply_kb(uid))
        elif msg.animation:
            await context.bot.send_animation(chat_id=OWNER_CHAT_ID, animation=msg.animation.file_id, caption=prefix + (msg.caption or ""), reply_markup=reply_kb(uid))
        elif msg.sticker:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=prefix + "[Sticker]", reply_markup=reply_kb(uid))
            await context.bot.send_sticker(chat_id=OWNER_CHAT_ID, sticker=msg.sticker.file_id)
        elif msg.document:
            await context.bot.send_document(chat_id=OWNER_CHAT_ID, document=msg.document.file_id, caption=prefix + (msg.caption or ""), reply_markup=reply_kb(uid))
        elif msg.video_note:
            await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=prefix + "[Video Note]", reply_markup=reply_kb(uid))
            await context.bot.send_video_note(chat_id=OWNER_CHAT_ID, video_note=msg.video_note.file_id)
        else:
            await msg.reply_text("Not supported.")
            return
        context.user_data["active"] = False
        await msg.reply_text("Sent! Send /start to send another.")
    except Exception as e:
        logger.error(str(e))
        await msg.reply_text("Error. Try again.")

async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sender_id = int(query.data.split("_")[1])
    context.user_data["replying"] = sender_id
    await query.message.reply_text("Write your reply:")

async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = context.user_data.get("replying")
    if not sender_id:
        return
    msg = update.message
    try:
        if msg.text:
            await context.bot.send_message(chat_id=sender_id, text="Reply: " + msg.text)
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
        await msg.reply_text("Reply sent!")
    except Exception as e:
        await msg.reply_text("Error: " + str(e))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_callback, pattern="^reply_"))
    all_media = filters.TEXT | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.ANIMATION | filters.Sticker.ALL | filters.Document.ALL | filters.VIDEO_NOTE
    app.add_handler(MessageHandler(all_media & ~filters.COMMAND, handle))
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()