import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8135606663:AAFyqQR_5_4nnRX-fK-adzJTGysQOBc1s8U")
GROUP_ID = int(os.environ.get("GROUP_ID", "-1002951040050"))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8068983911"))
WEBAPP_URL = "https://abdullayevbekzod666.github.io/cloude_vip/cloude_vip_webapp.html"

logging.basicConfig(level=logging.INFO)

# Pending users (screenshot yuborgan, tasdiq kutayotganlar)
pending_users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[
        InlineKeyboardButton(
            "💎 VIP Obuna olish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Salom, {user.first_name}! 👋\n\n"
        "👑 *CLOUDE VIP PREMIUM* ga xush kelibsiz!\n\n"
        "🔐 Yopiq VIP kanalga kirish uchun obuna oling.\n\n"
        "⬇️ Quyidagi tugmani bosing va tarifni tanlang:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Foydalanuvchini pending ga qo'shish
    pending_users[user.id] = {
        "name": user.first_name,
        "username": f"@{user.username}" if user.username else "username yo'q"
    }
    
    # Adminga xabar yuborish
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=(
            f"💳 *Yangi to'lov skrinshoti!*\n\n"
            f"👤 Ism: {user.first_name}\n"
            f"🔗 Username: @{user.username if user.username else 'yoq'}\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"✅ Tasdiqlash: `/approve {user.id}`\n"
            f"❌ Rad etish: `/reject {user.id}`"
        ),
        parse_mode="Markdown"
    )
    
    await update.message.reply_text(
        "✅ Skrinshot qabul qilindi!\n\n"
        "⏳ Admin 24 soat ichida tekshiradi va siz VIP kanalga qo'shilasiz.\n\n"
        "📞 Savol bo'lsa: @CLOUDE_SOFT"
    )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Foydalanish: /approve USER_ID")
        return
    
    user_id = int(context.args[0])
    
    try:
        # Guruhga qo'shish
        await context.bot.unban_chat_member(chat_id=GROUP_ID, user_id=user_id)
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            member_limit=1
        )
        
        # Foydalanuvchiga xabar
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 *Tabriklaymiz! To'lovingiz tasdiqlandi!*\n\n"
                "👑 VIP kanalga kirish uchun quyidagi tugmani bosing:\n\n"
                f"🔗 {invite_link.invite_link}\n\n"
                "⚠️ Bu link bir marta ishlaydi!"
            ),
            parse_mode="Markdown"
        )
        
        await update.message.reply_text(f"✅ {user_id} tasdiqlandi va guruhga qo'shildi!")
        
        if user_id in pending_users:
            del pending_users[user_id]
            
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Foydalanish: /reject USER_ID")
        return
    
    user_id = int(context.args[0])
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ *Afsuski, to'lovingiz tasdiqlanmadi.*\n\n"
                "Sabab: To'lov cheki noto'g'ri yoki summa kam.\n\n"
                "📞 Murojaat: @CLOUDE_SOFT"
            ),
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"✅ {user_id} rad etildi!")
        
        if user_id in pending_users:
            del pending_users[user_id]
            
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def pending_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not pending_users:
        await update.message.reply_text("📋 Kutayotgan foydalanuvchilar yo'q.")
        return
    
    text = "📋 *Kutayotgan foydalanuvchilar:*\n\n"
    for uid, info in pending_users.items():
        text += f"👤 {info['name']} ({info['username']}) - ID: `{uid}`\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))
    app.add_handler(CommandHandler("pending", pending_list))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
