"""
Jan 9 2025

Batch Automated Stock Trading Backtesting, Timeline Visualization, and File Organization

This script combines three core functionalities designed to streamline stock trading backtesting, analysis, and file management.

### Functionality:
1. **Batch Backtesting for Multiple Stocks:**
   - Automates the execution of a DMA-based backtesting script for a list of stock tickers.
   - Runs the backtesting script sequentially, avoiding manual execution for each stock.
   - Operates in `no_gui` mode to prevent opening multiple graph windows.
   - Generates and saves trade summaries and plot images for each stock.

2. **Trade Investment Timeline Visualization:**
   - Processes trade data from a CSV file named `trade_logs.csv` to analyze investments and profits over time.
   - Generates a comprehensive graph displaying:
     - Money invested in the market over time.
     - Cumulative profit from exited trades.
     - Annotated markers for trade entry and exit points with company names.
   - Graph features:
     - Month-wise markings on the x-axis.
     - Y-axis scaled to lakhs of rupees for better readability.
     - Annotations indicating total investment in ongoing trades.
   - Saves the graph as `trade_timeline.png` for easy access and reference.

3. **File Organization for Individual Stock Analysis:**
   - Organizes files by moving all analysis-related files (except specified ones) into a folder named `individual_stock_analysis_files`.
   - Excluded files:
     - `trade_logs.csv`
     - `trade_timeline.png`
     - `batch_backtest_enabler.py`
     - `DMA_trading_strategy_backtester.py`
     - `consolidated_trade_summary.csv`


### Usage:
   - Place the main backtesting script (e.g., `DMA_trading_strategy_backtester.py`) in the same directory.
   - Run this batch script to backtest all specified stock tickers in list.

"""

# Standard Library Imports
import os
import sys
import time
import shutil
from datetime import datetime
import subprocess

# Third-Party Library Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter


def run_for_each_stock():
    start_time = time.time()

    # List of multiple stock tickers (modify if there are changes to the constituent list)
    nifty50_stocks = [
    "ABB", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL",
    "AMBUJACEM", "APOLLOHOSP", "ASIANPAINT", "DMART", "AXISBANK", "BAJAJ-AUTO",
    "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BANKBARODA", "BEL", "BHEL", "BPCL",
    "BHARTIARTL", "BOSCHLTD", "BRITANNIA", "CANBK", "CHOLAFIN", "CIPLA", "COALINDIA",
    "DLF", "DABUR", "DIVISLAB", "DRREDDY", "EICHERMOT", "GAIL", "GODREJCP",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO",
    "HAL", "HINDUNILVR", "ICICIBANK", "ICICIGI", "ICICIPRULI", "ITC", "IOC", "IRCTC",
    "IRFC", "INDUSINDBK", "NAUKRI", "INFY", "INDIGO", "JSWENERGY", "JSWSTEEL",
    "JINDALSTEL", "JIOFIN", "KOTAKBANK", "LTIM", "LT", "LICI", "LODHA", "M&M",
    "MARUTI", "NHPC", "NTPC", "NESTLEIND", "ONGC", "PIDILITIND", "PFC", "POWERGRID",
    "PNB", "RECLTD", "RELIANCE", "SBILIFE", "MOTHERSON", "SHREECEM", "SHRIRAMFIN",
    "SIEMENS", "SBIN", "SUNPHARMA", "TVSMOTOR", "TCS", "TATACONSUM", "TATAMOTORS",
    "TATAPOWER", "TATASTEEL", "TECHM", "TITAN", "TORNTPHARM", "TRENT", "ULTRACEMCO",
    "UNIONBANK", "UNITDSPR", "VBL", "VEDL", "WIPRO", "ZOMATO", "ZYDUSLIFE"
]

    # Path to the main backtesting script
    main_script = 'DMA_trading_strategy_backtester.py'  # Replace with your main script filename

    # Check if the main script exists
    if not os.path.isfile(main_script):
        print(f"Error: Main script '{main_script}' not found in the current directory.")
        sys.exit(1)

    total_stocks = len(nifty50_stocks)
    print(f"Starting backtesting for {total_stocks} multiple stocks...\n")

    for idx, stock in enumerate(nifty50_stocks, start=1):
        print(f"Processing {idx}/{total_stocks}: {stock} ...")
        try:
            # Execute the main script with 'no_gui' and the stock ticker
            result = subprocess.run(
                ['python', main_script, 'no_gui', stock],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Optionally, capture and log the output
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {stock}:")
            print(e.stderr)
        except Exception as ex:
            print(f"Unexpected error processing {stock}: {ex}")
        print("-" * 50)
        # Optional: Add a short delay to avoid overwhelming resources
        time.sleep(1)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nBatch backtesting completed in {total_time / 60:.2f} minutes.")


def organize_files():
    # Define the files to exclude from moving
    exclude_files = {
        'trade_logs.csv',
        'trade_timeline.png',
        'batch_backtest_enabler.py',
        'DMA_trading_strategy_backtester.py',
        'consolidated_trade_summary.csv'
    }

    # Name of the target directory
    target_dir = 'individual_stock_analysis_files'

    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            print(f"Created directory: {target_dir}")
        except Exception as e:
            print(f"Error creating directory '{target_dir}': {e}")
            return

    # Iterate over all items in the current directory
    for item in os.listdir('.'):
        # Full path of the item
        item_path = os.path.join('.', item)

        # Check if it's a file and not in the exclude list
        if os.path.isfile(item_path) and item not in exclude_files:
            try:
                shutil.move(item_path, os.path.join(target_dir, item))
                print(f"Moved: {item} -> {target_dir}/")
            except Exception as e:
                print(f"Failed to move '{item}': {e}")
        else:
            # Skip directories and excluded files
            continue


def plot_trade_timeline(csv_file='trade_logs.csv', png_file='trade_timeline.png'):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading '{csv_file}': {e}")
        sys.exit(1)

    # Define a future date for 'Still Holding' trades
    future_date_str = '2024-12-31'
    future_date = pd.to_datetime(future_date_str, format='%Y-%m-%d')

    # Clean 'Entry Date' and 'Exit Date' by stripping leading/trailing spaces
    df['Entry Date'] = df['Entry Date'].astype(str).str.strip()
    df['Exit Date'] = df['Exit Date'].astype(str).str.strip()

    # Replace 'Still Holding' in 'Exit Date' with future_date_str
    df['Exit Date'] = df['Exit Date'].apply(
        lambda x: future_date_str if isinstance(x, str) and x.lower() == 'still holding' else x
    )

    # Parse 'Entry Date' and 'Exit Date' with the exact format
    df['Entry Date'] = pd.to_datetime(df['Entry Date'], format='%Y-%m-%d', errors='coerce')
    df['Exit Date'] = pd.to_datetime(df['Exit Date'], format='%Y-%m-%d', errors='coerce')

    # Identify and report parsing failures
    entry_parse_failures = df[df['Entry Date'].isna()]
    exit_parse_failures = df[df['Exit Date'].isna()]

    if not entry_parse_failures.empty:
        print("Warning: Some Entry Dates could not be parsed and will be excluded:")
        print(entry_parse_failures[['Stock', 'Entry Date']].to_string(index=False))

    if not exit_parse_failures.empty:
        print("Warning: Some Exit Dates could not be parsed and will be set to 'Still Holding' date:")
        print(exit_parse_failures[['Stock', 'Exit Date']].to_string(index=False))
        df.loc[df['Exit Date'].isna(), 'Exit Date'] = future_date

    # Drop rows with invalid Entry Dates
    initial_row_count = df.shape[0]
    df = df.dropna(subset=['Entry Date'])
    final_row_count = df.shape[0]
    dropped_rows = initial_row_count - final_row_count
    if dropped_rows > 0:
        print(f"Info: Dropped {dropped_rows} rows due to invalid Entry Dates.")

    # Replace NaN in Profit/Loss with 0 and ensure numeric
    df['Profit/Loss'] = pd.to_numeric(df['Profit/Loss'], errors='coerce').fillna(0)

    # Set the end date for the timeline as the maximum of Exit Date and Entry Date
    end_date = df[['Exit Date', 'Entry Date']].max().max()
    start_date = df['Entry Date'].min()

    if pd.isna(start_date) or pd.isna(end_date):
        print("Error: Start date or end date is NaT. Please check the date formats in the CSV.")
        sys.exit(1)

    # Create a date range from the earliest entry to the end date
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Initialize series for invested money and profit booked with float dtype
    invested_money = pd.Series(0.0, index=date_range)
    profit_booked = pd.Series(0.0, index=date_range)

    # Lists to store investment and exit events for markers
    investment_events = []
    exit_events = []

    # Calculate invested money using boolean masking for efficiency
    for idx, row in df.iterrows():
        entry = row['Entry Date']
        exit_ = row['Exit Date']
        stock = row['Stock']
        profit = row['Profit/Loss']

        if pd.isna(entry) or pd.isna(exit_):
            continue  # Skip if dates are invalid

        # Ensure entry and exit dates are within the date_range
        entry = max(entry, start_date)
        exit_ = min(exit_, end_date)

        if entry > exit_:
            print(f"Warning: Entry date {entry.date()} for stock '{stock}' is after Exit date {exit_.date()}. Skipping this trade.")
            continue  # Skip trades where entry date is after exit date

        # Create a mask for the date range where the trade is active
        mask = (invested_money.index >= entry) & (invested_money.index <= exit_)
        invested_money.loc[mask] += 100000.0

        # Record investment event
        investment_events.append((entry, stock))

        # Record exit event if not holding
        if exit_ != future_date:
            exit_events.append((exit_, stock, profit))

    # Calculate profit booked for completed trades
    for exit_date, stock, profit in exit_events:
        if exit_date in profit_booked.index:
            profit_booked.loc[exit_date] += profit

    # Cumulative profit booked
    cumulative_profit_booked = profit_booked.cumsum()

    # Calculate money required to invest each month (removed as per instruction)
    # Calculate money freed each month from exited trades (removed as per instruction)

    # Plotting
    plt.figure(figsize=(18, 10))

    # Plot Invested Money
    plt.plot(invested_money.index, invested_money.values, label='Invested Money (₹)', color='blue')

    # Plot Cumulative Profit Booked
    plt.plot(cumulative_profit_booked.index, cumulative_profit_booked.values, label='Cumulative Profit Booked (₹)', color='green')

    # Formatting the date axis with month markings
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    plt.xticks(rotation=45)

    # Scaling the y-axis to lakhs
    def to_lakhs(x, pos):
        return f'{int(x/100000)}L'

    plt.gca().yaxis.set_major_formatter(FuncFormatter(to_lakhs))
    plt.ylabel('Amount in ₹ (Lakhs)')
    plt.xlabel('Date')
    plt.title('Trade Investment Timeline and Profit Analysis')

    # Add markers for investment events
    for entry_date, stock in investment_events:
        if entry_date in invested_money.index:
            plt.plot(entry_date, invested_money.loc[entry_date], marker='^', color='green', markersize=10, label='Investment' if stock == investment_events[0][1] else "")
            plt.text(entry_date, invested_money.loc[entry_date]*1.02, stock, rotation=45, fontsize=8, verticalalignment='bottom', color='green')

    # Add markers for exit events
    for exit_date, stock, profit in exit_events:
        if exit_date in cumulative_profit_booked.index:
            plt.plot(exit_date, cumulative_profit_booked.loc[exit_date], marker='v', color='red', markersize=10, label='Exit' if stock == exit_events[0][1] else "")
            plt.text(exit_date, cumulative_profit_booked.loc[exit_date]*0.98, stock, rotation=45, fontsize=8, verticalalignment='top', color='red')

    # Adjust legend to avoid duplicates
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper left')

    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.tight_layout()

    # Annotation for ongoing investments
    holding_trades_count = df[df['Exit Date'] == future_date].shape[0]
    total_invested_ongoing = holding_trades_count * 100000
    if holding_trades_count > 0:
        plt.annotate(f'Ongoing Investments: {holding_trades_count} × ₹1,00,000 = ₹{total_invested_ongoing:,}',
                     xy=(1, 0), xycoords='axes fraction',
                     xytext=(-50, -50), textcoords='offset points',
                     ha='right', va='bottom',
                     fontsize=10,
                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

    # Save the plot as PNG
    try:
        plt.savefig(png_file)
        print(f"Graph saved as '{png_file}'.")
    except Exception as e:
        print(f"Error saving the graph: {e}")

    # Show the plot
    plt.show()


if __name__ == "__main__":
    run_for_each_stock()
    organize_files()
    plot_trade_timeline()