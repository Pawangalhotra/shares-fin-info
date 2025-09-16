import yfinance as yf
import pandas as pd
from tabulate import tabulate
import sys

# Check command line arguments
if len(sys.argv) < 2:
    print("Usage: python GetImportantRatios.py -growth")
    print("  -growth - Shows Price, EPS, P/E ratios, PEG ratios, Revenue Growth, and Margins")
    sys.exit(1)

mode = sys.argv[1].lower().lstrip('-')
if mode != 'growth':
    print("Invalid argument. Please use '-growth'")
    sys.exit(1)

# List of tickers to analyze
tickers = ["GOOGL", "MSFT", "ADBE", "NVDA"]

# Define headers for growth metrics
headers = ["Ticker", "Price", "Trailing EPS", "Expected EPS", "TTM EPS Growth %", "Fwd EPS Growth %", 
           "TTM Rev Growth %", "P/E", "Fwd P/E", "Trailing PEG", "Fwd PEG"]

table_data = []

# Fetch data for each ticker
for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info
       
    # Get values and format them appropriately
    current_price = info.get("currentPrice")
    
    # Calculate EPS from quarterly data instead of using the API's trailingEps
    earnings_history = stock.get_earnings_history()
    eps = None
    trailing_eps_growth = None
    trailing_eps_growth_per = None
    
    if not earnings_history.empty:
        # Get the last 4 quarters of EPS data
        quarterly_eps = earnings_history['epsActual'].head(4).tolist()
        
        # Calculate current trailing EPS (last 4 quarters)
        if len(quarterly_eps) == 4:
            current_trailing_eps = sum(quarterly_eps)
            eps = current_trailing_eps
                
    # Fallback to API value if quarterly data not available
    if eps is None:
        eps = info.get("trailingEps")
    
    # Get quarterly EPS data from income statement (each quarter shows TTM data)
    quarterly_income_stmt = stock.quarterly_income_stmt
    
    if not quarterly_income_stmt.empty and 'Diluted EPS' in quarterly_income_stmt.index:
        eps_data = quarterly_income_stmt.loc['Diluted EPS']
        if len(eps_data) >= 5:
            # Each data point is already TTM, so compare current TTM vs TTM from 4 quarters ago
            current_ttm_eps = eps_data.iloc[0]  # Latest quarter's TTM EPS
            previous_ttm_eps = eps_data.iloc[4]  # TTM EPS from 4 quarters ago (1 year back)
            trailing_eps_growth = current_ttm_eps - previous_ttm_eps
            trailing_eps_growth_per = trailing_eps_growth / previous_ttm_eps * 100
    
    # Calculate P/E based on our calculated EPS
    if eps and current_price:
        pe = current_price / eps
    else:
        pe = info.get("trailingPE")  # Fallback to API value
    
    #take a conservative approach and assume 75% growth from the previous year.
    forward_eps = eps * (trailing_eps_growth_per / 100 * 0.8 + 1)

    forward_pe = current_price / forward_eps 

    # Get revenue growth data
    revenue_growth = info.get("revenueGrowth")
    if revenue_growth:
        revenue_growth = revenue_growth * 100  # Convert to percentage
    
    # Calculate expected EPS growth percentage
    eps_growth_percent = None
    if eps and forward_eps and eps != 0:
        eps_growth_percent = ((forward_eps - eps) / eps) * 100
    
    peg_ratio = pe / trailing_eps_growth_per
    
    if forward_pe and eps_growth_percent != 0:  # Using forward PE instead of current PE
        forward_peg = forward_pe / eps_growth_percent  # Using forward PE for this calculation

    # Add data to table format
    row = [ticker, current_price, eps, forward_eps, trailing_eps_growth_per, eps_growth_percent,
           revenue_growth, pe, forward_pe, peg_ratio, forward_peg]
    
    table_data.append(row)

# Print the data in a beautiful table format
title = "📊 Growth Metrics and Ratios 📊"
print(f"\n{title}\n")

# Set float formatting for growth metrics
float_format = (".2f", ".2f", ".2f", ".2f", ".1f", ".1f", ".1f", ".2f", ".2f", ".2f", ".2f")

print(tabulate(table_data, headers=headers, tablefmt="grid", numalign="right", floatfmt=float_format))

# Add a legend/explanation
print("\nLegend:")
print("Price = Current stock price")
print("Trailing EPS = Sum of last 4 quarters' Earnings Per Share")
print("Expected EPS = Expected Earnings Per Share in next 12 months")
print("TTM EPS Growth % = Year-over-Year growth of trailing 12-month EPS vs previous 12 months")
print("Fwd EPS Growth % = Expected future EPS growth (Trailing to Expected EPS)")
print("TTM Rev Growth % = Year-over-Year Revenue Growth for trailing 12 months")
print("P/E = Price to Earnings ratio based on trailing EPS")
print("Fwd P/E = Forward Price to Earnings ratio based on expected EPS")
print("Trailing PEG = Price/Earnings to Growth ratio based on trailing earnings")
print("Fwd PEG = Forward P/E to Future Growth ratio based on expected earnings")
