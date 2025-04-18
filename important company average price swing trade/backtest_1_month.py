import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

def debug_print(message):
    """Utility function for debugging"""
    print(f"DEBUG: {message}")

def fetch_data(symbol):
    """
    Fetch historical data with detailed debugging
    """
    try:
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        end_date = datetime.now(ist)
        start_date = end_date - timedelta(days=120)
        
        debug_print(f"Attempting to fetch data for {symbol}")
        debug_print(f"Start Date: {start_date}")
        debug_print(f"End Date: {end_date}")
        
        # Create Ticker object
        stock = yf.Ticker(symbol)
        debug_print(f"Ticker object created for {symbol}")
        
        # Get info about the stock
        try:
            info = stock.info
            debug_print(f"Stock info retrieved: {info.get('shortName', 'Name not found')}")
        except Exception as e:
            debug_print(f"Error getting stock info: {str(e)}")
        
        # Try different date formats and intervals
        debug_print("Attempting to fetch historical data...")
        
        # Try with period instead of start/end dates
        df = stock.history(period="120d")
        
        if df.empty:
            debug_print(f"No data received for {symbol}")
            # Try alternative symbol format
            alternative_symbol = symbol.replace('.NS', '')
            debug_print(f"Trying alternative symbol: {alternative_symbol}")
            stock_alt = yf.Ticker(alternative_symbol)
            df = stock_alt.history(period="120d")
        
        debug_print(f"Data shape: {df.shape if not df.empty else 'Empty DataFrame'}")
        debug_print(f"Date range in data: {df.index.min() if not df.empty else 'No dates'} to {df.index.max() if not df.empty else 'No dates'}")
        
        # Print first few rows of data if available
        if not df.empty:
            debug_print("Sample of data received:")
            debug_print(df.head())
            
        return df

    except Exception as e:
        debug_print(f"Error in fetch_data: {str(e)}")
        debug_print(f"Error type: {type(e)}")
        return None

def analyze_stock(symbol):
    """
    Analyze single stock with detailed debugging
    """
    debug_print(f"\nStarting analysis for {symbol}")
    
    df = fetch_data(symbol)
    if df is None or df.empty:
        debug_print(f"No valid data available for {symbol}")
        return []
    
    debug_print(f"Successfully retrieved data for {symbol}")
    debug_print(f"Data points: {len(df)}")
    
    # Initialize variables
    trades = []
    position = False
    buy_price = 0
    quantity = 0
    
    try:
        # Calculate indicators
        debug_print("Calculating trading indicators...")
        df['Monthly_Avg'] = df['Close'].rolling(window=20).mean()
        df['Monthly_Low'] = df['Close'].rolling(window=20).min()
        df['Buy_Threshold'] = (df['Monthly_Avg'] + df['Monthly_Low']) / 2
        
        # Remove NaN values
        df = df.dropna()
        debug_print(f"Data points after removing NaN: {len(df)}")
        
        # Print some statistical information
        debug_print(f"Average price: {df['Close'].mean():.2f}")
        debug_print(f"Price range: {df['Close'].min():.2f} - {df['Close'].max():.2f}")
        
        for index, row in df.iterrows():
            if not position:
                if row['Close'] < row['Buy_Threshold']:
                    buy_price = row['Close']
                    quantity = int(100000 / buy_price)
                    position = True
                    debug_print(f"Buy signal at {index}: Price={buy_price:.2f}, Quantity={quantity}")
                    trades.append({
                        'Date': index,
                        'Action': 'Buy',
                        'Price': buy_price,
                        'Quantity': quantity
                    })
            else:
                if row['Close'] > row['Monthly_Avg']:
                    sell_price = row['Close']
                    profit_loss = (sell_price - buy_price) * quantity
                    position = False
                    debug_print(f"Sell signal at {index}: Price={sell_price:.2f}, P/L={profit_loss:.2f}")
                    trades.append({
                        'Date': index,
                        'Action': 'Sell',
                        'Price': sell_price,
                        'Quantity': quantity,
                        'Profit/Loss': profit_loss
                    })
        
        # Close any open position
        if position:
            last_price = df['Close'].iloc[-1]
            profit_loss = (last_price - buy_price) * quantity
            debug_print(f"Closing open position at {last_price:.2f}, P/L={profit_loss:.2f}")
            trades.append({
                'Date': df.index[-1],
                'Action': 'Sell',
                'Price': last_price,
                'Quantity': quantity,
                'Profit/Loss': profit_loss
            })
    
    except Exception as e:
        debug_print(f"Error during analysis: {str(e)}")
        debug_print(f"Error type: {type(e)}")
    
    debug_print(f"Total trades for {symbol}: {len(trades)}")
    return trades

def main():
    # Try to verify Yahoo Finance connection
    debug_print("Testing Yahoo Finance connection...")
    try:
        test_ticker = yf.Ticker("RELIANCE.NS")
        debug_print("Yahoo Finance connection successful")
    except Exception as e:
        debug_print(f"Yahoo Finance connection error: {str(e)}")

    stocks = [
        'ICICIBANK.NS', 'ADANIPORTS.NS', 'AXISBANK.NS', 'HDFCBANK.NS', 'NTPC.NS',
        'POWERGRID.NS', 'TATASTEEL.NS', 'SUNPHARMA.NS', 'BHARTIARTL.NS', 'RELIANCE.NS',
        'SBIN.NS', 'LT.NS'
    ]
    
    results_list = []
    total_pnl = 0
    
    for symbol in stocks:
        debug_print(f"\nProcessing {symbol}")
        trades = analyze_stock(symbol)
        
        stock_pnl = sum([trade.get('Profit/Loss', 0) for trade in trades if 'Profit/Loss' in trade])
        num_trades = len([t for t in trades if t['Action'] == 'Sell'])
        
        results_list.append({
            'Stock': symbol,
            'Total P&L': stock_pnl,
            'Number of Trades': num_trades,
            'Average P&L per Trade': stock_pnl/num_trades if num_trades > 0 else 0
        })
        
        total_pnl += stock_pnl
    
    # Create and display summary DataFrame
    summary_df = pd.DataFrame(results_list)
    print("\nTRADE SUMMARY")
    print("=" * 80)
    print(summary_df.to_string(index=False))
    print(f"\nTotal P&L: ₹{total_pnl:,.2f}")

if __name__ == "__main__":
    main()
