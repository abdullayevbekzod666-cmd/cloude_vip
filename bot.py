import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://abdullayevbekzod666-cmd.github.io/cloude_vip/cloude_vip_webapp.html")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CLOUDE_SOFT")

users = {}
payments = {}

def get_user(user_id, name="Foydalanuvchi"):
    if user_id not in users:
        users[user_id] = {
            "name": name,
            "balance": 0,
            "refs": 0,
            "referrer_id": None,
            "vip": None
        }
    return users[user_id]

def get_discount(user_id):
    u = get_user(user_id)
    refs = u["refs"]
    if refs >= 30:
        return 15
    elif refs >= 20:
        return 10
    elif refs >= 10:
        return 5
    return 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    name = user.full_name or "Foydalanuvchi"

    referrer_id = None
    if context.args:
        arg = context.args[0]
        if arg.startswith("ref_"):
            try:
                referrer_id = int(arg.replace("ref_", ""))
            except:
                pass

    u = get_user(user_id, name)
    u["name"] = name

    if referrer_id and referrer_id != user_id and u["referrer_id"] is None:
        u["referrer_id"] = referrer_id
        ref_u = get_user(referrer_id)
        ref_u["refs"] += 1
        discount = get_discount(referrer_id)
        try:
            await context.bot.send_message(
                referrer_id,
                f"Yangi do'st qo'shildi! Endi sizda {ref_u['refs']} ta referal bor.\n"
                f"Joriy chegirma: {discount}%"
            )
        except:
            pass

    ref_code = f"ref_{user_id}"
    webapp_url = f"{WEBAPP_URL}?user_id={user_id}&ref={ref_code}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 CLOUDE VIP ni ochish", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("💰 Balansim", callback_data="balance"),
         InlineKeyboardButton("👥 Referallarim", callback_data="refs")],
        [InlineKeyboardButton("🏆 Top o'yinchilar", callback_data="top")]
    ])

    await update.message.reply_text(
        f"Assalomu alaykum, {name}!\n\n"
        f"💎 CLOUDE VIP PREMIUM botiga xush kelibsiz!\n\n"
        f"👇 Boshlash uchun tugmani bosing:",
        reply_markup=keyboard
    )

async def balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    u = get_user(user_id)
    discount = get_discount(user_id)
    vip_status = u["vip"] or "Yoq"

    text = (
        f"💰 Balansingiz: {u['balance']:,} so'm\n"
        f"👥 Referallar: {u['refs']} ta\n"
        f"🎁 Chegirma: {discount}%\n"
        f"🏅 VIP status: {vip_status}\n\n"
        f"Balansni to'ldirish uchun WebApp'ni oching."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard)

async def refs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    u = get_user(user_id)
    discount = get_discount(user_id)
    bot_info = await context.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    text = (
        f"👥 Referal tizimi\n\n"
        f"Sizning havolangiz:\n{ref_link}\n\n"
        f"Statistika:\n"
        f"Taklif qilinganlar: {u['refs']} ta\n"
        f"Joriy chegirma: {discount}%\n\n"
        f"Chegirma darajalari:\n"
        f"10 ta do'st - 5%\n"
        f"20 ta do'st - 10%\n"
        f"30 ta do'st - 15%"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard)

async def top_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    sorted_users = sorted(users.items(), key=lambda x: x[1]["refs"], reverse=True)[:10]

    medals = ["🥇", "🥈", "🥉"]
    prizes = [120, 90, 60]

    text = "🏆 Top 10 o'yinchilar\n\n"
    for i, (uid, u) in enumerate(sorted_users):
        medal = medals[i] if i < 3 else f"{i+1}."
        prize = f" - {prizes[i]} UC" if i < 3 else ""
        text += f"{medal} {u['name']} - {u['refs']} referal{prize}\n"

    if not sorted_users:
        text += "Hali hech kim yo'q. Birinchi bo'ling!"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard)

async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = query.from_user
    name = user.full_name or "Foydalanuvchi"
    ref_code = f"ref_{user_id}"
    webapp_url = f"{WEBAPP_URL}?user_id={user_id}&ref={ref_code}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 CLOUDE VIP ni ochish", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("💰 Balansim", callback_data="balance"),
         InlineKeyboardButton("👥 Referallarim", callback_data="refs")],
        [InlineKeyboardButton("🏆 Top o'yinchilar", callback_data="top")]
    ])
    await query.edit_message_text(
        f"Assalomu alaykum, {name}!\n\n"
        f"💎 CLOUDE VIP PREMIUM botiga xush kelibsiz!\n\n"
        f"👇 Boshlash uchun tugmani bosing:",
        reply_markup=keyboard
    )

async def admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz!")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Ishlatish: /confirm <user_id> <summa>\n"
            "Misol: /confirm 123456789 30000"
        )
        return

    target_id = int(context.args[0])
    amount = int(context.args[1])

    u = get_user(target_id)
    u["balance"] += amount

    await update.message.reply_text(f"{target_id} foydalanuvchiga {amount:,} so'm qo'shildi.")
    try:
        await context.bot.send_message(
            target_id,
            f"To'lovingiz tasdiqlandi!\n\n"
            f"Hisobingizga {amount:,} so'm qo'shildi.\n"
            f"VIP sotib olish uchun botni oching."
        )
    except:
        pass

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz!")
        return

    total_users = len(users)
    total_balance = sum(u["balance"] for u in users.values())
    vip_users = sum(1 for u in users.values() if u["vip"])

    await update.message.reply_text(
        f"Bot statistikasi:\n\n"
        f"Jami foydalanuvchilar: {total_users}\n"
        f"VIP foydalanuvchilar: {vip_users}\n"
        f"Jami balans: {total_balance:,} so'm"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    name = user.full_name or "Foydalanuvchi"

    await update.message.reply_text(
        "Rasmingiz qabul qilindi! Admin tekshirib, tez orada balansingizni to'ldiradi."
    )

    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"Yangi to'lov screenshoti!\n\n"
            f"Foydalanuvchi: {name}\n"
            f"ID: {user_id}\n\n"
            f"Tasdiqlash uchun: /confirm {user_id} <summa>"
        )
        await context.bot.forward_message(ADMIN_ID, update.message.chat_id, update.message.message_id)
    except:
        pass

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Buyruqni tushunmadim. /start ni bosing.")

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", admin_confirm))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(balance_callback, pattern="^balance$"))
    app.add_handler(CallbackQueryHandler(refs_callback, pattern="^refs$"))
    app.add_handler(CallbackQueryHandler(top_callback, pattern="^top$"))
    app.add_handler(CallbackQueryHandler(back_callback, pattern="^back$"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
