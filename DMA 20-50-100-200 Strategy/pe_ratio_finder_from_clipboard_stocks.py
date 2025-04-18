# Import necessary libraries
import pyperclip
import yfinance as yf
import tkinter as tk
from tkinter import messagebox

# Function to read stock symbols from a file
def read_stock_symbols(file_name):
    """
    Read stock symbols from a file into a set.

    Args:
        file_name (str): Name of the file containing stock symbols.

    Returns:
        set: A set of stock symbols.
    """
    try:
        # Open the file in read mode
        with open(file_name, 'r') as file:
            # Read each line into a set, strip whitespace and convert to uppercase
            stock_symbols = set(line.strip().upper() for line in file)
        return stock_symbols
    except FileNotFoundError:
        # Handle the case where the file is not found
        print(f"File {file_name} not found.")
        return set()

# Function to fetch the PE ratio of a stock using Yahoo Finance
def fetch_pe_ratio(ticker):
    """
    Fetch the PE ratio of a stock.

    Args:
        ticker (str): Ticker symbol of the stock.

    Returns:
        float or None: The PE ratio of the stock, or None if it couldn't be fetched.
    """
    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker)
        # Get the info dictionary
        info = stock.info
        # Return the trailing EPS (used as a proxy for PE ratio)
        return info.get('trailingEps')
    except Exception as e:
        # Handle any exceptions that occur during the fetch
        print(f"Failed to fetch PE ratio for {ticker}: {str(e)}")
        return None

# Main function
def main():
    # Specify the file name containing the stock symbols
    file_name = 'stock_list.txt'
    # Read the stock symbols from the file
    stock_symbols = read_stock_symbols(file_name)
    
    # Check if any stock symbols were read
    if not stock_symbols:
        # If not, show an error message and exit
        messagebox.showerror("Error", "No stock symbols found in the file.")
        return
    
    # Read content from the clipboard
    content = pyperclip.paste()
    
    # Split the content into words
    words = content.split()
    # Extract stock symbols from the words
    found_symbols = [word for word in words if word.upper() in stock_symbols]
    
    # Check if any stock symbols were found in the clipboard content
    if not found_symbols:
        # If not, show an error message and exit
        messagebox.showerror("Error", "No stock symbols found in the clipboard data.")
        return
    
    # Create a dictionary to store the PE ratios
    pe_ratios = {}
    # Fetch the PE ratio for each found stock symbol
    for symbol in found_symbols:
        pe_ratio = fetch_pe_ratio(symbol.upper())
        # If the PE ratio was fetched successfully, store it in the dictionary
        if pe_ratio is not None:
            pe_ratios[symbol.upper()] = pe_ratio
    
    # Sort the PE ratios in ascending order
    sorted_pe_ratios = dict(sorted(pe_ratios.items(), key=lambda item: item[1]))
    
    # Create a new tkinter window
    root = tk.Tk()
    root.title("PE Ratios")
    
    # Create a text box to display the results
    text_box = tk.Text(root, height=len(sorted_pe_ratios) + 1, width=40)
    text_box.pack()
    
    # Insert a header into the text box
    text_box.insert(tk.END, "Stock Symbol\tPE Ratio\n")
    # Insert each stock symbol and its PE ratio into the text box
    for symbol, pe_ratio in sorted_pe_ratios.items():
        text_box.insert(tk.END, f"{symbol}\t{pe_ratio}\n")
    
    # Make the text box read-only
    text_box.config(state="disabled")
    
    # Start the tkinter event loop
    root.mainloop()

# Check if this script is being run directly (not being imported)
if __name__ == "__main__":
    # Call the main function
    main()
