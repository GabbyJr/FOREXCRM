from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
TOKEN = "8545485295:AAGbO7hrseQd5azAz1tB5h7G7jaUvTt968E"   # ← CHANGE THIS TO YOUR REAL TOKEN
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# Fake database
clients = {}   # telegram_id → info
agents = {}    # agent_code → agent name

# Register your test agent code
agents["GABBY001"] = "Gabby Jr"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args                     # This catches ?start=GABBY001

    referral_code = None
    if args:
        referral_code = args[0].upper()

    clients[user_id] = {
        "name": update.effective_user.first_name,
        "balance": 0,
        "agent": referral_code or "DIRECT"
    }

    welcome = f"Welcome {update.effective_user.first_name}!\n"
    if referral_code and referral_code in agents:
        welcome += f"You are under agent: {agents[referral_code]}"
    else:
        welcome += "You came directly!"

    keyboard = [
        [InlineKeyboardButton("Deposit", callback_data="deposit")],
        [InlineKeyboardButton("Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("Check Balance", callback_data="balance")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome + "\n\nWhat do you want?", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "deposit":
        await query.edit_message_text(
            "Send money to:\n"
            "M-Pesa: 0655-123-456 (John King)\n\n"
            "After sending, reply here with the amount in USD\n"
            "Example: 100"
        )
        context.user_data["waiting"] = "deposit"

    elif query.data == "withdraw":
        balance = clients.get(user_id, {}).get("balance", 0)
        await query.edit_message_text(
            f"Your balance: ${balance}\n\n"
            "How much do you want to withdraw? (USD)\n"
            "Example: 80"
        )
        context.user_data["waiting"] = "withdraw"

    elif query.data == "balance":
        balance = clients.get(user_id, {}).get("balance", 0)
        await query.edit_message_text(f"Your current balance: ${balance}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if context.user_data.get("waiting") == "deposit":
        try:
            amount = float(text)
            clients[user_id]["balance"] += amount
            await update.message.reply_text(
                f"Received ${amount}!\n"
                "Agent notified — your trading account will be funded in < 2 min!\n"
                f"New balance: ${clients[user_id]['balance']}"
            )
        except:
            await update.message.reply_text("Please send only the number (e.g. 100)")
        context.user_data["waiting"] = None

    elif context.user_data.get("waiting") == "withdraw":
        try:
            amount = float(text)
            if amount <= clients[user_id]["balance"]:
                clients[user_id]["balance"] -= amount
                await update.message.reply_text(
                    f"Withdrawal ${amount} approved!\n"
                    "Your agent will send to your M-Pesa soon.\n"
                    f"Remaining: ${clients[user_id]['balance']}"
                )
            else:
                await update.message.reply_text("Not enough balance!")
        except:
            await update.message.reply_text("Please send only the number")
        context.user_data["waiting"] = None


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running and onboarding is READY!")
    app.run_polling()


if __name__ == "__main__":
    main()