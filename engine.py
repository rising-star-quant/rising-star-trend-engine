import os
import yfinance as yf
import pandas as pd
import requests

# חיבור לטלגרם
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ חסרים פרטי התחברות לטלגרם")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("הודעה נשלחה בהצלחה לטלגרם! 📱")
        else:
            print(f"שליחת הודעה נכשלה: {response.text}")
    except Exception as e:
        print(f"שגיאה בשליחת הודעה: {e}")

# רשימת מניות רחבה ויציבה שסורקת ענקיות צמיחה וטכנולוגיה (ללא תלות באתרים חיצוניים חסומים)
def get_stock_universe():
    return [
        'CRWD', 'PLTR', 'DDOG', 'SNOW', 'PATH', 'NET', 'ZS', 'ANET', 'UBER', 'RBLX',
        'MDB', 'HUBS', 'BILL', 'CFLT', 'GTLB', 'DUOL', 'TOST', 'CELH', 'AXON', 'FTNT',
        'PANW', 'DECK', 'EXLS', 'MRVL', 'SMCI', 'ARM', 'ON', 'TTD', 'PCTY', 'GDDY',
        'SHOP', 'SQ', 'MELI', 'ROKU', 'PINS', 'TWLO', 'ESTC', 'APPN', 'FSLY', 'ZI'
    ]

universe_tickers = get_stock_universe()
print(f"סך הכל מניות לבדיקה היום: {len(universe_tickers)}")

rising_stars_found = []

# סריקת המניות אחת אחת
for ticker in universe_tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period='6mo')
        
        info = stock.info
        market_cap = info.get('marketCap', 0)
        trailing_eps = info.get('trailingEps', 0)
        avg_volume = info.get('averageVolume', 0)
        
        if not df.empty and len(df) >= 50:
            current_price = df['Close'].iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc(-1)
            
            # התנאים שלנו למציאת "כוכב עולה"
            is_large_cap = market_cap is not None and market_cap >= 18_000_000_000 # שווי שוק מעל 18 מיליארד
            is_profitable = trailing_eps is not None and trailing_eps > 0             # רווחית
            has_liquidity = avg_volume is not None and avg_volume > 250_000         # נזילות טובה
            is_above_ma50 = current_price > ma50                                    # מחיר מעל ממוצע 50
            
            if is_large_cap and is_profitable and has_liquidity and is_above_ma50:
                rising_stars_found.append(f"*{ticker}* | שווי שוק: ${round(market_cap/1e9, 1)}B | מחיר: ${round(current_price, 2)}")
                print(f"מצאנו כוכב עולה: {ticker}")
    except Exception as e:
        continue

# שליחת התראה לטלגרם עם המניות שעברו את הסינון היום
if rising_stars_found:
    alert_message = "🚀 *התראת כוכבים עולים (Rising Stars):*\n\n" + "\n".join(rising_stars_found)
    send_telegram_alert(alert_message)
else:
    print("\nהסריקה הסתיימה. לא נמצאו מניות שעומדות בכל התנאים היום.")
    send_telegram_alert("🤖 *רובוט הסריקה:* הסריקה היומית הסתיימה בהצלחה. אין מניות חדשות שעברו את התנאים היום.")
