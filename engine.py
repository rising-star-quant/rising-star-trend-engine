
import os
import yfinance as yf
import pandas as pd
import requests

# שליפת נתוני טלגרם מתוך משתני סביבה מאובטחים של GitHub
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram tokens not found in environment variables.")
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

# שליפת רשימת המניות מתוך קובץ ה-Watchlist ב-GitHub
watchlist_url = 'https://raw.githubusercontent.com/rising-star-quant/rising-star-trend-engine/main/watchlist.csv'

try:
    watchlist_df = pd.read_csv(watchlist_url)
    tickers = watchlist_df['ticker'].dropna().tolist()
    print(f"Successfully loaded {len(tickers)} tickers from GitHub Watchlist.")
except Exception as e:
    print(f"Error loading watchlist from GitHub: {e}")
    tickers = ['CRWD', 'PLTR', 'DDOG']

print(f"\nRunning S&P 500 Expanded Eligibility Engine...")

results = []
rising_stars_found = []

for ticker in tickers:
    stock = yf.Ticker(ticker)
    df = stock.history(period='6mo')
    
    try:
        info = stock.info
        market_cap = info.get('marketCap', 0)
        trailing_eps = info.get('trailingEps', 0)
        avg_volume = info.get('averageVolume', 0)
    except:
        market_cap = 0
        trailing_eps = 0
        avg_volume = 0
        
    if not df.empty and len(df) >= 50:
        current_price = df['Close'].iloc[-1]
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        
        # תנאי סף פונדמנטליים מורחבים
        is_large_cap = market_cap is not None and market_cap >= 18_000_000_000
        is_profitable = trailing_eps is not None and trailing_eps > 0
        has_liquidity = avg_volume is not None and avg_volume > 250_000
        is_above_ma50 = current_price > ma50
        
        passed_all = is_large_cap and is_profitable and has_liquidity and is_above_ma50
        
        if passed_all:
            rising_stars_found.append(f"*{ticker}* | Cap: ${round(market_cap/1e9, 1)}B | Price: ${round(current_price, 2)}")

# שליחת התראה לטלגרם אם נמצאו מניות שעברו את הסינון
if rising_stars_found:
    alert_message = "🚀 *S&P 500 Expanded Rising Star Alert!*\n\n" + "\n".join(rising_stars_found)
    send_telegram_alert(alert_message)
else:
    print("\nNo Rising Stars found today matching all criteria.")
