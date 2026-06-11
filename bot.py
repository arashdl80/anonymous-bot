import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = "arashdl"
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

REPLY_KEYBOARD = lambda uid: InlineKeyboardMarkup(
    [[InlineKeyboardButton("↩️ پاسخ", callback_data=f"reply_{uid}")]]
)

def is_owner(user):
    return user.username and user.username.lower() == OWNER_USERNAME.lower()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    bot_username = (await context.bot.get_me()).username

    if is_owner(user):
        await update.message.reply_text(
            "👋 سلام! این ربات ناشناس توست.\n"
            f"🔗 لینک اشتراک‌گذاری:\n`https://t.me/{bot_username}`\n\n"
            "هر پیام ناشناسی که کاربران بفرستن اینجا می‌رسه.",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"👤 *ربات پیام ناشناس*\n\n"
        f"می‌تونی به @{OWNER_USERNAME} پیام ناشناس بفرستی.\n"
        "هویتت کاملاً مخفی می‌مونه! ✉️\n\n"
        "متن، عکس، فایل، آهنگ، ویدیو یا گیف بفرست:",
        parse_mode="Markdown",
    )
    context.user_data["waiting_for_message"] = True


async def receive_any(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    msg = update.message

    if is_owner(user):
        if context.user_data.get("is_owner_replying"):
            await owner_reply_media(update, context)
        return

    if not context.user_data.get("waiting_for_message"):
        await msg.reply_text("لطفاً ابتدا /start بزن.")
        return

    if not OWNER_CHAT_ID:
        await msg.reply_text("❌ ربات هنوز تنظیم نشده.")
        return

    uid = user.id
    caption_prefix = "📩 *پیام ناشناس جدید:*\n\n"

    try:
        if msg.text:
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=f"{caption_prefix}{msg.text}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.photo:
            await context.bot.send_photo(
                chat_id=OWNER_CHAT_ID,
                photo=msg.photo[-1].file_id,
                caption=f"{caption_prefix}{msg.caption or ''}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.video:
            await context.bot.send_video(
                chat_id=OWNER_CHAT_ID,
                video=msg.video.file_id,
                caption=f"{caption_prefix}{msg.caption or ''}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.audio:
            await context.bot.send_audio(
                chat_id=OWNER_CHAT_ID,
                audio=msg.audio.file_id,
                caption=f"{caption_prefix}{msg.caption or ''}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.voice:
            await context.bot.send_voice(
                chat_id=OWNER_CHAT_ID,
                voice=msg.voice.file_id,
                caption=f"{caption_prefix}{msg.caption or ''}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.animation:
            await context.bot.send_animation(
                chat_id=OWNER_CHAT_ID,
                animation=msg.animation.file_id,
                caption=f"{caption_prefix}{msg.caption or ''}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.sticker:
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=f"{caption_prefix}[استیکر]",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
            await context.bot.send_sticker(
                chat_id=OWNER_CHAT_ID,
                sticker=msg.sticker.file_id,
            )
        elif msg.document:
            await context.bot.send_document(
                chat_id=OWNER_CHAT_ID,
                document=msg.document.file_id,
                caption=f"{caption_prefix}{msg.caption or ''}",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
        elif msg.video_note:
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=f"{caption_prefix}[ویدیو نوت]",
                parse_mode="Markdown",
                reply_markup=REPLY_KEYBOARD(uid),
            )
            await context.bot.send_video_note(
                chat_id=OWNER_CHAT_ID,
                video_note=msg.video_note.file_id,
            )
        else:
            await msg.reply_text("❌ این نوع محتوا پشتیبانی نمیشه.")
            return

        context.user_data["waiting_for_message"] = False
        await msg.reply_text(
            "✅ پیامت با موفقیت ارسال شد!\n"
            "برای ارسال پیام دیگه /start بزن."
        )

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await msg.reply_text("❌ خطا در ارسال. دوباره امتحان کن.")


async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    sender_id = int(query.data.split("_")[1])
    context.user_data["replying_to"] = sender_id
    context.user_data["is_owner_replying"] = True

    await query.message.reply_text("✏️ پاسخت رو بنویس (متن، عکس، فایل و... قبوله):")


async def owner_reply_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sender_id = context.user_data.get("replying_to")
    if not sender_id:
        return

    msg = update.message
    prefix = "💬 *پاسخ از صاحب ربات:*\n\n"

    try:
        if msg.text:
            await context.bot.send_message(chat_id=sender_id, text=f"{prefix}{msg.text}", parse_mode="Markdown")
        elif msg.photo:
            await context.bot.send_photo(chat_id=sender_id, photo=msg.photo[-1].file_id, caption=f"{prefix}{msg.caption or ''}", parse_mode="Markdown")
        elif msg.video:
            await context.bot.send_video(chat_id=sender_id, video=msg.video.file_id, caption=f"{prefix}{msg.caption or ''}", parse_mode="Markdown")
        elif msg.audio:
            await context.bot.send_audio(chat_id=sender_id, audio=msg.audio.file_id, caption=f"{prefix}{msg.caption or ''}", parse_mode="Markdown")
        elif msg.voice:
            await context.bot.send_voice(chat_id=sender_id, voice=msg.voice.file_id)
        elif msg.animation:
            await context.bot.send_animation(chat_id=sender_id, animation=msg.animation.file_id)
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=sender_id, sticker=msg        return

    await update.message.reply_text(
        f"👤 *ربات پیام ناشناس*\n\n"
        f"می‌تونی به @{OWNER_USERNAME} پیام ناشناس بفرستی.\n"
        "هویتت کاملاً مخفی می‌مونه! ✉️\n\n"
        "پیامت رو بنویس:",
        parse_mode="Markdown",
    )
    context.user_data["waiting_for_message"] = True


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if user.username and user.username.lower() == OWNER_USERNAME.lower():
        await update.message.reply_text("شما صاحب ربات هستید. این پیام ارسال نشد.")
        return

    if not context.user_data.get("waiting_for_message"):
        await update.message.reply_text("لطفاً ابتدا /start بزن.")
        return

    text = update.message.text

    if not OWNER_CHAT_ID:
        await update.message.reply_text("❌ ربات هنوز تنظیم نشده. لطفاً بعداً امتحان کن.")
        return

    keyboard = [[InlineKeyboardButton("↩️ پاسخ", callback_data=f"reply_{update.effective_user.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=OWNER_CHAT_ID,
        text=f"📩 *پیام ناشناس جدید:*\n\n{text}",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

    context.user_data["waiting_for_message"] = False
    await update.message.reply_text(
        "✅ پیامت با موفقیت ارسال شد!\n"
        "برای ارسال پیام دیگه /start بزن."
    )


async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    sender_id = int(query.data.split("_")[1])
    context.user_data["replying_to"] = sender_id
    context.user_data["is_owner_replying"] = True

    await query.message.reply_text("✏️ پاسخت رو بنویس:")


async def owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("is_owner_replying"):
        return

    sender_id = context.user_data.get("replying_to")
    if not sender_id:
        return

    try:
        await context.bot.send_message(
            chat_id=sender_id,
            text=f"💬 *پاسخ از صاحب ربات:*\n\n{update.message.text}",
            parse_mode="Markdown",
        )
        context.user_data["is_owner_replying"] = False
        await update.message.reply_text("✅ پاسخ ارسال شد!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال پاسخ: {e}")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(reply_callback, pattern="^reply_"))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(username=OWNER_USERNAME),
            owner_reply,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_message,
        )
    )

    logger.info("ربات شروع به کار کرد...")
    app.run_polling()


if __name__ == "__main__":
    main()
