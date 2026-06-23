const { Telegraf, Markup } = require("telegraf");
const express = require("express");
const fs = require("fs");

const bot = new Telegraf("8135606663:AAHqwY3_SXSuIV8WBLMwwvorpP5sp2jhC2c");
const app = express();

let users = {};

if (fs.existsSync("database.json")) {
    users = JSON.parse(fs.readFileSync("database.json"));
}

function saveData() {
    fs.writeFileSync("database.json", JSON.stringify(users, null, 2));
}

bot.start((ctx) => {
    if (!users[ctx.from.id]) {
        users[ctx.from.id] = {
            username: ctx.from.username || "NoUsername",
            balance: 0,
            referrals: 0
        };
        saveData();
    }

    ctx.reply(
        "🔥 CLOUDE VIP PREMIUM 🔥",
        Markup.inlineKeyboard([
            [
                Markup.button.webApp(
                    "🚀 OPEN APP",
                    "https://abdullayevbekzod666-cmd.github.io/cloude_vip/"
                )
            ]
        ])
    );
});

bot.on("photo", async (ctx) => {
    await ctx.reply("✅ Screenshot qabul qilindi. Admin tekshiradi.");
});

bot.launch();

app.use(express.static("public"));

app.listen(3000, () => {
    console.log("Server ishlayapti...");
});
