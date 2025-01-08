"""
Automated Stock Trading Backtesting and Visualization Script

### Features:
1. **Data Download & Preparation:**
   - Fetches historical stock data for the last 5 years via Yahoo Finance.
   - Calculates 20, 50, 100, and 200-day Simple Moving Averages (DMA).

2. **Trading Strategy:**
   - **Buy:** When Close < DMA_20 < DMA_50 < DMA_100 < DMA_200.
   - **Sell:** When DMA_200 < DMA_100 < DMA_50 < DMA_20 < Close and Sell Price > Buy Price.
   - Executes one trade at a time with full reinvestment of ₹100,000.

3. **Trade Summary:**
   - Logs Entry/Exit Dates, Prices, Holding Period, Profit/Loss, and Effective Annual Gain.
   - Calculates unrealized P/L if holding at the end.

4. **Visualization:**
   - Plots Close Price and DMA lines with distinct line patterns.
   - Marks buy (green ▲) and sell (red ▼) points with corresponding prices.
   - Saves the plot as a PNG file.

5. **Outputs:**
   - Prints a neatly formatted Trade Summary to the console with execution time.
   - Exports Trade Summary as `<STOCK>_trade_summary.csv`.
   - Appends a summary row to `consolidated_trade_summary.csv`.
   
6. **User Flexibility:**
   - Accepts stock name as a command-line argument (e.g., `python script.py maruti`).
   - Defaults to a predefined stock if no argument is provided.

### Usage:
- **With Argument:** `python script.py MARUTI`
- **Without Argument:** Uses the stock name defined in the script (e.g., UNIONBANK).

"""
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import sys
import os
import time

def main():
    start_time = time.time()
    
    # Default stock name
    default_stock = 'UNIONBANK'
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        stock_name = sys.argv[1].upper()
    else:
        stock_name = default_stock
    
    # Append '.NS' for Yahoo Finance
    stock_symbol = f"{stock_name}.NS"
    
    # Getting today's date and calculating the date 5 years ago
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=5 * 365)).strftime('%Y-%m-%d')
    
    # Download stock data for the last 5 years
    data = yf.download(stock_symbol, start=start_date, end=end_date)
    
    if data.empty:
        print(f"Error: No data found for '{stock_symbol}'. Please check the stock name.")
        sys.exit(1)
    
    # Clean the data by dropping rows with NaN Close values
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
    trades = []  # To store trade details
    buy_markers = []  # To keep track of buy markers (date, price)
    sell_markers = []  # To keep track of sell markers (date, price)
    
    entry_date = None  # Initialize entry date
    
    # Simulating Buy/Sell Conditions
    for i in range(len(data)):
        # Checking buy condition
        if not in_market and i > 199:  # Ensure enough data for DMA_200
            if (data['Close'].iloc[i] < data['DMA_20'].iloc[i] < data['DMA_50'].iloc[i] <
                data['DMA_100'].iloc[i] < data['DMA_200'].iloc[i]):
                # Buy shares
                buy_price = data['Close'].iloc[i]
                current_holding = investment / buy_price  # Calculate shares purchased
                entry_date = data.index[i]  # Track entry date
                in_market = True
                buy_markers.append((entry_date, buy_price))  # Add buy marker
                print(f"{'Bought on':<20}: {entry_date.date():<12} | {'Price':<10}: {buy_price:.2f}")
    
        # Checking sell condition
        elif in_market and i > 199:
            if (data['DMA_200'].iloc[i] < data['DMA_100'].iloc[i] < data['DMA_50'].iloc[i] <
                data['DMA_20'].iloc[i] < data['Close'].iloc[i] and
                data['Close'].iloc[i] > buy_price):
                # Sell shares
                sell_price = data['Close'].iloc[i]
                exit_date = data.index[i]  # Track exit date
                profit_or_loss = current_holding * sell_price - investment
                
                # Calculate holding duration
                duration_in_days = (exit_date - entry_date).days
                years_held = duration_in_days // 365
                months_held = (duration_in_days % 365) // 30
                
                # Effective annual gain
                if duration_in_days > 0:
                    years_fraction = duration_in_days / 365
                    effective_annual_gain = (((current_holding * sell_price) / investment) ** (1 / years_fraction) - 1) * 100
                else:
                    effective_annual_gain = 0
                
                trades.append({
                    'Entry Date': entry_date.date(),
                    'Exit Date': exit_date.date(),
                    'Holding Period (Y)': years_held,
                    'Holding Period (M)': months_held,
                    'Buy Price': round(buy_price, 2),
                    'Sell Price': round(sell_price, 2),
                    'Profit/Loss': round(profit_or_loss, 2),
                    'Effective Annual Gain (%)': round(effective_annual_gain, 2),
                    'Status': 'Completed'
                })
                sell_markers.append((exit_date, sell_price))  # Add sell marker
                print(f"{'Sold on':<20}: {exit_date.date():<12} | {'Price':<10}: {sell_price:.2f} | "
                      f"{'P/L':<15}: {profit_or_loss:.2f} | {'Annual Gain':<20}: {effective_annual_gain:.2f}%")
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
            'Holding Period (Y)': '',
            'Holding Period (M)': '',
            'Buy Price': round(buy_price, 2),
            'Sell Price': round(current_price, 2),
            'Profit/Loss': round(unrealized_pnl, 2),
            'Effective Annual Gain (%)': '',
            'Status': 'Holding'
        })
        print(f"{'Holding':<20}: {entry_date.date():<12} | {'Current Price':<15}: {current_price:.2f} | "
              f"{'Unrealized P/L':<20}: {unrealized_pnl:.2f}")
    
    # Create a DataFrame to display trade details
    trades_df = pd.DataFrame(trades)
    
    # Display trade results with formatting
    if not trades_df.empty:
        print("\nTrade Summary:")
        print(trades_df.to_string(index=False))
    else:
        print("\nNo trades made during this period.")
    
    # Save the trade summary to a CSV file with the stock name
    if not trades_df.empty:
        trade_summary_filename = f"{stock_name}_trade_summary.csv"
        trades_df.to_csv(trade_summary_filename, index=False)
        print(f"\nTrade summary saved to '{trade_summary_filename}'.")
    
    # Append to consolidated trade summary
    consolidated_file = "consolidated_trade_summary.csv"
    analysis_period = f"{start_date} to {end_date}"
    total_profit = trades_df['Profit/Loss'].sum() if not trades_df.empty else 0
    
    if in_market:
        consolidated_data = {
            'Stock': stock_name,
            'Analysis Period': analysis_period,
            'Total Profit/Loss': round(total_profit, 2),
            'Unrealized P/L': round(unrealized_pnl, 2)
        }
    else:
        consolidated_data = {
            'Stock': stock_name,
            'Analysis Period': analysis_period,
            'Total Profit/Loss': round(total_profit, 2),
            'Unrealized P/L': ''
        }
    
    consolidated_df = pd.DataFrame([consolidated_data])
    
    if not os.path.isfile(consolidated_file):
        consolidated_df.to_csv(consolidated_file, index=False)
    else:
        consolidated_df.to_csv(consolidated_file, mode='a', header=False, index=False)
    
    print(f"Consolidated trade summary updated in '{consolidated_file}'.")
    
    # Plotting the visualization with markers and distinct line patterns
    plt.figure(figsize=(16, 10), dpi=120)
    plt.title(f"Stock Analysis for {stock_name} (Last 5 Years) with Trades", fontsize=16)
    
    # Plot the "Close" price line
    plt.plot(data.index, data['Close'], label='Close Price', color='black', linestyle='-', linewidth=1.5)
    
    # Plot the DMA lines with different line patterns
    plt.plot(data.index, data['DMA_20'], label='DMA 20', color='blue', linestyle='--', linewidth=1)
    plt.plot(data.index, data['DMA_50'], label='DMA 50', color='blue', linestyle='-.', linewidth=1)
    plt.plot(data.index, data['DMA_100'], label='DMA 100', color='blue', linestyle=':', linewidth=1)
    plt.plot(data.index, data['DMA_200'], label='DMA 200', color='blue', linestyle='-', linewidth=1)
    
    # Mark Buy points with prices
    for date, price in buy_markers:
        plt.scatter(date, price, color='lime', s=100, label='Buy', marker='^', edgecolors='black', zorder=5)
        plt.text(date, price, f'{price:.2f}', fontsize=9, verticalalignment='bottom', color='green')
    
    # Mark Sell points with prices
    for date, price in sell_markers:
        plt.scatter(date, price, color='crimson', s=100, label='Sell', marker='v', edgecolors='black', zorder=5)
        plt.text(date, price, f'{price:.2f}', fontsize=9, verticalalignment='top', color='red')
    
    # Remove duplicate labels from legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=12)
    
    # Add labels and grid
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price (INR)', fontsize=14)
    plt.grid(True, alpha=0.5)
    
    # Save the plot as a PNG file
    plot_filename = f"{stock_name}_trade_plot.png"
    plt.savefig(plot_filename)
    print(f"Trade plot saved as '{plot_filename}'.")
    
    # Display the plot
    plt.show()
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal Execution Time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
