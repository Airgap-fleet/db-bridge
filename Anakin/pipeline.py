import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Constants
FOREX_SYMBOL = 'GBP/USD'
# API keys loaded from vault secrets
with open(r'C:\the force\00_Master\secrets.md', 'r') as f:
    secrets = f.read()
import re
ALPHA_VANTAGE_API_KEY = re.search(r'Alpha Vantage\s+`([^`]+)`', secrets).group(1)
FRED_API_KEY = re.search(r'FRED \(St\. Louis Fed\)\s+`([^`]+)`', secrets).group(1)
FRED_UNRATE = 'UNRATE'
FRED_PAYEMS = 'PAYEMS'
SIGNALS_FILE = r'C:\The Force\Anakin\signals.txt'
LOG_FILE = r'C:\The Force\AgentComms.md'

def fetch_forex_daily(symbol, api_key):
    # Expect symbol in format "FROM/TO"
    if '/' not in symbol:
        raise ValueError("Symbol must be in format FROM/TO (e.g., GBP/USD)")
    from_symbol, to_symbol = symbol.split('/')
    url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_symbol}&to_symbol={to_symbol}&outputsize=compact&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    ts_key = 'Time Series FX (Daily)'
    if ts_key not in data:
        # Check for error message
        if 'Error Message' in data:
            raise Exception(f"Alpha Vantage API error: {data['Error Message']}")
        elif 'Information' in data:
            raise Exception(f"Alpha Vantage API info: {data['Information']}")
        else:
            raise Exception(f"Unexpected response: {data}")
    df = pd.DataFrame.from_dict(data[ts_key], orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index(ascending=True)
    # Rename columns
    df = df.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close'
    })
    df = df[['open', 'high', 'low', 'close']].astype(float)
    # FX_DAILY does not provide volume, add zero volume
    df['volume'] = 0
    return df

def calculate_indicators(df):
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['sma_200'] = df['close'].rolling(window=200).mean()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def fetch_fred_series(series_id, api_key):
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json'
    response = requests.get(url)
    data = response.json()
    if 'observations' not in data:
        raise Exception(f"FRED API error for {series_id}: {data}")
    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df[['date', 'value']].dropna()
    df.set_index('date', inplace=True)
    return df

def calculate_mom_change(series):
    if len(series) < 2:
        return None
    sorted_dates = series.index.sort_values()
    latest = series.loc[sorted_dates[-1]]
    previous = series.loc[sorted_dates[-2]]
    return (latest - previous) / previous * 100

def generate_signal(df_fx, unrate_mom, payems_mom):
    latest = df_fx.iloc[-1]
    cond1 = latest['close'] > latest['sma_50'] > latest['sma_200']
    cond2 = 40 <= latest['rsi'] <= 60
    cond3 = False
    if unrate_mom is not None and payems_mom is not None:
        cond3 = (unrate_mom < 0) or (payems_mom > 0)
    elif unrate_mom is not None:
        cond3 = (unrate_mom < 0)
    elif payems_mom is not None:
        cond3 = (payems_mom > 0)
    signal = "BUY" if (cond1 and cond2 and cond3) else "NO_SIGNAL"
    return signal, cond1, cond2, cond3, latest

def main():
    try:
        # Fetch forex data
        df_fx = fetch_forex_daily(FOREX_SYMBOL, ALPHA_VANTAGE_API_KEY)
        df_fx = calculate_indicators(df_fx)
        
        # Fetch FRED data
        unrate_df = fetch_fred_series(FRED_UNRATE, FRED_API_KEY)
        payems_df = fetch_fred_series(FRED_PAYEMS, FRED_API_KEY)
        
        # Calculate MoM change
        unrate_mom = calculate_mom_change(unrate_df['value'])
        payems_mom = calculate_mom_change(payems_df['value'])
        
        # Generate signal
        signal, cond1, cond2, cond3, latest = generate_signal(df_fx, unrate_mom, payems_mom)
        
        # Prepare signal output
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        signal_text = f"{timestamp} - Signal: {signal}\\n"
        signal_text += f"  Price: {latest['close']:.4f}, 50 SMA: {latest['sma_50']:.4f}, 200 SMA: {latest['sma_200']:.4f}\\n"
        signal_text += f"  RSI: {latest['rsi']:.2f}\\n"
        unrate_str = f"{unrate_mom:.2f}" if unrate_mom is not None else "N/A"
        payems_str = f"{payems_mom:.2f}" if payems_mom is not None else "N/A"
        signal_text += f"  UNRATE MoM: {unrate_str}% (if available), PAYEMS MoM: {payems_str}% (if available)\\n"
        signal_text += f"  Conditions: price>50SMA>200SMA: {cond1}, RSI 40-60: {cond2}, Macro gate: {cond3}\\n"
        
        # Write signal to file
        with open(SIGNALS_FILE, 'w') as f:
            f.write(signal_text)
        
        # Append to log and reply
        log_entry = f"[{timestamp}] Pipeline executed. Signal: {signal}\\n"
        reply_line = f"> [Hermes Agent] Received and processed. Signal: {signal} at {timestamp}.\\n"
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
            f.write(reply_line)
        
        # Print to console for debugging
        print(signal_text)
        print(f"Signal written to {SIGNALS_FILE}")
        print(f"Log and reply appended to {LOG_FILE}")
        
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{timestamp}] Error in pipeline: {str(e)}\\n"
        print(error_msg)
        with open(LOG_FILE, 'a') as f:
            f.write(error_msg)

if __name__ == "__main__":
    main()