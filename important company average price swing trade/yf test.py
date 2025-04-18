import nsepy
import pandas_datareader as pdr
import pandas as pd
from datetime import date, datetime, timedelta
import time

class DataFetcher:
    def __init__(self):
        self.methods = [
            self.fetch_nse_data,
            self.fetch_stooq_data
        ]
    
    def fetch_nse_data(self, symbol):
        """NSE-Tools method"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=120)
            data = nsepy.get_history(symbol=symbol, start=start_date, end=end_date)
            return data if not data.empty else None
        except Exception as e:
            print(f"NSE-Tools error for {symbol}: {e}")
            return None

    def fetch_stooq_data(self, symbol):
        """Stooq method"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=120)
            df = pdr.get_data_stooq(f'{symbol}.NS', start=start_date, end=end_date)
            return df if not df.empty else None
        except Exception as e:
            print(f"Stooq error for {symbol}: {e}")
            return None

    def get_data(self, symbol):
        """Try all methods until successful"""
        for method in self.methods:
            print(f"Trying {method.__name__} for {symbol}")
            df = method(symbol)
            if df is not None and not df.empty:
                print(f"Successfully fetched data using {method.__name__}")
                return df
            time.sleep(1)  # Add delay between attempts
        return None

def analyze_stock(df, symbol):
    """Analyze stock data using your strategy"""
    if df is None or df.empty:
        return None
    
    try:
        # Calculate indicators
        df['Monthly_Avg'] = df['Close'].rolling(window=20).mean()
        df['Monthly_Low'] = df['Close'].rolling(window=20).min()
        df['Buy_Threshold'] = (df['Monthly_Avg'] + df['Monthly_Low']) / 2
        
        trades = []
        position = False
        buy_price = 0
        quantity = 0
        
        for index, row in df.iterrows():
            if not position:
                if row['Close'] < row['Buy_Threshold']:
                    buy_price = row['Close']
                    quantity = int(100000 / buy_price)
                    position = True
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
                    trades.append({
                        'Date': index,
                        'Action': 'Sell',
                        'Price': sell_price,
                        'Quantity': quantity,
                        'Profit/Loss': profit_loss
                    })
        
        return trades
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def main():
    stocks = [
        'ICICIBANK', 'ADANIPORTS', 'AXISBANK', 'HDFCBANK', 'NTPC',
        'POWERGRID', 'TATASTEEL', 'SUNPHARMA', 'BHARTIARTL', 'RELIANCE',
        'SBIN', 'LT'
    ]
    
    fetcher = DataFetcher()
    results = []
    
    for symbol in stocks:
        print(f"\nProcessing {symbol}")
        df = fetcher.get_data(symbol)
        
        if df is not None:
            trades = analyze_stock(df, symbol)
            if trades:
                total_pnl = sum([t.get('Profit/Loss', 0) for t in trades if 'Profit/Loss' in t])
                num_trades = len([t for t in trades if t['Action'] == 'Sell'])
                
                results.append({
                    'Stock': symbol,
                    'Total P&L': total_pnl,
                    'Number of Trades': num_trades,
                    'Average P&L per Trade': total_pnl/num_trades if num_trades > 0 else 0
                })
    
    if results:
        summary_df = pd.DataFrame(results)
        print("\nTRADE SUMMARY")
        print("=" * 80)
        print(summary_df.to_string(index=False))
        print(f"\nTotal P&L: ₹{summary_df['Total P&L'].sum():,.2f}")
    else:
        print("\nNo trading results to display")

if __name__ == "__main__":
    main()
