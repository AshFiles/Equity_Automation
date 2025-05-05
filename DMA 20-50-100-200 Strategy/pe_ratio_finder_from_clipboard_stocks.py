import requests
from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
import pyperclip
import time
import random


def search_screener_pe_ratio(stock_name):
    """
    Get P/E ratio from screener.in directly.

    Args:
        stock_name (str): Name/symbol of the stock to search for.

    Returns:
        float or None: The P/E ratio if found, None otherwise.
    """
    try:
        print(f"Searching for P/E ratio of {stock_name} on screener.in...")

        # Direct URL for companies on screener.in (NSE stocks)
        url = f"https://www.screener.in/company/{stock_name}/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        print(f"Sending request to {url}")
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            print(f"{stock_name} not found on screener.in, trying BSE ticker...")
            # Try with BSE prefix if NSE ticker not found
            url = f"https://www.screener.in/company/{stock_name}/consolidated/"
            response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to get data for {stock_name}: HTTP {response.status_code}")
            return None

        print(f"Response received, status code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find P/E ratio in the ratios section
        ratios = soup.find('div', {'id': 'ratios'})
        if not ratios:
            print("Ratios section not found")
            return None

        # Find P/E ratio in the table
        pe_row = None
        for row in ratios.find_all('li'):
            text = row.get_text().strip()
            if 'PE' in text or 'P/E' in text:
                pe_row = row
                break

        if not pe_row:
            print("P/E ratio row not found")
            return None

        # Extract P/E value
        value = pe_row.find('span', {'class': 'number'})
        if not value:
            print("P/E value element not found")
            return None

        pe_text = value.get_text().strip()
        print(f"Found P/E text: {pe_text}")

        if pe_text and pe_text.lower() != 'nan':
            try:
                pe_ratio = float(pe_text)
                print(f"Extracted P/E ratio for {stock_name}: {pe_ratio}")
                return pe_ratio
            except ValueError:
                print(f"Could not convert '{pe_text}' to float")

        return None
    except Exception as e:
        print(f"Error while searching for P/E ratio of {stock_name}: {e}")
        return None


def read_stock_symbols(file_name):
    """
    Read stock symbols from a file into a set.

    Args:
        file_name (str): Name of the file containing stock symbols.

    Returns:
        set: A set of stock symbols.
    """
    try:
        print(f"Reading stock symbols from '{file_name}'...")
        with open(file_name, 'r') as file:
            stock_symbols = set(line.strip().upper() for line in file)
        print(f"Read {len(stock_symbols)} stock symbols from '{file_name}'")
        return stock_symbols
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return set()


def main_gui():
    """Main function that creates a GUI for the application."""
    # Create the main window
    root = tk.Tk()
    root.title("Stock P/E Ratio Finder")
    root.geometry("600x500")

    # Specify the file name containing stock symbols
    file_name = 'stock_list.txt'
    stock_symbols = read_stock_symbols(file_name)

    def fetch_pe_ratios():
        # Clear the console text
        console_text.delete(1.0, tk.END)

        # Read content from clipboard
        print_to_console("Reading content from clipboard...")
        content = pyperclip.paste()
        print_to_console(
            f"Clipboard content: {content[:100]}..." if len(content) > 100 else f"Clipboard content: {content}")

        # Split the content into words
        words = content.split()
        print_to_console(f"Words extracted: {words}")

        # Extract stock symbols from the words
        found_symbols = [word for word in words if word.upper() in stock_symbols]
        print_to_console(f"Stock symbols found: {found_symbols}")

        if not found_symbols:
            message = "No stock symbols found in the clipboard data."
            print_to_console(message)
            messagebox.showerror("Error", message)
            return

        # Create a dictionary to store PE ratios
        pe_ratios = {}

        # Update the status text
        status_label.config(text="Fetching P/E ratios...")
        root.update()

        # Fetch PE ratio for each stock symbol
        for i, symbol in enumerate(found_symbols):
            status_label.config(text=f"Fetching P/E ratio for {symbol} ({i + 1}/{len(found_symbols)})...")
            root.update()

            pe_ratio = search_screener_pe_ratio(symbol.upper())
            if pe_ratio is not None:
                pe_ratios[symbol.upper()] = pe_ratio

            # Add a delay to avoid rate limiting
            if i < len(found_symbols) - 1:  # Don't sleep after last request
                delay = random.uniform(2, 4)  # Random delay between 2-4 seconds
                print_to_console(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)

        # Sort the PE ratios in ascending order
        sorted_pe_ratios = dict(sorted(pe_ratios.items(), key=lambda item: item[1]))
        print_to_console(f"Sorted P/E ratios: {sorted_pe_ratios}")

        # Display the results
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Symbol\tP/E Ratio\n")
        result_text.insert(tk.END, "-" * 30 + "\n")

        for symbol, pe_ratio in sorted_pe_ratios.items():
            result_text.insert(tk.END, f"{symbol}\t{pe_ratio}\n")

        status_label.config(text=f"Found P/E ratios for {len(pe_ratios)}/{len(found_symbols)} stocks")
        print_to_console("P/E ratio fetching completed")

    def print_to_console(message):
        """Print message to both console and GUI console widget"""
        print(message)
        console_text.insert(tk.END, message + "\n")
        console_text.see(tk.END)  # Scroll to the end
        root.update()

    # Create widgets
    header_label = tk.Label(root, text="Stock P/E Ratio Finder", font=("Arial", 16, "bold"))
    header_label.pack(pady=10)

    instruction_label = tk.Label(root, text="Copy stock symbols to clipboard and click 'Fetch P/E Ratios'")
    instruction_label.pack(pady=5)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    fetch_button = tk.Button(button_frame, text="Fetch P/E Ratios", command=fetch_pe_ratios,
                             bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5)
    fetch_button.pack(side=tk.LEFT, padx=5)

    clear_button = tk.Button(button_frame, text="Clear Results",
                             command=lambda: [result_text.delete(1.0, tk.END), console_text.delete(1.0, tk.END)],
                             bg="#f44336", fg="white", font=("Arial", 10), padx=10, pady=5)
    clear_button.pack(side=tk.LEFT, padx=5)

    status_label = tk.Label(root, text="Ready", fg="blue")
    status_label.pack(pady=5)

    # Main frame for results and console
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Left side - Results
    results_frame = tk.LabelFrame(main_frame, text="P/E Ratio Results")
    results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    result_text = scrolledtext.ScrolledText(results_frame, height=10, width=30, font=("Courier New", 10))
    result_text.pack(fill=tk.BOTH, expand=True)

    # Right side - Console output
    console_frame = tk.LabelFrame(main_frame, text="Console Output")
    console_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    console_text = scrolledtext.ScrolledText(console_frame, height=10, width=40, font=("Courier New", 9), bg="#f0f0f0")
    console_text.pack(fill=tk.BOTH, expand=True)

    footer_label = tk.Label(root, text="Note: P/E ratios are fetched from screener.in")
    footer_label.pack(pady=5)

    # Start the GUI event loop
    print("Starting GUI application")
    root.mainloop()


if __name__ == "__main__":
    main_gui()
