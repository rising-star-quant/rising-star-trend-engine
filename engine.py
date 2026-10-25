import os
import yfinance as yf
import pandas as pd
import requests

# שליפת נתוני טלגרם מתוך משתני סביבה מאובטחים של GitHub Secrets
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Error: Telegram tokens not found in environment variables!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram alert sent successfully! 📱")
        else:
            print(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def get_sp400_tickers():
    """שאיבה אוטומטית של רשימת כל מניות מדד S&P MidCap 400 עם User-Agent למניעת חסימה"""
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies'
        # הוספת כותרת דפדפן כדי שוויקיפדיה לא תחזיר שגיאת 403
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        html_content = requests.get(url, headers=headers).text
        
        tables = pd.read_html(html_content)
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
        print(f"Successfully fetched {len(tickers)} tickers from S&P MidCap 400 index.")
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 400 index list: {e}")
        # גיבוי מורחב למקרה קיצוני של נפילת רשת
        return ['CRWD', 'PLTR', 'DDOG', 'SNOW', 'PATH', 'NET', 'ZS', 'ANET', 'UBER', 'RBLX']

# שליפה אוטומטית של המדד
universe_tickers = get_sp400_tickers()

print(f"\nStarting Fully Autonomous S&P 500 Screening...")

results = []
rising_stars_found = []

# סריקת כל מניות המדד וניטור בזמן אמת
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
            
            # תנאי סף פונדמנטליים וטכניים מורחבים לפי ה-PRD
            is_large_cap = market_cap is not None and market_cap >= 18_000_000_000 # $18B+
            is_profitable = trailing_eps is not None and trailing_eps > 0
            has_liquidity = avg_volume is not None and avg_volume > 250_000
            is_above_ma50 = current_price > ma50
            
            passed_all = is_large_cap and is_profitable and has_liquidity and is_above_ma50
            
            if passed_all:
                rising_stars_found.append(f"*{ticker}* | Cap: ${round(market_cap/1e9, 1)}B | Price: ${round(current_price, 2)}")
                print(f"🔥 Found Rising Star: {ticker} (Market Cap: ${round(market_cap/1e9, 1)}B)")
                
    except Exception as e:
        continue

# שליחת התראה לטלגרם אם נמצאו מניות שעברו את הסינון
if rising_stars_found:
    alert_message = "🚀 *Fully Autonomous S&P 500 Rising Star Alert!*\n\n" + "\n".join(rising_stars_found)
    send_telegram_alert(alert_message)
else:
    print("\nScan completed. No Rising Stars found today matching all criteria.")
