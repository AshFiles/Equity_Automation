"""
Date: Jan 7 2025

Script for Automated Stock Trading Backtesting and Visualization Based on the 20-50-100-200 DMA Strategy

### Logic and Features:

1. **Data Download and Preparation:**
   - Fetches historical stock price data for the last 5 years using Yahoo Finance (via `yfinance`).
   - Calculates 20, 50, 100, and 200-day simple Daily Moving Averages (DMA) for the stock.

2. **Trading Strategy Logic:**
   - **Buy Condition:** Enter the market (buy the stock) when:
       - Close Price < DMA_20 < DMA_50 < DMA_100 < DMA_200.
   - **Sell Condition:** Exit the market (sell the stock) when:
       - DMA_200 < DMA_100 < DMA_50 < DMA_20 < Close Price, *and* the sell price must be greater than the buy price to avoid a loss.
   - Executes only one trade at a time: 
       - Full reinvestment of ₹100,000 during each buy.
       - No reinvestment until the stock is sold.

3. **Trade Summary:**
   - Tracks all completed trades and stores the following information:
       - Entry Date, Exit Date.
       - Buy Price, Sell Price.
       - Holding Period (calculated in Years and Months).
       - Profit/Loss from each trade.
       - **Effective Annual Gain (%):** Annualized percentage return for the trade.

4. **Unrealized Profit/Loss:**
   - If the stock is still being held at the end of the period, the script calculates the unrealized profit/loss based on the latest closing price.

5. **Visualization:**
   - Plots the Close Price and all DMA lines (20, 50, 100, 200).
   - Marks buy (green upward marker) and sell (red downward marker) points for trades.
   - Provides a clear, labeled visualization of the trades executed.

6. **Output:**
   - Prints a detailed **Trade Summary** to the console, showing all trades with metrics.
   - Exports the **Trade Summary** as a CSV file (`trade_summary.csv`).
   - Displays a graph with stock prices, DMA lines, and highlighted buy/sell points for easy analysis.

### Notes:
- Designed for backtesting this strategy on a single stock (e.g., SAIL.NS).
- Ensures no selling is performed at a loss (price at sell > price at buy).
- Can be used to assess strategy performance and identify trade opportunities based on DMA crossover patterns.
"""


import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

# Getting today's date and calculating the date 5 years ago
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=5 * 365)).strftime('%Y-%m-%d')

# SAIL Stock
stock = 'TATAMOTORS.NS'

# Download SAIL stock data for the last 5 years
data = yf.download(stock, start=start_date, end=end_date)

# Clean the data by dropping rows with NaN values
data = data.dropna(subset=['Close'])

# Calculate moving averages
data['DMA_20'] = data['Close'].rolling(window=20).mean()
data['DMA_50'] = data['Close'].rolling(window=50).mean()
data['DMA_100'] = data['Close'].rolling(window=100).mean()
data['DMA_200'] = data['Close'].rolling(window=200).mean()

# Initialize simulation variables
investment = 100000  # Fixed investment
in_market = False  # Tracks if we currently hold shares
buy_price = 0  # Price at which we bought shares
current_holding = 0  # Number of shares currently held
trades = []  # To store trade details: Entry Date, Exit Date, Profit/Loss
buy_markers = []  # To keep track of buy markers (date, price)
sell_markers = []  # To keep track of sell markers (date, price)

# Simulating Buy/Sell Conditions
for i in range(len(data)):
    # Checking buy condition
    if not in_market and i > 0:  # We can only buy if not in the market
        if (data['Close'].iloc[i] < data['DMA_20'].iloc[i] < data['DMA_50'].iloc[i] <
                data['DMA_100'].iloc[i] < data['DMA_200'].iloc[i]):
            # Buy shares
            buy_price = data['Close'].iloc[i]
            current_holding = investment / buy_price  # Calculate shares purchased
            entry_date = data.index[i]  # Track entry date
            in_market = True
            buy_markers.append((entry_date, buy_price))  # Add buy marker
            print(f"Bought on {entry_date.date()} at {buy_price:.2f} per share")

    # Checking sell condition
    elif in_market and i > 0:  # We can only sell if we are in the market
        if (data['DMA_200'].iloc[i] < data['DMA_100'].iloc[i] < data['DMA_50'].iloc[i] <
                data['DMA_20'].iloc[i] < data['Close'].iloc[i]
                and data['Close'].iloc[i] > buy_price):  # Ensure selling price is greater than buy price
            # Sell shares
            sell_price = data['Close'].iloc[i]
            exit_date = data.index[i]  # Track exit date
            profit_or_loss = current_holding * sell_price - investment
            
            # Calculate holding duration
            duration_in_days = (exit_date - entry_date).days
            years_held = duration_in_days // 365
            months_held = (duration_in_days % 365) // 30
            
            # Effective annual gain
            years_fraction = duration_in_days / 365
            effective_annual_gain = (((current_holding * sell_price) / investment) ** (1 / years_fraction) - 1) * 100
            
            trades.append({
                'Entry Date': entry_date.date(),
                'Exit Date': exit_date.date(),
                'Holding Period (Years)': years_held,
                'Holding Period (Months)': months_held,
                'Buy Price': round(buy_price, 2),
                'Sell Price': round(sell_price, 2),
                'Profit/Loss': round(profit_or_loss, 2),
                'Effective Annual Gain (%)': round(effective_annual_gain, 2),
                'Status': 'Completed'
            })
            sell_markers.append((exit_date, sell_price))  # Add sell marker
            print(f"Sold on {exit_date.date()} at {sell_price:.2f} per share, Profit/Loss: {profit_or_loss:.2f} "
                  f"Annual Gain: {effective_annual_gain:.2f}%")
            in_market = False  # Exit the market
            buy_price, current_holding = 0, 0  # Reset holdings

# If still in the market, calculate unrealized profit or loss
unrealized_pnl = 0  # Initialize unrealized profit or loss
if in_market:
    current_price = data['Close'].iloc[-1]  # Last available price
    unrealized_pnl = current_holding * current_price - investment
    
    # Add unrealized profit/loss as another row in the trade summary
    trades.append({
        'Entry Date': entry_date.date(),
        'Exit Date': 'Still Holding',
        'Holding Period (Years)': '',
        'Holding Period (Months)': '',
        'Buy Price': round(buy_price, 2),
        'Sell Price': round(current_price, 2),
        'Profit/Loss': round(unrealized_pnl, 2),
        'Effective Annual Gain (%)': '',
        'Status': 'Holding'
    })
    print(f"Still holding shares bought on {entry_date.date()}, "
          f"Current Price: {current_price:.2f}, Unrealized P/L: {unrealized_pnl:.2f}")

# Create a DataFrame to display trade details
trades_df = pd.DataFrame(trades)

# Display trade results
if not trades_df.empty:
    print("\nTrade Summary:")
    print(trades_df)
else:
    print("\nNo trades made during this period.")

# Save the trade summary to a CSV file with the name of the stock
if not trades_df.empty:
    filename = f"{stock}_trade_summary.csv"
    trades_df.to_csv(filename, index=False)
    print(f"Trade summary saved to '{filename}'.")

# Plotting the visualization with markers
plt.figure(figsize=(16, 10), dpi=120)
plt.title(f"Stock Analysis for {stock} (Last 5 Years) with Trades", fontsize=16)

# Plot the "Close" price line
plt.plot(data.index, data['Close'], label='Close Price', color='black', alpha=0.8, linewidth=1.5)

# Plot the DMA lines
plt.plot(data.index, data['DMA_20'], label='DMA 20', color='green', linestyle='--', linewidth=1)
plt.plot(data.index, data['DMA_50'], label='DMA 50', color='blue', linestyle='--', linewidth=1)
plt.plot(data.index, data['DMA_100'], label='DMA 100', color='orange', linestyle='--', linewidth=1)
plt.plot(data.index, data['DMA_200'], label='DMA 200', color='red', linestyle='--', linewidth=1)

# Mark Buy and Sell points on the graph
for date, price in buy_markers:
    plt.scatter(date, price, color='lime', s=150, label='Buy', marker='^', edgecolors='black', zorder=5)  # Larger green marker
for date, price in sell_markers:
    plt.scatter(date, price, color='crimson', s=150, label='Sell', marker='v', edgecolors='black', zorder=5)  # Larger red marker

# Remove duplicate labels from legend
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=12)

# Add labels and grid
plt.xlabel('Date', fontsize=14)
plt.ylabel('Price (INR)', fontsize=14)
plt.grid(True, alpha=0.5)

# Display the plot
plt.show()
