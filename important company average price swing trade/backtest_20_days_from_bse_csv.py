import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tabulate import tabulate

'''
download the csv file from bse archive section, 
when you run the script , choose that csv file

note that in the table the correct Running P&L and profit & loss calculation is shown only when there is no active holding.
so try to keep a date range of data where there is no active holding present for that stock.
how to check that ?
use trading view with pine script to make sure that in that date range, we have exited the market.
'''
# this target profit percent is % above the average at which we want to sell, not absolute percent increment
target_profit_percent = 2.5

class GraphWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Trading Strategy Graph")
        self.window.state('zoomed')  # Maximize window
        self.graph_frame = tk.Frame(self.window)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)


class ResultsWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Trading Results")
        self.window.geometry("1200x800")  # Increased window size
        self.results_frame = tk.Frame(self.window)
        self.results_frame.pack(fill=tk.BOTH, expand=True)


class TradeAnalyzer:
    def __init__(self):
        self.graph_window = GraphWindow()
        self.load_button = tk.Button(self.graph_window.window, text="Load CSV File",
                                     command=self.process_data,
                                     font=('Arial', 12))
        self.load_button.pack(pady=10)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            return pd.read_csv(file_path)
        return None

    def calculate_signals(self, df):
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date', ascending=True).reset_index(drop=True)

        df['SMA_20'] = df['Close Price'].rolling(window=20).mean()
        df['Low_20'] = df['Low Price'].rolling(window=20).min()
        df['Green_Line'] = (df['SMA_20'] + df['Low_20']) / 2
        df['Red_Line'] = df['SMA_20'] * (1+ (target_profit_percent/100))

        df['Buy_Signal'] = df['Close Price'] < df['Green_Line']
        df['Sell_Signal'] = df['Close Price'] > df['Red_Line']

        return df

    def calculate_trades(self, df):
        holdings = 0
        investment = 0
        trades = []
        current_holdings = []
        running_investment = 0
        running_returns = 0
        current_buy_value = 0

        for i in range(len(df)):
            if df['Buy_Signal'].iloc[i]:
                shares_to_buy = int(10000 / df['Close Price'].iloc[i])
                holdings += shares_to_buy
                trade_value = shares_to_buy * df['Close Price'].iloc[i]
                current_buy_value += trade_value
                running_investment += trade_value
                trades.append({
                    'Date': df['Date'].iloc[i],
                    'Action': 'BUY',
                    'Shares': shares_to_buy,
                    'Price': df['Close Price'].iloc[i],
                    'Value': trade_value,
                    'Holdings': holdings,
                    'Running_PnL': running_returns - running_investment
                })

            elif df['Sell_Signal'].iloc[i] and holdings > 0:
                sale_value = holdings * df['Close Price'].iloc[i]
                running_returns += sale_value
                trade_profit = sale_value - current_buy_value
                trades.append({
                    'Date': df['Date'].iloc[i],
                    'Action': 'SELL',
                    'Shares': holdings,
                    'Price': df['Close Price'].iloc[i],
                    'Value': sale_value,
                    'Holdings': 0,
                    'Running_PnL': running_returns - running_investment
                })
                holdings = 0
                current_buy_value = 0

            current_holdings.append(holdings)

        df['Holdings'] = current_holdings
        return trades, df

    def plot_results(self, df, trades):
        for widget in self.graph_window.graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(15, 8))

        ax.plot(df['Date'], df['Close Price'], label='Close Price', color='blue')
        ax.plot(df['Date'], df['Green_Line'], label='Green Line', color='green', alpha=0.5)
        ax.plot(df['Date'], df['Red_Line'], label='Red Line', color='red', alpha=0.5)

        buy_points = [trade for trade in trades if trade['Action'] == 'BUY']
        sell_points = [trade for trade in trades if trade['Action'] == 'SELL']

        if buy_points:
            ax.scatter([trade['Date'] for trade in buy_points],
                       [trade['Price'] for trade in buy_points],
                       color='green', marker='^', s=100, label='Buy')
        if sell_points:
            ax.scatter([trade['Date'] for trade in sell_points],
                       [trade['Price'] for trade in sell_points],
                       color='red', marker='v', s=100, label='Sell')

        ax.set_title('Trading Strategy Results', fontsize=12)
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Price', fontsize=10)
        ax.legend(fontsize=10)
        ax.grid(True)
        plt.xticks(rotation=45)

        canvas = FigureCanvasTkAgg(fig, self.graph_window.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_results(self, trades):
        results_window = ResultsWindow()

        # Create Treeview for trades
        columns = ('Date', 'Action', 'Shares', 'Price', 'Value', 'Holdings', 'Running P/L')
        tree = ttk.Treeview(results_window.results_frame, columns=columns, show='headings')

        # Configure column headings and widths
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)  # Increased column width

        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))

        # Calculate totals
        total_investment = 0
        total_returns = 0

        # Prepare data for console output
        console_data = []

        for trade in trades:
            values = (
                trade['Date'].strftime('%Y-%m-%d'),
                trade['Action'],
                trade['Shares'],
                f"{trade['Price']:.2f}",
                f"{trade['Value']:.2f}",
                trade['Holdings'],
                f"{trade['Running_PnL']:.2f}"
            )

            if trade['Action'] == 'BUY':
                total_investment += trade['Value']
                tag = 'buy'
                tree.tag_configure('buy', background='lightgreen')
            else:
                total_returns += trade['Value']
                tag = 'sell'
                tree.tag_configure('sell', background='pink')

            tree.insert('', 'end', values=values, tags=(tag,))

            console_data.append([
                trade['Date'].strftime('%Y-%m-%d'),
                trade['Action'],
                trade['Shares'],
                f"{trade['Price']:.2f}",
                f"{trade['Value']:.2f}",
                trade['Holdings'],
                f"{trade['Running_PnL']:.2f}"
            ])

        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_window.results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill=tk.BOTH, expand=True)

        # Display summary
        summary_frame = tk.Frame(results_window.results_frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)

        net_profit = total_returns - total_investment
        roi = (net_profit / total_investment * 100) if total_investment > 0 else 0

        summary_text = f"""
Trading Summary:
----------------
Total Investment: Rs. {total_investment:.2f}
Total Returns:    Rs. {total_returns:.2f}
Net Profit/Loss:  Rs. {net_profit:.2f}
Return on Investment: {roi:.2f}%
"""

        summary_label = tk.Label(summary_frame, text=summary_text,
                                 justify=tk.LEFT,
                                 font=('Courier', 12, 'bold'))
        summary_label.pack(anchor='w')

        # Print to console
        print("\nTrade Details:")
        print(tabulate(console_data,
                       headers=['Date', 'Action', 'Shares', 'Price', 'Value', 'Holdings', 'Running P/L'],
                       tablefmt='grid'))

        print("\nTrading Summary:")
        print("-" * 50)
        print(f"Total Investment: Rs. {total_investment:.2f}")
        print(f"Total Returns:    Rs. {total_returns:.2f}")
        print(f"Net Profit/Loss:  Rs. {net_profit:.2f}")
        print(f"ROI:             {roi:.2f}%")

    def process_data(self):
        df = self.load_data()
        if df is not None:
            df = self.calculate_signals(df)
            trades, df = self.calculate_trades(df)
            self.plot_results(df, trades)
            self.display_results(trades)

    def run(self):
        self.graph_window.window.mainloop()


if __name__ == "__main__":
    app = TradeAnalyzer()
    app.run()
