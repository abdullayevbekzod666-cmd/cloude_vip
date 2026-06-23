const { Telegraf, Markup } = require("telegraf");
const express = require("express");
const fs = require("fs");

const bot = new Telegraf("SENING_TOKENING");

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
            username: ctx.from.username,
            balance: 0,
            referrals: 0
        };
        saveData();
    }

    ctx.reply(
        "CLOUDE VIP PREMIUM",
        Markup.inlineKeyboard([
            [Markup.button.webApp("OPEN APP", "GITHUB_LINKING")]
        ])
    );
});

bot.launch();

app.use(express.static("public"));
app.listen(3000);
