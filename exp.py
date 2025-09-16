import yfinance as yf
import pandas as pd
import json
from datetime import datetime

# Pick a ticker symbol
ticker = "MSFT"

# Download the stock object
stock = yf.Ticker(ticker)

# Get current key statistics
info = stock.info

# Get earnings history for EPS data
earnings_history = stock.get_earnings_history()

# Also try to get historical quarterly earnings
try:
    quarterly_financials = stock.quarterly_financials
    historical_financials_available = True
except Exception as e:
    print(f"Error getting quarterly financials: {e}")
    historical_financials_available = False

print("=== Stock Info for", ticker, "===")
print("Current Price:", info.get("currentPrice"))
print("Trailing P/E:", info.get("trailingPE"))
print("Forward P/E:", info.get("forwardPE"))
print("Trailing EPS:", info.get("trailingEps"))
print("Forward EPS:", info.get("forwardEps"))
print()

print("=== Growth Metrics ===")
print("TTM Revenue Growth:", f"{info.get('revenueGrowth', 0) * 100:.1f}%")
print("TTM Earnings Growth:", f"{info.get('earningsGrowth', 0) * 100:.1f}%")
print("TTM EPS Growth:", f"{info.get('earningsQuarterlyGrowth', 0) * 100:.1f}%")

# Calculate forward EPS growth
if info.get("trailingEps") and info.get("forwardEps") and info.get("trailingEps") != 0:
    fwd_eps_growth = ((info.get("forwardEps") - info.get("trailingEps")) / info.get("trailingEps")) * 100
    print(f"Forward EPS Growth: {fwd_eps_growth:.1f}%")
print()

# Display available quarters of EPS data from earnings_history
print("=== Recent Quarters EPS Data from earnings_history ===")
if not earnings_history.empty:
    # Reset index to make 'quarter' a column
    eh_with_quarter = earnings_history.reset_index()
    # Format and sort by quarter (most recent first)
    eh_with_quarter['quarter'] = pd.to_datetime(eh_with_quarter['quarter'])
    eh_with_quarter = eh_with_quarter.sort_values('quarter', ascending=False)
    
    # Print all available quarters
    available_quarters = eh_with_quarter[['quarter', 'epsActual']]
    print(f"Number of quarters available: {len(available_quarters)}")
    print(available_quarters)
    
    # Calculate trailing 12-month EPS (sum of last 4 quarters)
    ttm_eps = available_quarters.head(4)['epsActual'].sum()
    print(f"\nCalculated TTM EPS (sum of last 4 quarters): {ttm_eps:.2f}")
    print(f"Yahoo Finance TTM EPS: {info.get('trailingEps')}")
else:
    print("No earnings history data available")

# If historical quarterly financials are available, display them
if historical_financials_available:
    print("\n=== Historical Quarterly Financials ===")
    # Get columns related to earnings/income
    income_columns = [col for col in quarterly_financials.columns if any(term in str(col).lower() for term in ['income', 'earnings', 'eps', 'revenue'])]
    
    if income_columns:
        print("Available income-related metrics:")
        for col in income_columns:
            print(f"- {col}")
        
        print("\nHistorical Quarterly Net Income:")
        if 'Net Income' in quarterly_financials.columns:
            print(quarterly_financials['Net Income'].head(8))
        elif 'NetIncome' in quarterly_financials.columns:
            print(quarterly_financials['NetIncome'].head(8))
        else:
            print("Net Income not found in quarterly financials.")
    else:
        print("No income-related metrics found in quarterly financials.")

# Save the full JSON response to a file
with open(f"{ticker}_full_info.json", "w") as f:
    json.dump(info, f, indent=4)
print(f"\nSaved full JSON data for {ticker} to {ticker}_full_info.json")