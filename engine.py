import os
import yfinance as yf
import pandas as pd
import requests

# חיבור לטלגרם דרך ההגדרות המאובטחות שהגדרנו מראש
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

def get_sp400_tickers():
    """מנסה למשוך אוטומטית את כל רשימת המניות מהאינטרנט"""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies'
        # אומרים לאתר שאנחנו דפדפן רגיל כדי שלא יחסום אותנו
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        tables = pd.read_html(response.text)
        df = tables[0]
        
        # מוצאים את העמודה של סימול המניות
        symbol_col = 'Symbol' if 'Symbol' in df.columns else df.columns[0]
        tickers = df[symbol_col].astype(str).str.replace('.', '-', regex=False).tolist()
        tickers = [t.strip() for t in tickers if len(t) <= 5]
        
        print(f"הצלחנו לשאוב אוטומטית {len(tickers)} מניות מהאינטרנט!")
        return tickers
    except Exception as e:
        print(f"⚠️ לא הצלחנו למשוך את הרשימה המלאה כרגע, עוברים לרשימת גיבוי רחבה. שגיאה: {e}")
        # רשימת גיבוי למקרה חירום שהאינטרנט חוסם את השאיבה
        return [
            'CRWD', 'PLTR', 'DDOG', 'SNOW', 'PATH', 'NET', 'ZS', 'ANET', 'UBER', 'RBLX',
            'MDB', 'HUBS', 'BILL', 'CFLT', 'GTLB', 'DUOL', 'TOST', 'CELH', 'AXON', 'FTNT',
            'PANW', 'DECK', 'EXLS', 'MRVL', 'SMCI', 'ARM', 'ON', 'TTD', 'PCTY', 'GDDY'
        ]

# מריצים את השאיבה
universe_tickers = get_sp400_tickers()
print(f"סך הכל מניות לבדיקה היום: {len(universe_tickers)}")

rising_stars_found = []

# עוברים מניה מניה ובודקים אם היא מתאימה לתנאים שלנו
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
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            
            # התנאים הקשוחים שלנו למציאת "כוכב עולה"
            is_large_cap = market_cap is not None and market_cap >= 18_000_000_000 # שווי שוק מעל 18 מיליארד
            is_profitable = trailing_eps is not None and trailing_eps > 0             # רווחית
            has_liquidity = avg_volume is not None and avg_volume > 250_000         # נזילות טובה
            is_above_ma50 = current_price > ma50                                    # מגמת עליה
            
            if is_large_cap and is_profitable and has_liquidity and is_above_ma50:
                rising_stars_found.append(f"*{ticker}* | שווי שוק: ${round(market_cap/1e9, 1)}B | מחיר: ${round(current_price, 2)}")
                print(מצאנו כוכב עולה: {ticker})
    except Exception:
        continue

# שולחים הודעה לטלגרם לפי מה שמצאנו
if rising_stars_found:
    alert_message = "🚀 *התראת כוכבים עולים (S&P 500 Rising Stars):*\n\n" + "\n".join(rising_stars_found)
    send_telegram_alert(alert_message)
else:
    print("\nהסריקה הסתיימה. לא נמצאו מניות שעומדות بكل התנאים היום.")
    send_telegram_alert("🤖 *רובוט הסריקה:* הסריקה היומית הסתיימה בהצלחה. אין מניות חדשות שעברו את התנאים היום.")
