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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    bot_username = (await context.bot.get_me()).username

    if user.username and user.username.lower() == OWNER_USERNAME.lower():
        await update.message.reply_text(
            "👋 سلام! این ربات ناشناس توست.\n"
            f"🔗 لینک اشتراک‌گذاری:\n`https://t.me/{bot_username}?start=anon`\n\n"
            "هر پیام ناشناسی که کاربران بفرستن اینجا می‌رسه.",
            parse_mode="Markdown",
        )
        return

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