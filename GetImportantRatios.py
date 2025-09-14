import yfinance as yf
from tabulate import tabulate

# List of tickers to analyze
tickers = ["GOOGL", "MSFT", "ADBE", "NVDA"]
headers = ["Ticker", "P/E", "Fwd P/E", "P/B", "Cash ($B)", "Rev Growth", "E Growth", "Margin", "PEG", "PE/FutureG"]
table_data = []

# Fetch data for each ticker
for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Get values and format them appropriately
    pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    pb = info.get("priceToBook")
    cash_flow = info.get("operatingCashflow")
    # Convert cash flow to billions for better display
    if cash_flow:
        cash_flow = cash_flow / 1000000000
    revenue_growth = info.get("revenueGrowth")
    if revenue_growth:
        revenue_growth = revenue_growth * 100  # Convert to percentage
    profit_margin = info.get("profitMargins")
    if profit_margin:
        profit_margin = profit_margin * 100  # Convert to percentage
    peg_ratio = info.get("trailingPegRatio")  # Using trailingPegRatio instead of pegRatio
    
    # Calculate Forward PEG Ratio (Current P/E divided by expected earnings growth rate)
    earnings_growth = info.get("earningsGrowth")
    earnings_growth_percent = None
    forward_peg = None
    if earnings_growth:
        earnings_growth_percent = earnings_growth * 100  # Convert to percentage
        if pe and earnings_growth != 0:  # Using current PE instead of forward PE
            forward_peg = pe / earnings_growth_percent  # Using current PE for this calculation
    
    # Add data to table format
    row = [ticker, pe, forward_pe, pb, cash_flow, revenue_growth, earnings_growth_percent, profit_margin, peg_ratio, forward_peg]
    table_data.append(row)

# Print the data in a beautiful table format
print("\n📊 Financial Ratios for Technology Companies 📊\n")
print(tabulate(table_data, headers=headers, tablefmt="grid", 
              numalign="right", floatfmt=(".2f", ".2f", ".2f", ".2f", ".2f", ".1f", ".1f", ".1f", ".2f", ".2f")))

# Add a legend/explanation
print("\nLegend:")
print("P/E = Price to Earnings ratio")
print("Fwd P/E = Forward Price to Earnings ratio")
print("P/B = Price to Book ratio")
print("Cash = Operating Cash Flow in billions")
print("Rev Growth = Year over Year Revenue Growth")
print("E Growth = Expected Earnings Growth")
print("Margin = Net Profit Margin")
print("PEG = Price/Earnings to Growth ratio (trailing)")
print("PE/FutureG = Current P/E to Future Growth ratio (hybrid metric)")
