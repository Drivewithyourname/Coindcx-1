import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Your new bot token
BOT_TOKEN = "7441451800:AAG3YX7Bh1p5NeCkmG-QlZRn3KGIlkSlihw"

# Users who started the bot
subscribed_users = set()

# Fetch USDT price from CoinDCX
def get_usdt_price():
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url).json()
    for item in response:
        if item["market"] == "USDTINR":
            return float(item["last_price"])
    return None

# Calculate price before and after tax
def calculate_price():
    price = get_usdt_price()
    if not price:
        return None, None, None
    before_tax = price
    after_tax = round(before_tax * 0.997, 2)  # Assuming 0.3% tax deduction
    return price, before_tax, after_tax

# Command: /price
async def price(update: Update, context: CallbackContext):
    price, before_tax, after_tax = calculate_price()
    if price:
        message = (
            f"💰 *USDT to INR Price* 💰\n"
            f"1 USDT = {price:.2f} INR\n\n"
            f"📌 *Before Tax*: {before_tax:.2f} INR\n"
            f"⚡ *After Tax*: {after_tax:.2f} INR"
        )
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Error fetching price!")

# Command: /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    subscribed_users.add(user_id)
    await update.message.reply_text("✅ You've subscribed to price alerts!")

# Price threshold alert (auto-send if > 90.5 INR)
async def check_price_threshold(app):
    while True:
        price, _, _ = calculate_price()
        if price and price > 90.5:
            for user_id in subscribed_users:
                await app.bot.send_message(
                    chat_id=user_id,
                    text=f"🚀 USDT price is above 90.5 INR! Current: {price:.2f} INR"
                )
        await asyncio.sleep(30)  # Check every 30 seconds

# Main function
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    # Start price checker in background
    asyncio.create_task(check_price_threshold(app))

    print("Bot is running...")
    await app.run_polling()

# Fix for Render.com event loop issue
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
