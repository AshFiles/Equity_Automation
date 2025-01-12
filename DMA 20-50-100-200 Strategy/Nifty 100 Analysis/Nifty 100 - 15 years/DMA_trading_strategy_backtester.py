# pip install yfinance matplotlib pandas
# Jan 9 2025
"""
Automated Stock Trading Backtesting and Visualization Script

### Features:
1. **Data Download & Preparation:**
   - Fetches historical stock data for the specified number of years via Yahoo Finance.
   - Calculates 20, 50, 100, and 200-day Simple Moving Averages (DMA).

2. **Trading Strategy:**
   - **Buy:** When Close < DMA_20 < DMA_50 < DMA_100 < DMA_200.
   - **Sell:** When DMA_200 < DMA_100 < DMA_50 < DMA_20 < Close and Sell Price > Buy Price.
   - Executes one trade at a time with full reinvestment of ₹100,000.

3. **Trade Summary:**
   - Logs Entry/Exit Dates, Holding Period in Months, Buy Price, Sell Price, Profit/Loss, Effective Annual Gain %, and Status.
   - Calculates unrealized P/L if holding at the end.

4. **Visualization:**
   - Plots Close Price and DMA lines with distinct line patterns.
   - Marks buy (green ▲) and sell (red ▼) points with corresponding prices.
   - Saves the plot as a PNG file.

5. **Outputs:**
   - Prints a neatly formatted Trade Summary to the console with execution time.
   - Exports Trade Summary as `<STOCK>_trade_summary.csv` with columns: Entry Date, Exit Date, Holding Period in Months, Buy Price, Sell Price, Profit/Loss, Effective Annual Gain %, Status.
   - Appends the same information with an additional 'Stock' column to `trade_logs.csv`.
   - Updates `consolidated_trade_summary.csv` with columns: Stock, Analysis Period, Total Profit/Loss, Unrealized P/L, Number of Times Entered Market.
   - Saves the trade plot as `<STOCK>_trade_plot.png`.

6. **User Flexibility:**
   - **Stock Selection:** Accepts stock name as a command-line argument.
     - Example: `python script.py MARUTI`
   - **No GUI Mode:** Run the script without displaying the graph by providing `no_gui` as a command-line argument before the stock name.
     - Example: `python script.py no_gui MARUTI`
   - **Default Behavior:** If no arguments are provided, uses a predefined stock (e.g., UNIONBANK) and displays the graph.

### Configurable Parameters:
- **Analysis Period:** Set the number of years for the analysis by modifying the `analysis_years` variable in the script.

### Usage:
- **With Graph:**
  - **With Argument:** `python script.py MARUTI`
  - **Without Argument:** Uses the stock name defined in the script (e.g., UNIONBANK).

- **Without Graph:**
  - **With Argument:** `python script.py no_gui MARUTI`
  - **Without Argument:** `python script.py no_gui`

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
    # -------------------------------
    # Configuration Section
    # -------------------------------
    analysis_years = 15  # Set the number of years for analysis (e.g., 5, 10)
    default_stock = 'UNIONBANK'  # Default stock if no argument is provided
    # -------------------------------

    # Initialize GUI flag and stock name
    no_gui = False
    stock_name = default_stock

    # Parse command-line arguments
    args = sys.argv[1:]

    if args:
        # Check if the first argument is 'no_gui' or similar
        if args[0].lower() in ['no_gui', 'no-gui', 'nogui', 'no gui']:
            no_gui = True
            if len(args) > 1:
                stock_name = args[1].upper()
            elif len(args) == 1:
                # If only 'no_gui' is provided without a stock name, use default stock
                stock_name = default_stock
        else:
            # First argument is assumed to be the stock name
            stock_name = args[0].upper()

    # Append '.NS' for Yahoo Finance
    stock_symbol = f"{stock_name}.NS"

    # Getting today's date and calculating the start date based on analysis_years
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=analysis_years * 365)).strftime('%Y-%m-%d')

    # Download stock data for the specified period
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

                # Calculate holding duration in months
                duration_in_days = (exit_date - entry_date).days
                holding_period_months = round(duration_in_days / 30, 2)

                # Effective annual gain
                if duration_in_days > 0:
                    years_fraction = duration_in_days / 365
                    effective_annual_gain = (((current_holding * sell_price) / investment) ** (
                                1 / years_fraction) - 1) * 100
                else:
                    effective_annual_gain = 0

                trades.append({
                    'Entry Date': entry_date.date(),
                    'Exit Date': exit_date.date(),
                    'Holding Period (Months)': holding_period_months,
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
    holding_period_months = ''
    if in_market:
        current_price = data['Close'].iloc[-1]  # Last available price
        unrealized_pnl = current_holding * current_price - investment

        # Calculate holding duration in months
        duration_in_days = (data.index[-1] - entry_date).days
        holding_period_months = round(duration_in_days / 30, 2)

        # Add unrealized profit/loss as another row in the trade summary
        trades.append({
            'Entry Date': entry_date.date(),
            'Exit Date': 'Still Holding',
            'Holding Period (Months)': holding_period_months,
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

    # Ensure 'Status' column exists even if trades_df is empty
    if trades_df.empty:
        trades_df = pd.DataFrame(columns=[
            'Entry Date', 'Exit Date', 'Holding Period (Months)',
            'Buy Price', 'Sell Price', 'Profit/Loss',
            'Effective Annual Gain (%)', 'Status'
        ])

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
    else:
        # Create an empty trade summary file with headers if no trades were made
        trade_summary_filename = f"{stock_name}_trade_summary.csv"
        trades_df.to_csv(trade_summary_filename, index=False)
        print(f"\nNo trades to save. Created empty trade summary file '{trade_summary_filename}'.")

    # Append to trade_logs.csv
    if not trades_df.empty:
        trade_logs_file = "trade_logs.csv"
        trades_df_logs = trades_df.copy()
        trades_df_logs.insert(0, 'Stock', stock_name)

        # Save to trade_logs.csv
        if not os.path.isfile(trade_logs_file):
            trades_df_logs.to_csv(trade_logs_file, index=False)
        else:
            trades_df_logs.to_csv(trade_logs_file, mode='a', header=False, index=False)

        print(f"Trade logs updated in '{trade_logs_file}'.")
    else:
        print(f"No trades to append to 'trade_logs.csv'.")

    # Update consolidated_trade_summary.csv
    consolidated_file = "consolidated_trade_summary.csv"
    total_profit = trades_df['Profit/Loss'].sum() if not trades_df.empty else 0
    unrealized_pnl_final = round(unrealized_pnl, 2) if in_market else ''
    number_of_entries = trades_df[trades_df['Status'] == 'Completed'].shape[0] if not trades_df.empty else 0
    if in_market:
        number_of_entries += 1  # Counting the current holding as an entry

    analysis_period = f"{start_date} to {end_date}"
    consolidated_data = {
        'Stock': stock_name,
        'Analysis Period': analysis_period,
        'Total Profit/Loss': round(total_profit, 2),
        'Unrealized P/L': unrealized_pnl_final,
        'Number of Times Entered Market': number_of_entries
    }
    consolidated_df = pd.DataFrame([consolidated_data])

    if not os.path.isfile(consolidated_file):
        consolidated_df.to_csv(consolidated_file, index=False)
    else:
        consolidated_df.to_csv(consolidated_file, mode='a', header=False, index=False)

    print(f"Consolidated trade summary updated in '{consolidated_file}'.")

    # Plotting the visualization with markers and distinct line patterns
    plt.figure(figsize=(16, 10), dpi=120)
    plt.title(f"Stock Analysis for {stock_name} (Last {analysis_years} Years) with Trades", fontsize=16)

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
    by_label = {}
    for handle, label in zip(handles, labels):
        if label not in by_label:
            by_label[label] = handle
    plt.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=12)

    # Add labels and grid
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price (INR)', fontsize=14)
    plt.grid(True, alpha=0.5)

    # Save the plot as a PNG file
    plot_filename = f"{stock_name}_trade_plot.png"
    plt.savefig(plot_filename)
    print(f"Trade plot saved as '{plot_filename}'.")

    # Display the plot window if GUI is enabled
    if not no_gui:
        plt.show()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal Execution Time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()