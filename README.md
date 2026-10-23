# 🚀 Rising Star Trend Engine (S&P 500)

Autonomous, quantitative trend engine designed to identify and track Mid-Cap growth equities undergoing S&P 500 inclusion arbitrage opportunities.

---

## 📌 Project Overview
* **Domain:** Quantitative Finance & S&P 500 Tail Arbitrage
* **Core Logic:** Fundamental S&P Eligibility Filtering + Technical Trend Analysis + Strict Risk Management (Stop Loss)
* **Tech Stack:** Python (`yfinance`, `pandas`), GitHub, Google Colab, Telegram API (Upcoming)
* **Architecture Goal:** Serverless execution with $0 operational cost

---

## 🛠️ Development Log (Dev Log)

### Stage 1: Proof of Concept (POC) - Data Verification
* **Date:** October 2026
* **Status:** Completed ✅
* **Objective:** Verify live market data ingestion from Yahoo Finance (`yfinance`) and validate basic trend indicators (MA50 calculations).

#### Execution Script (Google Colab):
```python
# 1. התקנת הספרייה לשליפת הנתונים
!pip install yfinance --quiet

import yfinance as yf
import pandas as pd

# רשימת המניות לבדיקה
tickers = ['CRWD', 'PLTR', 'KKR', 'DELL', 'SMCI']

print("Fetching data and calculating risk metrics...")

results = []
for ticker in tickers:
    stock = yf.Ticker(ticker)
    df = stock.history(period='6mo')
    
    if not df.empty and len(df) >= 50:
        current_price = df['Close'].iloc[-1]
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        
        # חישוב Stop Loss אוטומטי (שמרני: הנמכה של 8% ממחיר הסגירה או תמיכת MA50, הנמוך מבניהם או קטיעה קשיחה של 8%)
        stop_loss_price = round(current_price * 0.92, 2) # 8% מתחת למחיר הנוכחי
        
        results.append({
            'Ticker': ticker,
            'Current Price ($)': round(current_price, 2),
            'MA50 ($)': round(ma50, 2),
            'Stop Loss ($)': stop_loss_price,
            'Above MA50': 'Yes' if current_price > ma50 else 'No'
        })

results_df = pd.DataFrame(results)
print("\n--- Rising Star POC with Risk Management (Stop Loss) ---")
display(results_df)
