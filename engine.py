import os
import yfinance as yf
import pandas as pd
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסרים פרטי התחברות לטלגרם")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("הודעה נשלחה בהצלחה לטלגרם! 📱")
        else:
            print(f"שליחת הודעה נכשלה: {response.text}")
    except Exception as e:
        print(f"שגיאה בשליחת הודעה: {e}")

# רשימת מניות ממוקדת שרצה מהר ובלי תקיעות
def get_stock_universe():
    return [
        'CRWD', 'PLTR', 'DDOG', 'SNOW', 'PATH', 'NET', 'ZS', 'ANET', 'UBER', 'RBLX',
        'MDB', 'HUBS', 'BILL', 'CFLT', 'GTLB', 'DUOL', 'TOST', 'CELH', 'AXON', 'FTNT'
    ]

universe_tickers = get_stock_universe()
print(f"סך הכל מניות לבדיקה היום: {len(universe_tickers)}")

rising_stars_found = []

for ticker in universe_tickers:
    print(בודק מניה: {ticker}...)
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period='6mo')
        
        info = stock.info
        market_cap = info.get('marketCap', 0) or 0
        trailing_eps = info.get('trailingEps', 0) or 0
        avg_volume = info.get('averageVolume', 0) or 0
        
        if not df.empty and len(df) >= 50:
            current_price = df['Close'].iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            
            is_large_cap = market_cap >= 18_000_000_000
            is_profitable = trailing_eps > 0
            has_liquidity = avg_volume > 250_000
            is_above_ma50 = current_price > ma50
            
            if is_large_cap and is_profitable and has_liquidity and is_above_ma50:
                rising_stars_found.append(f"*{ticker}* | שווי שוק: ${round(market_cap/1e9, 1)}B | מחיר: ${round(current_price, 2)}")
                print(f"🔥 מצאנו כוכב עולה: {ticker}")
    except Exception as e:
        print(f"דילוג על {ticker} עקב בעיה זמנית: {e}")
        continue

# שליחת סיכום לטלגרם תמיד, כדי שנראה שהגיע לסוף
if rising_stars_found:
    alert_message = "🚀 *התראת כוכבים עולים (Rising Stars):*\n\n" + "\n".join(rising_stars_found)
    send_telegram_alert(alert_message)
else:
    print("\nהסריקה הסתיימה. שולח עדכון לטלגרם...")
    send_telegram_alert("🤖 *רובוט הסריקה:* הסריקה היומית הסתיימה בהצלחה. אין מניות חדשות שעברו את התנאים היום.")
