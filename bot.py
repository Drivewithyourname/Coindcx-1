import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler

# Your Telegram Bot Token
BOT_TOKEN = "7526934837:AAHqsEOl0NIwKtLX7BleUz9kywph-XqdvFA"

# CoinDCX API URL for USDT/INR price
COINDCX_URL = "https://public.coindcx.com/market_data/current_prices"

# Function to fetch the correct USDT selling price
def get_usdt_sell_price():
    try:
        response = requests.get(COINDCX_URL).json()
        sell_price = float(response.get("USDTINR", 0))  # Get correct sell price
        return sell_price
    except Exception as e:
        print("Error fetching price:", e)
        return None

# Function to calculate after-tax amount
def calculate_final_price(sell_price):
    TDS = 0.001  # 0.1% TDS deduction
    FEES = 0.002  # 0.2% trading fees
    GST = 0.18  # 18% GST on fees

    total_fees = sell_price * FEES
    gst_amount = total_fees * GST
    after_tax_price = sell_price - (sell_price * TDS) - total_fees - gst_amount

    return round(sell_price, 2), round(after_tax_price, 2)

# Command Handler for /price
async def price(update: Update, context):
    sell_price = get_usdt_sell_price()
    
    if sell_price:
        before_tax, after_tax = calculate_final_price(sell_price)
        message = (
            f"💰 USDT to INR Price 💰\n"
            f"1 USDT = {before_tax} INR\n\n"
            f"📌 Before Tax: {before_tax} INR\n"
            f"⚡ After Tax: {after_tax} INR"
        )
    else:
        message = "❌ Error fetching USDT price."

    await update.message.reply_text(message)

# Function to check price and alert users if it crosses 90.5 INR
async def check_price_threshold(application):
    while True:
        sell_price = get_usdt_sell_price()
        if sell_price and sell_price > 90.5:
            alert_message = f"🚀 USDT Price Alert 🚀\n1 USDT = {sell_price} INR\nSell Now!"
            
            # Send to all users who started the bot (Replace with actual user list)
            user_ids = [6381551315]  # Replace with actual user IDs from database
            for user_id in user_ids:
                await application.bot.send_message(chat_id=user_id, text=alert_message)

        await asyncio.sleep(60)  # Check every 60 seconds

# Main function to start bot
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handler
    app.add_handler(CommandHandler("price", price))

    # Start background task to monitor price
    app.create_task(check_price_threshold(app))

    print("Bot is running...")
    await app.run_polling()

# Run bot
if __name__ == "__main__":
    asyncio.run(main())
