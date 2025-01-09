"""
Batch Automated Stock Trading Backtesting for multiple Stocks

### Description:
This script automates the process of running the DMA-based backtesting and visualization
script for multiple stocks. Instead of executing the main backtesting script manually
for each stock, this batch script iterates through the list of multiple stock tickers and
launches the main script for each one.

### Features:
1. **Automated Execution:**
   - Iterates through all multiple stock tickers.
   - Executes the main backtesting script for each stock without manual intervention.

2. **No GUI Mode:**
   - Runs the backtesting in `no_gui` mode to prevent multiple graph windows from opening.
   - Generates and saves trade summaries and plot images for each stock.

3. **Concurrency Control:**
   - Runs the backtesting scripts sequentially to manage system resources effectively.
   - Can be modified to run in parallel if desired (requires careful handling).

4. **Logging:**
   - Prints progress messages to the console for monitoring.
   - Logs any errors encountered during the execution.

### Usage:
1. **Ensure Main Script Availability:**
   - Place the main backtesting script (e.g., `DMA_trading_strategy_backtester.py`) in the same directory as this batch script.
   - Ensure the main script accepts command-line arguments as specified:
     - **With GUI:** `python DMA_trading_strategy_backtester.py STOCK_NAME`
     - **No GUI:** `python DMA_trading_strategy_backtester.py no_gui STOCK_NAME`

2. **Run the Batch Script(this one):**
   python batch_backtest_enabler.py
"""

import subprocess
import sys
import os
import time

def main():
    start_time = time.time()

    # List of multiple stock tickers (modify if there are changes to the constituent list)
    nifty50_stocks = [
    'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK',
    'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BEL', 'BPCL',
    'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY',
     'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK',
    'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK',
    'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK',
    'LT', 'M&M', 'MARUTI', 'NTPC', 'NESTLEIND',
    'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SHRIRAMFIN',
    'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS',
    'TATASTEEL', 'TECHM', 'TITAN', 'TRENT', 'ULTRACEMCO', 'WIPRO'
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

if __name__ == "__main__":
    main()