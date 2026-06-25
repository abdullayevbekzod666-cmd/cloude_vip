import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8916800325:AAEPAHaUDwMJs6WhoTjwmL13W88h7KzS20Y")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8068983911"))
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://abdullayevbekzod666-cmd.github.io/cloude_vip/cloude_vip_webapp.html")

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_data()

def get_user(user_id, name="Foydalanuvchi"):
    key = str(user_id)
    if key not in users:
        users[key] = {
            "name": name,
            "balance": 0,
            "refs": 0,
            "referrer_id": None,
            "vip": None
        }
        save_data()
    return users[key]

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
        save_data()
        try:
            await context.bot.send_message(
                referrer_id,
                f"Yangi do'st qo'shildi! Endi sizda {ref_u['refs']} ta referal bor."
            )
        except:
            pass

    save_data()
    ref_code = f"ref_{user_id}"
    webapp_url = f"{WEBAPP_URL}?user_id={user_id}&ref={ref_code}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 CLOUDE VIP ni ochish", web_app=WebAppInfo(url=webapp_url))],
    ])

    await update.message.reply_text(
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

    target_id = str(context.args[0])
    amount = int(context.args[1])

    u = get_user(target_id)
    u["balance"] += amount
    save_data()

    await update.message.reply_text(f"{target_id} foydalanuvchiga {amount:,} so'm qo'shildi.")
    try:
        await context.bot.send_message(
            int(target_id),
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
    proxy = "http://proxy.pythonanywhere.com:3128"
    app = Application.builder().token(BOT_TOKEN).proxy(proxy).get_updates_proxy(proxy).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", admin_confirm))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
