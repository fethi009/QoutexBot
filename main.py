# main.py - بوت تداول لـ Qoutex على Render

import os
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import ta.momentum

# 🔐 التوكن من متغيرات البيئة
TOKEN = os.getenv("7147189698:AAEhuUJ85ZVmM57eKM1-2rMOccOnNGfXgUA")
if not TOKEN:
    raise ValueError("❌ ضع التوكن في متغيرات البيئة!")

# 📊 أزواج Qoutex
SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "XAUUSD": "GC=X",      # الذهب
    "BTCUSD": "BTC-USD",   # البيتكوين
}

# 📊 دالة حساب RSI
def get_rsi(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="5m", auto_adjust=True)
        if len(data) < 14:
            return None
        rsi_indicator = ta.momentum.RSIIndicator(data['Close'], window=14)
        rsi = rsi_indicator.rsi().iloc[-1]
        return round(rsi, 2)
    except:
        return None

# 🏁 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا! أنا بوت التداول لـ Qoutex\n\n"
        "📌 الأوامر:\n"
        "/price <رمز> - مثل EURUSD\n"
        "/rsi <رمز> - مؤشر RSI\n"
        "/signal - أرسل إشارة تداول"
    )

# 📈 /price EURUSD
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📌 استخدم: /price EURUSD")
        return
    symbol = context.args[0].upper()
    yf_symbol = SYMBOLS.get(symbol)
    if not yf_symbol:
        await update.message.reply_text("❌ غير مدعوم. جرب: EURUSD, XAUUSD")
        return
    try:
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period="1d")
        price = data['Close'].iloc[-1]
        await update.message.reply_text(f"💰 سعر {symbol} = {price:.5f}")
    except:
        await update.message.reply_text("❌ تعذر جلب السعر.")

# 📊 /rsi EURUSD
async def rsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📌 استخدم: /rsi EURUSD")
        return
    symbol = context.args[0].upper()
    yf_symbol = SYMBOLS.get(symbol)
    if not yf_symbol:
        await update.message.reply_text("❌ غير مدعوم")
        return
    rsi_value = get_rsi(yf_symbol)
    if rsi_value is None:
        await update.message.reply_text("لا توجد بيانات كافية.")
    else:
        await update.message.reply_text(f"📊 RSI لـ {symbol} = {rsi_value}")

# 🚀 /signal BUY EURUSD
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = ' '.join(context.args)
    if not user_msg:
        await update.message.reply_text("📌 مثال: /signal BUY EURUSD CALL 5M")
        return
    await update.message.reply_text(f"🎯 إشارة: {user_msg}\n\n✅ افتح Qoutex وادخل يدويًا.")

# 🚀 تشغيل البوت
if __name__ == '__main__':
    print("🚀 البوت يعمل على Render...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("rsi", rsi))
    app.add_handler(CommandHandler("signal", signal))

    app.run_polling()
